from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"


def test_makefile_valid_fixture_marks_build_as_phony() -> None:
    fixture = (SKILLS_ROOT / "internal-makefile/fixtures/valid/Makefile").read_text(
        encoding="utf-8"
    )

    assert ".PHONY: all build clean test" in fixture
