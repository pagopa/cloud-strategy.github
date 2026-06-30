#!/usr/bin/env python3
"""Purpose: plan and apply local home-directory AI resource sync operations.

Usage examples:
    python3 scripts/sync_home_ai_resources.py sync --targets skills --format report
    python3 scripts/sync_home_ai_resources.py plan --targets skills --format report
    python3 scripts/sync_home_ai_resources.py apply --targets skills --create-missing-dirs --format report
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bisync_skills import (
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
from sync_output import (
    build_compact_bisync_output,
    build_compact_install_output,
    render_doctor_report,
    render_install_report,
    render_sync_report,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan, audit, doctor, or apply allowlisted home AI resource sync operations."
    )
    subparsers = parser.add_subparsers(dest="command", required=False)
    subparsers.required = True

    for cmd in ("sync", "plan", "apply", "audit", "doctor", "dry-run"):
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
            help="Target runtimes: skills, codex, copilot, opencode, comma-separated combinations, or cross/all/tutto.",
        )
        if cmd != "doctor":
            cmd_parser.add_argument(
                "--retire-targets",
                default="",
                help="Previously synced runtimes to retire from the manifest and prune when combined with --prune-managed. Example: opencode",
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
            default="report",
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
        default="report",
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
        default="report",
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
            **blocked_report_fields(str(error)),
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
            **blocked_report_fields(message),
        }
        emit_output(payload, format_name=args.format, failure_message=message)
        return 1

    command = normalize_mode(args.command)
    if command == "sync":
        return run_sync(source_root, home_root, targets, retire_targets, args)

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
            "validation": "blocked" if blocked_codes else "ready",
            "next_step": next_step_for_doctor(blocked_codes),
            "next_action": next_action_for_doctor(blocked_codes),
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


def run_sync(
    source_root: Path,
    home_root: Path,
    targets: tuple[str, ...],
    retire_targets: tuple[str, ...],
    args: argparse.Namespace,
) -> int:
    install_plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=targets,
        retired_targets=retire_targets,
        mode="apply",
        experimental_targets=args.experimental_targets,
        prune_managed=args.prune_managed,
        fast=args.fast,
        changed_only=args.changed_only,
    )
    install_payload = install_plan.to_dict()
    auto_blockers = install_auto_apply_blockers(install_plan, args)
    if auto_blockers:
        install_payload["state_path"] = write_plan_snapshot(install_plan).as_posix()
        install_payload["auto_sync_blockers"] = auto_blockers
        emit_sync_output(
            {
                "mode": "sync",
                "status": "needs_review",
                "reason": "Install lane needs review before writing home resources.",
                "install": install_payload,
                "bisync": None,
            },
            format_name=args.format,
        )
        return 1

    install_changed = any(
        operation.action in {"copy", "delete", "mkdir"}
        for operation in install_plan.operations
    )
    if install_changed:
        try:
            manifest_path = apply_home_sync_plan(
                install_plan,
                create_missing_dirs=args.create_missing_dirs,
                prune_managed=args.prune_managed,
            )
        except RuntimeError as error:
            install_payload["state_path"] = write_plan_snapshot(install_plan).as_posix()
            install_payload["error"] = str(error)
            emit_sync_output(
                {
                    "mode": "sync",
                    "status": "blocked",
                    "reason": str(error),
                    "install": install_payload,
                    "bisync": None,
                },
                format_name=args.format,
            )
            return 1
        install_payload["manifest_path"] = manifest_path.as_posix()
    install_payload["state_path"] = write_plan_snapshot(install_plan).as_posix()

    bisync_payload: dict[str, object] | None = None
    if targets == ("skills",) and not retire_targets:
        bisync_plan = build_bisync_plan(source_root, home_root, mode="plan")
        bisync_payload = bisync_plan.to_dict()
        if bisync_requires_review(bisync_plan):
            emit_sync_output(
                {
                    "mode": "sync",
                    "status": "needs_review",
                    "reason": "Bisync detected home-owned or ambiguous drift that needs human review before sync can finish.",
                    "install": install_payload,
                    "bisync": bisync_payload,
                },
                format_name=args.format,
            )
            return 1

    emit_sync_output(
        {
            "mode": "sync",
            "status": "done",
            "reason": "Repo-to-home install completed and no home-owned bisync drift needs review.",
            "install": install_payload,
            "bisync": bisync_payload,
        },
        format_name=args.format,
    )
    return 0


def bisync_requires_review(plan) -> bool:
    safe_blocked_codes = {"bisync-only-repo"}
    if any(code not in safe_blocked_codes for code in plan.blocked_codes):
        return True

    for drift in plan.drifts:
        if drift.drift_type == "only-repo":
            continue
        if drift.drift_type == "drift" and drift.direction == "repo-to-home":
            continue
        return True

    return False


def install_auto_apply_blockers(
    plan,
    args: argparse.Namespace,
) -> list[str]:
    blockers = list(plan.blocked_codes())
    if any(
        operation.action in {"blocked", "stale-managed"}
        or (
            operation.action == "warning"
            and operation.code != "target-modified-managed"
        )
        for operation in plan.operations
    ):
        blockers.append("install-residual-drift")
    if any(operation.action == "mkdir" for operation in plan.operations) and not args.create_missing_dirs:
        blockers.append("needs-directory-create")
    if any(operation.action == "stale-managed" for operation in plan.operations):
        blockers.append("stale-managed")
    return sorted(set(blockers))


def emit_sync_output(payload: dict[str, object], *, format_name: str) -> None:
    install_payload = payload.get("install")
    bisync_payload = payload.get("bisync")
    if format_name == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if format_name == "compact":
        compact: dict[str, object] = {
            "mode": payload.get("mode"),
            "status": payload.get("status"),
            "reason": payload.get("reason"),
        }
        if isinstance(install_payload, dict):
            compact["install"] = build_compact_install_output(install_payload)
        if isinstance(bisync_payload, dict):
            compact["bisync"] = build_compact_bisync_output(bisync_payload)
        print(json.dumps(compact, indent=2, sort_keys=True))
        return

    print(render_sync_report(payload), end="")


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
    return 0


def next_step_for_doctor(blocked_codes: list[str]) -> str:
    if blocked_codes:
        return "Resolve the readiness blockers, then rerun doctor before applying home sync changes."
    return "Readiness checks passed. Run plan or sync when ready."


def next_action_for_doctor(blocked_codes: list[str]) -> dict[str, object]:
    if blocked_codes:
        return {
            "action": "resolve_blockers",
            "allowed": False,
            "requires_explicit_approval": True,
            "command": "none",
            "reason": "Doctor found readiness blockers that must be resolved before apply.",
        }
    return {
        "action": "plan",
        "allowed": True,
        "requires_explicit_approval": False,
        "command": "plan --targets <targets> --format report",
        "reason": "Doctor found no readiness blockers.",
    }


def blocked_report_fields(reason: str) -> dict[str, object]:
    return {
        "validation": "blocked",
        "next_step": "Resolve the reported blocker, then rerun the same command.",
        "next_action": {
            "action": "resolve_blockers",
            "allowed": False,
            "requires_explicit_approval": True,
            "command": "none",
            "reason": reason,
        },
    }


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

    if payload.get("mode") == "doctor":
        print(render_doctor_report(payload), end="")
        return
    print(render_install_report(payload), end="")


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir() or (current / ".git").exists():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


if __name__ == "__main__":
    raise SystemExit(main())
