from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BENCHMARK_SCRIPT = Path(".github/scripts/benchmark_skill_tokens.py")


def run_benchmark() -> dict:
    result = subprocess.run(
        [sys.executable, str(BENCHMARK_SCRIPT)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_benchmark_skill_tokens_runs_without_error() -> None:
    output = run_benchmark()
    assert "scenarios" in output
    assert "descriptions" in output
    assert "summary" in output
    assert "idea_gateway" in output
    assert len(output["scenarios"]) > 0
    assert len(output["descriptions"]) > 0


def test_benchmark_detects_no_chain_risk_for_self_contained_skills() -> None:
    output = run_benchmark()

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


def test_gateway_scenarios_have_unique_required_skill_lists() -> None:
    output = run_benchmark()
    gateway_scenarios = output["gateway"]["required_context_scenarios"]
    for scenario in gateway_scenarios:
        skills = scenario["required_skills"]
        assert len(skills) == len(set(skills)), (
            f"Duplicate skills in scenario '{scenario['scenario']}': {skills}"
        )


def test_idea_gateway_scenarios_exist_and_are_unique() -> None:
    output = run_benchmark()
    idea_scenarios = output["idea_gateway"]["context_scenarios"]
    assert len(idea_scenarios) >= 4, (
        f"Expected >=4 idea-gateway scenarios, got {len(idea_scenarios)}"
    )

    scenario_names = {s["scenario"] for s in idea_scenarios}
    expected = {
        "Idea core entry",
        "Interview support",
        "Mandatory critical pass",
        "Visible handoff",
    }
    missing = expected - scenario_names
    assert not missing, f"Missing idea-gateway scenarios: {missing}"

    for scenario in idea_scenarios:
        skills = scenario["required_skills"]
        assert len(skills) == len(set(skills)), (
            f"Duplicate skills in scenario '{scenario['scenario']}': {skills}"
        )


def test_idea_gateway_progressive_totals_are_consistent() -> None:
    output = run_benchmark()
    idea_scenarios = output["idea_gateway"]["context_scenarios"]
    by_name = {s["scenario"]: s["estimated_tokens"] for s in idea_scenarios}

    core = by_name["Idea core entry"]
    interview = by_name["Interview support"]
    critical = by_name["Mandatory critical pass"]
    handoff = by_name["Visible handoff"]

    assert core > 0
    assert interview > core
    assert critical > 0
    assert handoff > core
