from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
AGENT_PATH = (
    REPO_ROOT / ".github/agents/internal-gateway-review-generic.agent.md"
)


def test_ai_resource_review_covers_lifecycle_and_retirement() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8").lower()
    for marker in (
        "compatibility",
        "propagation",
        "periodic review",
        "retirement",
        "inventory",
        "sync",
    ):
        assert marker in text


def test_generic_review_remains_analysis_only() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    assert "Do not edit files" in text
    assert "internal-skill-creator" not in text
