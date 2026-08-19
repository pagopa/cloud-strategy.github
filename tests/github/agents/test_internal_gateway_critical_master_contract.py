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
SKILL_REPO_PATH = REPO_ROOT / ".github/skills/internal-gateway-critical-master/SKILL.md"
SKILL_HOME_PATH = Path.home() / ".agents/skills/internal-gateway-critical-master/SKILL.md"


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

    assert set(frontmatter) == {"name", "description", "tools", "agents"}
    assert frontmatter["name"] == "internal-gateway-critical-master"
    assert frontmatter["description"].startswith("Use this agent when")
    assert frontmatter["tools"] == ["read", "search", "edit", "execute"]
    assert "model" not in frontmatter
    assert "effort" not in frontmatter
    assert "model_reasoning_effort" not in frontmatter
    assert frontmatter["agents"] == []

    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
    assert headings == [
        "Role",
        "Core Skill",
        "Context and Input",
        "Operating Boundary",
        "Output",
        "No-context Failure",
    ]
    assert body.count("## Core Skill") == 1
    assert body.count("- `internal-gateway-critical-master`") == 1
    lowered = body.lower()
    for marker in (
        "load and follow `internal-gateway-critical-master`",
        "no structured input is required",
        "full critical procedure",
        "prefer read-only",
        "explicitly requests",
        "readable markdown report",
        "skill's fixed layout",
        "no-context failure",
    ):
        assert marker.lower() in lowered
    for retired_marker in (
        "full-analysis-v1",
        "target_revision",
        "target_path",
        "references/full-analysis-contract.md",
        "exactly one utf-8 json object",
        "number every evidence item consecutively",
        "critique, evidence, suggestion, why",
    ):
        assert retired_marker not in lowered


def test_internal_gateway_critical_master_codex_contract() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))
    instructions = payload["developer_instructions"]

    assert CODEX_PATH.stem == payload["name"] == "internal-gateway-critical-master"
    assert payload["description"]
    assert "critical-analysis" in payload["description"]
    assert "model" not in payload
    assert "model_reasoning_effort" not in payload
    assert payload["sandbox_mode"] == "workspace-write"

    assert isinstance(instructions, str)
    assert instructions.strip()
    lowered = " ".join(instructions.lower().split())
    for marker in (
        "structured input is optional",
        "only analysis failure",
        "prefer read-only",
        "explicitly asks",
        "readable markdown report",
        "skill's fixed layout",
        "no-context failure",
    ):
        assert marker in lowered
    for retired_marker in (
        "full-analysis-v1",
        "target_revision",
        "number evidence items consecutively",
        "critique, evidence, suggestion, why",
    ):
        assert retired_marker not in lowered


def test_internal_gateway_critical_master_home_skill_matches_repo() -> None:
    assert SKILL_REPO_PATH.exists()
    assert SKILL_HOME_PATH.exists()
    assert SKILL_HOME_PATH.read_bytes() == SKILL_REPO_PATH.read_bytes()
