"""Bundle-local CLI for retained-plan execution.

Commands: inspect resume checkpoint completion-check

Stdlib-only. Read-only. Does not import sibling bundles or .github/scripts/lib.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

NUMBERED_FILE_PATTERN = re.compile(r"\d{2}-.+\.md")
DONE_FILE_PATTERN = re.compile(r"done-\d{2}.+\.md")

COMPLETION_REPORT_FIELDS = (
    "Completion Report",
    "Active phase and owner:",
    "State:",
    "Continuation:",
    "User action required:",
    "Files changed:",
    "Completed items:",
    "Intentional non-actions:",
    "Validators:",
    "Evidence envelope:",
    "Source-item ledger:",
    "Evidence gaps:",
    "Residual risks:",
    "Next-step package:",
    "Follow-up suggestions:",
)

PLAN_STATE_REQUIRED_FIELDS = (
    "State:",
    "Continuation:",
)

PLAN_STATE_FILE_RE = re.compile(r"^([A-Z0-9_-]+)-plan-state\.md$")

OPEN_STATUSES = frozenset({"PENDING", "PARTIAL", "NOT_DONE", "UNVERIFIABLE", "BLOCKED"})

LEDGER_REQUIRED_FIELDS = (
    "Recommended use",
    "File map and role",
    "Clarification gate",
    "Target and anti-scope",
    "Owner and validator",
    "Stop conditions",
)


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "ERROR"


def classify_profile(plan_folder: Path) -> str:
    """Classify plan profile. Returns profile name or 'unsupported'."""
    compact_path = plan_folder / "02-execution.md"
    if compact_path.is_file():
        text = compact_path.read_text(encoding="utf-8")
        if re.search(r"Plan profile[:\s]+compact", text):
            return "compact"

    control_path = plan_folder / "02-control.md"
    if control_path.is_file():
        text = control_path.read_text(encoding="utf-8")
        if re.search(r"Plan profile[:\s]+extended", text):
            return "extended"

    # Packaged folders may no longer include numbered source files.
    report_path = plan_folder / "completion-report.md"
    if report_path.is_file():
        report_text = report_path.read_text(encoding="utf-8")
        if re.search(r"Plan profile[:\s]+extended", report_text):
            return "extended"
        if re.search(r"Plan profile[:\s]+compact", report_text):
            return "compact"

    return "unsupported"


def numbered_files(plan_folder: Path) -> list[str]:
    """Return sorted numbered plan files."""
    return sorted(
        p.name
        for p in plan_folder.glob("*.md")
        if NUMBERED_FILE_PATTERN.match(p.name)
    )


def done_files(plan_folder: Path) -> list[str]:
    """Return sorted done-* files."""
    return sorted(
        p.name for p in plan_folder.glob("done-*.md")
    )


def resolve_plan_state_marker(plan_folder: Path) -> tuple[Path | None, str | None, list[Finding]]:
    """Resolve lightweight plan-state marker path and state-from-filename if present."""
    findings: list[Finding] = []
    named_paths = sorted(path for path in plan_folder.glob("*-plan-state.md") if path.is_file())

    if len(named_paths) > 1:
        findings.append(
            Finding(
                code="multiple-plan-state-markers",
                message="Multiple <STATE>-plan-state.md markers found; keep exactly one",
            )
        )
        return None, None, findings

    if named_paths:
        marker_path = named_paths[0]
        match = PLAN_STATE_FILE_RE.match(marker_path.name)
        if match is None:
            findings.append(
                Finding(
                    code="invalid-plan-state-marker",
                    message="Plan state marker must match <STATE>-plan-state.md using uppercase state",
                )
            )
            return None, None, findings
        marker_state = match.group(1).upper()
        return marker_path, marker_state, findings

    return None, None, findings


def _check_unsupported(plan_folder: Path) -> tuple[str | None, list[Finding]]:
    profile = classify_profile(plan_folder)
    if profile == "unsupported":
        return None, [
            Finding(
                code="unsupported-plan-contract",
                message=f"Plan folder {plan_folder} has no supported Plan profile (compact or extended)",
            )
        ]
    return profile, []


def _emit_findings(findings: list[Finding], format: str, report: dict | None = None) -> None:
    if format == "json":
        payload: dict = {
            "findings": [{"code": f.code, "message": f.message, "severity": f.severity} for f in findings],
            "ready": not any(f.severity == "ERROR" for f in findings),
        }
        if report:
            payload = {**report, **payload}
        json.dump(payload, sys.stdout, indent=2)
    else:
        if report:
            for key, value in report.items():
                if isinstance(value, list):
                    print(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"{key}: {value}")
        if findings:
            for f in findings:
                print(f"[{f.severity}] {f.code}: {f.message}")
        if not findings and not report:
            print("No findings.")



def cmd_inspect(plan_folder: Path, format: str = "text") -> int:
    """Inspect a plan folder and report status."""
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1

    active = numbered_files(plan_folder)
    dones = done_files(plan_folder)
    envelope = (plan_folder / "evidence-envelope.md").is_file()
    report_exists = (plan_folder / "completion-report.md").is_file()
    questions = (plan_folder / "questions.md").is_file()
    summary = (plan_folder / "01-change-summary.md").is_file()

    report = {
        "plan_folder": str(plan_folder),
        "profile": profile,
        "summary_present": summary,
        "questions_present": questions,
        "active_numbered_files": active,
        "done_files": dones,
        "evidence_envelope_present": envelope,
        "completion_report_present": report_exists,
    }

    _emit_findings(findings, format, report)
    return 0


def cmd_resume(plan_folder: Path, format: str = "text") -> int:
    """Check resume safety for an interrupted plan."""
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1

    active = numbered_files(plan_folder)
    dones = done_files(plan_folder)

    if not active and dones:
        findings.append(
            Finding(
                code="resume-no-active-files",
                message="No active numbered files remain but done files exist; may be ready for completion",
                severity="WARNING",
            )
        )

    # Check for completion report state
    cr_path = plan_folder / "completion-report.md"
    if cr_path.is_file():
        cr_text = cr_path.read_text(encoding="utf-8")
        for state in ("APPLIED_UNVERIFIED", "PARTIAL", "BLOCKED", "ROLLED_BACK"):
            if f"State: {state}" in cr_text:
                findings.append(
                    Finding(
                        code="resume-live-folder",
                        message=f"Completion report state is {state}; folder is live, resume is valid",
                        severity="WARNING",
                    )
                )
                break

    report = {
        "plan_folder": str(plan_folder),
        "profile": profile,
        "active_numbered_files": active,
        "done_files": dones,
        "resumable": True,
    }

    _emit_findings(findings, format, report)
    return 0


def cmd_checkpoint(plan_folder: Path, format: str = "text") -> int:
    """Check that a plan is safe to checkpoint (pause)."""
    profile, findings = _check_unsupported(plan_folder)
    if profile is None:
        _emit_findings(findings, format)
        return 1

    active = numbered_files(plan_folder)
    dones = done_files(plan_folder)

    report = {
        "plan_folder": str(plan_folder),
        "profile": profile,
        "active_numbered_files": active,
        "done_files": dones,
        "can_checkpoint": True,
    }

    _emit_findings(findings, format, report)
    return 0


def cmd_completion_check(plan_folder: Path, format: str = "text") -> int:
    """Validate completion packaging for DONE readiness."""
    active = numbered_files(plan_folder)
    dones = done_files(plan_folder)
    findings: list[Finding] = []

    # Profile gate is always required during completion checks, including
    # packaged folders where numbered plan files were already removed.
    _profile, profile_findings = _check_unsupported(plan_folder)
    if _profile is None:
        _emit_findings(profile_findings, format)
        return 1

    plan_state_path, state_from_filename, marker_findings = resolve_plan_state_marker(plan_folder)
    findings.extend(marker_findings)
    envelope_path = plan_folder / "evidence-envelope.md"
    report_path = plan_folder / "completion-report.md"

    if marker_findings:
        _emit_findings(findings, format)
        return 1

    # Lightweight closeout path: explicit state marker without done-* packaging.
    if plan_state_path and not dones and not envelope_path.is_file() and not report_path.is_file():
        plan_state_text = plan_state_path.read_text(encoding="utf-8")
        for field in PLAN_STATE_REQUIRED_FIELDS:
            if field not in plan_state_text:
                findings.append(
                    Finding(
                        code="missing-plan-state-field",
                        message=f"{plan_state_path.name} is missing {field}",
                    )
                )

        state_match = re.search(r"^State:\s*(.+)$", plan_state_text, re.MULTILINE)
        continuation_match = re.search(
            r"^Continuation:\s*(.+)$", plan_state_text, re.MULTILINE
        )

        if state_from_filename and state_from_filename != "DONE":
            findings.append(
                Finding(
                    code="not-done-state",
                    message=f"{plan_state_path.name} does not encode DONE state",
                )
            )

        if state_match and state_match.group(1).strip() != "DONE":
            findings.append(
                Finding(
                    code="not-done-state",
                    message=f"{plan_state_path.name} does not declare State: DONE",
                )
            )

        if state_from_filename and state_match:
            declared_state = state_match.group(1).strip().upper()
            if declared_state != state_from_filename:
                findings.append(
                    Finding(
                        code="plan-state-name-mismatch",
                        message=(
                            f"{plan_state_path.name} encodes state {state_from_filename} "
                            f"but content declares State: {declared_state}"
                        ),
                    )
                )

        if continuation_match and continuation_match.group(1).strip() != "none":
            findings.append(
                Finding(
                    code="nonterminal-continuation",
                    message=f"{plan_state_path.name} must declare Continuation: none for DONE readiness",
                )
            )

        _emit_findings(findings, format)
        return 0 if not any(f.severity == "ERROR" for f in findings) else 1

    # Active numbered files must be gone for DONE
    if active:
        findings.append(
            Finding(
                code="active-numbered-files",
                message=f"Active numbered plan files remain: {', '.join(active)}",
            )
        )

    # Must have done files
    if not dones:
        findings.append(
            Finding(
                code="missing-done-files",
                message="No done-* files found; DONE requires done markers",
                severity="WARNING",
            )
        )

    # Evidence envelope
    if not envelope_path.is_file():
        findings.append(
            Finding(code="missing-evidence-envelope", message="evidence-envelope.md is missing")
        )
    else:
        envelope_text = envelope_path.read_text(encoding="utf-8")
        if "| Status |" not in envelope_text:
            findings.append(
                Finding(code="missing-status-column", message="Evidence envelope missing Status column")
            )
        if "| Evidence path or command |" not in envelope_text:
            findings.append(
                Finding(code="missing-evidence-column", message="Evidence envelope missing Evidence path or command column")
            )
        for status in OPEN_STATUSES:
            if f"| {status} |" in envelope_text:
                findings.append(
                    Finding(code="open-status", message=f"Evidence envelope contains open status: {status}")
                )

        for done_file in dones:
            if f"`{done_file}`" not in envelope_text:
                findings.append(
                    Finding(code="missing-done-reference", message=f"Evidence envelope does not reference {done_file}")
                )

    # Completion report
    if not report_path.is_file():
        findings.append(
            Finding(code="missing-completion-report", message="completion-report.md is missing")
        )
    else:
        report_text = report_path.read_text(encoding="utf-8")
        for field in COMPLETION_REPORT_FIELDS:
            if field not in report_text:
                findings.append(
                    Finding(code="missing-report-field", message=f"Completion report missing: {field}")
                )
        # DONE requires explicit State: DONE
        if "State: DONE" not in report_text:
            findings.append(
                Finding(
                    code="not-done-state",
                    message="Completion report does not declare State: DONE",
                )
            )

    # Item-by-item coverage matrix
    if envelope_path.is_file():
        envelope_text = envelope_path.read_text(encoding="utf-8")
        rows = re.findall(r"^\|.*\|$", envelope_text, re.MULTILINE)
        data_rows = [r for r in rows if re.search(r"\| (DONE|CHANGED|INTENTIONAL_NON_ACTION) \|", r)]
        if not data_rows:
            findings.append(
                Finding(
                    code="weak-envelope-coverage",
                    message="No DONE, CHANGED, or INTENTIONAL_NON_ACTION rows in evidence envelope",
                    severity="WARNING",
                )
            )

    _emit_findings(findings, format)
    return 0 if not any(f.severity == "ERROR" for f in findings) else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable retained-plan execution CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_p = sub.add_parser("inspect", help="Inspect plan folder status")
    inspect_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    inspect_p.add_argument("--format", choices=("text", "json"), default="text")

    resume_p = sub.add_parser("resume", help="Check resume safety")
    resume_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    resume_p.add_argument("--format", choices=("text", "json"), default="text")

    checkpoint_p = sub.add_parser("checkpoint", help="Check checkpoint safety")
    checkpoint_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    checkpoint_p.add_argument("--format", choices=("text", "json"), default="text")

    cc_p = sub.add_parser("completion-check", help="Validate DONE readiness")
    cc_p.add_argument("plan_folder", type=Path, help="Path to plan folder")
    cc_p.add_argument("--format", choices=("text", "json"), default="text")

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
    if args.command == "completion-check":
        return cmd_completion_check(plan_folder, args.format)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
