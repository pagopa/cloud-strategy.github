import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-execute-plans"
SCRIPTS = BUNDLE / "scripts"
FIXTURES = BUNDLE / "fixtures"

sys.path.insert(0, str(SCRIPTS))

from plan_execution import (  # noqa: E402
    Finding,
    build_compact_payload,
    classify_closeout,
    compute_sha256,
    validate_plan,
    validate_resume,
    validate_status,
)


def _closeout_evidence(
    *,
    outcome: str = "exact-pass",
    equivalence: dict[str, bool] | None = None,
    tasks_complete: bool = True,
    tasks_remaining: list[str] | None = None,
    human_review_required: bool = False,
    fatal_conditions: list[str] | None = None,
    recovery_candidates: list[str] | None = None,
    required: bool = True,
    pause_requested: bool = False,
    exhaustion_evidence: list[str] | None = None,
) -> dict[str, object]:
    return {
        "tasks_complete": tasks_complete,
        "tasks_remaining": tasks_remaining or [],
        "human_review_required": human_review_required,
        "fatal_conditions": fatal_conditions or [],
        "pause_requested": pause_requested,
        "exhaustion_evidence": exhaustion_evidence or [],
        "validations": [
            {
                "name": "focused validation",
                "required": required,
                "outcome": outcome,
                "recovery_candidates": recovery_candidates or [],
                **({"equivalence": equivalence} if equivalence is not None else {}),
            }
        ],
    }


def test_closeout_is_done_when_all_required_obligations_pass_exactly() -> None:
    decision = classify_closeout(_closeout_evidence(outcome="exact-pass"))
    assert decision.route == "DONE"


def test_closeout_accepts_fully_admissible_equivalent_validation() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            outcome="equivalent-pass",
            equivalence={
                "target_did_not_start": True,
                "same_checks": True,
                "same_inputs": True,
                "runtime_not_material": True,
            },
        )
    )
    assert decision.route == "DONE"


def test_closeout_rejects_equivalence_when_runtime_is_material() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            outcome="equivalent-pass",
            equivalence={
                "target_did_not_start": True,
                "same_checks": True,
                "same_inputs": True,
                "runtime_not_material": False,
            },
        )
    )
    assert decision.route != "DONE"


def test_closeout_continues_incomplete_executable_work() -> None:
    decision = classify_closeout(
        _closeout_evidence(tasks_complete=False, tasks_remaining=["Task 2"])
    )
    assert decision.route == "continue-execution"


def test_closeout_continues_recovery_when_a_candidate_exists() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            outcome="unresolved",
            recovery_candidates=["rerun with supported interpreter"],
        )
    )
    assert decision.route == "continue-recovery"


def test_closeout_continues_python_313_token_risk_recovery() -> None:
    decision = classify_closeout(
        {
            **_closeout_evidence(
                outcome="unresolved",
                recovery_candidates=[
                    ".github/scripts/.venv/bin/python (Python 3.13)"
                ],
            ),
            "validations": [
                {
                    "name": "make token-risks",
                    "required": True,
                    "outcome": "unresolved",
                    "recovery_candidates": [
                        ".github/scripts/.venv/bin/python (Python 3.13)"
                    ],
                },
                {
                    "name": "make github-catalog-validation",
                    "required": True,
                    "outcome": "unresolved",
                    "recovery_candidates": [
                        ".github/scripts/.venv/bin/python (Python 3.13)"
                    ],
                },
            ],
        }
    )
    assert decision.route == "continue-recovery"
    assert "make token-risks" in decision.next_action
    assert "make github-catalog-validation" in decision.next_action
    assert ".github/scripts/.venv/bin/python (Python 3.13)" in decision.next_action


def test_closeout_blocks_exhausted_task_local_regression() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            outcome="regression",
            fatal_conditions=["task-local regression"],
            exhaustion_evidence=["safe retry candidates exhausted"],
        )
    )
    assert decision.route == "BLOCKED"


def test_closeout_blocks_unknown_fatal_condition() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            fatal_conditions=["unknown fatal condition"],
            exhaustion_evidence=["no safe autonomous action remains"],
        )
    )
    assert decision.route == "BLOCKED"


def test_closeout_requires_review_for_exhausted_human_decision() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            outcome="unresolved",
            human_review_required=True,
            exhaustion_evidence=["requires owner decision"],
        )
    )
    assert decision.route == "NEEDS_REVIEW"


def test_closeout_requires_review_for_exhausted_environmental_gap() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            outcome="unresolved",
            exhaustion_evidence=["no compatible interpreter is available"],
        )
    )
    assert decision.route == "NEEDS_REVIEW"


