from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
EVALUATION = HERE / "evaluation"
FIXTURES = HERE / "fixtures"
SCORER = EVALUATION / "score_gateway_eval.py"
BENCHMARK = EVALUATION / "benchmark.json"
PASSING_RUN = FIXTURES / "passing-run.json"
FAILING_RUN = FIXTURES / "failing-run.json"

EXPECTED_CASES = {
    "CLEAR_REPORT_STOP",
    "NON_CLEAR_RETRY",
    "UNAVAILABLE_EVIDENCE_BLOCK",
    "REPORT_INPUT_IDENTITY",
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_gateway_eval", SCORER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_cli(run: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--manifest",
            str(BENCHMARK),
            "--run",
            str(run),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_passing_record_covers_every_gateway_branch() -> None:
    scorer = _load_scorer()
    result = scorer.score(_load(BENCHMARK), _load(PASSING_RUN))

    assert set(result["observed_case_ids"]) == EXPECTED_CASES
    assert result["missing_case_ids"] == []
    assert result["report_order_violation_cases"] == []
    assert result["identity_drift_cases"] == []
    assert result["missing_fingerprint_cases"] == []
    assert result["invalid_critic_state_cases"] == []
    assert result["missing_rerun_or_resume_cases"] == []
    assert result["false_report_return_cases"] == []
    assert result["missing_report_return_cases"] == []
    assert result["post_report_violation_cases"] == []
    assert result["accepted"] is True


def test_failing_record_reports_each_transition_violation() -> None:
    scorer = _load_scorer()
    result = scorer.score(_load(BENCHMARK), _load(FAILING_RUN))

    assert result["missing_case_ids"] == []
    assert result["report_order_violation_cases"] == ["CRITIQUE_BEFORE_REPORT"]
    assert result["identity_drift_cases"] == ["REPORT_INPUT_IDENTITY"]
    assert result["missing_fingerprint_cases"] == ["CLEAR_REPORT_STOP"]
    assert result["invalid_critic_state_cases"] == ["NON_CLEAR_RETRY"]
    assert result["missing_rerun_or_resume_cases"] == ["NON_CLEAR_NO_RERUN"]
    assert result["false_report_return_cases"] == ["NON_CLEAR_RETURNED_REPORT"]
    assert result["missing_report_return_cases"] == ["CLEAR_NO_RETURN"]
    assert result["post_report_violation_cases"] == ["POST_REPORT_ACTION"]
    assert result["accepted"] is False


@pytest.mark.parametrize(
    "missing_field",
    (
        "report_fingerprint",
        "critic_input_fingerprint",
    ),
)
def test_report_written_requires_every_fingerprint(missing_field: str) -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    clear_case = run["observations"][0]
    clear_case[missing_field] = None

    result = scorer.score(_load(BENCHMARK), run)

    assert result["missing_fingerprint_cases"] == ["CLEAR_REPORT_STOP"]
    assert result["accepted"] is False


def test_report_observation_requires_report_and_critic_fingerprints() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    retry_case = run["observations"][1]
    retry_case["critic_input_fingerprint"] = None

    result = scorer.score(_load(BENCHMARK), run)

    assert result["missing_fingerprint_cases"] == ["NON_CLEAR_RETRY"]
    assert result["accepted"] is False


def test_report_must_exist_before_critique() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    run["observations"][0]["report_written_before_critique"] = False

    result = scorer.score(_load(BENCHMARK), run)

    assert result["report_order_violation_cases"] == ["CLEAR_REPORT_STOP"]
    assert result["accepted"] is False


def test_non_clear_pass_requires_fresh_report_rerun_or_resume_condition() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    retry_case = run["observations"][1]
    retry_case["reran_external_report_flow"] = False
    retry_case["resume_condition"] = None

    result = scorer.score(_load(BENCHMARK), run)

    assert result["missing_rerun_or_resume_cases"] == ["NON_CLEAR_RETRY"]
    assert result["accepted"] is False


def test_only_clear_pass_may_return_report() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    retry_case = run["observations"][1]
    retry_case["report_returned"] = True

    result = scorer.score(_load(BENCHMARK), run)

    assert result["false_report_return_cases"] == ["NON_CLEAR_RETRY"]
    assert result["accepted"] is False


def test_clear_pass_must_return_completed_report() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    run["observations"][0]["report_returned"] = False

    result = scorer.score(_load(BENCHMARK), run)

    assert result["missing_report_return_cases"] == ["CLEAR_REPORT_STOP"]
    assert result["accepted"] is False


def test_non_null_critic_state_must_use_canonical_enums() -> None:
    scorer = _load_scorer()
    run = _load(PASSING_RUN)
    run["observations"][0]["critical_outcome"] = "blocked"
    run["observations"][3]["defense"] = "partly"

    result = scorer.score(_load(BENCHMARK), run)

    assert result["invalid_critic_state_cases"] == [
        "CLEAR_REPORT_STOP",
        "REPORT_INPUT_IDENTITY",
    ]
    assert result["accepted"] is False


def test_cli_returns_zero_for_an_accepted_run() -> None:
    completed = _run_cli(PASSING_RUN)

    assert completed.returncode == 0
    assert json.loads(completed.stdout)["accepted"] is True
    assert completed.stderr == ""


def test_cli_returns_one_for_a_scored_rejection() -> None:
    completed = _run_cli(FAILING_RUN)

    assert completed.returncode == 1
    assert json.loads(completed.stdout)["accepted"] is False
    assert completed.stderr == ""


def test_cli_returns_two_for_malformed_input(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{}\n", encoding="utf-8")

    completed = _run_cli(malformed)

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr.startswith("error:")
