"""Score sanitized observations from controlled internal-gateway-idea runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Final


CONTRACT_VERSION: Final = "internal-gateway-idea-eval-v1"
REQUIRED_CASE_IDS: Final = (
    "COVERAGE_OMISSION_BLOCK",
    "PLATFORM_ADAPTER_ONLY_BLOCK",
    "MINIMALITY_NEW_SKILL_BLOCK",
    "FULL_SCOPE_CRITIC_PASS",
    "DELTA_CRITIQUE_BLOCK",
    "MATERIAL_REVISION_RECRITIQUE",
    "STALE_RESUME_BLOCK",
    "LOW_RISK_PROPORTIONAL_PASS",
)
OBSERVATION_FIELDS: Final = (
    "case_id",
    "direct_skills",
    "declared_deliverable_ids",
    "covered_deliverable_ids",
    "platform_semantics_controlling",
    "primary_source_before_defaults",
    "minimality_options",
    "new_abstraction_selected",
    "new_abstraction_invariant",
    "new_abstraction_exit_criterion",
    "analysis_scope",
    "critic_context",
    "independent_fallback_routed",
    "material_revision_after_critique",
    "critic_rerun_after_revision",
    "resume_state",
    "stale_approval_reused",
    "final_plan_approval",
    "plan_writing_started",
    "expected_route",
)
ALLOWED_ANALYSIS_SCOPES: Final = {"full", "delta"}
ALLOWED_CRITIC_CONTEXTS: Final = {"independent", "same-context", "unavailable"}
ALLOWED_RESUME_STATES: Final = {"current", "stale", "missing"}
ALLOWED_ROUTES: Final = {
    "reopen-analysis",
    "revise-design",
    "request-separate-review",
    "await-final-approval",
    "write-plan",
}
HIGH_RISK_CASES: Final = frozenset(REQUIRED_CASE_IDS) - {
    "LOW_RISK_PROPORTIONAL_PASS"
}
MINIMALITY_BASELINES: Final = {
    "no-new-artifact",
    "existing-owner",
    "new-abstraction",
}
RESULT_LISTS: Final = (
    "missing_case_ids",
    "duplicate_case_ids",
    "coverage_violation_cases",
    "platform_order_violation_cases",
    "minimality_violation_cases",
    "full_scope_violation_cases",
    "stale_critique_cases",
    "stale_resume_cases",
    "approval_order_violation_cases",
    "route_violation_cases",
)


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _strings(value: object, label: str, *, unique: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be an array of strings")
    result = list(value)
    if unique and len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def _boolean(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be boolean")
    return value


def _enum(value: object, label: str, allowed: set[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{label} must be one of: {choices}")
    return value


def _validate_manifest(manifest: object) -> None:
    data = _mapping(manifest, "manifest")
    required_fields = {"contract_version", "required_case_ids", "observation_fields"}
    if set(data) != required_fields:
        raise ValueError("manifest must contain contract_version, required_case_ids, and observation_fields")
    if data["contract_version"] != CONTRACT_VERSION:
        raise ValueError("manifest contract_version is unsupported")

    case_ids = _strings(data["required_case_ids"], "manifest.required_case_ids", unique=True)
    if set(case_ids) != set(REQUIRED_CASE_IDS):
        raise ValueError("manifest.required_case_ids must contain the approved eight case IDs")
    fields = _strings(data["observation_fields"], "manifest.observation_fields", unique=True)
    if set(fields) != set(OBSERVATION_FIELDS):
        raise ValueError("manifest.observation_fields does not match the sanitized schema")


def _validate_observation(observation: object, index: int) -> dict[str, object]:
    data = _mapping(observation, f"observations[{index}]")
    if set(data) != set(OBSERVATION_FIELDS):
        raise ValueError(f"observations[{index}] does not match the sanitized schema")
    case_id = data["case_id"]
    if not isinstance(case_id, str) or case_id not in REQUIRED_CASE_IDS:
        raise ValueError(f"observations[{index}].case_id is not approved")

    _strings(data["direct_skills"], f"observations[{index}].direct_skills")
    _strings(data["declared_deliverable_ids"], f"observations[{index}].declared_deliverable_ids")
    _strings(data["covered_deliverable_ids"], f"observations[{index}].covered_deliverable_ids")
    _boolean(data["platform_semantics_controlling"], f"observations[{index}].platform_semantics_controlling")
    _boolean(data["primary_source_before_defaults"], f"observations[{index}].primary_source_before_defaults")
    _strings(data["minimality_options"], f"observations[{index}].minimality_options", unique=True)
    _boolean(data["new_abstraction_selected"], f"observations[{index}].new_abstraction_selected")
    _boolean(data["new_abstraction_invariant"], f"observations[{index}].new_abstraction_invariant")
    _boolean(data["new_abstraction_exit_criterion"], f"observations[{index}].new_abstraction_exit_criterion")
    _enum(data["analysis_scope"], f"observations[{index}].analysis_scope", ALLOWED_ANALYSIS_SCOPES)
    _enum(data["critic_context"], f"observations[{index}].critic_context", ALLOWED_CRITIC_CONTEXTS)
    _boolean(data["independent_fallback_routed"], f"observations[{index}].independent_fallback_routed")
    _boolean(data["material_revision_after_critique"], f"observations[{index}].material_revision_after_critique")
    _boolean(data["critic_rerun_after_revision"], f"observations[{index}].critic_rerun_after_revision")
    _enum(data["resume_state"], f"observations[{index}].resume_state", ALLOWED_RESUME_STATES)
    _boolean(data["stale_approval_reused"], f"observations[{index}].stale_approval_reused")
    _boolean(data["final_plan_approval"], f"observations[{index}].final_plan_approval")
    _boolean(data["plan_writing_started"], f"observations[{index}].plan_writing_started")
    _enum(data["expected_route"], f"observations[{index}].expected_route", ALLOWED_ROUTES)
    return data


def _validate_run(run: object) -> list[dict[str, object]]:
    data = _mapping(run, "run")
    if set(data) != {"observations"}:
        raise ValueError("run must contain only observations")
    observations = data["observations"]
    if not isinstance(observations, list):
        raise ValueError("run.observations must be an array")
    return [_validate_observation(item, index) for index, item in enumerate(observations)]


def _case_ids(observations: list[dict[str, object]], predicate) -> list[str]:
    return [observation["case_id"] for observation in observations if predicate(observation)]


def score(manifest: dict[str, object], run: dict[str, object]) -> dict[str, object]:
    """Return deterministic validation lists for a sanitized controlled run."""

    _validate_manifest(manifest)
    observations = _validate_run(run)
    observed_case_ids = [observation["case_id"] for observation in observations]
    counts = {case_id: observed_case_ids.count(case_id) for case_id in REQUIRED_CASE_IDS}

    result: dict[str, object] = {
        "observed_case_ids": observed_case_ids,
        "missing_case_ids": sorted(case_id for case_id, count in counts.items() if count == 0),
        "duplicate_case_ids": sorted(case_id for case_id, count in counts.items() if count > 1),
        "coverage_violation_cases": [],
        "platform_order_violation_cases": [],
        "minimality_violation_cases": [],
        "full_scope_violation_cases": [],
        "stale_critique_cases": [],
        "stale_resume_cases": [],
        "approval_order_violation_cases": [],
        "route_violation_cases": [],
    }

    result["coverage_violation_cases"] = _case_ids(
        observations,
        lambda item: (
            (item["plan_writing_started"] or item["expected_route"] == "write-plan")
            and set(item["declared_deliverable_ids"])
            != set(item["covered_deliverable_ids"])
        ),
    )
    result["platform_order_violation_cases"] = _case_ids(
        observations,
        lambda item: item["platform_semantics_controlling"]
        and not item["primary_source_before_defaults"],
    )
    result["minimality_violation_cases"] = _case_ids(
        observations,
        lambda item: item["new_abstraction_selected"]
        and (
            not MINIMALITY_BASELINES.issubset(set(item["minimality_options"]))
            or not item["new_abstraction_invariant"]
            or not item["new_abstraction_exit_criterion"]
        ),
    )
    result["full_scope_violation_cases"] = _case_ids(
        observations,
        lambda item: item["case_id"] in HIGH_RISK_CASES
        and (item["analysis_scope"] != "full" or item["critic_context"] != "independent"),
    )
    result["stale_critique_cases"] = _case_ids(
        observations,
        lambda item: item["material_revision_after_critique"]
        and not item["critic_rerun_after_revision"],
    )
    result["stale_resume_cases"] = _case_ids(
        observations,
        lambda item: item["resume_state"] in {"stale", "missing"}
        and (item["stale_approval_reused"] or item["plan_writing_started"]),
    )
    result["approval_order_violation_cases"] = _case_ids(
        observations,
        lambda item: item["plan_writing_started"]
        and (not item["final_plan_approval"] or item["expected_route"] != "write-plan"),
    )
    result["route_violation_cases"] = _case_ids(
        observations,
        lambda item: item["critic_context"] == "unavailable"
        and (
            not item["independent_fallback_routed"]
            or item["expected_route"] == "write-plan"
        ),
    )
    result["accepted"] = not any(result[key] for key in RESULT_LISTS)
    return result


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read {label}: {exc}") from exc
    return _mapping(payload, label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = score(_read_json(args.manifest, "manifest"), _read_json(args.run, "run"))
    except (OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
