from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from home_sync_contract import (
    CatalogResource,
    RuntimeSupportRow,
    TARGET_ORDER,
    load_home_sync_catalog,
    load_runtime_support_matrix,
    resolve_support_row,
    runtime_agent_root,
    runtime_skill_root,
    state_root_for_home,
)

from agent_translation import target_extension, translate_agent_for_target

MANIFEST_PATH = "manifest.json"
LAST_PLAN_PATH = "last-plan.json"
LAST_AUDIT_PATH = "last-audit.json"
LOCK_PATH = "locks/home-ai-resources.lock"
NORMALIZATION_VERSION = "v1"
TEXT_EXTENSIONS = (".md", ".txt", ".yml", ".yaml", ".json", ".sh", ".py")
IGNORED_SYNC_PARTS = {".venv", "__pycache__", ".pytest_cache"}
IGNORED_SYNC_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class ManagedResource:
    target: str
    resource_id: str
    resource_family: str
    source_path: str
    target_path: str
    source_hash: str
    content_hash: str
    last_action: str

    def to_dict(self) -> dict[str, str]:
        return {
            "target": self.target,
            "resource_family": self.resource_family,
            "resource_id": self.resource_id,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "source_hash": self.source_hash,
            "content_hash": self.content_hash,
            "last_action": self.last_action,
        }


@dataclass(frozen=True)
class HomeSyncOperation:
    target: str
    action: str
    path: str
    reason: str
    code: str | None = None
    source_path: str | None = None
    resource_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "target": self.target,
            "action": self.action,
            "path": self.path,
            "reason": self.reason,
            "code": self.code,
            "source_path": self.source_path,
            "resource_id": self.resource_id,
        }


@dataclass(frozen=True)
class HomeSyncPlan:
    source_root: Path
    home_root: Path
    state_root: Path
    mode: str
    selected_targets: tuple[str, ...]
    source_revision: str | None
    source_resources_considered: int
    operations: tuple[HomeSyncOperation, ...]
    desired_resources: tuple[ManagedResource, ...]
    missing_dirs: tuple[str, ...]
    unsupported_families_by_target: dict[str, tuple[str, ...]]
    residual_drift: tuple[str, ...]

    def blocked_codes(self) -> list[str]:
        return sorted(
            {
                operation.code
                for operation in self.operations
                if operation.action == "blocked" and operation.code
            }
        )

    def to_dict(self) -> dict[str, object]:
        blocked_codes = self.blocked_codes()
        validation = "blocked" if blocked_codes else ("warning" if self.residual_drift else "ready")
        return {
            "mode": self.mode,
            "selected_targets": list(self.selected_targets),
            "source_root": self.source_root.as_posix(),
            "home_root": self.home_root.as_posix(),
            "state_root": self.state_root.as_posix(),
            "source_revision": self.source_revision,
            "source_resources_considered": self.source_resources_considered,
            "copied": operation_paths(self.operations, "copy"),
            "skipped": operation_paths(self.operations, "skip"),
            "blocked": operation_paths(self.operations, "blocked"),
            "blocked_codes": blocked_codes,
            "conflicts": conflict_paths(self.operations),
            "missing_dirs": list(self.missing_dirs),
            "unsupported_families_by_target": {
                target: list(families)
                for target, families in self.unsupported_families_by_target.items()
            },
            "validation": validation,
            "residual_drift": list(self.residual_drift),
            "next_step": next_step_for_plan(
                mode=self.mode,
                blocked_codes=blocked_codes,
                missing_dirs=self.missing_dirs,
                residual_drift=self.residual_drift,
            ),
            "next_action": next_action_for_plan(
                mode=self.mode,
                blocked_codes=blocked_codes,
                missing_dirs=self.missing_dirs,
                residual_drift=self.residual_drift,
            ),
            "operations": [operation.to_dict() for operation in self.operations],
        }


CROSS_ALIASES = {"cross", "all", "tutto"}

def parse_targets(raw_targets: str) -> tuple[str, ...]:
    normalized = [part.strip().lower() for part in raw_targets.split(",") if part.strip()]
    if not normalized:
        raise ValueError("unknown-target: no targets selected")
    if len(normalized) == 1 and normalized[0] in CROSS_ALIASES:
        return TARGET_ORDER

    requested = set(normalized)
    unknown = requested.difference(TARGET_ORDER)
    if unknown:
        invalid = ", ".join(sorted(unknown))
        raise ValueError(f"unknown-target: {invalid}")

    return tuple(target for target in TARGET_ORDER if target in requested)


