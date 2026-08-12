#!/usr/bin/env python3
"""Read-only validator for retained plans, recovery evidence, and statuses."""
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


CloseoutRoute = Literal[
    "continue-execution",
    "continue-recovery",
    "request-authority",
    "DONE",
    "PARTIAL",
    "BLOCKED",
    "NEEDS_REVIEW",
]


DISCOVERY_CATEGORIES = (
    "repository-runtime",
    "path-executable",
    "absolute-executable",
    "supported-override",
    "native-command",
    "cached-dependency",
)

CONTRACT_SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = 1
CONTRACT_PHASES = frozenset({"baseline", "focused", "final"})
CONTRACT_EQUIVALENCE = frozenset({"exact-only", "allowed-if-admissible"})
CLOSEOUT_OUTCOMES = frozenset(
    {"exact-pass", "equivalent-pass", "warning", "unresolved", "regression"}
)
ALLOWED_STATUSES = frozenset({"DONE", "PARTIAL", "BLOCKED", "NEEDS_REVIEW"})
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

STATUS_FILENAME_RE = re.compile(
    r"^(?P<basename>.+)\.(?P<status>DONE|PARTIAL|BLOCKED|NEEDS_REVIEW)\.md$"
)
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
REQUIRED_STATUS_HEADINGS = (
    "Status",
    "Plan",
    "Plan Fingerprint",
    "Completed",
    "Remaining",
    "Validation",
    "Next",
)
REVIEW_REQUIRED_FIELDS = (
    "Event",
    "Impact",
    "Recovery",
    "Evidence",
    "Decision",
    "Next action",
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
            if any(phase not in CONTRACT_PHASES for phase in phases):
                raise ValueError(f"{label}.phases contains an unsupported phase")
            if "equivalence" in validation and validation["equivalence"] not in CONTRACT_EQUIVALENCE:
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


@dataclass(frozen=True)
class ValidationContract:
    id: str
    command: str
    phases: tuple[Literal["baseline", "focused", "final"], ...]
    required: bool
    success: Literal["exit-code-0"]
    equivalence: Literal["exact-only", "allowed-if-admissible"]


@dataclass(frozen=True)
class ManualObligation:
    id: str
    kind: Literal["human", "external"]
    required: bool
    acceptance: str


@dataclass(frozen=True)
class AuthorityContract:
    autonomous: tuple[str, ...]
    requires_approval: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionContract:
    schema_version: Literal[1]
    validations: tuple[ValidationContract, ...]
    manual_obligations: tuple[ManualObligation, ...]
    authority: AuthorityContract


@dataclass(frozen=True)
class ValidationEquivalence:
    target_did_not_start: bool
    same_checks: bool
    same_inputs: bool
    runtime_not_material: bool

    @property
    def admissible(self) -> bool:
        return all(
            (
                self.target_did_not_start,
                self.same_checks,
                self.same_inputs,
                self.runtime_not_material,
            )
        )


@dataclass(frozen=True)
class DiscoveryResult:
    category: str
    status: Literal["found", "not-found", "not-applicable"]
    candidates: tuple[str, ...]
    evidence: str


@dataclass(frozen=True)
class RecoveryCandidate:
    name: str
    source: str
    safe: bool
    requires_authority: bool
    attempted: bool
    result: Literal["not-run", "passed", "failed", "rejected"]
    evidence_delta: str


@dataclass(frozen=True)
class AuthorityState:
    state: Literal[
        "not-required",
        "required-unrequested",
        "requested-granted",
        "requested-declined",
    ]
    action: str


@dataclass(frozen=True)
class ValidationObligation:
    id: str
    command: str
    required: bool
    outcome: str
    phase: str | None = None
    equivalence: str | None = None
    equivalence_evidence: ValidationEquivalence | None = None
    failure_phase: str | None = None
    discovery_results: tuple[DiscoveryResult, ...] = ()
    candidates: tuple[RecoveryCandidate, ...] = ()
    authority: AuthorityState = AuthorityState("not-required", "")


@dataclass(frozen=True)
class ManualResult:
    id: str
    satisfied: bool
    evidence: str


@dataclass(frozen=True)
class CloseoutEvidence:
    plan_fingerprint: str
    content_hash: str
    tasks_complete: bool
    tasks_remaining: tuple[str, ...]
    fatal_conditions: tuple[str, ...]
    validations: tuple[ValidationObligation, ...]
    manual_obligations: tuple[ManualResult, ...]
    pause_requested: bool = False
    exhaustion_evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class CloseoutDecision:
    route: CloseoutRoute
    reasons: tuple[str, ...]
    next_action: str

    def as_dict(self) -> dict[str, object]:
        return {
            "route": self.route,
            "reason_codes": list(self.reasons),
            "next_action": self.next_action,
        }


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


def _contract_string_list(value: object, label: str) -> tuple[str, ...]:
    return _strings(value, label)


def parse_execution_contract(text: str) -> ExecutionContract:
    matches = list(re.finditer(r"(?m)^## Execution Contract\s*$", text))
    if not matches:
        raise ExecutionContractError(
            "missing-execution-contract", "Plan must contain exactly one ## Execution Contract"
        )
    if len(matches) > 1:
        raise ExecutionContractError(
            "duplicate-execution-contract", "Plan must contain only one ## Execution Contract"
        )

    start = matches[0].end()
    next_heading = re.search(r"(?m)^#{2,6}\s+", text[start:])
    body = text[start : start + next_heading.start()] if next_heading else text[start:]
    body = re.sub(r"\n\s*---\s*$", "\n", body)
    fenced = re.fullmatch(r"\s*```json\s*\n(.*?)\n```\s*", body, re.DOTALL)
    if not fenced:
        raise ExecutionContractError(
            "malformed-execution-contract",
            "Execution Contract must contain exactly one immediately contained ```json fenced object",
        )
    try:
        raw = json.loads(fenced.group(1))
    except json.JSONDecodeError as exc:
        raise ExecutionContractError(
            "malformed-execution-contract", f"Execution Contract JSON is malformed: {exc}"
        ) from exc
    try:
        root = _mapping(raw, "Execution Contract")
        _exact_fields(root, {"schema_version", "validations", "manual_obligations", "authority"}, "Execution Contract")
        version = root["schema_version"]
        if version != CONTRACT_SCHEMA_VERSION:
            raise ExecutionContractError(
                "unsupported-schema-version",
                f"schema_version must be {CONTRACT_SCHEMA_VERSION}",
            )
        raw_validations = root["validations"]
        if not isinstance(raw_validations, list) or not raw_validations:
            raise ValueError("validations must be a non-empty list")
        validations: list[ValidationContract] = []
        seen_ids: set[str] = set()
        for index, raw_validation in enumerate(raw_validations):
            label = f"validations[{index}]"
            item = _mapping(raw_validation, label)
            _exact_fields(item, {"id", "command", "phases", "required", "success", "equivalence"}, label)
            validation_id = _string(item["id"], f"{label}.id")
            if validation_id in seen_ids:
                raise ExecutionContractError("duplicate-validation-id", f"Duplicate validation id: {validation_id}")
            seen_ids.add(validation_id)
            phases = _strings(item["phases"], f"{label}.phases", allow_empty=False)
            if any(phase not in CONTRACT_PHASES for phase in phases):
                raise ValueError(f"{label}.phases must use only {sorted(CONTRACT_PHASES)}")
            success = _string(item["success"], f"{label}.success")
            if success != "exit-code-0":
                raise ValueError(f"{label}.success must be exit-code-0")
            equivalence = _string(item["equivalence"], f"{label}.equivalence")
            if equivalence not in CONTRACT_EQUIVALENCE:
                raise ValueError(f"{label}.equivalence must be one of {sorted(CONTRACT_EQUIVALENCE)}")
            validations.append(
                ValidationContract(
                    validation_id,
                    _string(item["command"], f"{label}.command"),
                    tuple(phases),
                    _bool(item["required"], f"{label}.required"),
                    success,  # type: ignore[arg-type]
                    equivalence,  # type: ignore[arg-type]
                )
            )

        raw_manual = root["manual_obligations"]
        if not isinstance(raw_manual, list):
            raise ValueError("manual_obligations must be a list")
        manual: list[ManualObligation] = []
        manual_ids: set[str] = set()
        for index, raw_obligation in enumerate(raw_manual):
            label = f"manual_obligations[{index}]"
            item = _mapping(raw_obligation, label)
            _exact_fields(item, {"id", "kind", "required", "acceptance"}, label)
            obligation_id = _string(item["id"], f"{label}.id")
            if obligation_id in manual_ids:
                raise ExecutionContractError("duplicate-manual-obligation-id", f"Duplicate manual obligation id: {obligation_id}")
            manual_ids.add(obligation_id)
            kind = _string(item["kind"], f"{label}.kind")
            if kind not in {"human", "external"}:
                raise ValueError(f"{label}.kind must be human or external")
            manual.append(ManualObligation(obligation_id, kind, _bool(item["required"], f"{label}.required"), _string(item["acceptance"], f"{label}.acceptance")))

        authority = _mapping(root["authority"], "authority")
        _exact_fields(authority, {"autonomous", "requires_approval"}, "authority")
        return ExecutionContract(
            1,
            tuple(validations),
            tuple(manual),
            AuthorityContract(
                _contract_string_list(authority["autonomous"], "authority.autonomous"),
                _contract_string_list(authority["requires_approval"], "authority.requires_approval"),
            ),
        )
    except ExecutionContractError:
        raise
    except (TypeError, ValueError) as exc:
        raise ExecutionContractError("malformed-execution-contract", str(exc)) from exc


def _execution_contract_from_manifest(manifest: Mapping[str, object]) -> ExecutionContract:
    """Build the closeout view from the authoritative manifest validations."""

    validations = manifest["validations"]
    if not isinstance(validations, list):
        raise ExecutionContractError(
            "malformed-execution-manifest", "Manifest validations must be a list"
        )
    parsed_validations: list[ValidationContract] = []
    for item in validations:
        if not isinstance(item, Mapping):
            raise ExecutionContractError(
                "malformed-execution-manifest",
                "Manifest validation entries must be objects",
            )
        equivalence = item.get("equivalence", "exact-only")
        if equivalence not in CONTRACT_EQUIVALENCE:
            raise ExecutionContractError(
                "malformed-execution-manifest",
                "Manifest validation equivalence is invalid",
            )
        parsed_validations.append(
            ValidationContract(
                _string(item["id"], "manifest validation id"),
                _string(item["command"], "manifest validation command"),
                tuple(_strings(item["phases"], "manifest validation phases", allow_empty=False)),
                True,
                "exit-code-0",
                equivalence,  # type: ignore[arg-type]
            )
        )
    manual_values = manifest["manual_obligations"]
    if not isinstance(manual_values, list):
        raise ExecutionContractError(
            "malformed-execution-manifest", "Manifest manual_obligations must be a list"
        )
    parsed_manual = tuple(
        ManualObligation(
            _string(item["id"], "manifest manual obligation id"),
            _string(item["kind"], "manifest manual obligation kind"),  # type: ignore[arg-type]
            _bool(item["required"], "manifest manual obligation required"),
            _string(item["acceptance"], "manifest manual obligation acceptance"),
        )
        for item in manual_values
        if isinstance(item, Mapping)
    )
    return ExecutionContract(
        1,
        tuple(parsed_validations),
        parsed_manual,
        AuthorityContract(
            ("read-only-inspection", "local-validation"),
            (
                "read-only-discovery",
                "scope-expansion",
                "plan-modification",
                "status-sibling",
                "git-mutation",
                "dependency-installation",
            ),
        ),
    )


def parse_plan_contract(text: str) -> ExecutionContract:
    """Return the closeout contract, with the manifest as the sole authority."""

    manifest = parse_execution_manifest(text)
    bootstrap = manifest["bootstrap"]
    if not isinstance(bootstrap, Mapping):
        raise ExecutionContractError(
            "malformed-execution-manifest", "Manifest bootstrap metadata is missing"
        )
    if bootstrap["mode"] == "explicit-single-plan":
        projection_findings = validate_manifest_projection(text, manifest)
        if projection_findings:
            raise ExecutionContractError(
                "bootstrap-projection-drift", "; ".join(projection_findings)
            )
        # The old object is a compatibility projection only. It supplies the
        # legacy closeout equivalence policy while the manifest owns identity,
        # commands, phases, authority, and task bindings.
        return parse_execution_contract(text)
    if re.search(r"(?m)^## Execution Contract\s*$", text):
        raise ExecutionContractError(
            "obsolete-execution-contract",
            "manifest-only plans must not contain an Execution Contract projection",
        )
    return _execution_contract_from_manifest(manifest)


def _parse_equivalence(value: object, label: str) -> ValidationEquivalence:
    mapping = _mapping(value, label)
    expected = {"target_did_not_start", "same_checks", "same_inputs", "runtime_not_material"}
    _exact_fields(mapping, expected, label)
    return ValidationEquivalence(
        _bool(mapping["target_did_not_start"], f"{label}.target_did_not_start"),
        _bool(mapping["same_checks"], f"{label}.same_checks"),
        _bool(mapping["same_inputs"], f"{label}.same_inputs"),
        _bool(mapping["runtime_not_material"], f"{label}.runtime_not_material"),
    )


def _parse_discovery(value: object, label: str) -> DiscoveryResult:
    mapping = _mapping(value, label)
    _exact_fields(mapping, {"category", "status", "candidates", "evidence"}, label)
    category = _string(mapping["category"], f"{label}.category")
    status = _string(mapping["status"], f"{label}.status")
    if category not in DISCOVERY_CATEGORIES:
        raise ValueError(f"{label}.category must be one of {list(DISCOVERY_CATEGORIES)}")
    if status not in {"found", "not-found", "not-applicable"}:
        raise ValueError(f"{label}.status is invalid")
    return DiscoveryResult(category, status, _strings(mapping["candidates"], f"{label}.candidates"), _string(mapping["evidence"], f"{label}.evidence"))


def _parse_candidate(value: object, label: str) -> RecoveryCandidate:
    mapping = _mapping(value, label)
    _exact_fields(mapping, {"name", "source", "safe", "requires_authority", "attempted", "result", "evidence_delta"}, label)
    result = _string(mapping["result"], f"{label}.result")
    if result not in {"not-run", "passed", "failed", "rejected"}:
        raise ValueError(f"{label}.result is invalid")
    candidate = RecoveryCandidate(
        _string(mapping["name"], f"{label}.name"),
        _string(mapping["source"], f"{label}.source"),
        _bool(mapping["safe"], f"{label}.safe"),
        _bool(mapping["requires_authority"], f"{label}.requires_authority"),
        _bool(mapping["attempted"], f"{label}.attempted"),
        result,  # type: ignore[arg-type]
        _string(mapping["evidence_delta"], f"{label}.evidence_delta"),
    )
    if not candidate.attempted and candidate.result != "not-run":
        raise ValueError(f"{label} not-run candidates must have result not-run")
    if candidate.attempted and not candidate.evidence_delta:
        raise ValueError(f"{label}.evidence_delta is required after an attempt")
    return candidate


def _parse_authority(value: object, label: str) -> AuthorityState:
    mapping = _mapping(value, label)
    _exact_fields(mapping, {"state", "action"}, label)
    state = _string(mapping["state"], f"{label}.state")
    allowed = {"not-required", "required-unrequested", "requested-granted", "requested-declined"}
    if state not in allowed:
        raise ValueError(f"{label}.state is invalid")
    return AuthorityState(state, _string(mapping["action"], f"{label}.action") if mapping["action"] else "")  # type: ignore[arg-type]


def parse_closeout_evidence(payload: Mapping[str, object]) -> CloseoutEvidence:
    mapping = _mapping(payload, "closeout evidence")
    allowed = {"plan_fingerprint", "content_hash", "tasks_complete", "tasks_remaining", "pause_requested", "fatal_conditions", "validations", "manual_obligations", "exhaustion_evidence"}
    unknown = set(mapping) - allowed
    missing = {
        "plan_fingerprint",
        "content_hash",
        "tasks_complete",
        "tasks_remaining",
        "validations",
    } - set(mapping)
    if unknown or missing:
        details = []
        if unknown:
            details.append(f"unknown fields: {sorted(unknown)}")
        if missing:
            details.append(f"missing fields: {sorted(missing)}")
        raise ValueError(f"closeout evidence is malformed ({'; '.join(details)})")
    raw_validations = mapping["validations"]
    if not isinstance(raw_validations, list):
        raise ValueError("validations must be a list")
    validations: list[ValidationObligation] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_validations):
        label = f"validations[{index}]"
        item = _mapping(raw, label)
        required = {"id", "command", "required", "outcome"}
        optional = {"phase", "equivalence", "equivalence_evidence", "failure_phase", "discovery_results", "candidates", "authority"}
        unknown = set(item) - required - optional
        missing = required - set(item)
        if unknown or missing:
            details = []
            if unknown:
                details.append(f"unknown fields: {sorted(unknown)}")
            if missing:
                details.append(f"missing fields: {sorted(missing)}")
            raise ValueError(f"{label} is malformed ({'; '.join(details)})")
        validation_id = _string(item["id"], f"{label}.id")
        if validation_id in seen_ids:
            raise ValueError(f"duplicate validation id: {validation_id}")
        seen_ids.add(validation_id)
        outcome = _string(item["outcome"], f"{label}.outcome")
        if outcome not in CLOSEOUT_OUTCOMES:
            raise ValueError(f"{label}.outcome must be one of {sorted(CLOSEOUT_OUTCOMES)}")
        equivalence = item.get("equivalence")
        equivalence_policy = _string(equivalence, f"{label}.equivalence") if equivalence is not None and isinstance(equivalence, str) else None
        equivalence_evidence = _parse_equivalence(item["equivalence_evidence"], f"{label}.equivalence_evidence") if "equivalence_evidence" in item else None
        if isinstance(equivalence, Mapping):
            equivalence_evidence = _parse_equivalence(equivalence, f"{label}.equivalence")
            equivalence_policy = "allowed-if-admissible"
        if outcome == "equivalent-pass" and equivalence_evidence is None:
            raise ValueError(f"{label}.equivalence_evidence is required for equivalent-pass")
        discovery = tuple(_parse_discovery(value, f"{label}.discovery_results[{index2}]") for index2, value in enumerate(item.get("discovery_results", [])))
        candidates = tuple(_parse_candidate(value, f"{label}.candidates[{index2}]") for index2, value in enumerate(item.get("candidates", [])))
        authority = _parse_authority(item["authority"], f"{label}.authority") if "authority" in item else AuthorityState("not-required", "")
        validations.append(ValidationObligation(validation_id, _string(item["command"], f"{label}.command"), _bool(item["required"], f"{label}.required"), outcome, item.get("phase"), equivalence_policy, equivalence_evidence, item.get("failure_phase"), discovery, candidates, authority))
    raw_manual = mapping.get("manual_obligations", [])
    if not isinstance(raw_manual, list):
        raise ValueError("manual_obligations must be a list")
    manuals: list[ManualResult] = []
    manual_ids: set[str] = set()
    for index, raw in enumerate(raw_manual):
        label = f"manual_obligations[{index}]"
        item = _mapping(raw, label)
        _exact_fields(item, {"id", "satisfied", "evidence"}, label)
        manual_id = _string(item["id"], f"{label}.id")
        if manual_id in manual_ids:
            raise ValueError(f"duplicate manual obligation id: {manual_id}")
        manual_ids.add(manual_id)
        manuals.append(ManualResult(manual_id, _bool(item["satisfied"], f"{label}.satisfied"), _string(item["evidence"], f"{label}.evidence")))
    return CloseoutEvidence(
        _string(mapping["plan_fingerprint"], "plan_fingerprint"),
        _string(mapping["content_hash"], "content_hash"),
        _bool(mapping["tasks_complete"], "tasks_complete"),
        _strings(mapping["tasks_remaining"], "tasks_remaining"),
        _strings(mapping.get("fatal_conditions", []), "fatal_conditions"),
        tuple(validations),
        tuple(manuals),
        _bool(mapping.get("pause_requested", False), "pause_requested"),
        _strings(mapping.get("exhaustion_evidence", []), "exhaustion_evidence"),
    )


