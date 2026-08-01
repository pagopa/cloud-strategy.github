"""Resolve post-critical transitions for the codebase-improvement gateway."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChallengeState:
    approved_cycle: int
    approved_packet_id: str
    critical_cycle: int
    challenged_packet_id: str
    outcome: str
    defense: str
    material_objection: bool
    unresolved_uncertainty: bool
    evidence_status: str
    recovery_attempted: bool


@dataclass(frozen=True)
class TransitionDecision:
    next_state: str
    approval_invalidated: bool
    reason: str
    stop_report: dict[str, str]


TERMINAL_EVIDENCE_STATES = frozenset(
    {"unavailable", "unsafe", "out-of-scope", "declined"}
)

STOP_REPORT_KEYS = (
    "what_happened",
    "recovery_attempted",
    "evidence_unavailable_reason",
    "approval_status",
    "consequence",
    "resume_condition",
)


def _stop_report(state: ChallengeState, reason: str) -> dict[str, str]:
    if state.recovery_attempted:
        recovery = (
            "The single bounded evidence-recovery attempt was already used; "
            "no second attempt is permitted."
        )
    else:
        recovery = (
            "No evidence-recovery attempt was made because the current stop "
            "condition is terminal or outside this gateway."
        )

    evidence_reason = {
        "unavailable": "Required evidence is unavailable in the current context.",
        "unsafe": "Retrieving the required evidence would be unsafe.",
        "out-of-scope": "Retrieving the required evidence is outside the approved scope.",
        "declined": "The user declined the required evidence-recovery action.",
        "missing-recoverable": "The bounded recovery attempt did not produce the required evidence.",
        "clear": "The request is outside this gateway; no evidence gap is being resolved here.",
    }.get(state.evidence_status, "Required evidence remains unavailable for this transition.")

    return {
        "what_happened": reason,
        "recovery_attempted": recovery,
        "evidence_unavailable_reason": evidence_reason,
        "approval_status": (
            "Approval for the current cycle and packet is invalidated; fresh approval is required."
        ),
        "consequence": (
            "The gateway stops without marking the challenged design ready and without invoking a planning owner."
        ),
        "resume_condition": (
            "Resume only with the required evidence or an explicit user decision, then rerun analysis and obtain fresh approval."
        ),
    }


def _stop(state: ChallengeState, reason: str) -> TransitionDecision:
    return TransitionDecision(
        next_state="stop-with-reason",
        approval_invalidated=True,
        reason=reason,
        stop_report=_stop_report(state, reason),
    )


def resolve_transition(state: ChallengeState) -> TransitionDecision:
    """Return the deterministic next state for a challenged gateway result."""
    binding_missing = (
        not state.approved_cycle
        or not state.critical_cycle
        or not state.approved_packet_id.strip()
        or not state.challenged_packet_id.strip()
    )
    binding_mismatch = (
        state.approved_cycle != state.critical_cycle
        or state.approved_packet_id != state.challenged_packet_id
    )
    if binding_missing or binding_mismatch:
        return TransitionDecision(
            next_state="analysis",
            approval_invalidated=True,
            reason="The approved cycle or packet binding is missing or mismatched.",
            stop_report={},
        )

    if state.outcome == "de-escalate-to-simple":
        return _stop(
            state,
            "The request de-escalates to a simple task outside this gateway.",
        )

    if state.evidence_status in TERMINAL_EVIDENCE_STATES:
        return _stop(
            state,
            "Required evidence cannot be safely or permissibly obtained in this cycle.",
        )

    if state.evidence_status == "missing-recoverable":
        if state.recovery_attempted:
            return _stop(
                state,
                "The recoverable evidence gap remains after the single bounded recovery attempt.",
            )
        return TransitionDecision(
            next_state="analysis",
            approval_invalidated=True,
            reason="A recoverable evidence gap remains and one bounded recovery attempt is available.",
            stop_report={},
        )

    if (
        state.outcome == "route-to-execution-owner"
        and state.defense in {"none", "resolves"}
        and not state.material_objection
        and not state.unresolved_uncertainty
        and state.evidence_status == "clear"
    ):
        return TransitionDecision(
            next_state="challenged-design-ready",
            approval_invalidated=False,
            reason="The current-cycle critical result matches the approved packet and is challenge-ready.",
            stop_report={},
        )

    return TransitionDecision(
        next_state="analysis",
        approval_invalidated=True,
        reason="The critical result remains open or carries accepted risk.",
        stop_report={},
    )


__all__ = [
    "ChallengeState",
    "STOP_REPORT_KEYS",
    "TERMINAL_EVIDENCE_STATES",
    "TransitionDecision",
    "resolve_transition",
]
