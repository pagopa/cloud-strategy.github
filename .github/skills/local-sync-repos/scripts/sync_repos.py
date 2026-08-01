#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_contract import (  # noqa: E402
    Operation,
    SourceContractError,
    SyncPlan,
    build_plan,
)

_PLAN_RELATIVE = "tmp/local-sync-repos.plan.md"
_FINGERPRINT_RE = re.compile(r"^Plan fingerprint:\s+([0-9a-f]{64})\s*$", re.MULTILINE)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or apply a local-sync-repos baseline sync."
    )
    parser.add_argument("command", choices=["plan", "apply"])
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--format", choices=["compact", "json", "text"], default="compact")
    return parser.parse_args(argv)


def _normalize_posix(path: str) -> str:
    return str(Path(path)).replace("\\", "/")


def _reject_unsafe_path(path: str) -> None:
    if os.path.isabs(path):
        raise ValueError(f"absolute operation path rejected: {path}")
    normalized = _normalize_posix(path)
    parts = Path(normalized).parts
    if ".." in parts:
        raise ValueError(f"parent-traversal operation path rejected: {path}")


def _plan_path_for(target_root: Path) -> Path:
    return target_root / _PLAN_RELATIVE


def _write_plan_file(plan: SyncPlan, plan_file: Path) -> None:
    lines: list[str] = [
        "# local-sync-repos plan",
        "",
        f"Plan fingerprint: {plan.fingerprint}",
        f"Source: {plan.source_root.as_posix()}",
        f"Target: {plan.target_root.as_posix()}",
        "",
        "## Operations",
        "",
    ]
    for op in plan.operations:
        lines.append(f"- {op.action:9s} {op.path} :: {op.reason}")
    if plan.dirty_managed_overlap:
        lines.append("")
        lines.append("## Dirty managed overlap")
        lines.append("")
        for path in plan.dirty_managed_overlap:
            lines.append(f"- {path}")
    lines.append("")
    content = "\n".join(lines)
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(plan_file.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        Path(tmp).replace(plan_file)
    except BaseException:
        if Path(tmp).exists():
            Path(tmp).unlink()
        raise


def _read_saved_fingerprint(plan_file: Path) -> str:
    text = plan_file.read_text(encoding="utf-8")
    match = _FINGERPRINT_RE.search(text)
    if not match:
        raise ValueError(f"saved plan has no parseable fingerprint: {plan_file}")
    return match.group(1)


def _read_operation_source(plan: SyncPlan, operation: Operation) -> bytes:
    source_file = plan.source_root / operation.path
    if source_file.is_file():
        return source_file.read_bytes()

    template_path = SCRIPT_DIR.parent / "templates" / "AGENTS.local.md"
    if operation.path == "AGENTS.local.md" and template_path.is_file():
        return template_path.read_bytes()
    return source_file.read_bytes()


def _apply_operation(plan: SyncPlan, operation: Operation) -> None:
    _reject_unsafe_path(operation.path)
    target_file = plan.target_root / operation.path
    if operation.action == "preserve":
        return
    if operation.action == "delete":
        if not operation.path.startswith(".github/instructions/"):
            raise ValueError(f"delete outside instructions: {operation.path}")
        if target_file.is_file():
            target_file.unlink()
        return
    if operation.action not in {"create", "update"}:
        return
    if operation.source_sha256 is None:
        raise ValueError(f"create/update missing source hash: {operation.path}")

    source_bytes = _read_operation_source(plan, operation)
    target_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target_file.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(source_bytes)
        Path(tmp).replace(target_file)
    except BaseException:
        if Path(tmp).exists():
            Path(tmp).unlink()
        raise


def _build_compact_payload(plan: SyncPlan, mode: str, status: str) -> dict[str, object]:
    operation_counts = Counter(op.action for op in plan.operations)
    return {
        "mode": mode,
        "status": status,
        "target_repo": plan.target_root.as_posix(),
        "fingerprint": plan.fingerprint,
        "operation_counts": {
            "total": len(plan.operations),
            "by_action": dict(sorted(operation_counts.items())),
        },
        "managed_mutation_paths": list(plan.managed_mutation_paths),
        "dirty_managed_overlap": list(plan.dirty_managed_overlap),
    }


def _build_json_payload(plan: SyncPlan, mode: str, status: str) -> dict[str, object]:
    return {
        "mode": mode,
        "status": status,
        "target_repo": plan.target_root.as_posix(),
        "fingerprint": plan.fingerprint,
        "source_root": plan.source_root.as_posix(),
        "operations": [
            {
                "action": op.action,
                "path": op.path,
                "reason": op.reason,
                "source_sha256": op.source_sha256,
                "target_sha256": op.target_sha256,
            }
            for op in plan.operations
        ],
        "managed_mutation_paths": list(plan.managed_mutation_paths),
        "dirty_managed_overlap": list(plan.dirty_managed_overlap),
    }


def _render_text(plan: SyncPlan, mode: str) -> None:
    print(f"local-sync-repos {mode} for {plan.target_root.as_posix()}")
    print(f"Plan fingerprint: {plan.fingerprint}")
    for op in plan.operations:
        print(f"- {op.action:9s} {op.path} :: {op.reason}")


def _emit(plan: SyncPlan, mode: str, status: str, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(_build_json_payload(plan, mode, status), indent=2, sort_keys=True))
    elif fmt == "compact":
        print(json.dumps(_build_compact_payload(plan, mode, status), sort_keys=True))
    else:
        _render_text(plan, mode)


def run_plan(source_root: Path, target_root: Path, fmt: str) -> int:
    plan = build_plan(source_root, target_root)
    plan_file = _plan_path_for(target_root)
    _write_plan_file(plan, plan_file)
    _emit(plan, "plan", "ok", fmt)
    return 0


def run_apply(source_root: Path, target_root: Path, fmt: str) -> int:
    plan_file = _plan_path_for(target_root)
    if not plan_file.is_file():
        print("error: missing-plan — run `plan` before `apply`.", file=sys.stderr)
        return 1
    saved_fingerprint = _read_saved_fingerprint(plan_file)
    plan = build_plan(source_root, target_root)
    if plan.dirty_managed_overlap:
        print(
            f"error: dirty-managed-overlap — {', '.join(plan.dirty_managed_overlap)}",
            file=sys.stderr,
        )
        _emit(plan, "apply", "dirty-managed-overlap", fmt)
        return 1
    if plan.fingerprint != saved_fingerprint:
        print(
            "error: stale-plan — saved plan fingerprint does not match current plan.",
            file=sys.stderr,
        )
        _emit(plan, "apply", "stale-plan", fmt)
        return 1
    for op in plan.operations:
        if op.is_mutation:
            _apply_operation(plan, op)
    updated = build_plan(source_root, target_root)
    if not any(op.is_mutation for op in updated.operations):
        if plan_file.exists():
            plan_file.unlink()
    _emit(updated, "apply", "ok", fmt)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.source_root).resolve()
    target = Path(args.target_repo).resolve()
    try:
        if args.command == "plan":
            return run_plan(source, target, args.format)
        return run_apply(source, target, args.format)
    except SourceContractError as error:
        print(f"error: source-contract — {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
