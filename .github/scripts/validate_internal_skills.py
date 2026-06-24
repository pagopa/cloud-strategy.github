#!/usr/bin/env python3
"""Purpose: validate the repository-owned internal skill catalog.

Usage examples:
  python3 ./.github/scripts/validate_internal_skills.py
  python3 ./.github/scripts/validate_internal_skills.py --strict --format json
  python3 ./.github/scripts/validate_internal_skills.py --skill internal-python-script --skill internal-terraform
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from lib.cli_runner import run_finding_cli, should_fail
from lib.internal_skills import detect_internal_skill_findings
from lib.shared import Finding, find_repo_root, log_success, log_warn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate internal-* skill metadata, references, and token hygiene.")
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Validate only the selected internal skill folder name. Repeatable.",
    )
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when any finding is reported.")
    parser.add_argument("--format", choices=["text", "json", "compact"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    selected_skills = set(args.skill) or None
    findings = run_finding_cli(
        detect_fn=lambda: detect_internal_skill_findings(
            root, selected_skills=selected_skills
        ),
        format_name=args.format,
        render_text=render_text,
        compact_builder=build_compact_payload,
    )
    return 1 if should_fail(findings, strict=args.strict) else 0


def render_text(findings: list[Finding]) -> None:
    if not findings:
        log_success("Internal skill catalog validation passed with no findings.")
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
        "finding_sample": [
            {
                "severity": finding.severity,
                "code": finding.code,
                "path": finding.path,
                "message": finding.message,
            }
            for finding in findings[:10]
        ],
        "next_action": (
            "Resolve blocking findings in selected internal skills."
            if severity_counts.get("blocking", 0)
            else "Validation passed without blocking findings."
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
