from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
AGENT_PATH = REPO_ROOT / ".github/agents/internal-gateway-review-generic.agent.md"


def test_ai_resource_review_covers_lifecycle_and_retirement() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8").lower()
    for marker in (
        "compatibility",
        "propagation",
        "periodic review",
        "retirement",
        "inventory",
        "sync",
    ):
        assert marker in text


def test_ai_resource_review_routes_surface_gated_depth_to_audit_owner() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())

    assert "internal-copilot-audit" in text
    assert "./.github/scripts/run.sh check_catalog_consistency" in text
    assert "conditional" in normalized_text
    assert "not a second review runtime" in normalized_text


def test_generic_review_is_report_only_until_manual_remediation_selection() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    assert "review pass is report-only" in text
    assert "explicitly selects" in text
    assert "Do not infer approval" in text
    assert "internal-skill-creator" not in text


def test_generic_review_uses_local_consistency_not_critical_agent() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "## Review Consistency Gate" in text
    assert "test the strongest contrary explanation" in text
    assert "internal-gateway-critical-master" not in text
    assert "Critical Counter-Analysis" not in text


def test_generic_review_core_skill_resolves_to_a_real_bundle() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    section = text.split("## Core Skill", 1)[1].split("\n## ", 1)[0]
    declared = [
        line.strip().removeprefix("- `").removesuffix("`")
        for line in section.splitlines()
        if line.strip().startswith("- `")
    ]

    assert declared == ["internal-review-high-level"]
    for name in declared:
        assert (REPO_ROOT / ".github/skills" / name / "SKILL.md").exists()
    assert "Do not delegate to peer agents" in text
    assert "internal-skill-creator" not in text


def test_generic_agent_can_attest_load_gate_without_delegation_tool() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())

    assert "perform this observable load gate directly" in normalized_text
    assert "Delegation may be used when available" in normalized_text
    assert "is not required" in normalized_text
    assert "delegate the load gate" not in normalized_text
    assert "The delegated gate" not in normalized_text


def test_generic_agent_no_longer_owns_the_severity_mapping() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "Map Critical findings" not in text


def test_generic_review_bounds_remediation_and_follow_up_owner_naming() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    section = text.split("## Remediation Boundary", 1)[1].split("\n## ", 1)[0]

    assert "non-executable artifacts" in section
    assert "executable or evaluable behavior" in section
    assert "outside the lane" in section
    assert "no changes were applied" in section
    for owner in (
        "internal-gateway-simple-task",
        "internal-gateway-execute-plans",
        "internal-gateway-writing-plans",
        "internal-lesson-codification",
        "internal-skill-creator",
    ):
        assert owner not in text
    assert "Do not name any owner that is not a review owner" in text


def test_generic_agent_keeps_routing_and_chat_projection_only() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")

    assert "## Review Framework" not in text
    assert "Every material finding contains" not in text
    assert "Expected verification" not in text
    for marker in ("`🔎`", "`📌`", "`🧪`", "`👉`"):
        assert marker in text
    assert "match the user's chat language" in text
    for surface in ("AI resources", "Workflows", "Policies and documentation", "Plans and review packages", "Mixed artifacts"):
        assert surface in text