def _closeout_decision(route: CloseoutRoute, reasons: list[str], next_action: str) -> CloseoutDecision:
    return CloseoutDecision(route, tuple(reasons[:6]), next_action)


def _validate_bound_evidence(contract: ExecutionContract, evidence: CloseoutEvidence) -> dict[str, ValidationObligation]:
    expected = {item.id: item for item in contract.validations}
    actual: dict[str, ValidationObligation] = {}
    for validation in evidence.validations:
        if validation.id in actual:
            raise ValueError(f"duplicate validation id: {validation.id}")
        if validation.id not in expected:
            raise ValueError(f"unknown validation id: {validation.id}")
        declared = expected[validation.id]
        if validation.command != declared.command:
            raise ValueError(f"command mismatch for validation {validation.id}")
        if validation.required != declared.required:
            raise ValueError(f"required flag mismatch for validation {validation.id}")
        if validation.equivalence != declared.equivalence:
            raise ValueError(f"equivalence policy mismatch for validation {validation.id}")
        if validation.outcome == "equivalent-pass" and declared.equivalence == "exact-only":
            raise ValueError(f"equivalence is not allowed for validation {validation.id}")
        if validation.phase is not None and validation.phase not in declared.phases:
            raise ValueError(f"invalid phase for validation {validation.id}")
        for candidate in validation.candidates:
            action = validation.authority.action
            if validation.authority.state == "required-unrequested" and action not in contract.authority.requires_approval:
                raise ValueError(f"undeclared authority action for validation {validation.id}: {action}")
            if validation.authority.state == "not-required" and action and action not in contract.authority.autonomous and action not in contract.authority.requires_approval:
                raise ValueError(f"undeclared authority action for validation {validation.id}: {action}")
        actual[validation.id] = validation
    missing = [item.id for item in contract.validations if item.id not in actual]
    required_missing = [item.id for item in contract.validations if item.required and item.id not in actual]
    if required_missing:
        raise ValueError(f"missing required validation: {', '.join(required_missing)}")
    if missing:
        raise ValueError(f"missing plan validation: {', '.join(missing)}")
    manual_expected = {item.id for item in contract.manual_obligations}
    manual_actual = {item.id for item in evidence.manual_obligations}
    if manual_actual - manual_expected:
        raise ValueError(f"unknown manual obligation: {sorted(manual_actual - manual_expected)[0]}")
    missing_manual = manual_expected - manual_actual
    if missing_manual:
        raise ValueError(f"missing manual obligation: {sorted(missing_manual)[0]}")
    return actual


