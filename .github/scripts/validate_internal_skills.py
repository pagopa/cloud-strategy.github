#!/usr/bin/env python3
"""Purpose: validate the repository-owned internal skill catalog.

Usage examples:
  python3 ./.github/scripts/validate_internal_skills.py
  python3 ./.github/scripts/validate_internal_skills.py --strict --format json
  python3 ./.github/scripts/validate_internal_skills.py --skill internal-python-script --skill internal-terraform
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.internal_skills import detect_internal_skill_findings
from lib.shared import Finding, find_repo_root, log_success, log_warn, render_json


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
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    selected_skills = set(args.skill) or None
    findings = detect_internal_skill_findings(root, selected_skills=selected_skills)

    if args.format == "json":
        print(render_json([finding.to_dict() for finding in findings]))
    else:
        render_text(findings)

    has_blocking = any(finding.severity == "blocking" for finding in findings)
    if has_blocking:
        return 1
    return 1 if args.strict and findings else 0


def render_text(findings: list[Finding]) -> None:
    if not findings:
        log_success("Internal skill catalog validation passed with no findings.")
        return

    for finding in findings:
        log_warn(f"{finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
