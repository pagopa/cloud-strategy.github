#!/usr/bin/env python3
"""Score sanitized observations of the direct execute-plans loop."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NoReturn

CONTRACT_VERSION = "internal-gateway-execute-plans-eval-v1"
SHA256_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
CASE_FIELDS = {
    "case_id",
    "status",
    "plan_reference_matches",
    "approval_fingerprint",
    "state_approval_fingerprint",
    "manifest_task_ids",
    "completed_task_ids",
    "remaining_task_ids",
    "dispatch_events",
    "edits",
    "validation_events",
    "repairs",
    "omission_detected",
    "omission_clearly_implied",
    "omission_repaired",
    "omission_repair_in_target",
    "retry_attempts",
    "failure_signatures",
    "progress_signatures",
    "recovery_attempted",
    "independent_tasks_continued",
    "native_equivalent_admissible",
    "validation_weakened",
    "blocked_reason_evidence",
    "authority_required",
    "pre_existing_failures",
    "independent_tasks_executable",
    "residual_failures",
    "last_validation",
    "next_action",
    "next_action_count",
    "bootstrap",
    "delivery_verdicts",
    "report_lines",
}
MANIFEST_FIELDS = {
    "contract_version",
    "required_case_ids",
    "allowed_statuses",
    "forbidden_dispatch_events",
    "report_labels",
    "observable_evidence",
    "bootstrap_fields",
    "bootstrap_statuses",
    "delivery_verdict_fields",
    "delivery_verdict_categories",
    "pre_existing_case",
    "authority_case",
}
RUN_FIELDS = {"contract_version", "observations"}
EDIT_FIELDS = {"path", "in_target"}
VALIDATION_FIELDS = {"id", "outcome", "repair_id"}
REPAIR_FIELDS = {"id", "safe", "in_target", "distinct"}
BOOTSTRAP_FIELDS = {"check", "status", "next_action"}
DELIVERY_VERDICT_FIELDS = {"category", "outcome", "coverage", "limit"}
BLOCKED_REASON_FIELDS = {
    "attempted_recovery",
    "no_progress",
    "inadmissible_alternative",
    "unblock_action",
}


def _schema_error(message: str) -> NoReturn:
    raise ValueError(message)


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _schema_error(f"{label} must be a JSON object")
    return value


def _exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        _schema_error(
            f"{label} fields must be exactly {sorted(expected)}; got {sorted(actual)}"
        )


def _strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        _schema_error(f"{label} must be an array of non-empty strings")
    return value


def _unique_strings(value: object, label: str) -> list[str]:
    values = _strings(value, label)
    if len(values) != len(set(values)):
        _schema_error(f"{label} must contain unique values")
    return values


def _validate_manifest(value: object) -> dict[str, Any]:
    manifest = _mapping(value, "manifest")
    _exact_fields(manifest, MANIFEST_FIELDS, "manifest")
    if manifest["contract_version"] != CONTRACT_VERSION:
        _schema_error(f"manifest contract_version must be {CONTRACT_VERSION}")
    required_case_ids = _unique_strings(
        manifest["required_case_ids"], "manifest required_case_ids"
    )
    if len(required_case_ids) != 5:
        _schema_error("manifest required_case_ids must contain exactly five branches")
    allowed_statuses = _unique_strings(
        manifest["allowed_statuses"], "manifest allowed_statuses"
    )
    if allowed_statuses != ["DONE", "PARTIAL", "BLOCKED"]:
        _schema_error("manifest allowed_statuses must be DONE, PARTIAL, BLOCKED")
    forbidden_events = _unique_strings(
        manifest["forbidden_dispatch_events"],
        "manifest forbidden_dispatch_events",
    )
    if not forbidden_events:
        _schema_error("manifest forbidden_dispatch_events must not be empty")
    report_labels = _unique_strings(manifest["report_labels"], "manifest report_labels")
    if report_labels != ["Plan", "Changed", "Checks", "Next"]:
        _schema_error("manifest report_labels must be Plan, Changed, Checks, Next")
    observable_evidence = _unique_strings(
        manifest["observable_evidence"], "manifest observable_evidence"
    )
    if observable_evidence != [
        "order",
        "semantic-approval",
        "scope",
        "invalidation",
        "recovery",
        "residuals",
    ]:
        _schema_error("manifest observable_evidence has an unsupported contract")
    if manifest["bootstrap_fields"] != ["check", "status", "next_action"]:
        _schema_error("manifest bootstrap_fields has an unsupported contract")
    if manifest["bootstrap_statuses"] != ["PASS", "BLOCKED"]:
        _schema_error("manifest bootstrap_statuses must be PASS, BLOCKED")
    if manifest["delivery_verdict_fields"] != [
        "category",
        "outcome",
        "coverage",
        "limit",
    ]:
        _schema_error("manifest delivery_verdict_fields has an unsupported contract")
    if manifest["delivery_verdict_categories"] != [
        "structure",
        "semantic_review",
        "artifact_provenance",
        "source_baseline",
        "execution_readiness",
    ]:
        _schema_error(
            "manifest delivery_verdict_categories has an unsupported contract"
        )
    for field in ("pre_existing_case", "authority_case"):
        if manifest[field] not in required_case_ids:
            _schema_error(f"manifest {field} must name a required case")
    return manifest


def _validate_edits(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _schema_error(f"{label} must be an array")
    edits: list[dict[str, Any]] = []
    for index, raw_edit in enumerate(value):
        edit = _mapping(raw_edit, f"{label}[{index}]")
        _exact_fields(edit, EDIT_FIELDS, f"{label}[{index}]")
        if not isinstance(edit["path"], str) or not edit["path"].strip():
            _schema_error(f"{label}[{index}].path must be a non-empty string")
        if not isinstance(edit["in_target"], bool):
            _schema_error(f"{label}[{index}].in_target must be boolean")
        edits.append(edit)
    return edits


def _validate_validation_events(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _schema_error(f"{label} must be an array")
    events: list[dict[str, Any]] = []
    for index, raw_event in enumerate(value):
        event = _mapping(raw_event, f"{label}[{index}]")
        _exact_fields(event, VALIDATION_FIELDS, f"{label}[{index}]")
        if not isinstance(event["id"], str) or not event["id"].strip():
            _schema_error(f"{label}[{index}].id must be a non-empty string")
        if event["outcome"] not in {"failed", "passed"}:
            _schema_error(f"{label}[{index}].outcome must be failed or passed")
        if event["repair_id"] is not None and not isinstance(event["repair_id"], str):
            _schema_error(f"{label}[{index}].repair_id must be string or null")
        events.append(event)
    return events


def _validate_repairs(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _schema_error(f"{label} must be an array")
    repairs: list[dict[str, Any]] = []
    for index, raw_repair in enumerate(value):
        repair = _mapping(raw_repair, f"{label}[{index}]")
        _exact_fields(repair, REPAIR_FIELDS, f"{label}[{index}]")
        if not isinstance(repair["id"], str) or not repair["id"].strip():
            _schema_error(f"{label}[{index}].id must be a non-empty string")
        for field in ("safe", "in_target", "distinct"):
            if not isinstance(repair[field], bool):
                _schema_error(f"{label}[{index}].{field} must be boolean")
        repairs.append(repair)
    return repairs


def _validate_blocked_reason(value: object, label: str) -> dict[str, Any]:
    reason = _mapping(value, label)
    _exact_fields(reason, BLOCKED_REASON_FIELDS, label)
    for field in (
        "attempted_recovery",
        "no_progress",
        "inadmissible_alternative",
    ):
        if not isinstance(reason[field], bool):
            _schema_error(f"{label}.{field} must be boolean")
    if (
        not isinstance(reason["unblock_action"], str)
        or not reason["unblock_action"].strip()
    ):
        _schema_error(f"{label}.unblock_action must be a non-empty string")
    return reason


def _validate_bootstrap(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _schema_error(f"{label} must be a non-empty array")
    observations: list[dict[str, Any]] = []
    for index, raw_observation in enumerate(value):
        observation = _mapping(raw_observation, f"{label}[{index}]")
        _exact_fields(observation, BOOTSTRAP_FIELDS, f"{label}[{index}]")
        for field in ("check", "next_action"):
            if (
                not isinstance(observation[field], str)
                or not observation[field].strip()
            ):
                _schema_error(f"{label}[{index}].{field} must be a non-empty string")
        if observation["status"] not in {"PASS", "BLOCKED"}:
            _schema_error(f"{label}[{index}].status must be PASS or BLOCKED")
        if observation["status"] == "BLOCKED" and observation[
            "next_action"
        ].strip().lower() in {
            "none",
            "no action",
            "n/a",
        }:
            _schema_error(f"{label}[{index}].next_action must be concrete when blocked")
        observations.append(observation)
    return observations


def _validate_delivery_verdicts(
    value: object, label: str, categories: list[str]
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _schema_error(f"{label} must be an array")
    verdicts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw_verdict in enumerate(value):
        verdict = _mapping(raw_verdict, f"{label}[{index}]")
        _exact_fields(verdict, DELIVERY_VERDICT_FIELDS, f"{label}[{index}]")
        if verdict["category"] not in categories or verdict["category"] in seen:
            _schema_error(f"{label} must contain each delivery category exactly once")
        if verdict["outcome"] not in {"passed", "failed", "inconclusive"}:
            _schema_error(f"{label}[{index}].outcome is invalid")
        for field in ("coverage", "limit"):
            if not isinstance(verdict[field], str) or not verdict[field].strip():
                _schema_error(f"{label}[{index}].{field} must be a non-empty string")
        seen.add(verdict["category"])
        verdicts.append(verdict)
    if seen != set(categories):
        _schema_error(f"{label} must contain all five delivery categories")
    return verdicts


def _validate_observation(
    value: object, index: int, manifest: dict[str, Any]
) -> dict[str, Any]:
    label = f"observation {index}"
    observation = _mapping(value, label)
    _exact_fields(observation, CASE_FIELDS, label)
    for field in (
        "case_id",
        "status",
        "approval_fingerprint",
        "state_approval_fingerprint",
        "last_validation",
        "next_action",
    ):
        if not isinstance(observation[field], str) or not observation[field].strip():
            _schema_error(f"{label}.{field} must be a non-empty string")
    if not isinstance(observation["plan_reference_matches"], bool):
        _schema_error(f"{label}.plan_reference_matches must be boolean")
    for field in (
        "manifest_task_ids",
        "completed_task_ids",
        "remaining_task_ids",
        "dispatch_events",
        "pre_existing_failures",
        "residual_failures",
        "failure_signatures",
        "progress_signatures",
        "report_lines",
    ):
        _strings(observation[field], f"{label}.{field}")
    for field in (
        "omission_detected",
        "omission_clearly_implied",
        "omission_repaired",
        "omission_repair_in_target",
        "authority_required",
        "independent_tasks_executable",
        "recovery_attempted",
        "independent_tasks_continued",
        "native_equivalent_admissible",
        "validation_weakened",
    ):
        if not isinstance(observation[field], bool):
            _schema_error(f"{label}.{field} must be boolean")
    if not isinstance(observation["next_action_count"], int) or isinstance(
        observation["next_action_count"], bool
    ):
        _schema_error(f"{label}.next_action_count must be an integer")
    for field in ("approval_fingerprint", "state_approval_fingerprint"):
        if not SHA256_RE.fullmatch(observation[field]):
            _schema_error(f"{label}.{field} must be a SHA-256 fingerprint")
    retry_attempts = observation["retry_attempts"]
    if not isinstance(retry_attempts, dict):
        _schema_error(f"{label}.retry_attempts must be an object")
    for task_id, attempts in retry_attempts.items():
        if not isinstance(task_id, str) or not task_id.strip():
            _schema_error(f"{label}.retry_attempts keys must be non-empty strings")
        if (
            not isinstance(attempts, int)
            or isinstance(attempts, bool)
            or not 0 <= attempts <= 5
        ):
            _schema_error(
                f"{label}.retry_attempts values must be integers from 0 through 5"
            )
    _validate_blocked_reason(
        observation["blocked_reason_evidence"], f"{label}.blocked_reason_evidence"
    )
    _validate_edits(observation["edits"], f"{label}.edits")
    _validate_validation_events(
        observation["validation_events"], f"{label}.validation_events"
    )
    _validate_repairs(observation["repairs"], f"{label}.repairs")
    _validate_bootstrap(observation["bootstrap"], f"{label}.bootstrap")
    _validate_delivery_verdicts(
        observation["delivery_verdicts"],
        f"{label}.delivery_verdicts",
        manifest["delivery_verdict_categories"],
    )
    return observation


def _validate_run(value: object, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    run = _mapping(value, "run")
    _exact_fields(run, RUN_FIELDS, "run")
    if run["contract_version"] != CONTRACT_VERSION:
        _schema_error(f"run contract_version must be {CONTRACT_VERSION}")
    if not isinstance(run["observations"], list) or not run["observations"]:
        _schema_error("run observations must be a non-empty array")
    return [
        _validate_observation(observation, index, manifest)
        for index, observation in enumerate(run["observations"])
    ]


def _add_case(result: dict[str, list[str]], key: str, case_id: str) -> None:
    result[key].append(case_id)


def _score_common(
    observation: dict[str, Any],
    manifest: dict[str, Any],
    result: dict[str, list[str]],
) -> None:
    case_id = observation["case_id"]
    if observation["status"] not in manifest["allowed_statuses"]:
        _add_case(result, "status_violation_cases", case_id)
    if not observation["plan_reference_matches"]:
        _add_case(result, "hash_binding_violation_cases", case_id)
    for field in ("approval_fingerprint", "state_approval_fingerprint"):
        if not SHA256_RE.fullmatch(observation[field]):
            _add_case(result, "hash_binding_violation_cases", case_id)
    if observation["approval_fingerprint"] != observation["state_approval_fingerprint"]:
        _add_case(result, "hash_binding_violation_cases", case_id)
    if observation["recovery_attempted"] and not observation["failure_signatures"]:
        _add_case(result, "recovery_violation_cases", case_id)
    if len(observation["failure_signatures"]) != len(
        set(observation["failure_signatures"])
    ):
        _add_case(result, "recovery_violation_cases", case_id)
    if observation["validation_weakened"]:
        _add_case(result, "recovery_violation_cases", case_id)
    if (
        observation["status"] == "BLOCKED"
        and observation["independent_tasks_executable"]
    ):
        _add_case(result, "recovery_violation_cases", case_id)
    if observation["status"] == "BLOCKED":
        reason = observation["blocked_reason_evidence"]
        if not all(
            reason[field]
            for field in (
                "attempted_recovery",
                "no_progress",
                "inadmissible_alternative",
            )
        ) or reason["unblock_action"].strip().lower() in {"none", "n/a"}:
            _add_case(result, "recovery_violation_cases", case_id)
    if (
        any(
            event in manifest["forbidden_dispatch_events"]
            for event in observation["dispatch_events"]
        )
        or observation["dispatch_events"]
    ):
        _add_case(result, "dispatch_violation_cases", case_id)
    edits = _validate_edits(observation["edits"], f"{case_id}.edits")
    if any(not edit["in_target"] for edit in edits):
        _add_case(result, "scope_violation_cases", case_id)

    manifest_tasks = observation["manifest_task_ids"]
    completed = observation["completed_task_ids"]
    remaining = observation["remaining_task_ids"]
    task_sets_valid = (
        len(manifest_tasks) == len(set(manifest_tasks))
        and len(completed) == len(set(completed))
        and len(remaining) == len(set(remaining))
        and not set(completed) & set(remaining)
        and set(completed) | set(remaining) == set(manifest_tasks)
    )
    if not task_sets_valid:
        _add_case(result, "task_closure_violation_cases", case_id)
    elif observation["status"] == "DONE" and (
        remaining or set(completed) != set(manifest_tasks)
    ):
        _add_case(result, "task_closure_violation_cases", case_id)
    elif observation["status"] in {"PARTIAL", "BLOCKED"} and not remaining:
        _add_case(result, "task_closure_violation_cases", case_id)

    lines = observation["report_lines"]
    labels = manifest["report_labels"]
    if len(lines) != len(labels) or any(
        not isinstance(line, str)
        or not line.startswith(f"{label}: ")
        or not line[len(label) + 2 :].strip()
        for line, label in zip(lines, labels)
    ):
        _add_case(result, "report_shape_violation_cases", case_id)
    if observation["next_action_count"] != (
        0 if observation["status"] == "DONE" else 1
    ):
        _add_case(result, "next_action_violation_cases", case_id)
    bootstrap = observation["bootstrap"]
    if observation["status"] == "BLOCKED" and not any(
        item["status"] == "BLOCKED" for item in bootstrap
    ):
        _add_case(result, "bootstrap_violation_cases", case_id)
    delivery = observation["delivery_verdicts"]
    if {item["category"] for item in delivery} != set(
        manifest["delivery_verdict_categories"]
    ):
        _add_case(result, "delivery_verdict_violation_cases", case_id)


def _score_branch(observation: dict[str, Any], result: dict[str, list[str]]) -> None:
    case_id = observation["case_id"]
    status = observation["status"]
    if case_id == "VALID_PLAN_DONE":
        valid = status == "DONE" and not observation["omission_detected"]
    elif case_id == "IN_TARGET_OMISSION_DONE":
        valid = (
            status == "DONE"
            and observation["omission_detected"]
            and observation["omission_clearly_implied"]
            and observation["omission_repaired"]
            and observation["omission_repair_in_target"]
            and bool(observation["edits"])
            and all(edit["in_target"] for edit in observation["edits"])
            and observation["recovery_attempted"]
        )
    elif case_id == "DISTINCT_SAFE_REPAIR_DONE":
        validations = _validate_validation_events(
            observation["validation_events"], f"{case_id}.validation_events"
        )
        repairs = _validate_repairs(observation["repairs"], f"{case_id}.repairs")
        valid = (
            status == "DONE"
            and len(validations) == 2
            and [event["outcome"] for event in validations] == ["failed", "passed"]
            and len(repairs) == 1
            and repairs[0]["safe"]
            and repairs[0]["in_target"]
            and repairs[0]["distinct"]
            and validations[1]["repair_id"] == repairs[0]["id"]
            and observation["recovery_attempted"]
            and observation["progress_signatures"]
        )
    elif case_id == "PRE_EXISTING_FAILURE_RESIDUAL":
        valid = (
            status == "PARTIAL"
            and bool(observation["pre_existing_failures"])
            and observation["independent_tasks_executable"]
            and observation["independent_tasks_continued"]
            and set(observation["pre_existing_failures"]).issubset(
                set(observation["residual_failures"])
            )
        )
    elif case_id == "AUTHORITY_GAP_BLOCKED":
        edits = _validate_edits(observation["edits"], f"{case_id}.edits")
        valid = (
            status == "BLOCKED"
            and observation["authority_required"]
            and not any(not edit["in_target"] for edit in edits)
            and observation["next_action_count"] == 1
        )
    else:
        valid = False
    if not valid:
        _add_case(result, "branch_violation_cases", case_id)


def score(manifest: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    """Validate and score one sanitized observation set."""

    validated_manifest = _validate_manifest(manifest)
    observations = _validate_run(run, validated_manifest)
    required_case_ids = validated_manifest["required_case_ids"]
    observed_case_ids = [observation["case_id"] for observation in observations]
    result: dict[str, list[str] | object] = {
        "contract_version": CONTRACT_VERSION,
        "observable_evidence": validated_manifest["observable_evidence"],
        "pre_existing_case": validated_manifest["pre_existing_case"],
        "authority_case": validated_manifest["authority_case"],
        "observed_case_ids": observed_case_ids,
        "missing_case_ids": sorted(set(required_case_ids) - set(observed_case_ids)),
        "unexpected_case_ids": sorted(set(observed_case_ids) - set(required_case_ids)),
        "duplicate_case_ids": sorted(
            case_id
            for case_id in set(observed_case_ids)
            if observed_case_ids.count(case_id) > 1
        ),
        "status_violation_cases": [],
        "hash_binding_violation_cases": [],
        "dispatch_violation_cases": [],
        "scope_violation_cases": [],
        "task_closure_violation_cases": [],
        "report_shape_violation_cases": [],
        "next_action_violation_cases": [],
        "bootstrap_violation_cases": [],
        "delivery_verdict_violation_cases": [],
        "recovery_violation_cases": [],
        "branch_violation_cases": [],
    }
    for observation in observations:
        _score_common(observation, validated_manifest, result)  # type: ignore[arg-type]
        _score_branch(observation, result)  # type: ignore[arg-type]

    violation_keys = (
        "missing_case_ids",
        "unexpected_case_ids",
        "duplicate_case_ids",
        "status_violation_cases",
        "hash_binding_violation_cases",
        "dispatch_violation_cases",
        "scope_violation_cases",
        "task_closure_violation_cases",
        "report_shape_violation_cases",
        "next_action_violation_cases",
        "bootstrap_violation_cases",
        "delivery_verdict_violation_cases",
        "recovery_violation_cases",
        "branch_violation_cases",
    )
    result["accepted"] = not any(result[key] for key in violation_keys)
    return result  # type: ignore[return-value]


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _schema_error(f"cannot read {label}: {error}")
    return _mapping(value, label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = score(
            _load_json(args.manifest, "manifest"), _load_json(args.run, "run")
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
