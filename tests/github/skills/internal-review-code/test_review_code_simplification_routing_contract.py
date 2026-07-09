from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-review-code/SKILL.md"
AGENT_PATH = REPO_ROOT / ".github/skills/internal-review-code/agents/openai.yaml"


def test_code_review_routes_simplification_as_a_separate_follow_up() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "`addyosmani-code-simplification`: on-demand remediation owner" in skill_text
    assert "separate simplification follow-up" in skill_text
    assert (
        "Do not load or execute `addyosmani-code-simplification` during the review pass."
        in skill_text
    )


def test_code_review_agent_does_not_preload_simplification() -> None:
    assert "addyosmani-code-simplification" not in AGENT_PATH.read_text()
