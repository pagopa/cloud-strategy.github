from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
EVALUATION = HERE / "evaluation"
BENCHMARK = EVALUATION / "benchmark.json"
SCORER = EVALUATION / "score_executor_eval.py"
EXPECTED_CASES = {
    "VALID_PLAN_DONE",
    "IN_TARGET_OMISSION_DONE",
    "DISTINCT_SAFE_REPAIR_DONE",
    "PRE_EXISTING_FAILURE_RESIDUAL",
    "AUTHORITY_GAP_BLOCKED",
}
HASHES = {
    "plan_fingerprint": "sha256:" + "1" * 64,
    "content_hash": "sha256:" + "2" * 64,
}
TASKS = ["T1", "T2", "T3"]


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_executor_eval", SCORER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _observation(case_id: str, status: str) -> dict[str, object]:
    completed = TASKS if status == "DONE" else ["T1"]
    remaining = [] if status == "DONE" else ["T2", "T3"]
    next_action = "none" if status == "DONE" else "Continue the approved task loop."
    return {
        "case_id": case_id,
        "status": status,
        "plan_reference_matches": True,
        "plan_fingerprint": HASHES["plan_fingerprint"],
        "state_plan_fingerprint": HASHES["plan_fingerprint"],
        "content_hash": HASHES["content_hash"],
        "state_content_hash": HASHES["content_hash"],
        "manifest_task_ids": TASKS.copy(),
        "completed_task_ids": completed,
        "remaining_task_ids": remaining,
        "dispatch_events": [],
        "edits": [],
        "validation_events": [],
        "repairs": [],
        "omission_detected": False,
        "omission_clearly_implied": False,
        "omission_repaired": False,
        "omission_repair_in_target": False,
        "authority_required": status == "BLOCKED",
        "pre_existing_failures": [],
        "independent_tasks_executable": status != "BLOCKED",
        "residual_failures": [],
        "last_validation": "focused validation passed",
        "next_action": next_action,
        "next_action_count": 0 if status == "DONE" else 1,
        "report_lines": [
            "Plan: tmp/superpowers/plans/example.md",
            "Changed: approved executor targets",
            "Checks: focused validation passed",
            f"Next: {next_action}",
        ],
    }


def _passing_run() -> dict[str, object]:
    valid = _observation("VALID_PLAN_DONE", "DONE")
    omission = _observation("IN_TARGET_OMISSION_DONE", "DONE")
    omission.update(
        {
            "edits": [{"path": "approved/target.py", "in_target": True}],
            "omission_detected": True,
            "omission_clearly_implied": True,
            "omission_repaired": True,
            "omission_repair_in_target": True,
        }
    )
    repair = _observation("DISTINCT_SAFE_REPAIR_DONE", "DONE")
    repair.update(
        {
            "validation_events": [
                {"id": "focused", "outcome": "failed", "repair_id": None},
                {"id": "focused", "outcome": "passed", "repair_id": "repair-1"},
            ],
            "repairs": [
                {"id": "repair-1", "safe": True, "in_target": True, "distinct": True}
            ],
        }
    )
    residual = _observation("PRE_EXISTING_FAILURE_RESIDUAL", "PARTIAL")
    residual.update(
        {
            "pre_existing_failures": ["baseline environment failure"],
            "independent_tasks_executable": True,
            "residual_failures": ["baseline environment failure"],
        }
    )
    blocked = _observation("AUTHORITY_GAP_BLOCKED", "BLOCKED")
    blocked.update(
        {
            "authority_required": True,
            "independent_tasks_executable": False,
            "next_action": "Request explicit scope approval.",
            "next_action_count": 1,
            "report_lines": [
                "Plan: tmp/superpowers/plans/example.md",
                "Changed: no out-of-scope changes",
                "Checks: authority boundary blocks the next task",
                "Next: Request explicit scope approval.",
            ],
        }
    )
    return {
        "contract_version": "internal-gateway-execute-plans-eval-v1",
        "observations": [valid, omission, repair, residual, blocked],
    }


def test_benchmark_declares_exactly_five_branches() -> None:
    benchmark = _load(BENCHMARK)

    assert set(benchmark["required_case_ids"]) == EXPECTED_CASES
    assert len(benchmark["required_case_ids"]) == 5


def test_five_observed_branches_are_accepted() -> None:
    scorer = _load_scorer()
    result = scorer.score(_load(BENCHMARK), _passing_run())

    assert set(result["observed_case_ids"]) == EXPECTED_CASES
    assert result["missing_case_ids"] == []
    assert result["accepted"] is True
    assert result["dispatch_violation_cases"] == []
    assert result["hash_binding_violation_cases"] == []
    assert result["task_closure_violation_cases"] == []
    assert result["report_shape_violation_cases"] == []


def test_scorer_rejects_forbidden_dispatch() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][0]["dispatch_events"] = ["subagent"]

    result = scorer.score(_load(BENCHMARK), run)

    assert result["dispatch_violation_cases"] == ["VALID_PLAN_DONE"]
    assert result["accepted"] is False


def test_scorer_rejects_unbound_hashes() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][1]["state_content_hash"] = "sha256:" + "3" * 64

    result = scorer.score(_load(BENCHMARK), run)

    assert result["hash_binding_violation_cases"] == ["IN_TARGET_OMISSION_DONE"]
    assert result["accepted"] is False


def test_scorer_rejects_incomplete_task_closure() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][0]["remaining_task_ids"] = ["T2"]

    result = scorer.score(_load(BENCHMARK), run)

    assert result["task_closure_violation_cases"] == ["VALID_PLAN_DONE"]
    assert result["accepted"] is False


def test_scorer_rejects_extra_report_line() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][0]["report_lines"].append("Extra: line")

    result = scorer.score(_load(BENCHMARK), run)

    assert result["report_shape_violation_cases"] == ["VALID_PLAN_DONE"]
    assert result["accepted"] is False


def test_authority_branch_rejects_out_of_scope_edit() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][4]["edits"] = [
        {"path": "outside/approved-target.py", "in_target": False}
    ]

    result = scorer.score(_load(BENCHMARK), run)

    assert result["scope_violation_cases"] == ["AUTHORITY_GAP_BLOCKED"]
    assert result["branch_violation_cases"] == ["AUTHORITY_GAP_BLOCKED"]
    assert result["accepted"] is False


@pytest.mark.parametrize("accepted", (True, False))
def test_cli_reports_structured_acceptance(tmp_path: Path, accepted: bool) -> None:
    benchmark = tmp_path / "benchmark.json"
    run = tmp_path / "run.json"
    benchmark.write_text(json.dumps(_load(BENCHMARK)), encoding="utf-8")
    payload = _passing_run()
    if not accepted:
        payload["observations"][0]["status"] = "NEEDS_REVIEW"
    run.write_text(json.dumps(payload), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--manifest",
            str(benchmark),
            "--run",
            str(run),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == (0 if accepted else 1)
    assert json.loads(completed.stdout)["accepted"] is accepted
    assert completed.stderr == ""