def _recovery_state(validation: ValidationObligation) -> tuple[bool, bool, bool, bool]:
    categories = [item.category for item in validation.discovery_results]
    complete = len(categories) == len(DISCOVERY_CATEGORIES) and set(categories) == set(DISCOVERY_CATEGORIES)
    duplicate = len(categories) != len(set(categories))
    safe_untried = any(candidate.safe and not candidate.requires_authority and not candidate.attempted and candidate.result == "not-run" for candidate in validation.candidates)
    authority_needed = any(candidate.requires_authority and not candidate.attempted and candidate.result == "not-run" for candidate in validation.candidates) and validation.authority.state == "required-unrequested"
    return complete, duplicate, safe_untried, authority_needed


def classify_closeout(contract: ExecutionContract, evidence: CloseoutEvidence | Mapping[str, object]) -> CloseoutDecision:
    if not isinstance(evidence, CloseoutEvidence):
        evidence = parse_closeout_evidence(evidence)
    bound = _validate_bound_evidence(contract, evidence)
    if evidence.fatal_conditions:
        return _closeout_decision("BLOCKED", ["fatal-condition-exhausted"], "Resolve the fatal condition before resuming execution.")
    if not evidence.tasks_complete or evidence.tasks_remaining:
        if evidence.pause_requested:
            return _closeout_decision("PARTIAL", ["pause-requested", "unfinished-tasks"], "Resume the first remaining executable task.")
        return _closeout_decision("continue-execution", ["unfinished-tasks"], "Continue execution with the first remaining task.")

    unresolved = [item for item in bound.values() if item.outcome in {"unresolved", "regression"} or (item.outcome == "equivalent-pass" and (item.equivalence_evidence is None or not item.equivalence_evidence.admissible)) or (item.outcome == "warning" and item.required)]
    for validation in unresolved:
        complete, duplicate, safe_untried, authority_needed = _recovery_state(validation)
        if duplicate:
            raise ValueError(f"structured recovery has duplicate discovery category for {validation.id}")
        if not complete:
            raise ValueError(f"structured recovery is incomplete for {validation.id}")
        if not validation.failure_phase:
            raise ValueError(f"structured recovery requires failure phase for {validation.id}")
        if safe_untried:
            return _closeout_decision("continue-recovery", ["safe-recovery-candidate", f"validation:{validation.id}"], f"Run the next safe recovery candidate for {validation.id}.")
        if authority_needed:
            return _closeout_decision("request-authority", ["authority-required", f"validation:{validation.id}"], f"Request approval for the recovery action for {validation.id}.")
        if validation.authority.state == "requested-declined":
            return _closeout_decision("NEEDS_REVIEW", ["authority-declined", f"validation:{validation.id}"], "Obtain the required authority, then rerun closeout-check.")
        if any(not candidate.attempted and candidate.result == "not-run" for candidate in validation.candidates):
            raise ValueError(f"structured recovery has an unclassified candidate for {validation.id}")
    if unresolved:
        return _closeout_decision(
            "NEEDS_REVIEW",
            ["recovery-exhausted"],
            "Review the material failure and decide whether to repair, narrow scope, or accept the gap.",
        )
    declared_manual = {item.id: item for item in contract.manual_obligations}
    pending_external = [
        item.id
        for item in evidence.manual_obligations
        if not item.satisfied
        and declared_manual[item.id].required
        and declared_manual[item.id].kind == "external"
    ]
    pending_human = [
        item.id
        for item in evidence.manual_obligations
        if not item.satisfied
        and declared_manual[item.id].required
        and declared_manual[item.id].kind == "human"
    ]
    follow_up_reasons: list[str] = []
    if pending_external:
        follow_up_reasons.append("external-follow-up-pending")
    if pending_human:
        follow_up_reasons.append("offline-human-review-pending")
    if follow_up_reasons:
        return _closeout_decision(
            "DONE",
            ["all-required-validations-passed", *follow_up_reasons],
            "No further execution is required; record pending external or human evidence as offline follow-up.",
        )
    return _closeout_decision("DONE", ["all-required-validations-passed"], "No further execution is required.")


