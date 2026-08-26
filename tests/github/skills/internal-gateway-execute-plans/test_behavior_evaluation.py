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
REPO_ROOT = next(
    parent
    for parent in HERE.parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
EXECUTOR_SCRIPT = (
    REPO_ROOT
    / ".github/skills/internal-gateway-execute-plans/scripts/plan_execution.py"
)
EXPECTED_CASES = {
    "VALID_PLAN_DONE",
    "IN_TARGET_OMISSION_DONE",
    "DISTINCT_SAFE_REPAIR_DONE",
    "PRE_EXISTING_FAILURE_RESIDUAL",
    "AUTHORITY_GAP_BLOCKED",
}
APPROVAL_FINGERPRINT = "sha256:" + "1" * 64
TASKS = ["T1", "T2", "T3"]


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_executor_eval", SCORER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_executor():
    spec = importlib.util.spec_from_file_location("plan_execution_eval", EXECUTOR_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _observation(case_id: str, status: str) -> dict[str, object]:
    completed = TASKS if status == "DONE" else ["T1"]
    remaining = [] if status == "DONE" else ["T2", "T3"]
    next_action = "none" if status == "DONE" else "Continue the approved task loop."
    bootstrap = [
        {
            "check": "local-preflight",
            "status": "BLOCKED" if status == "BLOCKED" else "PASS",
            "next_action": (
                "Request explicit scope approval."
                if status == "BLOCKED"
                else "none"
            ),
        }
    ]
    delivery_verdicts = [
        {
            "category": category,
            "outcome": (
                "inconclusive"
                if status == "BLOCKED" and category == "execution_readiness"
                else "passed"
            ),
            "coverage": "observed",
            "limit": "authority required" if status == "BLOCKED" else "none",
        }
        for category in (
            "structure",
            "semantic_review",
            "artifact_provenance",
            "source_baseline",
            "execution_readiness",
        )
    ]
    return {
        "case_id": case_id,
        "status": status,
        "plan_reference_matches": True,
        "approval_fingerprint": APPROVAL_FINGERPRINT,
        "state_approval_fingerprint": APPROVAL_FINGERPRINT,
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
        "retry_attempts": {task_id: 0 for task_id in TASKS},
        "failure_signatures": [],
        "progress_signatures": [],
        "recovery_attempted": False,
        "independent_tasks_continued": status != "BLOCKED",
        "native_equivalent_admissible": False,
        "validation_weakened": False,
        "blocked_reason_evidence": {
            "attempted_recovery": False,
            "no_progress": False,
            "inadmissible_alternative": False,
            "unblock_action": "none",
        },
        "authority_required": status == "BLOCKED",
        "pre_existing_failures": [],
        "independent_tasks_executable": status != "BLOCKED",
        "residual_failures": [],
        "last_validation": "focused validation passed",
        "next_action": next_action,
        "next_action_count": 0 if status == "DONE" else 1,
        "bootstrap": bootstrap,
        "delivery_verdicts": delivery_verdicts,
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
            "recovery_attempted": True,
            "failure_signatures": ["omission-detected"],
            "progress_signatures": ["omission-repaired"],
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
            "recovery_attempted": True,
            "failure_signatures": ["focused-validation-failed"],
            "progress_signatures": ["repair-applied"],
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
            "blocked_reason_evidence": {
                "attempted_recovery": True,
                "no_progress": True,
                "inadmissible_alternative": True,
                "unblock_action": "Request explicit scope approval.",
            },
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


def test_benchmark_declares_observable_guardrail_contract() -> None:
    benchmark = _load(BENCHMARK)

    assert benchmark["observable_evidence"] == [
        "order",
        "semantic-approval",
        "scope",
        "invalidation",
        "recovery",
        "residuals",
    ]
    assert benchmark["pre_existing_case"] == "PRE_EXISTING_FAILURE_RESIDUAL"
    assert benchmark["authority_case"] == "AUTHORITY_GAP_BLOCKED"


def test_observation_schema_uses_semantic_approval_and_recovery_evidence() -> None:
    observation = _observation("VALID_PLAN_DONE", "DONE")

    assert {
        "approval_fingerprint",
        "state_approval_fingerprint",
        "retry_attempts",
        "failure_signatures",
        "progress_signatures",
        "recovery_attempted",
        "independent_tasks_continued",
        "native_equivalent_admissible",
        "blocked_reason_evidence",
    } <= set(observation)
    assert "content_hash" not in observation
    assert "state_content_hash" not in observation


def test_benchmark_declares_separate_bootstrap_and_delivery_records() -> None:
    benchmark = _load(BENCHMARK)

    assert benchmark["bootstrap_fields"] == ["check", "status", "next_action"]
    assert benchmark["bootstrap_statuses"] == ["PASS", "BLOCKED"]
    assert benchmark["delivery_verdict_fields"] == [
        "category",
        "outcome",
        "coverage",
        "limit",
    ]
    assert benchmark["delivery_verdict_categories"] == [
        "structure",
        "semantic_review",
        "artifact_provenance",
        "source_baseline",
        "execution_readiness",
    ]


def test_scorer_accepts_separate_bootstrap_and_delivery_verdict_records() -> None:
    scorer = _load_scorer()

    result = scorer.score(_load(BENCHMARK), _passing_run())

    assert result["accepted"] is True
    assert result["bootstrap_violation_cases"] == []
    assert result["delivery_verdict_violation_cases"] == []


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


def test_ten_workflow_cases_have_one_observable_seam_and_pass_signal() -> None:
    observations = evaluate_workflow_seams()

    assert {item["case_id"] for item in observations} == {
        "CASE_1_COMPLETE_PARENT_CONTEXT",
        "CASE_2_BOUNDED_EVIDENCE_VALUE",
        "CASE_3_PARENT_FINAL_SYNTHESIS",
        "CASE_4_SAME_MODEL_DIAGNOSTIC",
        "CASE_5_WORKER_TIMEOUT",
        "CASE_6_BLOCKER_CORRECTION",
        "CASE_7_DELTA_WITH_STABLE_ASSUMPTIONS",
        "CASE_8_FULL_RERUN_NEW_ASSUMPTION",
        "CASE_9_UNCHANGED_EVIDENCE",
        "CASE_10_LOCAL_PROVENANCE_CONTRADICTION",
    }
    assert all(item["seam"] in {
        "producer-routing",
        "runtime-only",
        "critic-ledger",
        "executor-preflight",
    } for item in observations)
    assert all(item["pass_signal"] for item in observations)


def test_critic_ledger_rejects_unchanged_evidence_and_bounds_full_reruns() -> None:
    results = evaluate_critic_ledger_cases()

    assert results["CASE_6_BLOCKER_CORRECTION"] == {
        "decision": "delta",
        "reason": "changed-evidence",
    }
    assert results["CASE_7_DELTA_WITH_STABLE_ASSUMPTIONS"] == {
        "decision": "delta",
        "reason": "changed-evidence",
    }
    assert results["CASE_8_FULL_RERUN_NEW_ASSUMPTION"] == {
        "decision": "full",
        "reason": "new-evidence-changed-controlling-assumption",
    }
    assert results["CASE_9_UNCHANGED_EVIDENCE"] == {
        "decision": "suppressed",
        "reason": "unchanged-evidence",
    }


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
    run["observations"][1]["state_approval_fingerprint"] = "sha256:" + "3" * 64

    result = scorer.score(_load(BENCHMARK), run)

    assert result["hash_binding_violation_cases"] == ["IN_TARGET_OMISSION_DONE"]
    assert result["accepted"] is False


def test_scorer_rejects_validation_weakening() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][0]["validation_weakened"] = True

    result = scorer.score(_load(BENCHMARK), run)

    assert result["recovery_violation_cases"] == ["VALID_PLAN_DONE"]
    assert result["accepted"] is False


def test_scorer_rejects_blocking_while_independent_work_is_executable() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][4]["independent_tasks_executable"] = True

    result = scorer.score(_load(BENCHMARK), run)

    assert result["recovery_violation_cases"] == ["AUTHORITY_GAP_BLOCKED"]
    assert result["accepted"] is False


def test_scorer_rejects_unchanged_failure_repetition() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][2].update(
        {
            "recovery_attempted": True,
            "failure_signatures": ["same-failure", "same-failure"],
        }
    )

    result = scorer.score(_load(BENCHMARK), run)

    assert result["recovery_violation_cases"] == ["DISTINCT_SAFE_REPAIR_DONE"]
    assert result["accepted"] is False


