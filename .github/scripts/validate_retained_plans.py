"""Read-only retained-plan structure validator.

Usage:
  python validate_retained_plans.py --plan-folder <path> --stage <handoff|completion> [--format json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib.retained_plans import (
    HandoffFinding,
    handoff_validate,
    completion_validate,
    format_handoff_text,
    format_completion_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate retained plan structure and close semantics."
    )
    parser.add_argument(
        "--plan-folder",
        required=True,
        type=Path,
        help="Path to the retained plan folder.",
    )
    parser.add_argument(
        "--stage",
        required=True,
        choices=("handoff", "completion"),
        help="Validation stage: handoff (pre-execution readiness) or completion (final packaging).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_folder = args.plan_folder.resolve()

    if not plan_folder.is_dir():
        print(f"ERROR: Not a directory: {plan_folder}", file=sys.stderr)
        return 1

    if args.stage == "handoff":
        report = handoff_validate(plan_folder)
        if args.format == "json":
            json.dump(report.as_dict(), sys.stdout, indent=2)
        else:
            print(format_handoff_text(report))
        return 0 if report.ready else 1

    report = completion_validate(plan_folder)
    if args.format == "json":
        json.dump(report.as_dict(), sys.stdout, indent=2)
    else:
        print(format_completion_text(report))
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
