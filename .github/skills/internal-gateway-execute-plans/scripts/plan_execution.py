#!/usr/bin/env python3
"""Read-only, stdlib-only plan execution validator CLI."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: Literal["blocking", "notice"] = "blocking"


ALLOWED_STATUSES = frozenset({"DONE", "PARTIAL", "BLOCKED", "NEEDS_REVIEW"})

STATUS_FILENAME_RE = re.compile(
    r"^(?P<basename>.+)\.(?P<status>DONE|PARTIAL|BLOCKED|NEEDS_REVIEW)\.md$"
)

REQUIRED_PLAN_HEADINGS = (
    "Goal",
    "Global Constraints",
)

PLAN_HEADING_ALIASES = {
    "Repository Preflight": ("Repository Preflight", "Preflight"),
}

REQUIRED_EXECUTION_FIELDS = (
    "Baseline Validation",
    "Recovery Policy",
    "Escalation Conditions",
    "User-Facing Report",
)

REQUIRED_STATUS_HEADINGS = (
    "Status",
    "Plan",
    "Plan Fingerprint",
    "Reason",
    "Workspace Baseline",
    "Baseline Validation",
    "Files Changed",
    "Completed",
    "Remaining",
    "Validation",
    "Recovery Attempts",
    "Failure Classification",
    "Next",
    "Resume Notes",
)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _extract_headings(text: str) -> list[str]:
    return [
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("#")
    ]


def _parse_status_from_filename(path: Path) -> str | None:
    m = STATUS_FILENAME_RE.match(path.name)
    if m:
        return m.group("status")
    return None


def _parse_status_from_content(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip().strip("`")
        if stripped in ALLOWED_STATUSES:
            return stripped
    return None


def _has_named_field(text: str, name: str) -> bool:
    escaped = re.escape(name)
    patterns = (
        rf"(?im)^#+\s*{escaped}\s*$",
        rf"(?im)^\s*[-*]\s+\*\*{escaped}:\*\*",
        rf"(?im)^\s*[-*]\s+{escaped}:",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _extract_named_field(text: str, name: str) -> str | None:
    escaped = re.escape(name)
    bullet_pattern = re.compile(
        rf"(?im)^\s*[-*]\s+(?:\*\*)?{escaped}:(?:\*\*)?\s*(.+?)\s*$"
    )
    bullet_match = bullet_pattern.search(text)
    if bullet_match:
        return bullet_match.group(1).strip()

    section = _extract_section(text, name)
    if section:
        return section.strip()
    return None


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == f"## {heading}":
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def _validate_execution_field_quality(text: str) -> list[Finding]:
    findings: list[Finding] = []
    values = {
        name: _extract_named_field(text, name)
        for name in REQUIRED_EXECUTION_FIELDS
    }
    if any(value is None for value in values.values()):
        return findings

    baseline = (values["Baseline Validation"] or "").lower()
    recovery = (values["Recovery Policy"] or "").lower()
    escalation = (values["Escalation Conditions"] or "").lower()
    report = (values["User-Facing Report"] or "").lower()

    baseline_is_actionable = bool(
        re.search(r"`[^`\n]+`|\b(?:rtk|python3|pytest|make)\b", baseline)
    )
    recovery_is_bounded = "tbd" not in recovery and any(
        marker in recovery
        for marker in ("in-scope", "in scope", "task-local", "bounded")
    )
    escalation_distinguishes_failures = (
        "task-local" in escalation
        and any(marker in escalation for marker in ("pre-existing", "unrelated"))
    )
    report_is_complete = all(
        marker in report
        for marker in ("outcome", "validation", "recovery", "next action")
    )

    if not all(
        (
            baseline_is_actionable,
            recovery_is_bounded,
            escalation_distinguishes_failures,
            report_is_complete,
        )
    ):
        findings.append(
            Finding(
                "invalid-execution-field",
                "Execution fields must define an actionable baseline, bounded recovery, failure distinction, and standalone report",
            )
        )
    return findings


def _validate_status_evidence(text: str, status: str | None) -> list[Finding]:
    findings: list[Finding] = []
    baseline = _extract_section(text, "Baseline Validation")
    final = _extract_section(text, "Validation")
    recovery = _extract_section(text, "Recovery Attempts")
    classification = _extract_section(text, "Failure Classification")

    baseline_commands = set(re.findall(r"`([^`\n]+)`", baseline))
    final_commands = set(re.findall(r"`([^`\n]+)`", final))
    if baseline and final and (
        not baseline_commands
        or not final_commands
        or not baseline_commands.intersection(final_commands)
    ):
        findings.append(
            Finding(
                "validation-delta-mismatch",
                "Baseline and final validation must include at least one identical command",
            )
        )

    if recovery and recovery.strip().lower() in {"tbd", "todo", "pending"}:
        findings.append(
            Finding(
                "invalid-recovery-evidence",
                "Recovery Attempts must record actions or explicitly state none",
            )
        )

    classification_lower = classification.lower()
    allowed_classifications = (
        "none",
        "task-local regression",
        "pre-existing",
        "unrelated",
        "external",
        "environmental",
        "unknown",
    )
    if classification and not any(
        marker in classification_lower for marker in allowed_classifications
    ):
        findings.append(
            Finding(
                "invalid-failure-classification",
                "Failure Classification must use a contract classification or none",
            )
        )

    if status == "NEEDS_REVIEW" and classification and not any(
        marker in classification_lower
        for marker in (
            "pre-existing",
            "unrelated",
            "external",
            "environmental",
            "human",
        )
    ):
        findings.append(
            Finding(
                "needs-review-classification",
                "NEEDS_REVIEW requires human, pre-existing, unrelated, external, or environmental classification evidence",
            )
        )
    if status == "BLOCKED" and classification and all(
        marker not in classification_lower
        for marker in ("task-local regression", "environmental", "unknown", "fatal")
    ):
        findings.append(
            Finding(
                "blocked-without-fatal-condition",
                "BLOCKED requires evidence of a fatal execution condition",
            )
        )
    return findings


def validate_plan(path: Path, repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        findings.append(Finding("plan-not-found", f"Plan file not found: {path}"))
        return findings

    retained_dir = repo_root / "tmp" / "superpowers" / "plans"
    try:
        path.resolve().relative_to(retained_dir.resolve())
    except ValueError:
        findings.append(
            Finding(
                "plan-outside-retained-directory",
                f"Plan must be under {retained_dir}",
            )
        )

    text = path.read_text()
    headings = _extract_headings(text)
    heading_set = set(headings)

    for required in REQUIRED_PLAN_HEADINGS:
        if required not in heading_set:
            inline_pattern = f"**{required}:**"
            if inline_pattern not in text:
                findings.append(
                    Finding("missing-heading", f"Plan missing required heading: {required}")
                )

    for canonical, aliases in PLAN_HEADING_ALIASES.items():
        if not any(alias in heading_set for alias in aliases):
            findings.append(
                Finding(
                    "missing-heading",
                    f"Plan missing required heading: {canonical}",
                )
            )

    for required in REQUIRED_EXECUTION_FIELDS:
        if not _has_named_field(text, required):
            findings.append(
                Finding(
                    "missing-execution-field",
                    f"Plan missing required execution field: {required}",
                )
            )

    findings.extend(_validate_execution_field_quality(text))

    if "Task" not in " ".join(headings) and "## Task" not in text:
        findings.append(
            Finding("missing-task", "Plan must contain at least one task heading")
        )

    return findings


def validate_status(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        findings.append(
            Finding("status-not-found", f"Status file not found: {path}")
        )
        return findings

    text = path.read_text()
    headings = _extract_headings(text)
    heading_set = set(headings)

    status_from_file = _parse_status_from_filename(path)
    status_from_content = _parse_status_from_content(text)

    if status_from_file is None:
        findings.append(
            Finding(
                "unknown-status",
                f"Status filename must match <basename>.<STATUS>.md with STATUS in {sorted(ALLOWED_STATUSES)}",
            )
        )
    elif status_from_content is not None and status_from_file != status_from_content:
        findings.append(
            Finding(
                "status-mismatch",
                f"Filename status {status_from_file} != content status {status_from_content}",
            )
        )

    for required in REQUIRED_STATUS_HEADINGS:
        if required not in heading_set:
            findings.append(
                Finding(
                    "missing-heading",
                    f"Status missing required heading: {required}",
                )
            )

    findings.extend(_validate_status_evidence(text, status_from_file))

    return findings


def validate_resume(plan_path: Path, status_path: Path, repo_root: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    effective_root = repo_root or _find_repo_root(plan_path)
    findings.extend(validate_plan(plan_path, repo_root=effective_root))
    findings.extend(validate_status(status_path))

    if any(f.severity == "blocking" for f in findings):
        return findings

    plan_fingerprint = compute_sha256(plan_path)
    status_text = status_path.read_text()

    recorded_fingerprint = None
    for line in status_text.splitlines():
        stripped = line.strip().strip("`")
        if stripped.startswith("sha256:"):
            recorded_fingerprint = stripped
            break

    if recorded_fingerprint is None:
        findings.append(
            Finding(
                "missing-fingerprint",
                "Status file must contain a Plan Fingerprint heading with sha256: value",
            )
        )
    elif recorded_fingerprint != plan_fingerprint:
        findings.append(
            Finding(
                "plan-fingerprint-drift",
                f"Plan changed after approval: recorded {recorded_fingerprint} != computed {plan_fingerprint}",
            )
        )

    return findings


def validate_completion(plan_path: Path, status_path: Path, repo_root: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(validate_resume(plan_path, status_path, repo_root=repo_root))

    if any(f.severity == "blocking" for f in findings):
        return findings

    status_from_file = _parse_status_from_filename(status_path)
    if status_from_file != "DONE":
        findings.append(
            Finding(
                "not-done",
                f"Completion requires DONE status, got {status_from_file}",
            )
        )

    status_text = status_path.read_text()
    headings = _extract_headings(status_text)
    if "Remaining" in headings:
        idx = headings.index("Remaining")
        lines = status_text.splitlines()
        remaining_lines = []
        collecting = False
        for line in lines:
            if line.strip() == "## Remaining":
                collecting = True
                continue
            if collecting and line.startswith("## "):
                break
            if collecting and line.strip():
                remaining_lines.append(line.strip())

        has_real_items = any(
            item for item in remaining_lines if item.lower() not in ("none", "- none")
        )
        if has_real_items:
            findings.append(
                Finding(
                    "remaining-items",
                    "DONE status requires no remaining items",
                )
            )

    return findings


def build_compact_payload(findings: list[Finding]) -> dict[str, object]:
    blocking = [f for f in findings if f.severity == "blocking"]
    notice = [f for f in findings if f.severity == "notice"]
    sample = [
        {"code": f.code, "severity": f.severity} for f in findings[:10]
    ]
    return {
        "status": "passed" if not blocking else "failed",
        "finding_counts": {
            "total": len(findings),
            "blocking": len(blocking),
            "notice": len(notice),
        },
        "finding_sample": sample,
        "next_action": (
            "All checks passed."
            if not blocking
            else "Resolve blocking plan execution findings."
        ),
    }


def _format_text(findings: list[Finding]) -> str:
    if not findings:
        return "OK: all checks passed."
    lines = []
    for f in findings:
        lines.append(f"[{f.severity.upper()}] {f.code}: {f.message}")
    return "\n".join(lines)


def _format_json(findings: list[Finding]) -> str:
    blocking = any(f.severity == "blocking" for f in findings)
    return json.dumps(
        {
            "status": "failed" if blocking else "passed",
            "findings": [
                {"code": f.code, "message": f.message, "severity": f.severity}
                for f in findings
            ],
        },
        indent=2,
    )


def _find_repo_root(start: Path) -> Path:
    for parent in start.resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / ".github").exists():
            return parent
    return start.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only plan execution validator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Validate a plan file")
    preflight.add_argument("plan", type=Path)
    preflight.add_argument("--repo-root", type=Path, default=None)
    preflight.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    status_check = subparsers.add_parser("status-check", help="Validate a status file")
    status_check.add_argument("status", type=Path)
    status_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    resume_check = subparsers.add_parser(
        "resume-check", help="Validate resume safety"
    )
    resume_check.add_argument("plan", type=Path)
    resume_check.add_argument("status", type=Path)
    resume_check.add_argument("--repo-root", type=Path, default=None)
    resume_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    completion_check = subparsers.add_parser(
        "completion-check", help="Validate completion readiness"
    )
    completion_check.add_argument("plan", type=Path)
    completion_check.add_argument("status", type=Path)
    completion_check.add_argument("--repo-root", type=Path, default=None)
    completion_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    args = parser.parse_args(argv)

    if args.command == "preflight":
        repo_root = args.repo_root or _find_repo_root(args.plan)
        findings = validate_plan(args.plan, repo_root=repo_root)
    elif args.command == "status-check":
        findings = validate_status(args.status)
    elif args.command == "resume-check":
        findings = validate_resume(args.plan, args.status, repo_root=args.repo_root)
    elif args.command == "completion-check":
        findings = validate_completion(args.plan, args.status, repo_root=args.repo_root)
    else:
        parser.print_help(sys.stderr)
        return 2

    fmt = getattr(args, "format", "text")
    if fmt == "compact":
        output = json.dumps(build_compact_payload(findings))
    elif fmt == "json":
        output = _format_json(findings)
    else:
        output = _format_text(findings)

    sys.stdout.write(output + "\n")

    blocking = any(f.severity == "blocking" for f in findings)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
