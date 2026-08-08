import re
import tomllib
from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
COPILOT_PATH = REPO_ROOT / ".github/agents/internal-low-cost-copilot.agent.md"
CODEX_PATH = REPO_ROOT / ".codex/agents/internal-low-cost-codex.toml"
EXPECTED_HEADINGS = [
    "Role",
    "Eligibility",
    "Task Packet",
    "Execution Rules",
    "Stop Conditions",
    "Output Expectations",
]


def _parse_copilot(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    assert match is not None
    return yaml.safe_load(match.group(1)), content[match.end() :]


def _headings(body: str) -> list[str]:
    return re.findall(r"^#{1,6}\s+(.+?)\s*$", body, re.MULTILINE)


def test_internal_low_cost_copilot_contract() -> None:
    frontmatter, body = _parse_copilot(COPILOT_PATH)

    assert frontmatter["name"] == "internal-low-cost-copilot"
    assert frontmatter["model"] == "GPT-5.6 Luna"
    assert "effort" not in frontmatter
    assert frontmatter["user-invocable"] is False
    assert frontmatter["disable-model-invocation"] is False
    assert frontmatter["agents"] == []
    assert set(frontmatter["tools"]) == {"read", "search", "web", "edit", "execute"}
    assert _headings(body) == EXPECTED_HEADINGS


def test_internal_low_cost_codex_contract() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))

    assert payload["name"] == "internal-low-cost-codex"
    assert payload["model"] == "gpt-5.6-luna"
    assert payload["model_reasoning_effort"] == "high"
    assert payload["sandbox_mode"] == "workspace-write"
    assert "delegate" not in payload["developer_instructions"].lower()
    assert all(
        heading in payload["developer_instructions"]
        for heading in ("## Role", "## Eligibility", "## Task Packet", "## Stop Conditions")
    )