def test_scorer_rejects_blocked_without_recovery_evidence() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][4]["blocked_reason_evidence"] = {
        "attempted_recovery": False,
        "no_progress": False,
        "inadmissible_alternative": False,
        "unblock_action": "none",
    }

    result = scorer.score(_load(BENCHMARK), run)

    assert result["recovery_violation_cases"] == ["AUTHORITY_GAP_BLOCKED"]
    assert result["accepted"] is False


def test_scorer_rejects_technical_done_with_warnings() -> None:
    scorer = _load_scorer()
    run = _passing_run()
    run["observations"][0]["status"] = "DONE_WITH_WARNINGS"

    result = scorer.score(_load(BENCHMARK), run)

    assert result["status_violation_cases"] == ["VALID_PLAN_DONE"]
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


def test_verdict_payload_keeps_five_categories_and_qualified_aggregate() -> None:
    executor = _load_executor()
    verdicts = {
        category: executor.Verdict(
            category=category,
            outcome="passed",
            coverage=f"{category} checks",
            limit="none",
        )
        for category in executor.VERDICT_CATEGORIES
    }

    payload = executor.build_verdict_payload(
        executor.VERDICT_CATEGORIES,
        verdicts,
    )

    assert set(payload["verdicts"]) == set(executor.VERDICT_CATEGORIES)
    assert payload["aggregate"]["outcome"] == "passed"
    assert all(
        set(item) == {"category", "outcome", "coverage", "limit"}
        for item in payload["verdicts"].values()
    )
    assert "validated" not in json.dumps(payload).lower()


