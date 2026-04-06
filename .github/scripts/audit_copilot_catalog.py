#!/usr/bin/env python3
"""Purpose: run a deeper audit of the Copilot catalog and governance bridge.

Usage examples:
  python3 ./.github/scripts/audit_copilot_catalog.py --root .
  python3 ./.github/scripts/audit_copilot_catalog.py --root . --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.catalog_checks import run_consistency_checks
from lib.shared import Finding, find_repo_root, log_info, render_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a governance-focused audit of the Copilot catalog.")
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    findings = run_consistency_checks(root, include_token_risks=True)
    if args.format == "json":
        print(render_json([finding.to_dict() for finding in findings]))
    else:
        render_text(findings)
    return 1 if any(finding.severity == "blocking" for finding in findings) else 0


def render_text(findings: list[Finding]) -> None:
    if not findings:
        log_info("No catalog findings detected.")
        return
    current_severity = None
    for finding in findings:
        if finding.severity != current_severity:
            current_severity = finding.severity
            print(f"\n{current_severity.upper()}")
        print(f"- {finding.path} :: {finding.code}")
        print(f"  {finding.message}")
        print(f"  Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