def build_home_sync_plan(
    source_root: Path,
    home_root: Path,
    targets: tuple[str, ...],
    mode: str,
    *,
    experimental_targets: bool = False,
    prune_managed: bool = False,
    fast: bool = False,
    changed_only: bool = False,
) -> HomeSyncPlan:
    source_root = source_root.resolve()
    home_root = home_root.resolve()
    state_root = state_root_for_home(home_root)
    if is_relative_to(source_root, state_root):
        raise RuntimeError("reverse-sync-blocked: source_root is under the home sync state, sync must be repo → home only")
    runtime_rows = load_runtime_support_matrix(source_root)
    catalog = load_home_sync_catalog(source_root)
    manifest_payload, manifest_error = load_manifest(state_root / MANIFEST_PATH)
    manifest_index = index_manifest(manifest_payload)

    operations: list[HomeSyncOperation] = []
    desired_resources: list[ManagedResource] = []
    missing_dirs: list[str] = []
    unsupported_families_by_target: dict[str, set[str]] = {target: set() for target in targets}

    add_manifest_state_operation(operations, state_root, mode, manifest_error)
    catalog_resources = filter_catalog_for_fast_mode(catalog, manifest_payload, targets, fast=fast)
    add_target_root_operations(operations, missing_dirs, home_root, targets, mode)

    for resource in catalog_resources:
        source_path = source_root / resource.source_path
        if not source_path.exists():
            add_resource_blockers(operations, home_root, resource, targets, "source-missing")
            continue
        if not is_valid_resource(source_path, resource.source_family):
            add_resource_blockers(operations, home_root, resource, targets, resource_block_code(resource.source_family))
            continue

        source_hash = hash_resource(source_path)
        for target in intersection_targets(resource, targets):
            target_path = resource_target_path(home_root, resource, target)
            support_row = resolve_support_row(runtime_rows, target, resource.source_family)
            if support_row is None:
                unsupported_families_by_target[target].add(resource.source_family)
                add_blocked_operation(
                    operations,
                    target,
                    target_path,
                    "unsupported-family",
                    "The selected runtime target does not support this resource family.",
                    resource,
                )
                continue

            if not add_support_operation(
                operations,
                support_row,
                target,
                target_path,
                resource,
                mode,
                experimental_targets,
            ):
                continue

            content_hash = source_hash
            if resource.source_family == "agents" and target != "copilot":
                content_hash = _compute_agent_translation_hash(
                    source_root=source_root,
                    source_path=resource.source_path,
                    target=target,
                )
            managed_resource = ManagedResource(
                target=target,
                resource_id=resource.resource_id,
                resource_family=resource.source_family,
                source_path=resource.source_path,
                target_path=target_path.as_posix(),
                source_hash=source_hash,
                content_hash=content_hash,
                last_action="copy",
            )
            desired_resources.append(managed_resource)
            add_materialization_operation(
                operations,
                target,
                target_path,
                resource,
                source_hash,
                manifest_index,
                changed_only,
            )

    add_stale_managed_operations(operations, manifest_payload, desired_resources, targets, mode, prune_managed, home_root)
    return HomeSyncPlan(
        source_root=source_root,
        home_root=home_root,
        state_root=state_root,
        mode=mode,
        selected_targets=targets,
        source_revision=git_revision(source_root),
        source_resources_considered=len(catalog_resources),
        operations=tuple(operations),
        desired_resources=tuple(desired_resources),
        missing_dirs=tuple(sorted(set(missing_dirs))),
        unsupported_families_by_target={
            target: tuple(sorted(families))
            for target, families in unsupported_families_by_target.items()
            if families
        },
        residual_drift=tuple(
            sorted(
                operation.path
                for operation in operations
                if operation.action in {"blocked", "stale-managed", "warning"}
            )
        ),
    )


