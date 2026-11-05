#!/usr/bin/env python3
"""Purpose: detect token-heavy overlap and duplication in Copilot governance assets.

Usage examples:
    ./.github/tools/run.sh detect-token-risks --root .
    ./.github/tools/run.sh detect-token-risks --root . --strict --format json
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))

from common.command import find_repo_root, run_finding_cli, should_fail
from common.findings import Finding
from common.output import log_warn

from tokens.rules import detect_token_risks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect token efficiency risks in Copilot governance assets."
    )
    parser.add_argument(
        "--root", default=".", help="Repository root or any path inside it."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when any finding is reported.",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    findings = run_finding_cli(
        detect_fn=lambda: detect_token_risks(root),
        format_name=args.format,
        render_text=render_text,
    )
    return 1 if should_fail(findings, strict=args.strict, blocking_severity=None) else 0


def render_text(findings: list[Finding]) -> None:
    if not findings:
        return
    for finding in findings:
        log_warn(f"{finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
