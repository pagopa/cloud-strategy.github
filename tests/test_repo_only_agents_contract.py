from __future__ import annotations

from pathlib import Path

import yaml

SYNC_AGENTS = {
    "local-sync-external-resources": ".github/agents/local-sync-external-resources.agent.md",
    "local-sync-global-copilot-configs-into-repo": ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md",
    "local-sync-home-ai-resources": ".github/agents/local-sync-home-ai-resources.agent.md",
}

WATCHLIST_PATH = Path(
    ".github/skills/local-agent-sync-external-resources/references/external-watchlist.yaml"
)

LEGACY_AGENT_HEADINGS = (
    "## Mandatory Engine Skills",
    "## Optional Support Skills",
    "## Preferred/Optional Skills",
    "## Skill Usage Contract",
)

EXPECTED_CORE_SKILLS = {
    "local-sync-external-resources": "local-agent-sync-external-resources",
    "local-sync-global-copilot-configs-into-repo": (
        "local-agent-sync-global-copilot-configs-into-repo"
    ),
    "local-sync-home-ai-resources": "local-agent-sync-home-ai-resources",
}


def retired_mattpocock_ids() -> tuple[str, ...]:
    return tuple(
        f"mattpocock-{suffix}"
        for suffix in (
            "diagnose",
            "tdd",
            "improve-codebase-architecture",
            "zoom-out",
            "grill-with-docs",
            "setup-matt-pocock-skills",
        )
    )


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    frontmatter_text = text.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter_text)


def read_body(relative_path: str) -> str:
    text = Path(relative_path).read_text(encoding="utf-8")
    return text.split("---\n", 2)[2]


def core_skill(body: str) -> str:
    section = body.split("## Core Skill", 1)[1].split("\n## ", 1)[0]
    matches = [
        line.strip().strip("- ").strip("`")
        for line in section.splitlines()
        if line.strip().startswith("- ")
    ]
    assert len(matches) == 1
    return matches[0]


def test_repo_only_sync_agents_keep_boundary_and_tool_contracts() -> None:
    for agent_name, relative_path in SYNC_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        body = read_body(relative_path)

        assert frontmatter["name"] == agent_name
        assert isinstance(frontmatter.get("description"), str)
        assert frontmatter.get("tools")
        assert "agent" not in frontmatter.get("tools", [])
        assert frontmatter.get("disable-model-invocation") is True
        assert frontmatter.get("agents") in (None, [])
        assert "## Core Skill" in body
        assert "## Boundary Definition" in body
        assert "## Output Expectations" in body
        for heading in LEGACY_AGENT_HEADINGS:
            assert heading not in body
        assert core_skill(body) == EXPECTED_CORE_SKILLS[agent_name]


def test_repo_only_sync_agents_keep_their_named_operating_engines() -> None:
    sync_control_center = read_body(
        ".github/agents/local-sync-external-resources.agent.md"
    )
    sync_global = read_body(
        ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md"
    )

    assert "- `local-agent-sync-external-resources`" in sync_control_center
    assert "- `local-agent-sync-global-copilot-configs-into-repo`" in sync_global


def test_mattpocock_sync_scope_keeps_only_active_managed_imports() -> None:
    sync_control_center = read_body(
        ".github/agents/local-sync-external-resources.agent.md"
    )
    sync_global = read_body(
        ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md"
    )
    combined_text = f"{sync_control_center}\n{sync_global}"

    assert "`caveman` -> `mattpocock-caveman`" in combined_text
    assert "`grill-me` -> `grill-me`" in combined_text
    for retired_id in retired_mattpocock_ids():
        assert retired_id not in combined_text


def test_external_watchlist_is_alert_only_and_internal_owner_mapped() -> None:
    payload = yaml.safe_load(WATCHLIST_PATH.read_text(encoding="utf-8"))
    items = payload["items"]
    owners = {item["local_owner"] for item in items}
    upstream_ids = {item["upstream_id"] for item in items}

    assert payload["version"] == 1
    assert len(items) == 6
    assert all(item["source_family"] == "mattpocock/skills" for item in items)
    assert all(item["action"] == "alert-only" for item in items)
    assert "zoom-out" in upstream_ids
    assert {
        "internal-debugging",
        "internal-tdd",
        "internal-high-level-review",
        "internal-writing-plans",
        "local-agent-sync-external-resources",
    } <= owners


def test_direct_entry_model_keeps_removed_router_assets_out_of_live_catalog() -> None:
    assert not Path(".github/agents/internal-router.agent.md").exists()
    assert not Path(".github/skills/internal-agent-routing-engine").exists()