def apply_home_sync_plan(
    plan: HomeSyncPlan,
    *,
    create_missing_dirs: bool = False,
    prune_managed: bool = False,
) -> Path:
    blocking_codes = plan.blocked_codes()
    if blocking_codes:
        raise RuntimeError("apply blocked by codes: " + ", ".join(blocking_codes))

    mkdir_operations = [operation for operation in plan.operations if operation.action == "mkdir"]
    if mkdir_operations and not create_missing_dirs:
        raise RuntimeError("needs-directory-create: target runtime directories are missing")

    ensure_state_root(plan.state_root)
    write_lock_file(plan.state_root)
    for operation in mkdir_operations:
        Path(operation.path).mkdir(parents=True, exist_ok=True)

    desired_by_path = {resource.target_path: resource for resource in plan.desired_resources}
    copied_paths: set[str] = set()
    actual_content_hashes: dict[str, str] = {}
    for operation in plan.operations:
        if operation.action not in {"copy", "delete"}:
            continue
        target_path = Path(operation.path)
        if operation.action == "delete":
            if prune_managed:
                remove_resource(target_path)
            continue

        if target_path.as_posix() in copied_paths:
            continue

        managed_resource = desired_by_path[operation.path]
        source_path = plan.source_root / managed_resource.source_path
        if managed_resource.resource_family == "agents" and managed_resource.target != "copilot":
            _apply_translated_agent(source_path, target_path, managed_resource.target)
        else:
            copy_resource(source_path, target_path)
        actual_content_hashes[target_path.as_posix()] = hash_resource(target_path)
        copied_paths.add(target_path.as_posix())

    for resource in plan.desired_resources:
        target_path = Path(resource.target_path)
        if not target_path.exists():
            raise RuntimeError(f"post-apply-verify-failed: {target_path} missing after copy")
        actual_hash = actual_content_hashes.get(target_path.as_posix())
        if actual_hash is None:
            actual_hash = hash_resource(target_path)
        expected_hash = resource.content_hash
        if actual_hash != expected_hash:
            raise RuntimeError(f"post-apply-verify-failed: {target_path} hash mismatch (expected {expected_hash}, got {actual_hash})")

    manifest_path = plan.state_root / MANIFEST_PATH
    manifest_path.write_text(render_json(build_manifest_payload(plan, actual_content_hashes)), encoding="utf-8")
    return manifest_path


def write_plan_snapshot(plan: HomeSyncPlan) -> Path:
    return write_snapshot(plan, LAST_PLAN_PATH)


def write_audit_snapshot(plan: HomeSyncPlan) -> Path:
    return write_snapshot(plan, LAST_AUDIT_PATH)


def write_doctor_snapshot(
    *,
    source_root: Path,
    home_root: Path,
    targets: tuple[str, ...],
    checks: list[dict[str, object]],
    blocked_codes: list[str],
) -> Path:
    state_root = state_root_for_home(home_root)
    ensure_state_root(state_root)
    write_lock_file(state_root)
    payload = {
        "mode": "doctor",
        "generated_at": now_isoformat(),
        "source_root": source_root.as_posix(),
        "home_root": home_root.as_posix(),
        "selected_targets": list(targets),
        "checks": checks,
        "blocked_codes": blocked_codes,
    }
    audit_path = state_root / LAST_AUDIT_PATH
    audit_path.write_text(render_json(payload), encoding="utf-8")
    return audit_path


def run_doctor(
    source_root: Path,
    home_root: Path,
    targets: tuple[str, ...],
    *,
    experimental_targets: bool = False,
) -> tuple[list[dict[str, object]], list[str]]:
    runtime_rows = load_runtime_support_matrix(source_root)
    catalog = load_home_sync_catalog(source_root)
    checks: list[dict[str, object]] = [
        {
            "name": "state-root",
            "status": "ok",
            "path": state_root_for_home(home_root).as_posix(),
            "reason": "State root is derivable for the selected home directory.",
        }
    ]
    blocked_codes: set[str] = set()

    for target in targets:
        target_root = runtime_skill_root(home_root, target)
        add_doctor_target_check(checks, blocked_codes, target, target_root)
        support_row = resolve_support_row(runtime_rows, target, "skills")
        add_doctor_support_check(checks, blocked_codes, target, target_root, support_row, experimental_targets)
        agent_root = runtime_agent_root(home_root, target)
        add_doctor_target_check(checks, blocked_codes, target, agent_root)
        agent_support_row = resolve_support_row(runtime_rows, target, "agents")
        add_doctor_support_check(checks, blocked_codes, target, agent_root, agent_support_row, experimental_targets)

    for resource in catalog:
        source_path = source_root / resource.source_path
        checks.append(
            {
                "name": f"catalog:{resource.resource_id}",
                "status": "ok" if source_path.exists() else "blocked",
                "path": source_path.as_posix(),
                "reason": "Catalog source path exists." if source_path.exists() else "Catalog source path is missing.",
                "code": None if source_path.exists() else "source-missing",
            }
        )
        if not source_path.exists():
            blocked_codes.add("source-missing")

    return checks, sorted(blocked_codes)


def add_manifest_state_operation(
    operations: list[HomeSyncOperation],
    state_root: Path,
    mode: str,
    manifest_error: str | None,
) -> None:
    manifest_path = state_root / MANIFEST_PATH
    if manifest_error is not None:
        operations.append(
            HomeSyncOperation(
                target="state",
                action="blocked" if mode == "apply" else "warning",
                path=manifest_path.as_posix(),
                reason="Local manifest exists but cannot be parsed safely.",
                code="manifest-corrupt",
            )
        )
        return
    if mode == "audit" and not manifest_path.exists():
        operations.append(
            HomeSyncOperation(
                target="state",
                action="warning",
                path=manifest_path.as_posix(),
                reason="Audit is running without an existing manifest; results are first-run evidence only.",
                code="manifest-missing",
            )
        )