def status_for_route(route: CloseoutRoute) -> str | None:
    if route in {"continue-execution", "continue-recovery", "request-authority"}:
        return None
    return route


def compute_sha256(path: Path) -> str:
    return compute_content_sha256(path)


def compute_content_sha256(path: Path) -> str:
    """Hash the exact retained-plan bytes for external audit binding."""

    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


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


def _extract_plan_reference(text: str) -> str | None:
    for line in _extract_section(text, "Plan").splitlines():
        value = line.strip().strip("`").strip()
        if value:
            return value
    return None


def _sha256_in_section(text: str, heading: str) -> str | None:
    for line in _extract_section(text, heading).splitlines():
        value = line.strip().strip("`").strip()
        if SHA256_RE.fullmatch(value):
            return value if value.startswith("sha256:") else f"sha256:{value}"
    return None


def _plan_hash_bindings(plan_path: Path) -> tuple[str, str]:
    manifest = parse_execution_manifest(plan_path.read_text())
    return compute_semantic_fingerprint(manifest), compute_content_sha256(plan_path)


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
            contract = parse_execution_contract(text)
        except ExecutionContractError as exc:
            findings.append(f"Execution Contract projection is invalid: {exc}")
        else:
            manifest_validations = manifest.get("validations")
            manifest_by_id = {
                item["id"]: item
                for item in manifest_validations or []
                if isinstance(item, Mapping)
            }
            contract_by_id = {item.id: item for item in contract.validations}
            if set(manifest_by_id) != set(contract_by_id):
                findings.append(
                    "Execution Contract projection drift: validation IDs do not equal manifest.validations"
                )
            else:
                for validation_id, manifest_item in manifest_by_id.items():
                    contract_item = contract_by_id[validation_id]
                    if (
                        manifest_item["command"] != contract_item.command
                        or tuple(manifest_item["phases"]) != contract_item.phases
                    ):
                        findings.append(
                            f"Execution Contract projection drift for validation {validation_id}"
                        )
            manifest_manual = {
                item["id"]: item
                for item in manifest.get("manual_obligations", [])
                if isinstance(item, Mapping)
            }
            contract_manual = {item.id: item for item in contract.manual_obligations}
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


