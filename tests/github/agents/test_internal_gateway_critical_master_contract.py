import tomllib
from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
CODEX_PATH = REPO_ROOT / ".codex/agents/internal-gateway-critical-master.toml"
COPILOT_PATH = REPO_ROOT / ".github/agents/internal-gateway-critical-master.agent.md"
OPENAI_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-critical-master/agents/openai.yaml"
)


def _assert_ordered(markers: list[str], text: str) -> None:
    positions = [text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_internal_gateway_critical_master_codex_contract() -> None:
    payload = tomllib.loads(CODEX_PATH.read_text(encoding="utf-8"))
    instructions = payload["developer_instructions"]
    lowered = instructions.lower()

    assert CODEX_PATH.stem == payload["name"] == "internal-gateway-critical-master"
    assert payload["description"]
    assert "critical-challenge" in payload["description"]
    assert payload["model"] == "gpt-5.6"
    assert payload["model_reasoning_effort"] == "medium"
    assert payload["sandbox_mode"] == "read-only"

    _assert_ordered(
        ["Phase 1: Discover", "Phase 2: Challenge", "Phase 3: Synthesize"],
        instructions,
    )
    for marker in (
        "exactly three",
        "analogy",
        "reverse-assumption",
        "pre-mortem",
        "strongest supported objection",
        "at most one",
        "confirmed",
        "inference",
        "estimate",
        "final consistency gate",
        "exactly one canonical internal routing outcome",
        "full-analysis-v1",
        "full-analysis-contract.md",
        "target_path",
        "target_revision",
        "every material finding",
        "strict JSON packet",
    ):
        assert marker in instructions
    for defense in ("none", "resolves", "narrows", "accepts-risk", "unanswered"):
        assert defense in instructions

    for marker in (
        "do not edit files",
        "do not run commands",
        "do not author or modify plans",
        "do not access external systems",
        "do not dispatch subagents",
        "do not expose the internal critical record",
        "defense classification",
        "canonical routing outcome",
        "self-contained at runtime",
        "source skill is unavailable at runtime",
        "/internal-gateway-writing-plans",
        "/internal-gateway-execute-plans",
        "/internal-gateway-simple-task",
        "/internal-review-code",
    ):
        assert marker in lowered

    assert "output-contract.md" not in instructions
    assert "emoji card" not in lowered
    openai_prompt = OPENAI_PATH.read_text(encoding="utf-8")
    assert "full-analysis-v1" in openai_prompt
    assert "emoji card" not in openai_prompt.lower()

    assert not COPILOT_PATH.exists()
