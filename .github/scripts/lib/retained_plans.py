"""Deterministic retained-plan structure and close-semantics validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

NUMBERED_FILE_PATTERN = re.compile(r"\d{2}-.+\.md")
COMPLETION_REPORT_FIELDS = (
    "Completion Report",
    "Active phase and owner:",
    "State:",
    "Files changed:",
    "Completed items:",
    "Intentional non-actions:",
    "Validators:",
    "Evidence envelope:",
    "Source-item ledger:",
    "Evidence gaps:",
    "Residual risks:",
    "Follow-up suggestions:",
)
OPEN_STATUSES = frozenset({"PENDING", "PARTIAL", "NOT_DONE", "UNVERIFIABLE", "BLOCKED"})
LEDGER_REQUIRED_FIELDS = (
    "Recommended use",
    "File map and role",
    "Clarification gate",
    "Target and anti-scope",
    "Owner and validator",
    "Stop conditions",
)
COMPACT_REQUIRED_FILES = frozenset(
    {"01-change-summary.md", "02-source-item-ledger.md", "03-execution.md", "questions.md"}
)
EXTENDED_REQUIRED_FILES = COMPACT_REQUIRED_FILES | {"04-implementation-contract.md"}


@dataclass
class PlanProfile:
    name: str  # compact, extended, legacy
    required_files: frozenset[str]
    requires_implementation_contract: bool

    @staticmethod
    def classify(plan_folder: Path) -> "PlanProfile":
        ledger_path = plan_folder / "02-source-item-ledger.md"
        if ledger_path.is_file():
            text = ledger_path.read_text(encoding="utf-8")
            # Match "Plan profile: extended" or "Plan profile\nextended"
            if re.search(r"Plan profile[:\s]+extended", text):
                return PlanProfile(
                    name="extended",
                    required_files=EXTENDED_REQUIRED_FILES,
                    requires_implementation_contract=True,
                )
            if re.search(r"Plan profile[:\s]+compact", text):
                return PlanProfile(
                    name="compact",
                    required_files=COMPACT_REQUIRED_FILES,
                    requires_implementation_contract=False,
                )
        return PlanProfile(
            name="legacy",
            required_files=frozenset(),
            requires_implementation_contract=False,
        )


@dataclass
class HandoffFinding:
    code: str
    message: str
    severity: str = "ERROR"  # ERROR, WARNING


@dataclass
class HandoffReport:
    profile: PlanProfile
    plan_folder: str
    required_files_present: list[str] = field(default_factory=list)
    required_files_missing: list[str] = field(default_factory=list)
    ledger_fields_present: list[str] = field(default_factory=list)
    ledger_fields_missing: list[str] = field(default_factory=list)
    clarification_gate_status: str = "not found"
    implementation_contract_present: bool | None = None
    questions_present: bool = False
    active_numbered_files: list[str] = field(default_factory=list)
    findings: list[HandoffFinding] = field(default_factory=list)
    reading_budget: str = ""

    @property
    def ready(self) -> bool:
        return not any(f.severity == "ERROR" for f in self.findings)

    def as_dict(self) -> dict:
        return {
            "profile": self.profile.name,
            "plan_folder": self.plan_folder,
            "required_files_present": self.required_files_present,
            "required_files_missing": self.required_files_missing,
            "ledger_fields_present": self.ledger_fields_present,
            "ledger_fields_missing": self.ledger_fields_missing,
            "clarification_gate_status": self.clarification_gate_status,
            "implementation_contract_present": self.implementation_contract_present,
            "questions_present": self.questions_present,
            "active_numbered_files": self.active_numbered_files,
            "findings": [{"code": f.code, "message": f.message, "severity": f.severity} for f in self.findings],
            "ready": self.ready,
        }


def handoff_validate(plan_folder: Path) -> HandoffReport:
    profile = PlanProfile.classify(plan_folder)
    report = HandoffReport(profile=profile, plan_folder=str(plan_folder))

    # Required files
    for name in sorted(profile.required_files):
        if (plan_folder / name).is_file():
            report.required_files_present.append(name)
        else:
            report.required_files_missing.append(name)

    if report.required_files_missing:
        missing = ", ".join(report.required_files_missing)
        report.findings.append(
            HandoffFinding(code="missing-required-files", message=f"Missing required files: {missing}")
        )

    # Ledger fields
    ledger_path = plan_folder / "02-source-item-ledger.md"
    if ledger_path.is_file():
        ledger_text = ledger_path.read_text(encoding="utf-8")
        for field in LEDGER_REQUIRED_FIELDS:
            if field in ledger_text:
                report.ledger_fields_present.append(field)
            else:
                report.ledger_fields_missing.append(field)

        if report.ledger_fields_missing:
            missing = ", ".join(report.ledger_fields_missing)
            report.findings.append(
                HandoffFinding(code="missing-ledger-fields", message=f"Missing ledger fields: {missing}")
            )

        # Clarification gate
        if "clarification satisfied" in ledger_text:
            report.clarification_gate_status = "satisfied"
        elif "clarification required" in ledger_text:
            report.clarification_gate_status = "required"
        elif "clarification not applicable" in ledger_text:
            report.clarification_gate_status = "not applicable"
        else:
            report.clarification_gate_status = "not found"

        if report.clarification_gate_status == "required":
            report.findings.append(
                HandoffFinding(code="clarification-required", message="Clarification gate is still required")
            )
        elif report.clarification_gate_status == "not found":
            report.findings.append(
                HandoffFinding(
                    code="clarification-missing",
                    message="Clarification gate status not found in ledger",
                    severity="WARNING",
                )
            )
    else:
        report.findings.append(
            HandoffFinding(code="missing-ledger", message="02-source-item-ledger.md is missing")
        )

    # Implementation contract
    ic_path = plan_folder / "04-implementation-contract.md"
    report.implementation_contract_present = ic_path.is_file()
    if profile.requires_implementation_contract and not ic_path.is_file():
        report.findings.append(
            HandoffFinding(
                code="missing-implementation-contract",
                message="Extended profile requires 04-implementation-contract.md",
            )
        )

    # Questions
    questions_path = plan_folder / "questions.md"
    report.questions_present = questions_path.is_file()
    if not questions_path.is_file():
        report.findings.append(
            HandoffFinding(
                code="missing-questions",
                message="questions.md is missing (write '- none' when nothing remains)",
                severity="WARNING",
            )
        )

    # Active numbered files (control files excluded)
    control_files = {"01-change-summary.md", "02-source-item-ledger.md", "04-implementation-contract.md"}
    for md_path in sorted(plan_folder.glob("*.md")):
        if NUMBERED_FILE_PATTERN.match(md_path.name) and md_path.name not in control_files:
            report.active_numbered_files.append(md_path.name)

    return report


@dataclass
class CompletionFinding:
    code: str
    message: str
    severity: str = "ERROR"


@dataclass
class CompletionReport:
    plan_folder: str
    active_numbered_remaining: list[str]
    done_files: list[str]
    evidence_envelope_present: bool
    completion_report_present: bool
    findings: list[CompletionFinding] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not any(f.severity == "ERROR" for f in self.findings)

    def as_dict(self) -> dict:
        return {
            "plan_folder": self.plan_folder,
            "active_numbered_remaining": self.active_numbered_remaining,
            "done_files": self.done_files,
            "evidence_envelope_present": self.evidence_envelope_present,
            "completion_report_present": self.completion_report_present,
            "findings": [{"code": f.code, "message": f.message, "severity": f.severity} for f in self.findings],
            "ready": self.ready,
        }


def completion_validate(plan_folder: Path) -> CompletionReport:
    report = CompletionReport(
        plan_folder=str(plan_folder),
        active_numbered_remaining=[],
        done_files=[],
        evidence_envelope_present=False,
        completion_report_present=False,
    )

    # Active numbered files
    control_files = {"01-change-summary.md", "02-source-item-ledger.md", "04-implementation-contract.md"}
    for md_path in sorted(plan_folder.glob("*.md")):
        if NUMBERED_FILE_PATTERN.match(md_path.name) and md_path.name not in control_files:
            report.active_numbered_remaining.append(md_path.name)

    if report.active_numbered_remaining:
        remaining = ", ".join(report.active_numbered_remaining)
        report.findings.append(
            CompletionFinding(code="active-numbered-files", message=f"Active numbered plan files remain: {remaining}")
        )

    # Done files
    report.done_files = sorted(p.name for p in plan_folder.glob("done-*.md"))

    # Evidence envelope
    envelope_path = plan_folder / "evidence-envelope.md"
    report.evidence_envelope_present = envelope_path.is_file()
    if not envelope_path.is_file():
        report.findings.append(
            CompletionFinding(code="missing-evidence-envelope", message="evidence-envelope.md is missing")
        )
    else:
        envelope_text = envelope_path.read_text(encoding="utf-8")
        if "| Status |" not in envelope_text:
            report.findings.append(
                CompletionFinding(code="missing-status-column", message="Evidence envelope missing Status column")
            )
        if "| Evidence path or command |" not in envelope_text:
            report.findings.append(
                CompletionFinding(
                    code="missing-evidence-column", message="Evidence envelope missing Evidence path or command column"
                )
            )
        for status in OPEN_STATUSES:
            if f"| {status} |" in envelope_text:
                report.findings.append(
                    CompletionFinding(
                        code="open-status", message=f"Evidence envelope contains open status: {status}"
                    )
                )

        for done_file in report.done_files:
            if f"`{done_file}`" not in envelope_text:
                report.findings.append(
                    CompletionFinding(
                        code="missing-done-reference",
                        message=f"Evidence envelope does not reference {done_file}",
                    )
                )

    # Completion report
    report_path = plan_folder / "completion-report.md"
    report.completion_report_present = report_path.is_file()
    if not report_path.is_file():
        report.findings.append(
            CompletionFinding(code="missing-completion-report", message="completion-report.md is missing")
        )
    else:
        report_text = report_path.read_text(encoding="utf-8")
        for field in COMPLETION_REPORT_FIELDS:
            if field not in report_text:
                report.findings.append(
                    CompletionFinding(code="missing-report-field", message=f"Completion report missing: {field}")
                )

    return report


def format_handoff_text(report: HandoffReport) -> str:
    lines = [
        f"Profile: {report.profile.name}",
        f"Plan folder: {report.plan_folder}",
    ]
    if report.required_files_present:
        lines.append(f"Required files present: {', '.join(report.required_files_present)}")
    lines.append(f"Clarification gate: {report.clarification_gate_status}")
    lines.append(f"Questions: {'present' if report.questions_present else 'missing'}")
    lines.append(f"Implementation contract: {'present' if report.implementation_contract_present else 'missing'}")
    if report.active_numbered_files:
        lines.append(f"Active numbered files: {', '.join(report.active_numbered_files)}")

    if report.findings:
        lines.append("Findings:")
        for f in report.findings:
            lines.append(f"  [{f.severity}] {f.code}: {f.message}")
    else:
        lines.append("Result: READY")

    return "\n".join(lines)


def format_completion_text(report: CompletionReport) -> str:
    lines = [f"Plan folder: {report.plan_folder}"]
    if report.done_files:
        lines.append(f"Done files: {', '.join(report.done_files)}")
    lines.append(f"Evidence envelope: {'present' if report.evidence_envelope_present else 'missing'}")
    lines.append(f"Completion report: {'present' if report.completion_report_present else 'missing'}")

    if report.findings:
        lines.append("Findings:")
        for f in report.findings:
            lines.append(f"  [{f.severity}] {f.code}: {f.message}")
    else:
        lines.append("Result: READY")

    return "\n".join(lines)
