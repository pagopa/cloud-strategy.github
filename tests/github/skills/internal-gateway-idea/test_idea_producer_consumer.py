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
ADAPTER_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-idea/scripts/critical_report_adapter.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("idea_state_consumer_v2", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_adapter():
    spec = importlib.util.spec_from_file_location(
        "critical_report_adapter", ADAPTER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _state(
    module,
    *,
    state: str = "WAIT_G3",
    assurance: str = "standard",
    sources: tuple[str, ...] = (),
):
    return module.StateV2(
        schema="internal-gateway-idea-state/v2",
        slug="sample",
        revision=1,
        state=state,
        design_sha256="a" * 64,
        assurance=assurance,
        review_sources=sources,
        reviewed_revision=1 if state in {"WAIT_G4", "WAIT_G5", "APPROVED"} else None,
        approved_revision=1 if state == "APPROVED" else None,
    )


def _packet(
    source: str = "standard",
    *,
    outcome: str = "accepted",
    recommendation: str = "Keep the typed event boundary.",
    blocking: bool = False,
    diagnostics: list[str] | None = None,
) -> dict[str, object]:
    return {
        "schema": "internal-gateway-critical/full-analysis-v1",
        "source": source,
        "target_path": "tmp/idea/sample/design.md",
        "target_revision": 1,
        "outcome": outcome,
        "findings": [
            {
                "id": "C-001",
                "critique": "The current control needs explicit evidence.",
                "recommendation": recommendation,
                "reason": "The state must fail closed.",
                "blocking": blocking,
                "evidence": ["design.md#L1"],
            }
        ],
        "residual_risks": [],
        "diagnostics": diagnostics or [],
    }


def test_packet_shape_and_target_binding_fail_closed() -> None:
    module = _load_module()
    packet = _packet()
    packet["unknown"] = True
    with pytest.raises(module.DesignValidationError):
        module.record_review(
            _state(module),
            packet,
            g3_approval_event=module.TypedEvent("approve", {}),
            expected_target_path="tmp/idea/sample/design.md",
            expected_revision=1,
        )

    wrong_target = _packet()
    wrong_target["target_revision"] = 2
    with pytest.raises(module.DesignValidationError):
        module.record_review(
            _state(module),
            wrong_target,
            g3_approval_event=module.TypedEvent("approve", {}),
            expected_target_path="tmp/idea/sample/design.md",
            expected_revision=1,
        )


def test_record_review_requires_current_turn_g3_approval_and_enters_wait_g4() -> None:
    module = _load_module()
    reviewed = module.record_review(
        _state(module),
        _packet(),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )

    assert reviewed.state == "WAIT_G4"
    assert reviewed.reviewed_revision == reviewed.revision
    assert reviewed.approved_revision is None
    assert reviewed.review_sources == ("standard",)


def test_standalone_packet_cannot_advance_persisted_wait_g3() -> None:
    module = _load_module()
    with pytest.raises(module.DesignValidationError):
        module.consume_full_analysis_packet(
            _state(module),
            _packet(),
            expected_target_path="tmp/idea/sample/design.md",
            expected_revision=1,
            mandatory=True,
        )


def test_malformed_or_interrupted_critic_keeps_wait_g3_authoritative() -> None:
    module = _load_module()
    state = _state(module)
    malformed = _packet()
    malformed["findings"] = [{"id": "C-001", "blocking": "yes"}]
    with pytest.raises(module.DesignValidationError):
        module.record_review(
            state,
            malformed,
            g3_approval_event=module.TypedEvent("approve", {}),
            expected_target_path="tmp/idea/sample/design.md",
            expected_revision=1,
        )
    assert state.state == "WAIT_G3"
    assert state.review_sources == ()
    assert state.reviewed_revision is None


def test_invalid_target_packet_cannot_advance_review() -> None:
    module = _load_module()
    packet = _packet(outcome="invalid-target", diagnostics=["No analysable context."])

    with pytest.raises(module.DesignValidationError):
        module.record_review(
            _state(module),
            packet,
            g3_approval_event=module.TypedEvent("approve", {}),
            expected_target_path="tmp/idea/sample/design.md",
            expected_revision=1,
        )


def test_readable_report_is_adapted_and_recorded_in_one_consumer_call() -> None:
    module = _load_module()
    _load_adapter()
    report = """# Critical Analysis

## Scope
Review the typed event boundary.

## Assessment
The boundary is sound.

### Evidence 1 — Explicit state transition
**Critique:** The transition must remain typed.
**Evidence:** The gateway validates event names and payloads.
**Suggestion:** Keep the typed event boundary.
**Why:** It prevents free-form input from advancing state.
**Impact:** An untyped transition could bypass governance.
**Blocking:** false

## Conclusion
**Outcome:** accepted
**Summary:** The current boundary can proceed.
"""

    reviewed = module.record_readable_review(
        _state(module),
        report,
        source="standard",
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )

    assert reviewed.state == "WAIT_G4"
    assert reviewed.review_sources == ("standard",)
    assert reviewed.reviewed_revision == 1


def test_high_assurance_requires_both_review_sources() -> None:
    module = _load_module()
    state = _state(module, assurance="high")
    after_standard = module.record_review(
        state,
        _packet("standard"),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    assert after_standard.state == "WAIT_G3"
    assert after_standard.review_sources == ("standard",)
    assert after_standard.reviewed_revision is None

    after_independent = module.record_review(
        after_standard,
        _packet("independent"),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    assert after_independent.state == "WAIT_G4"
    assert after_independent.review_sources == ("standard", "independent")


def test_duplicate_review_source_is_rejected() -> None:
    module = _load_module()
    reviewed = module.record_review(
        _state(module, assurance="high"),
        _packet(),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    with pytest.raises(module.DesignValidationError):
        module.record_review(
            reviewed,
            _packet(),
            g3_approval_event=module.TypedEvent("approve", {}),
            expected_target_path="tmp/idea/sample/design.md",
            expected_revision=1,
        )


def test_equivalent_findings_merge_sources_and_evidence() -> None:
    module = _load_module()
    first = module.record_review(
        _state(module, assurance="high"),
        _packet("standard"),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    second_packet = _packet("independent")
    second_packet["findings"][0]["evidence"] = ["design.md#L2"]  # type: ignore[index]
    second = module.record_review(
        first,
        second_packet,
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )

    assert len(second.ledger) == 1
    assert second.ledger[0].sources == ("standard", "independent")
    assert set(second.ledger[0].evidence) == {"design.md#L1", "design.md#L2"}


def test_conflicting_recommendations_remain_open() -> None:
    module = _load_module()
    first = module.record_review(
        _state(module, assurance="high"),
        _packet("standard"),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    second = module.record_review(
        first,
        _packet("independent", recommendation="Replace the boundary."),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    assert len(second.ledger) == 2
    assert all(item.conflict for item in second.ledger)
    unresolved = module.resolve_review(
        second,
        disposition="open",
        remedy=None,
        risk_decision=None,
    )
    assert unresolved.state == "WAIT_G3"
    assert unresolved.revision == second.revision + 1


def test_advisory_packet_is_non_mandatory_and_cannot_set_review_claims() -> None:
    module = _load_module()
    advisory = module.start_advisory(
        _state(module, state="WAIT_G0"),
        prior_gate="WAIT_G0",
    )
    result = module.consume_full_analysis_packet(
        advisory,
        _packet(),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
        mandatory=False,
    )
    assert result.state.state == "ADVISORY_REVIEW"
    assert result.state.review_sources == ()
    assert result.state.reviewed_revision is None
    assert result.state.approved_revision is None


def test_advisory_review_returns_to_exact_prior_gate() -> None:
    module = _load_module()
    reviewing = module.start_advisory(
        _state(module, state="WAIT_G1"), prior_gate="WAIT_G1"
    )
    resumed = module.finish_advisory(reviewing)
    assert reviewing.state == "ADVISORY_REVIEW"
    assert resumed.state == "WAIT_G1"
    assert resumed.review_sources == ()
    assert resumed.reviewed_revision is None


def test_g4_resolution_is_separate_from_g3_packet_ingestion() -> None:
    module = _load_module()
    reviewed = module.record_review(
        _state(module),
        _packet(),
        g3_approval_event=module.TypedEvent("approve", {}),
        expected_target_path="tmp/idea/sample/design.md",
        expected_revision=1,
    )
    resolved = module.resolve_review(
        reviewed,
        disposition="closed",
        remedy={"action": "retain"},
        risk_decision={"accepted": True},
    )
    assert resolved.state == "WAIT_G5"
    assert resolved.approved_revision is None

    approval = module.transition_gate(
        resolved,
        module.TypedEvent("approve", {"token": "ok"}),
        gate="WAIT_G5",
    )
    assert approval.accepted is True
    assert approval.state.state == "APPROVED"
    route = module.derive_route(approval.state)
    assert route.next_actor == "user"
    assert route.next_owner == "/internal-gateway-idea"
    assert route.legal_events == ("select-handoff",)
    assert route.authorizes_execution is False


@pytest.mark.parametrize(
    (
        "mode",
        "expected_state",
        "expected_actor",
        "expected_owner",
        "authorizes_execution",
    ),
    (
        (
            "implementation-plan",
            "PLAN_WRITING",
            "plan-writer",
            "/internal-gateway-writing-plans",
            False,
        ),
        (
            "direct-execution",
            "DIRECT_EXECUTION",
            "task-executor",
            "/internal-gateway-simple-task",
            True,
        ),
    ),
)
def test_explicit_handoff_choice_selects_one_terminal_owner(
    mode: str,
    expected_state: str,
    expected_actor: str,
    expected_owner: str,
    authorizes_execution: bool,
) -> None:
    module = _load_module()
    approved = _state(module, state="APPROVED", sources=("standard",))

    result = module.transition_gate(
        approved,
        module.TypedEvent("select-handoff", {"mode": mode}),
        gate="APPROVED",
    )

    assert result.accepted is True
    assert result.state.state == expected_state
    route = module.derive_route(result.state)
    assert route.next_actor == expected_actor
    assert route.next_owner == expected_owner
    assert route.authorizes_execution is authorizes_execution


def test_invalid_handoff_choice_fails_closed_without_state_change() -> None:
    module = _load_module()
    approved = _state(module, state="APPROVED", sources=("standard",))

    result = module.transition_gate(
        approved,
        module.TypedEvent("select-handoff", {"mode": "guess"}),
        gate="APPROVED",
    )

    assert result.accepted is False
    assert result.state == approved


def test_material_revision_cannot_enter_g5() -> None:
    module = _load_module()
    state = _state(module, state="WAIT_G4")
    changed = replace(state, revision=2, reviewed_revision=1)
    assert not module.can_enter_g5(changed, "a" * 64)
