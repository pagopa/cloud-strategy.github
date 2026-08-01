#!/usr/bin/env python3
"""Validate that protected external skill changes have an exact allowlist."""

from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from pathlib import Path

from lib.cli_runner import run_finding_cli, should_fail
from lib.shared import Finding, find_repo_root, log_success, log_warn
from lib.skill_change_scope import (
    collect_changed_paths,
    detect_protected_skill_changes,
    validate_allowlist,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail when the worktree changes a protected external skill bundle."
    )
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument("--base-ref", help="Also include committed changes from BASE...HEAD.")
    parser.add_argument(
        "--allow-protected-skill",
        dest="allowed_bundles",
        action="append",
        default=[],
        help="Allow one exact protected bundle path. Repeatable.",
    )
    parser.add_argument("--format", choices=["text", "json", "compact"], default="text")
    return parser.parse_args()


def render_text(findings: list[Finding]) -> None:
    if not findings:
        log_success("Protected skill change scope passed with no findings.")
        return
    for finding in findings:
        log_warn(f"{finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


def build_compact_payload(findings: list[Finding]) -> dict[str, object]:
    severity_counts = Counter(finding.severity for finding in findings)
    return {
        "status": "failed" if severity_counts.get("blocking", 0) else "ok",
        "finding_counts": {
            "total": len(findings),
            "blocking": severity_counts.get("blocking", 0),
            "notice": severity_counts.get("notice", 0),
        },
        "finding_sample": [finding.to_dict() for finding in findings[:10]],
        "next_action": (
            "Review protected-skill authorization and exact allowlist entries."
            if findings
            else "Validation passed without protected-skill findings."
        ),
    }


def main() -> int:
    args = parse_args()
    try:
        allowed = validate_allowlist(args.allowed_bundles)
        root = find_repo_root(Path(args.root))
        changed_paths = collect_changed_paths(root, base_ref=args.base_ref)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        raise SystemExit(f"skill change scope validation could not run: {error}") from error

    findings = run_finding_cli(
        detect_fn=lambda: detect_protected_skill_changes(changed_paths, allowed),
        format_name=args.format,
        render_text=render_text,
        compact_builder=build_compact_payload,
    )
    return 1 if should_fail(findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
