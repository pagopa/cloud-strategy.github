from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-skill-creator"
SKILL_PATH = BUNDLE_ROOT / "SKILL.md"
OPENAI_PATH = BUNDLE_ROOT / "agents/openai.yaml"


def workflow_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8").split("## Workflow", 1)[1]


def test_material_work_runs_delegates_in_order() -> None:
    workflow = workflow_text()
    headings = (
        "### 1. Anthropic authoring",
        "### 2. Predictability review",
        "### 3. Repository closure",
    )
    positions = [workflow.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "Load `anthropic-skill-creator`" in workflow
    assert "Load `mattpocock-writing-great-skills`" in workflow


def test_anthropic_stage_is_proportional_and_evidence_gated() -> None:
    workflow = workflow_text()
    anthropic = workflow.split("### 1. Anthropic authoring", 1)[1].split(
        "### 2. Predictability review", 1
    )[0]
    assert "applicable evaluation branches" in anthropic
    assert "skipped branches and reasons" in anthropic
    assert "draft, evidence, blockers, and completion status" in anthropic


def test_predictability_stage_revises_instead_of_only_reporting() -> None:
    workflow = workflow_text()
    review = workflow.split("### 2. Predictability review", 1)[1].split(
        "### 3. Repository closure", 1
    )[0]
    assert "revise the draft" in review
    assert "invocation, description, information hierarchy" in review
    assert "duplication, sediment, no-op, and predictability" in review


def test_local_closure_keeps_repository_specific_checks() -> None:
    workflow = workflow_text()
    closure = workflow.split("### 3. Repository closure", 1)[1]
    assert "agents/openai.yaml" in closure
    assert "validate_internal_skills" in closure
    assert "routing fallout" in closure
    assert "before/after" in closure


def test_redundant_local_references_are_removed() -> None:
    assert not (
        BUNDLE_ROOT / "references/writing-skills-checklist.md"
    ).exists()
    assert not (
        BUNDLE_ROOT / "references/script-output-contract.md"
    ).exists()


def test_default_prompt_names_the_ordered_delegates() -> None:
    prompt = OPENAI_PATH.read_text(encoding="utf-8")
    anthropic = prompt.index("anthropic-skill-creator")
    matt = prompt.index("mattpocock-writing-great-skills")
    assert anthropic < matt
    assert "repository closure" in prompt
