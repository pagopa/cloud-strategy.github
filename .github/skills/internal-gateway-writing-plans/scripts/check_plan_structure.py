#!/usr/bin/env python3
"""Writer-owned structural producer check for Manifest v3 retained plans.

Read-only and dependency-free. It mirrors the structural contract of the
executor parser so producer defects surface during writing. It is not a
mechanical execution authority: the executor `preflight` remains the sole
mechanical gate and must still run on the exact final plan bytes.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

MANIFEST_SCHEMA_VERSION = 3
MANIFEST_VERSION = "execution-manifest/v3"
EXECUTION_OWNER = "/internal-gateway-execute-plans"
CANONICAL_HANDOFF_REQUIRES = (
    "human approval",
    "exact Manifest v3 review",
    "zero blocking preflight findings",
)
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
        "approval",
        "bootstrap",
        "rollout",
        "handoff",
    }
)
DELEGATION_FIELDS = frozenset(
    {"schema_version", "mode", "worker", "result", "receipt", "acceptance"}
)
AUTHORITY_FIELDS = frozenset(
    {
        "normative_owner",
        "execution_owner",
        "worker",
        "caller_owns",
        "protected_paths",
        "no_git_mutation",
    }
)
TASK_FIELDS = frozenset(
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
    }
)
MANIFEST_TARGET_STATES = frozenset({"create", "modify", "inspect"})
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
MANIFEST_PHASES = frozenset({"baseline", "focused", "final"})
MANIFEST_EQUIVALENCE = frozenset({"exact-only", "allowed-if-admissible"})
MANIFEST_BOOTSTRAP_MODES = frozenset({"explicit-single-plan", "manifest-only"})
PROJECTION_BINDING = {
    "controls": "manifest.controls",
    "tasks": "manifest.tasks",
    "validations": "manifest.validations",
    "authority": "manifest.authority_boundaries",
}
CANONICAL_COMPATIBILITY_PROJECTION = (
    "Control Inventory",
    "Task headings",
    "Execution Contract",
)
CANONICAL_DELEGATION = {
    "schema_version": 1,
    "mode": "none",
    "worker": "primary-owner",
    "result": "not_applicable",
    "receipt": None,
    "acceptance": None,
}
REQUIRED_LEVEL2_HEADINGS = (
    "Goal",
    "Global Constraints",
    "Repository Preflight",
    "Control Inventory",
)
REQUIRED_EXECUTION_FIELDS = (
    "Baseline Validation",
    "Recovery Policy",
    "Escalation Conditions",
    "User-Facing Report",
)
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")
CONTROL_ID_RE = re.compile(r"[A-Z][A-Z0-9-]+")
TASK_HEADING_RE = re.compile(r"(?im)^#{2,6}\s+Task(?:\s+\d+)?(?:\s*:|\b)")
TASK_NUMBER_HEADING_RE = re.compile(r"(?im)^#{2,6}\s+Task\s+(\d+)\s*:")
UNCHECKED_TASK_RE = re.compile(r"(?m)^\s*[-*]\s+\[\s\]\s+\S")
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
    {"-C", "-c", "--config-env", "--exec-path", "--git-dir", "--namespace", "--work-tree"}
)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: Literal["blocking", "notice"] = "blocking"


class StructureError(Exception):
    """A structural defect with a stable finding code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _reject_duplicate_json_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string(value: object, label: str) -> str:
    if not _non_empty_string(value):
        raise StructureError("malformed-execution-manifest", f"{label} must be a non-empty string")
    return str(value).strip()


def _bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise StructureError("malformed-execution-manifest", f"{label} must be a boolean")
    return value


