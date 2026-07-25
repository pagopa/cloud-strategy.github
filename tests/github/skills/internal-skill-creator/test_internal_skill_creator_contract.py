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
SCRIPT_OUTPUT_CONTRACT_PATH = (
    REPO_ROOT
    / ".github/skills/internal-skill-creator/references/script-output-contract.md"
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


def test_skill_cleanup_preserves_triggers_and_removes_responsibility_duplication() -> (
    None
):
    checklist_text = CHECKLIST_PATH.read_text()

    assert (
        "Remove duplicated responsibility, not useful trigger reinforcement"
        in checklist_text
    )
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
        "compare the wrapper against its core before editing",
    ]

    duplicates = [
        phrase
        for phrase in shared_phrases
        if phrase in skill_norm and phrase in checklist_norm
    ]

    assert not duplicates, (
        f"SKILL.md restates {len(duplicates)} phrases also in checklist: {duplicates[:3]}"
    )


def test_core_backed_wrapper_guidance_is_generic_and_reference_owned() -> None:
    skill_text = SKILL_PATH.read_text()
    checklist_text = CHECKLIST_PATH.read_text()

    required_guidance = (
        "## Core-backed wrappers",
        "Compare the wrapper against its core before editing",
        "trigger, repository-local policy, and proven environment fallbacks",
        "Do not restate the core's workflow, decision logic, output contract, or validation procedure",
        "Structural validation is not semantic alignment",
        "paired agent",
    )

    for phrase in required_guidance:
        assert phrase in checklist_text

    assert "Compare the wrapper against its core before editing" not in skill_text
    assert "internal-review-code" not in checklist_text
    assert "addyosmani-code-review-and-quality" not in checklist_text


def test_script_output_contract_uses_one_machine_serialization() -> None:
    contract_text = SCRIPT_OUTPUT_CONTRACT_PATH.read_text()

    assert "JSON is the only common machine-readable contract" in contract_text
    assert "`text` is operator presentation" in contract_text
    assert "`compact` and `full` are detail profiles" in contract_text
    assert "`--format json --detail compact|full`" in contract_text


def test_compact_profile_preserves_decision_evidence() -> None:
    contract_text = SCRIPT_OUTPUT_CONTRACT_PATH.read_text()

    for required_field in (
        "status",
        "material counts",
        "blockers",
        "traceable evidence",
        "truncation state",
        "next action",
    ):
        assert required_field in contract_text


def test_unapproved_formats_remain_out_of_scope() -> None:
    contract_text = SCRIPT_OUTPUT_CONTRACT_PATH.read_text().lower()

    assert "out of scope" in contract_text
    for deferred_format in ("tsv", "csv", "jsonl", "ndjson", "toon"):
        assert deferred_format in contract_text


def test_existing_compact_aliases_are_not_forced_to_migrate() -> None:
    contract_text = SCRIPT_OUTPUT_CONTRACT_PATH.read_text()

    assert "Existing `--format compact` interfaces may remain" in contract_text
    assert "Do not require repository-wide migration" in contract_text


def test_skill_routes_script_contract_detail_to_local_reference() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "references/script-output-contract.md" in skill_text
    assert "when a skill introduces or materially revises scripts" in skill_text


def test_wrapper_owns_full_bundle_lifecycle() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "bundle anatomy" in skill_text
    assert "references/script-output-contract.md" in skill_text


def test_skill_creator_routing_has_vendor_specific_downstream_lanes() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "anthropic-skill-creator" in skill_text
    assert "explicitly requests Anthropic or Claude" in skill_text
    assert "repository-owned" in skill_text

    internal_pos = skill_text.index("internal-skill-creator")
    anthropic_pos = skill_text.index("anthropic-skill-creator")
    assert internal_pos < anthropic_pos


def test_local_bundle_guidance_is_model_neutral() -> None:
    bundle_text = "\n".join(
        path.read_text()
        for path in (SKILL_PATH, CHECKLIST_PATH, SCRIPT_OUTPUT_CONTRACT_PATH)
    ).lower()

    for forbidden_name in ("chatgpt", "gpt-5", "gpt-6"):
        assert forbidden_name not in bundle_text
