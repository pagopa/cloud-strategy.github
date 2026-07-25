from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_ROOT = REPO_ROOT / ".github/skills/internal-gateway-codebase-improvement"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
OPENAI_PATH = SKILL_ROOT / "agents/openai.yaml"
CONTRACT_PATH = REPO_ROOT / "INTERNAL_CONTRACT.md"
AGENT_WRAPPER = (
    REPO_ROOT / ".github/agents/internal-gateway-codebase-improvement.agent.md"
)


def _frontmatter() -> dict[str, object]:
    text = SKILL_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def test_skill_is_manual_only_in_both_metadata_surfaces() -> None:
    assert _frontmatter()["name"] == "internal-gateway-codebase-improvement"
    assert _frontmatter()["disable-model-invocation"] is True
    policy = yaml.safe_load(OPENAI_PATH.read_text(encoding="utf-8"))["policy"]
    assert policy["allow_implicit_invocation"] is False


def test_skill_has_no_agent_wrapper() -> None:
    assert not AGENT_WRAPPER.exists()


def test_contract_classifies_the_skill_outside_the_gateway_core() -> None:
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    required = (
        "`internal-gateway-codebase-improvement` is a manual-only "
        "specialist gateway outside the canonical gateway core"
    )
    assert required in " ".join(contract.split())
    assert "must not become an implicit fallback" in contract


WORKFLOW_PATH = SKILL_ROOT / "references/workflow.md"
LANES = (
    "local-simplification",
    "architecture-improvement",
    "combined",
)
METHOD_OWNERS = (
    "internal-tdd",
    "superpowers-verification-before-completion",
)
REFERENCE_ONLY_OWNERS = (
    "mattpocock-improve-codebase-architecture",
    "addyosmani-code-simplification",
)


def test_skill_defines_exactly_three_evidence_selected_lanes() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for lane in LANES:
        assert f"`{lane}`" in skill
        assert lane in workflow
    assert "Select exactly one lane from repository evidence" in skill
    assert "Do not run both source methods by default" in skill
    assert "No silent lane escalation" in skill


def test_skill_references_existing_method_owners_without_copying_them() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    for owner in METHOD_OWNERS:
        assert f"`/{owner}`" in skill
    for owner in REFERENCE_ONLY_OWNERS:
        assert f"`{owner}`" in skill
        assert f"`/{owner}`" not in skill
    assert "HTML report scaffold" not in skill
    assert "The Five Principles" not in skill


def test_structural_work_requires_approval_and_protects_seams() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    required = (
        "Structural Approval Gate",
        "Protected seam set",
        "Passing behavior baseline",
        "Final Evidence Gate",
    )
    for marker in required:
        assert marker in skill
        assert marker in workflow
    assert workflow.index("Structural Approval Gate") < workflow.index(
        "Executable refactor"
    )
    assert workflow.index("Protected seam set") < workflow.index(
        "Behavior-preserving simplification"
    )
