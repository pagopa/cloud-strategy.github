#!/usr/bin/env python3
"""Purpose: detect token-heavy overlap and duplication in Copilot governance assets.

Usage examples:
  python3 ./.github/scripts/detect_token_risks.py --root .
  python3 ./.github/scripts/detect_token_risks.py --root . --strict --format json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.shared import Finding, find_repo_root, log_warn, render_json
from lib.token_risks import detect_token_risks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect token efficiency risks in Copilot governance assets.")
    parser.add_argument("--root", default=".", help="Repository root or any path inside it.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when any finding is reported.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    findings = detect_token_risks(root)
    if args.format == "json":
        print(render_json([finding.to_dict() for finding in findings]))
    else:
        render_text(findings)
    return 1 if args.strict and findings else 0


def render_text(findings: list[Finding]) -> None:
    if not findings:
        return
    for finding in findings:
        log_warn(f"{finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
