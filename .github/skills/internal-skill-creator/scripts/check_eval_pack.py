#!/usr/bin/env python3
"""Validate a skill eval pack and an optional run record using only the stdlib."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

PACK_SCHEMA = "skill-eval-pack/v1"
RUN_SCHEMA = "skill-eval-run/v1"
PACK_FIELDS = {"schema", "skill", "requirements", "cases", "triggers"}
REQUIREMENT_FIELDS = {"id", "text", "source"}
CASE_FIELDS = {
    "id",
    "family",
    "kind",
    "requirement_ids",
    "prompt",
    "initial_state",
    "expected_output",
    "files",
    "assertions",
    "forbidden_actions",
    "defective_fixture",
    "rubric",
    "status",
    "held_out",
}
TRIGGER_FIELDS = {"id", "query", "should_trigger", "split", "competing_owner"}
RUN_FIELDS = {
    "schema",
    "skill",
    "date",
    "host",
    "model",
    "configuration",
    "case_results",
}
IDENTIFIERS = {
    "requirement": re.compile(r"^R-[A-Z0-9-]+$"),
    "case": re.compile(r"^C-[A-Z0-9-]+$"),
    "query": re.compile(r"^Q-[A-Z0-9-]+$"),
}


class DuplicateJSONKey(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKey(key)
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _finding(code: str, message: str, path: Path | None = None) -> dict[str, str]:
    finding = {"code": code, "message": message, "severity": "blocking"}
    if path is not None:
        finding["path"] = path.as_posix()
    return finding


def _has_exact_fields(value: Any, required: set[str], optional: set[str] = frozenset()) -> bool:
    return isinstance(value, dict) and required <= value.keys() and value.keys() <= required | optional


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_existing_path(bundle_root: Path, value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return False
    try:
        resolved_root = bundle_root.resolve(strict=True)
        resolved_path = (resolved_root / relative).resolve(strict=True)
        resolved_path.relative_to(resolved_root)
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _pack_from_path(pack_path: Path, findings: list[dict[str, str]]) -> Any:
    try:
        return _load_json(pack_path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKey) as exc:
        findings.append(_finding("eval-pack-invalid-json", f"Pack is not strict JSON: {exc}", pack_path))
        return None


def _validate_pack(pack: Any, bundle_root: Path, skill_name: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not _has_exact_fields(pack, PACK_FIELDS) or pack.get("schema") != PACK_SCHEMA or pack.get("skill") != skill_name:
        findings.append(_finding("eval-pack-schema", "Pack top-level fields, schema, or skill name are invalid."))
        return findings

    requirements = pack["requirements"]
    cases = pack["cases"]
    triggers = pack["triggers"]
    if not isinstance(requirements, list) or not requirements or not isinstance(cases, list) or not cases:
        findings.append(_finding("eval-pack-schema", "Requirements and cases must be non-empty lists."))
        return findings
    if not _has_exact_fields(triggers, {"queries"}) or not isinstance(triggers["queries"], list):
        findings.append(_finding("eval-pack-schema", "Triggers must contain a queries list."))
        return findings

    requirement_ids: set[str] = set()
    case_ids: set[str] = set()
    query_ids: set[str] = set()
    all_ids: set[str] = set()
    covered_requirements: set[str] = set()

    def add_unique(identifier: Any, pattern: re.Pattern[str], seen: set[str]) -> bool:
        if not isinstance(identifier, str) or not pattern.fullmatch(identifier):
            return False
        if identifier in all_ids or identifier in seen:
            findings.append(_finding("eval-pack-duplicate-id", f"Duplicate identifier: {identifier}"))
            return False
        all_ids.add(identifier)
        seen.add(identifier)
        return True

    for item in requirements:
        if not _has_exact_fields(item, REQUIREMENT_FIELDS) or not all(
            _nonempty_string(item.get(field)) for field in ("id", "text", "source")
        ):
            findings.append(_finding("eval-pack-schema", "Requirement entries need id, text, and source strings."))
            continue
        if not IDENTIFIERS["requirement"].fullmatch(item["id"]):
            findings.append(_finding("eval-pack-schema", f"Invalid requirement identifier: {item['id']}"))
        else:
            add_unique(item["id"], IDENTIFIERS["requirement"], requirement_ids)

    known_requirements = set(requirement_ids)
    for case in cases:
        if not isinstance(case, dict):
            findings.append(_finding("eval-pack-schema", "Case entries must be objects."))
            continue
        kind = case.get("kind")
        required = CASE_FIELDS - {"defective_fixture", "rubric"}
        optional = {"defective_fixture"} if kind == "deterministic" else {"rubric"}
        if not _has_exact_fields(case, required, optional) or kind not in {"deterministic", "rubric"}:
            findings.append(_finding("eval-pack-schema", "Case fields or kind are invalid."))
            continue
        if not isinstance(case["id"], str) or not IDENTIFIERS["case"].fullmatch(case["id"]):
            findings.append(_finding("eval-pack-schema", f"Invalid case identifier: {case['id']}"))
        else:
            add_unique(case["id"], IDENTIFIERS["case"], case_ids)
        if not all(_nonempty_string(case[field]) for field in ("family", "prompt", "initial_state", "expected_output")):
            findings.append(_finding("eval-pack-schema", f"Case {case.get('id')} has an empty text field."))
        reqs = case["requirement_ids"]
        if not isinstance(reqs, list) or not reqs:
            findings.append(_finding("eval-pack-schema", f"Case {case.get('id')} needs requirement IDs."))
        else:
            for req_id in reqs:
                if req_id not in known_requirements:
                    findings.append(_finding("eval-pack-unresolved-requirement", f"Unknown requirement {req_id}."))
                else:
                    covered_requirements.add(req_id)
        if not isinstance(case["files"], list) or any(not _safe_existing_path(bundle_root, item) for item in case["files"]):
            findings.append(_finding("eval-pack-unsafe-path", f"Case {case.get('id')} has an unsafe or missing file path."))
        assertions = case["assertions"]
        if not isinstance(assertions, list) or not assertions:
            findings.append(_finding("eval-pack-schema", f"Case {case.get('id')} needs assertions."))
        else:
            assertion_ids: set[str] = set()
            for assertion in assertions:
                if not _has_exact_fields(assertion, {"id", "text", "critical"}) or not _nonempty_string(assertion.get("id")) or not _nonempty_string(assertion.get("text")) or not isinstance(assertion.get("critical"), bool):
                    findings.append(_finding("eval-pack-schema", f"Case {case.get('id')} has an invalid assertion."))
                elif assertion["id"] in assertion_ids:
                    findings.append(_finding("eval-pack-duplicate-id", f"Duplicate assertion identifier {assertion['id']} in {case.get('id')}."))
                else:
                    assertion_ids.add(assertion["id"])
        if not isinstance(case["forbidden_actions"], list) or any(not _nonempty_string(item) for item in case["forbidden_actions"]):
            findings.append(_finding("eval-pack-schema", f"Case {case.get('id')} has invalid forbidden actions."))
        if case["status"] not in {"generated", "not-run", "blocked"}:
            findings.append(_finding("eval-pack-invalid-status", f"Case {case.get('id')} has an invalid evidence status."))
        if not isinstance(case["held_out"], bool):
            findings.append(_finding("eval-pack-schema", f"Case {case.get('id')} held_out must be boolean."))
        if kind == "deterministic":
            if "defective_fixture" not in case:
                findings.append(_finding("eval-pack-missing-defective-fixture", f"Deterministic case {case.get('id')} has no defective fixture."))
            elif not _safe_existing_path(bundle_root, case["defective_fixture"]):
                findings.append(_finding("eval-pack-unsafe-path", f"Case {case.get('id')} has an unsafe or missing defective fixture."))
        elif "rubric" not in case:
            findings.append(_finding("eval-pack-missing-rubric", f"Rubric case {case.get('id')} has no rubric."))
        elif not _has_exact_fields(case["rubric"], {"pass", "fail"}) or any(
            not isinstance(case["rubric"].get(key), list)
            or not case["rubric"][key]
            or any(not _nonempty_string(anchor) for anchor in case["rubric"][key])
            for key in ("pass", "fail")
        ):
            findings.append(_finding("eval-pack-missing-rubric", f"Rubric case {case.get('id')} has no anchored pass/fail rubric."))

    if requirement_ids - covered_requirements:
        findings.append(_finding("eval-pack-uncovered-requirement", "One or more requirements have no case coverage."))

    polarities: set[bool] = set()
    splits: set[str] = set()
    for query in triggers["queries"]:
        if not _has_exact_fields(query, TRIGGER_FIELDS - {"competing_owner"}, {"competing_owner"}) or not _nonempty_string(query.get("id")) or not _nonempty_string(query.get("query")) or not isinstance(query.get("should_trigger"), bool) or query.get("split") not in {"train", "held-out"}:
            findings.append(_finding("eval-pack-trigger-coverage", "A trigger query has invalid fields."))
            continue
        if not IDENTIFIERS["query"].fullmatch(query["id"]):
            findings.append(_finding("eval-pack-schema", f"Invalid trigger identifier: {query['id']}"))
            continue
        if not add_unique(query["id"], IDENTIFIERS["query"], query_ids):
            continue
        polarities.add(query["should_trigger"])
        splits.add(query["split"])
        if "competing_owner" in query and not _nonempty_string(query["competing_owner"]):
            findings.append(_finding("eval-pack-schema", f"Trigger {query['id']} has an empty competing owner."))
    if polarities != {True, False} or splits != {"train", "held-out"}:
        findings.append(_finding("eval-pack-trigger-coverage", "Triggers need both polarities and both train and held-out splits."))
    return findings


def check_pack(pack_path: Path, bundle_root: Path, skill_name: str) -> list[dict[str, str]]:
    """Validate a pack file and return stable finding records."""
    findings: list[dict[str, str]] = []
    pack = _pack_from_path(Path(pack_path), findings)
    if findings:
        return findings
    if not isinstance(pack, dict):
        return [_finding("eval-pack-schema", "Pack top level must be an object.", Path(pack_path))]
    return _validate_pack(pack, Path(bundle_root), skill_name)


def check_run_record(record_path: Path, bundle_root: Path, pack: dict[str, Any]) -> list[dict[str, str]]:
    """Validate a run record against the exact cases and assertions in a pack."""
    try:
        record = _load_json(Path(record_path))
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKey) as exc:
        return [_finding("eval-run-unbacked-result", f"Run record is not valid strict JSON: {exc}", Path(record_path))]
    try:
        valid_date = isinstance(record, dict) and date.fromisoformat(record.get("date", "")).isoformat() == record.get("date")
    except (TypeError, ValueError):
        valid_date = False
    if not _has_exact_fields(record, RUN_FIELDS) or record.get("schema") != RUN_SCHEMA or record.get("skill") != pack.get("skill") or not valid_date or not _nonempty_string(record.get("host")) or not _nonempty_string(record.get("model")) or record.get("configuration") not in {"with-skill", "baseline-none", "baseline-previous"} or not isinstance(record.get("case_results"), list):
        return [_finding("eval-run-unbacked-result", "Run record metadata or fields are invalid.", Path(record_path))]
    cases = {case["id"]: case for case in pack.get("cases", []) if isinstance(case, dict) and isinstance(case.get("id"), str)}
    findings: list[dict[str, str]] = []
    for result in record["case_results"]:
        if not isinstance(result, dict) or not {"case_id", "status", "assertions"} <= result.keys() or result.keys() - {"case_id", "status", "transcript_ref", "assertions"}:
            findings.append(_finding("eval-run-unbacked-result", "Run case result fields are invalid."))
            continue
        case = cases.get(result.get("case_id"))
        status = result.get("status")
        if case is None or status not in {"executed", "passed", "failed", "blocked"}:
            findings.append(_finding("eval-run-unbacked-result", f"Run result is not backed by a pack case: {result.get('case_id')}"))
            continue
        if status in {"executed", "passed", "failed"} and not _nonempty_string(result.get("transcript_ref")):
            findings.append(_finding("eval-run-unbacked-result", f"{status} result for {result['case_id']} has no transcript reference."))
        declared = {item.get("id"): item for item in case.get("assertions", []) if isinstance(item, dict)}
        assertions = result.get("assertions")
        if not isinstance(assertions, list) or any(not isinstance(item, dict) or set(item) != {"id", "passed", "evidence"} or not isinstance(item.get("passed"), bool) for item in assertions):
            findings.append(_finding("eval-run-assertion-mismatch", f"Run assertions for {result['case_id']} are malformed."))
            continue
        actual = [item["id"] for item in assertions]
        if len(actual) != len(set(actual)) or set(actual) != set(declared):
            findings.append(_finding("eval-run-assertion-mismatch", f"Run assertions do not match case {result['case_id']} exactly."))
            continue
        if status == "passed" and any(not item["passed"] or not _nonempty_string(item["evidence"]) for item in assertions):
            findings.append(_finding("eval-run-unbacked-result", f"Passed result for {result['case_id']} lacks passing assertion evidence."))
        if status == "passed" and any(declared[item["id"]].get("critical") and not item["passed"] for item in assertions):
            findings.append(_finding("eval-run-unbacked-result", f"Passed result has a failed critical assertion for {result['case_id']}"))
    return findings


def _read_pack_for_run(pack_path: Path) -> dict[str, Any] | None:
    try:
        pack = _load_json(pack_path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKey):
        return None
    return pack if isinstance(pack, dict) else None


def _payload(findings: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "status": "failed" if findings else "ok",
        "finding_counts": {"blocking": len(findings), "total": len(findings)},
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--bundle-root", required=True, type=Path)
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--run-record", type=Path)
    parser.add_argument("--format", choices=("text", "compact"), default="text")
    args = parser.parse_args(argv)

    findings = check_pack(args.pack, args.bundle_root, args.skill_name)
    if args.run_record and not findings:
        pack = _read_pack_for_run(args.pack)
        if pack is None:
            findings.append(_finding("eval-run-unbacked-result", "Pack could not be loaded for run validation."))
        else:
            findings.extend(check_run_record(args.run_record, args.bundle_root, pack))
    if args.format == "compact":
        print(json.dumps(_payload(findings), sort_keys=True))
    elif findings:
        for finding in findings:
            print(f"{finding['code']}: {finding['message']}")
    else:
        print("OK: eval pack and run record are valid.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
