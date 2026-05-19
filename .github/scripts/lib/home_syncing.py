from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .fingerprinting import build_fingerprint, collect_files
from .home_sync_contract import (
    CatalogResource,
    RuntimeSupportRow,
    TARGET_ORDER,
    load_home_sync_catalog,
    load_runtime_support_matrix,
    resolve_support_row,
    runtime_skill_root,
    state_root_for_home,
)
from .shared import git_revision, render_json

MANIFEST_PATH = "manifest.json"
LAST_PLAN_PATH = "last-plan.json"
LAST_AUDIT_PATH = "last-audit.json"
LOCK_PATH = "locks/home-ai-resources.lock"


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
        codes = sorted(
            {
                operation.code
                for operation in self.operations
                if operation.action == "blocked" and operation.code
            }
        )
        return codes

    def to_dict(self) -> dict[str, object]:
        copied = [operation.path for operation in self.operations if operation.action == "copy"]
        skipped = [operation.path for operation in self.operations if operation.action == "skip"]
        blocked = [operation.path for operation in self.operations if operation.action == "blocked"]
        conflicts = [
            operation.path
            for operation in self.operations
            if operation.code in {"target-exists-unmanaged", "target-modified-managed"}
        ]
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
            "copied": copied,
            "skipped": skipped,
            "blocked": blocked,
            "blocked_codes": blocked_codes,
            "conflicts": conflicts,
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
            "operations": [operation.to_dict() for operation in self.operations],
        }


