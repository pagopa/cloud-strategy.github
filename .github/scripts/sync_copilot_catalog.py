#!/usr/bin/env python3
"""Purpose: plan and apply source-authoritative Copilot catalog sync operations.

Usage examples:
  python3 ./.github/scripts/sync_copilot_catalog.py plan --target-repo ../consumer-repo
  python3 ./.github/scripts/sync_copilot_catalog.py apply --target-repo ../consumer-repo --allow-dirty-target

Generated files:
  - Plan output: tmp/copilot-sync.plan.md
  - Canonical sync manifest on apply: .github/copilot-sync.manifest.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.catalog_checks import run_consistency_checks
from lib.fingerprinting import HASH_ALGO, NORMALIZATION_VERSION
from lib.shared import Finding, find_repo_root, log_error, log_info, log_success, render_json
from lib.syncing import apply_sync_plan, build_sync_plan, write_sync_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan or apply Copilot catalog sync operations.")
    parser.add_argument("command", choices=["plan", "apply"], help="Run a dry plan or apply the planned changes.")
    parser.add_argument("--source-root", default=".", help="Source standards repository root.")
    parser.add_argument("--target-repo", required=True, help="Target repository root.")
    parser.add_argument("--allow-dirty-target", action="store_true", help="Allow apply against a dirty target worktree.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = find_repo_root(Path(args.source_root))
    target_root = find_repo_root(Path(args.target_repo))
    source_findings = run_consistency_checks(source_root, include_token_risks=True)
    blocking_source_findings = [finding for finding in source_findings if finding.severity == "blocking"]

    plan = build_sync_plan(source_root, target_root)
    plan_path = write_sync_plan(plan)

    if args.command == "apply" and blocking_source_findings:
        render_source_findings(blocking_source_findings)
        log_error("Source repository has blocking governance findings; sync apply aborted.")
        return 1

    if args.command == "apply":
        try:
            manifest_path = apply_sync_plan(plan, allow_dirty_target=args.allow_dirty_target)
        except RuntimeError as error:
            log_error(str(error))
            return 1
        if args.format == "json":
            print(
                render_json(
                    {
                        "mode": "apply",
                        "plan": plan.to_dict(),
                        "plan_path": plan_path.as_posix(),
                        "manifest_path": manifest_path.as_posix(),
                        "normalization_version": NORMALIZATION_VERSION,
                        "hash_algo": HASH_ALGO,
                    }
                )
            )
        else:
            render_text("apply", plan, plan_path, manifest_path)
        log_success("Sync apply completed.")
        return 0

    if args.format == "json":
        print(
            render_json(
                {
                    "mode": "plan",
                    "plan": plan.to_dict(),
                    "plan_path": plan_path.as_posix(),
                    "source_findings": [finding.to_dict() for finding in source_findings],
                    "normalization_version": NORMALIZATION_VERSION,
                    "hash_algo": HASH_ALGO,
                }
            )
        )
    else:
        render_text("plan", plan, plan_path)
        render_source_findings(source_findings)
    return 0 if not blocking_source_findings else 1


def render_text(mode: str, plan, plan_path: Path, manifest_path: Path | None = None) -> None:
    if mode == "apply":
        log_info(f"Sync apply completed for {plan.target_root.as_posix()}.")
    else:
        log_info(f"Sync {mode} ready for {plan.target_root.as_posix()}.")
    if plan_path.exists():
        log_info(f"Plan file: {plan_path.as_posix()}")
    else:
        log_info(f"Plan file cleared: {plan_path.as_posix()}")
    if manifest_path is not None:
        log_info(f"Manifest file: {manifest_path.as_posix()}")
        log_info(f"Fingerprinting: {HASH_ALGO} normalized-content ({NORMALIZATION_VERSION})")
    for operation in plan.operations:
        print(f"- {operation.action:9s} {operation.path} :: {operation.reason}")


def render_source_findings(findings: list[Finding]) -> None:
    if not findings:
        return
    log_info("Source audit findings:")
    for finding in findings:
        print(f"- {finding.severity} :: {finding.path} :: {finding.code} :: {finding.message}")


if __name__ == "__main__":
    raise SystemExit(main())