def test_closeout_allows_partial_only_for_an_explicit_pause() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            tasks_complete=False,
            tasks_remaining=["Task 2"],
            pause_requested=True,
        )
    )
    assert decision.route == "PARTIAL"


def test_closeout_never_uses_partial_for_an_active_run() -> None:
    decision = classify_closeout(
        _closeout_evidence(
            tasks_complete=False,
            tasks_remaining=["Task 2"],
            pause_requested=False,
        )
    )
    assert decision.route == "continue-execution"


def test_closeout_allows_non_required_warning() -> None:
    decision = classify_closeout(
        _closeout_evidence(outcome="warning", required=False)
    )
    assert decision.route == "DONE"


def test_closeout_cli_reports_continue_route_in_compact_output(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "closeout.json"
    evidence.write_text(
        json.dumps(
            _closeout_evidence(
                outcome="unresolved",
                recovery_candidates=["supported interpreter"],
            )
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "closeout-check",
            str(evidence),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["route"] == "continue-recovery"
    assert payload["reason_codes"]
    assert payload["next_action"]


def test_closeout_cli_rejects_unknown_outcome(tmp_path: Path) -> None:
    evidence = tmp_path / "closeout.json"
    evidence.write_text(json.dumps(_closeout_evidence(outcome="maybe-pass")))

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "closeout-check",
            str(evidence),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "outcome" in result.stderr


def test_closeout_cli_rejects_equivalent_pass_without_admissibility_evidence(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "closeout.json"
    evidence.write_text(json.dumps(_closeout_evidence(outcome="equivalent-pass")))

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "closeout-check",
            str(evidence),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "equivalence" in result.stderr


def _fixture(name: str) -> Path:
    return FIXTURES / name


def _stage_valid_plan(tmp_path: Path, text: str | None = None) -> Path:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "valid-plan.md"
    plan.write_text(text or _fixture("valid-plan.md").read_text())
    return plan


def _minimal_status(plan: Path, status: str = "PARTIAL") -> str:
    return (
        f"## Status\n\n`{status}`\n\n"
        f"## Plan\n\n`{plan}`\n\n"
        f"## Plan Fingerprint\n\n`{compute_sha256(plan)}`\n\n"
        "## Completed\n\n- Task 1\n\n"
        "## Remaining\n\n- Task 2\n\n"
        "## Validation\n\n- Focused tests passed.\n\n"
        "## Next\n\nResume Task 2.\n"
    )


def test_valid_plan_is_bound_to_its_sha256(valid_plan: Path) -> None:
    findings = validate_plan(valid_plan, repo_root=valid_plan.parents[3])
    assert findings == []
    assert compute_sha256(valid_plan).startswith("sha256:")


@pytest.mark.parametrize(
    "preflight_heading",
    ("Repository Preflight", "Preflight", "Preflight Gate"),
)
def test_plan_accepts_preflight_heading_alias(
    tmp_path: Path, preflight_heading: str
) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "preflight-alias.md"
    plan.write_text(
        "# Plan\n\n"
        "## Goal\n\n- Validate the plan.\n\n"
        f"## {preflight_heading}\n\n- Use the repository validator.\n\n"
        "- Baseline Validation: run `python3 validator.py` before edits.\n"
        "- Recovery Policy: repair only in-scope regressions.\n"
        "- Escalation Conditions: continue pre-existing failures; stop on unsafe or task-local regression.\n"
        "- User-Facing Report: report outcome, validation, recovery, and next action.\n\n"
        "## Global Constraints\n\n- Keep the plan unchanged.\n\n"
        "## Task 1: Validate\n\n- [ ] Run the check.\n"
    )

    assert validate_plan(plan, repo_root=tmp_path) == []


def test_plan_without_supported_preflight_heading_is_a_notice(tmp_path: Path) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace(
            "## Repository Preflight",
            "## Execution Setup",
        )
    )
    plan = _stage_valid_plan(tmp_path, text)

    findings = validate_plan(plan, repo_root=tmp_path)

    assert not [item for item in findings if item.severity == "blocking"]
    assert any(
        item.code == "missing-heading" and item.severity == "notice"
        for item in findings
    )


def test_legacy_draft_plan_metadata_is_non_blocking(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path, _fixture("legacy-draft-plan.md").read_text())

    findings = validate_plan(plan, repo_root=tmp_path)

    assert not [item for item in findings if item.severity == "blocking"]
    assert {item.code for item in findings} >= {
        "missing-heading",
        "missing-execution-field",
    }
    assert all(
        item.severity == "notice"
        for item in findings
        if item.code in {"missing-heading", "missing-execution-field"}
    )


def test_plan_without_actionable_task_is_blocking(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path, "# Notes\n\nNo executable work is defined.\n")

    findings = validate_plan(plan, repo_root=tmp_path)

    assert any(
        item.code == "missing-task" and item.severity == "blocking" for item in findings
    )


def test_plan_outside_retained_plan_directory_is_rejected(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan\n")
    findings = validate_plan(plan, repo_root=tmp_path)
    assert {item.code for item in findings} >= {"plan-outside-retained-directory"}


def test_minimal_status_is_valid(tmp_path: Path, valid_plan: Path) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(_minimal_status(valid_plan))

    assert validate_status(status) == []


def test_minimal_status_preserves_resume_binding(
    tmp_path: Path, valid_plan: Path
) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(
        _minimal_status(valid_plan).replace("valid-plan.md", "other-plan.md")
    )

    assert {item.code for item in validate_resume(valid_plan, status)} >= {
        "plan-binding-mismatch"
    }


def test_plan_without_execution_metadata_is_non_blocking(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "incomplete-plan.md"
    plan.write_text(
        "# Plan\n\n"
        "## Goal\n\n- Validate the plan.\n\n"
        "## Repository Preflight\n\n- Target: validator.\n\n"
        "## Global Constraints\n\n- Keep the plan unchanged.\n\n"
        "## Task 1: Validate\n\n- [ ] Run the check.\n"
    )

    findings = validate_plan(plan, repo_root=tmp_path)

    assert not [item for item in findings if item.severity == "blocking"]
    missing_fields = [
        item for item in findings if item.code == "missing-execution-field"
    ]
    assert missing_fields
    assert all(item.severity == "notice" for item in missing_fields)


def test_plan_ignores_execution_field_quality(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "weak-plan.md"
    text = _fixture("valid-plan.md").read_text()
    text = text.replace(
        "- **Recovery Policy:** repair only task-local validation failures in scope.",
        "- **Recovery Policy:** TBD.",
    )
    text = text.replace(
        "- **Escalation Conditions:** stop on unsafe continuation or unresolved task-local regression.",
        "- **Escalation Conditions:** stop on failure.",
    )
    plan.write_text(text)

    findings = validate_plan(plan, repo_root=tmp_path)

    assert not [item for item in findings if item.severity == "blocking"]
    assert "invalid-execution-field" not in {item.code for item in findings}


def test_plan_accepts_semantically_complete_user_facing_report(
    tmp_path: Path,
) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace(
            "summarize outcome, changes, validation, recovery, gaps, and next action.",
            "summarize the result, checks performed, remediation attempts, and follow-up.",
        )
    )
    plan = _stage_valid_plan(tmp_path, text)

    assert validate_plan(plan, repo_root=tmp_path) == []


def test_plan_ignores_user_facing_report_quality(tmp_path: Path) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace(
            "summarize outcome, changes, validation, recovery, gaps, and next action.",
            "summarize outcome, validation, and recovery.",
        )
    )
    plan = _stage_valid_plan(tmp_path, text)

    findings = validate_plan(plan, repo_root=tmp_path)

    assert not [item for item in findings if item.severity == "blocking"]
    assert "invalid-execution-field" not in {item.code for item in findings}


def test_plan_accepts_empty_execution_field(tmp_path: Path) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace(
            "- **Recovery Policy:** repair only task-local validation failures in scope.",
            "- **Recovery Policy:**",
        )
    )
    plan = _stage_valid_plan(tmp_path, text)

    findings = validate_plan(plan, repo_root=tmp_path)

    assert not [item for item in findings if item.severity == "blocking"]
    assert "invalid-execution-field" not in {item.code for item in findings}


def test_status_rejects_unknown_state_and_missing_headings(
    invalid_status: Path,
) -> None:
    findings = validate_status(invalid_status)
    codes = {item.code for item in findings}
    assert "unknown-status" in codes
    assert "missing-heading" in codes


def test_status_accepts_missing_optional_evidence(tmp_path: Path) -> None:
    status = tmp_path / "plan.PARTIAL.md"
    status.write_text(
        "\n\n".join(
            f"## {heading}\n\nvalue"
            for heading in (
                "Status",
                "Plan",
                "Plan Fingerprint",
                "Reason",
                "Workspace Baseline",
                "Files Changed",
                "Completed",
                "Remaining",
                "Validation",
                "Next",
                "Resume Notes",
            )
        )
    )

    findings = validate_status(status)

    assert findings == []


def test_status_rejects_unclassified_failure_evidence(
    tmp_path: Path, valid_plan: Path
) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(
        _minimal_status(valid_plan) + "\n## Failure Classification\n\nTBD\n"
    )

    findings = validate_status(status)

    assert {item.code for item in findings} >= {"invalid-failure-classification"}


@pytest.mark.parametrize(
    ("heading", "code"),
    (
        ("Closeout Decision", "invalid-closeout-decision"),
        ("Recovery Exhaustion", "invalid-recovery-exhaustion"),
    ),
)
def test_status_rejects_unresolved_closeout_evidence(
    tmp_path: Path,
    valid_plan: Path,
    heading: str,
    code: str,
) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(_minimal_status(valid_plan) + f"\n## {heading}\n\nTBD\n")

    findings = validate_status(status)

    assert code in {item.code for item in findings}


def test_status_rejects_noncomparable_baseline_and_final_commands(
    tmp_path: Path, valid_plan: Path
) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(
        _minimal_status(valid_plan).replace(
            "## Validation\n\n- Focused tests passed.",
            "## Baseline Validation\n\n- `pytest -q tests/fixture/` — passed\n\n"
            "## Validation\n\n- `make unrelated-check` — passed",
        )
    )

    findings = validate_status(status)

    assert {item.code for item in findings} >= {"validation-delta-mismatch"}


def test_needs_review_accepts_environmental_external_gap(
    tmp_path: Path, valid_plan: Path
) -> None:
    status = tmp_path / "valid-plan.NEEDS_REVIEW.md"
    text = _minimal_status(valid_plan, "NEEDS_REVIEW")
    text += "\n## Failure Classification\n\nEnvironmental: validation service unavailable.\n"
    status.write_text(text)

    findings = validate_status(status)

    assert "needs-review-classification" not in {item.code for item in findings}


def test_resume_rejects_plan_fingerprint_drift(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    valid_plan.write_text(valid_plan.read_text() + "\nChanged after approval.\n")
    findings = validate_resume(valid_plan, valid_partial_status)
    assert {item.code for item in findings} >= {"plan-fingerprint-drift"}


def test_resume_accepts_matching_status_binding(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    assert validate_resume(valid_plan, valid_partial_status) == []


def test_resume_rejects_status_bound_to_different_plan(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    valid_partial_status.write_text(
        valid_partial_status.read_text().replace("valid-plan.md", "other-plan.md")
    )

    findings = validate_resume(valid_plan, valid_partial_status)

    assert {item.code for item in findings} >= {"plan-binding-mismatch"}


def test_compact_output_is_bounded() -> None:
    payload = build_compact_payload([Finding("missing-heading", "detail", "blocking")])
    assert payload == {
        "status": "failed",
        "finding_counts": {"total": 1, "blocking": 1, "notice": 0},
        "finding_sample": [{"code": "missing-heading", "severity": "blocking"}],
        "next_action": "Resolve blocking plan execution findings.",
    }


def test_preflight_cli_valid_fixture(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "valid-plan.md"
    plan.write_text(_fixture("valid-plan.md").read_text())
    repo_root = tmp_path
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "preflight",
            str(plan),
            "--repo-root",
            str(repo_root),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_preflight_cli_rejects_plan_outside_directory() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "preflight",
            str(_fixture("valid-plan.md")),
            "--repo-root",
            str(REPO_ROOT),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"


def test_preflight_json_reports_missing_current_fields_as_notices(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "incomplete-plan.md"
    plan.write_text(
        "# Plan\n\n"
        "## Goal\n\n- Execute an approved plan.\n\n"
        "## Repository Preflight\n\n- Target: current task.\n\n"
        "## Global Constraints\n\n- Preserve the fingerprint.\n\n"
        "## Task 1: Validate\n\n- [ ] Run the check.\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "preflight",
            str(plan),
            "--repo-root",
            str(tmp_path),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["findings"]
    assert all(item["severity"] == "notice" for item in payload["findings"])


def test_status_check_cli_invalid() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "status-check",
            str(_fixture("invalid-status.md")),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    codes = {f["code"] for f in payload["finding_sample"]}
    assert "unknown-status" in codes


def test_status_check_cli_valid() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "status-check",
            str(_fixture("valid-plan.PARTIAL.md")),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_resume_check_cli_detects_drift(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "valid-plan.md"
    plan.write_text(_fixture("valid-plan.md").read_text() + "\nDrifted.\n")
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(_fixture("valid-plan.PARTIAL.md").read_text())
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "resume-check",
            str(plan),
            str(status),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    codes = {f["code"] for f in payload["finding_sample"]}
    assert "plan-fingerprint-drift" in codes