def parse_targets(raw_targets: str) -> tuple[str, ...]:
    normalized = [part.strip().lower() for part in raw_targets.split(",") if part.strip()]
    if not normalized:
        raise ValueError("unknown-target: no targets selected")
    if normalized == ["all"]:
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
    runtime_rows = load_runtime_support_matrix(source_root)
    catalog = load_home_sync_catalog(source_root)
    manifest_payload, manifest_error = load_manifest(state_root / MANIFEST_PATH)
    manifest_index = index_manifest(manifest_payload)

    operations: list[HomeSyncOperation] = []
    desired_resources: list[ManagedResource] = []
    missing_dirs: list[str] = []
    unsupported_families_by_target: dict[str, set[str]] = {target: set() for target in targets}

    if manifest_error is not None:
        action = "blocked" if mode == "apply" else "warning"
        operations.append(
            HomeSyncOperation(
                target="state",
                action=action,
                path=(state_root / MANIFEST_PATH).as_posix(),
                reason="Local manifest exists but cannot be parsed safely.",
                code="manifest-corrupt",
            )
        )
    elif mode == "audit" and not (state_root / MANIFEST_PATH).exists():
        operations.append(
            HomeSyncOperation(
                target="state",
                action="warning",
                path=(state_root / MANIFEST_PATH).as_posix(),
                reason="Audit is running without an existing manifest; results are first-run evidence only.",
                code="manifest-missing",
            )
        )

    catalog_resources = catalog
    if fast and manifest_payload.get("managed_resources"):
        resource_ids = {
            item.get("resource_id")
            for item in manifest_payload.get("managed_resources", [])
            if item.get("target") in targets
        }
        catalog_resources = [
            resource for resource in catalog if resource.resource_id in resource_ids
        ]

    for target in targets:
        target_root = runtime_skill_root(home_root, target)
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
        else:
            safety_operation = assess_target_root_safety(
                home_root=home_root,
                target=target,
                target_root=target_root,
                mode=mode,
            )
            if safety_operation is not None:
                operations.append(safety_operation)

    for resource in catalog_resources:
        source_path = source_root / resource.source_path
        if not source_path.exists():
            for target in intersection_targets(resource, targets):
                operations.append(
                    HomeSyncOperation(
                        target=target,
                        action="blocked",
                        path=(runtime_skill_root(home_root, target) / resource.resource_id).as_posix(),
                        reason="Catalog entry points to a source path that does not exist.",
                        code="source-missing",
                        source_path=resource.source_path,
                        resource_id=resource.resource_id,
                    )
                )
            continue

        if not is_valid_skill_bundle(source_path):
            for target in intersection_targets(resource, targets):
                operations.append(
                    HomeSyncOperation(
                        target=target,
                        action="blocked",
                        path=(runtime_skill_root(home_root, target) / resource.resource_id).as_posix(),
                        reason="Source skill bundle is missing SKILL.md.",
                        code="source-invalid-skill",
                        source_path=resource.source_path,
                        resource_id=resource.resource_id,
                    )
                )
            continue

        source_hash = hash_resource(source_path)
        for target in intersection_targets(resource, targets):
            target_root = runtime_skill_root(home_root, target)
            target_path = target_root / resource.resource_id
            support_row = resolve_support_row(runtime_rows, target, resource.source_family)
            if support_row is None:
                unsupported_families_by_target[target].add(resource.source_family)
                operations.append(
                    HomeSyncOperation(
                        target=target,
                        action="blocked",
                        path=target_path.as_posix(),
                        reason="The selected runtime target does not support this resource family.",
                        code="unsupported-family",
                        source_path=resource.source_path,
                        resource_id=resource.resource_id,
                    )
                )
                continue

            support_action, support_code = support_action_for_mode(
                support_row=support_row,
                mode=mode,
                experimental_targets=experimental_targets,
            )
            if support_action is not None:
                if support_action == "blocked":
                    operations.append(
                        HomeSyncOperation(
                            target=target,
                            action="blocked",
                            path=target_path.as_posix(),
                            reason="Runtime support for this target remains undocumented for apply.",
                            code=support_code,
                            source_path=resource.source_path,
                            resource_id=resource.resource_id,
                        )
                    )
                    continue
                operations.append(
                    HomeSyncOperation(
                        target=target,
                        action=support_action,
                        path=target_path.as_posix(),
                        reason="Runtime support for this target remains undocumented; report only.",
                        code=support_code,
                        source_path=resource.source_path,
                        resource_id=resource.resource_id,
                    )
                )

            managed_resource = ManagedResource(
                target=target,
                resource_id=resource.resource_id,
                resource_family=resource.source_family,
                source_path=resource.source_path,
                target_path=target_path.as_posix(),
                source_hash=source_hash,
                content_hash=source_hash,
                last_action="copy",
            )
            desired_resources.append(managed_resource)

            manifest_entry = manifest_index.get(target_path.as_posix())
            if target_path.exists():
                current_hash = hash_resource(target_path)
                if manifest_entry is None:
                    operations.append(
                        HomeSyncOperation(
                            target=target,
                            action="blocked",
                            path=target_path.as_posix(),
                            reason="Target already exists but is not manifest-managed.",
                            code="target-exists-unmanaged",
                            source_path=resource.source_path,
                            resource_id=resource.resource_id,
                        )
                    )
                    continue
                if current_hash != manifest_entry.get("content_hash"):
                    operations.append(
                        HomeSyncOperation(
                            target=target,
                            action="blocked",
                            path=target_path.as_posix(),
                            reason="Managed target diverged from the last recorded manifest hash.",
                            code="target-modified-managed",
                            source_path=resource.source_path,
                            resource_id=resource.resource_id,
                        )
                    )
                    continue
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
                    continue
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
                    continue

            operations.append(
                HomeSyncOperation(
                    target=target,
                    action="copy",
                    path=target_path.as_posix(),
                    reason="Copy the allowlisted source bundle into the selected runtime home path.",
                    source_path=resource.source_path,
                    resource_id=resource.resource_id,
                )
            )

    desired_paths = {resource.target_path for resource in desired_resources}
    for item in manifest_payload.get("managed_resources", []):
        target = item.get("target")
        if target not in targets:
            continue
        target_path = item.get("target_path")
        if not isinstance(target_path, str) or target_path in desired_paths:
            continue
        action = "delete" if mode == "apply" and prune_managed else "stale-managed"
        code = None if action == "delete" else "prune-not-approved"
        operations.append(
            HomeSyncOperation(
                target=target,
                action=action,
                path=target_path,
                reason="Previously managed target is no longer planned.",
                code=code,
                resource_id=item.get("resource_id"),
            )
        )

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
        raise RuntimeError(
            "apply blocked by codes: " + ", ".join(blocking_codes)
        )

    mkdir_operations = [operation for operation in plan.operations if operation.action == "mkdir"]
    if mkdir_operations and not create_missing_dirs:
        raise RuntimeError("needs-directory-create: target runtime directories are missing")

    ensure_state_root(plan.state_root)
    write_lock_file(plan.state_root)
    for operation in mkdir_operations:
        Path(operation.path).mkdir(parents=True, exist_ok=True)

    desired_by_path = {resource.target_path: resource for resource in plan.desired_resources}
    for operation in plan.operations:
        if operation.action not in {"copy", "delete"}:
            continue
        target_path = Path(operation.path)
        if operation.action == "delete":
            if not prune_managed:
                continue
            remove_resource(target_path)
            continue

        managed_resource = desired_by_path[operation.path]
        source_path = plan.source_root / managed_resource.source_path
        copy_resource(source_path, target_path)

    manifest_resources = [
        resource.to_dict()
        for resource in plan.desired_resources
        if resource.target_path not in {
            operation.path
            for operation in plan.operations
            if operation.action == "blocked"
        }
    ]
    manifest_payload = {
        "schema_version": 1,
        "generated_at": now_isoformat(),
        "source_root": plan.source_root.as_posix(),
        "source_revision": plan.source_revision,
        "state_root": plan.state_root.as_posix(),
        "targets": list(plan.selected_targets),
        "managed_resources": manifest_resources,
    }
    manifest_path = plan.state_root / MANIFEST_PATH
    manifest_path.write_text(render_json(manifest_payload), encoding="utf-8")
    return manifest_path


