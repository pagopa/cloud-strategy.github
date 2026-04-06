#!/usr/bin/env python3
"""Purpose: run fast consistency checks for the Copilot catalog.

Usage examples:
  python3 ./.github/scripts/check_catalog_consistency.py --root .
  python3 ./.github/scripts/check_catalog_consistency.py --root . --include-token-risks --strict
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.catalog_checks import run_consistency_checks
from lib.shared import Finding, find_repo_root, log_error, log_success, log_warn, render_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run structural consistency checks for the Copilot catalog.")
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument("--include-token-risks", action="store_true", help="Include token-risk heuristics in the result.")
    parser.add_argument("--strict", action="store_true", help="Fail on any finding, not only blocking findings.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    findings = run_consistency_checks(root, include_token_risks=args.include_token_risks)
    if args.format == "json":
        print(render_json([finding.to_dict() for finding in findings]))
    else:
        render_text(findings)

    has_blocking = any(finding.severity == "blocking" for finding in findings)
    if has_blocking or (args.strict and findings):
        return 1
    if not findings:
        log_success("No consistency findings detected.")
    return 0


def render_text(findings: list[Finding]) -> None:
    if not findings:
        return
    for finding in findings:
        prefix = "BLOCKING" if finding.severity == "blocking" else "NOTICE"
        logger = log_error if finding.severity == "blocking" else log_warn
        logger(f"[{prefix}] {finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