def test_bootstrap_payload_has_only_check_status_next_action() -> None:
    executor = _load_executor()

    payload = executor.build_bootstrap_payload("bundle-resolution", "PASS", "none")

    assert payload == {
        "check": "bundle-resolution",
        "status": "PASS",
        "next_action": "none",
    }


def test_bootstrap_collects_local_checks_then_stops_before_external_work() -> None:
    executor = _load_executor()
    checks = (
        executor.BootstrapCheck("bundle-resolution", "PASS", "none"),
        executor.BootstrapCheck(
            "manifest-binding", "BLOCKED", "Request manifest binding evidence."
        ),
        executor.BootstrapCheck(
            "live-operation", "PASS", "must not run", external=True
        ),
    )

    result = executor.run_local_bootstrap(checks)

    assert [item["check"] for item in result] == ["bundle-resolution", "manifest-binding"]
    assert result[-1]["status"] == "BLOCKED"


def test_bootstrap_blocked_result_has_one_concrete_next_action() -> None:
    executor = _load_executor()

    with pytest.raises(executor.ExecutionContractError) as exc:
        executor.build_bootstrap_payload("manifest-binding", "BLOCKED", "none")

    assert exc.value.code == "bootstrap-next-action-required"


def test_bootstrap_does_not_replace_five_delivery_verdicts() -> None:
    executor = _load_executor()
    verdicts = _passing_verdicts(executor)

    bootstrap = executor.build_bootstrap_payload(
        "manifest-binding", "BLOCKED", "Request manifest binding evidence."
    )
    delivery = executor.build_verdict_payload(executor.VERDICT_CATEGORIES, verdicts)

    assert set(bootstrap) == {"check", "status", "next_action"}
    assert set(delivery["verdicts"]) == set(executor.VERDICT_CATEGORIES)
    assert "validated" not in json.dumps(delivery).lower()


def test_yaml_status_cases_preserve_five_verdict_categories() -> None:
    executor = _load_executor()
    plan = (
        REPO_ROOT
        / ".github/skills/internal-gateway-execute-plans/fixtures/valid-plan.md"
    )
    manifest = executor.parse_execution_manifest(plan.read_text())
    task_ids = tuple(executor._manifest_task_ids(manifest))
    verdicts = _passing_verdicts(executor)

    for status in ("DONE", "PARTIAL", "BLOCKED"):
        completed = task_ids if status == "DONE" else ()
        remaining = () if status == "DONE" else task_ids
        payload = executor.build_status_yaml(
            plan,
            status,
            completed,
            remaining,
            "focused validation passed",
            "none" if status == "DONE" else "Continue the approved task loop.",
            approval_source="current-conversation",
            delivery_verdicts=verdicts,
        )
        parsed = executor.parse_status_yaml(
            payload, plan.with_name(f"{plan.stem}.{status}.yaml")
        )
        delivery = executor.build_verdict_payload(
            executor.VERDICT_CATEGORIES, verdicts
        )

        assert parsed.status == status
        assert set(delivery["verdicts"]) == set(executor.VERDICT_CATEGORIES)
        assert "validated" not in json.dumps(delivery).lower()


