from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2

from .inventory import render_inventory_markdown, sections_from_catalog_paths
from .shared import (
    INVENTORY_PATH,
    MANAGED_ROOT_FILES,
    SyncOperation,
    SyncPlan,
    action_sort_key,
    all_files_under,
    git_revision,
    is_git_dirty,
    is_ignored_sync_path,
    is_local_asset,
    read_text,
    sha256_file,
    write_text,
)

MANAGED_SKILL_DIR = ".github/skills"


def build_sync_plan(source_root: Path, target_root: Path) -> SyncPlan:
    source_root = source_root.resolve()
    target_root = target_root.resolve()

    source_files = discover_source_sync_files(source_root)
    target_files = discover_target_managed_files(target_root)
    operations: list[SyncOperation] = []

    for relative_path in sorted(source_files):
        source_path = source_root / relative_path
        target_path = target_root / relative_path
        source_hash = sha256_file(source_path)
        if not target_path.exists():
            operations.append(
                SyncOperation(
                    action="create",
                    path=relative_path,
                    reason="Source-managed file missing from target.",
                    source_hash=source_hash,
                    target_hash=None,
                )
            )
            continue

        target_hash = sha256_file(target_path)
        action = "unchanged" if source_hash == target_hash else "update"
        reason = "Already aligned with source." if action == "unchanged" else "Target file differs from source."
        operations.append(
            SyncOperation(
                action=action,
                path=relative_path,
                reason=reason,
                source_hash=source_hash,
                target_hash=target_hash,
            )
        )

    local_assets: list[str] = []
    for relative_path in sorted(target_files - source_files - {INVENTORY_PATH}):
        if is_local_asset(relative_path):
            local_assets.append(relative_path)
            operations.append(
                SyncOperation(
                    action="preserve",
                    path=relative_path,
                    reason="Preserved target-owned local extension.",
                    source_hash=None,
                    target_hash=sha256_file(target_root / relative_path),
                )
            )
            continue
        operations.append(
            SyncOperation(
                action="delete",
                path=relative_path,
                reason="Target-only non-local asset inside a source-managed category.",
                source_hash=None,
                target_hash=sha256_file(target_root / relative_path),
            )
        )

    future_inventory_paths = sorted(
        catalog_path
        for catalog_path in source_files
        if catalog_path.startswith((".github/agents/", ".github/instructions/", ".github/prompts/", ".github/skills/"))
    )
    future_inventory_paths.extend(
        catalog_path
        for catalog_path in local_assets
        if catalog_path.startswith((".github/agents/", ".github/instructions/", ".github/prompts/", ".github/skills/"))
    )
    generated_inventory = render_inventory_markdown(sections_from_catalog_paths(future_inventory_paths))

    inventory_path = target_root / INVENTORY_PATH
    current_inventory = read_text(inventory_path) if inventory_path.exists() else None
    inventory_action = "unchanged" if current_inventory == generated_inventory else "rebuild"
    inventory_reason = "Inventory already reflects target state." if inventory_action == "unchanged" else "Inventory must be rebuilt from target filesystem state."
    operations.append(
        SyncOperation(
            action=inventory_action,
            path=INVENTORY_PATH,
            reason=inventory_reason,
            source_hash=None,
            target_hash=sha256_file(inventory_path) if inventory_path.exists() else None,
        )
    )

    ordered_operations = tuple(sorted(operations, key=lambda operation: (action_sort_key(operation.action), operation.path)))
    return SyncPlan(
        source_root=source_root,
        target_root=target_root,
        source_revision=git_revision(source_root),
        target_dirty=is_git_dirty(target_root),
        stacks=tuple(detect_target_stacks(target_root)),
        operations=ordered_operations,
        local_assets=tuple(sorted(local_assets)),
        generated_inventory=generated_inventory,
    )


def discover_source_sync_files(root: Path) -> set[str]:
    files = {relative_path for relative_path in MANAGED_ROOT_FILES if (root / relative_path).exists()}
    files.update(all_files_under(root, ".github/agents"))
    files.update(all_files_under(root, ".github/instructions"))
    files.update(all_files_under(root, ".github/prompts"))
    files.update(all_files_under(root, MANAGED_SKILL_DIR))
    return {relative_path for relative_path in files if not is_ignored_sync_path(relative_path)}


