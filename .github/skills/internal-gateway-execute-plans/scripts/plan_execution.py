"""Bundle-local CLI for gateway retained-plan status files.

Commands: inspect resume checkpoint status-check completion-check

Stdlib-only. Read-only. Does not import sibling bundles or .github/scripts/lib.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

VALID_STATUSES = frozenset({"DONE", "BLOCKED", "PARTIAL", "NEEDS_REVIEW"})
REQUIRED_HEADINGS = (
    "## Status",
    "## Reason",
    "## Completed",
    "## Remaining",
    "## Validation",
    "## Next",
    "## Resume Notes",
)


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "ERROR"


def status_pattern(plan_folder: Path) -> re.Pattern[str]:
    escaped_name = re.escape(plan_folder.name)
    statuses = "|".join(sorted(VALID_STATUSES))
    return re.compile(rf"^{escaped_name}\.({statuses})\.md$")


def find_status_files(plan_folder: Path) -> tuple[list[Path], list[Finding]]:
    findings: list[Finding] = []
    pattern = status_pattern(plan_folder)
    status_files: list[Path] = []

    for path in sorted(plan_folder.glob("*.md")):
        if pattern.match(path.name):
            status_files.append(path)
        elif re.match(rf"^{re.escape(plan_folder.name)}\.[A-Z0-9_-]+\.md$", path.name):
            findings.append(
                Finding(
                    code="invalid-status-file-name",
                    message=(
                        f"{path.name} uses an unsupported status; valid statuses are "
                        f"{', '.join(sorted(VALID_STATUSES))}"
                    ),
                )
            )

    legacy_markers = sorted(plan_folder.glob("*-plan-state.md"))
    if legacy_markers:
        findings.append(
            Finding(
                code="legacy-plan-state-marker",
                message="Legacy <STATE>-plan-state.md marker found; gateway output must use <plan-basename>.<STATUS>.md",
            )
        )

    return status_files, findings


def validate_status_file(plan_folder: Path) -> tuple[Path | None, str | None, list[Finding]]:
    status_files, findings = find_status_files(plan_folder)

    if len(status_files) > 1:
        findings.append(
            Finding(
                code="multiple-status-files",
                message="Multiple gateway status files found; keep exactly one current status file",
            )
        )
        return None, None, findings

    if not status_files:
        findings.append(
            Finding(
                code="missing-status-file",
                message="No <plan-basename>.<STATUS>.md status file found",
            )
        )
        return None, None, findings

    status_path = status_files[0]
    match = status_pattern(plan_folder).match(status_path.name)
    if match is None:
        findings.append(
            Finding(
                code="invalid-status-file-name",
                message=f"{status_path.name} does not match <plan-basename>.<STATUS>.md",
            )
        )
        return status_path, None, findings

    status = match.group(1)
    text = status_path.read_text(encoding="utf-8")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            findings.append(
                Finding(
                    code="missing-required-heading",
                    message=f"{status_path.name} is missing {heading}",
                )
            )

    status_match = re.search(r"^## Status\s*\n+\s*([A-Z0-9_-]+)\s*$", text, re.MULTILINE)
    if status_match is None:
        findings.append(
            Finding(
                code="missing-declared-status",
                message=f"{status_path.name} must declare the status under ## Status",
            )
        )
    elif status_match.group(1) != status:
        findings.append(
            Finding(
                code="status-mismatch",
                message=f"{status_path.name} encodes {status} but declares {status_match.group(1)}",
            )
        )

    return status_path, status, findings


def emit(findings: list[Finding], output_format: str, report: dict | None = None) -> None:
    ready = not any(f.severity == "ERROR" for f in findings)
    if output_format == "json":
        payload = {
            "ready": ready,
            "findings": [
                {"code": f.code, "message": f.message, "severity": f.severity}
                for f in findings
            ],
        }
        if report:
            payload = {**report, **payload}
        json.dump(payload, sys.stdout, indent=2)
        print()
        return

    if report:
        for key, value in report.items():
            print(f"{key}: {value}")
    if findings:
        for finding in findings:
            print(f"[{finding.severity}] {finding.code}: {finding.message}")
    elif not report:
        print("No findings.")


def basic_report(plan_folder: Path) -> dict:
    status_files, findings = find_status_files(plan_folder)
    return {
        "plan_folder": str(plan_folder),
        "plan_basename": plan_folder.name,
        "status_file_present": bool(status_files) and not findings,
        "status_files": [path.name for path in status_files],
    }


def cmd_inspect(plan_folder: Path, output_format: str) -> int:
    emit([], output_format, basic_report(plan_folder))
    return 0


def cmd_resume(plan_folder: Path, output_format: str) -> int:
    status_path, status, findings = validate_status_file(plan_folder)
    report = basic_report(plan_folder)
    report.update(
        {
            "status_file": status_path.name if status_path else None,
            "status": status,
            "resumable": status in {"BLOCKED", "PARTIAL", "NEEDS_REVIEW"},
        }
    )
    emit(findings, output_format, report)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def cmd_checkpoint(plan_folder: Path, output_format: str) -> int:
    report = basic_report(plan_folder)
    report["status_file_required"] = True
    emit([], output_format, report)
    return 0


def cmd_status_check(plan_folder: Path, output_format: str) -> int:
    status_path, status, findings = validate_status_file(plan_folder)
    report = {
        "plan_folder": str(plan_folder),
        "plan_basename": plan_folder.name,
        "status_file": status_path.name if status_path else None,
        "status": status,
    }
    emit(findings, output_format, report)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate gateway retained-plan status files.")
    sub = parser.add_subparsers(dest="command", required=True)

    for command in ("inspect", "resume", "checkpoint", "status-check", "completion-check"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("plan_folder", type=Path)
        command_parser.add_argument("--format", choices=("text", "json"), default="text")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_folder = args.plan_folder.resolve()

    if not plan_folder.is_dir():
        print(f"ERROR: Not a directory: {plan_folder}", file=sys.stderr)
        return 1

    if args.command == "inspect":
        return cmd_inspect(plan_folder, args.format)
    if args.command == "resume":
        return cmd_resume(plan_folder, args.format)
    if args.command == "checkpoint":
        return cmd_checkpoint(plan_folder, args.format)
    if args.command in {"status-check", "completion-check"}:
        return cmd_status_check(plan_folder, args.format)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
