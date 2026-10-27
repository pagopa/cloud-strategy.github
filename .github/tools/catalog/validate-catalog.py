#!/usr/bin/env python3
"""Purpose: run fast consistency checks for the Copilot catalog.

Usage examples:
    ./.github/tools/run.sh validate-catalog --root .
    ./.github/tools/run.sh validate-catalog --root . --include-token-risks --strict
    ./.github/tools/run.sh validate-catalog --root . --deep

Deep mode preserves the audit command's JSON and exit-code contract. Its text
renderer is per finding, and its compact output uses the validator next action.
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))

from common.command import (
    find_repo_root,
    run_finding_cli,
    should_fail,
)
from common.findings import Finding
from common.output import (
    log_error,
    log_success,
    log_warn,
)
from tokens.rules import detect_token_risks

from catalog.rules import run_consistency_checks


def run_catalog_checks(
    root: Path, *, include_token_risks: bool = False
) -> list[Finding]:
    token_risk_detector = detect_token_risks if include_token_risks else None
    return run_consistency_checks(
        root,
        include_token_risks=include_token_risks,
        token_risk_detector=token_risk_detector,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run structural consistency checks for the Copilot catalog."
    )
    parser.add_argument(
        "--root", default=".", help="Repository root or any path inside it."
    )
    parser.add_argument(
        "--include-token-risks",
        action="store_true",
        help="Include token-risk heuristics in the result.",
    )
    parser.add_argument(
        "--deep",
        dest="include_token_risks",
        action="store_true",
        help="Include the deep token-risk audit in the result.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any finding, not only blocking findings.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "compact"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = find_repo_root(Path(args.root))
    findings = run_finding_cli(
        detect_fn=lambda: run_catalog_checks(
            root, include_token_risks=args.include_token_risks
        ),
        format_name=args.format,
        render_text=render_text,
        compact_builder=build_compact_payload,
    )

    if should_fail(findings, strict=args.strict):
        return 1
    if not findings and args.format == "text":
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
            "Fix blocking findings first."
            if severity_counts.get("blocking", 0)
            else "No blocking findings; review notices if present."
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
