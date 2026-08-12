#!/usr/bin/env python3
"""Fail-closed state and persistence owner for the idea gateway v3 contract.

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


SCHEMA_V3 = "internal-gateway-idea-state/v3"
SCHEMA = SCHEMA_V3
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
ASSURANCES = frozenset({"lightweight", "standard", "intensive"})
ASSURANCE_RANK = {"lightweight": 1, "standard": 2, "intensive": 3}
REVIEW_SOURCES = frozenset({"standard", "independent"})
DISCOVERY_MODES = frozenset({"pre-draft", "targeted-refinement", "direct-draft"})
DISCOVERY_LEVELS = frozenset({"low", "medium", "high"})
MATERIAL_REOPEN_TRIGGERS = frozenset(
    {
        "incompatible-evidence",
        "scope-change",
        "constraint-change",
        "validation-failure",
        "dependency-change",
    }
)
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
        "events",
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


RESOLUTION_KEYS = frozenset(
    {
        "finding_id",
        "modification_fingerprint",
        "validation_reference",
        "risk_acceptance",
        "note",
    }
)


def _resolution_mapping(value: FindingResolutionEvidence) -> dict[str, object]:
    result: dict[str, object] = {"finding_id": value.finding_id}
    for key in (
        "modification_fingerprint",
        "validation_reference",
        "risk_acceptance",
        "note",
    ):
        resolved = getattr(value, key)
        if resolved is not None:
            result[key] = resolved
    return result


def _resolution_entries(value: object) -> tuple[FindingResolutionEvidence, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise DesignValidationError("finding_resolutions must be an array")
    entries: list[FindingResolutionEvidence] = []
    for index, raw in enumerate(value):
        if isinstance(raw, FindingResolutionEvidence):
            entry = raw
        else:
            mapping = _mapping(raw, f"finding_resolutions[{index}]")
            unknown = set(mapping) - RESOLUTION_KEYS
            if unknown:
                raise DesignValidationError(
                    f"finding_resolutions[{index}] has unknown keys: {sorted(unknown)}"
                )
            entry = FindingResolutionEvidence(
                finding_id=mapping.get("finding_id", ""),
                modification_fingerprint=mapping.get("modification_fingerprint"),
                validation_reference=mapping.get("validation_reference"),
                risk_acceptance=mapping.get("risk_acceptance"),
                note=mapping.get("note"),
            )
        if not isinstance(entry.finding_id, str) or not LEDGER_FINDING_ID.fullmatch(entry.finding_id):
            raise DesignValidationError(
                f"finding_resolutions[{index}].finding_id must be a ledger finding id"
            )
        for key in (
            "modification_fingerprint",
            "validation_reference",
            "risk_acceptance",
            "note",
        ):
            value_for_key = getattr(entry, key)
            if value_for_key is not None and not _is_non_empty_string(value_for_key):
                raise DesignValidationError(
                    f"finding_resolutions[{index}].{key} must be non-empty when present"
                )
        if not any(
            getattr(entry, key) is not None
            for key in ("modification_fingerprint", "validation_reference", "risk_acceptance")
        ):
            raise DesignValidationError(
                f"finding_resolutions[{index}] needs proof or explicit risk acceptance"
            )
        if any(existing.finding_id == entry.finding_id for existing in entries):
            raise DesignValidationError(
                f"duplicate finding resolution: {entry.finding_id}"
            )
        entries.append(entry)
    return tuple(entries)


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
class FindingResolutionEvidence:
    """Typed proof or explicit risk acceptance for one finding closure."""

    finding_id: str
    modification_fingerprint: str | None = None
    validation_reference: str | None = None
    risk_acceptance: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class EventLedgerEntry:
    """One compact, typed decision event retained in canonical state."""

    sequence: int
    event: str
    revision: int
    payload: Mapping[str, object]


@dataclass(frozen=True)
class StateV3:
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
    events: tuple[EventLedgerEntry, ...] = field(default_factory=tuple)
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
class DiscoveryDecision:
    mode: str
    impact: str
    confidence: str
    default_safety: bool
    rationale: str
    next_artifact: str


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
    state: StateV3
    accepted: bool
    legal_events: tuple[str, ...]
    reason: str | None = None

    @property
    def next_state(self) -> StateV3:
        return self.state


@dataclass(frozen=True)
class RuntimeSnapshot:
    state: StateV3
    root: Path | None = None
    design_text: str | None = None
    recovery_reason: str | None = None
    stable_artifacts: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkflowCounts:
    discovery_turns: int
    approvals: int
    reopenings: int
    critic_runs: int
    recovery_events: int


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
    state: StateV3
    source: str | None
    outcome: str | None
    findings: tuple[ReviewFinding, ...]
    residual_risks: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()


FINDING_KEYS = frozenset(
    {
        "id",
        "source",
        "sources",
        "critique",
        "recommendation",
        "reason",
        "blocking",
        "evidence",
        "disposition",
        "conflict",
        "equivalence_key",
    }
)


def _review_finding_mapping(finding: ReviewFinding) -> dict[str, object]:
    return {
        "id": finding.id,
        "source": finding.source,
        "sources": list(finding.sources),
        "critique": finding.critique,
        "recommendation": finding.recommendation,
        "reason": finding.reason,
        "blocking": finding.blocking,
        "evidence": list(finding.evidence),
        "disposition": finding.disposition,
        "conflict": finding.conflict,
        "equivalence_key": finding.equivalence_key,
    }


def _review_finding_from_mapping(value: object, index: int) -> ReviewFinding:
    mapping = _mapping(value, f"event findings[{index}]")
    if set(mapping) != FINDING_KEYS:
        raise StateValidationError(
            f"event findings[{index}] keys mismatch; missing={sorted(FINDING_KEYS - set(mapping))} "
            f"unknown={sorted(set(mapping) - FINDING_KEYS)}"
        )
    text_values = ("id", "source", "critique", "recommendation", "reason", "disposition", "equivalence_key")
    for key in text_values:
        if not _is_non_empty_string(mapping[key]):
            raise StateValidationError(f"event findings[{index}].{key} must be non-empty")
    sources = _string_array(mapping["sources"], f"event findings[{index}].sources")
    evidence = _string_array(mapping["evidence"], f"event findings[{index}].evidence")
    if type(mapping["blocking"]) is not bool or type(mapping["conflict"]) is not bool:
        raise StateValidationError(f"event findings[{index}] blocking and conflict must be boolean")
    assert isinstance(mapping["id"], str)
    assert isinstance(mapping["source"], str)
    assert isinstance(mapping["critique"], str)
    assert isinstance(mapping["recommendation"], str)
    assert isinstance(mapping["reason"], str)
    assert isinstance(mapping["disposition"], str)
    assert isinstance(mapping["equivalence_key"], str)
    if not LEDGER_FINDING_ID.fullmatch(mapping["id"]):
        raise StateValidationError(f"event findings[{index}].id is invalid")
    if mapping["source"] not in REVIEW_SOURCES or any(
        source not in REVIEW_SOURCES for source in sources
    ):
        raise StateValidationError(f"event findings[{index}] has an invalid source")
    if mapping["disposition"] not in {"open", "closed"}:
        raise StateValidationError(f"event findings[{index}].disposition is invalid")
    return ReviewFinding(
        id=mapping["id"],
        source=mapping["source"],
        sources=sources,
        critique=mapping["critique"],
        recommendation=mapping["recommendation"],
        reason=mapping["reason"],
        blocking=mapping["blocking"],
        evidence=evidence,
        disposition=mapping["disposition"],
        conflict=mapping["conflict"],
        equivalence_key=mapping["equivalence_key"],
    )


def _ledger_from_events(events: Sequence[EventLedgerEntry]) -> tuple[ReviewFinding, ...]:
    for entry in reversed(events):
        raw_findings = entry.payload.get("findings")
        if raw_findings is None:
            continue
        if not isinstance(raw_findings, list):
            raise StateValidationError("event findings must be an array")
        findings = tuple(
            _review_finding_from_mapping(value, index)
            for index, value in enumerate(raw_findings)
        )
        if len({finding.id for finding in findings}) != len(findings):
            raise StateValidationError("event findings must not contain duplicate ids")
        return findings
    return ()


EVENT_KEYS = frozenset({"sequence", "event", "revision", "payload"})
EVENT_NAME = re.compile(r"^[a-z][a-z0-9-]*$")


def _event_mapping(event: EventLedgerEntry) -> dict[str, object]:
    return {
        "sequence": event.sequence,
        "event": event.event,
        "revision": event.revision,
        "payload": dict(event.payload),
    }


def _validated_events(value: object, *, revision: int) -> tuple[EventLedgerEntry, ...]:
    if not isinstance(value, list):
        raise StateValidationError("events must be an array")
    events: list[EventLedgerEntry] = []
    for index, item in enumerate(value, start=1):
        event_mapping = _mapping(item, f"events[{index - 1}]")
        if set(event_mapping) != EVENT_KEYS:
            raise StateValidationError(
                f"events[{index - 1}] keys mismatch; missing={sorted(EVENT_KEYS - set(event_mapping))} "
                f"unknown={sorted(set(event_mapping) - EVENT_KEYS)}"
            )
        sequence = event_mapping["sequence"]
        if sequence != index:
            raise StateValidationError("event sequence must be contiguous from 1")
        event_name = event_mapping["event"]
        if not isinstance(event_name, str) or not EVENT_NAME.fullmatch(event_name):
            raise StateValidationError("event name must be a lowercase kebab-case string")
        event_revision = event_mapping["revision"]
        if not _is_non_negative_integer(event_revision) or event_revision > revision:
            raise StateValidationError("event revision must be between zero and the current revision")
        payload = _mapping(event_mapping["payload"], f"events[{index - 1}].payload")
        try:
            json.dumps(dict(payload), allow_nan=False)
        except (TypeError, ValueError) as error:
            raise StateValidationError(f"events[{index - 1}].payload is not strict JSON") from error
        events.append(
            EventLedgerEntry(
                sequence=sequence,
                event=event_name,
                revision=event_revision,
                payload=dict(payload),
            )
        )
    return tuple(events)


def append_typed_event(state: StateV3, event: TypedEvent) -> StateV3:
    """Append one strict typed event without accepting untyped repair input."""

    if not isinstance(event, TypedEvent):
        raise DesignValidationError("state changes require a typed event")
    if not EVENT_NAME.fullmatch(event.name):
        raise DesignValidationError("typed event name must be lowercase kebab-case")
    payload = _mapping(event.payload, f"{event.name} payload")
    try:
        json.dumps(dict(payload), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise DesignValidationError("typed event payload must be strict JSON") from error
    sequence = state.events[-1].sequence + 1 if state.events else 1
    updated = replace(
        state,
        events=(
            *state.events,
            EventLedgerEntry(sequence, event.name, state.revision, dict(payload)),
        ),
    )
    validate_state(_state_mapping(updated), expected_slug=updated.slug)
    return updated


def _state_mapping(state: StateV3) -> dict[str, object]:
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
        "events": [_event_mapping(event) for event in state.events],
    }
    if state.advisory_return_state is not None:
        payload["advisory_return_state"] = state.advisory_return_state
    return payload


def validate_state(value: Mapping[str, object], *, expected_slug: str) -> StateV3:
    """Validate the exact v3 state object; reject older fields."""

    if not isinstance(value, Mapping):
        raise StateValidationError("state must be a JSON object")
    keys = set(value)
    if not REQUIRED_PERSISTED_KEYS.issubset(keys):
        missing = sorted(REQUIRED_PERSISTED_KEYS - keys)
        raise StateValidationError(f"state missing keys: {missing}")
    unknown = keys - PERSISTED_KEYS
    if unknown:
        raise StateValidationError(f"state has unknown keys: {sorted(unknown)}")
    if value.get("schema") != SCHEMA_V3:
        raise StateValidationError(
            "unsupported state schema; archive state.json or reinitialize manually"
        )
    slug = value.get("slug")
    if not isinstance(slug, str) or slug != expected_slug or not SLUG.fullmatch(slug):
        raise StateValidationError("state slug does not match the expected slug")

    state_name = value.get("state")
    if state_name not in STATES:
        raise StateValidationError("state is not a supported v3 state")
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
        raise StateValidationError("assurance must be lightweight, standard, or intensive")

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

    events = _validated_events(value.get("events"), revision=revision)

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

    if state_name in {"WAIT_G0", "WAIT_G1", "WAIT_G2"}:
        if sources or reviewed is not None or approved is not None:
            raise StateValidationError("early gate cannot claim later review or approval")
    if state_name in {"WAIT_G4", "WAIT_G5", "APPROVED"} | TERMINAL_STATES:
        if reviewed is None or not sources:
            raise StateValidationError("review gate requires current mandatory review evidence")
        if assurance == "intensive" and set(sources) != REVIEW_SOURCES:
            raise StateValidationError("intensive assurance requires standard and independent review")
    if state_name in {"APPROVED"} | TERMINAL_STATES and approved is None:
        raise StateValidationError("approved state requires current approval")
    if state_name not in {"APPROVED"} | TERMINAL_STATES and approved is not None:
        raise StateValidationError("approval can only be persisted in APPROVED")

    return StateV3(
        schema=SCHEMA_V3,
        slug=slug,
        revision=revision,
        state=state_name,
        design_sha256=design_hash,
        assurance=assurance,
        review_sources=sources,
        reviewed_revision=reviewed,
        approved_revision=approved,
        advisory_return_state=advisory_return,
        events=events,
    )


def serialize_state(state: StateV3) -> str:
    """Serialize only the canonical v3 state fields and event ledger."""

    if state.schema != SCHEMA_V3:
        raise StateValidationError("only internal-gateway-idea-state/v3 can be persisted")
    return json.dumps(_state_mapping(state), sort_keys=True, separators=(",", ":")) + "\n"


def parse_state(payload: str | Mapping[str, object], *, expected_slug: str) -> StateV3:
    decoded = _strict_json_loads(payload) if isinstance(payload, str) else payload
    state = validate_state(_mapping(decoded, "state"), expected_slug=expected_slug)
    return replace(state, ledger=_ledger_from_events(state.events))


def render_design_projection(state: StateV3) -> str:
    """Render a deterministic readable projection without becoming state authority."""

    validate_state(_state_mapping(state), expected_slug=state.slug)
    decisions = [
        f"{entry.sequence}. {entry.event} (revision {entry.revision})"
        for entry in state.events
    ] or ["None recorded."]
    text = "\n\n".join(
        (
            "# Idea Design",
            "## Intent\nRuntime projection for the bounded idea workflow.",
            "## Accepted Decisions\n" + "\n".join(f"- {decision}" for decision in decisions),
            "## Open Decisions\n- None recorded.",
            "## Selected Approach\n" + f"- Current route: {state.state}.",
            "## Essential Evidence\n" + f"- Typed event ledger entries: {len(state.events)}.",
        )
    )
    if state.ledger:
        text = text + "\n\n" + _ledger_markdown(state.ledger)
    validate_design_text(text, pre_g3=state.state in {"WAIT_G0", "WAIT_G1", "WAIT_G2", "WAIT_G3"})
    return text + "\n"


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


def _route_fields(state: StateV3) -> tuple[str, str, tuple[str, ...], str]:
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


def derive_route(state: StateV3) -> Route:
    actor, owner, events, action = _route_fields(state)
    return Route(
        state=state.state,
        next_actor=actor,
        next_owner=owner,
        legal_events=events,
        next_action=action,
        authorizes_execution=state.state == DIRECT_EXECUTION,
    )


def select_discovery_mode(
    impact: str,
    confidence: str,
    default_safety: bool,
) -> DiscoveryDecision:
    if impact not in DISCOVERY_LEVELS:
        raise DesignValidationError("impact must be low, medium, or high")
    if confidence not in DISCOVERY_LEVELS:
        raise DesignValidationError("confidence must be low, medium, or high")
    if type(default_safety) is not bool:
        raise DesignValidationError("default_safety must be boolean")

    if impact == "high" or confidence == "low" or not default_safety:
        mode = "pre-draft"
        rationale = "Consequential or unsafe uncertainty requires bounded discovery before drafting."
        next_artifact = "decision-brief"
    elif impact == "medium" or confidence == "medium":
        mode = "targeted-refinement"
        rationale = "Material ambiguity is narrow enough for focused refinement before the draft."
        next_artifact = "refinement-questions"
    else:
        mode = "direct-draft"
        rationale = "The request is clear, falsifiable, and safe to draft directly."
        next_artifact = "design-draft"
    return DiscoveryDecision(
        mode=mode,
        impact=impact,
        confidence=confidence,
        default_safety=default_safety,
        rationale=rationale,
        next_artifact=next_artifact,
    )


def minimum_assurance(impact: str, confidence: str, default_safety: bool) -> str:
    if impact not in DISCOVERY_LEVELS:
        raise DesignValidationError("impact must be low, medium, or high")
    if confidence not in DISCOVERY_LEVELS:
        raise DesignValidationError("confidence must be low, medium, or high")
    if type(default_safety) is not bool:
        raise DesignValidationError("default_safety must be boolean")
    if impact == "high" or confidence == "low":
        return "intensive"
    if impact == "medium" or confidence == "medium" or not default_safety:
        return "standard"
    return "lightweight"


def enforce_assurance_minimum(
    requested: str,
    impact: str,
    confidence: str,
    default_safety: bool,
) -> str:
    if requested not in ASSURANCES:
        raise DesignValidationError("assurance must be lightweight, standard, or intensive")
    minimum = minimum_assurance(impact, confidence, default_safety)
    if ASSURANCE_RANK[requested] < ASSURANCE_RANK[minimum]:
        raise DesignValidationError(
            f"requested assurance {requested} is below the computed minimum {minimum}"
        )
    return requested


def record_discovery_decision(state: StateV3, decision: DiscoveryDecision) -> StateV3:
    if not isinstance(decision, DiscoveryDecision):
        raise DesignValidationError("discovery decisions must be typed")
    if state.state not in {"WAIT_G0", "WAIT_G1", "WAIT_G2", "WAIT_G3"}:
        raise DesignValidationError("discovery selection is not legal after handoff")
    selected = select_discovery_mode(
        decision.impact, decision.confidence, decision.default_safety
    )
    if selected != decision:
        raise DesignValidationError("discovery decision is not deterministic")
    return append_typed_event(
        state,
        TypedEvent(
            "select-discovery",
            {
                "mode": decision.mode,
                "impact": decision.impact,
                "confidence": decision.confidence,
                "default_safety": decision.default_safety,
                "rationale": decision.rationale,
                "next_artifact": decision.next_artifact,
            },
        ),
    )


def reopen_for_material_change(
    state: StateV3,
    *,
    trigger: str,
    detail: str = "",
) -> StateV3:
    if trigger not in MATERIAL_REOPEN_TRIGGERS:
        raise DesignValidationError(
            "reopen requires a material evidence, scope, constraint, validation, or dependency change"
        )
    if not _is_non_empty_string(detail):
        raise DesignValidationError("material reopen needs a non-empty detail")
    target_state = state.state if state.state in {"WAIT_G0", "WAIT_G1", "WAIT_G2"} else "WAIT_G3"
    reopened = replace(
        state,
        state=target_state,
        revision=state.revision + 1,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        advisory_return_state=None,
        ledger=state.ledger,
    )
    return append_typed_event(
        reopened,
        TypedEvent(
            "reopen-review",
            {
                "trigger": trigger,
                "detail": detail.strip(),
                "next_state": target_state,
                "next_revision": reopened.revision,
            },
        ),
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
        "finding_resolutions",
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
    if "finding_resolutions" in payload:
        _resolution_entries(payload["finding_resolutions"])


def validate_event(event: Mapping[str, object], *, current_state: StateV3) -> TypedEvent:
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
        _payload_keys(payload, {"token", "note"}, "approve payload")
        if "token" in payload and not _is_non_empty_string(payload["token"]):
            raise DesignValidationError("approve token must be non-empty")
        if "note" in payload and not _is_non_empty_string(payload["note"]):
            raise DesignValidationError("approve note must be non-empty when present")
    else:
        raise DesignValidationError(f"unknown or future event: {name}")
    return TypedEvent(name=name, payload=dict(payload))


def adapt_presented_approval(
    message: str,
    *,
    current_state: StateV3,
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
    current_state: StateV3,
    presented: PresentedDecision,
) -> TypedEvent:
    if _gate_for_state(current_state.state) not in {presented.gate, current_state.state}:
        raise DesignValidationError("presented answer is not bound to the current gate")
    return validate_event(
        {"event": presented.event_name, "payload": dict(payload)},
        current_state=current_state,
    )


def _clear_review(state: StateV3, *, state_name: str | None = None, revision: int | None = None) -> StateV3:
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


def _assurance_review_complete(state: StateV3, sources: Sequence[str] | None = None) -> bool:
    available = set(state.review_sources if sources is None else sources)
    return set(available) == REVIEW_SOURCES if state.assurance == "intensive" else "standard" in available


def transition_gate(state: StateV3, event: TypedEvent, *, gate: str) -> TransitionResult:
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
        if not _assurance_review_complete(state):
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
            finding_resolutions=_resolution_entries(
                validated.payload.get("finding_resolutions")
            ),
        )
    elif validated.name == "approve" and state.state == "WAIT_G5":
        if (
            state.reviewed_revision != state.revision
            or not _assurance_review_complete(state)
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
    if validated.name != "resolve-review":
        next_state = append_typed_event(next_state, validated)
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


def replace_design_then_state(root: Path, design_text: str, state: StateV3) -> None:
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
    persisted = replace(state, schema=SCHEMA_V3, design_sha256=design_hash, design_text=None)
    # The state validator is deliberately applied after the design replacement;
    # a failure leaves a conservative hash mismatch for the next load.
    validate_state(_state_mapping(persisted), expected_slug=persisted.slug)
    _atomic_replace_text(state_path, serialize_state(persisted))


def _persist_state_only(root: Path, state: StateV3) -> None:
    replace_design_then_state(Path(root), render_design_projection(state), state)


def _empty_runtime_state(slug: str, *, design_hash: str = "") -> StateV3:
    return StateV3(
        schema=SCHEMA_V3,
        slug=slug,
        revision=0,
        state="WAIT_G0",
        design_sha256=design_hash,
        assurance="standard",
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
    )


def _earliest_safe_state(events: Sequence[EventLedgerEntry]) -> str:
    current = "WAIT_G0"
    for entry in events:
        payload = entry.payload
        if entry.event == "resolve-g0" and current == "WAIT_G0":
            current = "WAIT_G1"
        elif entry.event == "approve" and current == "WAIT_G1":
            current = "WAIT_G2"
        elif entry.event == "select-approach" and current == "WAIT_G2":
            current = "WAIT_G3"
        elif entry.event == "record-review" and payload.get("review_complete") is True:
            current = "WAIT_G4"
        elif entry.event == "reopen-review":
            current = "WAIT_G3"
    return current


def recover_hash_mismatch(snapshot: RuntimeSnapshot) -> StateV3:
    design_hash = ""
    if snapshot.design_text is not None:
        design_hash = hashlib.sha256(snapshot.design_text.encode("utf-8")).hexdigest()
    safe_state = _earliest_safe_state(snapshot.state.events)
    cleared = replace(
        snapshot.state,
        schema=SCHEMA_V3,
        state=safe_state,
        design_sha256=design_hash,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        advisory_return_state=None,
        ledger=(),
    )
    return append_typed_event(
        cleared,
        TypedEvent(
            "repair-state",
            {
                "from_state": snapshot.state.state,
                "to_state": safe_state,
                "reason": snapshot.recovery_reason or "design-hash-mismatch",
            },
        ),
    )


def load_runtime(
    root: Path,
    *,
    slug: str = "sample",
    persist_recovery: bool = True,
) -> RuntimeSnapshot:
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
        if not persist_recovery:
            return RuntimeSnapshot(
                persisted,
                root=root,
                design_text=design_text,
                recovery_reason="design hash mismatch; recovery required",
                stable_artifacts=("design.md", "state.json"),
            )
        recovered = recover_hash_mismatch(
            RuntimeSnapshot(persisted, root=root, design_text=design_text)
        )
        recovered_design = render_design_projection(recovered)
        replace_design_then_state(root, recovered_design, recovered)
        return RuntimeSnapshot(
            recovered,
            root=root,
            design_text=recovered_design,
            recovery_reason="design hash mismatch; later claims cleared",
            stable_artifacts=("design.md", "state.json"),
        )
    return RuntimeSnapshot(
        replace(persisted, design_text=design_text),
        root=root,
        design_text=design_text,
        stable_artifacts=("design.md", "state.json"),
    )


def recover_runtime(root: Path, *, slug: str) -> RuntimeSnapshot:
    """Load and persist any deterministic recovery before returning it."""

    snapshot = load_runtime(Path(root), slug=slug)
    if snapshot.recovery_reason and snapshot.stable_artifacts != (
        "design.md",
        "state.json",
    ):
        raise DesignValidationError(
            f"cannot recover unpersisted runtime: {snapshot.recovery_reason}; "
            "expected state.json and design.md; archive artifacts or reinitialize manually"
        )
    if snapshot.recovery_reason and snapshot.design_text is not None:
        persisted = parse_state(
            (Path(root) / "state.json").read_text(encoding="utf-8"),
            expected_slug=slug,
        )
        design_text = (Path(root) / "design.md").read_text(encoding="utf-8")
        return RuntimeSnapshot(
            replace(persisted, design_text=design_text),
            root=Path(root),
            design_text=design_text,
            recovery_reason=snapshot.recovery_reason,
            stable_artifacts=snapshot.stable_artifacts,
        )
    return snapshot


def initialize_after_g0(
    root: Path,
    *,
    slug: str,
    decision_payload: Mapping[str, object],
    assurance: str,
) -> RuntimeSnapshot:
    if assurance not in ASSURANCES:
        raise DesignValidationError("assurance must be lightweight, standard, or intensive")
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
    state = StateV3(
        schema=SCHEMA_V3,
        slug=slug,
        revision=revision,
        state="WAIT_G1",
        design_sha256="0" * 64,
        assurance=assurance,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        events=existing.state.events if existing.state.state == "ADVISORY_REVIEW" else (),
    )
    state = append_typed_event(state, TypedEvent("resolve-g0", dict(decision_payload)))
    design_text = render_design_projection(state)
    replace_design_then_state(root, design_text, state)
    return load_runtime(root, slug=slug)


def start_advisory(
    state: StateV3,
    *,
    prior_gate: str,
) -> StateV3:
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


def finish_advisory(state: StateV3) -> StateV3:
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
        raise DesignValidationError("assurance must be lightweight, standard, or intensive")
    root = Path(root)
    existing = load_runtime(root, slug=slug)
    if existing.stable_artifacts:
        raise DesignValidationError("advisory-before-G0 requires no stable runtime artifacts")
    _validate_bounded_design(bounded_design)
    state = StateV3(
        schema=SCHEMA_V3,
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
    state: StateV3,
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
        next_state = append_typed_event(
            next_state,
            TypedEvent(
                "record-advisory",
                {
                    "source": parsed.source,
                    "outcome": parsed.outcome,
                    "finding_ids": [finding.id for finding in ledger],
                    "findings": [_review_finding_mapping(finding) for finding in ledger],
                },
            ),
        )
        return ReviewResult(next_state, parsed.source, parsed.outcome, ledger, parsed.residual_risks)

    sources = tuple(
        source for source in ("standard", "independent") if source in (*state.review_sources, parsed.source)
    )
    review_complete = "standard" in sources and (state.assurance != "intensive" or "independent" in sources)
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
    state: StateV3,
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


def promote_advisory_finding(
    state: StateV3,
    finding_id: str,
    *,
    classification: str,
    detail: str,
) -> StateV3:
    if state.state != "ADVISORY_REVIEW":
        raise DesignValidationError("advisory findings can only be promoted during advisory review")
    if classification not in {"blocker", "conflict", "risk-accepted"}:
        raise DesignValidationError("advisory classification is not supported")
    if not _is_non_empty_string(detail):
        raise DesignValidationError("advisory promotion needs a non-empty detail")
    matching = [finding for finding in state.ledger if finding.id == finding_id]
    if len(matching) != 1:
        raise DesignValidationError("advisory finding id is not present in the ledger")
    ledger = tuple(
        replace(
            finding,
            blocking=classification == "blocker" or finding.blocking,
            conflict=classification == "conflict" or finding.conflict,
            disposition="closed" if classification == "risk-accepted" else finding.disposition,
        )
        if finding.id == finding_id
        else finding
        for finding in state.ledger
    )
    promoted = replace(state, ledger=ledger)
    return append_typed_event(
        promoted,
        TypedEvent(
            "promote-advisory",
            {
                "finding_id": finding_id,
                "classification": classification,
                "detail": detail.strip(),
                "findings": [_review_finding_mapping(finding) for finding in ledger],
            },
        ),
    )


def record_review(
    state: StateV3,
    packet: Mapping[str, object],
    *,
    g3_approval_event: TypedEvent,
    expected_target_path: str,
    expected_revision: int,
) -> StateV3:
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
    next_state = result.state
    return append_typed_event(
        next_state,
        TypedEvent(
            "record-review",
            {
                "source": result.source or "",
                "outcome": result.outcome or "",
                "review_sources": list(next_state.review_sources),
                "review_complete": next_state.state == "WAIT_G4",
                "finding_ids": [finding.id for finding in result.findings],
                "findings": [_review_finding_mapping(finding) for finding in result.findings],
            },
        ),
    )


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
    state: StateV3,
    report: str,
    *,
    source: str,
    g3_approval_event: TypedEvent,
    expected_target_path: str,
    expected_revision: int,
) -> StateV3:
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
    state: StateV3,
    *,
    disposition: str,
    remedy: Mapping[str, object] | None,
    risk_decision: Mapping[str, object] | None,
    presented_default: bool = False,
    finding_resolutions: Sequence[FindingResolutionEvidence] | None = None,
) -> StateV3:
    payload: dict[str, object] = {"disposition": disposition, "presented_default": presented_default}
    if remedy is not None:
        payload["remedy"] = remedy
    if risk_decision is not None:
        payload["risk_decision"] = risk_decision
    resolutions = _resolution_entries(finding_resolutions)
    payload["finding_resolutions"] = [_resolution_mapping(item) for item in resolutions]
    _validate_resolution_payload(payload)
    if state.state != "WAIT_G4":
        raise DesignValidationError("resolve-review requires WAIT_G4")
    if disposition in {"closed", "accepted-remedy", "accepted-risk"}:
        evidence_by_id = {item.finding_id: item for item in resolutions}
        missing_proof = [
            item.id
            for item in state.ledger
            if item.disposition != "closed"
            and (item.blocking or item.conflict)
            and item.id not in evidence_by_id
        ]
        if missing_proof:
            raise DesignValidationError(
                "finding proof or explicit risk acceptance is required for: "
                + ", ".join(missing_proof)
            )
        ledger = tuple(
            replace(item, disposition="closed")
            if item.disposition != "closed"
            else item
            for item in state.ledger
        )
        if _has_open_blocker_or_conflict(ledger):
            raise DesignValidationError("review blockers or conflicts remain open")
        next_state = replace(state, state="WAIT_G5", ledger=ledger, approved_revision=None)
    else:
        next_state = replace(
        state,
        state="WAIT_G3",
        revision=state.revision + 1,
        review_sources=(),
        reviewed_revision=None,
        approved_revision=None,
        ledger=state.ledger,
        )
    event_payload = dict(payload)
    event_payload.update(
        {
            "next_state": next_state.state,
            "next_revision": next_state.revision,
            "findings": [_review_finding_mapping(finding) for finding in next_state.ledger],
        }
    )
    return append_typed_event(next_state, TypedEvent("resolve-review", event_payload))


def can_enter_g5(state: StateV3, design_hash: str) -> bool:
    return (
        state.state == "WAIT_G4"
        and state.design_sha256 == design_hash
        and state.reviewed_revision == state.revision
        and _assurance_review_complete(state)
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


def _compact_for_snapshot(snapshot: RuntimeSnapshot) -> str:
    route = derive_route(snapshot.state)
    events = ",".join(route.legal_events) or "none"
    action = " ".join(route.next_action.split())
    counts = derive_workflow_counts(snapshot.state)
    count_text = (
        f"discovery:{counts.discovery_turns},approvals:{counts.approvals},"
        f"reopenings:{counts.reopenings},critic:{counts.critic_runs},"
        f"recovery:{counts.recovery_events}"
    )
    return (
        f"state={snapshot.state.state}|revision={snapshot.state.revision}|"
        f"actor={route.next_actor}|events={events}|action={action}|counts={count_text}"
    )


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


def validate_runtime_root(root: Path, slug: str) -> Path:
    root = Path(root).expanduser()
    if not isinstance(slug, str) or not SLUG.fullmatch(slug):
        raise DesignValidationError("slug must be a non-empty directory name")
    if root.name != slug:
        expected = root / slug
        raise DesignValidationError(
            f"--root must be the slug directory '{slug}'; expected {expected}"
        )
    return root


def derive_workflow_counts(state: StateV3) -> WorkflowCounts:
    if not isinstance(state, StateV3):
        raise DesignValidationError("workflow counts require v3 state")
    event_names = [entry.event for entry in state.events]
    return WorkflowCounts(
        discovery_turns=event_names.count("select-discovery"),
        approvals=event_names.count("approve"),
        reopenings=event_names.count("reopen-review"),
        critic_runs=sum(
            event_name in {"record-review", "record-advisory"}
            for event_name in event_names
        ),
        recovery_events=event_names.count("repair-state"),
    )


def _cli_inspect(root: Path, slug: str, compact: bool) -> int:
    root = validate_runtime_root(root, slug)
    snapshot = load_runtime(root, slug=slug, persist_recovery=False)
    if snapshot.recovery_reason:
        raise DesignValidationError(
            f"inspect cannot recover runtime: {snapshot.recovery_reason}; "
            "use recover explicitly"
        )
    if compact:
        print(_compact_for_snapshot(snapshot))
    else:
        print(json.dumps(_json_projection(snapshot), sort_keys=True, separators=(",", ":")))
    return 0


def _cli_init(args: argparse.Namespace) -> int:
    payload = _mapping(_cli_payload(args.payload_json, name="init"), "init payload")
    root = validate_runtime_root(_cli_root(args.root), args.slug)
    initialize_after_g0(
        root,
        slug=args.slug,
        decision_payload=payload,
        assurance=args.assurance,
    )
    return _cli_inspect(root, args.slug, args.compact)


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
    root = validate_runtime_root(_cli_root(args.root), args.slug)
    start_advisory_before_g0(
        root,
        slug=args.slug,
        bounded_design=design,
        assurance=args.assurance,
    )
    return _cli_inspect(root, args.slug, args.compact)


def _cli_advance(args: argparse.Namespace) -> int:
    root = validate_runtime_root(_cli_root(args.root), args.slug)
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
    root = validate_runtime_root(_cli_root(args.root), args.slug)
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
    parser = argparse.ArgumentParser(description="Manage internal-gateway-idea-state/v3.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_runtime_options(command: argparse.ArgumentParser) -> None:
        command.add_argument("--root", required=True)
        command.add_argument("--slug", required=True)
        command.add_argument("--compact", action="store_true")

    inspect = subparsers.add_parser("inspect")
    add_runtime_options(inspect)
    inspect.set_defaults(
        handler=lambda args: _cli_inspect(
            validate_runtime_root(_cli_root(args.root), args.slug), args.slug, args.compact
        )
    )

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
    raw = _strict_json_loads(payload)
    value = _mapping(raw, "state")
    slug = value.get("slug")
    if not isinstance(slug, str):
        raise DesignValidationError("state.json needs a slug")
    state = validate_state(value, expected_slug=slug)
    snapshot = RuntimeSnapshot(state, root=path.parent)
    if args.compact:
        print(_compact_for_snapshot(snapshot))
    else:
        print(json.dumps(_json_projection(snapshot), sort_keys=True, separators=(",", ":")))
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
