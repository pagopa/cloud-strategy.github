#!/usr/bin/env python3
"""Validator for retained plans and hash-bound execution status."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import yaml


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: Literal["blocking", "notice"] = "blocking"


VerdictOutcome = Literal["passed", "failed", "inconclusive"]
VERDICT_CATEGORIES = (
    "structure",
    "semantic_review",
    "artifact_provenance",
    "source_baseline",
    "execution_readiness",
)
VERDICT_OUTCOMES = frozenset({"passed", "failed", "inconclusive"})


@dataclass(frozen=True)
class Verdict:
    category: str
    outcome: VerdictOutcome
    coverage: str
    limit: str

    def __post_init__(self) -> None:
        if self.category not in VERDICT_CATEGORIES and self.category != "aggregate":
            raise ValueError(f"unsupported verdict category: {self.category}")
        if self.outcome not in VERDICT_OUTCOMES:
            raise ValueError(f"unsupported verdict outcome: {self.outcome}")
        if not self.coverage.strip() or not self.limit.strip():
            raise ValueError("verdict coverage and limit must be non-empty")

    def as_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "outcome": self.outcome,
            "coverage": self.coverage,
            "limit": self.limit,
        }


@dataclass(frozen=True)
class ApprovalEvidence:
    source: str
    statement: str
    plan_fingerprint: str
    content_hash: str

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "statement": self.statement,
            "plan_fingerprint": self.plan_fingerprint,
            "content_hash": self.content_hash,
        }


MANIFEST_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 2
STATE_STATUSES = frozenset({"DONE", "PARTIAL", "BLOCKED"})
APPROVAL_SOURCES = frozenset({"current-conversation", "external-authority-record"})
APPROVAL_STATEMENT = "explicit execution approval"
APPROVAL_EVIDENCE_FIELDS = frozenset(
    {"source", "statement", "plan_fingerprint", "content_hash"}
)
GIT_MUTATING_SUBCOMMANDS = frozenset(
    {
        "add",
        "am",
        "apply",
        "branch",
        "checkout",
        "clean",
        "clone",
        "commit",
        "config",
        "fetch",
        "gc",
        "init",
        "merge",
        "mv",
        "pull",
        "push",
        "rebase",
        "reflog",
        "reset",
        "restore",
        "rm",
        "stash",
        "switch",
        "tag",
        "update-ref",
        "worktree",
    }
)
GIT_OPTIONS_WITH_VALUE = frozenset(
    {
        "-C",
        "-c",
        "--config-env",
        "--exec-path",
        "--git-dir",
        "--namespace",
        "--work-tree",
    }
)
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
        "delegation",
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
DELEGATION_FIELDS = frozenset(
    {"schema_version", "mode", "worker", "result", "receipt", "acceptance"}
)
DELEGATION_RECORD_FIELDS = frozenset(
    {"status", "content_hash", "plan_fingerprint"}
)
DELEGATION_MODES = frozenset({"none", "delegated"})
LOCAL_DELEGATION_RESULT = "not_applicable"
LEGACY_DELEGATION_COMPATIBILITY = "manifest-v1-without-delegation"
CURRENT_DELEGATION_COMPATIBILITY = "manifest-v1-with-delegation-v1"

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
        "approval_evidence",
        "delivery_verdicts",
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


BootstrapStatus = Literal["PASS", "BLOCKED"]


@dataclass(frozen=True)
class BootstrapCheck:
    check: str
    status: BootstrapStatus
    next_action: str
    external: bool = False


def build_bootstrap_payload(
    check: str, status: BootstrapStatus, next_action: str
) -> dict[str, str]:
    """Build the compact three-field local bootstrap projection."""

    if not isinstance(check, str) or not check.strip():
        raise ExecutionContractError(
            "bootstrap-check-required", "Bootstrap check must be non-empty"
        )
    if status not in {"PASS", "BLOCKED"}:
        raise ExecutionContractError(
            "bootstrap-status-invalid", "Bootstrap status must be PASS or BLOCKED"
        )
    if not isinstance(next_action, str) or not next_action.strip():
        raise ExecutionContractError(
            "bootstrap-next-action-required",
            "Bootstrap next_action must be concrete and non-empty",
        )
    if status == "BLOCKED" and next_action.strip().lower() in {"none", "no action", "n/a"}:
        raise ExecutionContractError(
            "bootstrap-next-action-required",
            "A blocked bootstrap check must name one concrete next action",
        )
    return {
        "check": check.strip(),
        "status": status,
        "next_action": next_action.strip(),
    }


def run_local_bootstrap(
    checks: Sequence[BootstrapCheck],
) -> tuple[dict[str, str], ...]:
    """Collect finite local checks and stop before external work after a block."""

    results: list[dict[str, str]] = []
    for check in checks:
        if check.external:
            break
        results.append(build_bootstrap_payload(check.check, check.status, check.next_action))
        if check.status == "BLOCKED":
            break
    return tuple(results)


def resolve_loaded_bundle(entrypoint: Path) -> Path:
    """Resolve the physical executor bundle owning a loaded entrypoint."""

    if entrypoint.is_symlink() and not entrypoint.exists():
        raise ExecutionContractError(
            "loaded-bundle-stale",
            f"Loaded executor entrypoint is a stale symlink: {entrypoint}; "
            "next action: repair the loaded bundle link before execution.",
        )
    try:
        physical_entrypoint = entrypoint.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ExecutionContractError(
            "loaded-bundle-missing",
            f"Loaded executor entrypoint is unavailable: {entrypoint}; "
            "next action: load the executor bundle before execution.",
        ) from exc
    if not physical_entrypoint.is_file():
        raise ExecutionContractError(
            "loaded-bundle-invalid",
            f"Loaded executor entrypoint is not a file: {physical_entrypoint}; "
            "next action: repair the loaded executor bundle.",
        )
    scripts_dir = physical_entrypoint.parent
    bundle_root = scripts_dir.parent
    if (
        physical_entrypoint.name != "plan_execution.py"
        or scripts_dir.name != "scripts"
        or not (bundle_root / "SKILL.md").is_file()
    ):
        raise ExecutionContractError(
            "loaded-bundle-invalid",
            f"Loaded entrypoint does not belong to an executor bundle: {physical_entrypoint}; "
            "next action: use the physical internal-gateway-execute-plans bundle.",
        )
    return bundle_root

def bundle_runner_command(
    bundle_entrypoint: Path, argv: Sequence[str], cwd: Path
) -> list[str]:
    """Build the runner command from a loaded entrypoint, independent of cwd."""

    entrypoint = bundle_entrypoint
    if not entrypoint.is_absolute():
        entrypoint = cwd / entrypoint
    bundle_root = resolve_loaded_bundle(entrypoint)
    runner = bundle_root / "scripts" / "run.sh"
    if not runner.is_file():
        raise ExecutionContractError(
            "bundle-runner-missing",
            f"Executor bundle runner is missing: {runner}; "
            "next action: restore scripts/run.sh in the loaded bundle.",
        )
    return ["bash", str(runner), *(str(argument) for argument in argv)]


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


def _contains_embedded_digest(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"content_sha256", "semantic_fingerprint"} and isinstance(
                child, str
            ):
                if SHA256_RE.fullmatch(child):
                    return True
            if _contains_embedded_digest(child):
                return True
    elif isinstance(value, list):
        return any(_contains_embedded_digest(item) for item in value)
    return False


def compute_semantic_fingerprint(manifest: Mapping[str, object]) -> str:
    """Return the external SHA-256 of the canonical Execution Manifest JSON."""

    if _contains_embedded_digest(manifest):
        raise ExecutionContractError(
            "manifest-hash-self-reference",
            "Execution Manifest must not contain a content or semantic digest value",
        )
    return f"sha256:{hashlib.sha256(canonical_json(manifest)).hexdigest()}"


def _field_differences(
    mapping: Mapping[str, object], expected: set[str] | frozenset[str]
) -> tuple[set[str], set[str]]:
    expected_fields = set(expected)
    return set(mapping) - expected_fields, expected_fields - set(mapping)


def _manifest_exact_fields(
    mapping: Mapping[str, object], expected: set[str] | frozenset[str], label: str
) -> None:
    unknown, missing = _field_differences(mapping, expected)
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


def delegation_compatibility_mode(manifest: Mapping[str, object]) -> str:
    """Name the explicit compatibility path for Manifest v1 provenance."""

    if "delegation" not in manifest:
        return LEGACY_DELEGATION_COMPATIBILITY
    return CURRENT_DELEGATION_COMPATIBILITY


def _delegation_record(value: object, label: str) -> dict[str, str]:
    if value is None:
        code = (
            "worker-result-not-accepted"
            if label == "delegation.result"
            else "delegation-acceptance-required"
        )
        raise ExecutionContractError(
            code, f"{label} must be an accepted provenance record"
        )
    try:
        record = _manifest_object(value, label)
        _manifest_exact_fields(record, DELEGATION_RECORD_FIELDS, label)
        status = _string(record["status"], f"{label}.status")
        content_hash = _string(record["content_hash"], f"{label}.content_hash")
        plan_fingerprint = _string(
            record["plan_fingerprint"], f"{label}.plan_fingerprint"
        )
    except (TypeError, ValueError) as exc:
        raise ExecutionContractError(
            "malformed-delegation-record", str(exc)
        ) from exc

    if status != "accepted":
        code = (
            "worker-result-not-accepted"
            if label == "delegation.result"
            else "delegation-acceptance-required"
        )
        raise ExecutionContractError(code, f"{label}.status must be accepted")
    if not SHA256_RE.fullmatch(content_hash):
        raise ExecutionContractError(
            "invalid-delegation-hash",
            f"{label}.content_hash must be a SHA-256 digest",
        )
    if not SHA256_RE.fullmatch(plan_fingerprint):
        raise ExecutionContractError(
            "invalid-delegation-hash",
            f"{label}.plan_fingerprint must be a SHA-256 digest",
        )
    return {
        "status": status,
        "content_hash": content_hash,
        "plan_fingerprint": plan_fingerprint,
    }


def _validate_delegation_provenance(
    root: Mapping[str, object], authority: Mapping[str, object]
) -> None:
    if "delegation" not in root:
        return

    try:
        delegation = _manifest_object(root["delegation"], "delegation")
        _manifest_exact_fields(delegation, DELEGATION_FIELDS, "delegation")
        schema_version = delegation["schema_version"]
        mode = _string(delegation["mode"], "delegation.mode")
        worker = _string(delegation["worker"], "delegation.worker")
    except (TypeError, ValueError) as exc:
        raise ExecutionContractError(
            "malformed-delegation-extension", str(exc)
        ) from exc

    if not _is_int(schema_version) or schema_version != 1:
        raise ExecutionContractError(
            "unsupported-delegation-schema",
            "delegation.schema_version must be 1",
        )
    if mode not in DELEGATION_MODES:
        raise ExecutionContractError(
            "invalid-delegation-mode",
            "delegation.mode must be none or delegated",
        )

    if mode == "none":
        if worker != "primary-owner":
            raise ExecutionContractError(
                "local-worker-authorship",
                "mode none must use worker primary-owner",
            )
        if delegation["receipt"] is not None:
            raise ExecutionContractError(
                "delegation-receipt-without-worker",
                "mode none cannot claim a delegation receipt",
            )
        if (
            delegation["result"] is not None
            and delegation["result"] != LOCAL_DELEGATION_RESULT
        ) or delegation["acceptance"] is not None:
            raise ExecutionContractError(
                "local-worker-authorship",
                "mode none cannot claim worker result or acceptance",
            )
        if delegation["result"] != LOCAL_DELEGATION_RESULT:
            raise ExecutionContractError(
                "local-provenance-marker",
                "mode none must record result not_applicable",
            )
        return

    if worker != authority["worker"]:
        raise ExecutionContractError(
            "delegation-worker-mismatch",
            "delegated worker must match authority_boundaries.worker",
        )
    result = _delegation_record(delegation["result"], "delegation.result")
    receipt = _delegation_record(delegation["receipt"], "delegation.receipt")
    acceptance = _delegation_record(
        delegation["acceptance"], "delegation.acceptance"
    )
    for record_name, record in (("receipt", receipt), ("acceptance", acceptance)):
        if record["content_hash"] != result["content_hash"] or record[
            "plan_fingerprint"
        ] != result["plan_fingerprint"]:
            raise ExecutionContractError(
                "stale-delegation-binding",
                f"delegation.{record_name} must bind the accepted result hashes; "
                "material edits require new content and semantic hashes plus acceptance",
            )


def _manifest_non_empty_strings(value: object, label: str) -> tuple[str, ...]:
    return _strings(value, label, allow_empty=False)


def _manifest_id_list(value: object, label: str) -> tuple[str, ...]:
    return _unique_strings(value, label, allow_empty=True)


def _remember_unique(
    value: str,
    seen: set[str],
    message: str,
    *,
    code: str | None = None,
) -> None:
    if value in seen:
        if code is not None:
            raise ExecutionContractError(code, message)
        raise ValueError(message)
    seen.add(value)


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


def _validate_manifest_identity(root: Mapping[str, object]) -> None:
    if (
        not _is_int(root["schema_version"])
        or root["schema_version"] != MANIFEST_SCHEMA_VERSION
    ):
        raise ExecutionContractError(
            "unsupported-manifest-schema",
            f"Execution Manifest schema_version must be {MANIFEST_SCHEMA_VERSION}",
        )
    if (
        not _non_empty_string(root["manifest_version"])
        or root["manifest_version"] != "execution-manifest/v1"
    ):
        raise ValueError("manifest_version must be execution-manifest/v1")
    if not _non_empty_string(root["plan_id"]):
        raise ValueError("plan_id must be non-empty")
    if root["repository_root"] != ".":
        raise ValueError("repository_root must be .")


def _validate_authority_boundaries(
    root: Mapping[str, object]
) -> Mapping[str, object]:
    authority = _manifest_object(root["authority_boundaries"], "authority_boundaries")
    _manifest_exact_fields(
        authority,
        {
            "normative_owner",
            "execution_owner",
            "worker",
            "caller_owns",
            "protected_paths",
            "no_git_mutation",
        },
        "authority_boundaries",
    )
    if not _non_empty_string(authority["normative_owner"]) or not _non_empty_string(
        authority["execution_owner"]
    ):
        raise ValueError("authority owners must be non-empty")
    if not _non_empty_string(authority["worker"]):
        raise ValueError("authority_boundaries.worker must be non-empty")
    _manifest_non_empty_strings(
        authority["caller_owns"], "authority_boundaries.caller_owns"
    )
    _manifest_non_empty_strings(
        authority["protected_paths"], "authority_boundaries.protected_paths"
    )
    if not _bool(authority["no_git_mutation"], "authority_boundaries.no_git_mutation"):
        raise ValueError("authority_boundaries.no_git_mutation must be true")
    return authority


def _validate_targets(value: object) -> None:
    targets = value
    if not isinstance(targets, list) or not targets:
        raise ValueError("targets must be a non-empty list")
    target_ids: set[str] = set()
    for index, raw_target in enumerate(targets):
        label = f"targets[{index}]"
        target = _manifest_object(raw_target, label)
        keys = (
            {"id", "path", "state", "condition"}
            if "condition" in target
            else {"id", "path", "state"}
        )
        _manifest_exact_fields(target, keys, label)
        target_id = _string(target["id"], f"{label}.id")
        _remember_unique(target_id, target_ids, f"duplicate target id: {target_id}")
        target_path = _string(target["path"], f"{label}.path")
        if _is_git_directory_path(target_path):
            raise ExecutionContractError(
                "git-target-prohibited",
                f"{label}.path must not target the .git directory",
            )
        if target["state"] not in MANIFEST_TARGET_STATES:
            raise ValueError(f"{label}.state is invalid")
        if "condition" in target:
            _string(target["condition"], f"{label}.condition")


def _validate_controls(value: object) -> None:
    controls = _manifest_object(value, "controls")
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


def _validate_validations(value: object) -> None:
    validations = value
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
        _remember_unique(
            validation_id,
            validation_ids,
            f"Duplicate validation id: {validation_id}",
            code="duplicate-validation-id",
        )
        validation_command = _string(validation["command"], f"{label}.command")
        _reject_git_mutation(validation_command, f"{label}.command")
        _string(validation["owner"], f"{label}.owner")
        _string(validation["pass_signal"], f"{label}.pass_signal")
        phases = _manifest_non_empty_strings(validation["phases"], f"{label}.phases")
        if any(phase not in MANIFEST_PHASES for phase in phases):
            raise ValueError(f"{label}.phases contains an unsupported phase")
        if (
            "equivalence" in validation
            and validation["equivalence"] not in MANIFEST_EQUIVALENCE
        ):
            raise ValueError(f"{label}.equivalence is invalid")


def _validate_manual_obligations(value: object) -> None:
    manual = value
    if not isinstance(manual, list):
        raise ValueError("manual_obligations must be a list")
    manual_ids: set[str] = set()
    for index, raw_obligation in enumerate(manual):
        label = f"manual_obligations[{index}]"
        obligation = _manifest_object(raw_obligation, label)
        _manifest_exact_fields(
            obligation, {"id", "kind", "required", "acceptance"}, label
        )
        obligation_id = _string(obligation["id"], f"{label}.id")
        _remember_unique(
            obligation_id,
            manual_ids,
            f"duplicate manual obligation id: {obligation_id}",
        )
        if obligation["kind"] not in {"human", "external"}:
            raise ValueError(f"{label}.kind is invalid")
        _bool(obligation["required"], f"{label}.required")
        obligation_acceptance = _string(
            obligation["acceptance"], f"{label}.acceptance"
        )
        _reject_git_mutation(obligation_acceptance, f"{label}.acceptance")


def _validate_tasks(value: object) -> None:
    tasks = value
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")
    task_ids: set[str] = set()
    orders: set[int] = set()
    for index, raw_task in enumerate(tasks):
        label = f"tasks[{index}]"
        task = _manifest_object(raw_task, label)
        _manifest_exact_fields(
            task,
            {
                "id",
                "order",
                "posture",
                "objective",
                "depends_on",
                "target_ids",
                "validation_ids",
                "manual_obligation_ids",
                "acceptance",
                "stop_conditions",
            },
            label,
        )
        task_id = _string(task["id"], f"{label}.id")
        _remember_unique(task_id, task_ids, f"duplicate task id: {task_id}")
        if (
            not _is_int(task["order"])
            or task["order"] < 1
            or task["order"] in orders
        ):
            raise ValueError(f"{label}.order must be a unique positive integer")
        orders.add(task["order"])
        if task["posture"] not in MANIFEST_POSTURES:
            raise ValueError(f"{label}.posture is invalid")
        task_objective = _string(task["objective"], f"{label}.objective")
        _reject_git_mutation(task_objective, f"{label}.objective")
        _manifest_id_list(task["depends_on"], f"{label}.depends_on")
        _manifest_id_list(task["target_ids"], f"{label}.target_ids")
        _manifest_id_list(task["validation_ids"], f"{label}.validation_ids")
        task_acceptance = _manifest_non_empty_strings(
            task["acceptance"], f"{label}.acceptance"
        )
        task_stop_conditions = _manifest_non_empty_strings(
            task["stop_conditions"], f"{label}.stop_conditions"
        )
        for item in (*task_acceptance, *task_stop_conditions):
            _reject_git_mutation(item, label)


def _validate_retry_policy(value: object) -> None:
    retry = _manifest_object(value, "retry_policy")
    _manifest_exact_fields(
        retry,
        {
            "initial_attempts",
            "max_context_refills",
            "max_corrective_retries",
            "caller_may_lower",
            "repeat_progress_status",
            "minor_or_cosmetic_reopens",
        },
        "retry_policy",
    )
    for field in (
        "initial_attempts",
        "max_context_refills",
        "max_corrective_retries",
    ):
        if not _is_int(retry[field]) or retry[field] < 0:
            raise ValueError(f"retry_policy.{field} must be a non-negative integer")
    if (
        retry["initial_attempts"] != 1
        or retry["max_context_refills"] != 1
        or retry["max_corrective_retries"] != 1
    ):
        raise ValueError(
            "retry_policy must retain one initial attempt, one refill, and one corrective retry"
        )
    _bool(retry["caller_may_lower"], "retry_policy.caller_may_lower")
    if retry["repeat_progress_status"] != "stalled":
        raise ValueError("retry_policy.repeat_progress_status must be stalled")
    if retry["minor_or_cosmetic_reopens"] is not False:
        raise ValueError("retry_policy.minor_or_cosmetic_reopens must be false")


def _validate_hashing(value: object) -> None:
    hashing = _manifest_object(value, "hashing")
    _manifest_exact_fields(
        hashing,
        {"content_sha256", "semantic_fingerprint", "self_reference"},
        "hashing",
    )
    content_hash = _manifest_object(
        hashing["content_sha256"], "hashing.content_sha256"
    )
    semantic_hash = _manifest_object(
        hashing["semantic_fingerprint"], "hashing.semantic_fingerprint"
    )
    _manifest_exact_fields(
        content_hash,
        {"algorithm", "input", "binding"},
        "hashing.content_sha256",
    )
    _manifest_exact_fields(
        semantic_hash,
        {"algorithm", "input", "version", "binding"},
        "hashing.semantic_fingerprint",
    )
    if (
        content_hash["algorithm"] != "SHA-256"
        or semantic_hash["algorithm"] != "SHA-256"
    ):
        raise ValueError("hashing algorithms must be SHA-256")
    _string(content_hash["input"], "hashing.content_sha256.input")
    _string(semantic_hash["input"], "hashing.semantic_fingerprint.input")
    if (
        content_hash["binding"] != "external"
        or semantic_hash["binding"] != "external"
    ):
        raise ValueError("hashing bindings must be external")
    _string(semantic_hash["version"], "hashing.semantic_fingerprint.version")
    if hashing["self_reference"] is not False:
        raise ValueError("hashing.self_reference must be false")


def _validate_approval(value: object) -> None:
    approval = _manifest_object(value, "approval")
    _manifest_exact_fields(
        approval,
        {"binds", "editorial_content_change", "normative_manifest_change"},
        "approval",
    )
    if approval["binds"] != "semantic_fingerprint":
        raise ValueError("approval.binds must be semantic_fingerprint")
    _string(
        approval["editorial_content_change"], "approval.editorial_content_change"
    )
    _string(
        approval["normative_manifest_change"], "approval.normative_manifest_change"
    )


def _validate_bootstrap(value: object) -> None:
    bootstrap = _manifest_object(value, "bootstrap")
    _manifest_exact_fields(
        bootstrap,
        {
            "mode",
            "compatibility_projection",
            "projection_binding",
            "legacy_only",
            "retirement_evidence",
        },
        "bootstrap",
    )
    mode = _string(bootstrap["mode"], "bootstrap.mode")
    if mode not in MANIFEST_BOOTSTRAP_MODES:
        raise ValueError("bootstrap.mode is invalid")
    projection = _strings(
        bootstrap["compatibility_projection"], "bootstrap.compatibility_projection"
    )
    if mode == "explicit-single-plan" and projection != (
        "Control Inventory",
        "Task headings",
        "Execution Contract",
    ):
        raise ValueError(
            "bootstrap.compatibility_projection is not the supported projection"
        )
    if mode == "manifest-only" and projection:
        raise ValueError("manifest-only plans must not emit a compatibility projection")
    binding = _manifest_object(
        bootstrap["projection_binding"], "bootstrap.projection_binding"
    )
    _manifest_exact_fields(
        binding,
        {"controls", "tasks", "validations", "authority"},
        "bootstrap.projection_binding",
    )
    if dict(binding) != {
        "controls": "manifest.controls",
        "tasks": "manifest.tasks",
        "validations": "manifest.validations",
        "authority": "manifest.authority_boundaries",
    }:
        raise ValueError("bootstrap.projection_binding is conflicting")
    if bootstrap["legacy_only"] != "reject":
        raise ValueError("bootstrap.legacy_only must be reject")
    _string(bootstrap["retirement_evidence"], "bootstrap.retirement_evidence")


def _validate_rollout_and_handoff(root: Mapping[str, object]) -> None:
    _manifest_non_empty_strings(root["rollout"], "rollout")
    handoff = _manifest_object(root["handoff"], "handoff")
    _manifest_exact_fields(
        handoff,
        {"next_owner", "requires", "status_sibling", "git_mutation"},
        "handoff",
    )
    if handoff["next_owner"] != "/internal-gateway-execute-plans":
        raise ValueError("handoff.next_owner must be /internal-gateway-execute-plans")
    requires = _manifest_non_empty_strings(
        handoff["requires"], "handoff.requires"
    )
    for required in (
        "human approval",
        "exact semantic_fingerprint review",
        "zero blocking preflight findings",
    ):
        if required not in requires:
            raise ValueError(f"handoff.requires is missing {required}")
    if handoff["status_sibling"] != "none" or handoff["git_mutation"] != "prohibited":
        raise ValueError("handoff must prohibit status sibling and Git mutation")


def parse_execution_manifest(text: str) -> dict[str, object]:
    """Parse and validate exactly one normative Execution Manifest object."""

    root = _manifest_fenced_object(text, "Execution Manifest")
    manifest_fields = (
        MANIFEST_FIELDS
        if "delegation" in root
        else MANIFEST_FIELDS - {"delegation"}
    )
    _manifest_exact_fields(root, manifest_fields, "Execution Manifest")
    try:
        _validate_manifest_identity(root)
        authority = _validate_authority_boundaries(root)
        _validate_delegation_provenance(root, authority)

        _validate_targets(root["targets"])
        _validate_controls(root["controls"])
        _validate_validations(root["validations"])
        _validate_manual_obligations(root["manual_obligations"])
        _validate_tasks(root["tasks"])
        _validate_retry_policy(root["retry_policy"])
        _validate_hashing(root["hashing"])
        compute_semantic_fingerprint(root)
        _validate_approval(root["approval"])
        _validate_bootstrap(root["bootstrap"])
        _validate_rollout_and_handoff(root)
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


def _manifest_object(value: object, label: str) -> Mapping[str, object]:
    return _mapping(value, label)


def _bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string(value: object, label: str) -> str:
    if not _non_empty_string(value):
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _strings(value: object, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        _non_empty_string(item) for item in value
    ):
        raise ValueError(f"{label} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise ValueError(f"{label} must not be empty")
    return tuple(item.strip() for item in value)


def _unique_strings(
    value: object, label: str, *, allow_empty: bool = True
) -> tuple[str, ...]:
    values = _strings(value, label, allow_empty=allow_empty)
    duplicate = next(
        (item for index, item in enumerate(values) if item in values[:index]),
        None,
    )
    if duplicate is not None:
        raise ValueError(f"{label} must not contain duplicate ids")
    return values


def _exact_fields(
    mapping: Mapping[str, object], expected: set[str] | frozenset[str], label: str
) -> None:
    unknown, missing = _field_differences(mapping, expected)
    if unknown or missing:
        details: list[str] = []
        if unknown:
            details.append(f"unknown fields: {sorted(unknown)}")
        if missing:
            details.append(f"missing fields: {sorted(missing)}")
        raise ValueError(f"{label} is malformed ({'; '.join(details)})")


def _git_mutating_subcommands(value: str) -> tuple[str, ...]:
    """Return explicitly mutating Git subcommands found in a command-like value."""

    try:
        tokens = shlex.split(value)
    except ValueError:
        return ()

    found: list[str] = []
    for index, token in enumerate(tokens):
        if Path(token).name != "git":
            continue
        cursor = index + 1
        while cursor < len(tokens) and tokens[cursor].startswith("-"):
            option = tokens[cursor]
            cursor += 1
            if option in GIT_OPTIONS_WITH_VALUE and cursor < len(tokens):
                cursor += 1
        if cursor < len(tokens) and tokens[cursor] in GIT_MUTATING_SUBCOMMANDS:
            found.append(tokens[cursor])
    return tuple(dict.fromkeys(found))


def _reject_git_mutation(value: str, label: str) -> None:
    mutations = _git_mutating_subcommands(value)
    if mutations:
        raise ExecutionContractError(
            "git-mutation-command",
            f"{label} contains prohibited Git mutation: {', '.join(mutations)}",
        )


def _is_git_directory_path(value: str) -> bool:
    return ".git" in Path(value).parts


def _parse_approval_evidence(
    value: object, plan_fingerprint: str, content_hash: str
) -> ApprovalEvidence:
    try:
        mapping = _mapping(value, "approval_evidence")
        _exact_fields(mapping, APPROVAL_EVIDENCE_FIELDS, "approval_evidence")
        source = _string(mapping["source"], "approval_evidence.source")
        statement = _string(mapping["statement"], "approval_evidence.statement")
        recorded_plan_fingerprint = _string(
            mapping["plan_fingerprint"], "approval_evidence.plan_fingerprint"
        )
        recorded_content_hash = _string(
            mapping["content_hash"], "approval_evidence.content_hash"
        )
    except (TypeError, ValueError) as exc:
        raise ExecutionContractError(
            "malformed-approval-evidence", str(exc)
        ) from exc

    if source not in APPROVAL_SOURCES:
        raise ExecutionContractError(
            "invalid-approval-source",
            f"approval_evidence.source must be one of {sorted(APPROVAL_SOURCES)}",
        )
    if statement != APPROVAL_STATEMENT:
        raise ExecutionContractError(
            "approval-statement-required",
            f"approval_evidence.statement must be {APPROVAL_STATEMENT!r}",
        )
    if recorded_plan_fingerprint != plan_fingerprint or recorded_content_hash != content_hash:
        raise ExecutionContractError(
            "approval-binding-mismatch",
            "approval evidence must bind the current plan fingerprint and content hash",
        )
    return ApprovalEvidence(
        source,
        statement,
        recorded_plan_fingerprint,
        recorded_content_hash,
    )


def _parse_delivery_verdicts(value: object) -> tuple[Verdict, ...]:
    if not isinstance(value, list):
        raise ExecutionContractError(
            "malformed-delivery-verdicts",
            "delivery_verdicts must be a list",
        )

    verdicts: list[Verdict] = []
    for index, raw_verdict in enumerate(value):
        label = f"delivery_verdicts[{index}]"
        try:
            mapping = _mapping(raw_verdict, label)
            _exact_fields(mapping, {"category", "outcome", "coverage", "limit"}, label)
            verdicts.append(
                Verdict(
                    _string(mapping["category"], f"{label}.category"),
                    _string(mapping["outcome"], f"{label}.outcome"),
                    _string(mapping["coverage"], f"{label}.coverage"),
                    _string(mapping["limit"], f"{label}.limit"),
                )
            )
        except (TypeError, ValueError) as exc:
            raise ExecutionContractError(
                "malformed-delivery-verdicts", str(exc)
            ) from exc

    categories = tuple(verdict.category for verdict in verdicts)
    if categories != VERDICT_CATEGORIES:
        raise ExecutionContractError(
            "delivery-verdict-categories",
            "delivery_verdicts must contain the five categories in canonical order",
        )
    return tuple(verdicts)


def compute_sha256(path: Path) -> str:
    return compute_content_sha256(path)


def compute_content_sha256(path: Path) -> str:
    """Hash the exact retained-plan bytes for external audit binding."""

    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


@dataclass(frozen=True)
class ResumeState:
    schema_version: Literal[2]
    status: Literal["DONE", "PARTIAL", "BLOCKED"]
    plan: str
    plan_fingerprint: str
    content_hash: str
    approval_evidence: ApprovalEvidence
    delivery_verdicts: tuple[Verdict, ...]
    completed_task_ids: tuple[str, ...]
    remaining_task_ids: tuple[str, ...]
    last_validation: str
    next_action: str


@dataclass(frozen=True)
class StatusDiscovery:
    path: Path | None
    state: ResumeState | None
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class Baseline:
    head: str
    paths: Mapping[str, str]


def _git_head(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ExecutionContractError(
            "baseline-head-unavailable",
            f"Unable to resolve repository HEAD: {exc}",
        ) from exc
    head = completed.stdout.strip()
    if not head:
        raise ExecutionContractError("baseline-head-unavailable", "Repository HEAD is empty")
    return head


def _relevant_files(repo_root: Path, declared_paths: Sequence[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    root = repo_root.resolve()
    for declared in declared_paths:
        candidate = Path(declared)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ExecutionContractError(
                "invalid-baseline-path",
                f"Relevant baseline path must remain repository-relative: {declared}",
            )
        target = (root / candidate).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ExecutionContractError(
                "invalid-baseline-path",
                f"Relevant baseline path escapes repository: {declared}",
            ) from exc
        if target.is_file():
            hashes[candidate.as_posix()] = compute_content_sha256(target)
        elif target.is_dir():
            for entry in sorted(target.rglob("*")):
                if not entry.is_file():
                    continue
                relative = entry.resolve().relative_to(root).as_posix()
                hashes[relative] = compute_content_sha256(entry)
        else:
            hashes[candidate.as_posix()] = "<missing>"
    return hashes


def compute_relevant_baseline(repo_root: Path, paths: Sequence[str]) -> Baseline:
    """Capture HEAD and exact dirty bytes for explicitly relevant paths."""

    return Baseline(_git_head(repo_root.resolve()), _relevant_files(repo_root, paths))


def validate_relevant_baseline(
    baseline: Baseline, current: Baseline
) -> list[Finding]:
    """Fail closed on HEAD, declared-path, or undeclared dependency drift."""

    findings: list[Finding] = []
    if baseline.head != current.head:
        findings.append(
            Finding(
                "baseline-head-drift",
                f"Repository HEAD changed: {baseline.head} != {current.head}",
            )
        )
    baseline_paths = dict(baseline.paths)
    current_paths = dict(current.paths)
    for path, expected in baseline_paths.items():
        actual = current_paths.get(path, "<missing>")
        if actual != expected:
            findings.append(
                Finding(
                    "relevant-path-drift",
                    f"Relevant path changed: {path}",
                )
            )
    for path in sorted(set(current_paths) - set(baseline_paths)):
        findings.append(
            Finding(
                "undeclared-dependency-drift",
                f"Current baseline contains undeclared path: {path}",
            )
        )
    return findings


def validate_ignored_artifact(path: Path, expected_hash: str) -> Finding | None:
    """Validate an ignored retained artifact by reading its exact bytes."""

    if not path.is_file():
        return Finding("ignored-artifact-missing", f"Ignored artifact is missing: {path}")
    actual_hash = compute_content_sha256(path)
    if actual_hash != expected_hash:
        return Finding(
            "ignored-artifact-hash-drift",
            f"Ignored artifact bytes changed: {path}",
        )
    return None


def git_diff_check_coverage(outcome: str) -> dict[str, str]:
    """Describe the narrow coverage of `git diff --check` without overclaiming."""

    if not outcome.strip():
        raise ValueError("git diff --check outcome must be non-empty")
    return {
        "command": "git diff --check",
        "outcome": outcome,
        "coverage": "Git-visible paths only",
        "limit": "Ignored paths are not covered and require direct byte validation",
    }


def aggregate_verdict(
    required: Sequence[str], verdicts: Mapping[str, Verdict]
) -> Verdict:
    """Combine independent verdicts without hiding missing or inconclusive work."""

    required_categories = tuple(required)
    if not required_categories or len(set(required_categories)) != len(required_categories):
        raise ValueError("required verdict categories must be unique and non-empty")
    unsupported = set(required_categories) - set(VERDICT_CATEGORIES)
    if unsupported:
        raise ValueError(f"unsupported required verdict categories: {sorted(unsupported)}")

    missing = [category for category in required_categories if category not in verdicts]
    inconclusive = [
        category
        for category in required_categories
        if category in verdicts and verdicts[category].outcome == "inconclusive"
    ]
    failed = [
        category
        for category in required_categories
        if category in verdicts and verdicts[category].outcome == "failed"
    ]
    if missing or inconclusive:
        outcome: VerdictOutcome = "inconclusive"
        limits: list[str] = []
        if missing:
            limits.append(f"missing={','.join(missing)}")
        if inconclusive:
            limits.append(f"inconclusive={','.join(inconclusive)}")
        limit = "; ".join(limits)
    elif failed:
        outcome = "failed"
        limit = f"failed={','.join(failed)}"
    else:
        outcome = "passed"
        limit = "none"
    coverage = f"required categories={','.join(required_categories)}"
    return Verdict("aggregate", outcome, coverage, limit)


def build_verdict_payload(
    required: Sequence[str], verdicts: Mapping[str, Verdict]
) -> dict[str, object]:
    """Build category-qualified output and preserve gaps as explicit verdicts."""

    aggregate = aggregate_verdict(required, verdicts)
    rendered: dict[str, dict[str, str]] = {}
    for category in required:
        verdict = verdicts.get(category)
        if verdict is None:
            verdict = Verdict(
                category,
                "inconclusive",
                "No category result was supplied",
                "Missing required verdict",
            )
        elif verdict.category != category:
            raise ValueError(f"verdict key does not match category: {category}")
        rendered[category] = verdict.as_dict()
    return {"verdicts": rendered, "aggregate": aggregate.as_dict()}


def _manifest_task_ids(manifest: Mapping[str, object]) -> tuple[str, ...]:
    tasks = manifest["tasks"]
    if not isinstance(tasks, list):
        raise ExecutionContractError("malformed-execution-manifest", "Manifest tasks must be a list")
    return tuple(
        item["id"]
        for item in sorted(tasks, key=lambda value: value["order"])
        if isinstance(item, Mapping)
    )


@dataclass(frozen=True)
class _PlanSnapshot:
    text: str
    manifest: dict[str, object]
    semantic_fingerprint: str
    content_hash: str
    task_ids: tuple[str, ...]


def _load_plan_snapshot(plan_path: Path) -> _PlanSnapshot:
    text = plan_path.read_text(encoding="utf-8")
    manifest = parse_execution_manifest(text)
    return _PlanSnapshot(
        text=text,
        manifest=manifest,
        semantic_fingerprint=compute_semantic_fingerprint(manifest),
        content_hash=compute_content_sha256(plan_path),
        task_ids=_manifest_task_ids(manifest),
    )


def parse_resume_state(payload: Mapping[str, object]) -> ResumeState:
    """Parse the strict, hash-bound state persisted by the execution gateway."""

    mapping = _mapping(payload, "resume state")
    _exact_fields(mapping, STATE_FIELDS, "resume state")
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
    approval_evidence = _parse_approval_evidence(
        mapping["approval_evidence"], plan_fingerprint, content_hash
    )
    delivery_verdicts = _parse_delivery_verdicts(mapping["delivery_verdicts"])
    if status == "DONE":
        aggregate = aggregate_verdict(
            VERDICT_CATEGORIES,
            {verdict.category: verdict for verdict in delivery_verdicts},
        )
        if aggregate.outcome != "passed":
            raise ExecutionContractError(
                "done-with-unpassed-delivery-verdicts",
                "DONE status requires all five delivery verdicts to be passed",
            )
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
        approval_evidence,
        delivery_verdicts,
        completed,
        remaining,
        _string(mapping["last_validation"], "resume state.last_validation"),
        _string(mapping["next_action"], "resume state.next_action"),
    )


def _build_status_payload(
    plan_path: Path,
    status: str,
    completed_task_ids: list[str] | tuple[str, ...],
    remaining_task_ids: list[str] | tuple[str, ...],
    last_validation: str,
    next_action: str,
    approval_source: str,
    delivery_verdicts: Mapping[str, Verdict],
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Build a bound status payload without choosing execution work."""

    manifest = parse_execution_manifest(plan_path.read_text(encoding="utf-8"))
    root = repo_root or _find_repo_root(plan_path)
    try:
        plan_reference = plan_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("plan must be inside the repository root") from exc
    if approval_source not in APPROVAL_SOURCES:
        raise ExecutionContractError(
            "invalid-approval-source",
            f"approval_source must be one of {sorted(APPROVAL_SOURCES)}",
        )
    if set(delivery_verdicts) != set(VERDICT_CATEGORIES):
        raise ExecutionContractError(
            "delivery-verdict-categories",
            "delivery_verdicts must provide exactly the five required categories",
        )
    delivery_payload = build_verdict_payload(VERDICT_CATEGORIES, delivery_verdicts)
    plan_fingerprint = compute_semantic_fingerprint(manifest)
    content_hash = compute_content_sha256(plan_path)
    payload: dict[str, object] = {
        "schema_version": STATE_SCHEMA_VERSION,
        "status": status,
        "plan": plan_reference,
        "plan_fingerprint": plan_fingerprint,
        "content_hash": content_hash,
        "approval_evidence": {
            "source": approval_source,
            "statement": APPROVAL_STATEMENT,
            "plan_fingerprint": plan_fingerprint,
            "content_hash": content_hash,
        },
        "delivery_verdicts": list(delivery_payload["verdicts"].values()),
        "completed_task_ids": list(completed_task_ids),
        "remaining_task_ids": list(remaining_task_ids),
        "last_validation": last_validation,
        "next_action": next_action,
    }
    parse_resume_state(payload)
    return payload