def _parse_status_from_filename(path: Path) -> str | None:
    match = STATUS_FILENAME_RE.match(path.name)
    return match.group("status") if match else None


def _parse_status_from_content(text: str) -> str | None:
    for line in text.splitlines():
        value = line.strip().strip("`")
        if value in ALLOWED_STATUSES:
            return value
    return None


def _validate_status_evidence(text: str, status: str | None) -> list[Finding]:
    findings: list[Finding] = []
    baseline = _extract_section(text, "Baseline Validation")
    final = _extract_section(text, "Validation")
    recovery = _extract_section(text, "Recovery Attempts")
    decision = _extract_section(text, "Closeout Decision")
    exhaustion = _extract_section(text, "Recovery Exhaustion")
    classification = _extract_section(text, "Failure Classification")
    review = _extract_section(text, "Review Required")
    if baseline and final:
        baseline_commands = set(re.findall(r"`([^`\n]+)`", baseline))
        final_commands = set(re.findall(r"`([^`\n]+)`", final))
        if not baseline_commands.intersection(final_commands):
            findings.append(Finding("validation-delta-mismatch", "Baseline and final validation must include an identical command"))
    if status in ALLOWED_STATUSES:
        if not decision:
            findings.append(Finding("missing-closeout-decision", "Terminal or paused status requires ## Closeout Decision"))
        if not recovery:
            findings.append(Finding("missing-recovery-attempts", "Terminal or paused status requires ## Recovery Attempts"))
    if status in {"BLOCKED", "NEEDS_REVIEW"} and not exhaustion:
        findings.append(Finding("missing-recovery-exhaustion", f"{status} requires ## Recovery Exhaustion"))
    if status == "NEEDS_REVIEW":
        if not review:
            findings.append(Finding("missing-review-request", "NEEDS_REVIEW requires ## Review Required"))
        else:
            missing_fields = [
                field
                for field in REVIEW_REQUIRED_FIELDS
                if not re.search(rf"(?im)^\s*[-*]\s+{re.escape(field)}\s*:", review)
            ]
            if missing_fields:
                findings.append(
                    Finding(
                        "incomplete-review-request",
                        "Review Required is missing: " + ", ".join(missing_fields),
                    )
                )
        lowered = (decision + "\n" + classification + "\n" + exhaustion + "\n" + review).lower()
        if not any(
            marker in lowered
            for marker in (
                "material",
                "task-local regression",
                "recovery-exhausted",
                "recovery exhausted",
                "authority-declined",
                "fatal",
                "unsafe",
                "failed",
                "regression",
                "plan drift",
                "scope expansion",
            )
        ):
            findings.append(Finding("needs-review-without-bound-reason", "NEEDS_REVIEW requires a material failure, exhausted recovery, or declined authority"))
    if status == "BLOCKED":
        lowered = (decision + "\n" + classification + "\n" + exhaustion).lower()
        if not any(marker in lowered for marker in ("fatal", "task-local regression", "unsafe")):
            findings.append(Finding("blocked-without-fatal-condition", "BLOCKED requires an exhausted fatal condition"))
    if classification and not any(marker in classification.lower() for marker in ("none", "task-local regression", "pre-existing", "unrelated", "external", "environmental", "unknown")):
        findings.append(Finding("invalid-failure-classification", "Failure Classification must use a contract classification or none"))
    return findings


