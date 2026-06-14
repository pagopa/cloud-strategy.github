#!/usr/bin/env python3
"""Purpose: plan and apply local home-directory AI resource sync operations.

Usage examples:
    python3 scripts/sync_home_ai_resources.py plan --targets skills
    python3 scripts/sync_home_ai_resources.py apply --targets skills --create-missing-dirs
    python3 scripts/sync_home_ai_resources.py apply --targets skills,codex --retire-targets claude --prune-managed
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bisync_skills import (
    apply_bisync_plan,
    build_bisync_plan,
    run_bisync_apply,
    run_bisync_plan,
)
from home_syncing import (
    apply_home_sync_plan,
    build_home_sync_plan,
    parse_targets,
    run_doctor,
    write_audit_snapshot,
    write_doctor_snapshot,
    write_plan_snapshot,
)
from sync_output import build_compact_install_output, render_install_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan, audit, doctor, or apply allowlisted home AI resource sync operations."
    )
    subparsers = parser.add_subparsers(dest="command", required=False)
    subparsers.required = True

    for cmd in ("plan", "apply", "audit", "doctor", "dry-run"):
        cmd_parser = subparsers.add_parser(cmd, help=f"Run {cmd} sync operation.")
        cmd_parser.add_argument("--source-root", default=".", help="Source repository root.")
        cmd_parser.add_argument(
            "--home-root",
            default=str(Path.home()),
            help="Home directory root to target. Defaults to the current user home.",
        )
        cmd_parser.add_argument(
            "--targets",
            default="skills",
            help="Target runtimes: skills, codex, copilot, claude, opencode, comma-separated combinations, or cross/all/tutto.",
        )
        if cmd != "doctor":
            cmd_parser.add_argument(
                "--retire-targets",
                default="",
                help="Previously synced runtimes to retire from the manifest and prune when combined with --prune-managed. Example: claude",
            )
        cmd_parser.add_argument(
            "--create-missing-dirs",
            action="store_true",
            help="Allow apply to create missing runtime directories.",
        )
        cmd_parser.add_argument(
            "--prune-managed",
            action="store_true",
            help="Allow apply to delete stale manifest-managed resources.",
        )
        cmd_parser.add_argument(
            "--experimental-targets",
            action="store_true",
            help="Allow apply-like execution against undocumented targets.",
        )
        cmd_parser.add_argument(
            "--format",
            choices=["text", "json", "compact", "report"],
            default="text",
            help="Output format.",
        )
        cmd_parser.add_argument(
            "--fast",
            action="store_true",
            help="Prefer manifest-focused audit or plan evaluation when possible.",
        )
        cmd_parser.add_argument(
            "--changed-only",
            action="store_true",
            help="Skip unchanged manifest-managed resources when possible.",
        )

    bisync_parser = subparsers.add_parser("bisync", help="Bidirectional sync between repo skills and home skills.")
    bisync_sub = bisync_parser.add_subparsers(dest="bisync_command", required=True)
    bisync_plan = bisync_sub.add_parser("plan", help="Detect drift without writing.")
    bisync_plan.add_argument("--source-root", default=".", help="Source repository root.")
    bisync_plan.add_argument(
        "--home-root",
        default=str(Path.home()),
        help="Home directory root.",
    )
    bisync_plan.add_argument(
        "--format",
        choices=["text", "json", "compact", "report"],
        default="text",
        help="Output format.",
    )
    bisync_apply = bisync_sub.add_parser("apply", help="Apply bisync resolution.")
    bisync_apply.add_argument("--source-root", default=".", help="Source repository root.")
    bisync_apply.add_argument(
        "--home-root",
        default=str(Path.home()),
        help="Home directory root.",
    )
    bisync_apply.add_argument(
        "--format",
        choices=["text", "json", "compact", "report"],
        default="text",
        help="Output format.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(argv))


def run(args: argparse.Namespace) -> int:
    if args.command == "bisync":
        if args.bisync_command == "plan":
            return run_bisync_plan(args)
        return run_bisync_apply(args)

    source_root = find_repo_root(Path(args.source_root))
    home_root = Path(args.home_root).expanduser().resolve()
    try:
        targets = parse_targets(args.targets)
        retire_targets = ()
        if getattr(args, "retire_targets", "").strip():
            retire_targets = parse_targets(args.retire_targets)
    except ValueError as error:
        payload = {
            "mode": normalize_mode(args.command),
            "selected_targets": [],
            "retired_targets": [],
            "blocked_codes": ["unknown-target"],
            "error": str(error),
        }
        emit_output(payload, format_name=args.format, failure_message=str(error))
        return 1

    overlap = sorted(set(targets) & set(retire_targets))
    if overlap:
        message = (
            "retire-target-overlap: selected and retired targets must be disjoint: "
            + ", ".join(overlap)
        )
        payload = {
            "mode": normalize_mode(args.command),
            "selected_targets": list(targets),
            "retired_targets": list(retire_targets),
            "blocked_codes": ["retire-target-overlap"],
            "error": message,
        }
        emit_output(payload, format_name=args.format, failure_message=message)
        return 1

    command = normalize_mode(args.command)
    if command == "doctor":
        checks, blocked_codes = run_doctor(
            source_root,
            home_root,
            targets,
            experimental_targets=args.experimental_targets,
        )
        snapshot_path = write_doctor_snapshot(
            source_root=source_root,
            home_root=home_root,
            targets=targets,
            checks=checks,
            blocked_codes=blocked_codes,
        )
        payload = {
            "mode": "doctor",
            "selected_targets": list(targets),
            "checks": checks,
            "blocked_codes": blocked_codes,
            "state_path": snapshot_path.as_posix(),
        }
        emit_output(payload, format_name=args.format)
        return 0

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=targets,
        retired_targets=retire_targets,
        mode=command,
        experimental_targets=args.experimental_targets,
        prune_managed=args.prune_managed,
        fast=args.fast,
        changed_only=args.changed_only,
    )

    if command == "apply":
        return run_apply(plan, args)

    snapshot_path = write_audit_snapshot(plan) if command == "audit" else write_plan_snapshot(plan)
    payload = plan.to_dict()
    payload["state_path"] = snapshot_path.as_posix()
    emit_output(payload, format_name=args.format)
    return 0


def run_apply(plan, args: argparse.Namespace) -> int:
    try:
        manifest_path = apply_home_sync_plan(
            plan,
            create_missing_dirs=args.create_missing_dirs,
            prune_managed=args.prune_managed,
        )
    except RuntimeError as error:
        payload = plan.to_dict()
        payload["state_path"] = write_plan_snapshot(plan).as_posix()
        emit_output(payload, format_name=args.format, failure_message=str(error))
        return 1

    snapshot_path = write_plan_snapshot(plan)
    payload = plan.to_dict()
    payload["manifest_path"] = manifest_path.as_posix()
    payload["state_path"] = snapshot_path.as_posix()
    emit_output(payload, format_name=args.format)
    log_success("Home AI resource apply completed.")
    return 0


def normalize_mode(command: str) -> str:
    return "plan" if command == "dry-run" else command


def emit_output(
    payload: dict[str, object],
    *,
    format_name: str,
    failure_message: str | None = None,
) -> None:
    if format_name == "compact":
        compact_payload = build_compact_install_output(payload)
        if failure_message and "error" not in compact_payload:
            compact_payload["error"] = failure_message
        print(json.dumps(compact_payload, indent=2, sort_keys=True))
        return

    if format_name == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    if format_name == "report":
        print(render_install_report(payload), end="")
        return

    mode = payload.get("mode", "plan")
    targets = ", ".join(payload.get("selected_targets", [])) or "none"
    retired_targets = ", ".join(payload.get("retired_targets", []))
    log_info(f"Mode: {mode}")
    log_info(f"Targets: {targets}")
    if retired_targets:
        log_info(f"Retire targets: {retired_targets}")

    operations = payload.get("operations", [])
    copied_ops = [op for op in operations if isinstance(op, dict) and op.get("action") == "copy"]
    skipped_ops = [op for op in operations if isinstance(op, dict) and op.get("action") == "skip"]
    blocked_ops = [op for op in operations if isinstance(op, dict) and op.get("action") == "blocked"]
    stale_ops = [op for op in operations if isinstance(op, dict) and op.get("action") == "stale-managed"]
    mkdir_ops = [op for op in operations if isinstance(op, dict) and op.get("action") == "mkdir"]
    source_resources = payload.get("source_resources_considered")

    log_info(
        f"Summary: {len(copied_ops)} to copy, {len(skipped_ops)} up-to-date, "
        f"{len(blocked_ops)} blocked"
        + (f", {len(stale_ops)} stale" if stale_ops else "")
        + (f" ({source_resources} resources considered)" if isinstance(source_resources, int) else "")
    )

    if copied_ops:
        copied_resources: dict[str, dict[str, list[str]]] = {}
        for op in copied_ops:
            rid = op.get("resource_id", "unknown")
            target = op.get("target", "?")
            path = op.get("path", "")
            family = "agents" if "/agents/" in path else "skills"
            if rid not in copied_resources:
                copied_resources[rid] = {"skills": [], "agents": []}
            copied_resources[rid][family].append(target)
        for rid, families in sorted(copied_resources.items()):
            parts = []
            for family in ("skills", "agents"):
                if families[family]:
                    parts.append(f"{family}→{','.join(families[family])}")
            log_info(f"  + {rid} ({'; '.join(parts)})")

    blocked_codes = payload.get("blocked_codes", [])
    if blocked_codes:
        log_error(f"Blocked codes: {', '.join(blocked_codes)}")
        blocked_by_code: dict[str, list[dict]] = {}
        for op in blocked_ops:
            code = op.get("code", "unknown")
            blocked_by_code.setdefault(code, []).append(op)
        for code, ops in sorted(blocked_by_code.items()):
            log_error(f"  [{code}] {len(ops)} path(s)")
            for op in ops:
                path = op.get("path", "")
                reason = op.get("reason", "")
                if reason:
                    log_error(f"    - {path}: {reason}")
                else:
                    log_error(f"    - {path}")

    if stale_ops:
        log_info(f"Stale managed resources: {len(stale_ops)}")
        for op in stale_ops:
            path = op.get("path", "")
            reason = op.get("reason", "")
            code = op.get("code", "")
            if code:
                log_info(f"  ~ {path} [{code}]: {reason}")
            else:
                log_info(f"  ~ {path}: {reason}")

    for path in payload.get("missing_dirs", []):
        log_info(f"Missing dir: {path}")

    residual_drift = payload.get("residual_drift", [])
    if residual_drift:
        log_info(f"Residual drift: {len(residual_drift)} path(s)")

    validation = payload.get("validation")
    if isinstance(validation, str):
        log_info(f"Validation: {validation}")

    next_step = payload.get("next_step")
    if isinstance(next_step, str) and next_step:
        log_info(f"Next: {next_step}")

    state_path = payload.get("state_path")
    if isinstance(state_path, str):
        log_info(f"State: {state_path}")

    manifest_path = payload.get("manifest_path")
    if isinstance(manifest_path, str):
        log_info(f"Manifest: {manifest_path}")

    if failure_message:
        log_error(failure_message)


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir() or (current / ".git").exists():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


def log_info(message: str) -> None:
    print(f"ℹ️  {message}", flush=True)


def log_success(message: str) -> None:
    print(f"✅ {message}", flush=True)


def log_error(message: str) -> None:
    print(f"❌ {message}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
