import re
import tomllib
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
COPILOT_PATH = REPO_ROOT / ".github/agents/internal-luna-executor.agent.md"
CODEX_PATH = REPO_ROOT / ".codex/agents/internal-luna-executor.toml"
SECTION_HEADINGS = ["Role", "Boundaries", "Output Expectations"]
EXPECTED_TOOLS = {"read", "search", "web", "edit", "execute"}
EXPECTED_PROTOCOL = "internal-subagent-contract/v1"


def _parse_copilot(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    assert match is not None
    return yaml.safe_load(match.group(1)), content[match.end() :]


def _headings(body: str) -> list[str]:
    return re.findall(r"^#{1,6}\s+(.+?)\s*$", body, re.MULTILINE)


def test_internal_luna_executor_copilot_profile() -> None:
    frontmatter, body = _parse_copilot(COPILOT_PATH)

    assert frontmatter["name"] == "internal-luna-executor"
    assert frontmatter["model"] == "GPT-5.6 Luna"
    assert "effort" not in frontmatter
    assert frontmatter["user-invocable"] is False
    assert frontmatter["disable-model-invocation"] is False
    assert frontmatter["agents"] == []
    assert set(frontmatter["tools"]) == EXPECTED_TOOLS
    assert _headings(body) == ["Luna Executor", *SECTION_HEADINGS]
    assert EXPECTED_PROTOCOL in body


def test_internal_luna_executor_codex_profile() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))
    instructions = payload["developer_instructions"]

    assert payload["name"] == "internal-luna-executor"
    assert payload["model"] == "gpt-5.6-luna"
    assert payload["model_reasoning_effort"] == "high"
    assert payload["sandbox_mode"] == "workspace-write"
    assert _headings(instructions) == SECTION_HEADINGS
    assert EXPECTED_PROTOCOL in instructions