def write_plan_snapshot(plan: HomeSyncPlan) -> Path:
    ensure_state_root(plan.state_root)
    write_lock_file(plan.state_root)
    payload = plan.to_dict()
    payload["generated_at"] = now_isoformat()
    plan_path = plan.state_root / LAST_PLAN_PATH
    plan_path.write_text(render_json(payload), encoding="utf-8")
    return plan_path


def write_audit_snapshot(plan: HomeSyncPlan) -> Path:
    ensure_state_root(plan.state_root)
    write_lock_file(plan.state_root)
    payload = plan.to_dict()
    payload["generated_at"] = now_isoformat()
    audit_path = plan.state_root / LAST_AUDIT_PATH
    audit_path.write_text(render_json(payload), encoding="utf-8")
    return audit_path


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
    checks: list[dict[str, object]] = []
    blocked_codes: set[str] = set()
    state_root = state_root_for_home(home_root)

    checks.append(
        {
            "name": "state-root",
            "status": "ok",
            "path": state_root.as_posix(),
            "reason": "State root is derivable for the selected home directory.",
        }
    )

    for target in targets:
        target_root = runtime_skill_root(home_root, target)
        checks.append(
            {
                "name": f"target-root:{target}",
                "status": "ok" if target_root.exists() else "warning",
                "path": target_root.as_posix(),
                "reason": (
                    "Runtime target root exists."
                    if target_root.exists()
                    else "Runtime target root is missing and may need directory creation."
                ),
                "code": None if target_root.exists() else "needs-directory-create",
            }
        )
        if not target_root.exists():
            blocked_codes.add("needs-directory-create")

        support_row = resolve_support_row(runtime_rows, target, "skills")
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
            continue

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

    for resource in catalog:
        source_path = source_root / resource.source_path
        checks.append(
            {
                "name": f"catalog:{resource.resource_id}",
                "status": "ok" if source_path.exists() else "blocked",
                "path": source_path.as_posix(),
                "reason": (
                    "Catalog source path exists."
                    if source_path.exists()
                    else "Catalog source path is missing."
                ),
                "code": None if source_path.exists() else "source-missing",
            }
        )
        if not source_path.exists():
            blocked_codes.add("source-missing")

    return checks, sorted(blocked_codes)


def load_manifest(path: Path) -> tuple[dict[str, object], str | None]:
    if not path.exists():
        return {"managed_resources": []}, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError:
        return {"managed_resources": []}, "manifest-corrupt"


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


def hash_resource(path: Path) -> str:
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()

    files = collect_files(path, [path])
    normalized_items = []
    for file_path in files:
        fingerprint = build_fingerprint(path, file_path)
        normalized_items.append(fingerprint.to_dict())
    return hashlib.sha256(
        json.dumps(normalized_items, sort_keys=True).encode("utf-8")
    ).hexdigest()


def support_action_for_mode(
    *,
    support_row: RuntimeSupportRow,
    mode: str,
    experimental_targets: bool,
) -> tuple[str | None, str | None]:
    if support_row.support_level == "Documented" and support_row.direct_copy_possible:
        return None, None
    if mode == "apply" and not experimental_targets:
        return "blocked", "docs-unverified"
    return "warning", "docs-unverified"


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
        action = "blocked" if mode == "apply" else "warning"
        return HomeSyncOperation(
            target=target,
            action=action,
            path=target_root.as_posix(),
            reason="Runtime target root resolves outside the selected home directory.",
            code=code,
        )

    if not is_read_write_accessible(target_root):
        action = "blocked" if mode == "apply" else "warning"
        return HomeSyncOperation(
            target=target,
            action=action,
            path=target_root.as_posix(),
            reason="Runtime target root is not readable and writable enough for this mode.",
            code="permission-denied",
        )

    return None


def is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
    except ValueError:
        return False
    return True


def is_read_write_accessible(path: Path) -> bool:
    return path.exists() and path.is_dir() and os_access(path)


def os_access(path: Path) -> bool:
    import os

    return os.access(path, os.R_OK | os.W_OK | os.X_OK)


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


def copy_resource(source_path: Path, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        if target_path.exists():
            remove_resource(target_path)
        shutil.copytree(source_path, target_path)
        return
    shutil.copy2(source_path, target_path)


def remove_resource(target_path: Path) -> None:
    if target_path.is_dir():
        shutil.rmtree(target_path)
        return
    if target_path.exists():
        target_path.unlink()


def now_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()
