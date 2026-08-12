#!/usr/bin/env python3
"""Fail-closed state and persistence owner for the idea gateway v2 contract.

The runtime contract has exactly two stable artifacts: ``design.md`` and
``state.json``.  The JSON state is deliberately small; actor, legal events,
and event payloads are derived or transient.  Design and state are replaced
individually, in that order, so a crash between replacements is recovered as a
hash mismatch rather than guessed into forward progress.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_V2 = "internal-gateway-idea-state/v2"
SCHEMA = SCHEMA_V2
PACKET_SCHEMA = "internal-gateway-critical/full-analysis-v1"
PLAN_WRITING = "PLAN_WRITING"
DIRECT_EXECUTION = "DIRECT_EXECUTION"
HANDOFF_MODES = frozenset({"implementation-plan", "direct-execution"})
TERMINAL_STATES = frozenset({PLAN_WRITING, DIRECT_EXECUTION})

STATES = frozenset(
    {
        "WAIT_G0",
        "WAIT_G1",
        "WAIT_G2",
        "WAIT_G3",
        "WAIT_G4",
        "WAIT_G5",
        "APPROVED",
        PLAN_WRITING,
        DIRECT_EXECUTION,
        "ADVISORY_REVIEW",
    }
)
GATES = ("G0", "G1", "G2", "G3", "G4", "G5")
ASSURANCES = frozenset({"standard", "high"})
REVIEW_SOURCES = frozenset({"standard", "independent"})
SHORT_APPROVALS = frozenset({"ok", "approvo", "continua", "va bene", "procedi"})
DISPOSITIONS = frozenset(
    {"open", "closed", "accepted-remedy", "accepted-risk", "reopen-analysis"}
)
PACKET_OUTCOMES = frozenset(
    {
        "accepted",
        "revise-design",
        "reopen-analysis",
        "needs-clarification",
        "invalid-target",
        "request-separate-review",
    }
)
PACKET_KEYS = frozenset(
    {
        "schema",
        "source",
        "target_path",
        "target_revision",
        "outcome",
        "findings",
        "residual_risks",
        "diagnostics",
    }
)
PACKET_FINDING_KEYS = frozenset(
    {"id", "critique", "recommendation", "reason", "blocking", "evidence"}
)
PACKET_FINDING_ID = re.compile(r"^C-[0-9]{3}$")
LEDGER_FINDING_ID = re.compile(r"^F-[0-9]{3}$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

PERSISTED_KEYS = frozenset(
    {
        "schema",
        "slug",
        "revision",
        "state",
        "design_sha256",
        "assurance",
        "review_sources",
        "reviewed_revision",
        "approved_revision",
        "advisory_return_state",
    }
)
REQUIRED_PERSISTED_KEYS = PERSISTED_KEYS - {"advisory_return_state"}

PRE_G3_SECTIONS = (
    "Intent",
    "Accepted Decisions",
    "Open Decisions",
    "Selected Approach",
    "Essential Evidence",
)


class DesignValidationError(ValueError):
    """Raised when state, design, event, or packet evidence is unsafe."""


class StateValidationError(DesignValidationError):
    """More specific alias for strict persisted-state failures."""


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_integer(value: object) -> bool:
    return type(value) is int and value > 0


def _is_non_negative_integer(value: object) -> bool:
    return type(value) is int and value >= 0


def _string_array(value: object, name: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise DesignValidationError(f"{name} must be an array of strings")
    values: list[str] = []
    for item in value:
        if not _is_non_empty_string(item):
            raise DesignValidationError(f"{name} must contain non-empty strings")
        assert isinstance(item, str)
        values.append(item.strip())
    if len(set(values)) != len(values):
        raise DesignValidationError(f"{name} must not contain duplicates")
    if not allow_empty and not values:
        raise DesignValidationError(f"{name} must not be empty")
    return tuple(values)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise DesignValidationError(f"{name} must be an object")
    if any(not isinstance(key, str) for key in value):
        raise DesignValidationError(f"{name} keys must be strings")
    return value  # type: ignore[return-value]


def _strict_json_loads(payload: str) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise StateValidationError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    try:
        return json.loads(payload, object_pairs_hook=reject_duplicates)
    except StateValidationError:
        raise
    except json.JSONDecodeError as error:
        raise StateValidationError(f"invalid JSON: {error.msg}") from error


@dataclass(frozen=True)
class ReviewFinding:
    """A consolidated, packet-free row in the design ledger."""

    id: str
    source: str
    sources: tuple[str, ...]
    critique: str
    recommendation: str
    reason: str
    blocking: bool
    evidence: tuple[str, ...]
    disposition: str = "open"
    conflict: bool = False
    equivalence_key: str = ""


@dataclass(frozen=True)
class StateV2:
    schema: str
    slug: str
    revision: int
    state: str
    design_sha256: str
    assurance: str
    review_sources: tuple[str, ...]
    reviewed_revision: int | None
    approved_revision: int | None
    advisory_return_state: str | None = None
    # These fields are transient and are intentionally omitted from state.json.
    ledger: tuple[ReviewFinding, ...] = field(default_factory=tuple, compare=True)
    design_text: str | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class TypedEvent:
    name: str
    payload: Mapping[str, object] = field(default_factory=dict)

    @property
    def event_name(self) -> str:
        return self.name


@dataclass(frozen=True)
class PresentedDecision:
    event_name: str
    default_payload: Mapping[str, object] | None
    gate: str


@dataclass(frozen=True)
class Route:
    state: str
    next_actor: str
    next_owner: str
    legal_events: tuple[str, ...]
    next_action: str
    authorizes_execution: bool = False

    @property
    def owner(self) -> str:
        return self.next_owner


@dataclass(frozen=True)
class TransitionResult:
    state: StateV2
    accepted: bool
    legal_events: tuple[str, ...]
    reason: str | None = None

    @property
    def next_state(self) -> StateV2:
        return self.state


@dataclass(frozen=True)
class RuntimeSnapshot:
    state: StateV2
    root: Path | None = None
    design_text: str | None = None
    recovery_reason: str | None = None
    stable_artifacts: tuple[str, ...] = ()


@dataclass(frozen=True)
class PacketResult:
    source: str
    target_path: str
    target_revision: int
    outcome: str
    findings: tuple[ReviewFinding, ...]
    residual_risks: tuple[str, ...]
    diagnostics: tuple[str, ...]


@dataclass(frozen=True)
class ReviewResult:
    state: StateV2
    source: str | None
    outcome: str | None
    findings: tuple[ReviewFinding, ...]
    residual_risks: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()


def _state_mapping(state: StateV2) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": state.schema,
        "slug": state.slug,
        "revision": state.revision,
        "state": state.state,
        "design_sha256": state.design_sha256,
        "assurance": state.assurance,
        "review_sources": list(state.review_sources),
        "reviewed_revision": state.reviewed_revision,
        "approved_revision": state.approved_revision,
    }
    if state.advisory_return_state is not None:
        payload["advisory_return_state"] = state.advisory_return_state
    return payload


def validate_state(value: Mapping[str, object], *, expected_slug: str) -> StateV2:
    """Validate the exact minimal v2 state object; never migrate v1 fields."""

    if not isinstance(value, Mapping):
        raise StateValidationError("state must be a JSON object")
    keys = set(value)
    if not REQUIRED_PERSISTED_KEYS.issubset(keys):
        missing = sorted(REQUIRED_PERSISTED_KEYS - keys)
        raise StateValidationError(f"state missing keys: {missing}")
    unknown = keys - PERSISTED_KEYS
    if unknown:
        raise StateValidationError(f"state has unknown keys: {sorted(unknown)}")
    if value.get("schema") != SCHEMA_V2:
        raise StateValidationError(f"schema must be {SCHEMA_V2}")
    slug = value.get("slug")
    if not isinstance(slug, str) or slug != expected_slug or not SLUG.fullmatch(slug):
        raise StateValidationError("state slug does not match the expected slug")

    state_name = value.get("state")
    if state_name not in STATES:
        raise StateValidationError("state is not a supported v2 state")
    revision = value.get("revision")
    if not _is_non_negative_integer(revision):
        raise StateValidationError("revision must be a non-negative integer")
    if state_name != "WAIT_G0" and revision == 0:
        raise StateValidationError("initialized state revision must be positive")

    design_hash = value.get("design_sha256")
    if not isinstance(design_hash, str) or (
        not SHA256.fullmatch(design_hash) and not (state_name == "WAIT_G0" and design_hash == "")
    ):
        raise StateValidationError("design_sha256 must be a 64-character hexadecimal hash")

    assurance = value.get("assurance")
    if assurance not in ASSURANCES:
        raise StateValidationError("assurance must be standard or high")

    sources = _string_array(value.get("review_sources"), "review_sources")
    if any(source not in REVIEW_SOURCES for source in sources):
        raise StateValidationError("review_sources contains an unknown source")

    reviewed = value.get("reviewed_revision")
    approved = value.get("approved_revision")
    if reviewed is not None and not _is_positive_integer(reviewed):
        raise StateValidationError("reviewed_revision must be a positive integer or null")
    if approved is not None and not _is_positive_integer(approved):
        raise StateValidationError("approved_revision must be a positive integer or null")
    if reviewed is not None and reviewed != revision:
        raise StateValidationError("reviewed_revision is stale")
    if approved is not None and approved != revision:
        raise StateValidationError("approved_revision is stale")
    if approved is not None and reviewed is None:
        raise StateValidationError("approved_revision requires reviewed_revision")

    advisory_return = value.get("advisory_return_state")
    if advisory_return is not None and advisory_return not in {
        "WAIT_G0",
        "WAIT_G1",
        "WAIT_G2",
        "WAIT_G3",
    }:
        raise StateValidationError("advisory_return_state is not a safe gate")
    if state_name == "ADVISORY_REVIEW":
        if advisory_return is None:
            raise StateValidationError("advisory review needs a return gate")
        if sources or reviewed is not None or approved is not None:
            raise StateValidationError("advisory review cannot claim mandatory review")
    elif advisory_return is not None:
        raise StateValidationError("advisory_return_state is only valid for advisory review")

    if state_name in {"WAIT_G0", "WAIT_G1", "WAIT_G2", "WAIT_G3"}:
        if sources or reviewed is not None or approved is not None:
            raise StateValidationError("early gate cannot claim later review or approval")
    if state_name in {"WAIT_G4", "WAIT_G5", "APPROVED"} | TERMINAL_STATES:
        if reviewed is None or not sources:
            raise StateValidationError("review gate requires current mandatory review evidence")
        if assurance == "high" and set(sources) != REVIEW_SOURCES:
            raise StateValidationError("high assurance requires standard and independent review")
    if state_name in {"APPROVED"} | TERMINAL_STATES and approved is None:
        raise StateValidationError("approved state requires current approval")
    if state_name not in {"APPROVED"} | TERMINAL_STATES and approved is not None:
        raise StateValidationError("approval can only be persisted in APPROVED")

    return StateV2(
        schema=SCHEMA_V2,
        slug=slug,
        revision=revision,
        state=state_name,
        design_sha256=design_hash,
        assurance=assurance,
        review_sources=sources,
        reviewed_revision=reviewed,
        approved_revision=approved,
        advisory_return_state=advisory_return,
    )


def serialize_state(state: StateV2) -> str:
    """Serialize only the canonical persisted state fields."""

    if state.schema != SCHEMA_V2:
        raise StateValidationError("only internal-gateway-idea-state/v2 can be persisted")
    return json.dumps(_state_mapping(state), sort_keys=True, separators=(",", ":")) + "\n"


def parse_state(payload: str | Mapping[str, object], *, expected_slug: str) -> StateV2:
    decoded = _strict_json_loads(payload) if isinstance(payload, str) else payload
    return validate_state(_mapping(decoded, "state"), expected_slug=expected_slug)


def _gate_for_state(state: str) -> str | None:
    if state in {"WAIT_G0"}:
        return "G0"
    if state in {"WAIT_G1"}:
        return "G1"
    if state in {"WAIT_G2"}:
        return "G2"
    if state in {"WAIT_G3"}:
        return "G3"
    if state in {"WAIT_G4"}:
        return "G4"
    if state in {"WAIT_G5"}:
        return "G5"
    return None


def _route_fields(state: StateV2) -> tuple[str, str, tuple[str, ...], str]:
    if state.state == "WAIT_G0":
        return (
            "user",
            "/internal-gateway-idea",
            ("resolve-g0", "approve"),
            "Submit typed G0 decisions or accept the presented default.",
        )
    if state.state == "WAIT_G1":
        return "user", "/internal-gateway-idea", ("approve",), "Approve G1 to continue."
    if state.state == "WAIT_G2":
        return (
            "user",
            "/internal-gateway-idea",
            ("select-approach", "approve"),
            "Submit the typed approach or accept the presented default.",
        )
    if state.state == "WAIT_G3":
        return (
            "user",
            "/internal-gateway-idea",
            ("approve",),
            "Approve G3; the current-turn critic boundary must complete before G4.",
        )
    if state.state == "WAIT_G4":
        return (
            "user",
            "/internal-gateway-idea",
            ("resolve-review", "approve"),
            "Submit the typed review resolution or accept the presented default.",
        )
    if state.state == "WAIT_G5":
        return (
            "user",
            "/internal-gateway-idea",
            ("approve",),
            "Approve G5 to hand off to writing-plans, then stop.",
        )
    if state.state == "APPROVED":
        return (
            "user",
            "/internal-gateway-idea",
            ("select-handoff",),
            "Choose direct execution through simple-task or implementation-plan writing.",
        )
    if state.state == PLAN_WRITING:
        return (
            "plan-writer",
            "/internal-gateway-writing-plans",
            (),
            "Writing-plans is the selected next owner; execution is not authorized.",
        )
    if state.state == DIRECT_EXECUTION:
        return (
            "task-executor",
            "/internal-gateway-simple-task",
            (),
            "Simple-task is the selected next owner; revalidate the bounded execution scope before acting.",
        )
    if state.state == "ADVISORY_REVIEW":
        return (
            "critic",
            "/internal-gateway-idea",
            ("finish-advisory",),
            "Finish the optional advisory and return to its recorded gate.",
        )
    return (
        "plan-writer",
        "/internal-gateway-writing-plans",
        (),
        "Writing-plans is the next owner; execution is not authorized.",
    )


def derive_route(state: StateV2) -> Route:
    actor, owner, events, action = _route_fields(state)
    return Route(
        state=state.state,
        next_actor=actor,
        next_owner=owner,
        legal_events=events,
        next_action=action,
        authorizes_execution=state.state == DIRECT_EXECUTION,
    )


def normalize_short_approval(message: str) -> str | None:
    """Normalize only whole-message short approvals and terminal punctuation."""

    if not isinstance(message, str):
        return None
    normalized = message.strip().casefold()
    if not normalized:
        return None
    normalized = normalized.rstrip(".!?")
    if normalized in SHORT_APPROVALS:
        return normalized
    return None


def _payload_keys(payload: Mapping[str, object], allowed: set[str], name: str) -> None:
    unknown = set(payload) - allowed
    if unknown:
        raise DesignValidationError(f"{name} has unknown keys: {sorted(unknown)}")


def _require_text(payload: Mapping[str, object], key: str, name: str) -> str:
    value = payload.get(key)
    if not _is_non_empty_string(value):
        raise DesignValidationError(f"{name}.{key} must be a non-empty string")
    assert isinstance(value, str)
    return value.strip()


def _require_group(payload: Mapping[str, object], keys: tuple[str, ...], name: str) -> object:
    for key in keys:
        if key in payload:
            value = payload[key]
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (list, tuple)):
                _string_array(value, f"{name}.{key}")
                return value
            raise DesignValidationError(f"{name}.{key} has an invalid type")
    raise DesignValidationError(f"{name} needs one of: {', '.join(keys)}")


def _validate_g0_payload(payload: Mapping[str, object]) -> None:
    allowed = {
        "intent",
        "goal",
        "accepted_decisions",
        "decisions",
        "open_decisions",
        "constraints",
        "success_criteria",
        "success",
        "validation",
        "anti_scope",
        "evidence",
        "assurance",
        "approach",
        "selected_approach",
    }
    _payload_keys(payload, allowed, "resolve-g0 payload")
    _require_group(payload, ("intent", "goal"), "resolve-g0 payload")
    _require_group(payload, ("accepted_decisions", "decisions"), "resolve-g0 payload")
    _require_group(payload, ("constraints",), "resolve-g0 payload")
    _require_group(payload, ("success_criteria", "success", "validation"), "resolve-g0 payload")
    _require_group(payload, ("anti_scope",), "resolve-g0 payload")
    if "open_decisions" in payload:
        _string_array(payload["open_decisions"], "resolve-g0 payload.open_decisions")
    if "evidence" in payload:
        _string_array(payload["evidence"], "resolve-g0 payload.evidence")


def _validate_approach_payload(payload: Mapping[str, object]) -> None:
    allowed = {
        "approach",
        "selected_approach",
        "rationale",
        "alternatives_considered",
        "tradeoffs",
        "evidence",
    }
    _payload_keys(payload, allowed, "select-approach payload")
    _require_group(payload, ("approach", "selected_approach"), "select-approach payload")
    if "rationale" in payload:
        _require_text(payload, "rationale", "select-approach payload")
    if "alternatives_considered" in payload:
        _string_array(
            payload["alternatives_considered"],
            "select-approach payload.alternatives_considered",
        )


def _validate_resolution_payload(payload: Mapping[str, object]) -> None:
    allowed = {
        "disposition",
        "remedy",
        "risk_decision",
        "blockers_closed",
        "conflicts_closed",
        "presented_default",
    }
    _payload_keys(payload, allowed, "resolve-review payload")
    disposition = payload.get("disposition")
    if disposition not in DISPOSITIONS:
        raise DesignValidationError("resolve-review disposition is not supported")
    if "remedy" in payload and payload["remedy"] is not None:
        _mapping(payload["remedy"], "resolve-review remedy")
    if "risk_decision" in payload and payload["risk_decision"] is not None:
        _mapping(payload["risk_decision"], "resolve-review risk_decision")
    for key in ("blockers_closed", "conflicts_closed", "presented_default"):
        if key in payload and type(payload[key]) is not bool:
            raise DesignValidationError(f"resolve-review {key} must be boolean")


def validate_event(event: Mapping[str, object], *, current_state: StateV2) -> TypedEvent:
    if not isinstance(event, Mapping):
        raise DesignValidationError("event must be an object")
    keys = set(event)
    if keys != {"event", "payload"}:
        raise DesignValidationError("event must contain exactly event and payload")
    name = event.get("event")
    if not isinstance(name, str):
        raise DesignValidationError("event name must be a string")
    payload = _mapping(event.get("payload"), f"{name} payload")
    gate = _gate_for_state(current_state.state)
    if name == "resolve-g0":
        if gate != "G0":
            raise DesignValidationError("resolve-g0 is not legal at the current gate")
        _validate_g0_payload(payload)
    elif name == "select-approach":
        if gate != "G2":
            raise DesignValidationError("select-approach is not legal at the current gate")
        _validate_approach_payload(payload)
    elif name == "record-review":
        if gate != "G3":
            raise DesignValidationError("record-review is not legal at the current gate")
        _payload_keys(payload, {"packet", "g3_approval"}, "record-review payload")
        _mapping(payload.get("packet"), "record-review packet")
        if payload.get("g3_approval") is not True:
            raise DesignValidationError("record-review needs the current-turn G3 approval")
    elif name == "resolve-review":
        if gate != "G4":
            raise DesignValidationError("resolve-review is not legal at the current gate")
        _validate_resolution_payload(payload)
    elif name == "select-handoff":
        if current_state.state != "APPROVED":
            raise DesignValidationError("select-handoff is not legal before G5 approval")
        _payload_keys(payload, {"mode"}, "select-handoff payload")
        if payload.get("mode") not in HANDOFF_MODES:
            raise DesignValidationError("select-handoff mode must be implementation-plan or direct-execution")
    elif name == "approve":
        if gate not in {"G1", "G3", "G5"}:
            raise DesignValidationError("simple approval is not legal at this gate")
        _payload_keys(payload, {"token"}, "approve payload")
        if "token" in payload and not _is_non_empty_string(payload["token"]):
            raise DesignValidationError("approve token must be non-empty")
    else:
        raise DesignValidationError(f"unknown or future event: {name}")
    return TypedEvent(name=name, payload=dict(payload))


def adapt_presented_approval(
    message: str,
    *,
    current_state: StateV2,
    presented: PresentedDecision,
) -> TypedEvent:
    token = normalize_short_approval(message)
    if token is None:
        raise DesignValidationError("message is not a legal whole-message short approval")
    expected_gate = _gate_for_state(current_state.state)
    if expected_gate is None or presented.gate not in {current_state.state, expected_gate}:
        raise DesignValidationError("presented decision is not bound to the current gate")
    if expected_gate in {"G0", "G2", "G4"}:
        if presented.default_payload is None:
            raise DesignValidationError("a typed presented default is required")
        event = {
            "event": presented.event_name,
            "payload": dict(presented.default_payload),
        }
    elif expected_gate in {"G1", "G3", "G5"}:
        event = {"event": "approve", "payload": {"token": token}}
    else:
        raise DesignValidationError("short approval is not legal in the current state")
    return validate_event(event, current_state=current_state)


def adapt_presented_answer(
    payload: Mapping[str, object],
    *,
    current_state: StateV2,
    presented: PresentedDecision,
) -> TypedEvent:
    if _gate_for_state(current_state.state) not in {presented.gate, current_state.state}:
        raise DesignValidationError("presented answer is not bound to the current gate")
    return validate_event(
        {"event": presented.event_name, "payload": dict(payload)},
        current_state=current_state,
    )


def _clear_review(state: StateV2, *, state_name: str | None = None, revision: int | None = None) -> StateV2:
    return replace(
        state,
        state=state_name or state.state,
        revision=state.revision if revision is None else revision,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        advisory_return_state=None,
        ledger=(),
    )


def _high_assurance_review_complete(state: StateV2, sources: Sequence[str] | None = None) -> bool:
    available = set(state.review_sources if sources is None else sources)
    return set(available) == REVIEW_SOURCES if state.assurance == "high" else "standard" in available


def transition_gate(state: StateV2, event: TypedEvent, *, gate: str) -> TransitionResult:
    legal = derive_route(state).legal_events
    expected_gate = _gate_for_state(state.state)
    if gate not in {state.state, expected_gate}:
        return TransitionResult(state, False, legal, "gate does not match current state")
    try:
        validated = validate_event(
            {"event": event.name, "payload": dict(event.payload)},
            current_state=state,
        )
    except DesignValidationError as error:
        return TransitionResult(state, False, legal, str(error))

    next_state = state
    if validated.name == "resolve-g0":
        next_state = replace(state, state="WAIT_G1", revision=max(1, state.revision))
    elif validated.name == "approve" and state.state == "WAIT_G1":
        next_state = replace(state, state="WAIT_G2")
    elif validated.name == "select-approach":
        next_state = replace(state, state="WAIT_G3")
    elif validated.name == "approve" and state.state == "WAIT_G3":
        if not _high_assurance_review_complete(state):
            return TransitionResult(state, False, legal, "G3 approval needs mandatory review evidence")
        next_state = replace(state, state="WAIT_G4")
    elif validated.name == "resolve-review":
        next_state = resolve_review(
            state,
            disposition=str(validated.payload["disposition"]),
            remedy=validated.payload.get("remedy") if isinstance(validated.payload.get("remedy"), Mapping) else None,
            risk_decision=(
                validated.payload.get("risk_decision")
                if isinstance(validated.payload.get("risk_decision"), Mapping)
                else None
            ),
            presented_default=bool(validated.payload.get("presented_default", False)),
        )
    elif validated.name == "approve" and state.state == "WAIT_G5":
        if (
            state.reviewed_revision != state.revision
            or not _high_assurance_review_complete(state)
            or _has_open_blocker_or_conflict(state.ledger)
        ):
            return TransitionResult(state, False, legal, "G5 requires current resolved mandatory review")
        next_state = replace(state, state="APPROVED", approved_revision=state.revision)
    elif validated.name == "select-handoff" and state.state == "APPROVED":
        mode = str(validated.payload["mode"])
        next_state = replace(
            state,
            state=PLAN_WRITING if mode == "implementation-plan" else DIRECT_EXECUTION,
        )
    else:
        return TransitionResult(state, False, legal, "event cannot advance the current gate")
    return TransitionResult(next_state, True, derive_route(next_state).legal_events)


def _design_value(payload: Mapping[str, object], *keys: str, default: object = "") -> object:
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def _render_value(value: object) -> str:
    if isinstance(value, (list, tuple)):
        if not value:
            return "- None recorded."
        return "\n".join(f"- {item}" for item in value)
    if isinstance(value, Mapping):
        return json.dumps(dict(value), sort_keys=True, separators=(",", ":"))
    if value is None or value == "":
        return "- None recorded."
    return str(value).strip()


def render_bounded_design(payload: Mapping[str, object]) -> str:
    """Render only the five pre-G3 decision sections from typed G0 data."""

    _validate_g0_payload(payload)
    text = "\n\n".join(
        (
            "# Idea Design",
            "## Intent\n" + _render_value(_design_value(payload, "intent", "goal")),
            "## Accepted Decisions\n"
            + _render_value(_design_value(payload, "accepted_decisions", "decisions")),
            "## Open Decisions\n" + _render_value(payload.get("open_decisions", [])),
            "## Selected Approach\n"
            + _render_value(_design_value(payload, "selected_approach", "approach", default="To be selected at G2.")),
            "## Essential Evidence\n"
            + _render_value(_design_value(payload, "evidence", "success_criteria", "success", "validation")),
        )
    )
    validate_design_text(text, pre_g3=True)
    return text + "\n"


def _section_names(text: str) -> tuple[str, ...]:
    return tuple(match.group(1).strip() for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))


def validate_design_text(text: str, *, pre_g3: bool) -> int:
    if not isinstance(text, str) or not text.strip():
        raise DesignValidationError("design.md must be non-empty")
    if text.lstrip().startswith("---"):
        raise DesignValidationError("design.md must not contain YAML front matter")
    if re.search(r"^\s*(schema|state|revision|design_sha256)\s*:", text, re.MULTILINE):
        raise DesignValidationError("design.md must not duplicate persisted state")
    sections = _section_names(text)
    if len(set(sections)) != len(sections):
        raise DesignValidationError("design.md contains duplicate sections")
    missing = [section for section in PRE_G3_SECTIONS if section not in sections]
    if pre_g3 and missing:
        raise DesignValidationError(f"design.md missing pre-G3 sections: {missing}")
    unexpected = sorted(set(sections) - set(PRE_G3_SECTIONS))
    if pre_g3 and unexpected:
        raise DesignValidationError(f"pre-G3 design.md has disallowed sections: {unexpected}")
    words = len(re.findall(r"\S+", text))
    if pre_g3 and words > 300:
        raise DesignValidationError("pre-G3 design.md exceeds the 300-word bound")
    return words


def _validate_bounded_design(text: str) -> int:
    """Validate advisory text without requiring the full typed G0 sections."""

    words = validate_design_text(text, pre_g3=False)
    if words > 300:
        raise DesignValidationError("pre-G3 design.md exceeds the 300-word bound")
    return words


def _ledger_markdown(findings: Sequence[ReviewFinding]) -> str:
    lines = [
        "## Review Ledger",
        "",
        "| ID | Sources | Critique | Recommendation | Reason | Blocking | Evidence | Disposition |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not findings:
        lines.append("| — | — | No findings recorded. | — | — | false | — | closed |")
    else:
        for finding in findings:
            evidence = "; ".join(finding.evidence)
            sources = ", ".join(finding.sources)
            lines.append(
                f"| {finding.id} | {sources} | {finding.critique} | "
                f"{finding.recommendation} | {finding.reason} | "
                f"{str(finding.blocking).lower()} | {evidence} | {finding.disposition} |"
            )
    return "\n".join(lines)


def design_with_ledger(design_text: str, findings: Sequence[ReviewFinding]) -> str:
    base = re.split(r"^##\s+Review Ledger\s*$", design_text, maxsplit=1, flags=re.MULTILINE)[0].rstrip()
    rendered = base + "\n\n" + _ledger_markdown(findings) + "\n"
    validate_design_text(rendered, pre_g3=False)
    return rendered


def _artifact_paths(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    return root / "design.md", root / "state.json"


def _cleanup_temp_files(root: Path) -> None:
    if not root.exists():
        return
    for path in root.iterdir():
        if path.is_file() and (
            path.name.startswith(".design.md.") or path.name.startswith(".state.json.")
        ) and path.name.endswith(".tmp"):
            try:
                path.unlink()
            except OSError:
                pass


def _atomic_replace_text(path: Path, text: str) -> None:
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            try:
                temporary.unlink()
            except OSError:
                pass


def replace_design_then_state(root: Path, design_text: str, state: StateV2) -> None:
    """Replace design first and state second; there is no cross-file transaction."""

    root = Path(root)
    design_path, state_path = _artifact_paths(root)
    pre_g3 = state.state in {"WAIT_G0", "WAIT_G1", "WAIT_G2", "WAIT_G3"}
    if state.state == "ADVISORY_REVIEW":
        _validate_bounded_design(design_text)
    else:
        validate_design_text(design_text, pre_g3=pre_g3)
    _cleanup_temp_files(root)

    design_bytes = design_text.encode("utf-8")
    design_hash = hashlib.sha256(design_bytes).hexdigest()
    _atomic_replace_text(design_path, design_text)
    persisted = replace(state, schema=SCHEMA_V2, design_sha256=design_hash, design_text=None)
    # The state validator is deliberately applied after the design replacement;
    # a failure leaves a conservative hash mismatch for the next load.
    validate_state(_state_mapping(persisted), expected_slug=persisted.slug)
    _atomic_replace_text(state_path, serialize_state(persisted))


def _persist_state_only(root: Path, state: StateV2) -> None:
    _, state_path = _artifact_paths(Path(root))
    validate_state(_state_mapping(state), expected_slug=state.slug)
    _atomic_replace_text(state_path, serialize_state(state))


def _empty_runtime_state(slug: str, *, design_hash: str = "") -> StateV2:
    return StateV2(
        schema=SCHEMA_V2,
        slug=slug,
        revision=0,
        state="WAIT_G0",
        design_sha256=design_hash,
        assurance="standard",
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
    )


def recover_hash_mismatch(snapshot: RuntimeSnapshot) -> StateV2:
    design_hash = ""
    if snapshot.design_text is not None:
        design_hash = hashlib.sha256(snapshot.design_text.encode("utf-8")).hexdigest()
    return replace(
        snapshot.state,
        schema=SCHEMA_V2,
        state="WAIT_G0",
        design_sha256=design_hash,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        advisory_return_state=None,
        ledger=(),
    )


def load_runtime(root: Path, *, slug: str = "sample") -> RuntimeSnapshot:
    root = Path(root)
    design_path, state_path = _artifact_paths(root)
    _cleanup_temp_files(root)
    if root.exists():
        stable = tuple(
            sorted(
                path.name
                for path in root.iterdir()
                if path.is_file()
                and not path.name.startswith(".")
                and path.name not in {"design.md", "state.json"}
            )
        )
        if stable:
            raise DesignValidationError(f"unexpected stable runtime artifacts: {list(stable)}")
    else:
        stable = ()

    has_design = design_path.exists()
    has_state = state_path.exists()
    if not has_design and not has_state:
        return RuntimeSnapshot(_empty_runtime_state(slug), root=root, stable_artifacts=())

    design_text: str | None = None
    if has_design:
        try:
            design_text = design_path.read_text(encoding="utf-8")
        except OSError as error:
            return RuntimeSnapshot(
                _empty_runtime_state(slug),
                root=root,
                recovery_reason=f"design read failed: {error}",
                stable_artifacts=("design.md",),
            )

    if not has_state:
        design_hash = hashlib.sha256((design_text or "").encode("utf-8")).hexdigest() if design_text is not None else ""
        return RuntimeSnapshot(
            _empty_runtime_state(slug, design_hash=design_hash),
            root=root,
            design_text=design_text,
            recovery_reason="orphaned design is uninitialized",
            stable_artifacts=("design.md",) if has_design else (),
        )
    if not has_design:
        return RuntimeSnapshot(
            _empty_runtime_state(slug),
            root=root,
            recovery_reason="state exists without design",
            stable_artifacts=("state.json",),
        )

    try:
        persisted = parse_state(state_path.read_text(encoding="utf-8"), expected_slug=slug)
        if persisted.state == "ADVISORY_REVIEW":
            _validate_bounded_design(design_text or "")
        else:
            validate_design_text(
                design_text or "",
                pre_g3=persisted.state in {"WAIT_G0", "WAIT_G1", "WAIT_G2", "WAIT_G3"},
            )
    except (OSError, DesignValidationError) as error:
        current_hash = hashlib.sha256((design_text or "").encode("utf-8")).hexdigest()
        return RuntimeSnapshot(
            replace(_empty_runtime_state(slug, design_hash=current_hash), revision=1),
            root=root,
            design_text=design_text,
            recovery_reason=f"invalid persisted evidence: {error}",
            stable_artifacts=("design.md", "state.json"),
        )

    actual_hash = hashlib.sha256((design_text or "").encode("utf-8")).hexdigest()
    if persisted.design_sha256 != actual_hash:
        recovered = recover_hash_mismatch(
            RuntimeSnapshot(persisted, root=root, design_text=design_text)
        )
        return RuntimeSnapshot(
            recovered,
            root=root,
            design_text=design_text,
            recovery_reason="design hash mismatch; later claims cleared",
            stable_artifacts=("design.md", "state.json"),
        )
    return RuntimeSnapshot(
        replace(persisted, design_text=design_text),
        root=root,
        design_text=design_text,
        stable_artifacts=("design.md", "state.json"),
    )


def initialize_after_g0(
    root: Path,
    *,
    slug: str,
    decision_payload: Mapping[str, object],
    assurance: str,
) -> RuntimeSnapshot:
    if assurance not in ASSURANCES:
        raise DesignValidationError("assurance must be standard or high")
    root = Path(root)
    design_path, state_path = _artifact_paths(root)
    existing = load_runtime(root, slug=slug)
    if existing.state.state == "ADVISORY_REVIEW":
        if existing.state.advisory_return_state != "WAIT_G0":
            raise DesignValidationError("only an advisory returning to WAIT_G0 can be initialized")
        revision = max(1, existing.state.revision + 1)
    elif design_path.exists() or state_path.exists():
        if existing.recovery_reason and existing.state.state == "WAIT_G0":
            revision = max(1, existing.state.revision)
        else:
            raise DesignValidationError("normal G0 initialization requires an uninitialized directory")
    else:
        revision = 1
    design_text = render_bounded_design(decision_payload)
    state = StateV2(
        schema=SCHEMA_V2,
        slug=slug,
        revision=revision,
        state="WAIT_G1",
        design_sha256="",
        assurance=assurance,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
    )
    replace_design_then_state(root, design_text, state)
    return load_runtime(root, slug=slug)


def start_advisory(
    state: StateV2,
    *,
    prior_gate: str,
) -> StateV2:
    if prior_gate not in {"WAIT_G0", "WAIT_G1", "WAIT_G2", "WAIT_G3"}:
        raise DesignValidationError("advisory may return only to an early gate")
    return replace(
        state,
        state="ADVISORY_REVIEW",
        advisory_return_state=prior_gate,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        ledger=(),
    )


def finish_advisory(state: StateV2) -> StateV2:
    if state.state != "ADVISORY_REVIEW" or state.advisory_return_state is None:
        raise DesignValidationError("state is not an active advisory review")
    return replace(
        state,
        state=state.advisory_return_state,
        advisory_return_state=None,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        ledger=(),
    )


def start_advisory_before_g0(
    root: Path,
    *,
    slug: str,
    bounded_design: str,
    assurance: str,
) -> RuntimeSnapshot:
    if assurance not in ASSURANCES:
        raise DesignValidationError("assurance must be standard or high")
    root = Path(root)
    existing = load_runtime(root, slug=slug)
    if existing.stable_artifacts:
        raise DesignValidationError("advisory-before-G0 requires no stable runtime artifacts")
    _validate_bounded_design(bounded_design)
    state = StateV2(
        schema=SCHEMA_V2,
        slug=slug,
        revision=1,
        state="ADVISORY_REVIEW",
        design_sha256="",
        assurance=assurance,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        advisory_return_state="WAIT_G0",
    )
    replace_design_then_state(root, bounded_design, state)
    return load_runtime(root, slug=slug)


def _valid_repository_path(value: object) -> bool:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and ".." not in parts


def _packet_string_array(value: object, name: str, diagnostics: list[str]) -> tuple[str, ...]:
    if not isinstance(value, list):
        diagnostics.append(f"{name} must be an array")
        return ()
    if any(not _is_non_empty_string(item) for item in value):
        diagnostics.append(f"{name} must contain non-empty strings")
    values = tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
    if len(set(values)) != len(values):
        diagnostics.append(f"{name} must not contain duplicates")
    return values


def _packet_to_finding(item: object, source: str, index: int, diagnostics: list[str]) -> ReviewFinding | None:
    prefix = f"findings[{index}]"
    if not isinstance(item, Mapping):
        diagnostics.append(f"{prefix} must be an object")
        return None
    keys = set(item)
    missing = PACKET_FINDING_KEYS - keys
    unknown = keys - PACKET_FINDING_KEYS
    if missing:
        diagnostics.append(f"{prefix} missing keys: {sorted(missing)}")
    if unknown:
        diagnostics.append(f"{prefix} has unknown keys: {sorted(unknown)}")
    finding_id = item.get("id")
    if not isinstance(finding_id, str) or not PACKET_FINDING_ID.fullmatch(finding_id):
        diagnostics.append(f"{prefix}.id must match C-000 format")
    text_values: dict[str, str] = {}
    for key in ("critique", "recommendation", "reason"):
        value = item.get(key)
        if not _is_non_empty_string(value):
            diagnostics.append(f"{prefix}.{key} must be a non-empty string")
        else:
            assert isinstance(value, str)
            text_values[key] = value.strip()
    blocking = item.get("blocking")
    if type(blocking) is not bool:
        diagnostics.append(f"{prefix}.blocking must be boolean")
    evidence = _packet_string_array(item.get("evidence"), f"{prefix}.evidence", diagnostics)
    if (
        isinstance(finding_id, str)
        and PACKET_FINDING_ID.fullmatch(finding_id)
        and len(text_values) == 3
        and type(blocking) is bool
        and evidence
    ):
        key = "|".join(
            (text_values["critique"].casefold(), text_values["reason"].casefold())
        )
        return ReviewFinding(
            id="",
            source=source,
            sources=(source,),
            critique=text_values["critique"],
            recommendation=text_values["recommendation"],
            reason=text_values["reason"],
            blocking=blocking,
            evidence=evidence,
            equivalence_key=key,
        )
    return None


def _validate_packet(
    packet: Mapping[str, object],
    *,
    expected_target_path: str,
    expected_revision: int,
) -> PacketResult:
    diagnostics: list[str] = []
    keys = set(packet)
    missing = PACKET_KEYS - keys
    unknown = keys - PACKET_KEYS
    if missing:
        diagnostics.append(f"packet missing keys: {sorted(missing)}")
    if unknown:
        diagnostics.append(f"packet has unknown keys: {sorted(unknown)}")
    if packet.get("schema") != PACKET_SCHEMA:
        diagnostics.append(f"schema must be {PACKET_SCHEMA}")
    source = packet.get("source")
    if source not in REVIEW_SOURCES:
        diagnostics.append("source must be standard or independent")
        source = "standard"
    target_path = packet.get("target_path")
    if not _valid_repository_path(target_path):
        diagnostics.append("target_path must be a repository-relative POSIX path")
        target_path = expected_target_path
    elif target_path != expected_target_path:
        diagnostics.append("target_path does not match the expected target")
    target_revision = packet.get("target_revision")
    if not _is_positive_integer(target_revision):
        diagnostics.append("target_revision must be a positive integer")
        target_revision = expected_revision
    elif target_revision != expected_revision:
        diagnostics.append("target_revision does not match the expected revision")
    outcome = packet.get("outcome")
    if outcome not in PACKET_OUTCOMES:
        diagnostics.append("outcome is not supported")
        outcome = "invalid-target"
    findings: list[ReviewFinding] = []
    raw_findings = packet.get("findings")
    if not isinstance(raw_findings, list):
        diagnostics.append("findings must be an array")
    else:
        packet_ids: set[str] = set()
        for index, item in enumerate(raw_findings):
            if isinstance(item, Mapping) and item.get("id") in packet_ids:
                diagnostics.append(f"duplicate finding id: {item.get('id')}")
            if isinstance(item, Mapping) and isinstance(item.get("id"), str):
                packet_ids.add(item["id"])
            finding = _packet_to_finding(item, str(source), index, diagnostics)
            if finding is not None:
                findings.append(finding)
    residual_risks = _packet_string_array(packet.get("residual_risks"), "residual_risks", diagnostics)
    packet_diagnostics = _packet_string_array(packet.get("diagnostics"), "diagnostics", diagnostics)
    blockers = tuple(finding for finding in findings if finding.blocking)
    if outcome == "accepted":
        if blockers:
            diagnostics.append("accepted cannot contain a blocking finding")
        if packet_diagnostics:
            diagnostics.append("accepted must have empty diagnostics")
    elif outcome == "revise-design" and not findings:
        diagnostics.append("revise-design requires at least one finding")
    elif outcome == "reopen-analysis" and not blockers:
        diagnostics.append("reopen-analysis requires a blocking finding")
    elif outcome == "needs-clarification":
        clarification = " ".join(f"{f.critique} {f.reason}" for f in blockers).casefold()
        if not blockers or not any(marker in clarification for marker in ("user decision", "unresolved", "clarif")):
            diagnostics.append("needs-clarification requires an unresolved user-decision blocker")
    elif outcome == "invalid-target":
        diagnostics.append("invalid-target packets cannot be consumed")
    elif outcome == "request-separate-review":
        if source != "independent":
            diagnostics.append("request-separate-review requires independent source")
        if not packet_diagnostics:
            diagnostics.append("request-separate-review requires diagnostics")
    if diagnostics:
        raise DesignValidationError("invalid full-analysis packet: " + "; ".join(dict.fromkeys(diagnostics)))
    return PacketResult(
        source=str(source),
        target_path=str(target_path),
        target_revision=int(target_revision),
        outcome=str(outcome),
        findings=tuple(findings),
        residual_risks=residual_risks,
        diagnostics=packet_diagnostics,
    )


def _next_ledger_id(findings: Sequence[ReviewFinding]) -> str:
    numbers = [int(item.id[2:]) for item in findings if LEDGER_FINDING_ID.fullmatch(item.id)]
    return f"F-{(max(numbers) if numbers else 0) + 1:03d}"


def _consolidate_ledger(
    existing: Sequence[ReviewFinding], incoming: Sequence[ReviewFinding]
) -> tuple[ReviewFinding, ...]:
    result = list(existing)
    for item in incoming:
        same_key = [
            index
            for index, current in enumerate(result)
            if current.equivalence_key == item.equivalence_key
        ]
        same_recommendation = next(
            (index for index in same_key if result[index].recommendation.casefold() == item.recommendation.casefold()),
            None,
        )
        if same_recommendation is not None:
            current = result[same_recommendation]
            result[same_recommendation] = replace(
                current,
                sources=tuple(dict.fromkeys((*current.sources, *item.sources))),
                evidence=tuple(dict.fromkeys((*current.evidence, *item.evidence))),
                blocking=current.blocking or item.blocking,
                disposition="open" if current.disposition == "open" or item.disposition == "open" else current.disposition,
            )
            continue
        conflict = bool(same_key)
        result.append(
            replace(
                item,
                id=_next_ledger_id(result),
                conflict=conflict,
            )
        )
        if conflict:
            for index in same_key:
                result[index] = replace(result[index], conflict=True)
    return tuple(result)


def _consume_packet(
    state: StateV2,
    packet: Mapping[str, object],
    *,
    expected_target_path: str,
    expected_revision: int,
    mandatory: bool,
    allow_wait_g3: bool,
) -> ReviewResult:
    if mandatory and state.state == "WAIT_G3" and not allow_wait_g3:
        raise DesignValidationError("standalone mandatory packet cannot advance WAIT_G3")
    if mandatory and state.state not in {"WAIT_G3", "WAIT_G4"}:
        raise DesignValidationError("mandatory review packet is not legal at the current state")
    if not mandatory and state.state not in {"WAIT_G0", "ADVISORY_REVIEW"}:
        raise DesignValidationError("advisory review packet is only legal before mandatory review")
    parsed = _validate_packet(
        _mapping(packet, "packet"),
        expected_target_path=expected_target_path,
        expected_revision=expected_revision,
    )
    if mandatory and parsed.source in state.review_sources:
        raise DesignValidationError("duplicate mandatory review source")
    ledger = _consolidate_ledger(state.ledger, parsed.findings)
    if not mandatory:
        next_state = replace(state, ledger=ledger)
        return ReviewResult(next_state, parsed.source, parsed.outcome, ledger, parsed.residual_risks)

    sources = tuple(
        source for source in ("standard", "independent") if source in (*state.review_sources, parsed.source)
    )
    review_complete = "standard" in sources and (state.assurance != "high" or "independent" in sources)
    next_state = replace(
        state,
        state="WAIT_G4" if review_complete else "WAIT_G3",
        review_sources=sources,
        reviewed_revision=state.revision if review_complete else None,
        approved_revision=None,
        ledger=ledger,
    )
    return ReviewResult(next_state, parsed.source, parsed.outcome, ledger, parsed.residual_risks)


def consume_full_analysis_packet(
    state: StateV2,
    packet: Mapping[str, object],
    *,
    expected_target_path: str,
    expected_revision: int,
    mandatory: bool,
) -> ReviewResult:
    return _consume_packet(
        state,
        packet,
        expected_target_path=expected_target_path,
        expected_revision=expected_revision,
        mandatory=mandatory,
        allow_wait_g3=False,
    )


def record_review(
    state: StateV2,
    packet: Mapping[str, object],
    *,
    g3_approval_event: TypedEvent,
    expected_target_path: str,
    expected_revision: int,
) -> StateV2:
    if state.state != "WAIT_G3":
        raise DesignValidationError("record-review requires persisted WAIT_G3")
    if not isinstance(g3_approval_event, TypedEvent) or g3_approval_event.name != "approve":
        raise DesignValidationError("record-review requires the transient G3 approve event")
    result = _consume_packet(
        state,
        packet,
        expected_target_path=expected_target_path,
        expected_revision=expected_revision,
        mandatory=True,
        allow_wait_g3=True,
    )
    return result.state


def _load_critical_report_adapter() -> Any:
    module_name = "critical_report_adapter"
    module = sys.modules.get(module_name)
    if module is None:
        adapter_path = Path(__file__).with_name("critical_report_adapter.py")
        spec = importlib.util.spec_from_file_location(module_name, adapter_path)
        if spec is None or spec.loader is None:
            raise DesignValidationError("critical report adapter cannot be loaded")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    adapter = getattr(module, "adapt_critical_report", None)
    if not callable(adapter):
        raise DesignValidationError("critical report adapter has no adaptation function")
    return adapter


def record_readable_review(
    state: StateV2,
    report: str,
    *,
    source: str,
    g3_approval_event: TypedEvent,
    expected_target_path: str,
    expected_revision: int,
) -> StateV2:
    """Adapt one readable critic report and record it at the current G3 boundary."""

    adapt_critical_report = _load_critical_report_adapter()
    packet = adapt_critical_report(
        report,
        source=source,
        target_path=expected_target_path,
        target_revision=expected_revision,
    )
    return record_review(
        state,
        packet,
        g3_approval_event=g3_approval_event,
        expected_target_path=expected_target_path,
        expected_revision=expected_revision,
    )


def _has_open_blocker_or_conflict(findings: Sequence[ReviewFinding]) -> bool:
    return any(
        item.disposition != "closed" and (item.blocking or item.conflict) for item in findings
    )


def resolve_review(
    state: StateV2,
    *,
    disposition: str,
    remedy: Mapping[str, object] | None,
    risk_decision: Mapping[str, object] | None,
    presented_default: bool = False,
) -> StateV2:
    payload: dict[str, object] = {"disposition": disposition, "presented_default": presented_default}
    if remedy is not None:
        payload["remedy"] = remedy
    if risk_decision is not None:
        payload["risk_decision"] = risk_decision
    _validate_resolution_payload(payload)
    if state.state != "WAIT_G4":
        raise DesignValidationError("resolve-review requires WAIT_G4")
    if disposition in {"closed", "accepted-remedy", "accepted-risk"}:
        ledger = tuple(
            replace(item, disposition="closed")
            if item.disposition != "closed"
            else item
            for item in state.ledger
        )
        if _has_open_blocker_or_conflict(ledger):
            raise DesignValidationError("review blockers or conflicts remain open")
        return replace(state, state="WAIT_G5", ledger=ledger, approved_revision=None)
    return replace(
        state,
        state="WAIT_G3",
        revision=state.revision + 1,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        ledger=state.ledger,
    )


def can_enter_g5(state: StateV2, design_hash: str) -> bool:
    return (
        state.state == "WAIT_G4"
        and state.design_sha256 == design_hash
        and state.reviewed_revision == state.revision
        and _high_assurance_review_complete(state)
        and state.advisory_return_state is None
        and not _has_open_blocker_or_conflict(state.ledger)
    )


def render_public_critique(findings: Sequence[ReviewFinding]) -> str:
    if not findings:
        return "No consolidated findings."
    lines: list[str] = []
    for index, finding in enumerate(findings, start=1):
        lines.append(f"{index}. {finding.critique} — {finding.recommendation}")
    return "\n".join(lines)


# Narrow compatibility projection for repository state probes. It uses the v2
# schema but is not the runtime serializer: canonical state.json never contains
# completed_gates or plan_handoff.


@dataclass(frozen=True)
class WorkflowState:
    schema: str
    slug: str
    revision: int
    state: str
    design_sha256: str
    assurance: str
    review_sources: tuple[str, ...]
    reviewed_revision: int | None
    approved_revision: int | None
    advisory_return_state: str | None
    completed_gates: tuple[str, ...]
    plan_handoff: str | None


WORKFLOW_KEYS = frozenset(
    {
        "schema",
        "slug",
        "revision",
        "state",
        "design_sha256",
        "assurance",
        "review_sources",
        "reviewed_revision",
        "approved_revision",
        "advisory_return_state",
        "completed_gates",
        "plan_handoff",
    }
)


def new_workflow_state(
    slug: str,
    design_sha256: str,
    assurance: str,
    g0_complete: bool = False,
) -> WorkflowState:
    return WorkflowState(
        schema=SCHEMA_V2,
        slug=slug,
        revision=1,
        state="WAIT_G1" if g0_complete else "WAIT_G0",
        design_sha256=design_sha256,
        assurance=assurance,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        advisory_return_state=None,
        completed_gates=("G0",) if g0_complete else (),
        plan_handoff=None,
    )


def _workflow_mapping(state: WorkflowState) -> dict[str, object]:
    return {
        "schema": state.schema,
        "slug": state.slug,
        "revision": state.revision,
        "state": state.state,
        "design_sha256": state.design_sha256,
        "assurance": state.assurance,
        "review_sources": list(state.review_sources),
        "reviewed_revision": state.reviewed_revision,
        "approved_revision": state.approved_revision,
        "advisory_return_state": state.advisory_return_state,
        "completed_gates": list(state.completed_gates),
        "plan_handoff": state.plan_handoff,
    }


def serialize_workflow_state(state: WorkflowState) -> str:
    return json.dumps(_workflow_mapping(state), sort_keys=True, separators=(",", ":")) + "\n"


def parse_workflow_state(payload: str | Mapping[str, object]) -> WorkflowState:
    decoded = _strict_json_loads(payload) if isinstance(payload, str) else payload
    value = _mapping(decoded, "workflow state")
    keys = set(value)
    if keys != WORKFLOW_KEYS:
        raise StateValidationError(
            f"workflow state keys mismatch; missing={sorted(WORKFLOW_KEYS - keys)} unknown={sorted(keys - WORKFLOW_KEYS)}"
        )
    if value.get("schema") != SCHEMA_V2:
        raise StateValidationError("workflow state is not v2")
    if not isinstance(value.get("slug"), str) or not SLUG.fullmatch(value["slug"]):
        raise StateValidationError("workflow slug is invalid")
    if not _is_positive_integer(value.get("revision")):
        raise StateValidationError("workflow revision is invalid")
    if value.get("state") not in STATES | {PLAN_WRITING}:
        raise StateValidationError("workflow state is invalid")
    if not isinstance(value.get("design_sha256"), str) or not SHA256.fullmatch(value["design_sha256"]):
        raise StateValidationError("workflow design hash is invalid")
    if value.get("assurance") not in ASSURANCES:
        raise StateValidationError("workflow assurance is invalid")
    sources = _string_array(value.get("review_sources"), "workflow review_sources")
    if any(source not in REVIEW_SOURCES for source in sources):
        raise StateValidationError("workflow review source is invalid")
    completed = _string_array(value.get("completed_gates"), "completed_gates")
    if any(gate not in GATES for gate in completed):
        raise StateValidationError("completed_gates contains an invalid gate")
    for key in ("reviewed_revision", "approved_revision"):
        if value[key] is not None and not _is_positive_integer(value[key]):
            raise StateValidationError(f"workflow {key} is invalid")
    plan_handoff = value.get("plan_handoff")
    if plan_handoff is not None and not isinstance(plan_handoff, str):
        raise StateValidationError("plan_handoff must be a string or null")
    advisory = value.get("advisory_return_state")
    if advisory is not None and not isinstance(advisory, str):
        raise StateValidationError("advisory_return_state must be a string or null")
    return WorkflowState(
        schema=SCHEMA_V2,
        slug=value["slug"],
        revision=value["revision"],
        state=value["state"],
        design_sha256=value["design_sha256"],
        assurance=value["assurance"],
        review_sources=sources,
        reviewed_revision=value["reviewed_revision"],
        approved_revision=value["approved_revision"],
        advisory_return_state=advisory,
        completed_gates=completed,
        plan_handoff=plan_handoff,
    )


def advance_waiting_gate(
    state: WorkflowState,
    message: str,
    *,
    design_sha256: str,
    review_sources: Sequence[str] | None = None,
) -> WorkflowState:
    if state.design_sha256 != design_sha256:
        raise DesignValidationError("design hash mismatch; approval cannot advance")
    token = normalize_short_approval(message)
    if token is None:
        raise DesignValidationError("only a whole-message short approval can advance")
    sources = tuple(state.review_sources if review_sources is None else review_sources)
    if any(source not in REVIEW_SOURCES for source in sources) or len(set(sources)) != len(sources):
        raise DesignValidationError("review sources are invalid")
    if state.state == "WAIT_G1":
        return replace(state, state="WAIT_G2", completed_gates=(*state.completed_gates, "G1"))
    if state.state == "WAIT_G2":
        return replace(state, state="WAIT_G3", completed_gates=(*state.completed_gates, "G2"))
    if state.state == "WAIT_G3":
        if not _high_assurance_review_complete(
            StateV2(
                SCHEMA_V2,
                state.slug,
                state.revision,
                "WAIT_G3",
                state.design_sha256,
                state.assurance,
                sources,
                state.reviewed_revision,
                state.approved_revision,
            )
        ):
            raise DesignValidationError("G3 cannot advance without mandatory current review")
        return replace(
            state,
            state="WAIT_G4",
            review_sources=sources,
            reviewed_revision=state.revision,
            completed_gates=(*state.completed_gates, "G3"),
        )
    if state.state == "WAIT_G4":
        if state.reviewed_revision != state.revision or not _high_assurance_review_complete(
            StateV2(
                SCHEMA_V2,
                state.slug,
                state.revision,
                "WAIT_G4",
                state.design_sha256,
                state.assurance,
                sources,
                state.reviewed_revision,
                state.approved_revision,
            )
        ):
            raise DesignValidationError("G4 cannot advance without current review")
        return replace(state, state="WAIT_G5", review_sources=sources, completed_gates=(*state.completed_gates, "G4"))
    if state.state == "WAIT_G5":
        if state.reviewed_revision != state.revision or "standard" not in sources:
            raise DesignValidationError("G5 requires current mandatory review")
        if state.assurance == "high" and "independent" not in sources:
            raise DesignValidationError("high assurance requires independent review")
        return replace(
            state,
            state="APPROVED",
            review_sources=sources,
            approved_revision=state.revision,
            completed_gates=(*state.completed_gates, "G5"),
            plan_handoff=None,
        )
    if state.state == "APPROVED":
        raise DesignValidationError("select-handoff is required before choosing a terminal owner")
    raise DesignValidationError("short approval is not legal at the current workflow gate")


def advance_handoff(state: WorkflowState, *, mode: str) -> WorkflowState:
    if state.state != "APPROVED":
        raise DesignValidationError("select-handoff requires an approved workflow")
    if mode not in HANDOFF_MODES:
        raise DesignValidationError("select-handoff mode must be implementation-plan or direct-execution")
    return replace(
        state,
        state=PLAN_WRITING if mode == "implementation-plan" else DIRECT_EXECUTION,
        plan_handoff="requested" if mode == "implementation-plan" else "direct-execution",
    )


def start_advisory_review(state: WorkflowState) -> WorkflowState:
    if state.state in {PLAN_WRITING, DIRECT_EXECUTION, "APPROVED"}:
        raise DesignValidationError("advisory review cannot reopen a completed handoff")
    return replace(
        state,
        state="ADVISORY_REVIEW",
        advisory_return_state=state.state,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        plan_handoff=None,
    )


def finish_advisory_review(state: WorkflowState, *, design_sha256: str) -> WorkflowState:
    if state.state != "ADVISORY_REVIEW" or state.advisory_return_state is None:
        raise DesignValidationError("workflow is not in advisory review")
    if state.design_sha256 != design_sha256:
        raise DesignValidationError("design hash mismatch; advisory cannot return")
    return replace(
        state,
        state=state.advisory_return_state,
        advisory_return_state=None,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        plan_handoff=None,
    )


def _compact_for_workflow(state: WorkflowState) -> str:
    actor_events = {
        "WAIT_G0": ("user", "resolve-g0"),
        "WAIT_G1": ("user", "approve"),
        "WAIT_G2": ("user", "select-approach"),
        "WAIT_G3": ("user", "approve"),
        "WAIT_G4": ("user", "resolve-review"),
        "WAIT_G5": ("user", "approve"),
        "APPROVED": ("user", "select-handoff"),
        "ADVISORY_REVIEW": ("critic", "finish-advisory"),
        PLAN_WRITING: ("plan-writer", "stop"),
        DIRECT_EXECUTION: ("task-executor", "stop"),
    }
    actor, event = actor_events[state.state]
    return f"{state.state}|R{state.revision}|{actor}|{event}"


def _compact_for_snapshot(snapshot: RuntimeSnapshot) -> str:
    route = derive_route(snapshot.state)
    events = ",".join(route.legal_events) or "none"
    action = " ".join(route.next_action.split())
    return f"state={snapshot.state.state}|revision={snapshot.state.revision}|actor={route.next_actor}|events={events}|action={action}"


def _json_projection(snapshot: RuntimeSnapshot) -> dict[str, object]:
    route = derive_route(snapshot.state)
    result = _state_mapping(snapshot.state)
    result.update(
        {
            "next_actor": route.next_actor,
            "next_owner": route.next_owner,
            "legal_events": list(route.legal_events),
            "next_action": route.next_action,
            "authorizes_execution": route.authorizes_execution,
        }
    )
    return result


def _cli_payload(raw: str | None, *, name: str) -> object:
    if raw is None:
        raise DesignValidationError(f"{name} needs --payload-json")
    return _strict_json_loads(raw)


def _cli_root(value: str) -> Path:
    return Path(value).expanduser()


def _cli_inspect(root: Path, slug: str, compact: bool) -> int:
    snapshot = load_runtime(root, slug=slug)
    if compact:
        print(_compact_for_snapshot(snapshot))
    else:
        print(json.dumps(_json_projection(snapshot), sort_keys=True, separators=(",", ":")))
    return 0


def _cli_init(args: argparse.Namespace) -> int:
    payload = _mapping(_cli_payload(args.payload_json, name="init"), "init payload")
    initialize_after_g0(
        _cli_root(args.root),
        slug=args.slug,
        decision_payload=payload,
        assurance=args.assurance,
    )
    return _cli_inspect(_cli_root(args.root), args.slug, args.compact)


def _cli_advisory_start(args: argparse.Namespace) -> int:
    payload = _cli_payload(args.payload_json, name="advisory start")
    if isinstance(payload, str):
        design = payload
    else:
        value = _mapping(payload, "advisory payload")
        design_value = value.get("design", value.get("bounded_design"))
        if not isinstance(design_value, str):
            raise DesignValidationError("advisory payload needs a bounded design string")
        design = design_value
    start_advisory_before_g0(
        _cli_root(args.root),
        slug=args.slug,
        bounded_design=design,
        assurance=args.assurance,
    )
    return _cli_inspect(_cli_root(args.root), args.slug, args.compact)


def _cli_advance(args: argparse.Namespace) -> int:
    root = _cli_root(args.root)
    snapshot = load_runtime(root, slug=args.slug)
    if not (root / "state.json").exists():
        raise DesignValidationError("advance is not legal before init; use init --event resolve-g0")
    if args.message is not None:
        token = normalize_short_approval(args.message)
        if token is None or snapshot.state.state not in {"WAIT_G1", "WAIT_G3", "WAIT_G5"}:
            raise DesignValidationError("this short approval is not legal without a presented typed default")
        event = TypedEvent("approve", {"token": token})
        result = transition_gate(snapshot.state, event, gate=snapshot.state.state)
        if not result.accepted:
            raise DesignValidationError(result.reason or "approval did not advance")
        _persist_state_only(root, result.state)
    else:
        payload = _mapping(_cli_payload(args.payload_json, name="advance"), "advance payload")
        name = args.event
        if name == "record-review":
            packet = _mapping(payload.get("packet"), "record-review packet")
            approval = TypedEvent("approve", {})
            next_state = record_review(
                snapshot.state,
                packet,
                g3_approval_event=approval,
                expected_target_path=f"tmp/idea/{args.slug}/design.md",
                expected_revision=snapshot.state.revision,
            )
        elif name == "record-readable-review":
            report = payload.get("report")
            if not isinstance(report, str):
                raise DesignValidationError("record-readable-review needs a report string")
            source = payload.get("source", "standard")
            if not isinstance(source, str):
                raise DesignValidationError("record-readable-review source must be a string")
            next_state = record_readable_review(
                snapshot.state,
                report,
                source=source,
                g3_approval_event=TypedEvent("approve", {}),
                expected_target_path=f"tmp/idea/{args.slug}/design.md",
                expected_revision=snapshot.state.revision,
            )
        else:
            event = validate_event({"event": name, "payload": payload}, current_state=snapshot.state)
            result = transition_gate(snapshot.state, event, gate=snapshot.state.state)
            if not result.accepted:
                raise DesignValidationError(result.reason or "event did not advance")
            next_state = result.state
        if name in {"record-review", "record-readable-review"}:
            if next_state.ledger != snapshot.state.ledger and snapshot.design_text is not None:
                replace_design_then_state(root, design_with_ledger(snapshot.design_text, next_state.ledger), next_state)
            else:
                _persist_state_only(root, next_state)
        else:
            _persist_state_only(root, next_state)
    return _cli_inspect(root, args.slug, args.compact)


def _cli_recover(args: argparse.Namespace) -> int:
    root = _cli_root(args.root)
    snapshot = load_runtime(root, slug=args.slug)
    recovered = recover_hash_mismatch(snapshot)
    if (root / "design.md").exists():
        _persist_state_only(root, recovered)
    if args.compact:
        print(_compact_for_snapshot(replace(snapshot, state=recovered)))
    else:
        print(json.dumps(_json_projection(replace(snapshot, state=recovered)), sort_keys=True, separators=(",", ":")))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage internal-gateway-idea-state/v2.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_runtime_options(command: argparse.ArgumentParser) -> None:
        command.add_argument("--root", required=True)
        command.add_argument("--slug", required=True)
        command.add_argument("--compact", action="store_true")

    inspect = subparsers.add_parser("inspect")
    add_runtime_options(inspect)
    inspect.set_defaults(handler=lambda args: _cli_inspect(_cli_root(args.root), args.slug, args.compact))

    init = subparsers.add_parser("init")
    add_runtime_options(init)
    init.add_argument("--event", required=True, choices=("resolve-g0",))
    init.add_argument("--payload-json", required=True)
    init.add_argument("--assurance", choices=tuple(sorted(ASSURANCES)), default="standard")
    init.set_defaults(handler=_cli_init)

    advance = subparsers.add_parser("advance")
    add_runtime_options(advance)
    advance.add_argument(
        "--event",
        choices=(
            "select-approach",
            "select-handoff",
            "record-review",
            "record-readable-review",
            "resolve-review",
            "approve",
        ),
    )
    advance.add_argument("--payload-json")
    advance.add_argument("--message")
    advance.set_defaults(handler=_cli_advance)

    recover = subparsers.add_parser("recover")
    add_runtime_options(recover)
    recover.set_defaults(handler=_cli_recover)

    advisory = subparsers.add_parser("advisory")
    advisory_sub = advisory.add_subparsers(dest="advisory_command", required=True)
    start = advisory_sub.add_parser("start")
    add_runtime_options(start)
    start.add_argument("--payload-json", required=True)
    start.add_argument("--assurance", choices=tuple(sorted(ASSURANCES)), default="standard")
    start.set_defaults(handler=_cli_advisory_start)

    show = subparsers.add_parser("show")
    show.add_argument("state_path")
    show.add_argument("--compact", action="store_true")
    show.set_defaults(handler=_cli_show)
    return parser


def _cli_show(args: argparse.Namespace) -> int:
    path = Path(args.state_path)
    payload = path.read_text(encoding="utf-8")
    try:
        compatibility = parse_workflow_state(payload)
    except DesignValidationError:
        raw = _strict_json_loads(payload)
        value = _mapping(raw, "state")
        slug = value.get("slug")
        if not isinstance(slug, str):
            raise DesignValidationError("state.json needs a slug")
        state = validate_state(value, expected_slug=slug)
        snapshot = RuntimeSnapshot(state, root=path.parent)
        print(_compact_for_snapshot(snapshot) if args.compact else json.dumps(_json_projection(snapshot), sort_keys=True, separators=(",", ":")))
        return 0
    print(_compact_for_workflow(compatibility) if args.compact else serialize_workflow_state(compatibility).rstrip("\n"))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "advance" and args.event == "approve" and args.message is None:
            raise DesignValidationError("advance --event approve needs --message")
        if args.command == "advance" and args.event != "approve" and args.payload_json is None:
            raise DesignValidationError("typed advance events need --payload-json")
        return int(args.handler(args))
    except (DesignValidationError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