STATUS_FILENAME_RE = re.compile(r"^(?P<base>.+)\.(?P<status>[^.]+)\.yaml$")


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ExecutionContractError(
                "duplicate-status-field", f"Duplicate YAML field: {key}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _load_status_yaml(text: str) -> Mapping[str, object]:
    try:
        payload = yaml.load(text, Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise ExecutionContractError(
            "malformed-status-yaml", f"Status YAML is malformed: {exc}"
        ) from exc
    return _mapping(payload, "status YAML")


def status_sibling_paths(plan_path: Path) -> tuple[Path, ...]:
    """Return the three canonical YAML status siblings for a retained plan."""

    return tuple(
        plan_path.with_name(f"{plan_path.stem}.{status}.yaml")
        for status in ("DONE", "PARTIAL", "BLOCKED")
    )


def _status_filename(path: Path, plan_path: Path) -> str | None:
    match = STATUS_FILENAME_RE.fullmatch(path.name)
    if not match or match.group("base") != plan_path.stem:
        return None
    return match.group("status")


def parse_status_yaml(payload: Mapping[str, object], source_path: Path) -> ResumeState:
    """Parse YAML state and bind its status to the uppercase filename."""

    match = STATUS_FILENAME_RE.fullmatch(source_path.name)
    status_from_filename = match.group("status") if match else None
    if status_from_filename not in STATE_STATUSES:
        raise ExecutionContractError(
            "invalid-status-filename",
            f"Status YAML filename must end in .DONE.yaml, .PARTIAL.yaml, or .BLOCKED.yaml: {source_path.name}",
        )
    state = parse_resume_state(_mapping(payload, "status YAML"))
    if state.status != status_from_filename:
        raise ExecutionContractError(
            "status-filename-mismatch",
            f"Status filename {source_path.name} disagrees with YAML status {state.status}",
        )
    return state


def build_status_yaml(
    plan_path: Path,
    status: str,
    completed_task_ids: Sequence[str],
    remaining_task_ids: Sequence[str],
    last_validation: str,
    next_action: str,
    *,
    approval_source: str,
    delivery_verdicts: Mapping[str, Verdict],
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Build a hash-bound YAML status payload without choosing execution work."""

    payload = _build_status_payload(
        plan_path,
        status,
        tuple(completed_task_ids),
        tuple(remaining_task_ids),
        last_validation,
        next_action,
        approval_source,
        delivery_verdicts,
        repo_root,
    )
    if status not in STATE_STATUSES:
        raise ExecutionContractError(
            "unknown-status", f"status must be one of {sorted(STATE_STATUSES)}"
        )
    return payload


def write_status_yaml(path: Path, payload: Mapping[str, object]) -> None:
    """Write one validated YAML status sibling through an atomic transition."""

    state = parse_status_yaml(payload, path)
    serialized = yaml.safe_dump(
        {
            "schema_version": state.schema_version,
            "status": state.status,
            "plan": state.plan,
            "plan_fingerprint": state.plan_fingerprint,
            "content_hash": state.content_hash,
            "approval_evidence": state.approval_evidence.as_dict(),
            "delivery_verdicts": [
                verdict.as_dict() for verdict in state.delivery_verdicts
            ],
            "completed_task_ids": list(state.completed_task_ids),
            "remaining_task_ids": list(state.remaining_task_ids),
            "last_validation": state.last_validation,
            "next_action": state.next_action,
        },
        sort_keys=False,
    )
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(serialized, encoding="utf-8")
    os.replace(temporary, path)


def _status_binding_findings(
    plan_path: Path,
    state_path: Path,
    state: ResumeState,
    repo_root: Path,
    snapshot: _PlanSnapshot | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    if not _plan_reference_matches(plan_path, state_path, state.plan, repo_root):
        findings.append(
            Finding("plan-binding-mismatch", f"Status plan does not match: {state.plan}")
        )
    try:
        plan_snapshot = (
            snapshot if snapshot is not None else _load_plan_snapshot(plan_path)
        )
    except (OSError, UnicodeError, ExecutionContractError) as exc:
        return findings + [Finding("plan-unreadable", str(exc))]
    if state.plan_fingerprint != plan_snapshot.semantic_fingerprint:
        findings.append(
            Finding(
                "semantic-fingerprint-drift",
                f"Manifest changed after approval: recorded {state.plan_fingerprint} != computed {plan_snapshot.semantic_fingerprint}",
            )
        )
    if state.content_hash != plan_snapshot.content_hash:
        findings.append(
            Finding(
                "content-hash-drift",
                f"Plan bytes changed after approval: recorded {state.content_hash} != computed {plan_snapshot.content_hash}",
            )
        )
    completed = set(state.completed_task_ids)
    remaining = set(state.remaining_task_ids)
    expected_task_ids = set(plan_snapshot.task_ids)
    unknown = (completed | remaining) - expected_task_ids
    if unknown:
        findings.append(Finding("unknown-task-id", f"Status contains unknown task IDs: {sorted(unknown)}"))
    if completed & remaining:
        findings.append(Finding("task-progress-overlap", "Status completed and remaining tasks overlap"))
    if completed | remaining != expected_task_ids:
        findings.append(Finding("incomplete-task-progress", "Status must account for every manifest task exactly once"))
    if state.status == "DONE" and remaining:
        findings.append(Finding("done-with-remaining-tasks", "DONE status must not contain remaining tasks"))
    if state.status != "DONE" and not remaining:
        findings.append(Finding("status-progress-mismatch", "A complete task set must use DONE status"))
    return findings


def discover_status(plan_path: Path) -> StatusDiscovery:
    """Discover exactly one unambiguous YAML status sibling."""

    findings: list[Finding] = []
    yaml_candidates: list[tuple[Path, str]] = []
    prefix = f"{plan_path.stem}."
    try:
        entries = sorted(plan_path.parent.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        return StatusDiscovery(None, None, (Finding("status-directory-unreadable", str(exc)),))

    for entry in entries:
        if entry.resolve() == plan_path.resolve():
            continue
        if not entry.name.startswith(prefix):
            continue
        if entry.is_symlink() and not entry.exists():
            findings.append(Finding("stale-status-sibling", f"Status sibling is a stale symlink: {entry}"))
            continue
        if entry.name.endswith(".tmp"):
            findings.append(Finding("interrupted-status-transition", f"Temporary status transition remains: {entry}"))
            continue
        status = _status_filename(entry, plan_path)
        if status is not None:
            if status not in STATE_STATUSES:
                findings.append(Finding("unknown-status", f"Unknown status filename: {entry.name}"))
            else:
                yaml_candidates.append((entry, status))
            continue
        findings.append(Finding("unknown-status-sibling", f"Unrecognized status sibling: {entry.name}"))

    if len(yaml_candidates) > 1:
        findings.append(Finding("ambiguous-status-siblings", "More than one YAML status sibling was found"))

    state: ResumeState | None = None
    selected_path: Path | None = None
    if len(yaml_candidates) == 1:
        selected_path = yaml_candidates[0][0]
        try:
            state = parse_status_yaml(
                _load_status_yaml(selected_path.read_text(encoding="utf-8")),
                selected_path,
            )
        except (OSError, UnicodeError, ExecutionContractError, TypeError, ValueError) as exc:
            findings.append(Finding(getattr(exc, "code", "malformed-status"), str(exc)))
    return StatusDiscovery(selected_path, state, tuple(findings))


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
    if declared.is_absolute():
        candidates = {declared.resolve()}
    else:
        candidates = {
            (status_path.parent / declared).resolve(),
            (plan_path.parent / declared).resolve(),
            (repo_root / declared).resolve(),
        }
    return plan_path.resolve() in candidates


def _validate_plan(
    path: Path, repo_root: Path, snapshot: _PlanSnapshot | None = None
) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        return [Finding("plan-not-found", f"Plan file not found: {path}")]
    retained_dir = repo_root / "tmp" / "superpowers" / "plans"
    try:
        path.resolve().relative_to(retained_dir.resolve())
    except ValueError:
        findings.append(Finding("plan-outside-retained-directory", f"Plan must be under {retained_dir}"))
    manifest: dict[str, object] | None = None
    try:
        if snapshot is None:
            text = path.read_text(encoding="utf-8")
        else:
            text = snapshot.text
            manifest = snapshot.manifest
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
        if snapshot is None:
            try:
                manifest = parse_execution_manifest(text)
            except ExecutionContractError as exc:
                findings.append(Finding(exc.code, str(exc)))
        if manifest is not None:
            for message in validate_manifest_projection(text, manifest):
                code = (
                    "obsolete-execution-contract"
                    if message.startswith("manifest-only plans must not")
                    else "bootstrap-projection-drift"
                )
                findings.append(Finding(code, message))
    return findings


def validate_plan(path: Path, repo_root: Path) -> list[Finding]:
    return _validate_plan(path, repo_root)


def validate_state(
    plan_path: Path, state_path: Path, repo_root: Path | None = None
) -> list[Finding]:
    """Validate one YAML status sibling bound to the retained plan."""

    effective_root = repo_root or _find_repo_root(plan_path)
    snapshot: _PlanSnapshot | None = None
    if plan_path.is_file():
        try:
            snapshot = _load_plan_snapshot(plan_path)
        except (OSError, UnicodeError, ExecutionContractError):
            pass
    findings = _validate_plan(plan_path, effective_root, snapshot)
    if state_path.suffix.lower() != ".yaml":
        return findings + [
            Finding(
                "status-format-required",
                "Runtime status must use one of the canonical YAML siblings",
            )
        ]
    expected_paths = {path.resolve() for path in status_sibling_paths(plan_path)}
    if state_path.resolve() not in expected_paths:
        findings.append(
            Finding(
                "state-path-mismatch",
                f"YAML status must be one of {sorted(str(path) for path in expected_paths)}",
            )
        )
    if not state_path.is_file():
        return findings + [Finding("state-not-found", f"Resume state not found: {state_path}")]
    try:
        state = parse_status_yaml(
            _load_status_yaml(state_path.read_text(encoding="utf-8")), state_path
        )
    except ExecutionContractError as exc:
        return findings + [Finding(exc.code, str(exc))]
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        return findings + [Finding("malformed-state", str(exc))]
    return findings + _status_binding_findings(
        plan_path, state_path, state, effective_root, snapshot
    )


def build_compact_payload(findings: list[Finding]) -> dict[str, object]:
    blocking = [item for item in findings if item.severity == "blocking"]
    notices = [item for item in findings if item.severity == "notice"]
    return {
        "status": "passed" if not blocking else "failed",
        "finding_counts": {
            "total": len(findings),
            "blocking": len(blocking),
            "notice": len(notices),
        },
        "finding_sample": [
            {"code": item.code, "severity": item.severity}
            for item in findings[:10]
        ],
        "next_action": (
            "All checks passed."
            if not blocking
            else "Resolve blocking plan execution findings."
        ),
    }


def _find_repo_root(start: Path) -> Path:
    for parent in start.resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / ".github").exists():
            return parent
    return start.resolve()


def _format_findings(findings: list[Finding], fmt: str) -> str:
    if fmt == "compact":
        return json.dumps(build_compact_payload(findings))
    if fmt == "json":
        status = "failed" if any(item.severity == "blocking" for item in findings) else "passed"
        return json.dumps(
            {"status": status, "findings": [item.__dict__ for item in findings]},
            indent=2,
        )
    if not findings:
        return "OK: all checks passed."
    return "\n".join(
        f"[{item.severity.upper()}] {item.code}: {item.message}"
        for item in findings
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only plan and resume-state validator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight = subparsers.add_parser("preflight", help="Validate a retained plan")
    preflight.add_argument("path", type=Path)
    preflight.add_argument("--repo-root", type=Path, default=None)
    preflight.add_argument("--format", choices=("text", "json", "compact"), default="text")
    state_check = subparsers.add_parser("state-check", help="Validate a YAML status sibling")
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
