#!/usr/bin/env python3
"""Score sanitized codebase-improvement gateway observations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

_CONTRACT_VERSION = "internal-gateway-codebase-improvement-eval-v2"
_CLEAR_OUTCOME = "route-to-execution-owner"
_CLEAR_DEFENSES = {"none", "resolves"}
_CANONICAL_OUTCOMES = {
    "reformulate-plan",
    "de-escalate-to-simple",
    "route-to-execution-owner",
    "review-evidence",
    "continue-critical-with-new-evidence",
    "accept-with-risk",
}
_CANONICAL_DEFENSES = {
    "none",
    "resolves",
    "narrows",
    "accepts-risk",
    "unanswered",
}
_CASE_FIELDS = {
    "case_id": str,
    "direct_skills": list,
    "report_fingerprint": (str, type(None)),
    "critic_input_fingerprint": (str, type(None)),
    "report_written_before_critique": bool,
    "critical_outcome": (str, type(None)),
    "defense": (str, type(None)),
    "unresolved_material_issue": bool,
    "reran_external_report_flow": bool,
    "report_returned": bool,
    "resume_condition": (str, type(None)),
    "post_report_actions": list,
}


def _schema_error(message: str) -> NoReturn:
    raise ValueError(message)


def _require_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _schema_error(f"{label} must be a JSON object")
    return value


def _require_string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        _schema_error(f"{label} must be an array of strings")
    return value


def _validate_manifest(manifest: dict[str, object]) -> tuple[list[str], list[str]]:
    if manifest.get("contract_version") != _CONTRACT_VERSION:
        _schema_error(f"manifest contract_version must be {_CONTRACT_VERSION}")
    required_cases = _require_string_list(
        manifest.get("required_case_ids"), "manifest required_case_ids"
    )
    if not required_cases or len(required_cases) != len(set(required_cases)):
        _schema_error("manifest required_case_ids must be non-empty and unique")
    direct_skills = _require_string_list(
        manifest.get("required_direct_skills"), "manifest required_direct_skills"
    )
    if not direct_skills:
        _schema_error("manifest required_direct_skills must be non-empty")
    if manifest.get("maximum_identity_drift_cases") != 0:
        _schema_error("manifest maximum_identity_drift_cases must be 0")
    if manifest.get("maximum_post_report_actions") != 0:
        _schema_error("manifest maximum_post_report_actions must be 0")
    if manifest.get("forbid_non_clear_reports") is not True:
        _schema_error("manifest forbid_non_clear_reports must be true")
    return required_cases, direct_skills


def _validate_run(run: dict[str, object]) -> list[dict[str, object]]:
    if run.get("contract_version") != _CONTRACT_VERSION:
        _schema_error(f"run contract_version must be {_CONTRACT_VERSION}")
    observations = run.get("observations")
    if not isinstance(observations, list) or not observations:
        _schema_error("run observations must be a non-empty array")

    validated: list[dict[str, object]] = []
    for index, value in enumerate(observations):
        case = _require_mapping(value, f"observation {index}")
        for field, expected_type in _CASE_FIELDS.items():
            if field not in case or not isinstance(case[field], expected_type):
                _schema_error(f"observation {index} has invalid {field}")
        _require_string_list(case["direct_skills"], f"observation {index} direct_skills")
        _require_string_list(
            case["post_report_actions"],
            f"observation {index} post_report_actions",
        )
        validated.append(case)
    return validated


def score(manifest: dict[str, object], run: dict[str, object]) -> dict[str, object]:
    """Validate and score one sanitized runtime observation set."""

    required_cases, required_direct_skills = _validate_manifest(
        _require_mapping(manifest, "manifest")
    )
    observations = _validate_run(_require_mapping(run, "run"))

    observed_case_ids = [str(case["case_id"]) for case in observations]
    missing_case_ids = sorted(set(required_cases) - set(observed_case_ids))
    duplicate_case_ids = sorted(
        case_id
        for case_id in set(observed_case_ids)
        if observed_case_ids.count(case_id) > 1
    )
    direct_skill_violation_cases: list[str] = []
    report_order_violation_cases: list[str] = []
    identity_drift_cases: list[str] = []
    missing_fingerprint_cases: list[str] = []
    invalid_critic_state_cases: list[str] = []
    missing_rerun_or_resume_cases: list[str] = []
    false_report_return_cases: list[str] = []
    missing_report_return_cases: list[str] = []
    post_report_violation_cases: list[str] = []

    for case in observations:
        case_id = str(case["case_id"])
        report_fingerprint = case["report_fingerprint"]
        critic_input_fingerprint = case["critic_input_fingerprint"]
        critical_outcome = case["critical_outcome"]
        defense = case["defense"]
        report_available = report_fingerprint is not None or critic_input_fingerprint is not None

        if case["direct_skills"] != required_direct_skills:
            direct_skill_violation_cases.append(case_id)

        if not report_available and (critical_outcome is not None or defense is not None):
            invalid_critic_state_cases.append(case_id)
        elif (critical_outcome is None) != (defense is None):
            invalid_critic_state_cases.append(case_id)
        elif (
            critical_outcome is not None
            and critical_outcome not in _CANONICAL_OUTCOMES
        ) or (defense is not None and defense not in _CANONICAL_DEFENSES):
            invalid_critic_state_cases.append(case_id)

        if report_available and (
            report_fingerprint is None or critic_input_fingerprint is None
        ):
            missing_fingerprint_cases.append(case_id)
        if case["report_returned"] and report_fingerprint is None:
            missing_fingerprint_cases.append(case_id)
        if report_fingerprint is not None and critic_input_fingerprint is not None:
            if report_fingerprint != critic_input_fingerprint:
                identity_drift_cases.append(case_id)

        if not case["report_written_before_critique"] and (
            report_available
            or critical_outcome is not None
            or defense is not None
            or case["report_returned"]
        ):
            report_order_violation_cases.append(case_id)

        clear = (
            critical_outcome == _CLEAR_OUTCOME
            and defense in _CLEAR_DEFENSES
            and case["unresolved_material_issue"] is False
        )
        resume_condition = case["resume_condition"]
        has_resume_condition = isinstance(resume_condition, str) and bool(resume_condition.strip())
        if not clear and not case["reran_external_report_flow"] and not has_resume_condition:
            missing_rerun_or_resume_cases.append(case_id)
        if not clear and case["report_returned"]:
            false_report_return_cases.append(case_id)
        if clear and not case["report_returned"]:
            missing_report_return_cases.append(case_id)
        if case["post_report_actions"]:
            post_report_violation_cases.append(case_id)

    result: dict[str, object] = {
        "contract_version": _CONTRACT_VERSION,
        "observed_case_ids": observed_case_ids,
        "missing_case_ids": missing_case_ids,
        "duplicate_case_ids": duplicate_case_ids,
        "direct_skill_violation_cases": sorted(direct_skill_violation_cases),
        "report_order_violation_cases": sorted(report_order_violation_cases),
        "identity_drift_cases": sorted(identity_drift_cases),
        "missing_fingerprint_cases": sorted(set(missing_fingerprint_cases)),
        "invalid_critic_state_cases": sorted(invalid_critic_state_cases),
        "missing_rerun_or_resume_cases": sorted(missing_rerun_or_resume_cases),
        "false_report_return_cases": sorted(false_report_return_cases),
        "missing_report_return_cases": sorted(missing_report_return_cases),
        "post_report_violation_cases": sorted(post_report_violation_cases),
    }
    result["accepted"] = not any(
        result[key]
        for key in (
            "missing_case_ids",
            "duplicate_case_ids",
            "direct_skill_violation_cases",
            "report_order_violation_cases",
            "identity_drift_cases",
            "missing_fingerprint_cases",
            "invalid_critic_state_cases",
            "missing_rerun_or_resume_cases",
            "false_report_return_cases",
            "missing_report_return_cases",
            "post_report_violation_cases",
        )
    )
    return result


def _load_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _schema_error(f"cannot read {label}: {error}")
    return _require_mapping(value, label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        result = score(
            _load_json(args.manifest, "manifest"),
            _load_json(args.run, "run"),
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
