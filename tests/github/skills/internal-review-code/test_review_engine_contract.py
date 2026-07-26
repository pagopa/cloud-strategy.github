from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
ENGINE_PATH = REPO_ROOT / ".github/skills/addyosmani-code-review-and-quality/SKILL.md"
WRAPPER_PATH = REPO_ROOT / ".github/skills/internal-review-code/SKILL.md"


def test_imported_review_engine_axes_and_categories_remain_stable() -> None:
    engine_text = ENGINE_PATH.read_text(encoding="utf-8")
    wrapper_text = WRAPPER_PATH.read_text(encoding="utf-8")

    assert "## The Five-Axis Review" in engine_text
    for heading in (
        "Correctness",
        "Readability & Simplicity",
        "Architecture",
        "Security",
        "Performance",
    ):
        assert heading in engine_text
    for category in ("Critical:", "Nit:", "Optional:", "Consider:", "FYI"):
        assert category in engine_text
    assert "six review axes" not in wrapper_text.lower()
