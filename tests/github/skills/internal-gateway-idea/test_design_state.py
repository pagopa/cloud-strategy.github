from __future__ import annotations

import importlib.util
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = REPO_ROOT / ".github/skills/internal-gateway-idea/scripts/idea_state.py"
FIXTURES = Path(__file__).parent / "fixtures"


def _load_module():
    assert MODULE_PATH.exists(), f"missing state module: {MODULE_PATH}"
    spec = importlib.util.spec_from_file_location("idea_state", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_text() -> str:
    return (FIXTURES / "design-valid.md").read_text(encoding="utf-8")


def _parse(module, text: str | None = None):
    return module.parse_design_document(text or _valid_text(), expected_slug="sample")


def _draft_document(module, *, assurance: str = "standard"):
    document = _parse(module)
    return replace(
        document,
        header=replace(
            document.header,
            assurance=assurance,
            assurance_reason="Explicit test assurance state.",
            status="under-review",
            reviewed_revision=None,
            approved_revision=None,
            review_sources=(),
            next_actor="critic",
            next_action="Run the required review for the current revision.",
        ),
    )


def _high_text() -> str:
    return (
        _valid_text()
        .replace("assurance: standard", "assurance: high")
        .replace(
            "assurance_reason: No high assurance trigger applies.",
            "assurance_reason: Explicit high-assurance fixture.",
        )
        .replace(
            "review_sources: [standard]",
            "review_sources: [standard, independent]",
        )
    )


def test_valid_document_covers_both_lane_shape_and_sections() -> None:
    module = _load_module()

    document = _parse(module)

    assert document.header.lane == "shape-idea"
    assert document.header.status == "awaiting-final-approval"
    assert document.header.revision == 2
    assert set(document.sections) >= {
        "Context and Goal",
        "Decisions and Rationale",
        "Scope and Coverage",
        "Design",
        "Validation and Handoff",
        "Review Ledger",
        "Risks and Open Questions",
        "Continuation",
    }
    assert document.coverage_rows[0].requirement_id == "D-001"


def test_review_existing_requires_a_source_baseline() -> None:
    module = _load_module()
    text = _valid_text().replace("lane: shape-idea", "lane: review-existing").replace(
        "source_baseline: Current idea gateway and critical-master contracts.",
        "source_baseline: null",
    )

    with pytest.raises(module.DesignValidationError):
        _parse(module, text)


@pytest.mark.parametrize("review_sources", ("[unknown]", "[standard, standard]"))
def test_header_review_sources_reject_unknown_or_duplicate_values(
    review_sources: str,
) -> None:
    module = _load_module()
    text = _valid_text().replace(
        "review_sources: [standard]", f"review_sources: {review_sources}"
    )

    with pytest.raises(module.DesignValidationError):
        _parse(module, text)


@pytest.mark.parametrize(
    "change",
    (
        ("revision: 2", "revision: true"),
        ("status: awaiting-final-approval", "status: invalid"),
        ("next_actor: user", "next_actor: critic"),
        ("reviewed_revision: 2", "reviewed_revision: 1"),
        ("approved_revision: null", "approved_revision: 1"),
    ),
)
def test_invalid_header_values_and_stale_state_fail_closed(
    change: tuple[str, str],
) -> None:
    module = _load_module()
    text = _valid_text().replace(*change)

    with pytest.raises(module.DesignValidationError):
        _parse(module, text)


def test_invalid_fixture_rejects_missing_sections_and_bad_revision() -> None:
    module = _load_module()

    with pytest.raises(module.DesignValidationError):
        _parse(module, (FIXTURES / "design-invalid.md").read_text(encoding="utf-8"))


def test_material_change_increments_revision_and_clears_approval() -> None:
    module = _load_module()
    document = _parse(module)

    changed = module.apply_material_change(document, central_change=True)

    assert changed.header.revision == 3
    assert changed.header.reviewed_revision is None
    assert changed.header.approved_revision is None
    assert changed.header.status == "analyzing"
    assert changed.header.next_actor == "agent"


def test_persisted_standard_review_sources_survive_clean_chat_round_trip() -> None:
    module = _load_module()
    document = _parse(module)
    resumed = module.parse_design_document(document.raw_text, expected_slug="sample")

    assert resumed.header.review_sources == ("standard",)
    assert module.can_complete_review(resumed)
    assert module.can_finalize_approval(resumed)


def test_persisted_high_review_sources_survive_clean_chat_round_trip() -> None:
    module = _load_module()
    document = module.parse_design_document(_high_text(), expected_slug="sample")
    resumed = module.parse_design_document(document.raw_text, expected_slug="sample")

    assert resumed.header.assurance == "high"
    assert resumed.header.review_sources == ("standard", "independent")
    assert module.can_finalize_approval(resumed)


def test_missing_review_sources_deny_approval_and_handoff() -> None:
    module = _load_module()
    document = _parse(module)
    missing = replace(document, header=replace(document.header, review_sources=()))
    approved_missing = replace(
        missing,
        header=replace(
            missing.header,
            status="approved",
            approved_revision=missing.header.revision,
            next_actor="plan-writer",
            next_action="Write the approved implementation plan.",
        ),
    )

    assert not module.can_complete_review(missing)
    assert not module.can_finalize_approval(missing)
    assert not module.can_handoff(approved_missing)


@pytest.mark.parametrize("central_change", (False, True))
def test_material_change_clears_persisted_review_sources(central_change: bool) -> None:
    module = _load_module()
    changed = module.apply_material_change(
        _parse(module), central_change=central_change
    )

    assert changed.header.revision == 3
    assert changed.header.review_sources == ()
    assert changed.header.approved_revision is None


def test_open_findings_are_persistable_but_block_review_approval_and_handoff() -> None:
    module = _load_module()
    text = _valid_text().replace("| false | design-valid.md#L50 | closed |", "| true | design-valid.md#L50 | open |")
    document = _parse(module, text)

    assert document.open_findings
    assert not module.can_complete_review(document)
    assert not module.can_finalize_approval(document)
    assert not module.can_handoff(document)


def test_clean_chat_resume_uses_only_current_document_state() -> None:
    module = _load_module()
    document = _parse(module)

    route = module.resume_route(document)

    assert route.next_actor == "user"
    assert "Approve" in route.next_action
    assert route.source == "design.md"
