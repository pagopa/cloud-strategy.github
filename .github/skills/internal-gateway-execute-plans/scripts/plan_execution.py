#!/usr/bin/env python3
"""Read-only validator for retained plans and JSON resume state."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: Literal["blocking", "notice"] = "blocking"


MANIFEST_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1
STATE_STATUSES = frozenset({"DONE", "PARTIAL", "BLOCKED"})
MANIFEST_CONTROL_CLASSES = frozenset(
    {
        "automatable-local",
        "observable-runtime",
        "external-capability",
        "authority-or-scope",
        "genuine-human-judgment",
    }
)
MANIFEST_POSTURES = frozenset(
    {"mandatory-test-first", "feature-first", "prototype-unverified", "validation-only"}
)
MANIFEST_TARGET_STATES = frozenset({"create", "modify", "inspect"})
MANIFEST_BOOTSTRAP_MODES = frozenset({"explicit-single-plan", "manifest-only"})
MANIFEST_PHASES = frozenset({"baseline", "focused", "final"})
MANIFEST_EQUIVALENCE = frozenset({"exact-only", "allowed-if-admissible"})
MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "manifest_version",
        "plan_id",
        "repository_root",
        "authority_boundaries",
        "targets",
        "controls",
        "validations",
        "manual_obligations",
        "tasks",
        "retry_policy",
        "hashing",
        "approval",
        "bootstrap",
        "rollout",
        "handoff",
    }
)
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")

TASK_HEADING_RE = re.compile(r"(?im)^#{2,6}\s+Task(?:\s+\d+)?(?:\s*:|\b)")
UNCHECKED_TASK_RE = re.compile(r"(?m)^\s*[-*]\s+\[\s\]\s+\S")
PLAN_HEADING_ALIASES = {
    "Repository Preflight": ("Repository Preflight", "Preflight", "Preflight Gate"),
}
REQUIRED_PLAN_HEADINGS = ("Goal", "Global Constraints")
REQUIRED_EXECUTION_FIELDS = (
    "Baseline Validation",
    "Recovery Policy",
    "Escalation Conditions",
    "User-Facing Report",
)
STATE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "plan",
        "plan_fingerprint",
        "content_hash",
        "completed_task_ids",
        "remaining_task_ids",
        "last_validation",
        "next_action",
    }
)


class ExecutionContractError(ValueError):
    """A parse error with a stable preflight finding code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def canonical_json(value: object) -> bytes:
    """Serialize manifest values using compact, sorted-key JSON for JCS inputs."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _reject_duplicate_json_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _contains_embedded_digest(value: object, path: str = "") -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if key in {"content_sha256", "semantic_fingerprint"} and isinstance(child, str):
                if SHA256_RE.fullmatch(child):
                    return True
            if _contains_embedded_digest(child, child_path):
                return True
    elif isinstance(value, list):
        return any(_contains_embedded_digest(item, path) for item in value)
    return False


def compute_semantic_fingerprint(manifest: Mapping[str, object]) -> str:
    """Return the external SHA-256 of the canonical Execution Manifest JSON."""

    if _contains_embedded_digest(manifest):
        raise ExecutionContractError(
            "manifest-hash-self-reference",
            "Execution Manifest must not contain a content or semantic digest value",
        )
    return f"sha256:{hashlib.sha256(canonical_json(manifest)).hexdigest()}"


def _manifest_exact_fields(
    mapping: Mapping[str, object], expected: set[str] | frozenset[str], label: str
) -> None:
    unknown = set(mapping) - set(expected)
    missing = set(expected) - set(mapping)
    if unknown:
        raise ExecutionContractError(
            "unknown-manifest-field",
            f"{label} has unknown fields: {sorted(unknown)}",
        )
    if missing:
        raise ExecutionContractError(
            "missing-manifest-field",
            f"{label} is missing fields: {sorted(missing)}",
        )


def _manifest_object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _manifest_non_empty_strings(value: object, label: str) -> tuple[str, ...]:
    return _strings(value, label, allow_empty=False)


def _manifest_id_list(value: object, label: str) -> tuple[str, ...]:
    values = _strings(value, label, allow_empty=True)
    if len(set(values)) != len(values):
        raise ValueError(f"{label} must not contain duplicate ids")
    return values


def _manifest_fenced_object(text: str, heading: str) -> Mapping[str, object]:
    matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\s*$", text))
    if not matches:
        raise ExecutionContractError(
            "missing-execution-manifest",
            f"Plan must contain exactly one ## {heading}",
        )
    if len(matches) > 1:
        raise ExecutionContractError(
            "duplicate-execution-manifest",
            f"Plan must contain only one ## {heading}",
        )
    start = matches[0].end()
    next_heading = re.search(r"(?m)^#{2,6}\s+", text[start:])
    body = text[start : start + next_heading.start()] if next_heading else text[start:]
    fenced = re.fullmatch(r"\s*```json\s*\n(.*?)\n```\s*", body, re.DOTALL)
    if not fenced:
        raise ExecutionContractError(
            "malformed-execution-manifest",
            f"{heading} must contain exactly one immediately contained ```json fenced object",
        )
    try:
        raw = json.loads(fenced.group(1), object_pairs_hook=_reject_duplicate_json_fields)
    except ValueError as exc:
        message = str(exc)
        code = "duplicate-manifest-field" if message.startswith("duplicate JSON field") else "malformed-execution-manifest"
        raise ExecutionContractError(code, f"{heading} JSON is malformed: {message}") from exc
    return _manifest_object(raw, heading)


def parse_execution_manifest(text: str) -> dict[str, object]:
    """Parse and validate exactly one normative Execution Manifest object."""

    root = _manifest_fenced_object(text, "Execution Manifest")
    _manifest_exact_fields(root, MANIFEST_FIELDS, "Execution Manifest")
    try:
        if not _is_int(root["schema_version"]) or root["schema_version"] != MANIFEST_SCHEMA_VERSION:
            raise ExecutionContractError(
                "unsupported-manifest-schema",
                f"Execution Manifest schema_version must be {MANIFEST_SCHEMA_VERSION}",
            )
        if not _non_empty_string(root["manifest_version"]) or root["manifest_version"] != "execution-manifest/v1":
            raise ValueError("manifest_version must be execution-manifest/v1")
        if not _non_empty_string(root["plan_id"]):
            raise ValueError("plan_id must be non-empty")
        if root["repository_root"] != ".":
            raise ValueError("repository_root must be .")

        authority = _manifest_object(root["authority_boundaries"], "authority_boundaries")
        _manifest_exact_fields(
            authority,
            {"normative_owner", "execution_owner", "worker", "caller_owns", "protected_paths", "no_git_mutation"},
            "authority_boundaries",
        )
        if not _non_empty_string(authority["normative_owner"]) or not _non_empty_string(authority["execution_owner"]):
            raise ValueError("authority owners must be non-empty")
        if not _non_empty_string(authority["worker"]):
            raise ValueError("authority_boundaries.worker must be non-empty")
        _manifest_non_empty_strings(authority["caller_owns"], "authority_boundaries.caller_owns")
        _manifest_non_empty_strings(authority["protected_paths"], "authority_boundaries.protected_paths")
        if not _bool(authority["no_git_mutation"], "authority_boundaries.no_git_mutation"):
            raise ValueError("authority_boundaries.no_git_mutation must be true")

        targets = root["targets"]
        if not isinstance(targets, list) or not targets:
            raise ValueError("targets must be a non-empty list")
        target_ids: set[str] = set()
        for index, raw_target in enumerate(targets):
            label = f"targets[{index}]"
            target = _manifest_object(raw_target, label)
            keys = {"id", "path", "state", "condition"} if "condition" in target else {"id", "path", "state"}
            _manifest_exact_fields(target, keys, label)
            target_id = _string(target["id"], f"{label}.id")
            if target_id in target_ids:
                raise ValueError(f"duplicate target id: {target_id}")
            target_ids.add(target_id)
            _string(target["path"], f"{label}.path")
            if target["state"] not in MANIFEST_TARGET_STATES:
                raise ValueError(f"{label}.state is invalid")
            if "condition" in target:
                _string(target["condition"], f"{label}.condition")

        controls = _manifest_object(root["controls"], "controls")
        if not controls:
            raise ValueError("controls must not be empty")
        for control_id, raw_control in controls.items():
            label = f"controls.{control_id}"
            control = _manifest_object(raw_control, label)
            _manifest_exact_fields(control, {"class", "owner", "binding"}, label)
            if control["class"] not in MANIFEST_CONTROL_CLASSES:
                raise ValueError(f"{label}.class is invalid")
            _string(control["owner"], f"{label}.owner")
            _manifest_non_empty_strings(control["binding"], f"{label}.binding")

        validations = root["validations"]
        if not isinstance(validations, list) or not validations:
            raise ValueError("validations must be a non-empty list")
        validation_ids: set[str] = set()
        for index, raw_validation in enumerate(validations):
            label = f"validations[{index}]"
            validation = _manifest_object(raw_validation, label)
            validation_fields = {"id", "command", "owner", "pass_signal", "phases"}
            if "equivalence" in validation:
                validation_fields.add("equivalence")
            _manifest_exact_fields(validation, validation_fields, label)
            validation_id = _string(validation["id"], f"{label}.id")
            if validation_id in validation_ids:
                raise ExecutionContractError(
                    "duplicate-validation-id",
                    f"Duplicate validation id: {validation_id}",
                )
            validation_ids.add(validation_id)
            _string(validation["command"], f"{label}.command")
            _string(validation["owner"], f"{label}.owner")
            _string(validation["pass_signal"], f"{label}.pass_signal")
            phases = _manifest_non_empty_strings(validation["phases"], f"{label}.phases")
            if any(phase not in MANIFEST_PHASES for phase in phases):
                raise ValueError(f"{label}.phases contains an unsupported phase")
            if "equivalence" in validation and validation["equivalence"] not in MANIFEST_EQUIVALENCE:
                raise ValueError(f"{label}.equivalence is invalid")

        manual = root["manual_obligations"]
        if not isinstance(manual, list):
            raise ValueError("manual_obligations must be a list")
        manual_ids: set[str] = set()
        for index, raw_obligation in enumerate(manual):
            label = f"manual_obligations[{index}]"
            obligation = _manifest_object(raw_obligation, label)
            _manifest_exact_fields(obligation, {"id", "kind", "required", "acceptance"}, label)
            obligation_id = _string(obligation["id"], f"{label}.id")
            if obligation_id in manual_ids:
                raise ValueError(f"duplicate manual obligation id: {obligation_id}")
            manual_ids.add(obligation_id)
            if obligation["kind"] not in {"human", "external"}:
                raise ValueError(f"{label}.kind is invalid")
            _bool(obligation["required"], f"{label}.required")
            _string(obligation["acceptance"], f"{label}.acceptance")

        tasks = root["tasks"]
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("tasks must be a non-empty list")
        task_ids: set[str] = set()
        orders: set[int] = set()
        for index, raw_task in enumerate(tasks):
            label = f"tasks[{index}]"
            task = _manifest_object(raw_task, label)
            _manifest_exact_fields(
                task,
                {"id", "order", "posture", "objective", "depends_on", "target_ids", "validation_ids", "manual_obligation_ids", "acceptance", "stop_conditions"},
                label,
            )
            task_id = _string(task["id"], f"{label}.id")
            if task_id in task_ids:
                raise ValueError(f"duplicate task id: {task_id}")
            task_ids.add(task_id)
            if not _is_int(task["order"]) or task["order"] < 1 or task["order"] in orders:
                raise ValueError(f"{label}.order must be a unique positive integer")
            orders.add(task["order"])
            if task["posture"] not in MANIFEST_POSTURES:
                raise ValueError(f"{label}.posture is invalid")
            _string(task["objective"], f"{label}.objective")
            _manifest_id_list(task["depends_on"], f"{label}.depends_on")
            _manifest_id_list(task["target_ids"], f"{label}.target_ids")
            _manifest_id_list(task["validation_ids"], f"{label}.validation_ids")
            _manifest_id_list(task["manual_obligation_ids"], f"{label}.manual_obligation_ids")
            _manifest_non_empty_strings(task["acceptance"], f"{label}.acceptance")
            _manifest_non_empty_strings(task["stop_conditions"], f"{label}.stop_conditions")

        retry = _manifest_object(root["retry_policy"], "retry_policy")
        _manifest_exact_fields(retry, {"initial_attempts", "max_context_refills", "max_corrective_retries", "caller_may_lower", "repeat_progress_status", "minor_or_cosmetic_reopens"}, "retry_policy")
        for field in ("initial_attempts", "max_context_refills", "max_corrective_retries"):
            if not _is_int(retry[field]) or retry[field] < 0:
                raise ValueError(f"retry_policy.{field} must be a non-negative integer")
        if retry["initial_attempts"] != 1 or retry["max_context_refills"] != 1 or retry["max_corrective_retries"] != 1:
            raise ValueError("retry_policy must retain one initial attempt, one refill, and one corrective retry")
        _bool(retry["caller_may_lower"], "retry_policy.caller_may_lower")
        if retry["repeat_progress_status"] != "stalled":
            raise ValueError("retry_policy.repeat_progress_status must be stalled")
        if retry["minor_or_cosmetic_reopens"] is not False:
            raise ValueError("retry_policy.minor_or_cosmetic_reopens must be false")

        hashing = _manifest_object(root["hashing"], "hashing")
        _manifest_exact_fields(hashing, {"content_sha256", "semantic_fingerprint", "self_reference"}, "hashing")
        content_hash = _manifest_object(hashing["content_sha256"], "hashing.content_sha256")
        semantic_hash = _manifest_object(hashing["semantic_fingerprint"], "hashing.semantic_fingerprint")
        _manifest_exact_fields(content_hash, {"algorithm", "input", "binding"}, "hashing.content_sha256")
        _manifest_exact_fields(semantic_hash, {"algorithm", "input", "version", "binding"}, "hashing.semantic_fingerprint")
        if content_hash["algorithm"] != "SHA-256" or semantic_hash["algorithm"] != "SHA-256":
            raise ValueError("hashing algorithms must be SHA-256")
        _string(content_hash["input"], "hashing.content_sha256.input")
        _string(semantic_hash["input"], "hashing.semantic_fingerprint.input")
        if content_hash["binding"] != "external" or semantic_hash["binding"] != "external":
            raise ValueError("hashing bindings must be external")
        _string(semantic_hash["version"], "hashing.semantic_fingerprint.version")
        if hashing["self_reference"] is not False:
            raise ValueError("hashing.self_reference must be false")
        compute_semantic_fingerprint(root)

        approval = _manifest_object(root["approval"], "approval")
        _manifest_exact_fields(approval, {"binds", "editorial_content_change", "normative_manifest_change"}, "approval")
        if approval["binds"] != "semantic_fingerprint":
            raise ValueError("approval.binds must be semantic_fingerprint")
        _string(approval["editorial_content_change"], "approval.editorial_content_change")
        _string(approval["normative_manifest_change"], "approval.normative_manifest_change")

        bootstrap = _manifest_object(root["bootstrap"], "bootstrap")
        _manifest_exact_fields(bootstrap, {"mode", "compatibility_projection", "projection_binding", "legacy_only", "retirement_evidence"}, "bootstrap")
        mode = _string(bootstrap["mode"], "bootstrap.mode")
        if mode not in MANIFEST_BOOTSTRAP_MODES:
            raise ValueError("bootstrap.mode is invalid")
        projection = _strings(bootstrap["compatibility_projection"], "bootstrap.compatibility_projection")
        if mode == "explicit-single-plan" and projection != (
            "Control Inventory",
            "Task headings",
            "Execution Contract",
        ):
            raise ValueError("bootstrap.compatibility_projection is not the supported projection")
        if mode == "manifest-only" and projection:
            raise ValueError("manifest-only plans must not emit a compatibility projection")
        binding = _manifest_object(bootstrap["projection_binding"], "bootstrap.projection_binding")
        _manifest_exact_fields(binding, {"controls", "tasks", "validations", "authority"}, "bootstrap.projection_binding")
        if dict(binding) != {"controls": "manifest.controls", "tasks": "manifest.tasks", "validations": "manifest.validations", "authority": "manifest.authority_boundaries"}:
            raise ValueError("bootstrap.projection_binding is conflicting")
        if bootstrap["legacy_only"] != "reject":
            raise ValueError("bootstrap.legacy_only must be reject")
        _string(bootstrap["retirement_evidence"], "bootstrap.retirement_evidence")

        _manifest_non_empty_strings(root["rollout"], "rollout")
        handoff = _manifest_object(root["handoff"], "handoff")
        _manifest_exact_fields(handoff, {"next_owner", "requires", "status_sibling", "git_mutation"}, "handoff")
        if handoff["next_owner"] != "/internal-gateway-execute-plans":
            raise ValueError("handoff.next_owner must be /internal-gateway-execute-plans")
        requires = _manifest_non_empty_strings(handoff["requires"], "handoff.requires")
        for required in ("human approval", "exact semantic_fingerprint review", "zero blocking preflight findings"):
            if required not in requires:
                raise ValueError(f"handoff.requires is missing {required}")
        if handoff["status_sibling"] != "none" or handoff["git_mutation"] != "prohibited":
            raise ValueError("handoff must prohibit status sibling and Git mutation")
    except ExecutionContractError:
        raise
    except (TypeError, ValueError) as exc:
        raise ExecutionContractError("malformed-execution-manifest", str(exc)) from exc
    return dict(root)


def _parse_bootstrap_projection(
    text: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Read only the validation and manual IDs needed for bootstrap drift checks."""

    root = _manifest_fenced_object(text, "Execution Contract")
    raw_validations = root.get("validations")
    raw_manual_obligations = root.get("manual_obligations", [])
    if not isinstance(raw_validations, list) or not isinstance(raw_manual_obligations, list):
        raise ExecutionContractError(
            "malformed-execution-contract",
            "Execution Contract projection must contain validation and manual-obligation lists",
        )
    validations: list[dict[str, object]] = []
    validation_ids: set[str] = set()
    for index, raw_validation in enumerate(raw_validations):
        validation = _manifest_object(raw_validation, f"Execution Contract validations[{index}]")
        validation_id = _string(validation.get("id"), "Execution Contract validation id")
        if validation_id in validation_ids:
            raise ExecutionContractError(
                "duplicate-execution-contract-validation-id",
                f"Duplicate Execution Contract validation id: {validation_id}",
            )
        validation_ids.add(validation_id)
        validations.append(
            {
                "id": validation_id,
                "command": _string(validation.get("command"), "Execution Contract validation command"),
                "phases": list(_manifest_non_empty_strings(validation.get("phases"), "Execution Contract validation phases")),
            }
        )
    manual_obligations: list[dict[str, object]] = []
    manual_ids: set[str] = set()
    for index, raw_obligation in enumerate(raw_manual_obligations):
        obligation = _manifest_object(raw_obligation, f"Execution Contract manual_obligations[{index}]")
        obligation_id = _string(obligation.get("id"), "Execution Contract manual obligation id")
        if obligation_id in manual_ids:
            raise ExecutionContractError(
                "duplicate-execution-contract-manual-id",
                f"Duplicate Execution Contract manual obligation id: {obligation_id}",
            )
        manual_ids.add(obligation_id)
        manual_obligations.append(
            {"id": obligation_id}
        )
    return validations, manual_obligations


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _strings(value: object, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"{label} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise ValueError(f"{label} must not be empty")
    return tuple(item.strip() for item in value)


def _exact_fields(mapping: Mapping[str, object], expected: set[str], label: str) -> None:
    unknown = set(mapping) - expected
    missing = expected - set(mapping)
    if unknown or missing:
        details: list[str] = []
        if unknown:
            details.append(f"unknown fields: {sorted(unknown)}")
        if missing:
            details.append(f"missing fields: {sorted(missing)}")
        raise ValueError(f"{label} is malformed ({'; '.join(details)})")


def compute_sha256(path: Path) -> str:
    return compute_content_sha256(path)


def compute_content_sha256(path: Path) -> str:
    """Hash the exact retained-plan bytes for external audit binding."""

    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


@dataclass(frozen=True)
class ResumeState:
    schema_version: Literal[1]
    status: Literal["DONE", "PARTIAL", "BLOCKED"]
    plan: str
    plan_fingerprint: str
    content_hash: str
    completed_task_ids: tuple[str, ...]
    remaining_task_ids: tuple[str, ...]
    last_validation: str
    next_action: str


def state_path_for(plan_path: Path) -> Path:
    """Return the one JSON resume sibling for a retained plan."""

    return plan_path.with_suffix(".status.json")


def _manifest_task_ids(manifest: Mapping[str, object]) -> tuple[str, ...]:
    tasks = manifest["tasks"]
    if not isinstance(tasks, list):
        raise ExecutionContractError("malformed-execution-manifest", "Manifest tasks must be a list")
    return tuple(
        item["id"]
        for item in sorted(tasks, key=lambda value: value["order"])
        if isinstance(item, Mapping)
    )


def parse_resume_state(payload: Mapping[str, object]) -> ResumeState:
    """Parse the strict, hash-bound state persisted by the execution gateway."""

    mapping = _mapping(payload, "resume state")
    _exact_fields(mapping, set(STATE_FIELDS), "resume state")
    if not _is_int(mapping["schema_version"]) or mapping["schema_version"] != STATE_SCHEMA_VERSION:
        raise ExecutionContractError(
            "unsupported-state-schema",
            f"resume state schema_version must be {STATE_SCHEMA_VERSION}",
        )
    status = _string(mapping["status"], "resume state.status")
    if status not in STATE_STATUSES:
        raise ExecutionContractError(
            "unknown-status",
            f"resume state.status must be one of {sorted(STATE_STATUSES)}",
        )
    plan_fingerprint = _string(mapping["plan_fingerprint"], "resume state.plan_fingerprint")
    content_hash = _string(mapping["content_hash"], "resume state.content_hash")
    if not SHA256_RE.fullmatch(plan_fingerprint):
        raise ExecutionContractError("invalid-plan-fingerprint", "resume state.plan_fingerprint must be a SHA-256 digest")
    if not SHA256_RE.fullmatch(content_hash):
        raise ExecutionContractError("invalid-content-hash", "resume state.content_hash must be a SHA-256 digest")
    completed = _strings(mapping["completed_task_ids"], "resume state.completed_task_ids")
    remaining = _strings(mapping["remaining_task_ids"], "resume state.remaining_task_ids")
    if len(set(completed)) != len(completed) or len(set(remaining)) != len(remaining):
        raise ExecutionContractError("duplicate-task-id", "resume state task IDs must be unique")
    if set(completed) & set(remaining):
        raise ExecutionContractError("task-progress-overlap", "resume state completed and remaining tasks must not overlap")
    return ResumeState(
        STATE_SCHEMA_VERSION,
        status,  # type: ignore[arg-type]
        _string(mapping["plan"], "resume state.plan"),
        plan_fingerprint,
        content_hash,
        completed,
        remaining,
        _string(mapping["last_validation"], "resume state.last_validation"),
        _string(mapping["next_action"], "resume state.next_action"),
    )


def build_resume_state(
    plan_path: Path,
    status: str,
    completed_task_ids: list[str] | tuple[str, ...],
    remaining_task_ids: list[str] | tuple[str, ...],
    last_validation: str,
    next_action: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Build a bound state payload without executing or choosing plan work."""

    manifest = parse_execution_manifest(plan_path.read_text())
    root = repo_root or _find_repo_root(plan_path)
    try:
        plan_reference = plan_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("plan must be inside the repository root") from exc
    payload: dict[str, object] = {
        "schema_version": STATE_SCHEMA_VERSION,
        "status": status,
        "plan": plan_reference,
        "plan_fingerprint": compute_semantic_fingerprint(manifest),
        "content_hash": compute_content_sha256(plan_path),
        "completed_task_ids": list(completed_task_ids),
        "remaining_task_ids": list(remaining_task_ids),
        "last_validation": last_validation,
        "next_action": next_action,
    }
    parse_resume_state(payload)
    return payload


def write_resume_state(path: Path, payload: Mapping[str, object]) -> None:
    """Serialize validated state; approval and execution remain gateway-owned."""

    state = parse_resume_state(payload)
    path.write_text(
        json.dumps(
            {
                "schema_version": state.schema_version,
                "status": state.status,
                "plan": state.plan,
                "plan_fingerprint": state.plan_fingerprint,
                "content_hash": state.content_hash,
                "completed_task_ids": list(state.completed_task_ids),
                "remaining_task_ids": list(state.remaining_task_ids),
                "last_validation": state.last_validation,
                "next_action": state.next_action,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    )


def _extract_headings(text: str) -> list[str]:
    return [line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")]


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == f"## {heading}":
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def validate_manifest_projection(
    text: str, manifest: Mapping[str, object]
) -> list[str]:
    """Check the one-plan bootstrap projection without reconstructing legacy plans."""

    findings: list[str] = []
    controls = manifest.get("controls")
    if not isinstance(controls, Mapping):
        findings.append("Control Inventory projection does not bind manifest.controls")
    else:
        inventory_ids: list[str] = []
        for line in _extract_section(text, "Control Inventory").splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if (
                cells
                and cells[0] not in {"ID", "---"}
                and re.fullmatch(r"[A-Z][A-Z0-9-]+", cells[0])
            ):
                inventory_ids.append(cells[0])
        if set(inventory_ids) != set(controls):
            findings.append(
                "Control Inventory projection drift: IDs do not equal manifest.controls"
            )

    tasks = manifest.get("tasks")
    task_ids = [
        f"T{match.group(1)}"
        for match in re.finditer(r"(?im)^#{2,6}\s+Task\s+(\d+)\s*:", text)
    ]
    manifest_task_ids = [
        item["id"]
        for item in sorted(tasks or [], key=lambda item: item.get("order", 0))
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    ]
    if task_ids != manifest_task_ids:
        findings.append(
            "Task heading projection drift: ordered headings do not equal manifest.tasks"
        )

    bootstrap = manifest.get("bootstrap")
    bootstrap_mode = bootstrap.get("mode") if isinstance(bootstrap, Mapping) else None
    if bootstrap_mode == "explicit-single-plan":
        try:
            projected_validations, projected_manual_obligations = _parse_bootstrap_projection(text)
        except ExecutionContractError as exc:
            findings.append(f"Execution Contract projection is invalid: {exc}")
        else:
            manifest_validations = manifest.get("validations")
            manifest_by_id = {
                item["id"]: item
                for item in manifest_validations or []
                if isinstance(item, Mapping)
            }
            contract_by_id = {item["id"]: item for item in projected_validations}
            if set(manifest_by_id) != set(contract_by_id):
                findings.append(
                    "Execution Contract projection drift: validation IDs do not equal manifest.validations"
                )
            else:
                for validation_id, manifest_item in manifest_by_id.items():
                    contract_item = contract_by_id[validation_id]
                    if (
                        manifest_item["command"] != contract_item["command"]
                        or tuple(manifest_item["phases"]) != tuple(contract_item["phases"])
                    ):
                        findings.append(
                            f"Execution Contract projection drift for validation {validation_id}"
                        )
            manifest_manual = {
                item["id"]: item
                for item in manifest.get("manual_obligations", [])
                if isinstance(item, Mapping)
            }
            contract_manual = {item["id"]: item for item in projected_manual_obligations}
            if set(manifest_manual) != set(contract_manual):
                findings.append(
                    "Execution Contract projection drift: manual obligation IDs do not equal manifest.manual_obligations"
                )
    elif bootstrap_mode == "manifest-only":
        if re.search(r"(?m)^## Execution Contract\s*$", text):
            findings.append(
                "manifest-only plans must not contain an Execution Contract projection"
            )
    else:
        findings.append("Bootstrap projection mode is invalid or missing")

    authority = manifest.get("authority_boundaries")
    if not isinstance(authority, Mapping) or authority.get("no_git_mutation") is not True:
        findings.append("Authority projection drift: no_git_mutation is not true")
    if isinstance(bootstrap, Mapping):
        expected_binding = {
            "controls": "manifest.controls",
            "tasks": "manifest.tasks",
            "validations": "manifest.validations",
            "authority": "manifest.authority_boundaries",
        }
        if bootstrap.get("projection_binding") != expected_binding:
            findings.append("Bootstrap projection binding is conflicting")
        if bootstrap.get("legacy_only") != "reject":
            findings.append("Bootstrap must reject legacy-only plans")
    else:
        findings.append("Bootstrap projection metadata is missing")
    return findings


def _plan_reference_matches(plan_path: Path, status_path: Path, reference: str, repo_root: Path) -> bool:
    declared = Path(reference)
    candidates = {declared.resolve()} if declared.is_absolute() else {(status_path.parent / declared).resolve(), (plan_path.parent / declared).resolve(), (repo_root / declared).resolve()}
    return plan_path.resolve() in candidates


def validate_plan(path: Path, repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        return [Finding("plan-not-found", f"Plan file not found: {path}")]
    retained_dir = repo_root / "tmp" / "superpowers" / "plans"
    try:
        path.resolve().relative_to(retained_dir.resolve())
    except ValueError:
        findings.append(Finding("plan-outside-retained-directory", f"Plan must be under {retained_dir}"))
    try:
        text = path.read_text()
    except (OSError, UnicodeError) as exc:
        return findings + [Finding("plan-unreadable", f"Plan content is unreadable: {exc}")]
    headings = set(_extract_headings(text))
    for required in REQUIRED_PLAN_HEADINGS:
        if required not in headings and f"**{required}:**" not in text:
            findings.append(Finding("missing-heading", f"Plan missing required heading: {required}"))
    for canonical, aliases in PLAN_HEADING_ALIASES.items():
        if not any(alias in headings for alias in aliases):
            findings.append(Finding("missing-heading", f"Plan missing required heading: {canonical}"))
    for required in REQUIRED_EXECUTION_FIELDS:
        if not re.search(rf"(?im)^\s*(?:[-*]\s+)?(?:\*\*)?{re.escape(required)}(?:\*\*)?\s*:", text):
            findings.append(Finding("missing-execution-field", f"Plan missing required execution field: {required}"))
    if "Control Inventory" not in headings:
        findings.append(
            Finding(
                "missing-control-inventory",
                "Current plan missing required heading: Control Inventory",
            )
        )
    global_constraints = _extract_section(text, "Global Constraints")
    if not re.search(r"(?im)^\s*[-*]\s+.*\bno[- ]git\b.*$", global_constraints):
        findings.append(
            Finding(
                "missing-no-git-constraint",
                "Current plan missing an explicit no-Git constraint",
            )
        )
    if not (TASK_HEADING_RE.search(text) or UNCHECKED_TASK_RE.search(text)):
        findings.append(Finding("missing-task", "Plan must contain at least one task heading"))
    if not re.search(r"(?m)^## Execution Manifest\s*$", text):
        findings.append(
            Finding(
                "missing-execution-manifest",
                "Current plans must contain exactly one ## Execution Manifest",
            )
        )
    else:
        try:
            manifest = parse_execution_manifest(text)
        except ExecutionContractError as exc:
            findings.append(Finding(exc.code, str(exc)))
        else:
            for message in validate_manifest_projection(text, manifest):
                code = (
                    "obsolete-execution-contract"
                    if message.startswith("manifest-only plans must not")
                    else "bootstrap-projection-drift"
                )
                findings.append(Finding(code, message))
    return findings


def validate_state(
    plan_path: Path, state_path: Path, repo_root: Path | None = None
) -> list[Finding]:
    """Validate state location, plan binding, hashes, and task progress."""

    effective_root = repo_root or _find_repo_root(plan_path)
    findings = validate_plan(plan_path, effective_root)
    if state_path.resolve() != state_path_for(plan_path).resolve():
        findings.append(
            Finding(
                "state-path-mismatch",
                f"Resume state must be the plan sibling {state_path_for(plan_path)}",
            )
        )
    if not state_path.is_file():
        return findings + [Finding("state-not-found", f"Resume state not found: {state_path}")]
    try:
        payload = json.loads(
            state_path.read_text(), object_pairs_hook=_reject_duplicate_json_fields
        )
        state = parse_resume_state(_mapping(payload, "resume state"))
    except json.JSONDecodeError as exc:
        return findings + [Finding("malformed-state", f"Resume state JSON is malformed: {exc}")]
    except ExecutionContractError as exc:
        return findings + [Finding(exc.code, str(exc))]
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        return findings + [Finding("malformed-state", str(exc))]

    if not _plan_reference_matches(plan_path, state_path, state.plan, effective_root):
        findings.append(Finding("plan-binding-mismatch", f"Resume state plan does not match: {state.plan}"))
    try:
        manifest = parse_execution_manifest(plan_path.read_text())
        semantic_fingerprint = compute_semantic_fingerprint(manifest)
        content_hash = compute_content_sha256(plan_path)
        expected_task_ids = set(_manifest_task_ids(manifest))
    except (OSError, UnicodeError, ExecutionContractError) as exc:
        return findings + [Finding("plan-unreadable", str(exc))]
    if state.plan_fingerprint != semantic_fingerprint:
        findings.append(
            Finding(
                "semantic-fingerprint-drift",
                f"Manifest changed after approval: recorded {state.plan_fingerprint} != computed {semantic_fingerprint}",
            )
        )
    if state.content_hash != content_hash:
        findings.append(
            Finding(
                "content-hash-drift",
                f"Plan bytes changed after approval: recorded {state.content_hash} != computed {content_hash}",
            )
        )
    completed = set(state.completed_task_ids)
    remaining = set(state.remaining_task_ids)
    unknown = (completed | remaining) - expected_task_ids
    if unknown:
        findings.append(Finding("unknown-task-id", f"Resume state contains unknown task IDs: {sorted(unknown)}"))
    if completed | remaining != expected_task_ids:
        findings.append(Finding("incomplete-task-progress", "Resume state must account for every manifest task exactly once"))
    if state.status == "DONE" and remaining:
        findings.append(Finding("done-with-remaining-tasks", "DONE state must not contain remaining tasks"))
    if state.status != "DONE" and not remaining:
        findings.append(Finding("status-progress-mismatch", "A complete task set must use DONE status"))
    return findings


def build_compact_payload(findings: list[Finding]) -> dict[str, object]:
    blocking = [item for item in findings if item.severity == "blocking"]
    notices = [item for item in findings if item.severity == "notice"]
    return {"status": "passed" if not blocking else "failed", "finding_counts": {"total": len(findings), "blocking": len(blocking), "notice": len(notices)}, "finding_sample": [{"code": item.code, "severity": item.severity} for item in findings[:10]], "next_action": "All checks passed." if not blocking else "Resolve blocking plan execution findings."}


def _find_repo_root(start: Path) -> Path:
    for parent in start.resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / ".github").exists():
            return parent
    return start.resolve()


def _format_findings(findings: list[Finding], fmt: str) -> str:
    if fmt == "compact":
        return json.dumps(build_compact_payload(findings))
    if fmt == "json":
        return json.dumps({"status": "failed" if any(item.severity == "blocking" for item in findings) else "passed", "findings": [item.__dict__ for item in findings]}, indent=2)
    return "OK: all checks passed." if not findings else "\n".join(f"[{item.severity.upper()}] {item.code}: {item.message}" for item in findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only plan and resume-state validator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight = subparsers.add_parser("preflight", help="Validate a retained plan")
    preflight.add_argument("path", type=Path)
    preflight.add_argument("--repo-root", type=Path, default=None)
    preflight.add_argument("--format", choices=("text", "json", "compact"), default="text")
    state_check = subparsers.add_parser("state-check", help="Validate a JSON resume sibling")
    state_check.add_argument("plan", type=Path)
    state_check.add_argument("state", type=Path)
    state_check.add_argument("--repo-root", type=Path, default=None)
    state_check.add_argument("--format", choices=("text", "json", "compact"), default="text")
    args = parser.parse_args(argv)

    if args.command == "preflight":
        findings = validate_plan(args.path, args.repo_root or _find_repo_root(args.path))
    else:
        findings = validate_state(args.plan, args.state, args.repo_root)
    sys.stdout.write(_format_findings(findings, args.format) + "\n")
    return 1 if any(item.severity == "blocking" for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
