#!/usr/bin/env python3
"""Score sanitized internal-gateway-idea evaluation records."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path

CONTRACT_VERSION = "internal-gateway-idea-eval-v1"
CASE_IDS = ("C-01", "C-02", "C-03", "C-04", "C-05")
REQUIRED_RECORD_KEYS = (
    "decision_records",
    "question_records",
    "evidence_records",
    "transition_events",
    "route_events",
    "artifact_events",
    "authority_events",
    "communication_records",
    "recovery_records",
    "provenance",
)
EVIDENCE_CLASSES = frozenset(
    {"Facts", "Reports", "Assumptions", "Unknowns", "Constraints"}
)
DECISION_STATES = frozenset(
    {
        "eligible-now",
        "blocked-later",
        "deferred",
        "resolved-from-evidence",
        "accepted",
        "accepted-risk",
        "rejected",
        "open",
    }
)
TERMINAL_STATES = frozenset(
    {"deferred", "resolved-from-evidence", "accepted", "accepted-risk", "rejected"}
)
REOPEN_TRIGGERS = frozenset(
    {"new-evidence", "explicit-user-change", "critical-finding"}
)
CAPSULE_FIELDS = (
    "subject",
    "mode",
    "decision_focus",
    "accepted_ids",
    "rejected_ids",
    "deferred_ids",
    "accepted_risk_ids",
    "eligible_now_ids",
    "blocked_later",
    "evidence_anchors",
    "next_action",
)
RECOVERY_RECORD_FIELDS = (
    "record_id",
    "event_index",
    "unit_lock",
    "state_capsule",
    "decision_ledger",
    "authority_envelope",
    "communication_projection",
)
RECOVERY_UNIT_LOCK_FIELDS = (
    "subject",
    "mode",
    "decision_focus",
    "desired_artifact",
    "implementation_permission",
)
RECOVERY_CAPSULE_FIELDS = (
    "subject",
    "mode",
    "decision_focus",
    "terminal_decision_ids",
    "eligible_now_ids",
    "blocked_later",
    "evidence_anchors",
    "next_action",
)
RECOVERY_LEDGER_FIELDS = (
    "decision_id",
    "state",
    "basis",
    "reopen_condition",
    "dependencies",
)
RECOVERY_AUTHORITY_FIELDS = (
    "authorized_paths",
    "authorized_actions",
    "continuation_boundaries",
)
COMMUNICATION_FIELDS = (
    "view_id",
    "kind",
    "event_index",
    "material_delta_ids",
    "outcome",
    "controlling_evidence_ids",
    "principal_risk_id",
    "active_choice",
    "blocker_ids",
    "unknown_ids",
    "acceptance_condition_ids",
    "word_count",
    "word_count_mode",
    "diagrams",
)
FINDING_FIELDS = (
    "recoverable_fact_question_cases",
    "premature_dependent_question_cases",
    "split_known_question_batch_cases",
    "unmapped_question_cases",
    "uncovered_material_root_cases",
    "unjustified_reopen_cases",
    "rejected_reappearance_cases",
    "anchored_challenge_violation_cases",
    "visible_alternative_violation_cases",
    "state_continuity_violation_cases",
    "analysis_only_routing_violation_cases",
    "critical_choice_violation_cases",
    "critical_disposition_violation_cases",
    "artifact_replay_violation_cases",
    "multiple_saved_artifact_cases",
    "save_semantics_violation_cases",
    "lifecycle_order_violation_cases",
    "authority_envelope_violation_cases",
    "protected_status_authority_violation_cases",
    "scope_delta_violation_cases",
    "canonical_view_violation_cases",
    "canonical_recovery_violation_cases",
    "route_projection_violation_cases",
    "visual_budget_violation_cases",
    "protected_workflow_violation_cases",
    "self_attested_verdict_cases",
    "gate_type_violation_cases",
    "grill_me_routing_violation_cases",
    "critical_review_completion_violation_cases",
    "gate_override_violation_cases",
    "menu_projection_violation_cases",
    "provisional_save_violation_cases",
    "spec_plan_readiness_violation_cases",
)


def _schema_error(message: str) -> ValueError:
    return ValueError(f"schema error: {message}")


def _require_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise _schema_error(f"{label} must be an object")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _schema_error(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise _schema_error(f"{label} must be a list of non-empty strings")
    return list(value)


def _require_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise _schema_error(f"{label} must be a list")
    return value


def _require_event_index(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _schema_error(f"{label} must be a number")
    return float(value)


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _schema_error(f"unable to load {path}: {exc}") from exc


def _validate_manifest(manifest: object) -> Mapping[str, object]:
    value = _require_mapping(manifest, "manifest")
    if value.get("contract_version") != CONTRACT_VERSION:
        raise _schema_error("manifest.contract_version is unsupported")

    case_ids = _require_string_list(
        value.get("required_case_ids"), "manifest.required_case_ids"
    )
    if tuple(case_ids) != CASE_IDS or len(set(case_ids)) != len(case_ids):
        raise _schema_error(
            "manifest.required_case_ids must contain C-01 through C-05 once"
        )
    record_keys = _require_string_list(
        value.get("required_record_keys"), "manifest.required_record_keys"
    )
    if tuple(record_keys) != REQUIRED_RECORD_KEYS:
        raise _schema_error("manifest.required_record_keys does not match the contract")
    _require_string_list(
        value.get("forbidden_verdict_fields"), "manifest.forbidden_verdict_fields"
    )

    protected = _require_mapping(
        value.get("protected_workflow"), "manifest.protected_workflow"
    )
    required_classes = _require_string_list(
        protected.get("required_evidence_classes"),
        "manifest.protected_workflow.required_evidence_classes",
    )
    if set(required_classes) != EVIDENCE_CLASSES:
        raise _schema_error("manifest protected evidence classes are incomplete")
    for field in (
        "max_recoverable_fact_questions",
        "max_premature_dependent_questions",
        "max_unjustified_reopens",
        "max_split_known_question_batches",
        "max_saved_artifacts",
    ):
        limit = protected.get(field)
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise _schema_error(
                f"manifest.protected_workflow.{field} must be a non-negative integer"
            )
    for field in (
        "forbid_fixed_question_cap",
        "forbid_automatic_critical_realign",
        "save_is_non_promoting",
    ):
        if not isinstance(protected.get(field), bool):
            raise _schema_error(f"manifest.protected_workflow.{field} must be boolean")

    requirements = _require_mapping(
        value.get("case_requirements"), "manifest.case_requirements"
    )
    for case_id in CASE_IDS:
        _require_mapping(
            requirements.get(case_id), f"manifest.case_requirements.{case_id}"
        )
    _require_string_list(
        value.get("analysis_only_forbidden_routes"),
        "manifest.analysis_only_forbidden_routes",
    )
    authority = _require_mapping(
        value.get("authority_workflow"), "manifest.authority_workflow"
    )
    _require_string_list(
        authority.get("required_event_types"),
        "manifest.authority_workflow.required_event_types",
    )
    _require_string_list(
        authority.get("continuation_boundaries"),
        "manifest.authority_workflow.continuation_boundaries",
    )
    _require_string(
        authority.get("scope_delta_outcome"),
        "manifest.authority_workflow.scope_delta_outcome",
    )
    lifecycle = _require_mapping(
        value.get("lifecycle_workflow"), "manifest.lifecycle_workflow"
    )
    global_gates = _require_string_list(
        lifecycle.get("global_gates"), "manifest.lifecycle_workflow.global_gates"
    )
    if global_gates != ["GRILL-ME", "CRITICAL REVIEW"]:
        raise _schema_error(
            "manifest.lifecycle_workflow.global_gates must contain exactly GRILL-ME and CRITICAL REVIEW"
        )
    if lifecycle.get("post_setup_gate") != "GRILL-ME":
        raise _schema_error(
            "manifest.lifecycle_workflow.post_setup_gate must be GRILL-ME"
        )
    review_lenses = _require_string_list(
        lifecycle.get("review_lenses"), "manifest.lifecycle_workflow.review_lenses"
    )
    if review_lenses != ["primary", "evidence", "lateral"]:
        raise _schema_error(
            "manifest.lifecycle_workflow.review_lenses must contain the three required review lenses"
        )
    lateral_lens_types = _require_string_list(
        lifecycle.get("lateral_lens_types"),
        "manifest.lifecycle_workflow.lateral_lens_types",
    )
    if lateral_lens_types != ["analogy", "reverse-assumption"]:
        raise _schema_error(
            "manifest.lifecycle_workflow.lateral_lens_types is unsupported"
        )
    _require_string_list(
        lifecycle.get("candidate_menu"), "manifest.lifecycle_workflow.candidate_menu"
    )
    for field in (
        "critical_review_event",
        "realignment_event",
        "critical_finding_event",
        "disposition_event",
    ):
        _require_string(lifecycle.get(field), f"manifest.lifecycle_workflow.{field}")
    _require_string_list(
        lifecycle.get("promotion_options"),
        "manifest.lifecycle_workflow.promotion_options",
    )
    _require_string(
        lifecycle.get("spec_artifact_readiness_field"),
        "manifest.lifecycle_workflow.spec_artifact_readiness_field",
    )
    _require_string_list(
        lifecycle.get("allowed_dispositions"),
        "manifest.lifecycle_workflow.allowed_dispositions",
    )
    _require_string(
        lifecycle.get("gate_override_event"),
        "manifest.lifecycle_workflow.gate_override_event",
    )
    _require_string_list(
        lifecycle.get("finding_classifications"),
        "manifest.lifecycle_workflow.finding_classifications",
    )
    communication = _require_mapping(
        value.get("communication_workflow"), "manifest.communication_workflow"
    )
    _require_string(
        communication.get("candidate_kind"),
        "manifest.communication_workflow.candidate_kind",
    )
    for field in (
        "max_controlling_evidence",
        "max_diagrams",
        "diagram_min_relationships",
    ):
        limit = communication.get(field)
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise _schema_error(
                f"manifest.communication_workflow.{field} must be a non-negative integer"
            )
    _require_string(
        communication.get("word_count_mode"),
        "manifest.communication_workflow.word_count_mode",
    )
    return value


def _validate_record_list(
    records: object,
    label: str,
    required_fields: tuple[str, ...],
) -> list[Mapping[str, object]]:
    values = _require_list(records, label)
    result: list[Mapping[str, object]] = []
    for index, record in enumerate(values):
        mapping = _require_mapping(record, f"{label}[{index}]")
        for field in required_fields:
            if field not in mapping:
                raise _schema_error(f"{label}[{index}] is missing {field}")
        result.append(mapping)
    return result


def _validate_communication_records(
    records: object, label: str
) -> list[Mapping[str, object]]:
    values = _validate_record_list(records, label, COMMUNICATION_FIELDS)
    for index, record in enumerate(values):
        record_label = f"{label}[{index}]"
        for field in (
            "view_id",
            "kind",
            "outcome",
            "principal_risk_id",
            "active_choice",
            "word_count_mode",
        ):
            _require_string(record[field], f"{record_label}.{field}")
        for field in (
            "material_delta_ids",
            "controlling_evidence_ids",
            "blocker_ids",
            "unknown_ids",
            "acceptance_condition_ids",
        ):
            _require_string_list(record[field], f"{record_label}.{field}")
        if isinstance(record["word_count"], bool) or not isinstance(
            record["word_count"], int
        ):
            raise _schema_error(f"{record_label}.word_count must be an integer")
        diagrams = _require_list(record["diagrams"], f"{record_label}.diagrams")
        for diagram_index, diagram in enumerate(diagrams):
            diagram_mapping = _require_mapping(
                diagram, f"{record_label}.diagrams[{diagram_index}]"
            )
            relationship_count = diagram_mapping.get("relationship_count")
            if isinstance(relationship_count, bool) or not isinstance(
                relationship_count, int
            ):
                raise _schema_error(
                    f"{record_label}.diagrams[{diagram_index}].relationship_count must be an integer"
                )
            for field in ("useful", "conclusion_adjacent"):
                if not isinstance(diagram_mapping.get(field), bool):
                    raise _schema_error(
                        f"{record_label}.diagrams[{diagram_index}].{field} must be boolean"
                    )
    return values


def _validate_run(
    manifest: Mapping[str, object], run: object
) -> list[Mapping[str, object]]:
    value = _require_mapping(run, "run")
    observations = _validate_record_list(
        value.get("observations"),
        "run.observations",
        ("observation_id", "case_id", "kind", *REQUIRED_RECORD_KEYS),
    )
    seen_observation_ids: set[str] = set()
    for observation_index, observation in enumerate(observations):
        observation_id = _require_string(
            observation["observation_id"],
            f"run.observations[{observation_index}].observation_id",
        )
        if observation_id in seen_observation_ids:
            raise _schema_error(f"duplicate observation_id: {observation_id}")
        seen_observation_ids.add(observation_id)
        case_id = _require_string(
            observation["case_id"], f"run.observations[{observation_index}].case_id"
        )
        if case_id not in CASE_IDS:
            raise _schema_error(f"unsupported case_id: {case_id}")
        _require_string(
            observation["kind"], f"run.observations[{observation_index}].kind"
        )

        decisions = _validate_record_list(
            observation["decision_records"],
            f"{observation_id}.decision_records",
            ("decision_id", "status", "material", "dependencies", "evidence_ids"),
        )
        decision_ids: set[str] = set()
        for index, decision in enumerate(decisions):
            decision_id = _require_string(
                decision["decision_id"],
                f"{observation_id}.decision_records[{index}].decision_id",
            )
            if decision_id in decision_ids:
                raise _schema_error(
                    f"duplicate decision_id in {observation_id}: {decision_id}"
                )
            decision_ids.add(decision_id)
            status = _require_string(
                decision["status"], f"{observation_id}.decision_records[{index}].status"
            )
            if status not in DECISION_STATES:
                raise _schema_error(f"unsupported decision state: {status}")
            if not isinstance(decision["material"], bool):
                raise _schema_error(
                    f"{observation_id}.decision_records[{index}].material must be boolean"
                )
            _require_string_list(
                decision["dependencies"],
                f"{observation_id}.decision_records[{index}].dependencies",
            )
            _require_string_list(
                decision["evidence_ids"],
                f"{observation_id}.decision_records[{index}].evidence_ids",
            )
            if "reopen_condition" in decision:
                _require_string(
                    decision["reopen_condition"],
                    f"{observation_id}.decision_records[{index}].reopen_condition",
                )

        questions = _validate_record_list(
            observation["question_records"],
            f"{observation_id}.question_records",
            (
                "question_id",
                "decision_id",
                "event_index",
                "eligible_event_index",
                "block_id",
                "evidence_ids",
                "prerequisites",
            ),
        )
        question_ids: set[str] = set()
        for index, question in enumerate(questions):
            question_id = _require_string(
                question["question_id"],
                f"{observation_id}.question_records[{index}].question_id",
            )
            if question_id in question_ids:
                raise _schema_error(
                    f"duplicate question_id in {observation_id}: {question_id}"
                )
            question_ids.add(question_id)
            _require_string(
                question["decision_id"],
                f"{observation_id}.question_records[{index}].decision_id",
            )
            question_event_index = _require_event_index(
                question["event_index"],
                f"{observation_id}.question_records[{index}].event_index",
            )
            eligible_event_index = _require_event_index(
                question["eligible_event_index"],
                f"{observation_id}.question_records[{index}].eligible_event_index",
            )
            if eligible_event_index > question_event_index:
                raise _schema_error(f"{question_id} became eligible after it was asked")
            _require_string(
                question["block_id"],
                f"{observation_id}.question_records[{index}].block_id",
            )
            _require_string_list(
                question["evidence_ids"],
                f"{observation_id}.question_records[{index}].evidence_ids",
            )
            _require_string_list(
                question["prerequisites"],
                f"{observation_id}.question_records[{index}].prerequisites",
            )

        evidence = _validate_record_list(
            observation["evidence_records"],
            f"{observation_id}.evidence_records",
            ("evidence_id", "class", "strength", "event_index", "decision_ids"),
        )
        evidence_ids: set[str] = set()
        for index, item in enumerate(evidence):
            evidence_id = _require_string(
                item["evidence_id"],
                f"{observation_id}.evidence_records[{index}].evidence_id",
            )
            if evidence_id in evidence_ids:
                raise _schema_error(
                    f"duplicate evidence_id in {observation_id}: {evidence_id}"
                )
            evidence_ids.add(evidence_id)
            evidence_class = _require_string(
                item["class"], f"{observation_id}.evidence_records[{index}].class"
            )
            if evidence_class not in EVIDENCE_CLASSES:
                raise _schema_error(f"unsupported evidence class: {evidence_class}")
            _require_string(
                item["strength"], f"{observation_id}.evidence_records[{index}].strength"
            )
            _require_event_index(
                item["event_index"],
                f"{observation_id}.evidence_records[{index}].event_index",
            )
            _require_string_list(
                item["decision_ids"],
                f"{observation_id}.evidence_records[{index}].decision_ids",
            )

        for key in ("transition_events", "route_events", "artifact_events"):
            events = _validate_record_list(
                observation[key], f"{observation_id}.{key}", ("event", "event_index")
            )
            for index, event in enumerate(events):
                _require_string(
                    event["event"], f"{observation_id}.{key}[{index}].event"
                )
                _require_event_index(
                    event["event_index"], f"{observation_id}.{key}[{index}].event_index"
                )
            if key == "route_events":
                for index, event in enumerate(events):
                    _require_string(
                        event.get("owner"),
                        f"{observation_id}.route_events[{index}].owner",
                    )
                    _require_string(
                        event.get("mode"),
                        f"{observation_id}.route_events[{index}].mode",
                    )

        authority_events = _validate_record_list(
            observation["authority_events"],
            f"{observation_id}.authority_events",
            ("event", "event_index"),
        )
        for index, event in enumerate(authority_events):
            label = f"{observation_id}.authority_events[{index}]"
            event_name = _require_string(event["event"], f"{label}.event")
            if event_name in {"authority-snapshot", "continuation"}:
                _require_string_list(
                    event.get("authorized_paths"), f"{label}.authorized_paths"
                )
                _require_string_list(
                    event.get("authorized_actions"), f"{label}.authorized_actions"
                )
            elif event_name == "protected-status":
                _require_string(event.get("status"), f"{label}.status")
                _require_string(event.get("user_authority"), f"{label}.user_authority")
                if not isinstance(event.get("authorizes_mutation"), bool):
                    raise _schema_error(f"{label}.authorizes_mutation must be boolean")
            elif event_name == "scope-delta":
                _require_string(event.get("path"), f"{label}.path")
                _require_string(event.get("action"), f"{label}.action")
                _require_string(event.get("outcome"), f"{label}.outcome")
                if not isinstance(event.get("accepted"), bool):
                    raise _schema_error(f"{label}.accepted must be boolean")

        _validate_communication_records(
            observation["communication_records"],
            f"{observation_id}.communication_records",
        )

        recovery_records = _validate_record_list(
            observation["recovery_records"],
            f"{observation_id}.recovery_records",
            RECOVERY_RECORD_FIELDS,
        )
        for index, recovery in enumerate(recovery_records):
            label = f"{observation_id}.recovery_records[{index}]"
            _require_string(recovery["record_id"], f"{label}.record_id")
            _require_event_index(recovery["event_index"], f"{label}.event_index")

            unit_lock = _require_mapping(recovery["unit_lock"], f"{label}.unit_lock")
            for field in ("subject", "mode", "decision_focus", "desired_artifact"):
                _require_string(unit_lock.get(field), f"{label}.unit_lock.{field}")
            if not isinstance(unit_lock.get("implementation_permission"), bool):
                raise _schema_error(
                    f"{label}.unit_lock.implementation_permission must be boolean"
                )

            capsule = _require_mapping(
                recovery["state_capsule"], f"{label}.state_capsule"
            )
            for field in ("subject", "mode", "decision_focus", "next_action"):
                _require_string(capsule.get(field), f"{label}.state_capsule.{field}")
            for field in (
                "terminal_decision_ids",
                "eligible_now_ids",
                "evidence_anchors",
            ):
                _require_string_list(
                    capsule.get(field), f"{label}.state_capsule.{field}"
                )
            blocked_later = _require_list(
                capsule.get("blocked_later"), f"{label}.state_capsule.blocked_later"
            )
            for blocked_index, blocked in enumerate(blocked_later):
                blocked_mapping = _require_mapping(
                    blocked, f"{label}.state_capsule.blocked_later[{blocked_index}]"
                )
                _require_string(
                    blocked_mapping.get("decision_id"),
                    f"{label}.state_capsule.blocked_later[{blocked_index}].decision_id",
                )
                _require_string_list(
                    blocked_mapping.get("prerequisites"),
                    f"{label}.state_capsule.blocked_later[{blocked_index}].prerequisites",
                )

            ledger = _validate_record_list(
                recovery["decision_ledger"],
                f"{label}.decision_ledger",
                RECOVERY_LEDGER_FIELDS,
            )
            for ledger_index, entry in enumerate(ledger):
                entry_label = f"{label}.decision_ledger[{ledger_index}]"
                for field in ("decision_id", "state", "basis", "reopen_condition"):
                    _require_string(entry[field], f"{entry_label}.{field}")
                _require_string_list(
                    entry["dependencies"], f"{entry_label}.dependencies"
                )

            authority = _require_mapping(
                recovery["authority_envelope"], f"{label}.authority_envelope"
            )
            for field in RECOVERY_AUTHORITY_FIELDS:
                _require_string_list(
                    authority.get(field), f"{label}.authority_envelope.{field}"
                )
            _validate_communication_records(
                [recovery["communication_projection"]],
                f"{label}.communication_projection",
            )

        provenance = _require_mapping(
            observation["provenance"], f"{observation_id}.provenance"
        )
        for field in (
            "kind",
            "source",
            "sanitized_perimeter",
            "baseline_id",
            "candidate_id",
        ):
            _require_string(
                provenance.get(field), f"{observation_id}.provenance.{field}"
            )
        if provenance["kind"] not in {"synthetic-test", "controlled-runtime"}:
            raise _schema_error(f"unsupported provenance kind: {provenance['kind']}")
        if "role" in provenance:
            role = _require_string(
                provenance["role"], f"{observation_id}.provenance.role"
            )
            if role not in {"baseline", "candidate"}:
                raise _schema_error(f"unsupported provenance role: {role}")
    return observations


def _event_index(event: Mapping[str, object]) -> float:
    return float(event["event_index"])


def _sorted_events(
    observation: Mapping[str, object], key: str
) -> list[Mapping[str, object]]:
    return sorted(observation[key], key=_event_index)  # type: ignore[arg-type]


def _status_at(
    decision_id: str,
    event_index: float,
    decisions: Mapping[str, Mapping[str, object]],
    transitions: list[Mapping[str, object]],
) -> str:
    status = "open"
    for event in transitions:
        if (
            event.get("event") != "decision-status"
            or event.get("decision_id") != decision_id
        ):
            continue
        if _event_index(event) <= event_index:
            status = str(event["to"])
    if status == "open" and decision_id in decisions:
        record_status = str(decisions[decision_id]["status"])
        if not any(
            event.get("event") == "decision-status"
            and event.get("decision_id") == decision_id
            for event in transitions
        ):
            status = record_status
    return status


def _final_status(
    decision_id: str,
    decision: Mapping[str, object],
    transitions: list[Mapping[str, object]],
) -> str:
    status_events = [
        event
        for event in transitions
        if event.get("event") == "decision-status"
        and event.get("decision_id") == decision_id
    ]
    return str(status_events[-1]["to"]) if status_events else str(decision["status"])


def _dependencies_open(
    decision: Mapping[str, object],
    question: Mapping[str, object],
    decisions: Mapping[str, Mapping[str, object]],
    transitions: list[Mapping[str, object]],
) -> bool:
    dependencies = list(decision["dependencies"]) + list(question["prerequisites"])
    question_index = _event_index(question)
    for dependency_id in dependencies:
        dependency = decisions.get(str(dependency_id))
        if dependency is None:
            return True
        if (
            _status_at(str(dependency_id), question_index, decisions, transitions)
            not in TERMINAL_STATES
        ):
            return True
    return False


def _evidence_supports_question(
    question: Mapping[str, object], evidence: Mapping[str, Mapping[str, object]]
) -> bool:
    question_index = _event_index(question)
    for evidence_id in question["evidence_ids"]:
        item = evidence.get(str(evidence_id))
        if (
            item is not None
            and item["class"] == "Facts"
            and item["strength"] in {"sufficient", "strong", "verified"}
            and _event_index(item) <= question_index
        ):
            return True
    return False


def _decision_has_support(
    decision: Mapping[str, object], evidence: Mapping[str, Mapping[str, object]]
) -> bool:
    return any(str(evidence_id) in evidence for evidence_id in decision["evidence_ids"])


def _record_self_attested_cases(
    observations: list[Mapping[str, object]], forbidden_fields: set[str]
) -> set[str]:
    return {
        str(observation["case_id"])
        for observation in observations
        if forbidden_fields.intersection(observation)
    }


def _behavioral_evidence(observations: list[Mapping[str, object]]) -> dict[str, object]:
    runtime = [
        observation
        for observation in observations
        if observation["kind"] == "controlled-runtime"
        or observation["provenance"]["kind"] == "controlled-runtime"
    ]
    if not runtime:
        return {
            "status": "unavailable",
            "controlled_runtime": "unavailable",
            "merge_ready": False,
            "case_ids": list(CASE_IDS),
            "limit": "records are synthetic-test observations, not controlled runtime evidence",
        }

    by_case: dict[str, dict[str, Mapping[str, object]]] = {}
    perimeters: set[str] = set()
    for observation in runtime:
        provenance = observation["provenance"]
        role = provenance.get("role")
        if role in {"baseline", "candidate"}:
            by_case.setdefault(str(observation["case_id"]), {})[str(role)] = observation
        perimeters.add(str(provenance["sanitized_perimeter"]))
    missing = [
        case_id
        for case_id in CASE_IDS
        if set(by_case.get(case_id, {})) != {"baseline", "candidate"}
    ]
    if len(perimeters) != 1 or missing:
        return {
            "status": "unavailable",
            "controlled_runtime": "unavailable",
            "merge_ready": False,
            "case_ids": sorted(set(missing or CASE_IDS)),
            "limit": "controlled runtime needs baseline and candidate observations on one sanitized perimeter",
        }
    return {
        "status": "observed",
        "controlled_runtime": "observed",
        "merge_ready": True,
        "case_ids": list(CASE_IDS),
        "limit": "controlled baseline and candidate observations share one sanitized perimeter",
    }


def _score_observation(
    observation: Mapping[str, object],
    manifest: Mapping[str, object],
    findings: dict[str, set[str]],
) -> None:
    case_id = str(observation["case_id"])
    decisions = {
        str(record["decision_id"]): record
        for record in observation["decision_records"]  # type: ignore[union-attr]
    }
    evidence = {
        str(record["evidence_id"]): record
        for record in observation["evidence_records"]  # type: ignore[union-attr]
    }
    transitions = _sorted_events(observation, "transition_events")
    questions = observation["question_records"]  # type: ignore[assignment]

    authority_events = _sorted_events(observation, "authority_events")
    authority_by_type = {str(event.get("event")): event for event in authority_events}
    required_authority_events = set(
        manifest["authority_workflow"]["required_event_types"]  # type: ignore[index]
    )
    required_authority_events.discard("scope-delta")
    if not required_authority_events.issubset(authority_by_type):
        findings["authority_envelope_violation_cases"].add(case_id)
    snapshot = authority_by_type.get("authority-snapshot")
    if snapshot is None:
        findings["authority_envelope_violation_cases"].add(case_id)
    else:
        for event in authority_events:
            if event.get("event") != "continuation":
                continue
            if event.get("authorized_paths") != snapshot.get(
                "authorized_paths"
            ) or event.get("authorized_actions") != snapshot.get("authorized_actions"):
                findings["authority_envelope_violation_cases"].add(case_id)
    protected_status = authority_by_type.get("protected-status")
    if (
        protected_status is None
        or protected_status.get("authorizes_mutation") is not False
    ):
        findings["protected_status_authority_violation_cases"].add(case_id)
    scope_delta = authority_by_type.get("scope-delta")
    expected_scope_outcome = manifest["authority_workflow"]["scope_delta_outcome"]  # type: ignore[index]
    if (
        scope_delta is None
        or scope_delta.get("outcome") != expected_scope_outcome
        or scope_delta.get("accepted") is not False
    ):
        findings["scope_delta_violation_cases"].add(case_id)

    recovery_records = observation["recovery_records"]  # type: ignore[assignment]
    communication_records = [
        record
        for record in observation["communication_records"]  # type: ignore[union-attr]
        if record.get("kind") == manifest["communication_workflow"]["candidate_kind"]  # type: ignore[index]
    ]
    if len(recovery_records) != 1:  # type: ignore[arg-type]
        findings["canonical_recovery_violation_cases"].add(case_id)
    else:
        recovery = recovery_records[0]  # type: ignore[index]
        unit_lock = recovery["unit_lock"]
        capsule = recovery["state_capsule"]
        if (
            unit_lock.get("subject") != capsule.get("subject")
            or unit_lock.get("mode") != capsule.get("mode")
            or unit_lock.get("decision_focus") != capsule.get("decision_focus")
        ):
            findings["canonical_recovery_violation_cases"].add(case_id)

        expected_terminal_ids = {
            decision_id
            for decision_id, decision in decisions.items()
            if _final_status(decision_id, decision, transitions) in TERMINAL_STATES
        }
        ledger = recovery["decision_ledger"]
        ledger_by_id = {
            str(entry.get("decision_id")): entry
            for entry in ledger  # type: ignore[union-attr]
        }
        if set(ledger_by_id) != set(decisions):
            findings["canonical_recovery_violation_cases"].add(case_id)
        else:
            for decision_id, decision in decisions.items():
                entry = ledger_by_id[decision_id]
                if (
                    entry.get("state")
                    != _final_status(decision_id, decision, transitions)
                    or entry.get("dependencies") != decision.get("dependencies")
                    or entry.get("reopen_condition") != decision.get("reopen_condition")
                ):
                    findings["canonical_recovery_violation_cases"].add(case_id)
        if set(capsule.get("terminal_decision_ids", [])) != expected_terminal_ids:
            findings["canonical_recovery_violation_cases"].add(case_id)

        recovery_authority = recovery["authority_envelope"]
        if snapshot is None or (
            recovery_authority.get("authorized_paths")
            != snapshot.get("authorized_paths")
            or recovery_authority.get("authorized_actions")
            != snapshot.get("authorized_actions")
        ):
            findings["canonical_recovery_violation_cases"].add(case_id)
        if (
            len(communication_records) != 1
            or recovery["communication_projection"] != communication_records[0]
        ):
            findings["canonical_recovery_violation_cases"].add(case_id)

    communication_workflow = manifest["communication_workflow"]  # type: ignore[index]
    if len(communication_records) != 1:
        findings["canonical_view_violation_cases"].add(case_id)
    for record in communication_records:
        if not (
            record.get("material_delta_ids")
            and record.get("outcome")
            and record.get("controlling_evidence_ids")
            and len(record["controlling_evidence_ids"])
            <= communication_workflow["max_controlling_evidence"]
            and record.get("principal_risk_id")
            and record.get("active_choice")
            and record.get("acceptance_condition_ids")
            and record.get("word_count_mode")
            == communication_workflow["word_count_mode"]
        ):
            findings["canonical_view_violation_cases"].add(case_id)
        diagrams = record.get("diagrams", [])
        if len(diagrams) > communication_workflow["max_diagrams"]:
            findings["visual_budget_violation_cases"].add(case_id)
        for diagram in diagrams:
            if (
                diagram.get("relationship_count", 0)
                < communication_workflow["diagram_min_relationships"]
                or diagram.get("useful") is not True
                or diagram.get("conclusion_adjacent") is not True
            ):
                findings["visual_budget_violation_cases"].add(case_id)

    protected = manifest["protected_workflow"]  # type: ignore[index]
    if case_id == "C-05":
        lifecycle = manifest["lifecycle_workflow"]  # type: ignore[index]
        artifact_events = _sorted_events(observation, "artifact_events")
        candidate = next(
            (
                event
                for event in artifact_events
                if event.get("event") == "candidate-presented"
            ),
            None,
        )
        menus = [
            event for event in transitions if event.get("event") == "candidate-menu"
        ]
        menu = menus[0] if menus else None
        promotion_menu = next(
            (
                event
                for event in menus
                if event.get("options") == lifecycle["candidate_menu"]
                and event.get("phase") == "post-review"
            ),
            None,
        )
        critical_review = next(
            (
                event
                for event in transitions
                if event.get("event") == lifecycle["critical_review_event"]
            ),
            None,
        )
        critical_finding = next(
            (
                event
                for event in transitions
                if event.get("event") == lifecycle["critical_finding_event"]
            ),
            None,
        )
        realignment = next(
            (
                event
                for event in transitions
                if event.get("event") == lifecycle["realignment_event"]
            ),
            None,
        )
        disposition_events = [
            event
            for event in transitions
            if event.get("event") == lifecycle["disposition_event"]
        ]
        disposition = disposition_events[-1] if disposition_events else None

        gate_events = [event for event in transitions if "gate" in event]
        observed_gates = {str(event.get("gate")) for event in gate_events}
        expected_gates = set(lifecycle["global_gates"])
        if observed_gates != expected_gates or any(
            event.get("gate") not in expected_gates for event in gate_events
        ):
            findings["gate_type_violation_cases"].add(case_id)

        grill_events = [
            event
            for event in gate_events
            if event.get("gate") == lifecycle["post_setup_gate"]
        ]
        post_setup = next(
            (
                event
                for event in grill_events
                if event.get("phase") == "post-setup"
                and event.get("route_owner") == "/grill-me"
            ),
            None,
        )
        covered_question_ids = {
            str(question_id)
            for event in grill_events
            for question_id in event.get("question_ids", [])
        }
        question_ids = {str(question["question_id"]) for question in questions}
        if (
            post_setup is None
            or not question_ids.issubset(covered_question_ids)
            or any(
                not any(
                    route.get("owner") == "/grill-me"
                    and _event_index(route) <= _event_index(question)
                    for route in observation["route_events"]  # type: ignore[union-attr]
                )
                for question in questions
            )
        ):
            findings["grill_me_routing_violation_cases"].add(case_id)
        for event in grill_events:
            if event.get("repeat") is True:
                eligible_ids = set(
                    str(item) for item in event.get("eligible_decision_ids", [])
                )
                question_decision_ids = {
                    str(question["decision_id"])
                    for question in questions
                    if str(question["question_id"])
                    in set(str(item) for item in event.get("question_ids", []))
                }
                if not eligible_ids or eligible_ids != question_decision_ids:
                    findings["grill_me_routing_violation_cases"].add(case_id)

        critical_review = next(
            (
                event
                for event in transitions
                if event.get("event") == lifecycle["critical_review_event"]
            ),
            None,
        )
        review_valid = False
        if critical_review is not None:
            lenses = critical_review.get("lenses")
            expected_lenses = list(lifecycle["review_lenses"])
            lens_names = (
                [str(lens.get("name")) for lens in lenses if isinstance(lens, Mapping)]
                if isinstance(lenses, list)
                else []
            )
            lateral_types = (
                {
                    str(lens.get("type"))
                    for lens in lenses
                    if isinstance(lens, Mapping) and lens.get("name") == "lateral"
                }
                if isinstance(lenses, list)
                else set()
            )
            finding_events = [
                event
                for event in transitions
                if event.get("event") == lifecycle["critical_finding_event"]
            ]
            finding_ids = {
                str(finding_id)
                for event in finding_events
                for finding_id in event.get("finding_ids", [])
            }
            finding_records = [
                record
                for event in finding_events
                for record in event.get("findings", [])
                if isinstance(record, Mapping)
            ]
            classified_ids = {
                str(record.get("finding_id"))
                for record in finding_records
                if record.get("classification") in lifecycle["finding_classifications"]
            }
            review_valid = (
                critical_review.get("gate") == "CRITICAL REVIEW"
                and critical_review.get("explicit") is True
                and critical_review.get("completed") is True
                and isinstance(lenses, list)
                and len(lenses) >= 3
                and lens_names[:3] == expected_lenses
                and bool(lateral_types)
                and lateral_types.issubset(set(lifecycle["lateral_lens_types"]))
                and isinstance(critical_review.get("conclusion"), str)
                and bool(str(critical_review.get("conclusion")).strip())
                and classified_ids == finding_ids
            )
        if not review_valid:
            findings["critical_review_completion_violation_cases"].add(case_id)

        overrides = [
            event
            for event in transitions
            if event.get("event") == lifecycle["gate_override_event"]
        ]
        for override in overrides:
            overridden_gate = override.get("gate")
            named_action = override.get("named_action")
            preserved_gates = set(
                str(item) for item in override.get("preserved_gates", [])
            )
            if (
                override.get("explicit") is not True
                or overridden_gate not in expected_gates
                or not isinstance(named_action, str)
                or not named_action.strip()
                or override.get("action") != named_action
                or override.get("risk_disposition") != "accepted-risk"
                or preserved_gates != expected_gates - {str(overridden_gate)}
            ):
                findings["gate_override_violation_cases"].add(case_id)

        expected_menu = list(lifecycle["candidate_menu"])
        if any(
            menu_item.get("options") != expected_menu
            or set(menu_item.get("locks", {})) != set(expected_menu)
            or any(
                not isinstance(menu_item.get("locks", {}).get(option), Mapping)
                or (
                    menu_item["locks"][option].get("locked") is True
                    and not str(menu_item["locks"][option].get("reason", "")).strip()
                )
                for option in expected_menu
            )
            for menu_item in menus
        ):
            findings["menu_projection_violation_cases"].add(case_id)

        saves = [
            event for event in artifact_events if event.get("event") == "artifact-saved"
        ]
        if (
            len(saves) != 1
            or critical_review is None
            or saves[0].get("critical_review") != "pending"
            or _event_index(saves[0]) >= _event_index(critical_review)
            or saves[0].get("promotes") is not False
            or saves[0].get("checkpoint") is not True
            or saves[0].get("closes_findings") is not False
            or saves[0].get("authorizes") != []
        ):
            findings["provisional_save_violation_cases"].add(case_id)

        finding_ids = [
            str(finding_id)
            for event in transitions
            if event.get("event") == lifecycle["critical_finding_event"]
            for finding_id in event.get("finding_ids", [])
        ]
        if (
            menu is None
            or candidate is None
            or critical_review is None
            or critical_review.get("explicit") is not True
            or _event_index(critical_review) <= _event_index(candidate)
            or promotion_menu is None
            or promotion_menu.get("phase") != "post-review"
            or promotion_menu.get("critical_review_complete") is not True
            or promotion_menu.get("dispositions_complete") is not True
            or _event_index(promotion_menu) <= _event_index(critical_review)
        ):
            findings["lifecycle_order_violation_cases"].add(case_id)
        if any(
            set(lifecycle["promotion_options"]).issubset(
                set(menu_item.get("options", []))
            )
            and (
                critical_review is None
                or _event_index(menu_item) <= _event_index(critical_review)
                or disposition is None
                or _event_index(menu_item) <= _event_index(disposition)
            )
            and not all(
                isinstance(menu_item.get("locks", {}).get(option), Mapping)
                and menu_item["locks"][option].get("locked") is True
                for option in lifecycle["promotion_options"]
            )
            for menu_item in menus
        ):
            findings["lifecycle_order_violation_cases"].add(case_id)
        if menu is not None and menu.get("findings_present") is True:
            if (
                critical_finding is None
                or realignment is None
                or realignment.get("explicit") is not True
                or _event_index(realignment) <= _event_index(critical_finding)
            ):
                findings["lifecycle_order_violation_cases"].add(case_id)
        if finding_ids:
            dispositions = disposition.get("dispositions") if disposition else None
            if (
                disposition is None
                or disposition.get("explicit") is not True
                or disposition.get("finding_ids") != finding_ids
                or not isinstance(dispositions, Mapping)
                or set(dispositions) != set(finding_ids)
                or any(
                    dispositions.get(finding_id)
                    not in lifecycle["allowed_dispositions"]
                    for finding_id in finding_ids
                )
                or realignment is None
                or _event_index(disposition) <= _event_index(realignment)
            ):
                findings["critical_disposition_violation_cases"].add(case_id)

    question_owner_events = [
        event
        for event in observation["route_events"]  # type: ignore[union-attr]
        if event.get("owner") == "/grill-me"
    ]
    known_batches: dict[float, set[tuple[str, float]]] = {}
    for question in questions:  # type: ignore[union-attr]
        if _evidence_supports_question(question, evidence):
            findings["recoverable_fact_question_cases"].add(case_id)
        decision = decisions.get(str(question["decision_id"]))
        if decision is None or not decision["material"]:
            findings["unmapped_question_cases"].add(case_id)
            continue
        dependencies_open = _dependencies_open(
            decision, question, decisions, transitions
        )
        if dependencies_open:
            findings["premature_dependent_question_cases"].add(case_id)
        question_index = _event_index(question)
        status = _status_at(
            str(question["decision_id"]), question_index, decisions, transitions
        )
        if status in TERMINAL_STATES or status == "blocked-later":
            findings["unmapped_question_cases"].add(case_id)
        if not any(
            _event_index(event) <= question_index for event in question_owner_events
        ):
            findings["protected_workflow_violation_cases"].add(case_id)
        if not dependencies_open and status not in TERMINAL_STATES:
            eligible_index = float(question["eligible_event_index"])
            known_batches.setdefault(eligible_index, set()).add(
                (str(question["block_id"]), question_index)
            )

    if any(len(blocks) > 1 for blocks in known_batches.values()):
        findings["split_known_question_batch_cases"].add(case_id)

    for decision_id, decision in decisions.items():
        dependencies = decision["dependencies"]
        is_root = decision.get("kind", "root") == "root" or not dependencies
        if decision["material"] and is_root:
            if _final_status(decision_id, decision, transitions) not in TERMINAL_STATES:
                findings["uncovered_material_root_cases"].add(case_id)

    reopen_events = [
        event for event in transitions if event.get("event") == "decision-reopened"
    ]
    for event in reopen_events:
        decision_id = str(event.get("decision_id", ""))
        decision = decisions.get(decision_id)
        trigger = event.get("trigger")
        evidence_ids = event.get("evidence_ids", [])
        condition = decision.get("reopen_condition") if decision else None
        evidence_present = bool(evidence_ids) and all(
            str(item) in evidence for item in evidence_ids
        )
        if (
            decision is None
            or trigger not in REOPEN_TRIGGERS
            or not isinstance(condition, str)
            or trigger != condition
            or (
                trigger in {"new-evidence", "critical-finding"} and not evidence_present
            )
        ):
            findings["unjustified_reopen_cases"].add(case_id)

    status_events_by_decision: dict[str, list[Mapping[str, object]]] = {}
    for event in transitions:
        if event.get("event") == "decision-status":
            status_events_by_decision.setdefault(
                str(event.get("decision_id")), []
            ).append(event)
    for decision_id, status_events in status_events_by_decision.items():
        rejected_index: float | None = None
        for status_event in status_events:
            status_event_index = _event_index(status_event)
            if status_event.get("to") == "rejected":
                rejected_index = status_event_index
            elif rejected_index is not None and status_event.get("to") != "rejected":
                reopened = any(
                    candidate.get("event") == "decision-reopened"
                    and candidate.get("decision_id") == decision_id
                    and rejected_index < _event_index(candidate) <= status_event_index
                    for candidate in transitions
                )
                if not reopened:
                    findings["rejected_reappearance_cases"].add(case_id)
                rejected_index = None

    if case_id == "C-03":
        challenge_events = [
            event for event in transitions if event.get("event") == "internal-challenge"
        ]
        valid_challenge = any(
            event.get("dimension")
            in {
                "actor",
                "mechanism",
                "constraint",
                "causal-assumption",
                "causal_assumption",
            }
            and event.get("changed_from") != event.get("changed_to")
            and bool(event.get("evidence_ids"))
            for event in challenge_events
        )
        if not valid_challenge:
            findings["anchored_challenge_violation_cases"].add(case_id)
        for event in challenge_events:
            alternatives = event.get("visible_alternatives", [])
            if not alternatives:
                continue
            credible_count = event.get("credible_mechanism_count", 0)
            supported = all(
                str(alternative) in decisions
                and decisions[str(alternative)].get("kind") == "alternative"
                and _decision_has_support(decisions[str(alternative)], evidence)
                for alternative in alternatives
            )
            if (
                not isinstance(credible_count, int)
                or credible_count < 2
                or len(alternatives) < 2
                or not supported
            ):
                findings["visible_alternative_violation_cases"].add(case_id)

    requirements = manifest["case_requirements"][case_id]  # type: ignore[index]
    if requirements.get("requires_material_unknown_question"):
        has_unknown_question = any(
            any(
                str(evidence_id) in evidence
                and evidence[str(evidence_id)]["class"] == "Unknowns"
                for evidence_id in question["evidence_ids"]
            )
            and str(question["decision_id"]) in decisions
            and decisions[str(question["decision_id"])]["material"]
            for question in questions  # type: ignore[union-attr]
        )
        if not has_unknown_question:
            findings["protected_workflow_violation_cases"].add(case_id)

    if case_id == "C-04":
        required_boundaries = requirements.get("requires_capsule_boundaries", [])
        capsule_events = [
            event for event in transitions if event.get("event") == "capsule-written"
        ]
        by_boundary = {str(event.get("boundary")): event for event in capsule_events}
        for boundary in required_boundaries:
            event = by_boundary.get(str(boundary))
            capsule = event.get("capsule") if event else None
            if (
                event is None
                or not isinstance(capsule, Mapping)
                or any(field not in capsule for field in CAPSULE_FIELDS)
            ):
                findings["state_continuity_violation_cases"].add(case_id)
                continue
            for field in (
                "accepted_ids",
                "rejected_ids",
                "deferred_ids",
                "accepted_risk_ids",
                "eligible_now_ids",
                "blocked_later",
                "evidence_anchors",
            ):
                if not isinstance(capsule[field], list):
                    findings["state_continuity_violation_cases"].add(case_id)
        for route in observation["route_events"]:  # type: ignore[union-attr]
            if route.get("event") not in {"subject-change", "mode-change"}:
                continue
            boundary_event = by_boundary.get(str(route["event"]))
            capsule = boundary_event.get("capsule") if boundary_event else None
            if (
                not isinstance(capsule, Mapping)
                or capsule.get("subject") != route.get("subject")
                or capsule.get("mode") != route.get("mode")
            ):
                findings["state_continuity_violation_cases"].add(case_id)

    forbidden_routes = set(manifest["analysis_only_forbidden_routes"])  # type: ignore[arg-type]
    invocations = [
        route
        for route in observation["route_events"]  # type: ignore[union-attr]
        if route.get("event") == "invocation"
    ]
    if len(invocations) != 1 or any(
        invocation.get("owner") != "/internal-gateway-idea"
        or invocation.get("mode") != "analysis-only"
        or invocation.get("explicit") is not True
        for invocation in invocations
    ):
        findings["route_projection_violation_cases"].add(case_id)
    if not any(invocation.get("explicit") is True for invocation in invocations):
        findings["protected_workflow_violation_cases"].add(case_id)
    if any(
        route.get("mode") == "analysis-only" and route.get("owner") in forbidden_routes
        for route in observation["route_events"]  # type: ignore[union-attr]
    ):
        findings["analysis_only_routing_violation_cases"].add(case_id)

    if case_id == "C-05":
        artifacts = _sorted_events(observation, "artifact_events")
        candidate = next(
            (
                event
                for event in artifacts
                if event.get("event") == "candidate-presented"
            ),
            None,
        )
        accepted = next(
            (
                event
                for event in artifacts
                if event.get("event") == "candidate-accepted"
            ),
            None,
        )
        choices = [
            event for event in artifacts if event.get("event") == "critical-choice"
        ]
        integrations = [
            event
            for event in artifacts
            if event.get("event") == "critical-findings-integrated"
        ]
        saves = [event for event in artifacts if event.get("event") == "artifact-saved"]
        replays = [
            event for event in artifacts if event.get("event") == "planning-replay"
        ]
        explicit_choice = next(
            (event for event in choices if event.get("explicit") is True), None
        )
        if (
            requirements.get("requires_explicit_critical_choice")
            and explicit_choice is None
        ):
            findings["critical_choice_violation_cases"].add(case_id)
        if integrations and (
            explicit_choice is None
            or _event_index(explicit_choice) > _event_index(integrations[0])
        ):
            findings["critical_choice_violation_cases"].add(case_id)
        if integrations and (
            disposition is None
            or disposition.get("explicit") is not True
            or _event_index(disposition) >= _event_index(integrations[0])
            or not isinstance(disposition.get("dispositions"), Mapping)
            or any(
                value != "integrate"
                for value in disposition["dispositions"].values()  # type: ignore[union-attr]
            )
        ):
            findings["critical_disposition_violation_cases"].add(case_id)
        if len(saves) > 1:
            findings["multiple_saved_artifact_cases"].add(case_id)
        if protected["save_is_non_promoting"] and any(
            save.get("promotes") is not False or save.get("checkpoint") is not True
            for save in saves
        ):
            findings["save_semantics_violation_cases"].add(case_id)
        if (
            len(saves) != 1
            or not replays
            or any(replay.get("uses_transcript") is not False for replay in replays)
        ):
            findings["artifact_replay_violation_cases"].add(case_id)
        if (
            candidate is None
            or accepted is None
            or accepted.get("explicit") is not True
            or _event_index(accepted) <= _event_index(candidate)
        ):
            findings["lifecycle_order_violation_cases"].add(case_id)
        if replays and saves and _event_index(replays[0]) <= _event_index(saves[0]):
            findings["lifecycle_order_violation_cases"].add(case_id)

        if accepted is not None and accepted.get("choice") == "+spec":
            spec_artifact = next(
                (
                    event
                    for event in artifacts
                    if event.get("event") == "spec-authored"
                    and event.get("artifact_id") == accepted.get("artifact_id")
                ),
                None,
            )
            plan_handoffs = [
                event
                for event in observation["route_events"]  # type: ignore[union-attr]
                if event.get("event") == "plan-authoring-handoff"
                and event.get("trigger") == "+spec"
            ]
            readiness_field = str(lifecycle["spec_artifact_readiness_field"])
            if (
                spec_artifact is None
                or spec_artifact.get(readiness_field) is not True
                or _event_index(spec_artifact) <= _event_index(accepted)
                or plan_handoffs
            ):
                findings["spec_plan_readiness_violation_cases"].add(case_id)

    protected = manifest["protected_workflow"]  # type: ignore[index]
    for field in ("question_cap", "max_questions", "fixed_question_cap"):
        if field in observation:
            findings["protected_workflow_violation_cases"].add(case_id)
    for event in observation["route_events"]:  # type: ignore[union-attr]
        if event.get("event") == "invocation" and event.get("explicit") is not True:
            findings["protected_workflow_violation_cases"].add(case_id)
    for event in observation["artifact_events"]:  # type: ignore[union-attr]
        if event.get("event") == "critical-findings-integrated" and not any(
            choice.get("explicit") is True
            and _event_index(choice) < _event_index(event)
            for choice in observation["artifact_events"]  # type: ignore[union-attr]
            if choice.get("event") == "critical-choice"
        ):
            findings["critical_choice_violation_cases"].add(case_id)


def score(manifest: dict[str, object], run: dict[str, object]) -> dict[str, object]:
    """Return a structural score derived from sanitized records."""

    validated_manifest = _validate_manifest(manifest)
    observations = _validate_run(validated_manifest, run)
    present_cases = {str(observation["case_id"]) for observation in observations}
    findings: dict[str, set[str]] = {field: set() for field in FINDING_FIELDS}
    forbidden_fields = set(validated_manifest["forbidden_verdict_fields"])  # type: ignore[arg-type]
    self_attested = _record_self_attested_cases(observations, forbidden_fields)
    findings["self_attested_verdict_cases"].update(self_attested)

    all_evidence_classes = {
        str(item["class"])
        for observation in observations
        for item in observation["evidence_records"]  # type: ignore[union-attr]
    }
    if all_evidence_classes != EVIDENCE_CLASSES:
        findings["protected_workflow_violation_cases"].update(present_cases)

    for observation in observations:
        _score_observation(observation, validated_manifest, findings)

    total_saves = sum(
        1
        for observation in observations
        for event in observation["artifact_events"]  # type: ignore[union-attr]
        if event.get("event") == "artifact-saved"
    )
    protected = validated_manifest["protected_workflow"]
    if total_saves > protected["max_saved_artifacts"]:  # type: ignore[operator]
        findings["protected_workflow_violation_cases"].update(present_cases)

    missing_case_ids = sorted(set(CASE_IDS) - present_cases)
    result: dict[str, object] = {
        "missing_case_ids": missing_case_ids,
        **{field: sorted(cases) for field, cases in findings.items()},
    }
    result["findings"] = [
        {"code": field, "cases": result[field]}
        for field in sorted(FINDING_FIELDS)
        if result[field]
    ]
    result["behavioral_evidence"] = _behavioral_evidence(observations)
    result["accepted"] = not missing_case_ids and not any(findings.values())
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = _load_json(args.manifest)
        run = _load_json(args.run)
        result = score(manifest, run)  # type: ignore[arg-type]
    except (OSError, TypeError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