def discover_target_managed_files(root: Path) -> set[str]:
    files = {relative_path for relative_path in MANAGED_ROOT_FILES if (root / relative_path).exists()}
    if (root / INVENTORY_PATH).exists():
        files.add(INVENTORY_PATH)
    files.update(all_files_under(root, ".github/agents"))
    files.update(all_files_under(root, ".github/instructions"))
    files.update(all_files_under(root, ".github/prompts"))
    files.update(all_files_under(root, MANAGED_SKILL_DIR))
    return {relative_path for relative_path in files if not is_ignored_sync_path(relative_path)}


def detect_target_stacks(root: Path) -> list[str]:
    stacks: list[str] = []
    if (root / "pyproject.toml").exists() or any(root.rglob("*.py")):
        stacks.append("python")
    if (root / "package.json").exists() or any(root.rglob("*.ts")) or any(root.rglob("*.js")):
        stacks.append("node")
    if (root / "go.mod").exists() or any(root.rglob("*.go")):
        stacks.append("go")
    if any(root.rglob("*.tf")):
        stacks.append("terraform")
    if any(root.rglob("*.java")) or any(root.rglob("*.kt")):
        stacks.append("java")
    return stacks or ["unknown"]


def render_sync_plan_markdown(plan: SyncPlan) -> str:
    lines = [
        "# Copilot Sync Plan",
        "",
        f"- Source root: `{plan.source_root.as_posix()}`",
        f"- Target root: `{plan.target_root.as_posix()}`",
        f"- Source revision: `{plan.source_revision or 'unknown'}`",
        f"- Target dirty: `{'yes' if plan.target_dirty else 'no'}`",
        f"- Detected stacks: `{', '.join(plan.stacks)}`",
        "",
        "## Preserved Local Assets",
        "",
    ]
    if plan.local_assets:
        lines.extend(f"- `{path}`" for path in plan.local_assets)
    else:
        lines.append("No preserved `local-*` assets detected.")
    lines.append("")

    action_groups: dict[str, list[SyncOperation]] = {}
    for operation in plan.operations:
        action_groups.setdefault(operation.action, []).append(operation)

    lines.append("## Planned Operations")
    lines.append("")
    for action in ["create", "update", "rebuild", "delete", "preserve", "unchanged"]:
        group = action_groups.get(action, [])
        if not group:
            continue
        lines.append(f"### {action.title()}")
        lines.append("")
        for operation in group:
            lines.append(f"- `{operation.path}`: {operation.reason}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_sync_plan(plan: SyncPlan) -> Path:
    plan_path = plan.target_root / "tmp/internal-sync-copilot-configs.plan.md"
    write_text(plan_path, render_sync_plan_markdown(plan))
    return plan_path


def write_sync_manifest(plan: SyncPlan) -> Path:
    manifest_path = plan.target_root / ".github/internal-sync-copilot-configs.manifest.json"
    managed_hashes: dict[str, str] = {}
    for operation in plan.operations:
        if operation.action in {"delete", "preserve"}:
            continue
        target_path = plan.target_root / operation.path
        if target_path.exists():
            managed_hashes[operation.path] = sha256_file(target_path)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": plan.source_root.as_posix(),
        "target_root": plan.target_root.as_posix(),
        "source_revision": plan.source_revision,
        "local_assets": list(plan.local_assets),
        "managed_hashes": managed_hashes,
    }
    write_text(manifest_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return manifest_path


def apply_sync_plan(plan: SyncPlan, allow_dirty_target: bool = False) -> Path:
    if plan.target_dirty and not allow_dirty_target and any(
        operation.action in {"create", "update", "rebuild", "delete"} for operation in plan.operations
    ):
        raise RuntimeError("Target repository is dirty. Re-run with --allow-dirty-target if this is intentional.")

    for operation in plan.operations:
        target_path = plan.target_root / operation.path
        if operation.action in {"create", "update"}:
            source_path = plan.source_root / operation.path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            copy2(source_path, target_path)
        elif operation.action == "delete":
            if target_path.exists():
                target_path.unlink()
                cleanup_empty_parents(target_path, plan.target_root)
        elif operation.action == "rebuild" and operation.path == INVENTORY_PATH:
            write_text(target_path, plan.generated_inventory)

    return write_sync_manifest(plan)


def cleanup_empty_parents(path: Path, stop_at: Path) -> None:
    current = path.parent
    while current != stop_at and current.exists():
        if any(current.iterdir()):
            return
        current.rmdir()
        current = current.parent
