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


def test_skill_md_does_not_restate_checklist() -> None:
    import re
    skill_text = SKILL_PATH.read_text()
    checklist_text = CHECKLIST_PATH.read_text()

    def normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().lower()

    skill_norm = normalize(skill_text)
    checklist_norm = normalize(checklist_text)

    shared_phrases = [
        "iron law: do not create or materially revise a skill without first seeing the failure",
        "treat skills as reusable reference guides, not narratives",
        "prefer the smallest change that fixes the local problem",
        "keep `description:` trigger-only",
        "preserve a working `description:` during token optimization",
        "treat generic skill shape as conditional, not a rigid section template",
        "treat `## referenced skills` as an audit index, not a preload list",
        "remove duplicated responsibility, not useful trigger reinforcement",
        "prefer `references/` over new `scripts/` for static tables",
        "reference other skills by skill name and behavior only",
        "prefer bundle-relative references to files under",
        "do not copy the same material back into `skill.md`",
    ]

    duplicates = [
        phrase for phrase in shared_phrases
        if phrase in skill_norm and phrase in checklist_norm
    ]

    assert not duplicates, (
        f"SKILL.md restates {len(duplicates)} phrases also in checklist: {duplicates[:3]}"
    )