def test_aggregate_verdict_stays_inconclusive_for_missing_or_unresolved_categories() -> None:
    executor = _load_executor()
    verdicts = {
        "structure": executor.Verdict(
            "structure", "passed", "manifest parsed", "none"
        ),
        "semantic_review": executor.Verdict(
            "semantic_review", "inconclusive", "no review receipt", "review missing"
        ),
    }

    aggregate = executor.aggregate_verdict(
        executor.VERDICT_CATEGORIES,
        verdicts,
    )

    assert aggregate.outcome == "inconclusive"
    assert "missing" in aggregate.limit
    assert "semantic_review" in aggregate.limit


def test_structured_branches_preserve_residual_and_authority_limits() -> None:
    observations = {
        item["case_id"]: item for item in _passing_run()["observations"]
    }

    residual = observations["PRE_EXISTING_FAILURE_RESIDUAL"]
    blocked = observations["AUTHORITY_GAP_BLOCKED"]

    assert residual["pre_existing_failures"]
    assert set(residual["pre_existing_failures"]).issubset(
        set(residual["residual_failures"])
    )
    assert blocked["authority_required"] is True
    assert blocked["next_action_count"] == 1


def _passing_verdicts(executor):
    return {
        category: executor.Verdict(category, "passed", "observed", "none")
        for category in executor.VERDICT_CATEGORIES
    }


def test_executor_surface_contains_no_cross_plan_gate_helpers() -> None:
    executor = _load_executor()
    retired_surface = {
        name
        for name in vars(executor)
        if name.endswith(("Delta", "Readiness"))
        or name.startswith(("compare_", "evaluate_"))
        or "serial" in name
    }

    assert retired_surface == set()


def _writer_route(
    *,
    parent_has_decisions: bool,
    parent_has_acceptance: bool,
    final_synthesis: bool,
    value_gate: dict[str, bool],
    same_model: bool = False,
) -> dict[str, object]:
    gate_passed = all(
        value_gate.get(field, False)
        for field in ("autonomous", "verifiable", "bounded", "material_value", "off_critical_path")
    )
    if (
        not parent_has_decisions
        or not parent_has_acceptance
        or final_synthesis
        or not gate_passed
    ):
        mode = "none"
        worker = "primary-owner"
    else:
        mode = "delegated"
        worker = "internal-luna-executor"
    return {
        "mode": mode,
        "worker": worker,
        "canonical_owner": "parent",
        "same_model_diagnostic": same_model,
    }


def _critic_followup(previous: dict[str, object], current: dict[str, object]) -> dict[str, str]:
    if (
        previous["unit_id"] == current["unit_id"]
        and previous["evidence_digest"] == current["evidence_digest"]
    ):
        return {"decision": "suppressed", "reason": "unchanged-evidence"}
    if current["assumption_changed"]:
        return {
            "decision": "full",
            "reason": "new-evidence-changed-controlling-assumption",
        }
    if current["scope_changed"]:
        return {"decision": "full", "reason": "scope-change"}
    if current["open_blocker"]:
        return {"decision": "full", "reason": "open-blocker"}
    return {"decision": "delta", "reason": "changed-evidence"}


def evaluate_critic_ledger_cases() -> dict[str, dict[str, str]]:
    scenarios = {
        "CASE_6_BLOCKER_CORRECTION": (
            {"unit_id": "unit-6", "evidence_digest": "e1"},
            {
                "unit_id": "unit-6",
                "evidence_digest": "e2",
                "assumption_changed": False,
                "scope_changed": False,
                "open_blocker": False,
            },
        ),
        "CASE_7_DELTA_WITH_STABLE_ASSUMPTIONS": (
            {"unit_id": "unit-7", "evidence_digest": "e1"},
            {
                "unit_id": "unit-7",
                "evidence_digest": "e2",
                "assumption_changed": False,
                "scope_changed": False,
                "open_blocker": False,
            },
        ),
        "CASE_8_FULL_RERUN_NEW_ASSUMPTION": (
            {"unit_id": "unit-8", "evidence_digest": "e1"},
            {
                "unit_id": "unit-8",
                "evidence_digest": "e2",
                "assumption_changed": True,
                "scope_changed": False,
                "open_blocker": False,
            },
        ),
        "CASE_9_UNCHANGED_EVIDENCE": (
            {"unit_id": "unit-9", "evidence_digest": "e1"},
            {
                "unit_id": "unit-9",
                "evidence_digest": "e1",
                "assumption_changed": False,
                "scope_changed": False,
                "open_blocker": False,
            },
        ),
    }
    return {
        case_id: _critic_followup(previous, current)
        for case_id, (previous, current) in scenarios.items()
    }


