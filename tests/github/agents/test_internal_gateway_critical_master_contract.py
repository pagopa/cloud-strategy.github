import re
import tomllib
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
CODEX_PATH = REPO_ROOT / ".codex/agents/internal-gateway-critical-master.toml"
COPILOT_PATH = REPO_ROOT / ".github/agents/internal-gateway-critical-master.agent.md"


def _parse_copilot(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    assert match is not None
    return yaml.safe_load(match.group(1)), content[match.end() :]


def test_internal_gateway_critical_master_codex_declares_required_core_skill() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))

    assert payload["skills"]["config"] == [
        {
            "path": "~/.agents/skills/internal-gateway-critical-master/SKILL.md",
            "enabled": True,
        }
    ]


def test_internal_gateway_critical_master_copilot_contract() -> None:
    assert COPILOT_PATH.exists()
    frontmatter, body = _parse_copilot(COPILOT_PATH)

    assert set(frontmatter) == {"name", "description", "tools", "model", "agents"}
    assert frontmatter["name"] == "internal-gateway-critical-master"
    assert frontmatter["description"].startswith("Use this agent when")
    assert frontmatter["tools"] == ["read", "search"]
    assert frontmatter["model"] == "GPT-5.6 Sol"
    assert frontmatter["model"] != "GPT-5.6 Luna"
    assert "effort" not in frontmatter
    assert "model_reasoning_effort" not in frontmatter
    assert frontmatter["agents"] == []

    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
    assert headings == [
        "Role",
        "Core Skill",
        "Routing Rules/Boundaries",
        "Required Input",
        "Output Expectations",
    ]
    assert body.count("## Core Skill") == 1
    assert body.count("- `internal-gateway-critical-master`") == 1
    lowered = body.lower()
    for marker in (
        "load and follow `internal-gateway-critical-master`",
        "references/full-analysis-contract.md",
        "source",
        "target_path",
        "target_revision",
        "do not edit files",
        "do not run commands or execute",
        "do not access external systems",
        "do not author or modify plans",
        "do not dispatch subagents",
        "do not perform active routing",
        "exactly one UTF-8 JSON object",
        "internal-gateway-critical/full-analysis-v1",
        "exact top-level keys",
        "every material finding",
        "no Markdown or prose outside JSON",
        "full-analysis contract",
    ):
        assert marker.lower() in lowered


def test_internal_gateway_critical_master_codex_contract() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))
    instructions = payload["developer_instructions"]

    assert CODEX_PATH.stem == payload["name"] == "internal-gateway-critical-master"
    assert payload["description"]
    assert "critical-challenge" in payload["description"]
    assert payload["model"] == "gpt-5.6-sol"
    assert payload["model_reasoning_effort"] == "medium"
    assert payload["sandbox_mode"] == "read-only"

    assert isinstance(instructions, str)
    assert instructions.strip()
