"""Validate the portable internal subagent brief/result protocol.

This module is deliberately a protocol seam.  It validates structure,
repository-relative paths, hashes, budgets, and progress evidence.  It does
not select a worker, route a task, decide semantic acceptance, or perform a
retry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CONTRACT_VERSION = "internal-subagent-contract/v1"
MAX_ATTEMPTS = 2
MAX_CONTEXT_REFILLS = 1
MAX_CORRECTIVE_RETRIES = 1

BRIEF_FIELDS = frozenset(
    {
        "schema_version",
        "delegation_id",
        "mode",
        "objective",
        "value_gate",
        "evidence",
        "constraints",
        "write_scope",
        "expected_output",
        "acceptance",
        "validation",
        "budgets",
        "result_path",
        "cache",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "delegation_id",
        "brief_sha256",
        "status",
        "value_delivered",
        "summary",
        "artifacts",
        "evidence",
        "non_blocking_findings",
        "remaining",
        "progress_signature",
        "retry",
        "budgets_used",
    }
)

MODES = frozenset({"read", "write", "plan"})
STATUSES = frozenset(
    {"completed", "partial", "blocked", "stalled", "invalid_input", "failed"}
)
OUTPUT_KINDS = frozenset({"artifact", "analysis", "patch", "validation"})
OUTPUT_FORMATS = frozenset({"json", "markdown", "patch", "text"})
VALIDATION_OWNERS = frozenset({"worker", "caller"})
EVIDENCE_OUTCOMES = frozenset({"pass", "fail", "not_run"})
PROMPT_PREFIX_ORDER = (
    "role",
    "protocol",
    "schemas",
    "mode",
    "breakpoint",
    "brief",
    "retry",
)

_DELEGATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256 = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")


class ContractError(ValueError):
    """Raised by the assertion helpers when a payload is not valid."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def canonical_json(value: Any) -> bytes:
    """Return the compact, key-sorted UTF-8 JSON used by protocol hashes.

    The progress projection contains only JSON strings, booleans, arrays, and
    objects.  Those values are serialized with the RFC 8785-compatible
    compact/key-order rules needed by this protocol without adding a runtime
    dependency.
    """

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_bytes(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _normal_hash(value: object, label: str) -> str | None:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        return None
    return value.removeprefix("sha256:").lower()


def _hash_matches(actual: object, expected: object) -> bool:
    actual_hash = _normal_hash(actual, "actual")
    expected_hash = _normal_hash(expected, "expected")
    return actual_hash is not None and expected_hash is not None and actual_hash == expected_hash


def _is_bool(value: object) -> bool:
    return isinstance(value, bool)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _field_errors(value: object, expected: set[str] | frozenset[str], label: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    present = set(value)
    errors: list[str] = []
    for field in sorted(set(expected) - present):
        errors.append(f"{label} missing required field: {field}")
    for field in sorted(present - set(expected)):
        errors.append(f"{label} has unknown field: {field}")
    return errors


def _relative_path(value: object, label: str, repo_root: Path) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{label} must be a non-empty repository-relative path"]
    if "\\" in value:
        return [f"{label} must use repository-relative POSIX separators"]
    path = Path(value)
    if path.is_absolute() or value.startswith("//"):
        return [f"{label} must be repository-relative"]
    if ".." in path.parts:
        return [f"{label} must not traverse outside the repository"]
    try:
        resolved = (repo_root / path).resolve()
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return [f"{label} must remain inside the repository"]
    return []


def _scope_allows(path: str, scopes: Sequence[str]) -> bool:
    candidate = path.rstrip("/")
    for scope in scopes:
        root = scope.rstrip("/")
        if candidate == root or candidate.startswith(root + "/"):
            return True
    return False


def _list_of_strings(value: object, label: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        return [f"{label} must be a list"]
    errors = [f"{label} entries must be non-empty strings" for item in value if not _non_empty(item)]
    if not allow_empty and not value:
        errors.append(f"{label} must not be empty")
    return errors


def _unique_ids(items: Sequence[object], label: str) -> list[str]:
    ids: list[str] = []
    errors: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping) or not _non_empty(item.get("id")):
            errors.append(f"{label}[{index}].id must be a non-empty string")
            continue
        item_id = item["id"]
        assert isinstance(item_id, str)
        if item_id in ids:
            errors.append(f"{label} contains duplicate id: {item_id}")
        ids.append(item_id)
    return errors


def validate_value_gate(value: object) -> list[str]:
    errors = _field_errors(value, {"autonomous", "verifiable", "leverage"}, "value_gate")
    if errors:
        return errors
    assert isinstance(value, Mapping)
    if not _is_bool(value["autonomous"]) or not value["autonomous"]:
        errors.append("value_gate.autonomous must be true")
    if not _is_bool(value["verifiable"]) or not value["verifiable"]:
        errors.append("value_gate.verifiable must be true")
    if not _non_empty(value["leverage"]):
        errors.append("value_gate.leverage must explain material leverage")
    return errors


def validate_brief(brief: Mapping[str, object], *, repo_root: Path | None = None) -> list[str]:
    """Return structural and scope findings for a DelegationBrief v1."""

    root = (repo_root or Path.cwd()).resolve()
    errors = _field_errors(brief, BRIEF_FIELDS, "brief")
    if errors:
        return errors

    if brief["schema_version"] != 1 or not _is_int(brief["schema_version"]):
        errors.append("brief.schema_version must be integer 1")
    if not isinstance(brief["delegation_id"], str) or not _DELEGATION_ID.fullmatch(brief["delegation_id"]):
        errors.append("brief.delegation_id must be a stable identifier")
    if brief["mode"] not in MODES:
        errors.append(f"brief.mode must be one of: {', '.join(sorted(MODES))}")
    if not _non_empty(brief["objective"]):
        errors.append("brief.objective must be a non-empty measurable outcome")
    errors.extend(validate_value_gate(brief["value_gate"]))

    evidence = brief["evidence"]
    if not isinstance(evidence, list) or not evidence:
        errors.append("brief.evidence must be a non-empty list")
    else:
        for index, item in enumerate(evidence):
            errors.extend(_field_errors(item, {"ref", "purpose"}, f"brief.evidence[{index}]"))
            if isinstance(item, Mapping):
                if not _non_empty(item.get("ref")):
                    errors.append(f"brief.evidence[{index}].ref must be non-empty")
                if not _non_empty(item.get("purpose")):
                    errors.append(f"brief.evidence[{index}].purpose must be non-empty")

    errors.extend(_list_of_strings(brief["constraints"], "brief.constraints"))
    write_scope = brief["write_scope"]
    if not isinstance(write_scope, list):
        errors.append("brief.write_scope must be a list")
        write_scope = []
    for index, path in enumerate(write_scope):
        errors.extend(_relative_path(path, f"brief.write_scope[{index}]", root))
    if brief["mode"] == "read" and write_scope:
        errors.append("brief.write_scope must be empty for read mode")

    expected = brief["expected_output"]
    errors.extend(_field_errors(expected, {"kind", "path", "format"}, "brief.expected_output"))
    if isinstance(expected, Mapping):
        if expected.get("kind") not in OUTPUT_KINDS:
            errors.append("brief.expected_output.kind is invalid")
        if expected.get("format") not in OUTPUT_FORMATS:
            errors.append("brief.expected_output.format is invalid")
        output_path = expected.get("path")
        if output_path is not None:
            errors.extend(_relative_path(output_path, "brief.expected_output.path", root))
            if isinstance(output_path, str) and write_scope and not _scope_allows(output_path, write_scope):
                errors.append("brief.expected_output.path is outside write_scope")
        elif brief["mode"] != "read":
            errors.append("brief.expected_output.path is required for write and plan modes")
    elif isinstance(expected, Mapping):
        pass

    acceptance = brief["acceptance"]
    if not isinstance(acceptance, list) or not acceptance:
        errors.append("brief.acceptance must be a non-empty list")
    else:
        for index, item in enumerate(acceptance):
            errors.extend(_field_errors(item, {"id", "observable"}, f"brief.acceptance[{index}]"))
            if isinstance(item, Mapping) and not _non_empty(item.get("observable")):
                errors.append(f"brief.acceptance[{index}].observable must be non-empty")
        errors.extend(_unique_ids(acceptance, "brief.acceptance"))

    validation = brief["validation"]
    if not isinstance(validation, list) or not validation:
        errors.append("brief.validation must be a non-empty list")
    else:
        for index, item in enumerate(validation):
            errors.extend(
                _field_errors(
                    item,
                    {"id", "owner", "command", "pass_signal"},
                    f"brief.validation[{index}]",
                )
            )
            if isinstance(item, Mapping):
                if item.get("owner") not in VALIDATION_OWNERS:
                    errors.append(f"brief.validation[{index}].owner must be worker or caller")
                for field in ("id", "command", "pass_signal"):
                    if not _non_empty(item.get(field)):
                        errors.append(f"brief.validation[{index}].{field} must be non-empty")
        errors.extend(_unique_ids(validation, "brief.validation"))

    budgets = brief["budgets"]
    errors.extend(_field_errors(budgets, {"attempts", "context_refills"}, "brief.budgets"))
    if isinstance(budgets, Mapping):
        attempts = budgets.get("attempts")
        refills = budgets.get("context_refills")
        if not _is_int(attempts) or not 1 <= attempts <= MAX_ATTEMPTS:
            errors.append(f"brief.budgets.attempts must be between 1 and {MAX_ATTEMPTS}")
        if not _is_int(refills) or not 0 <= refills <= MAX_CONTEXT_REFILLS:
            errors.append(
                f"brief.budgets.context_refills must be between 0 and {MAX_CONTEXT_REFILLS}"
            )

    errors.extend(_relative_path(brief["result_path"], "brief.result_path", root))
    cache = brief["cache"]
    errors.extend(_field_errors(cache, {"prefix_version", "key_class"}, "brief.cache"))
    if isinstance(cache, Mapping):
        if cache.get("prefix_version") != CONTRACT_VERSION:
            errors.append(f"brief.cache.prefix_version must be {CONTRACT_VERSION}")
        if not _non_empty(cache.get("key_class")):
            errors.append("brief.cache.key_class must be non-empty")
    return errors


def _evidence_errors(
    evidence: object,
    acceptance_ids: set[str],
    label: str = "result.evidence",
) -> tuple[list[str], bool]:
    if not isinstance(evidence, list):
        return [f"{label} must be a list"], False
    errors: list[str] = []
    acceptance_pass = False
    for index, item in enumerate(evidence):
        if not isinstance(item, Mapping):
            errors.append(f"{label}[{index}] must be an object")
            continue
        keys = set(item)
        accepted_shapes = ({"acceptance_id", "ref", "outcome"}, {"kind", "ref", "outcome"})
        if keys not in accepted_shapes:
            errors.append(f"{label}[{index}] must use one exact evidence shape")
        if not _non_empty(item.get("ref")):
            errors.append(f"{label}[{index}].ref must be non-empty")
        if item.get("outcome") not in EVIDENCE_OUTCOMES:
            errors.append(f"{label}[{index}].outcome is invalid")
        if "acceptance_id" in item:
            acceptance_id = item.get("acceptance_id")
            if acceptance_id not in acceptance_ids:
                errors.append(f"{label}[{index}].acceptance_id is not declared by the brief")
            if item.get("outcome") == "pass":
                acceptance_pass = True
    return errors, acceptance_pass


def _progress_projection(result: Mapping[str, object]) -> dict[str, object]:
    artifacts: list[dict[str, str]] = []
    for item in result.get("artifacts", []) if isinstance(result.get("artifacts", []), list) else []:
        if isinstance(item, Mapping):
            digest = item.get("sha256")
            artifacts.append(
                {
                    "path": str(item.get("path", "")),
                    "sha256": str(digest).lower(),
                }
            )
    artifacts.sort(key=lambda item: (item["path"], item["sha256"]))

    evidence: list[dict[str, str]] = []
    for item in result.get("evidence", []) if isinstance(result.get("evidence", []), list) else []:
        if not isinstance(item, Mapping):
            continue
        projection = {
            "ref": str(item.get("ref", "")),
            "outcome": str(item.get("outcome", "")),
        }
        if "acceptance_id" in item:
            projection["acceptance_id"] = str(item.get("acceptance_id", ""))
        elif "kind" in item:
            projection["kind"] = str(item.get("kind", ""))
        evidence.append(projection)
    evidence.sort(key=lambda item: canonical_json(item))

    remaining = result.get("remaining", [])
    remaining_values = sorted(str(item) for item in remaining) if isinstance(remaining, list) else []
    retry = result.get("retry", {})
    required_new_input = retry.get("required_new_input") if isinstance(retry, Mapping) else None
    return {
        "status": result.get("status"),
        "artifacts": artifacts,
        "evidence": evidence,
        "remaining": remaining_values,
        "required_new_input": required_new_input,
    }


def compute_progress_signature(result: Mapping[str, object]) -> str:
    """Hash the canonical material-progress projection of a WorkerResult."""

    return sha256_bytes(canonical_json(_progress_projection(result)))


def compare_progress(previous: Mapping[str, object], current: Mapping[str, object]) -> str:
    return "stalled" if _progress_projection(previous) == _progress_projection(current) else "progressed"


def _acceptance_ids(brief: Mapping[str, object]) -> set[str]:
    acceptance = brief.get("acceptance", [])
    return {
        item["id"]
        for item in acceptance
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }


def validate_result(
    result: Mapping[str, object],
    brief: Mapping[str, object],
    *,
    repo_root: Path | None = None,
    brief_bytes: bytes | None = None,
    result_path: Path | str | None = None,
) -> list[str]:
    """Return binding and invariant findings for a WorkerResult v1."""

    root = (repo_root or Path.cwd()).resolve()
    errors = _field_errors(result, RESULT_FIELDS, "result")
    if errors:
        return errors
    errors.extend(validate_brief(brief, repo_root=root))

    if result["schema_version"] != 1 or not _is_int(result["schema_version"]):
        errors.append("result.schema_version must be integer 1")
    if result["delegation_id"] != brief.get("delegation_id"):
        errors.append("result.delegation_id must match brief.delegation_id")
    expected_brief_hash = sha256_bytes(brief_bytes) if brief_bytes is not None else sha256_bytes(canonical_json(brief))
    if not _hash_matches(result["brief_sha256"], expected_brief_hash):
        errors.append("result.brief_sha256 does not match the exact brief bytes")
    if result["status"] not in STATUSES:
        errors.append("result.status is invalid")
    if not _is_bool(result["value_delivered"]):
        errors.append("result.value_delivered must be boolean")
    if not _non_empty(result["summary"]):
        errors.append("result.summary must be non-empty")

    artifacts = result["artifacts"]
    if not isinstance(artifacts, list):
        errors.append("result.artifacts must be a list")
        artifacts = []
    seen_paths: set[str] = set()
    write_scope = brief.get("write_scope", [])
    for index, item in enumerate(artifacts):
        errors.extend(_field_errors(item, {"path", "sha256", "kind"}, f"result.artifacts[{index}]"))
        if not isinstance(item, Mapping):
            continue
        path = item.get("path")
        if isinstance(path, str):
            errors.extend(_relative_path(path, f"result.artifacts[{index}].path", root))
            if path in seen_paths:
                errors.append(f"result.artifacts contains duplicate path: {path}")
            seen_paths.add(path)
            if not isinstance(write_scope, list) or not _scope_allows(path, write_scope):
                errors.append(f"result.artifacts[{index}].path is outside brief.write_scope")
            artifact_path = root / path
            if not artifact_path.is_file():
                errors.append(f"result.artifacts[{index}] is missing: {path}")
            elif not _hash_matches(item.get("sha256"), sha256_path(artifact_path)):
                errors.append(f"result.artifacts[{index}] hash does not match file bytes")
        if not _non_empty(item.get("kind")):
            errors.append(f"result.artifacts[{index}].kind must be non-empty")

    evidence_errors, acceptance_pass = _evidence_errors(
        result["evidence"], _acceptance_ids(brief)
    )
    errors.extend(evidence_errors)
    errors.extend(_list_of_strings(result["non_blocking_findings"], "result.non_blocking_findings"))
    errors.extend(_list_of_strings(result["remaining"], "result.remaining"))

    signature = _normal_hash(result["progress_signature"], "result.progress_signature")
    if signature is None:
        errors.append("result.progress_signature must be a SHA-256 value")
    elif not _hash_matches(result["progress_signature"], compute_progress_signature(result)):
        errors.append("result.progress_signature does not match the canonical progress projection")

    retry = result["retry"]
    errors.extend(_field_errors(retry, {"recommended", "reason", "required_new_input"}, "result.retry"))
    if isinstance(retry, Mapping):
        if not _is_bool(retry.get("recommended")):
            errors.append("result.retry.recommended must be boolean")
        if not _non_empty(retry.get("reason")):
            errors.append("result.retry.reason must be non-empty")
        if retry.get("required_new_input") is not None and not _non_empty(retry.get("required_new_input")):
            errors.append("result.retry.required_new_input must be null or non-empty")
        if retry.get("recommended") and result.get("status") in {"completed", "blocked", "stalled", "invalid_input"}:
            errors.append("result.retry cannot reopen a terminal status")
        if retry.get("recommended") and result.get("non_blocking_findings"):
            errors.append("Minor or cosmetic non-blocking findings cannot reopen retry")

    budgets_used = result["budgets_used"]
    if not isinstance(budgets_used, Mapping):
        errors.append("result.budgets_used must be an object")
    else:
        allowed_budget_fields = {"wall_seconds", "attempts", "context_refills"}
        errors.extend(_field_errors(budgets_used, allowed_budget_fields, "result.budgets_used"))
        attempts = budgets_used.get("attempts")
        refills = budgets_used.get("context_refills")
        brief_budgets = brief.get("budgets", {})
        max_attempts = brief_budgets.get("attempts", MAX_ATTEMPTS) if isinstance(brief_budgets, Mapping) else MAX_ATTEMPTS
        max_refills = brief_budgets.get("context_refills", MAX_CONTEXT_REFILLS) if isinstance(brief_budgets, Mapping) else MAX_CONTEXT_REFILLS
        if not _is_int(attempts) or not 1 <= attempts <= max_attempts:
            errors.append("result.budgets_used.attempts exceeds brief budget")
        if not _is_int(refills) or not 0 <= refills <= min(max_refills, MAX_CONTEXT_REFILLS):
            errors.append("result.budgets_used.context_refills exceeds brief budget")
        if "wall_seconds" in budgets_used and (
            not _is_int(budgets_used["wall_seconds"]) or budgets_used["wall_seconds"] < 0
        ):
            errors.append("result.budgets_used.wall_seconds must be a non-negative integer")

    if result["value_delivered"] and not artifacts and not acceptance_pass:
        errors.append("result.value_delivered requires an artifact or acceptance-bound pass evidence")
    if result["status"] == "blocked" and isinstance(retry, Mapping) and retry.get("recommended"):
        errors.append("blocked results cannot recommend retry")
    if result_path is not None:
        supplied = Path(result_path)
        errors.extend(_relative_path(str(supplied), "result_path", root))
        if str(supplied) != str(brief.get("result_path")):
            errors.append("result_path must match brief.result_path")
    return errors


def retry_eligible(
    previous_brief: Mapping[str, object],
    next_brief: Mapping[str, object],
    previous_result: Mapping[str, object],
    next_result: Mapping[str, object],
) -> bool:
    """Check one caller-requested corrective transition without performing it."""

    if previous_result.get("status") in {"completed", "blocked", "stalled", "invalid_input"}:
        return False
    if previous_result.get("budgets_used", {}).get("attempts", 1) >= MAX_ATTEMPTS:
        return False
    if canonical_json(previous_brief) == canonical_json(next_brief):
        return False
    return compare_progress(previous_result, next_result) == "progressed"


def validate_prompt_order(labels: Sequence[str]) -> list[str]:
    """Validate the stable-before-dynamic prompt section order."""

    errors: list[str] = []
    if not isinstance(labels, Sequence) or isinstance(labels, (str, bytes)):
        return ["prompt sections must be a sequence"]
    unknown = [label for label in labels if label not in PROMPT_PREFIX_ORDER]
    if unknown:
        errors.append(f"unknown prompt sections: {', '.join(map(str, unknown))}")
    duplicates = {label for label in labels if labels.count(label) > 1}
    if duplicates:
        errors.append(f"prompt sections duplicated: {', '.join(sorted(duplicates))}")
    positions = [PROMPT_PREFIX_ORDER.index(label) for label in labels if label in PROMPT_PREFIX_ORDER]
    if positions != sorted(positions):
        errors.append("prompt sections must keep stable protocol content before dynamic brief/retry data")
    required = {"role", "protocol", "schemas", "mode", "brief"}
    missing = required - set(labels)
    if missing:
        errors.append(f"prompt sections missing required entries: {', '.join(sorted(missing))}")
    if "retry" in labels and "brief" in labels and labels.index("retry") < labels.index("brief"):
        errors.append("retry evidence must follow the dynamic brief")
    return errors


def _load_json(path: Path) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate internal-subagent-contract v1 payloads.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    brief = subparsers.add_parser("brief", help="Validate a DelegationBrief JSON file.")
    brief.add_argument("path", type=Path)
    brief.add_argument("--repo-root", type=Path, default=Path.cwd())
    result = subparsers.add_parser("result", help="Validate a WorkerResult JSON file against a brief.")
    result.add_argument("path", type=Path)
    result.add_argument("brief", type=Path)
    result.add_argument("--repo-root", type=Path, default=Path.cwd())
    progress = subparsers.add_parser("progress-signature", help="Print a result progress signature.")
    progress.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "brief":
        errors = validate_brief(_load_json(args.path), repo_root=args.repo_root)  # type: ignore[arg-type]
    elif args.command == "result":
        result = _load_json(args.path)
        brief = _load_json(args.brief)
        errors = validate_result(
            result,  # type: ignore[arg-type]
            brief,  # type: ignore[arg-type]
            repo_root=args.repo_root,
            brief_bytes=args.brief.read_bytes(),
        )
    else:
        print(compute_progress_signature(_load_json(args.path)))  # type: ignore[arg-type]
        return 0
    if errors:
        for error in errors:
            print(error)
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
