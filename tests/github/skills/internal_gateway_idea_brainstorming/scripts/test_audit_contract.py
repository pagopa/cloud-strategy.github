from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(
    ".github/skills/internal-gateway-idea-brainstorming/scripts/audit_contract.py"
)


def run_json(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_audit_reports_minimal_marker_shape() -> None:
    report = run_json()
    assert set(report["markers"]) == {
        "critical",
        "planning",
        "stop_before_execution",
        "bounded_evidence_pass",
        "facts_options_summary",
        "intent_traceability",
        "plan_approval_gate",
        "handoff_gate_4",
        "ask_before_critical",
        "explicit_plan_approval",
        "alias_mapping",
    }
    assert report["strict_ok"] is True


def test_audit_script_emits_json_for_invocation() -> None:
    report = run_json()
    assert isinstance(report, dict)


def test_audit_script_checks_the_canonical_planning_owner() -> None:
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "internal-gateway-writing-plans" in script_text
    assert "internal-writing-plans" not in script_text