def validate_status(path: Path) -> list[Finding]:
    if not path.is_file():
        return [Finding("status-not-found", f"Status file not found: {path}")]
    text = path.read_text()
    findings: list[Finding] = []
    headings = set(_extract_headings(text))
    status_file = _parse_status_from_filename(path)
    status_content = _parse_status_from_content(text)
    if status_file is None:
        findings.append(Finding("unknown-status", f"Status filename must use one of {sorted(ALLOWED_STATUSES)}"))
    elif status_content is not None and status_file != status_content:
        findings.append(Finding("status-mismatch", f"Filename status {status_file} != content status {status_content}"))
    for required in REQUIRED_STATUS_HEADINGS:
        if required not in headings:
            findings.append(Finding("missing-heading", f"Status missing required heading: {required}"))
    findings.extend(_validate_status_evidence(text, status_file))
    return findings


def validate_resume(plan_path: Path, status_path: Path, repo_root: Path | None = None) -> list[Finding]:
    effective_root = repo_root or _find_repo_root(plan_path)
    findings = validate_plan(plan_path, effective_root) + validate_status(status_path)
    if any(item.severity == "blocking" for item in findings):
        return findings
    text = status_path.read_text()
    declared = _extract_plan_reference(text)
    if declared is None:
        findings.append(Finding("missing-plan-binding", "Status must declare the plan path"))
    elif not _plan_reference_matches(plan_path, status_path, declared, effective_root):
        findings.append(Finding("plan-binding-mismatch", f"Status plan reference does not match the validated plan: {declared}"))
    try:
        semantic_fingerprint, content_hash = _plan_hash_bindings(plan_path)
    except ExecutionContractError as exc:
        findings.append(Finding(exc.code, str(exc)))
        return findings
    recorded_semantic = _sha256_in_section(text, "Plan Fingerprint")
    if recorded_semantic is None:
        findings.append(
            Finding(
                "missing-fingerprint",
                "Status must contain a sha256: semantic Plan Fingerprint",
            )
        )
    elif recorded_semantic != semantic_fingerprint:
        findings.append(
            Finding(
                "semantic-fingerprint-drift",
                f"Manifest changed after approval: recorded {recorded_semantic} != computed {semantic_fingerprint}",
            )
        )
    recorded_content = _sha256_in_section(text, "Content Hash")
    if recorded_content is None:
        findings.append(
            Finding(
                "missing-content-hash",
                "Manifest-bound status must contain a sha256: Content Hash audit binding",
            )
        )
    elif recorded_content != content_hash:
        findings.append(
            Finding(
                "content-hash-drift",
                f"Plan bytes changed after approval: recorded {recorded_content} != computed {content_hash}",
            )
        )
    return findings


