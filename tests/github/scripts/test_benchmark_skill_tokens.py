from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

BENCHMARK_SCRIPT = Path(".github/scripts/benchmark_skill_tokens.py")


def test_benchmark_skill_tokens_runs_without_error() -> None:
    result = subprocess.run(
        [sys.executable, str(BENCHMARK_SCRIPT)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "scenarios" in output
    assert "descriptions" in output
    assert "summary" in output
    assert len(output["scenarios"]) > 0
    assert len(output["descriptions"]) > 0


def test_benchmark_detects_no_chain_risk_for_self_contained_skills() -> None:
    result = subprocess.run(
        [sys.executable, str(BENCHMARK_SCRIPT)],
        capture_output=True,
        text=True,
        check=True,
    )
    output = json.loads(result.stdout)

    # Self-contained skills modified in this plan should have no chain risks
    self_contained_skills = {
        "internal-python-script",
        "internal-python-project",
        "internal-bash-script",
        "internal-nodejs-project",
        "internal-java-project",
    }

    for scenario in output["scenarios"]:
        if scenario["expected_owner"] in self_contained_skills:
            assert scenario["chain_risks"] == [], (
                f"Expected no chain risks for {scenario['expected_owner']} "
                f"but found {scenario['chain_risks']}"
            )
