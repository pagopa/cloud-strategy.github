"""Tests for lib/retained_plans.py — profile classification, handoff, and completion validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[4] / ".github" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from lib.retained_plans import (  # noqa: E402
    COMPLETION_REPORT_FIELDS,
    COMPACT_REQUIRED_FILES,
    EXTENDED_REQUIRED_FILES,
    PlanProfile,
    handoff_validate,
    completion_validate,
)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_compact_plan(plan_folder: Path) -> None:
    write_file(plan_folder / "01-change-summary.md", "# Summary\n\nChange summary.\n")
    write_file(
        plan_folder / "02-source-item-ledger.md",
        "# Ledger\n\n"
        "## Recommended use\napply-plan\n\n"
        "## Plan profile\ncompact\n\n"
        "## File map and role\n| File | Ruolo |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Initial evidence pass\ntarget, validator\n\n"
        "## Reading budget\nthis folder only\n\n"
        "## Target and anti-scope\nTest target.\n\n"
        "## Owner and validator\ninternal-gateway-operational-flow\n\n"
        "## Stop conditions\nNone.\n\n"
        "## Source item ledger\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| T-01 | Test | diff | diff | pytest | PENDING | 03 |\n",
    )
    write_file(
        plan_folder / "03-execution.md",
        "# Execution\n\n## Objective\nTest.\n\n## Chosen logic\nTest.\n\n"
        "## Key assumptions\nTest.\n\n## Executable steps\n1. Do it.\n\n## Validation\nTest.\n",
    )
    write_file(plan_folder / "questions.md", "# Questions\n\n- none\n")


def make_extended_plan(plan_folder: Path) -> None:
    make_compact_plan(plan_folder)
    # Overwrite ledger with extended profile
    write_file(
        plan_folder / "02-source-item-ledger.md",
        "# Ledger\n\n"
        "## Recommended use\napply-plan\n\n"
        "## Plan profile\nextended\n\n"
        "## File map and role\n| File | Ruolo |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Initial evidence pass\ntarget, validator\n\n"
        "## Reading budget\nthis folder only\n\n"
        "## Target and anti-scope\nTest target.\n\n"
        "## Owner and validator\ninternal-gateway-operational-flow\n\n"
        "## Stop conditions\nNone.\n\n"
        "## Source item ledger\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| T-01 | Test | diff | diff | pytest | PENDING | 03 |\n",
    )
    write_file(
        plan_folder / "04-implementation-contract.md",
        "# Implementation Contract\n\n## Purpose\nTest.\n",
    )


def make_legacy_plan(plan_folder: Path) -> None:
    write_file(plan_folder / "01-summary-direction-and-decision.md", "# Summary\n")
    write_file(plan_folder / "02-operational-matrix.md", "# Matrix\n")
    write_file(plan_folder / "02-execution.md", "# Execution\n")
    write_file(plan_folder / "doubts-and-questions.md", "# Questions\n- none\n")


# Profile classification


def test_classify_compact_profile(tmp_path: Path) -> None:
    make_compact_plan(tmp_path / "plan")
    profile = PlanProfile.classify(tmp_path / "plan")
    assert profile.name == "compact"
    assert not profile.requires_implementation_contract


def test_classify_extended_profile(tmp_path: Path) -> None:
    make_extended_plan(tmp_path / "plan")
    profile = PlanProfile.classify(tmp_path / "plan")
    assert profile.name == "extended"
    assert profile.requires_implementation_contract


def test_classify_legacy_no_ledger(tmp_path: Path) -> None:
    folder = tmp_path / "plan"
    folder.mkdir()
    profile = PlanProfile.classify(folder)
    assert profile.name == "legacy"


def test_classify_legacy_no_profile_declared(tmp_path: Path) -> None:
    folder = tmp_path / "plan"
    folder.mkdir()
    write_file(folder / "02-source-item-ledger.md", "# Ledger\n\nNo profile declared.\n")
    profile = PlanProfile.classify(folder)
    assert profile.name == "legacy"


# Handoff validation


def test_handoff_compact_ready(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    make_compact_plan(plan)
    report = handoff_validate(plan)
    assert report.profile.name == "compact"
    assert report.ready
    assert report.clarification_gate_status == "satisfied"
    assert not report.ledger_fields_missing


def test_handoff_extended_ready(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    make_extended_plan(plan)
    report = handoff_validate(plan)
    assert report.profile.name == "extended"
    assert report.ready
    assert report.implementation_contract_present is True


def test_handoff_extended_missing_implementation_contract(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    make_compact_plan(plan)
    # Override ledger to extended but don't add implementation contract
    write_file(
        plan / "02-source-item-ledger.md",
        "# Ledger\n\n"
        "## Plan profile\nextended\n\n"
        "## Recommended use\napply-plan\n\n"
        "## File map and role\n| File | Ruolo |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Target and anti-scope\nT.\n\n"
        "## Owner and validator\nT.\n\n"
        "## Stop conditions\nT.\n\n"
        "## Source item ledger\n| ID | Source item | Acceptance | Evidence | Status | Route |\n",
    )
    report = handoff_validate(plan)
    assert report.profile.name == "extended"
    assert not report.ready
    assert any(f.code == "missing-implementation-contract" for f in report.findings)


def test_handoff_missing_required_files(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(
        plan / "02-source-item-ledger.md",
        "# Ledger\n\n## Plan profile\ncompact\n\n",
    )
    report = handoff_validate(plan)
    assert report.profile.name == "compact"
    assert not report.ready
    assert any(f.code == "missing-required-files" for f in report.findings)


def test_handoff_missing_ledger_fields(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "01-change-summary.md", "# Summary\n")
    write_file(
        plan / "02-source-item-ledger.md",
        "# Ledger\n\n## Plan profile\ncompact\n\nJust profile, nothing else.\n",
    )
    write_file(plan / "03-execution.md", "# Execution\n")
    write_file(plan / "questions.md", "- none\n")
    report = handoff_validate(plan)
    assert not report.ready
    assert any(f.code == "missing-ledger-fields" for f in report.findings)


def test_handoff_clarification_required_blocks(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    make_compact_plan(plan)
    write_file(
        plan / "02-source-item-ledger.md",
        "# Ledger\n\n"
        "## Recommended use\nreview\n\n"
        "## Plan profile\ncompact\n\n"
        "## File map and role\n| File | Ruolo |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification required\n\n"
        "## Target and anti-scope\nT.\n\n"
        "## Owner and validator\nT.\n\n"
        "## Stop conditions\nT.\n\n"
        "## Source item ledger\n| ID | Source item | Acceptance | Evidence | Status | Route |\n",
    )
    report = handoff_validate(plan)
    assert report.clarification_gate_status == "required"
    assert not report.ready
    assert any(f.code == "clarification-required" for f in report.findings)


def test_handoff_legacy_plan(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    make_legacy_plan(plan)
    report = handoff_validate(plan)
    assert report.profile.name == "legacy"
    # Legacy has no required files, so no file errors
    # But missing ledger is still flagged
    assert any(
        f.code == "missing-ledger" or f.code.startswith("missing-") for f in report.findings
    )


# Completion validation


def test_completion_ready(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "done-01-sample.md", "# Done\n")
    write_file(
        plan / "evidence-envelope.md",
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01-sample.md` | DONE | `pytest` |\n",
    )
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    assert report.ready


def test_completion_rejects_active_numbered_files(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "03-still-active.md", "# Active\n")
    write_file(plan / "evidence-envelope.md", "| Status |\n| --- |\n")
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "active-numbered-files" for f in report.findings)


def test_completion_rejects_open_statuses(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "done-01.md", "# Done\n")
    write_file(
        plan / "evidence-envelope.md",
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01.md` | PENDING | `pytest` |\n",
    )
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "open-status" for f in report.findings)


def test_completion_rejects_missing_evidence_columns(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "done-01.md", "# Done\n")
    write_file(plan / "evidence-envelope.md", "# Evidence\n\nJust text.\n")
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "missing-status-column" for f in report.findings)


def test_completion_rejects_missing_done_reference_in_envelope(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "done-01.md", "# Done\n")
    write_file(plan / "done-02.md", "# Done\n")
    write_file(
        plan / "evidence-envelope.md",
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01.md` | DONE | `pytest` |\n",
    )
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "missing-done-reference" for f in report.findings)


def test_completion_rejects_missing_report_fields(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "done-01.md", "# Done\n")
    write_file(
        plan / "evidence-envelope.md",
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01.md` | DONE | `pytest` |\n",
    )
    write_file(plan / "completion-report.md", "# Bare report\nNo fields.\n")
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "missing-report-field" for f in report.findings)


def test_completion_missing_envelope(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "missing-evidence-envelope" for f in report.findings)


def test_completion_missing_report(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(
        plan / "evidence-envelope.md",
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| item | DONE | test |\n",
    )
    report = completion_validate(plan)
    assert not report.ready
    assert any(f.code == "missing-completion-report" for f in report.findings)


# JSON output


def test_handoff_json_output(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    make_compact_plan(plan)
    report = handoff_validate(plan)
    d = report.as_dict()
    assert d["profile"] == "compact"
    assert d["ready"] is True
    assert d["clarification_gate_status"] == "satisfied"


def test_completion_json_output(tmp_path: Path) -> None:
    plan = tmp_path / "plan"
    plan.mkdir()
    write_file(plan / "done-01.md", "# Done\n")
    write_file(
        plan / "evidence-envelope.md",
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01.md` | DONE | `pytest` |\n",
    )
    write_file(plan / "completion-report.md", "\n".join(COMPLETION_REPORT_FIELDS) + "\n")
    report = completion_validate(plan)
    d = report.as_dict()
    assert d["ready"] is True
    assert d["evidence_envelope_present"] is True
    assert d["completion_report_present"] is True
