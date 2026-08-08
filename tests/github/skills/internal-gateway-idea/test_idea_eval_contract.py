from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Repository owner: .github/skills/internal-gateway-idea
HERE = Path(__file__).parent
EVALUATION = HERE / "evaluation"
FIXTURES = HERE / "fixtures"
SCORER = EVALUATION / "score_idea_eval.py"
BENCHMARK = EVALUATION / "benchmark.json"
PASSING_RUN = FIXTURES / "passing-run.json"
FAILING_RUN = FIXTURES / "failing-run.json"

EXPECTED_CASES = {
    "COVERAGE_OMISSION_BLOCK",
    "PLATFORM_ADAPTER_ONLY_BLOCK",
    "MINIMALITY_NEW_SKILL_BLOCK",
    "FULL_SCOPE_CRITIC_PASS",
    "DELTA_CRITIQUE_BLOCK",
    "MATERIAL_REVISION_RECRITIQUE",
    "STALE_RESUME_BLOCK",
    "LOW_RISK_PROPORTIONAL_PASS",
}

RESULT_LISTS = (
    "missing_case_ids",
    "duplicate_case_ids",
    "coverage_violation_cases",
    "platform_order_violation_cases",
    "minimality_violation_cases",
    "full_scope_violation_cases",
    "stale_critique_cases",
    "stale_resume_cases",
    "approval_order_violation_cases",
    "route_violation_cases",
)

OBSERVATION_FIELDS = {
    "case_id",
    "direct_skills",
    "declared_deliverable_ids",
    "covered_deliverable_ids",
    "platform_semantics_controlling",
    "primary_source_before_defaults",
    "minimality_options",
    "new_abstraction_selected",
    "new_abstraction_invariant",
    "new_abstraction_exit_criterion",
    "analysis_scope",
    "critic_context",
    "independent_fallback_routed",
    "material_revision_after_critique",
    "critic_rerun_after_revision",
    "resume_state",
    "stale_approval_reused",
    "final_plan_approval",
    "plan_writing_started",
    "expected_route",
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_idea_eval", SCORER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_cli(run: Path, manifest: Path = BENCHMARK) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--manifest",
            str(manifest),
            "--run",
            str(run),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_passing_record_covers_every_case_and_is_accepted() -> None:
    scorer = _load_scorer()
    result = scorer.score(_load(BENCHMARK), _load(PASSING_RUN))

    assert set(result["observed_case_ids"]) == EXPECTED_CASES
    assert result["missing_case_ids"] == []
    assert result["duplicate_case_ids"] == []
    for result_key in RESULT_LISTS[2:]:
        assert result[result_key] == []
    assert result["accepted"] is True


def test_failing_record_reports_each_behavior_violation() -> None:
    scorer = _load_scorer()
    result = scorer.score(_load(BENCHMARK), _load(FAILING_RUN))

    assert result["missing_case_ids"] == []
    assert result["duplicate_case_ids"] == []
    assert result["coverage_violation_cases"] == ["COVERAGE_OMISSION_BLOCK"]
    assert result["platform_order_violation_cases"] == [
        "PLATFORM_ADAPTER_ONLY_BLOCK"
    ]
    assert result["minimality_violation_cases"] == [
        "MINIMALITY_NEW_SKILL_BLOCK"
    ]
    assert result["full_scope_violation_cases"] == ["DELTA_CRITIQUE_BLOCK"]
    assert result["stale_critique_cases"] == ["MATERIAL_REVISION_RECRITIQUE"]
    assert result["stale_resume_cases"] == ["STALE_RESUME_BLOCK"]
    assert result["approval_order_violation_cases"] == ["FULL_SCOPE_CRITIC_PASS"]
    assert result["route_violation_cases"] == ["LOW_RISK_PROPORTIONAL_PASS"]
    assert result["accepted"] is False


def test_missing_and_duplicate_case_ids_are_rejected() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    observations = run["observations"]
    assert isinstance(observations, list)
    observations.pop()
    observations.append(dict(observations[0]))

    result = scorer.score(_load(BENCHMARK), run)

    assert result["missing_case_ids"] == ["LOW_RISK_PROPORTIONAL_PASS"]
    assert result["duplicate_case_ids"] == ["COVERAGE_OMISSION_BLOCK"]
    assert result["accepted"] is False


def test_observations_use_the_sanitized_exact_field_set() -> None:
    run = _load(PASSING_RUN)

    for observation in run["observations"]:
        assert set(observation) == OBSERVATION_FIELDS
        assert observation["analysis_scope"] in {"full", "delta"}
        assert observation["critic_context"] in {
            "independent",
            "same-context",
            "unavailable",
        }
        assert observation["resume_state"] in {"current", "stale", "missing"}
        assert observation["expected_route"] in {
            "reopen-analysis",
            "revise-design",
            "request-separate-review",
            "await-final-approval",
            "write-plan",
        }


def test_cli_returns_zero_for_an_accepted_run() -> None:
    completed = _run_cli(PASSING_RUN)

    assert completed.returncode == 0
    assert json.loads(completed.stdout)["accepted"] is True
    assert completed.stderr == ""
    assert len(completed.stdout.splitlines()) == 1


def test_cli_returns_one_for_a_scored_rejection() -> None:
    completed = _run_cli(FAILING_RUN)

    assert completed.returncode == 1
    assert json.loads(completed.stdout)["accepted"] is False
    assert completed.stderr == ""


@pytest.mark.parametrize(
    "payload",
    ("{", "{}"),
)
def test_cli_returns_two_for_malformed_or_missing_required_input(
    tmp_path: Path, payload: str
) -> None:
    invalid_run = tmp_path / "invalid-run.json"
    invalid_run.write_text(payload, encoding="utf-8")

    completed = _run_cli(invalid_run)

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr.startswith("error:")


def test_cli_rejects_manifest_without_required_case_ids(tmp_path: Path) -> None:
    invalid_manifest = tmp_path / "invalid-manifest.json"
    invalid_manifest.write_text("{}\n", encoding="utf-8")

    completed = _run_cli(PASSING_RUN, invalid_manifest)

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr.startswith("error:")
