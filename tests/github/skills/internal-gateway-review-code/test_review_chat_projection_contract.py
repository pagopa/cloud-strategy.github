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


def test_review_agents_define_complete_material_findings() -> None:
    for text in _agent_texts():
        for field in MATERIAL_FIELDS:
            assert field in text
        assert "consolidate equivalent findings" in text
        assert "show every blocking and important finding" in text


def test_review_agents_hide_legacy_internal_sections() -> None:
    for text in _agent_texts():
        for heading in LEGACY_PUBLIC_SECTIONS:
            assert heading not in text


def test_review_agents_require_manual_remediation_selection() -> None:
    for text in _agent_texts():
        assert "separate follow-up" in text
        assert "no changes were applied" in text
        assert "review pass is report-only" in text
        assert "explicitly selects" in text
        assert "finding IDs" in text


def test_review_agents_can_edit_an_explicitly_selected_remediation() -> None:
    for frontmatter in _agent_frontmatters():
        assert "edit" in frontmatter["tools"]
