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
EXPECTED_HEADINGS = ["Luna Executor", "Role", "Boundaries", "Output Expectations"]
EXPECTED_TOOLS = {"read", "search", "web", "edit", "execute"}
EXPECTED_PROTOCOL = "internal-subagent-contract/v1"


def _parse_copilot(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    assert match is not None
    return yaml.safe_load(match.group(1)), content[match.end() :]


def _headings(body: str) -> list[str]:
    return re.findall(r"^#{1,6}\s+(.+?)\s*$", body, re.MULTILINE)


def test_internal_luna_executor_copilot_contract() -> None:
    frontmatter, body = _parse_copilot(COPILOT_PATH)

    assert frontmatter["name"] == "internal-luna-executor"
    assert frontmatter["model"] == "GPT-5.6 Luna"
    assert "effort" not in frontmatter
    assert frontmatter["user-invocable"] is False
    assert frontmatter["disable-model-invocation"] is False
    assert frontmatter["agents"] == []
    assert set(frontmatter["tools"]) == {"read", "search", "web", "edit", "execute"}
    assert _headings(body) == EXPECTED_HEADINGS
    assert EXPECTED_PROTOCOL in body
    assert "nested_agents: prohibited" in body
    assert "WorkerResult" in body


def test_internal_luna_executor_codex_contract() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))

    assert payload["name"] == "internal-luna-executor"
    assert payload["model"] == "gpt-5.6-luna"
    assert payload["model_reasoning_effort"] == "high"
    assert payload["sandbox_mode"] == "workspace-write"
    assert "delegate" not in payload["developer_instructions"].lower()
    assert all(
        heading in payload["developer_instructions"]
        for heading in ("## Role", "## Boundaries", "## Output Expectations")
    )
    assert EXPECTED_PROTOCOL in payload["developer_instructions"]
    assert "nested_agents: prohibited" in payload["developer_instructions"]
    assert "WorkerResult" in payload["developer_instructions"]


def test_luna_profiles_expose_the_same_parsed_worker_contract() -> None:
    copilot, copilot_body = _parse_copilot(COPILOT_PATH)
    codex = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))
    codex_body = codex["developer_instructions"]

    assert copilot["agents"] == []
    assert EXPECTED_TOOLS == set(copilot["tools"])
    assert "nested_agents: prohibited" in copilot_body
    assert "nested_agents: prohibited" in codex_body
    assert EXPECTED_PROTOCOL in copilot_body
    assert EXPECTED_PROTOCOL in codex_body


def test_luna_profiles_have_no_positive_nested_dispatch_route() -> None:
    _, copilot_body = _parse_copilot(COPILOT_PATH)
    codex_body = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))["developer_instructions"]

    for body in (copilot_body, codex_body):
        assert "nested_agents: prohibited" in body
        assert not re.search(r"\b(delegate|spawn)\s+(?:to\s+)?another\s+agent", body, re.I)
