import textwrap
import tomllib
from pathlib import Path

import pytest
from agent_translation import (
    parse_frontmatter_and_body,
    target_extension,
    translate_agent_for_target,
)


def test_translate_agent_for_codex_preserves_body_and_handoffs(tmp_path: Path) -> None:
    source_path = tmp_path / "review.agent.md"
    source_path.write_text(
        textwrap.dedent(
            """\
            ---
            name: review-agent
            description: Review changes carefully.
            handoffs:
              - label: Escalate
                agent: review-specialist
                prompt: Include the risky files.
            ---
            Main body instructions.
            """
        ),
        encoding="utf-8",
    )

    translated = translate_agent_for_target(source_path, "codex")
    payload = tomllib.loads(translated)

    assert target_extension("codex") == ".toml"
    assert payload["name"] == "review-agent"
    assert "Main body instructions." in payload["developer_instructions"]
    assert "## Handoffs" in payload["developer_instructions"]
    assert "review-specialist" in payload["developer_instructions"]


def test_translate_agent_for_opencode_maps_tools_agents_and_visibility(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "worker.agent.md"
    source_path.write_text(
        textwrap.dedent(
            """\
            ---
            name: worker
            description: Bounded worker.
            model: GPT-5.6 Luna
            tools: [read, search, execute, web, edit, unmapped-tool]
            agents: [helper-a, helper-b]
            disable-model-invocation: true
            handoffs:
              - label: Escalate
                agent: helper-a
            ---
            Worker body.
            """
        ),
        encoding="utf-8",
    )

    translated = translate_agent_for_target(source_path, "opencode")
    frontmatter, body = parse_frontmatter_and_body(translated)

    assert target_extension("opencode") == ".md"
    assert frontmatter == {
        "description": "Bounded worker.",
        "mode": "subagent",
        "hidden": True,
        "permission": {
            "read": "allow",
            "grep": "allow",
            "glob": "allow",
            "bash": "allow",
            "webfetch": "allow",
            "websearch": "allow",
            "edit": "allow",
            "task": {"*": "deny", "helper-a": "allow", "helper-b": "allow"},
        },
    }
    assert body == "Worker body.\n\n## Handoffs\n- **Escalate** → `helper-a`\n"


def test_translate_agent_for_codex_projects_sidecar_overrides(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "low-cost.agent.md"
    source_path.write_text(
        textwrap.dedent(
            """\
            ---
            name: internal-low-cost-agent
            description: Bounded token-intensive worker.
            model: GPT-5.6 Luna
            user-invocable: false
            tools: [read, search, web, edit, execute]
            ---
            Follow the complete parent task packet.
            """
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / "low-cost.agent-config.yaml"
    config_path.write_text(
        textwrap.dedent(
            """\
            codex:
              model: gpt-5.6-luna
              model_reasoning_effort: high
              sandbox_mode: workspace-write
            """
        ),
        encoding="utf-8",
    )

    translated = translate_agent_for_target(source_path, "codex", config_path)
    payload = tomllib.loads(translated)

    assert payload["name"] == "internal-low-cost-agent"
    assert payload["description"] == "Bounded token-intensive worker."
    assert payload["model"] == "gpt-5.6-luna"
    assert payload["model_reasoning_effort"] == "high"
    assert payload["sandbox_mode"] == "workspace-write"
    assert (
        payload["developer_instructions"] == "Follow the complete parent task packet."
    )
    assert "GPT-5.6 Luna" not in translated


def test_translate_agent_for_codex_rejects_unsupported_sidecar_override(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "low-cost.agent.md"
    source_path.write_text(
        "---\nname: internal-low-cost-agent\n---\nWorker body.\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "low-cost.agent-config.yaml"
    config_path.write_text(
        "codex:\n  unsupported_key: value\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=r"unsupported Codex agent override.*unsupported_key",
    ):
        translate_agent_for_target(source_path, "codex", config_path)
