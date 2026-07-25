from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-review-code/SKILL.md"
AGENT_PATH = REPO_ROOT / ".github/skills/internal-review-code/agents/openai.yaml"
CARD_MARKERS = ("🔎", "📌", "🧪", "👉")


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


def test_code_review_wrapper_owns_only_the_public_chat_projection() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "The core owns review reasoning and severity" in skill_text
    assert "This wrapper owns the public chat projection" in skill_text
    for marker in CARD_MARKERS:
        assert marker in skill_text
    assert "retained review engine" not in skill_text


def test_code_review_runtime_prompt_requests_the_adaptive_projection() -> None:
    prompt_text = AGENT_PATH.read_text(encoding="utf-8")

    assert "adaptive chat projection" in prompt_text
    assert "separate follow-up" in prompt_text
