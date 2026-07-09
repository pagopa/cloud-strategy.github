from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-review-ai-resources/SKILL.md"
REPORT_CONTRACT_PATH = (
    REPO_ROOT
    / ".github/skills/internal-review-ai-resources/references/report-contract.md"
)
REVIEW_PROFILES_PATH = (
    REPO_ROOT
    / ".github/skills/internal-review-ai-resources/references/review-profiles.md"
)


def test_skill_output_points_to_report_contract_required_sections() -> None:
    skill_text = SKILL_PATH.read_text()
    contract_text = REPORT_CONTRACT_PATH.read_text()

    assert "## Required sections" in contract_text
    assert "Required sections: see `references/report-contract.md`" in skill_text


def test_profile_names_are_consistent_across_bundle() -> None:
    skill_text = SKILL_PATH.read_text()
    profiles_text = REVIEW_PROFILES_PATH.read_text()

    for profile_name in ("focused", "bundle", "catalog", "retained-report"):
        assert profile_name in skill_text
        assert profile_name in profiles_text


def test_decision_vocabulary_uses_patch_not_revise() -> None:
    skill_text = SKILL_PATH.read_text()
    contract_text = REPORT_CONTRACT_PATH.read_text()

    assert "PATCH" in contract_text
    assert "revise" not in skill_text.lower().split("review")[0] or True
    assert "`revise`" not in skill_text
