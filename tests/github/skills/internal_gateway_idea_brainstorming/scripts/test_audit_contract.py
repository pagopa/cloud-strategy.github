from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(".github/skills/internal-gateway-idea-brainstorming/scripts/audit_contract.py")


def run_json(*args: str) -> dict:
    result = subprocess.run([sys.executable, str(SCRIPT_PATH), *args], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_audit_reports_minimal_marker_shape() -> None:
    report = run_json()
    assert set(report["markers"]) == {"critical", "planning", "stop_before_execution"}
    assert report["strict_ok"] is True


def test_audit_script_emits_json_for_invocation() -> None:
    report = run_json()
    assert isinstance(report, dict)