def filter_catalog_for_fast_mode(
    catalog: list[CatalogResource],
    manifest_payload: dict[str, object],
    targets: tuple[str, ...],
    *,
    fast: bool,
) -> list[CatalogResource]:
    if not fast or not manifest_payload.get("managed_resources"):
        return catalog
    resource_ids = {
        item.get("resource_id")
        for item in manifest_payload.get("managed_resources", [])
        if isinstance(item, dict) and item.get("target") in targets
    }
    return [resource for resource in catalog if resource.resource_id in resource_ids]


def add_target_root_operations(
    operations: list[HomeSyncOperation],
    missing_dirs: list[str],
    home_root: Path,
    targets: tuple[str, ...],
    mode: str,
) -> None:
    for target in targets:
        skill_root = runtime_skill_root(home_root, target)
        _add_root_operation(operations, missing_dirs, home_root, target, skill_root, mode)
        agent_root = runtime_agent_root(home_root, target)
        _add_root_operation(operations, missing_dirs, home_root, target, agent_root, mode)


def _add_root_operation(
    operations: list[HomeSyncOperation],
    missing_dirs: list[str],
    home_root: Path,
    target: str,
    target_root: Path,
    mode: str,
) -> None:
    if not target_root.exists():
        missing_dirs.append(target_root.as_posix())
        operations.append(
            HomeSyncOperation(
                target=target,
                action="mkdir",
                path=target_root.as_posix(),
                reason="Target runtime root is missing and may need directory creation.",
                code="needs-directory-create",
            )
        )
        return

    safety_operation = assess_target_root_safety(
        home_root=home_root,
        target=target,
        target_root=target_root,
        mode=mode,
    )
    if safety_operation is not None:
        operations.append(safety_operation)


def add_resource_blockers(
    operations: list[HomeSyncOperation],
    home_root: Path,
    resource: CatalogResource,
    targets: tuple[str, ...],
    code: str,
) -> None:
    reason = {
        "source-missing": "Catalog entry points to a source path that does not exist. Blocked to avoid materializing a stale or incomplete resource and to surface catalog drift.",
        "source-invalid-skill": "Source skill bundle is missing SKILL.md. Blocked because a valid direct-copy skill bundle must contain SKILL.md.",
        "source-invalid-agent": "Source agent file is missing or not a .md file. Blocked because only allowlisted .agent.md files are eligible for translation.",
    }[code]
    for target in intersection_targets(resource, targets):
        add_blocked_operation(
            operations,
            target,
            resource_target_path(home_root, resource, target),
            code,
            reason,
            resource,
        )


def add_blocked_operation(
    operations: list[HomeSyncOperation],
    target: str,
    target_path: Path,
    code: str,
    reason: str,
    resource: CatalogResource,
) -> None:
    operations.append(
        HomeSyncOperation(
            target=target,
            action="blocked",
            path=target_path.as_posix(),
            reason=reason,
            code=code,
            source_path=resource.source_path,
            resource_id=resource.resource_id,
        )
    )


def add_support_operation(
    operations: list[HomeSyncOperation],
    support_row: RuntimeSupportRow,
    target: str,
    target_path: Path,
    resource: CatalogResource,
    mode: str,
    experimental_targets: bool,
) -> bool:
    support_action, support_code = support_action_for_mode(
        support_row=support_row,
        mode=mode,
        experimental_targets=experimental_targets,
    )
    if support_action is None:
        return True

    operations.append(
        HomeSyncOperation(
            target=target,
            action=support_action,
            path=target_path.as_posix(),
            reason=(
                "Runtime support for this target remains undocumented for apply. Blocked because the support matrix lacks explicit evidence that this family is safe to materialize for the selected target."
                if support_action == "blocked"
                else "Runtime support for this target remains undocumented; report only. Plan and audit are allowed, but apply requires verified support evidence."
            ),
            code=support_code,
            source_path=resource.source_path,
            resource_id=resource.resource_id,
        )
    )
    return support_action != "blocked"


