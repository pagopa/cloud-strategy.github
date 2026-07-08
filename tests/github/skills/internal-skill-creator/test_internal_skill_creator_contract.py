from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-skill-creator/SKILL.md"
CHECKLIST_PATH = (
    REPO_ROOT
    / ".github/skills/internal-skill-creator/references/writing-skills-checklist.md"
)


def test_referenced_skills_are_audit_index_not_preload() -> None:
    skill_text = SKILL_PATH.read_text()
    checklist_text = CHECKLIST_PATH.read_text()

    assert "audit index, not a preload" in skill_text
    assert "audit index, not a preload" in checklist_text
    assert "Do not load referenced skills from this section alone" in checklist_text


def test_generic_skill_shape_is_conditional_not_rigid() -> None:
    checklist_text = CHECKLIST_PATH.read_text()

    assert "## Generic skill shape" in checklist_text
    assert "Conditional sections" in checklist_text
    assert "Do not require every section for every skill" in checklist_text


def test_skill_cleanup_preserves_triggers_and_removes_responsibility_duplication() -> None:
    checklist_text = CHECKLIST_PATH.read_text()

    assert "Remove duplicated responsibility, not useful trigger reinforcement" in checklist_text
    assert "Preserve a working `description:` during cleanup" in checklist_text
