from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
MODULE_PATH = REPO_ROOT / ".github/skills/internal-gateway-idea/scripts/idea_state.py"
FIXTURE = Path(__file__).parent / "fixtures/design-valid.md"


def _load_module():
    assert MODULE_PATH.exists(), f"missing state module: {MODULE_PATH}"
    spec = importlib.util.spec_from_file_location("idea_state_consumer", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _document(module):
    return module.parse_design_document(
        FIXTURE.read_text(encoding="utf-8"), expected_slug="sample"
    )


def _packet(
    source: str,
    *,
    outcome: str = "accepted",
    findings: list[dict[str, object]] | None = None,
    diagnostics: list[str] | None = None,
) -> dict[str, object]:
    return {
        "schema": "internal-gateway-critical/full-analysis-v1",
        "source": source,
        "target_path": "tmp/idea/sample/design.md",
        "target_revision": 2,
        "outcome": outcome,
        "findings": findings or [],
        "residual_risks": [],
        "diagnostics": diagnostics or [],
    }


def _finding(
    *,
    recommendation: str = "Keep the compact contract.",
    reason: str = "The design must retain a reviewable proof.",
    blocking: bool = False,
    evidence: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": "C-001",
        "critique": "The current control needs explicit evidence.",
        "recommendation": recommendation,
        "reason": reason,
        "blocking": blocking,
        "evidence": evidence or ["design.md#L12"],
    }


def test_standard_and_independent_packets_consolidate_to_one_canonical_finding() -> None:
    module = _load_module()
    document = _document(module)

    reviewed = module.apply_review_precedence(
        document,
        [
            _packet(
                "standard",
                outcome="revise-design",
                findings=[_finding(evidence=["design.md#L12"])],
            ),
            _packet(
                "independent",
                outcome="revise-design",
                findings=[_finding(blocking=True, evidence=["design.md#L18"])],
            ),
        ],
        required_independent=True,
    )

    assert reviewed.header.reviewed_revision is None
    assert reviewed.header.status == "awaiting-remedy-decision"
    assert len(reviewed.ledger) == 2
    merged = next(item for item in reviewed.ledger if item.id == "F-002")
    assert merged.blocking is True
    assert set(merged.sources) == {"standard", "independent"}
    assert set(merged.evidence) == {"design.md#L12", "design.md#L18"}


def test_conflicting_recommendations_remain_separate_and_open() -> None:
    module = _load_module()
    document = _document(module)
    packets = [
        _packet(
            "standard", findings=[_finding(recommendation="Keep the compact contract.")]
        ),
        _packet(
            "independent",
            findings=[_finding(recommendation="Replace the contract entirely.")],
        ),
    ]

    reviewed = module.apply_review_precedence(
        document, packets, required_independent=True
    )

    assert len(reviewed.ledger) == 3
    assert sum(item.disposition == "open" for item in reviewed.ledger) >= 2
    assert not module.can_complete_review(reviewed)


@pytest.mark.parametrize(
    ("outcome", "expected_status", "expected_actor"),
    (
        ("needs-clarification", "awaiting-decisions", "user"),
        ("reopen-analysis", "analyzing", "agent"),
        ("revise-design", "awaiting-remedy-decision", "user"),
    ),
)
def test_review_precedence_routes_outcomes_without_automatic_loops(
    outcome: str, expected_status: str, expected_actor: str
) -> None:
    module = _load_module()
    document = _document(module)

    routed = module.apply_review_precedence(
        document,
        [
            _packet(
                "standard",
                outcome=outcome,
                findings=[
                    _finding(
                        blocking=True,
                        reason=(
                            "The unresolved user decision needs one bounded answer."
                            if outcome == "needs-clarification"
                            else "The design must retain a reviewable proof."
                        ),
                    )
                ],
            )
        ],
        required_independent=False,
    )

    assert routed.header.status == expected_status
    assert routed.header.next_actor == expected_actor
    assert routed.header.revision == 2


def test_missing_independent_packet_fails_closed() -> None:
    module = _load_module()

    routed = module.apply_review_precedence(
        _document(module), [_packet("standard")], required_independent=True
    )

    assert routed.header.status == "awaiting-independent-review"
    assert routed.header.next_actor == "user"
    assert routed.header.reviewed_revision is None


def test_public_critique_is_numbered_and_does_not_expose_packet_json() -> None:
    module = _load_module()
    findings = module.consolidate_findings(
        [],
        [
            module.NormalizedFinding(
                critique="A control is missing.",
                recommendation="Add the control.",
                reason="Evidence is incomplete.",
                blocking=True,
                source="standard",
                evidence=("design.md#L12",),
                equivalence_key="control-missing",
            )
        ],
    )

    rendered = module.render_public_critique(findings)

    assert "1." in rendered
    assert "Critica:" in rendered
    assert "Suggerimento:" in rendered
    assert "Perché:" in rendered
    assert "Bloccante: si" in rendered
    assert '"schema"' not in rendered


@pytest.mark.parametrize(
    ("signals", "expected"),
    (
        ({"destructive": True}, "high"),
        ({"security": True}, "high"),
        ({"unknown_platform_claim": True}, "high"),
        ({"independent_owners": 3}, "high"),
        ({"feasibility_unknown": True}, "high"),
        ({"explicit_user_request": True}, "high"),
        ({"destructive": False, "security": False}, "standard"),
    ),
)
def test_assurance_triggers_and_near_miss_are_explicit(
    signals: dict[str, object], expected: str
) -> None:
    module = _load_module()

    assert module.determine_assurance(signals) == expected


def test_final_approval_separates_design_plan_and_execution() -> None:
    module = _load_module()
    document = _document(module)

    approval = module.route_final_approval(document, "approvo")
    plan_route = module.route_final_approval(document, "approvo e scrivi il piano")
    later_plan_route = module.route_final_approval(document, "scrivi il piano")

    assert approval.approved is True
    assert approval.next_actor == "none"
    assert plan_route.next_actor == "plan-writer"
    assert later_plan_route.next_actor == "plan-writer"
    assert approval.authorizes_execution is False
    assert plan_route.authorizes_execution is False
    assert later_plan_route.authorizes_execution is False


@pytest.mark.parametrize(
    ("prompt", "owner"),
    (
        ("shape this repository idea and compare alternatives", "internal-gateway-idea"),
        ("review this completed architecture independently", "internal-review-high-level"),
        ("challenge this design with a full critical analysis", "internal-gateway-critical-master"),
        ("implement this small bounded repository task", "internal-gateway-simple-task"),
    ),
)
def test_routing_cases_have_one_nearest_owner(prompt: str, owner: str) -> None:
    module = _load_module()

    route = module.resolve_route(prompt)

    assert route.owner == owner
    assert route.competing_owners == ()


def test_clean_chat_route_has_no_automatic_implementation_transition() -> None:
    module = _load_module()
    route = module.route_final_approval(_document(module), "approvo e scrivi il piano")

    assert route.next_actor == "plan-writer"
    assert route.authorizes_execution is False
