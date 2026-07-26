from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
AGENT_PATHS = (
    REPO_ROOT / ".github/agents/internal-gateway-review-code.agent.md",
    REPO_ROOT / ".github/agents/internal-gateway-review-generic.agent.md",
)
CODE_AGENT = REPO_ROOT / ".github/agents/internal-gateway-review-code.agent.md"
CODE_SKILL = REPO_ROOT / ".github/skills/internal-review-code/SKILL.md"
CARD_MARKERS = ("🔎", "📌", "🧪", "👉")
MATERIAL_FIELDS = (
    "Location",
    "Evidence",
    "Impact",
    "Correction",
    "Expected verification",
)
LEGACY_PUBLIC_SECTIONS = (
    "### Verification Story",
    "### Critical Counter-Analysis Result",
    "### Residual Risk",
    "### Next Decision",
    "**Review Gate:**",
)


def _agent_texts() -> tuple[str, ...]:
    return tuple(path.read_text(encoding="utf-8") for path in AGENT_PATHS)


def _agent_frontmatters() -> tuple[dict[str, object], ...]:
    return tuple(
        yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        for path in AGENT_PATHS
    )


def test_review_agents_define_the_same_public_card_fields() -> None:
    for text in _agent_texts():
        for marker in CARD_MARKERS:
            assert marker in text
        assert "match the user's chat language" in text
        assert "one user action" in text


def test_code_review_owner_defines_complete_material_findings() -> None:
    text = " ".join(CODE_SKILL.read_text(encoding="utf-8").split())
    for field in MATERIAL_FIELDS:
        assert field in text
    assert "consolidate equivalent findings" in text
    assert "show every blocking and important finding" in text


def test_review_agents_hide_legacy_internal_sections() -> None:
    for text in (
        AGENT_PATHS[1].read_text(encoding="utf-8"),
        CODE_SKILL.read_text(encoding="utf-8"),
    ):
        for heading in LEGACY_PUBLIC_SECTIONS:
            assert heading not in text


def test_review_agents_require_manual_remediation_selection() -> None:
    for text in _agent_texts():
        assert "separate follow-up" in text
        assert "no changes were applied" in text
        assert "review pass is report-only" in text
        assert "explicitly selects" in text
        assert "finding IDs" in text


def test_generic_review_agent_can_edit_an_explicitly_selected_remediation() -> None:
    assert "edit" in _agent_frontmatters()[1]["tools"]


def test_code_review_agent_edit_is_plan_only() -> None:
    text = AGENT_PATHS[0].read_text(encoding="utf-8")
    frontmatter = _agent_frontmatters()[0]

    assert "edit" in frontmatter["tools"]
    assert "plan-only" in text
    assert "tmp/superpowers/plans/" in text
    assert (
        "must not edit source, test, configuration, build, or dependency files"
        in text
    )
    assert "execute remediation" not in text


MANDATORY_REVIEW_SKILLS = (
    "internal-review-code",
    "addyosmani-code-review-and-quality",
)


def test_code_agent_requires_exactly_two_review_skills() -> None:
    text = CODE_AGENT.read_text(encoding="utf-8")
    section = text.split("## Mandatory Review Skills", 1)[1].split("\n## ", 1)[0]
    listed = tuple(
        line.strip().removeprefix("- `").removesuffix("`")
        for line in section.splitlines()
        if line.strip().startswith("- `")
    )

    assert listed == MANDATORY_REVIEW_SKILLS


def test_code_agent_load_gate_is_fail_closed_and_provenance_based() -> None:
    text = CODE_AGENT.read_text(encoding="utf-8")

    assert "NEEDS INVESTIGATION" in text
    assert "model identifier" in text
    assert "target fingerprint" in text
    assert "skill identities" in text
    assert "resolved sources" in text
    assert "Entry modes" in text
    assert "agent-mediated" in text
    assert "delegat" in text.lower()
    assert "Before substantive review, perform this observable load gate:" not in text


def test_code_agent_can_attest_load_gate_without_delegation_tool() -> None:
    text = CODE_AGENT.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())
    frontmatter = _agent_frontmatters()[0]

    assert "agent" not in frontmatter["tools"]
    assert frontmatter["agents"] == []
    assert "perform this observable load gate directly" in normalized_text
    assert "Delegation may be used when available" in normalized_text
    assert "is not required" in normalized_text
    assert "delegate the mandatory-skill load gate" not in normalized_text


def test_code_agent_gate_wording_does_not_presume_delegation() -> None:
    text = CODE_AGENT.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())

    assert "The delegated gate" not in normalized_text
    assert "This gate verifies model behavior" in normalized_text
    assert "does not claim platform-level eager preload" in normalized_text


def test_code_agent_delegates_severity_mapping_to_skill() -> None:
    text = CODE_AGENT.read_text(encoding="utf-8")

    assert "Map Critical findings" not in text


def test_code_agent_delegates_public_projection_to_skill() -> None:
    text = CODE_AGENT.read_text(encoding="utf-8")

    assert "skill's public projection" in text