def _strings(value: object, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(_non_empty_string(item) for item in value):
        raise StructureError("malformed-execution-manifest", f"{label} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise StructureError("malformed-execution-manifest", f"{label} must not be empty")
    return tuple(str(item).strip() for item in value)


def _unique_strings(value: object, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    values = _strings(value, label, allow_empty=allow_empty)
    if len(set(values)) != len(values):
        raise StructureError("malformed-execution-manifest", f"{label} must not contain duplicate ids")
    return values


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise StructureError("malformed-execution-manifest", f"{label} must be a JSON object")
    return value


def _exact_fields(mapping: Mapping[str, object], expected: frozenset[str], label: str) -> None:
    unknown = set(mapping) - set(expected)
    missing = set(expected) - set(mapping)
    if unknown and missing:
        code = "malformed-execution-manifest"
    elif unknown:
        code = "unknown-manifest-field"
    else:
        code = "missing-manifest-field"
    if unknown or missing:
        details: list[str] = []
        if unknown:
            details.append(f"unknown fields: {sorted(unknown)}")
        if missing:
            details.append(f"missing fields: {sorted(missing)}")
        raise StructureError(code, f"{label} is malformed ({'; '.join(details)})")


def _git_mutating_subcommands(value: str) -> tuple[str, ...]:
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
        raise StructureError(
            "git-mutation-command",
            f"{label} contains prohibited Git mutation: {', '.join(mutations)}",
        )


def _is_git_directory_path(value: str) -> bool:
    return ".git" in Path(value).parts


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


def _level2_heading(text: str, heading: str) -> re.Match[str] | None:
    return re.search(rf"(?m)^## {re.escape(heading)}\s*$", text)


def _require_level2_heading(text: str, heading: str) -> None:
    if _level2_heading(text, heading):
        return
    headings = _extract_headings(text)
    if any(item == heading or item.startswith(f"{heading} ") for item in headings):
        raise StructureError(
            "missing-heading",
            f"Required heading `{heading}` must be the exact level-2 heading `## {heading}` "
            "with no suffix; found it at another heading level or with a suffix",
        )
    raise StructureError("missing-heading", f"Plan missing required heading: {heading}")


def _manifest_fenced_object(text: str, heading: str) -> Mapping[str, object]:
    matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\s*$", text))
    if not matches:
        raise StructureError(
            "missing-execution-manifest",
            f"Plan must contain exactly one `## {heading}` heading with no suffix",
        )
    if len(matches) > 1:
        raise StructureError(
            "duplicate-execution-manifest",
            f"Plan must contain only one `## {heading}` heading",
        )
    start = matches[0].end()
    next_heading = re.search(r"(?m)^#{2,6}\s+", text[start:])
    body = text[start : start + next_heading.start()] if next_heading else text[start:]
    fenced = re.fullmatch(r"\s*```json\s*\n(.*?)\n```\s*", body, re.DOTALL)
    if not fenced:
        if "```json" not in body:
            raise StructureError(
                "malformed-execution-manifest",
                f"`## {heading}` must contain exactly one fenced code block opened with the "
                "`json` language tag and nothing else",
            )
        raise StructureError(
            "malformed-execution-manifest",
            f"`## {heading}` must contain exactly one immediately contained ```json fenced "
            "object with no surrounding prose and no second fence",
        )
    try:
        raw = json.loads(fenced.group(1), object_pairs_hook=_reject_duplicate_json_fields)
    except ValueError as exc:
        message = str(exc)
        code = (
            "duplicate-manifest-field"
            if message.startswith("duplicate JSON field")
            else "malformed-execution-manifest"
        )
        raise StructureError(code, f"`## {heading}` JSON is malformed: {message}") from exc
    return _mapping(raw, heading)


def _entity_ids(value: object, label: str) -> set[str]:
    if not isinstance(value, list):
        raise StructureError("malformed-execution-manifest", f"{label} must be a list")
    return {
        _string(_mapping(item, f"{label}[{index}]")["id"], f"{label}[{index}].id")
        for index, item in enumerate(value)
    }


def _validate_manifest_identity(root: Mapping[str, object]) -> None:
    if not _is_int(root["schema_version"]) or root["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise StructureError(
            "unsupported-manifest-schema",
            f"Execution Manifest schema_version must be {MANIFEST_SCHEMA_VERSION}",
        )
    if root["manifest_version"] != MANIFEST_VERSION:
        raise StructureError(
            "malformed-execution-manifest",
            f"manifest_version must be {MANIFEST_VERSION!r}",
        )
    _string(root["plan_id"], "plan_id")
    if root["repository_root"] != ".":
        raise StructureError(
            "malformed-execution-manifest",
            'repository_root must be exactly "."',
        )


def _validate_authority_boundaries(root: Mapping[str, object]) -> None:
    authority = _mapping(root["authority_boundaries"], "authority_boundaries")
    _exact_fields(authority, AUTHORITY_FIELDS, "authority_boundaries")
    for field in ("normative_owner", "execution_owner", "worker"):
        _string(authority[field], f"authority_boundaries.{field}")
    _strings(authority["caller_owns"], "authority_boundaries.caller_owns", allow_empty=False)
    _strings(authority["protected_paths"], "authority_boundaries.protected_paths", allow_empty=False)
    if _bool(authority["no_git_mutation"], "authority_boundaries.no_git_mutation") is not True:
        raise StructureError(
            "malformed-execution-manifest",
            "authority_boundaries.no_git_mutation must be true",
        )


def _validate_delegation(root: Mapping[str, object]) -> None:
    delegation = _mapping(root["delegation"], "delegation")
    _exact_fields(delegation, DELEGATION_FIELDS, "delegation")
    if not _is_int(delegation["schema_version"]) or delegation["schema_version"] != 1:
        raise StructureError("malformed-execution-manifest", "delegation.schema_version must be 1")
    if delegation["mode"] == "delegated":
        raise StructureError(
            "delegation-not-supported",
            "The Execution Manifest supports only local primary-owner authoring; "
            "do not manufacture worker provenance",
        )
    if delegation["mode"] != "none":
        raise StructureError("malformed-execution-manifest", "delegation.mode must be none")
    if dict(delegation) != CANONICAL_DELEGATION:
        raise StructureError(
            "malformed-execution-manifest",
            "delegation must be the canonical local tuple "
            '{"schema_version": 1, "mode": "none", "worker": "primary-owner", '
            '"result": "not_applicable", "receipt": null, "acceptance": null}',
        )


def _validate_targets(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise StructureError("malformed-execution-manifest", "targets must be a non-empty list")
    target_ids: set[str] = set()
    for index, raw_target in enumerate(value):
        label = f"targets[{index}]"
        target = _mapping(raw_target, label)
        keys = {"id", "path", "state", "condition"} if "condition" in target else {"id", "path", "state"}
        _exact_fields(target, frozenset(keys), label)
        target_id = _string(target["id"], f"{label}.id")
        if target_id in target_ids:
            raise StructureError("malformed-execution-manifest", f"duplicate target id: {target_id}")
        target_ids.add(target_id)
        target_path = _string(target["path"], f"{label}.path")
        if _is_git_directory_path(target_path):
            raise StructureError(
                "git-target-prohibited",
                f"{label}.path must not target the .git directory",
            )
        if target["state"] not in MANIFEST_TARGET_STATES:
            raise StructureError(
                "malformed-execution-manifest",
                f"{label}.state must be one of {sorted(MANIFEST_TARGET_STATES)}",
            )
        if "condition" in target:
            _string(target["condition"], f"{label}.condition")


def _validate_controls(value: object) -> None:
    if not isinstance(value, Mapping):
        raise StructureError(
            "malformed-execution-manifest",
            "controls must be a JSON object mapping Control Inventory IDs to "
            '{"class", "owner", "binding"} entries; an array is rejected',
        )
    if not value:
        raise StructureError("malformed-execution-manifest", "controls must not be empty")
    for control_id, raw_control in value.items():
        label = f"controls.{control_id}"
        control = _mapping(raw_control, label)
        _exact_fields(control, frozenset({"class", "owner", "binding"}), label)
        if control["class"] not in MANIFEST_CONTROL_CLASSES:
            raise StructureError(
                "malformed-execution-manifest",
                f"{label}.class must be one of {sorted(MANIFEST_CONTROL_CLASSES)}",
            )
        _string(control["owner"], f"{label}.owner")
        _strings(control["binding"], f"{label}.binding", allow_empty=False)


def _validate_validations(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise StructureError("malformed-execution-manifest", "validations must be a non-empty list")
    validation_ids: set[str] = set()
    for index, raw_validation in enumerate(value):
        label = f"validations[{index}]"
        validation = _mapping(raw_validation, label)
        fields = {"id", "command", "owner", "pass_signal", "phases"}
        if "equivalence" in validation:
            fields.add("equivalence")
        _exact_fields(validation, frozenset(fields), label)
        validation_id = _string(validation["id"], f"{label}.id")
        if validation_id in validation_ids:
            raise StructureError("duplicate-validation-id", f"Duplicate validation id: {validation_id}")
        validation_ids.add(validation_id)
        command = _string(validation["command"], f"{label}.command")
        _reject_git_mutation(command, f"{label}.command")
        _string(validation["owner"], f"{label}.owner")
        _string(validation["pass_signal"], f"{label}.pass_signal")
        phases = _strings(validation["phases"], f"{label}.phases", allow_empty=False)
        unknown_phases = [phase for phase in phases if phase not in MANIFEST_PHASES]
        if unknown_phases:
            raise StructureError(
                "malformed-execution-manifest",
                f"{label}.phases must be a subset of {sorted(MANIFEST_PHASES)}; found {unknown_phases}",
            )
        if "equivalence" in validation and validation["equivalence"] not in MANIFEST_EQUIVALENCE:
            raise StructureError(
                "malformed-execution-manifest",
                f"{label}.equivalence must be one of {sorted(MANIFEST_EQUIVALENCE)}",
            )


def _validate_manual_obligations(value: object) -> None:
    if not isinstance(value, list):
        raise StructureError("malformed-execution-manifest", "manual_obligations must be a list")
    manual_ids: set[str] = set()
    for index, raw_obligation in enumerate(value):
        label = f"manual_obligations[{index}]"
        obligation = _mapping(raw_obligation, label)
        _exact_fields(obligation, frozenset({"id", "kind", "required", "acceptance"}), label)
        obligation_id = _string(obligation["id"], f"{label}.id")
        if obligation_id in manual_ids:
            raise StructureError(
                "malformed-execution-manifest",
                f"duplicate manual obligation id: {obligation_id}",
            )
        manual_ids.add(obligation_id)
        if obligation["kind"] not in {"human", "external"}:
            raise StructureError(
                "malformed-execution-manifest",
                f'{label}.kind must be "human" or "external"',
            )
        _bool(obligation["required"], f"{label}.required")
        acceptance = _string(obligation["acceptance"], f"{label}.acceptance")
        _reject_git_mutation(acceptance, f"{label}.acceptance")


def _validate_tasks(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise StructureError("malformed-execution-manifest", "tasks must be a non-empty list")
    task_ids: set[str] = set()
    orders: set[int] = set()
    for index, raw_task in enumerate(value):
        label = f"tasks[{index}]"
        task = _mapping(raw_task, label)
        _exact_fields(task, TASK_FIELDS, label)
        task_id = _string(task["id"], f"{label}.id")
        if task_id in task_ids:
            raise StructureError("malformed-execution-manifest", f"duplicate task id: {task_id}")
        task_ids.add(task_id)
        if not _is_int(task["order"]) or task["order"] < 1 or task["order"] in orders:
            raise StructureError(
                "malformed-execution-manifest",
                f"{label}.order must be a unique positive integer",
            )
        orders.add(task["order"])
        if task["posture"] not in MANIFEST_POSTURES:
            raise StructureError(
                "malformed-execution-manifest",
                f"{label}.posture must be one of {sorted(MANIFEST_POSTURES)}",
            )
        objective = _string(task["objective"], f"{label}.objective")
        _reject_git_mutation(objective, f"{label}.objective")
        for field in ("depends_on", "target_ids", "validation_ids", "manual_obligation_ids"):
            _unique_strings(task[field], f"{label}.{field}")
        acceptance = _strings(task["acceptance"], f"{label}.acceptance", allow_empty=False)
        stop_conditions = _strings(task["stop_conditions"], f"{label}.stop_conditions", allow_empty=False)
        for item in (*acceptance, *stop_conditions):
            _reject_git_mutation(item, label)


def _validate_task_references(root: Mapping[str, object]) -> None:
    available_ids = {
        "depends_on": _entity_ids(root["tasks"], "tasks"),
        "target_ids": _entity_ids(root["targets"], "targets"),
        "validation_ids": _entity_ids(root["validations"], "validations"),
        "manual_obligation_ids": _entity_ids(root["manual_obligations"], "manual_obligations"),
    }
    for index, raw_task in enumerate(root["tasks"]):
        task = _mapping(raw_task, f"tasks[{index}]")
        for field, ids in available_ids.items():
            references = _unique_strings(task[field], f"tasks[{index}].{field}")
            unknown = sorted(set(references) - ids)
            if unknown:
                raise StructureError(
                    "unknown-task-reference",
                    f"tasks[{index}].{field} references unknown IDs: {unknown}",
                )


def _validate_retry_policy(value: object) -> None:
    retry = _mapping(value, "retry_policy")
    _exact_fields(
        retry,
        frozenset(
            {
                "initial_attempts",
                "max_context_refills",
                "max_corrective_retries",
                "caller_may_lower",
                "repeat_progress_status",
                "minor_or_cosmetic_reopens",
            }
        ),
        "retry_policy",
    )
    for field in ("initial_attempts", "max_context_refills"):
        if not _is_int(retry[field]) or retry[field] < 0:
            raise StructureError(
                "malformed-execution-manifest",
                f"retry_policy.{field} must be a non-negative integer",
            )
    if retry["initial_attempts"] != 1 or retry["max_context_refills"] != 1:
        raise StructureError(
            "malformed-execution-manifest",
            "retry_policy must retain one initial attempt and one context refill",
        )
    if not _is_int(retry["max_corrective_retries"]) or not 1 <= retry["max_corrective_retries"] <= 5:
        raise StructureError(
            "malformed-execution-manifest",
            "retry_policy.max_corrective_retries must be an integer between 1 and 5",
        )
    _bool(retry["caller_may_lower"], "retry_policy.caller_may_lower")
    if retry["repeat_progress_status"] != "stalled":
        raise StructureError(
            "malformed-execution-manifest",
            'retry_policy.repeat_progress_status must be "stalled"',
        )
    if retry["minor_or_cosmetic_reopens"] is not False:
        raise StructureError(
            "malformed-execution-manifest",
            "retry_policy.minor_or_cosmetic_reopens must be false",
        )


def _validate_approval(value: object) -> None:
    approval = _mapping(value, "approval")
    _exact_fields(
        approval,
        frozenset({"editorial_content_change", "normative_manifest_change"}),
        "approval",
    )
    _string(approval["editorial_content_change"], "approval.editorial_content_change")
    _string(approval["normative_manifest_change"], "approval.normative_manifest_change")


def _validate_bootstrap(value: object) -> None:
    bootstrap = _mapping(value, "bootstrap")
    _exact_fields(
        bootstrap,
        frozenset(
            {
                "mode",
                "compatibility_projection",
                "projection_binding",
                "legacy_only",
                "retirement_evidence",
            }
        ),
        "bootstrap",
    )
    mode = _string(bootstrap["mode"], "bootstrap.mode")
    if mode not in MANIFEST_BOOTSTRAP_MODES:
        raise StructureError(
            "malformed-execution-manifest",
            "bootstrap.mode must be explicit-single-plan or manifest-only",
        )
    projection = _strings(bootstrap["compatibility_projection"], "bootstrap.compatibility_projection")
    if mode == "manifest-only" and projection:
        raise StructureError(
            "malformed-execution-manifest",
            "manifest-only plans must not emit a compatibility projection",
        )
    if mode == "explicit-single-plan" and projection != CANONICAL_COMPATIBILITY_PROJECTION:
        raise StructureError(
            "malformed-execution-manifest",
            "explicit-single-plan compatibility_projection must be "
            '["Control Inventory", "Task headings", "Execution Contract"]',
        )
    binding = _mapping(bootstrap["projection_binding"], "bootstrap.projection_binding")
    _exact_fields(binding, frozenset(PROJECTION_BINDING), "bootstrap.projection_binding")
    if dict(binding) != PROJECTION_BINDING:
        raise StructureError(
            "malformed-execution-manifest",
            "bootstrap.projection_binding is conflicting",
        )
    if bootstrap["legacy_only"] != "reject":
        raise StructureError(
            "malformed-execution-manifest",
            'bootstrap.legacy_only must be "reject"',
        )
    _string(bootstrap["retirement_evidence"], "bootstrap.retirement_evidence")


def _validate_rollout_and_handoff(root: Mapping[str, object]) -> None:
    _strings(root["rollout"], "rollout", allow_empty=False)
    handoff = _mapping(root["handoff"], "handoff")
    _exact_fields(
        handoff,
        frozenset({"next_owner", "requires", "status_sibling", "git_mutation"}),
        "handoff",
    )
    if handoff["next_owner"] != EXECUTION_OWNER:
        raise StructureError(
            "malformed-execution-manifest",
            f"handoff.next_owner must be {EXECUTION_OWNER}",
        )
    requires = _strings(handoff["requires"], "handoff.requires", allow_empty=False)
    missing = [required for required in CANONICAL_HANDOFF_REQUIRES if required not in requires]
    if missing:
        raise StructureError(
            "malformed-execution-manifest",
            f"handoff.requires is missing {missing}",
        )
    if list(requires) != list(CANONICAL_HANDOFF_REQUIRES):
        raise StructureError(
            "non-canonical-handoff-requires",
            "handoff.requires must be exactly "
            f"{list(CANONICAL_HANDOFF_REQUIRES)}; rewrite it with the canonical strings",
        )
    if handoff["status_sibling"] != "none" or handoff["git_mutation"] != "prohibited":
        raise StructureError(
            "malformed-execution-manifest",
            "handoff must prohibit the status sibling (none) and Git mutation (prohibited)",
        )


def _contains_embedded_digest(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"content_sha256", "semantic_fingerprint"} and isinstance(child, str):
                if SHA256_RE.fullmatch(child):
                    return True
            if _contains_embedded_digest(child):
                return True
    elif isinstance(value, list):
        return any(_contains_embedded_digest(item) for item in value)
    return False


def parse_structural_manifest(text: str) -> dict[str, object]:
    """Parse and structurally validate exactly one Execution Manifest object."""

    root = _mapping(_manifest_fenced_object(text, "Execution Manifest"), "Execution Manifest")
    _exact_fields(root, MANIFEST_FIELDS, "Execution Manifest")
    try:
        _validate_manifest_identity(root)
        _validate_authority_boundaries(root)
        _validate_delegation(root)
        _validate_targets(root["targets"])
        _validate_controls(root["controls"])
        _validate_validations(root["validations"])
        _validate_manual_obligations(root["manual_obligations"])
        _validate_tasks(root["tasks"])
        _validate_task_references(root)
        _validate_retry_policy(root["retry_policy"])
        _validate_approval(root["approval"])
        _validate_bootstrap(root["bootstrap"])
        _validate_rollout_and_handoff(root)
    except StructureError:
        raise
    except (TypeError, ValueError) as exc:
        raise StructureError("malformed-execution-manifest", str(exc)) from exc
    if _contains_embedded_digest(root):
        raise StructureError(
            "manifest-hash-self-reference",
            "Execution Manifest must not contain a content or semantic digest value",
        )
    return dict(root)


def _parse_bootstrap_projection(text: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    root = _mapping(_manifest_fenced_object(text, "Execution Contract"), "Execution Contract")
    raw_validations = root.get("validations")
    raw_manual = root.get("manual_obligations", [])
    if not isinstance(raw_validations, list) or not isinstance(raw_manual, list):
        raise StructureError(
            "malformed-execution-contract",
            "Execution Contract projection must contain validation and manual-obligation lists",
        )
    validations: list[dict[str, object]] = []
    validation_ids: set[str] = set()
    for index, raw_validation in enumerate(raw_validations):
        validation = _mapping(raw_validation, f"Execution Contract validations[{index}]")
        validation_id = _string(validation.get("id"), "Execution Contract validation id")
        if validation_id in validation_ids:
            raise StructureError(
                "duplicate-execution-contract-validation-id",
                f"Duplicate Execution Contract validation id: {validation_id}",
            )
        validation_ids.add(validation_id)
        validations.append(
            {
                "id": validation_id,
                "command": _string(
                    validation.get("command"), "Execution Contract validation command"
                ),
                "phases": _strings(
                    validation.get("phases"),
                    "Execution Contract validation phases",
                    allow_empty=False,
                ),
            }
        )
    manual: list[dict[str, object]] = []
    manual_ids: set[str] = set()
    for index, raw_obligation in enumerate(raw_manual):
        obligation = _mapping(raw_obligation, f"Execution Contract manual_obligations[{index}]")
        obligation_id = _string(obligation.get("id"), "Execution Contract manual obligation id")
        if obligation_id in manual_ids:
            raise StructureError(
                "duplicate-execution-contract-manual-id",
                f"Duplicate Execution Contract manual obligation id: {obligation_id}",
            )
        manual_ids.add(obligation_id)
        manual.append({"id": obligation_id})
    return validations, manual


def _markdown_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for heading in REQUIRED_LEVEL2_HEADINGS:
        try:
            _require_level2_heading(text, heading)
        except StructureError as exc:
            findings.append(Finding(exc.code, str(exc)))
    preflight_section = _extract_section(text, "Repository Preflight")
    for required in REQUIRED_EXECUTION_FIELDS:
        if not re.search(
            rf"(?im)^\s*(?:[-*]\s+)?(?:\*\*)?{re.escape(required)}(?:\*\*)?\s*:",
            preflight_section,
        ):
            findings.append(
                Finding(
                    "missing-execution-field",
                    f"`## Repository Preflight` is missing the required bold field "
                    f"`- **{required}:**` with a concrete value",
                )
            )
    global_constraints = _extract_section(text, "Global Constraints")
    if not re.search(r"(?im)^\s*[-*]\s+.*\bno[- ]git\b.*$", global_constraints):
        findings.append(
            Finding(
                "missing-no-git-constraint",
                "`## Global Constraints` must contain an explicit no-Git bullet such as "
                "`- No Git mutation.`",
            )
        )
    if not (TASK_HEADING_RE.search(text) or UNCHECKED_TASK_RE.search(text)):
        findings.append(Finding("missing-task", "Plan must contain at least one task heading"))
    return findings


def _check_control_inventory(text: str, manifest: Mapping[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    inventory_ids: list[str] = []
    stray_rows: list[str] = []
    for line in _extract_section(text, "Control Inventory").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if first in {"ID", "---"} or not first:
            continue
        if CONTROL_ID_RE.fullmatch(first):
            inventory_ids.append(first)
        else:
            stray_rows.append(first)
    controls = manifest.get("controls")
    control_keys = set(controls) if isinstance(controls, Mapping) else set()
    if set(inventory_ids) != control_keys:
        findings.append(
            Finding(
                "bootstrap-projection-drift",
                "Control Inventory projection drift: table IDs do not equal manifest.controls "
                f"keys; table={sorted(set(inventory_ids))} manifest={sorted(control_keys)}. "
                "The inventory table must contain only the header, the separator row, and one "
                "row per control ID in `[A-Z][A-Z0-9-]+` form",
            )
        )
    for first in stray_rows:
        findings.append(
            Finding(
                "inventory-row-not-a-control",
                f"Control Inventory row `{first}` does not use the uppercase `[A-Z][A-Z0-9-]+` "
                "ID form and is not a header or separator; remove it or give it a control ID",
                "notice",
            )
        )
    return findings


def _check_task_headings(text: str, manifest: Mapping[str, object]) -> list[Finding]:
    heading_ids = [f"T{match.group(1)}" for match in TASK_NUMBER_HEADING_RE.finditer(text)]
    tasks = manifest.get("tasks")
    manifest_task_ids = [
        item["id"]
        for item in sorted(tasks or [], key=lambda item: item.get("order", 0))
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    ]
    if heading_ids == manifest_task_ids:
        return []
    return [
        Finding(
            "bootstrap-projection-drift",
            "Task heading projection drift: ordered `## Task N:` headings do not equal "
            f"manifest.tasks IDs in manifest order; headings={heading_ids} "
            f"manifest={manifest_task_ids}. Use one `## Task N: <title>` heading per manifest "
            "task, numbered consecutively, and no other `Task N:` heading",
        )
    ]


def _check_projection_binding(text: str, manifest: Mapping[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    bootstrap = manifest.get("bootstrap")
    if not isinstance(bootstrap, Mapping):
        return [Finding("missing-manifest-field", "Bootstrap projection metadata is missing")]
    if bootstrap.get("projection_binding") != PROJECTION_BINDING:
        findings.append(
            Finding("bootstrap-projection-drift", "Bootstrap projection binding is conflicting")
        )
    if bootstrap.get("legacy_only") != "reject":
        findings.append(Finding("bootstrap-projection-drift", "Bootstrap must reject legacy-only plans"))
    authority = manifest.get("authority_boundaries")
    if not isinstance(authority, Mapping) or authority.get("no_git_mutation") is not True:
        findings.append(
            Finding("bootstrap-projection-drift", "Authority projection drift: no_git_mutation is not true")
        )
    if bootstrap.get("mode") == "manifest-only" and _level2_heading(text, "Execution Contract"):
        findings.append(
            Finding(
                "obsolete-execution-contract",
                "manifest-only plans must not contain an `## Execution Contract` projection; "
                "remove the section and its fenced block",
            )
        )
    if bootstrap.get("mode") == "explicit-single-plan":
        findings.extend(_check_execution_contract_projection(text, manifest))
    return findings


def _check_execution_contract_projection(
    text: str, manifest: Mapping[str, object]
) -> list[Finding]:
    findings: list[Finding] = []
    try:
        projected_validations, projected_manual = _parse_bootstrap_projection(text)
    except StructureError as exc:
        return [Finding(exc.code, f"Execution Contract projection is invalid: {exc}")]
    manifest_by_id = {
        item["id"]: item
        for item in manifest.get("validations") or []
        if isinstance(item, Mapping)
    }
    contract_by_id = {item["id"]: item for item in projected_validations}
    if set(manifest_by_id) != set(contract_by_id):
        findings.append(
            Finding(
                "bootstrap-projection-drift",
                "Execution Contract projection drift: validation IDs do not equal manifest.validations",
            )
        )
    else:
        for validation_id, manifest_item in manifest_by_id.items():
            contract_item = contract_by_id[validation_id]
            if (
                manifest_item["command"] != contract_item["command"]
                or tuple(manifest_item["phases"]) != tuple(contract_item["phases"])
            ):
                findings.append(
                    Finding(
                        "bootstrap-projection-drift",
                        f"Execution Contract projection drift for validation {validation_id}",
                    )
                )
    manifest_manual = {
        item["id"]: item
        for item in manifest.get("manual_obligations") or []
        if isinstance(item, Mapping)
    }
    contract_manual = {item["id"]: item for item in projected_manual}
    if set(manifest_manual) != set(contract_manual):
        findings.append(
            Finding(
                "bootstrap-projection-drift",
                "Execution Contract projection drift: manual obligation IDs do not equal "
                "manifest.manual_obligations",
            )
        )
    return findings


def _producer_notices(plan_path: Path | None, manifest: Mapping[str, object]) -> list[Finding]:
    notices: list[Finding] = []
    plan_id = manifest.get("plan_id")
    if isinstance(plan_id, str) and plan_path is not None and plan_id != plan_path.stem:
        notices.append(
            Finding(
                "plan-id-filename-mismatch",
                f"plan_id `{plan_id}` differs from the retained filename stem "
                f"`{plan_path.stem}`; keep them aligned for traceability",
                "notice",
            )
        )
    tasks = {item["id"] for item in manifest.get("tasks") or [] if isinstance(item, Mapping)}
    validations = {
        item["id"] for item in manifest.get("validations") or [] if isinstance(item, Mapping)
    }
    obligations = {
        item["id"] for item in manifest.get("manual_obligations") or [] if isinstance(item, Mapping)
    }
    resolvable = tasks | validations | obligations
    controls = manifest.get("controls")
    if isinstance(controls, Mapping):
        for control_id, raw_control in controls.items():
            if not isinstance(raw_control, Mapping) or not isinstance(raw_control.get("binding"), list):
                continue
            unresolved = [
                item
                for item in raw_control["binding"]
                if isinstance(item, str) and item not in resolvable
            ]
            if unresolved:
                notices.append(
                    Finding(
                        "control-binding-unresolved",
                        f"Control `{control_id}` binds to IDs that do not resolve to a task, "
                        f"validation, or manual obligation: {unresolved}",
                        "notice",
                    )
                )
    return notices


def check_plan_structure(text: str, plan_path: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    try:
        manifest = parse_structural_manifest(text)
    except StructureError as exc:
        findings.extend(_manifest_heading_variants(text) or [Finding(exc.code, str(exc))])
        findings.extend(_markdown_findings(text))
        return findings
    findings.extend(_markdown_findings(text))
    findings.extend(_check_control_inventory(text, manifest))
    findings.extend(_check_task_headings(text, manifest))
    findings.extend(_check_projection_binding(text, manifest))
    findings.extend(_producer_notices(plan_path, manifest))
    if plan_path is not None:
        retained_dir = _find_repo_root(plan_path) / "tmp" / "superpowers" / "plans"
        if not plan_path.resolve().is_relative_to(retained_dir.resolve()):
            findings.append(
                Finding("plan-outside-retained-directory", f"Plan must be under {retained_dir}")
            )
    return findings


def _manifest_heading_variants(text: str) -> list[Finding]:
    variant = re.search(r"(?im)^##\s*Execution Manifest\b[^\n]*$", text)
    if variant and not _level2_heading(text, "Execution Manifest"):
        return [
            Finding(
                "missing-execution-manifest",
                f"Plan must use the exact heading `## Execution Manifest`; found "
                f"`{variant.group(0).strip()}` with a suffix",
            )
        ]
    return []


def _find_repo_root(start: Path) -> Path:
    for parent in start.resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / ".github").exists():
            return parent
    return start.resolve()


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
            {"code": item.code, "severity": item.severity} for item in findings[:10]
        ],
        "next_action": (
            "Run the executor preflight against the exact final plan bytes."
            if not blocking
            else "Resolve blocking producer structure findings before the executor preflight."
        ),
    }


def _format_findings(findings: list[Finding], fmt: str) -> str:
    if fmt == "compact":
        return json.dumps(build_compact_payload(findings))
    if not findings:
        return "OK: producer structure is ready for the executor preflight."
    return "\n".join(
        f"[{item.severity.upper()}] {item.code}: {item.message}" for item in findings
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Writer-owned structural plan check (read-only, stdlib only)"
    )
    parser.add_argument("path", type=Path, help="Retained plan Markdown path")
    parser.add_argument("--format", choices=("text", "compact"), default="text")
    args = parser.parse_args(argv)

    if not args.path.is_file():
        findings = [Finding("plan-not-found", f"Plan file not found: {args.path}")]
    else:
        try:
            text = args.path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings = [Finding("plan-unreadable", f"Plan content is unreadable: {exc}")]
        else:
            findings = check_plan_structure(text, args.path)
    sys.stdout.write(_format_findings(findings, args.format) + "\n")
    return 1 if any(item.severity == "blocking" for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
