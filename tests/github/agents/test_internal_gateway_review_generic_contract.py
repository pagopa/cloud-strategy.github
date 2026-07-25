from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
AGENT_PATH = REPO_ROOT / ".github/agents/internal-gateway-review-generic.agent.md"


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


def test_generic_review_is_report_only_until_manual_remediation_selection() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    assert "review pass is report-only" in text
    assert "explicitly selects" in text
    assert "Do not infer approval" in text
    assert "internal-skill-creator" not in text


def test_generic_review_uses_local_consistency_not_critical_agent() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "## Review Consistency Gate" in text
    assert "test the strongest contrary explanation" in text
    assert "internal-gateway-critical-master" not in text
    assert "Critical Counter-Analysis" not in text


def test_generic_review_has_no_synthetic_core_skill() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "## Core Skill" not in text
    assert "Do not delegate to peer agents" in text