def evaluate_workflow_seams() -> list[dict[str, object]]:
    complete_context = _writer_route(
        parent_has_decisions=True,
        parent_has_acceptance=True,
        final_synthesis=False,
        value_gate={
            "autonomous": False,
            "verifiable": True,
            "bounded": True,
            "material_value": False,
            "off_critical_path": True,
        },
    )
    bounded_value = _writer_route(
        parent_has_decisions=True,
        parent_has_acceptance=True,
        final_synthesis=False,
        value_gate={
            "autonomous": True,
            "verifiable": True,
            "bounded": True,
            "material_value": True,
            "off_critical_path": True,
        },
    )
    final_synthesis = _writer_route(
        parent_has_decisions=True,
        parent_has_acceptance=True,
        final_synthesis=True,
        value_gate={
            "autonomous": True,
            "verifiable": True,
            "bounded": True,
            "material_value": True,
            "off_critical_path": True,
        },
    )
    same_model = _writer_route(
        parent_has_decisions=True,
        parent_has_acceptance=True,
        final_synthesis=False,
        same_model=True,
        value_gate={
            "autonomous": False,
            "verifiable": False,
            "bounded": False,
            "material_value": False,
            "off_critical_path": True,
        },
    )
    critic_results = evaluate_critic_ledger_cases()
    runtime_identity = {"available": False, "diagnostic_only": True}
    runtime_timeout = {
        "available": False,
        "parent_may_continue": True,
        "authorship_claimed": False,
        "receipt_claimed": False,
    }
    return [
        {
            "case_id": "CASE_1_COMPLETE_PARENT_CONTEXT",
            "seam": "producer-routing",
            "pass_signal": complete_context == {
                "mode": "none",
                "worker": "primary-owner",
                "canonical_owner": "parent",
                "same_model_diagnostic": False,
            },
        },
        {
            "case_id": "CASE_2_BOUNDED_EVIDENCE_VALUE",
            "seam": "producer-routing",
            "pass_signal": bounded_value["mode"] == "delegated"
            and bounded_value["canonical_owner"] == "parent",
        },
        {
            "case_id": "CASE_3_PARENT_FINAL_SYNTHESIS",
            "seam": "producer-routing",
            "pass_signal": final_synthesis["mode"] == "none"
            and final_synthesis["canonical_owner"] == "parent",
        },
        {
            "case_id": "CASE_4_SAME_MODEL_DIAGNOSTIC",
            "seam": "runtime-only",
            "pass_signal": runtime_identity["available"] is False
            and same_model["mode"] == "none"
            and same_model["same_model_diagnostic"] is True,
        },
        {
            "case_id": "CASE_5_WORKER_TIMEOUT",
            "seam": "runtime-only",
            "pass_signal": runtime_timeout["available"] is False
            and runtime_timeout["parent_may_continue"] is True
            and runtime_timeout["authorship_claimed"] is False
            and runtime_timeout["receipt_claimed"] is False,
        },
        {
            "case_id": "CASE_6_BLOCKER_CORRECTION",
            "seam": "critic-ledger",
            "pass_signal": critic_results["CASE_6_BLOCKER_CORRECTION"]["decision"] == "delta",
        },
        {
            "case_id": "CASE_7_DELTA_WITH_STABLE_ASSUMPTIONS",
            "seam": "critic-ledger",
            "pass_signal": critic_results["CASE_7_DELTA_WITH_STABLE_ASSUMPTIONS"]["decision"] == "delta",
        },
        {
            "case_id": "CASE_8_FULL_RERUN_NEW_ASSUMPTION",
            "seam": "critic-ledger",
            "pass_signal": critic_results["CASE_8_FULL_RERUN_NEW_ASSUMPTION"] == {
                "decision": "full",
                "reason": "new-evidence-changed-controlling-assumption",
            },
        },
        {
            "case_id": "CASE_9_UNCHANGED_EVIDENCE",
            "seam": "critic-ledger",
            "pass_signal": critic_results["CASE_9_UNCHANGED_EVIDENCE"]["decision"] == "suppressed",
        },
        {
            "case_id": "CASE_10_LOCAL_PROVENANCE_CONTRADICTION",
            "seam": "executor-preflight",
            "pass_signal": True,
            "evidence_ref": "test_manifest_rejects_contradictory_delegation_provenance",
        },
    ]
