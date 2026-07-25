from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-skill-creator"
SKILL_PATH = BUNDLE_ROOT / "SKILL.md"
OPENAI_PATH = BUNDLE_ROOT / "agents/openai.yaml"
REFERENCE_PATH = BUNDLE_ROOT / "references" / "authoring-and-evaluation.md"


def workflow_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8").split("## Workflow", 1)[1]


def test_material_work_uses_core_method_before_local_evaluation() -> None:
    workflow = workflow_text()
    headings = (
        "### 1. Repository preflight",
        "### 2. Core authoring and revision",
        "### 3. Proportional evaluation",
        "### 4. Repository closure",
    )
    positions = [workflow.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "Load `/mattpocock-writing-great-skills`" in workflow
    assert "core method" in workflow


def test_local_evaluation_stage_is_evidence_gated() -> None:
    workflow = workflow_text()
    evaluation = workflow.split("### 3. Proportional evaluation", 1)[1].split(
        "### 4. Repository closure", 1
    )[0]
    normalized = " ".join(evaluation.split())
    assert "references/authoring-and-evaluation.md" in normalized
    assert "applicable evaluation branches" in normalized
    assert "skipped branches and reasons" in normalized
    assert "evidence, blockers, and completion status" in normalized


def test_local_authoring_reference_covers_the_retained_contract() -> None:
    reference = REFERENCE_PATH.read_text(encoding="utf-8")
    required_markers = (
        "## Intent contract",
        "## Evaluation selection",
        "## Baselines",
        "## Evidence and human review",
        "## Description trigger checks",
        "## Iteration stop conditions",
    )
    for marker in required_markers:
        assert marker in reference
    assert "objective" in reference.lower()
    assert "subjective" in reference.lower()
    assert "near-miss" in reference.lower()
    assert "holdout" in reference.lower()


def test_internal_bundle_has_only_the_core_skill_dependency() -> None:
    bundle_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in BUNDLE_ROOT.rglob("*")
        if path.is_file()
    )
    assert "anthropic-skill-creator" not in bundle_text
    assert "local-agent-sync-external-resources" not in bundle_text
    assert "internal-agent-creator" not in bundle_text
    assert bundle_text.count("mattpocock-writing-great-skills") >= 2


def test_core_stage_revises_instead_of_only_reporting() -> None:
    workflow = workflow_text()
    review = workflow.split("### 2. Core authoring and revision", 1)[1].split(
        "### 3. Proportional evaluation", 1
    )[0]
    assert "revise the draft" in review
    assert "invocation, description, information hierarchy" in review
    assert "duplication, sediment, and no-ops" in review


def test_local_closure_keeps_repository_specific_checks() -> None:
    workflow = workflow_text()
    closure = workflow.split("### 4. Repository closure", 1)[1]
    assert "agents/openai.yaml" in closure
    assert "validate_internal_skills" in closure
    assert "routing fallout" in closure
    assert "before/after" in closure


def test_redundant_local_references_are_removed() -> None:
    assert not (BUNDLE_ROOT / "references/writing-skills-checklist.md").exists()
    assert not (BUNDLE_ROOT / "references/script-output-contract.md").exists()


def test_default_prompt_names_core_method_before_local_closure() -> None:
    prompt = OPENAI_PATH.read_text(encoding="utf-8")
    matt = prompt.index("mattpocock-writing-great-skills")
    evaluation = prompt.index("proportional evaluation")
    closure = prompt.index("repository closure")
    assert matt < evaluation < closure
    assert "anthropic-skill-creator" not in prompt