def add_materialization_operation(
    operations: list[HomeSyncOperation],
    target: str,
    target_path: Path,
    resource: CatalogResource,
    source_hash: str,
    manifest_index: dict[str, dict[str, object]],
    changed_only: bool,
) -> None:
    manifest_entry = manifest_index.get(target_path.as_posix())
    if target_path.exists():
        current_hash = hash_resource(target_path)
        if manifest_entry is None:
            add_blocked_operation(
                operations,
                target=target,
                target_path=target_path,
                code="target-exists-unmanaged",
                reason="Target already exists but is not manifest-managed. Blocked to protect locally created or installed files from being silently overwritten by repository-managed copies.",
                resource=resource,
            )
            return
        if current_hash != manifest_entry.get("content_hash"):
            add_blocked_operation(
                operations,
                target=target,
                target_path=target_path,
                code="target-modified-managed",
                reason="Managed target diverged from the last recorded manifest hash. Blocked to prevent losing local edits or runtime-generated changes that occurred after the last sync.",
                resource=resource,
            )
            return
        if changed_only and manifest_entry.get("source_hash") == source_hash:
            operations.append(
                HomeSyncOperation(
                    target=target,
                    action="skip",
                    path=target_path.as_posix(),
                    reason="Changed-only mode skipped an unchanged managed resource.",
                    source_path=resource.source_path,
                    resource_id=resource.resource_id,
                )
            )
            return
        if manifest_entry.get("source_hash") == source_hash:
            operations.append(
                HomeSyncOperation(
                    target=target,
                    action="skip",
                    path=target_path.as_posix(),
                    reason="Managed target already matches the current source bundle.",
                    source_path=resource.source_path,
                    resource_id=resource.resource_id,
                )
            )
            return

    operations.append(
        HomeSyncOperation(
            target=target,
            action="copy",
            path=target_path.as_posix(),
            reason="Copy the allowlisted source bundle into the selected runtime home path. The source hash matches the expected manifest state and the target path is safe to materialize.",
            source_path=resource.source_path,
            resource_id=resource.resource_id,
        )
    )


def add_stale_managed_operations(
    operations: list[HomeSyncOperation],
    manifest_payload: dict[str, object],
    desired_resources: list[ManagedResource],
    targets: tuple[str, ...],
    mode: str,
    prune_managed: bool,
    home_root: Path,
) -> None:
    desired_paths = {resource.target_path for resource in desired_resources}
    managed_resources = manifest_payload.get("managed_resources")
    if not isinstance(managed_resources, list):
        operations.append(
            HomeSyncOperation(
                target="state",
                action="blocked",
                path=(home_root / ".sync").as_posix(),
                reason="Manifest managed_resources is not a list; cannot trust stale items.",
                code="manifest-corrupt",
            )
        )
        return

    for item in managed_resources:
        if not isinstance(item, dict) or item.get("target") not in targets:
            continue
        target_path = item.get("target_path")
        if not isinstance(target_path, str) or target_path in desired_paths:
            continue

        confinement_code = _stale_confinement_check(
            item=item,
            target_path=target_path,
            home_root=home_root,
            mode=mode,
        )
        if confinement_code is not None:
            operations.append(
                HomeSyncOperation(
                    target=str(item.get("target", "")),
                    action="blocked",
                    path=target_path,
                    reason="Stale managed target fails trust-boundary check; delete is not safe. The path may escape the expected home root, cross a symlink, or belong to a different runtime family.",
                    code=confinement_code,
                    resource_id=str(item.get("resource_id", "")),
                )
            )
            continue

        hash_code = _stale_hash_check(
            item=item,
            target_path=target_path,
            mode=mode,
        )
        if hash_code is not None:
            operations.append(
                HomeSyncOperation(
                    target=str(item.get("target", "")),
                    action="blocked",
                    path=target_path,
                    reason="Stale managed target content drift detected; delete is not safe. The file was modified after the last sync, so removing it could discard local changes.",
                    code=hash_code,
                    resource_id=str(item.get("resource_id", "")),
                )
            )
            continue

        action = "delete" if mode == "apply" and prune_managed else "stale-managed"
        operations.append(
            HomeSyncOperation(
                target=str(item.get("target")),
                action=action,
                path=target_path,
                reason=(
                    "Previously managed target is no longer planned. Removed because --prune-managed is enabled and all safety checks passed."
                    if action == "delete"
                    else "Previously managed target is no longer planned. Kept by default because prune requires explicit approval (--prune-managed) to prevent accidental data loss."
                ),
                code=None if action == "delete" else "prune-not-approved",
                resource_id=str(item.get("resource_id")),
            )
        )


