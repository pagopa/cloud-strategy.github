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
PACK_FIELDS = frozenset({"schema", "skill", "requirements", "cases", "triggers"})
REQUIREMENT_FIELDS = frozenset({"id", "text", "source"})
CASE_FIELDS = frozenset(
    {
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
        "status",
        "held_out",
    }
)
CASE_TEXT_FIELDS = ("family", "prompt", "initial_state", "expected_output")
ASSERTION_FIELDS = frozenset({"id", "text", "critical"})
QUERY_FIELDS = frozenset({"id", "query", "should_trigger", "split"})
RUN_FIELDS = frozenset(
    {"schema", "skill", "date", "host", "model", "configuration", "case_results"}
)
RESULT_FIELDS = frozenset({"case_id", "status", "assertions"})
VERDICT_FIELDS = frozenset({"id", "passed", "evidence"})
CASE_KINDS = frozenset({"deterministic", "rubric"})
PACK_STATUSES = frozenset({"generated", "not-run", "blocked"})
SPLITS = frozenset({"train", "held-out"})
CONFIGURATIONS = frozenset({"with-skill", "baseline-none", "baseline-previous"})
RUN_STATUSES = frozenset({"executed", "passed", "failed", "blocked"})
TRANSCRIPT_STATUSES = frozenset({"executed", "passed", "failed"})
IDENTIFIERS = {
    "requirement": re.compile(r"R-[A-Z0-9-]+"),
    "case": re.compile(r"C-[A-Z0-9-]+"),
    "query": re.compile(r"Q-[A-Z0-9-]+"),
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


def _has_exact_fields(value: Any, required: frozenset[str], optional: frozenset[str] = frozenset()) -> bool:
    return isinstance(value, dict) and required <= value.keys() and value.keys() <= required | optional


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _one_of(value: Any, allowed: Any) -> bool:
    return isinstance(value, str) and value in allowed


def _iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _safe_existing_file(bundle_root: Path, value: Any) -> bool:
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
    return resolved_path.is_file()


def _pack_from_path(pack_path: Path, findings: list[dict[str, str]]) -> Any:
    try:
        return _load_json(pack_path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKey) as exc:
        findings.append(_finding("eval-pack-invalid-json", f"Pack is not strict JSON: {exc}", pack_path))
        return None


def _validate_pack(pack: Any, bundle_root: Path, skill_name: str) -> list[dict[str, str]]:
    if not _has_exact_fields(pack, PACK_FIELDS) or pack["schema"] != PACK_SCHEMA or pack["skill"] != skill_name:
        return [_finding("eval-pack-schema", "Pack top-level fields, schema, or skill name are invalid.")]
    requirements, cases, triggers = pack["requirements"], pack["cases"], pack["triggers"]
    if not isinstance(requirements, list) or not requirements or not isinstance(cases, list) or not cases:
        return [_finding("eval-pack-schema", "Requirements and cases must be non-empty lists.")]
    if not _has_exact_fields(triggers, frozenset({"queries"})) or not isinstance(triggers["queries"], list):
        return [_finding("eval-pack-schema", "Triggers must contain a queries list.")]

    findings: list[dict[str, str]] = []
    all_ids: set[str] = set()
    requirement_ids: set[str] = set()
    covered_requirements: set[str] = set()

    def add_unique(identifier: Any, category: str) -> bool:
        if not isinstance(identifier, str) or not IDENTIFIERS[category].fullmatch(identifier):
            findings.append(_finding("eval-pack-schema", f"Invalid {category} identifier: {identifier!r}"))
            return False
        if identifier in all_ids:
            findings.append(_finding("eval-pack-duplicate-id", f"Duplicate identifier: {identifier}"))
            return False
        all_ids.add(identifier)
        return True

    for item in requirements:
        if not _has_exact_fields(item, REQUIREMENT_FIELDS) or not all(_nonempty_string(item[field]) for field in REQUIREMENT_FIELDS):
            findings.append(_finding("eval-pack-schema", "Requirement entries need id, text, and source strings."))
            continue
        if add_unique(item["id"], "requirement"):
            requirement_ids.add(item["id"])

    for case in cases:
        kind = case.get("kind") if isinstance(case, dict) else None
        optional = frozenset({"defective_fixture"} if kind == "deterministic" else {"rubric"})
        if not _one_of(kind, CASE_KINDS) or not _has_exact_fields(case, CASE_FIELDS, optional):
            findings.append(_finding("eval-pack-schema", "Case fields or kind are invalid."))
            continue
        add_unique(case["id"], "case")
        label = case["id"] if isinstance(case["id"], str) else "<invalid>"
        if not all(_nonempty_string(case[field]) for field in CASE_TEXT_FIELDS):
            findings.append(_finding("eval-pack-schema", f"Case {label} has an empty text field."))
        reqs = case["requirement_ids"]
        if not isinstance(reqs, list) or not reqs:
            findings.append(_finding("eval-pack-schema", f"Case {label} needs requirement IDs."))
        else:
            for req_id in reqs:
                if _one_of(req_id, requirement_ids):
                    covered_requirements.add(req_id)
                else:
                    findings.append(_finding("eval-pack-unresolved-requirement", f"Unknown requirement {req_id!r}."))
        if not isinstance(case["files"], list) or not all(_safe_existing_file(bundle_root, item) for item in case["files"]):
            findings.append(_finding("eval-pack-unsafe-path", f"Case {label} has an unsafe or missing file path."))
        assertions = case["assertions"]
        if not isinstance(assertions, list) or not assertions:
            findings.append(_finding("eval-pack-schema", f"Case {label} needs assertions."))
        else:
            assertion_ids: set[str] = set()
            for assertion in assertions:
                if (
                    not _has_exact_fields(assertion, ASSERTION_FIELDS)
                    or not _nonempty_string(assertion["id"])
                    or not _nonempty_string(assertion["text"])
                    or not isinstance(assertion["critical"], bool)
                ):
                    findings.append(_finding("eval-pack-schema", f"Case {label} has an invalid assertion."))
                elif assertion["id"] in assertion_ids:
                    findings.append(_finding("eval-pack-duplicate-id", f"Duplicate assertion identifier {assertion['id']} in {label}."))
                else:
                    assertion_ids.add(assertion["id"])
        if not isinstance(case["forbidden_actions"], list) or not all(_nonempty_string(item) for item in case["forbidden_actions"]):
            findings.append(_finding("eval-pack-schema", f"Case {label} has invalid forbidden actions."))
        if not _one_of(case["status"], PACK_STATUSES):
            findings.append(_finding("eval-pack-invalid-status", f"Case {label} has an invalid evidence status."))
        if not isinstance(case["held_out"], bool):
            findings.append(_finding("eval-pack-schema", f"Case {label} held_out must be boolean."))
        if kind == "deterministic":
            if "defective_fixture" not in case:
                findings.append(_finding("eval-pack-missing-defective-fixture", f"Deterministic case {label} has no defective fixture."))
            elif not _safe_existing_file(bundle_root, case["defective_fixture"]):
                findings.append(_finding("eval-pack-unsafe-path", f"Case {label} has an unsafe or missing defective fixture."))
        elif "rubric" not in case:
            findings.append(_finding("eval-pack-missing-rubric", f"Rubric case {label} has no rubric."))
        elif not _has_exact_fields(case["rubric"], frozenset({"pass", "fail"})) or not all(
            isinstance(case["rubric"][key], list)
            and case["rubric"][key]
            and all(_nonempty_string(anchor) for anchor in case["rubric"][key])
            for key in ("pass", "fail")
        ):
            findings.append(_finding("eval-pack-missing-rubric", f"Rubric case {label} has no anchored pass/fail rubric."))

    if requirement_ids - covered_requirements:
        findings.append(_finding("eval-pack-uncovered-requirement", "One or more requirements have no case coverage."))

    polarities: set[bool] = set()
    splits: set[str] = set()
    for query in triggers["queries"]:
        if (
            not _has_exact_fields(query, QUERY_FIELDS, frozenset({"competing_owner"}))
            or not _nonempty_string(query["query"])
            or not isinstance(query["should_trigger"], bool)
            or not _one_of(query["split"], SPLITS)
        ):
            findings.append(_finding("eval-pack-trigger-coverage", "A trigger query has invalid fields."))
            continue
        if add_unique(query["id"], "query"):
            polarities.add(query["should_trigger"])
            splits.add(query["split"])
        if "competing_owner" in query and not _nonempty_string(query["competing_owner"]):
            findings.append(_finding("eval-pack-schema", "A trigger query has an empty competing owner."))
    if polarities != {True, False} or splits != set(SPLITS):
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


def check_run_record(record_path: Path, pack: dict[str, Any]) -> list[dict[str, str]]:
    """Validate a run record against the exact cases and assertions in a pack."""
    try:
        record = _load_json(Path(record_path))
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKey) as exc:
        return [_finding("eval-run-unbacked-result", f"Run record is not valid strict JSON: {exc}", Path(record_path))]
    if (
        not _has_exact_fields(record, RUN_FIELDS)
        or record["schema"] != RUN_SCHEMA
        or record["skill"] != pack.get("skill")
        or not _iso_date(record["date"])
        or not _nonempty_string(record["host"])
        or not _nonempty_string(record["model"])
        or not _one_of(record["configuration"], CONFIGURATIONS)
        or not isinstance(record["case_results"], list)
    ):
        return [_finding("eval-run-unbacked-result", "Run record metadata or fields are invalid.", Path(record_path))]
    cases = {case["id"]: case for case in pack.get("cases", []) if isinstance(case, dict) and isinstance(case.get("id"), str)}
    findings: list[dict[str, str]] = []
    seen: set[str] = set()
    for result in record["case_results"]:
        if not _has_exact_fields(result, RESULT_FIELDS, frozenset({"transcript_ref"})):
            findings.append(_finding("eval-run-unbacked-result", "Run case result fields are invalid."))
            continue
        case_id, status = result["case_id"], result["status"]
        if not _one_of(case_id, cases) or not _one_of(status, RUN_STATUSES):
            findings.append(_finding("eval-run-unbacked-result", f"Run result is not backed by a pack case: {case_id!r}"))
            continue
        if case_id in seen:
            findings.append(_finding("eval-run-unbacked-result", f"Duplicate run result for {case_id}."))
            continue
        seen.add(case_id)
        if status in TRANSCRIPT_STATUSES and not _nonempty_string(result.get("transcript_ref")):
            findings.append(_finding("eval-run-unbacked-result", f"{status} result for {case_id} has no transcript reference."))
        declared = {
            item["id"]: item
            for item in cases[case_id].get("assertions", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        verdicts = result["assertions"]
        if not isinstance(verdicts, list) or not all(
            _has_exact_fields(item, VERDICT_FIELDS)
            and isinstance(item["id"], str)
            and isinstance(item["passed"], bool)
            and isinstance(item["evidence"], str)
            for item in verdicts
        ):
            findings.append(_finding("eval-run-assertion-mismatch", f"Run assertions for {case_id} are malformed."))
            continue
        actual = [item["id"] for item in verdicts]
        if len(actual) != len(set(actual)) or set(actual) != set(declared):
            findings.append(_finding("eval-run-assertion-mismatch", f"Run assertions do not match case {case_id} exactly."))
            continue
        if status == "passed" and not all(item["passed"] and _nonempty_string(item["evidence"]) for item in verdicts):
            findings.append(_finding("eval-run-unbacked-result", f"Passed result for {case_id} lacks passing assertion evidence."))
        if status == "executed" and any(declared[item["id"]].get("critical") is True and not item["passed"] for item in verdicts):
            findings.append(_finding("eval-run-unbacked-result", f"A failed critical assertion requires status failed for {case_id}."))
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
            findings.extend(check_run_record(args.run_record, pack))
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