def validate_completion(plan_path: Path, status_path: Path, repo_root: Path | None = None) -> list[Finding]:
    findings = validate_resume(plan_path, status_path, repo_root)
    if any(item.severity == "blocking" for item in findings):
        return findings
    if _parse_status_from_filename(status_path) != "DONE":
        findings.append(Finding("not-done", "Completion requires DONE status"))
    remaining = _extract_section(status_path.read_text(), "Remaining").strip().lower()
    if remaining and remaining not in {"none", "- none"}:
        findings.append(Finding("remaining-items", "DONE status requires no remaining items"))
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
    parser = argparse.ArgumentParser(description="Read-only plan execution validator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("preflight", "Validate a plan file"), ("status-check", "Validate a status file")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("path", type=Path)
        command.add_argument("--format", choices=("text", "json", "compact"), default="text")
        if name == "preflight":
            command.add_argument("--repo-root", type=Path, default=None)
    for name, help_text in (("resume-check", "Validate resume safety"), ("completion-check", "Validate completion readiness")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("plan", type=Path)
        command.add_argument("status", type=Path)
        command.add_argument("--repo-root", type=Path, default=None)
        command.add_argument("--format", choices=("text", "json", "compact"), default="text")
    closeout = subparsers.add_parser("closeout-check", help="Classify bound closeout evidence")
    closeout.add_argument("plan", type=Path)
    closeout.add_argument("evidence", type=Path)
    closeout.add_argument("--format", choices=("text", "json", "compact"), default="text")
    args = parser.parse_args(argv)

    if args.command == "closeout-check":
        try:
            repo_root = _find_repo_root(args.plan)
            plan_findings = validate_plan(args.plan, repo_root)
            if any(item.severity == "blocking" for item in plan_findings):
                raise ValueError("plan preflight failed")
            contract = parse_plan_contract(args.plan.read_text())
            evidence = parse_closeout_evidence(json.loads(args.evidence.read_text()))
            semantic_fingerprint, content_hash = _plan_hash_bindings(args.plan)
            if evidence.plan_fingerprint != semantic_fingerprint:
                raise ValueError("semantic plan fingerprint mismatch")
            if evidence.content_hash != content_hash:
                raise ValueError("content hash mismatch")
            decision = classify_closeout(contract, evidence)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            sys.stderr.write(f"Invalid closeout evidence: {exc}\n")
            return 1
        if args.format == "compact" or args.format == "json":
            output = json.dumps(decision.as_dict(), indent=None if args.format == "compact" else 2)
        else:
            output = f"Route: {decision.route}\nReason codes: {', '.join(decision.reasons)}\nNext action: {decision.next_action}"
        sys.stdout.write(output + "\n")
        return 0

    if args.command == "preflight":
        findings = validate_plan(args.path, args.repo_root or _find_repo_root(args.path))
    elif args.command == "status-check":
        findings = validate_status(args.path)
    elif args.command == "resume-check":
        findings = validate_resume(args.plan, args.status, args.repo_root)
    else:
        findings = validate_completion(args.plan, args.status, args.repo_root)
    sys.stdout.write(_format_findings(findings, args.format) + "\n")
    return 1 if any(item.severity == "blocking" for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