def _stale_confinement_check(
    *,
    item: dict[str, object],
    target_path: str,
    home_root: Path,
    mode: str,
) -> str | None:
    required_keys = {"target", "resource_family", "resource_id", "content_hash"}
    if not required_keys.issubset(item.keys()):
        return "manifest-corrupt"

    resolved_home = home_root.resolve()
    stale_path = Path(target_path).expanduser()
    if not stale_path.is_absolute():
        stale_path = home_root / target_path
    resolved_stale = stale_path.resolve()

    if not is_relative_to(resolved_stale, resolved_home):
        if stale_path.is_symlink() or any(p.is_symlink() for p in stale_path.parents):
            return "symlink-not-allowed"
        return "unsafe-home-path"

    target_name = str(item.get("target", ""))
    resource_family = str(item.get("resource_family", ""))
    if resource_family == "agents":
        expected_root = runtime_agent_root(home_root, target_name).resolve()
    elif resource_family == "skills":
        expected_root = runtime_skill_root(home_root, target_name).resolve()
    else:
        return "unsafe-home-path"

    if not is_relative_to(resolved_stale, expected_root):
        return "unsafe-home-path"

    if stale_path.is_symlink() or any(p.is_symlink() for p in stale_path.parents):
        return "symlink-not-allowed"

    return None


def _stale_hash_check(
    *,
    item: dict[str, object],
    target_path: str,
    mode: str,
) -> str | None:
    stale_path = Path(target_path).expanduser()
    if not stale_path.is_absolute():
        return "stale-path-unresolvable"
    if not stale_path.exists():
        return None

    manifest_content_hash = item.get("content_hash")
    if not isinstance(manifest_content_hash, str):
        return None

    current_hash = hash_resource(stale_path)
    if current_hash != manifest_content_hash:
        return "stale-content-drifted"

    return None


def add_doctor_target_check(
    checks: list[dict[str, object]],
    blocked_codes: set[str],
    target: str,
    target_root: Path,
) -> None:
    checks.append(
        {
            "name": f"target-root:{target}",
            "status": "ok" if target_root.exists() else "warning",
            "path": target_root.as_posix(),
            "reason": "Runtime target root exists."
            if target_root.exists()
            else "Runtime target root is missing and may need directory creation.",
            "code": None if target_root.exists() else "needs-directory-create",
        }
    )
    if not target_root.exists():
        blocked_codes.add("needs-directory-create")


def add_doctor_support_check(
    checks: list[dict[str, object]],
    blocked_codes: set[str],
    target: str,
    target_root: Path,
    support_row: RuntimeSupportRow | None,
    experimental_targets: bool,
) -> None:
    if support_row is None:
        checks.append(
            {
                "name": f"support:{target}",
                "status": "blocked",
                "path": target_root.as_posix(),
                "reason": "The selected target does not support skills.",
                "code": "unsupported-family",
            }
        )
        blocked_codes.add("unsupported-family")
        return
    if support_row.support_level != "Documented" and not experimental_targets:
        checks.append(
            {
                "name": f"support:{target}",
                "status": "warning",
                "path": target_root.as_posix(),
                "reason": "Runtime support remains undocumented for apply.",
                "code": "docs-unverified",
            }
        )
        blocked_codes.add("docs-unverified")


def load_manifest(path: Path) -> tuple[dict[str, object], str | None]:
    if not path.exists():
        return {"managed_resources": []}, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"managed_resources": []}, "manifest-corrupt"
    if not isinstance(payload, dict):
        return {"managed_resources": []}, "manifest-corrupt"
    if not isinstance(payload.get("managed_resources"), list):
        return {"managed_resources": []}, "manifest-corrupt"
    for i, item in enumerate(payload.get("managed_resources", [])):
        if not isinstance(item, dict):
            return {"managed_resources": []}, "manifest-corrupt"
        if not isinstance(item.get("target"), str):
            return {"managed_resources": []}, "manifest-corrupt"
        if not isinstance(item.get("target_path"), str):
            return {"managed_resources": []}, "manifest-corrupt"
    return payload, None


def index_manifest(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        item["target_path"]: item
        for item in payload.get("managed_resources", [])
        if isinstance(item, dict) and "target_path" in item
    }


def intersection_targets(resource: CatalogResource, targets: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(target for target in targets if target in resource.include_targets)


def is_valid_skill_bundle(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def is_valid_resource(path: Path, source_family: str) -> bool:
    if source_family == "agents":
        return path.is_file() and path.suffix == ".md"
    return is_valid_skill_bundle(path)


def resource_target_path(
    home_root: Path,
    resource: CatalogResource,
    target: str,
) -> Path:
    if resource.source_family == "agents":
        agent_root = runtime_agent_root(home_root, target)
        ext = target_extension(target)
        return agent_root / f"{resource.resource_id}{ext}"
    return runtime_skill_root(home_root, target) / resource.resource_id


def resource_block_code(source_family: str) -> str:
    if source_family == "agents":
        return "source-invalid-agent"
    return "source-invalid-skill"


def hash_resource(path: Path) -> str:
    if path.is_file():
        return sha256_bytes(path.read_bytes())

    fingerprints = [build_fingerprint(path, file_path) for file_path in collect_files(path)]
    return sha256_bytes(json.dumps(fingerprints, sort_keys=True).encode("utf-8"))


def build_fingerprint(root: Path, file_path: Path) -> dict[str, object]:
    relative_path = file_path.relative_to(root).as_posix()
    raw_bytes = file_path.read_bytes()
    normalized_bytes = normalize_content(relative_path, raw_bytes)
    return {
        "resource_id": relative_path,
        "normalization_version": NORMALIZATION_VERSION,
        "source_hash": sha256_bytes(raw_bytes),
        "content_hash": sha256_bytes(normalized_bytes),
        "metadata": {
            "bytes": len(raw_bytes),
            "normalized_bytes": len(normalized_bytes),
        },
    }


def collect_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not should_ignore_sync_path(path.relative_to(root))
    )


def normalize_content(relative_path: str, raw_bytes: bytes) -> bytes:
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_lines = [line.rstrip() for line in normalized.split("\n")]
    while normalized_lines and normalized_lines[-1] == "":
        normalized_lines.pop()
    normalized = "\n".join(normalized_lines) + "\n"
    if relative_path.endswith(TEXT_EXTENSIONS):
        return normalized.encode("utf-8")
    return raw_bytes


def support_action_for_mode(
    *,
    support_row: RuntimeSupportRow,
    mode: str,
    experimental_targets: bool,
) -> tuple[str | None, str | None]:
    if support_row.support_level == "Documented" and (
        support_row.direct_copy_possible or support_row.translation_required
    ):
        return None, None
    if mode == "apply" and not experimental_targets:
        return "blocked", "docs-unverified"
    return "warning", "docs-unverified"


def _compute_agent_translation_hash(
    *,
    source_root: Path,
    source_path: str,
    target: str,
) -> str:
    source = source_root / source_path
    config_path = source.parent / source.name.replace(".agent.md", ".agent-config.yaml")
    if not config_path.exists():
        config_path = None
    translated = translate_agent_for_target(source, target, config_path)
    return sha256_bytes(translated.encode("utf-8"))


def _apply_translated_agent(
    source_path: Path,
    target_path: Path,
    target: str,
) -> None:
    config_path = source_path.parent / source_path.name.replace(".agent.md", ".agent-config.yaml")
    if not config_path.exists():
        config_path = None
    translated = translate_agent_for_target(source_path, target, config_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(translated, encoding="utf-8")


def write_snapshot(plan: HomeSyncPlan, relative_path: str) -> Path:
    ensure_state_root(plan.state_root)
    write_lock_file(plan.state_root)
    payload = plan.to_dict()
    payload["generated_at"] = now_isoformat()
    snapshot_path = plan.state_root / relative_path
    snapshot_path.write_text(render_json(payload), encoding="utf-8")
    return snapshot_path


def build_manifest_payload(
    plan: HomeSyncPlan,
    actual_content_hashes: dict[str, str] | None = None,
) -> dict[str, object]:
    blocked_paths = {operation.path for operation in plan.operations if operation.action == "blocked"}
    managed_resources = []
    for resource in plan.desired_resources:
        if resource.target_path in blocked_paths:
            continue
        entry = resource.to_dict()
        if actual_content_hashes and resource.target_path in actual_content_hashes:
            entry["content_hash"] = actual_content_hashes[resource.target_path]
        managed_resources.append(entry)
    return {
        "schema_version": 1,
        "generated_at": now_isoformat(),
        "source_root": plan.source_root.as_posix(),
        "source_revision": plan.source_revision,
        "state_root": plan.state_root.as_posix(),
        "targets": list(plan.selected_targets),
        "managed_resources": managed_resources,
    }


def ensure_state_root(state_root: Path) -> None:
    state_root.mkdir(parents=True, exist_ok=True)


def write_lock_file(state_root: Path) -> Path:
    lock_path = state_root / LOCK_PATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(now_isoformat() + "\n", encoding="utf-8")
    return lock_path


def assess_target_root_safety(
    *,
    home_root: Path,
    target: str,
    target_root: Path,
    mode: str,
) -> HomeSyncOperation | None:
    resolved_home = home_root.resolve()
    resolved_target = target_root.resolve()
    if not is_relative_to(resolved_target, resolved_home):
        code = "symlink-not-allowed" if target_root.is_symlink() else "unsafe-home-path"
        return HomeSyncOperation(
            target=target,
            action="blocked" if mode == "apply" else "warning",
            path=target_root.as_posix(),
            reason="Runtime target root resolves outside the selected home directory. Blocked to enforce path confinement and prevent writing to unexpected locations.",
            code=code,
        )

    if not is_read_write_accessible(target_root):
        return HomeSyncOperation(
            target=target,
            action="blocked" if mode == "apply" else "warning",
            path=target_root.as_posix(),
            reason="Runtime target root is not readable and writable enough for this mode. Blocked to prevent I/O failures and partial materialization that could corrupt the home runtime state.",
            code="permission-denied",
        )

    return None


def copy_resource(source_path: Path, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        if target_path.exists():
            remove_resource(target_path)
        shutil.copytree(source_path, target_path, ignore=copytree_ignore_runtime_artifacts)
        return
    shutil.copy2(source_path, target_path)


def remove_resource(target_path: Path) -> None:
    if target_path.is_dir():
        shutil.rmtree(target_path)
        return
    if target_path.exists():
        target_path.unlink()


def copytree_ignore_runtime_artifacts(directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if should_ignore_sync_path(Path(directory, name))
    }


def should_ignore_sync_path(path: Path) -> bool:
    if any(part in IGNORED_SYNC_PARTS for part in path.parts):
        return True
    return path.suffix in IGNORED_SYNC_SUFFIXES


def is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
    except ValueError:
        return False
    return True


def is_read_write_accessible(path: Path) -> bool:
    return path.exists() and path.is_dir() and os.access(path, os.R_OK | os.W_OK | os.X_OK)


def operation_paths(operations: tuple[HomeSyncOperation, ...], action: str) -> list[str]:
    return [operation.path for operation in operations if operation.action == action]


def conflict_paths(operations: tuple[HomeSyncOperation, ...]) -> list[str]:
    return [
        operation.path
        for operation in operations
        if operation.code in {"target-exists-unmanaged", "target-modified-managed"}
    ]


def next_step_for_plan(
    *,
    mode: str,
    blocked_codes: list[str],
    missing_dirs: tuple[str, ...],
    residual_drift: tuple[str, ...],
) -> str:
    if blocked_codes:
        return "Review the blocked codes before attempting apply."
    if missing_dirs and mode != "apply":
        return "Review the planned directory creation before apply."
    if residual_drift:
        return "Review residual drift before treating the selected targets as converged."
    if mode == "plan":
        return "Review the plan and re-run with apply when ready."
    if mode == "audit":
        return "Review the audit snapshot and resolve any residual drift."
    if mode == "apply":
        return "Inspect the manifest and run audit or doctor for follow-up evidence."
    return "Review the generated output and continue with the next safe mode."


def next_action_for_plan(
    *,
    mode: str,
    blocked_codes: list[str],
    missing_dirs: tuple[str, ...],
    residual_drift: tuple[str, ...],
) -> dict[str, object]:
    if blocked_codes:
        return {
            "action": "resolve_blockers",
            "allowed": False,
            "requires_explicit_approval": True,
            "command": "",
            "reason": f"Blocked codes prevent apply. Resolve each blocker manually.",
        }
    if missing_dirs and mode != "apply":
        return {
            "action": "apply",
            "allowed": True,
            "requires_explicit_approval": True,
            "command": "apply --create-missing-dirs --targets <targets>",
            "reason": "Plan is ready. Missing directories need creation. Run apply --create-missing-dirs to proceed.",
        }
    if residual_drift:
        return {
            "action": "resolve_blockers",
            "allowed": False,
            "requires_explicit_approval": True,
            "command": "",
            "reason": "Residual drift detected. Resolve each conflict before apply.",
        }
    if mode == "plan":
        return {
            "action": "apply",
            "allowed": True,
            "requires_explicit_approval": True,
            "command": "apply --targets <targets>",
            "reason": "Plan is ready with zero blockers. Run apply when ready.",
        }
    if mode == "audit":
        return {
            "action": "review",
            "allowed": False,
            "requires_explicit_approval": False,
            "command": "",
            "reason": "Audit complete. Review the audit snapshot.",
        }
    if mode == "apply":
        return {
            "action": "done",
            "allowed": False,
            "requires_explicit_approval": False,
            "command": "",
            "reason": "Apply completed. Manifest updated.",
        }
    return {
        "action": "unknown",
        "allowed": False,
        "requires_explicit_approval": True,
        "command": "",
        "reason": "Review the generated output.",
    }


def git_revision(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def render_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def now_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()
