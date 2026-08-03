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
    DISCOVERY_CATEGORIES,
    Finding,
    build_compact_payload,
    classify_closeout,
    compute_sha256,
    parse_execution_contract,
    status_for_route,
    validate_completion,
    validate_plan,
    validate_resume,
    validate_status,
)


def _fixture(name: str) -> Path:
    return FIXTURES / name


def _stage_valid_plan(tmp_path: Path, text: str | None = None) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "valid-plan.md"
    plan.write_text(text or _fixture("valid-plan.md").read_text())
    return plan


def _contract(plan: Path):
    return parse_execution_contract(plan.read_text())


def _discovery() -> list[dict[str, object]]:
    return [
        {
            "category": category,
            "status": "not-found",
            "candidates": [],
            "evidence": f"No candidate found in {category}.",
        }
        for category in DISCOVERY_CATEGORIES
    ]


def _validation(
    plan: Path,
    validation_id: str,
    *,
    outcome: str = "exact-pass",
    candidate: dict[str, object] | None = None,
    authority_state: str = "not-required",
    equivalent_evidence: dict[str, bool] | None = None,
) -> dict[str, object]:
    declared = {item.id: item for item in _contract(plan).validations}[validation_id]
    value: dict[str, object] = {
        "id": declared.id,
        "command": declared.command,
        "required": declared.required,
        "outcome": outcome,
        "phase": declared.phases[-1],
        "equivalence": declared.equivalence,
    }
    if equivalent_evidence is not None:
        value["outcome"] = "equivalent-pass"
        value["equivalence_evidence"] = equivalent_evidence
    if outcome in {"unresolved", "regression"} or equivalent_evidence is not None:
        value.update(
            {
                "failure_phase": "validator-result",
                "discovery_results": _discovery(),
                "candidates": [candidate] if candidate else [],
                "authority": {
                    "state": authority_state,
                    "action": "dependency-installation"
                    if authority_state != "not-required"
                    else "read-only-discovery",
                },
            }
        )
    return value


def _closeout_evidence(
    plan: Path,
    *,
    validations: list[dict[str, object]] | None = None,
    outcome: str = "exact-pass",
    candidate: dict[str, object] | None = None,
    authority_state: str = "not-required",
    tasks_complete: bool = True,
    tasks_remaining: list[str] | None = None,
    pause_requested: bool = False,
    fatal_conditions: list[str] | None = None,
    exhaustion_evidence: list[str] | None = None,
    manual_obligations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    if validations is None:
        declared = list(_contract(plan).validations)
        validations = [
            _validation(
                plan,
                item.id,
                outcome=outcome,
                candidate=candidate if index == 0 else None,
                authority_state=authority_state,
            )
            for index, item in enumerate(declared)
        ]
    return {
        "plan_fingerprint": compute_sha256(plan),
        "tasks_complete": tasks_complete,
        "tasks_remaining": tasks_remaining or [],
        "pause_requested": pause_requested,
        "fatal_conditions": fatal_conditions or [],
        "validations": validations,
        "manual_obligations": manual_obligations or [],
        "exhaustion_evidence": exhaustion_evidence or [],
    }


def _minimal_status(plan: Path, status: str = "PARTIAL") -> str:
    reason = (
        "Recovery exhausted for an environmental validation."
        if status == "NEEDS_REVIEW"
        else "Classifier route is paused by the caller."
    )
    exhaustion = (
        "No safe candidate remains after complete discovery."
        if status in {"BLOCKED", "NEEDS_REVIEW"}
        else "None; execution remains resumable."
    )
    return (
        f"## Status\n\n`{status}`\n\n"
        f"## Plan\n\n`{plan}`\n\n"
        f"## Plan Fingerprint\n\n`{compute_sha256(plan)}`\n\n"
        "## Completed\n\n- Task 1\n\n"
        "## Remaining\n\n- Task 2\n\n"
        "## Validation\n\n- `python3 -m pytest -q tests/fixture/` — passed.\n\n"
        "## Next\n\nResume Task 2.\n\n"
        "## Closeout Decision\n\n- Route: " + reason + "\n\n"
        "## Recovery Attempts\n\n- None beyond recorded evidence.\n\n"
        "## Recovery Exhaustion\n\n- " + exhaustion + "\n"
    )


def test_valid_plan_parses_contract_and_has_no_findings(valid_plan: Path) -> None:
    assert parse_execution_contract(valid_plan.read_text()).schema_version == 1
    assert validate_plan(valid_plan, repo_root=valid_plan.parents[3]) == []


def test_plan_without_execution_contract_is_blocking(tmp_path: Path) -> None:
    plan = _stage_valid_plan(
        tmp_path,
        "# Plan\n\n## Goal\n\nStrict plan.\n\n"
        "## Repository Preflight\n\n- Baseline Validation: run check.\n"
        "- Recovery Policy: use bounded recovery.\n"
        "- Escalation Conditions: request authority.\n"
        "- User-Facing Report: report evidence.\n\n"
        "## Global Constraints\n\n- No Git mutation.\n\n"
        "## Task 1: Validate\n\n- [ ] Run validation.\n",
    )
    findings = validate_plan(plan, repo_root=tmp_path)
    assert "missing-execution-contract" in {item.code for item in findings}
    assert any(item.severity == "blocking" for item in findings)


def test_current_plan_requires_control_inventory(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text()
    start = text.index("## Control Inventory")
    end = text.index("\n## ", start + 1)
    plan = _stage_valid_plan(tmp_path, text[:start] + text[end + 1 :])
    assert "missing-control-inventory" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_current_plan_requires_explicit_no_git_constraint(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text().replace(
        "- No Git mutation.\n", "", 1
    )
    plan = _stage_valid_plan(tmp_path, text)
    assert "missing-no-git-constraint" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_explicit_legacy_or_imported_plan_remains_non_actionable(
    tmp_path: Path,
) -> None:
    plan = _stage_valid_plan(tmp_path, _fixture("legacy-draft-plan.md").read_text())
    assert any(item.severity == "blocking" for item in validate_plan(plan, tmp_path))


def test_legacy_plan_is_rejected(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path, _fixture("legacy-draft-plan.md").read_text())
    assert any(item.severity == "blocking" for item in validate_plan(plan, tmp_path))


def test_plan_rejects_duplicate_validation_ids(tmp_path: Path) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace('"id": "diff-check"', '"id": "focused-tests"')
    )
    plan = _stage_valid_plan(tmp_path, text)
    assert "duplicate-validation-id" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


@pytest.mark.parametrize(
    ("needle", "replacement", "message"),
    (
        ('"schema_version": 1', '"schema_version": 2', "schema_version"),
        (
            '"id": "focused-tests"',
            '"id": "focused-tests", "unknown": true',
            "unknown fields",
        ),
        (
            '"command": "python3 -m pytest -q tests/fixture/"',
            '"command": ""',
            "command",
        ),
        ('"phases": ["final"]', '"phases": ["other"]', "phases"),
        ('"equivalence": "exact-only"', '"equivalence": "never"', "equivalence"),
    ),
)
def test_execution_contract_rejects_invalid_fields(
    tmp_path: Path, needle: str, replacement: str, message: str
) -> None:
    plan = _stage_valid_plan(
        tmp_path, _fixture("valid-plan.md").read_text().replace(needle, replacement, 1)
    )
    assert any(message in item.message for item in validate_plan(plan, tmp_path))


def test_execution_contract_rejects_malformed_json_and_duplicate_blocks(
    tmp_path: Path,
) -> None:
    malformed = _stage_valid_plan(
        tmp_path,
        _fixture("valid-plan.md")
        .read_text()
        .replace('"schema_version": 1', '"schema_version":', 1),
    )
    assert "malformed-execution-contract" in {
        item.code for item in validate_plan(malformed, tmp_path)
    }
    duplicate = _stage_valid_plan(
        tmp_path / "duplicate",
        _fixture("valid-plan.md").read_text()
        + "\n## Execution Contract\n\n```json\n{}\n```\n",
    )
    assert "duplicate-execution-contract" in {
        item.code for item in validate_plan(duplicate, duplicate.parents[3])
    }


def test_closeout_is_done_when_all_required_obligations_pass_exactly(
    valid_plan: Path,
) -> None:
    decision = classify_closeout(_contract(valid_plan), _closeout_evidence(valid_plan))
    assert decision.route == "DONE"


def test_closeout_accepts_admissible_equivalent_validation(valid_plan: Path) -> None:
    evidence = _closeout_evidence(
        valid_plan,
        validations=[
            _validation(
                valid_plan,
                "focused-tests",
                equivalent_evidence={
                    "target_did_not_start": True,
                    "same_checks": True,
                    "same_inputs": True,
                    "runtime_not_material": True,
                },
            ),
            _validation(valid_plan, "diff-check"),
        ],
    )
    assert classify_closeout(_contract(valid_plan), evidence).route == "DONE"


def test_closeout_rejects_omitted_required_plan_validation(valid_plan: Path) -> None:
    with pytest.raises(ValueError, match="missing required validation"):
        classify_closeout(
            _contract(valid_plan), _closeout_evidence(valid_plan, validations=[])
        )


def test_closeout_rejects_changed_command_and_unknown_id(valid_plan: Path) -> None:
    changed = _closeout_evidence(valid_plan)
    changed["validations"][0]["command"] = "make unrelated"  # type: ignore[index]
    with pytest.raises(ValueError, match="command mismatch"):
        classify_closeout(_contract(valid_plan), changed)
    unknown = _closeout_evidence(valid_plan)
    unknown["validations"][0]["id"] = "unknown"  # type: ignore[index]
    with pytest.raises(ValueError, match="unknown validation id"):
        classify_closeout(_contract(valid_plan), unknown)


def test_closeout_continues_on_safe_untried_candidate(valid_plan: Path) -> None:
    candidate = {
        "name": "retry with compatible runtime",
        "source": "path-executable",
        "safe": True,
        "requires_authority": False,
        "attempted": False,
        "result": "not-run",
        "evidence_delta": "candidate has not been tried",
    }
    assert (
        classify_closeout(
            _contract(valid_plan),
            _closeout_evidence(valid_plan, outcome="unresolved", candidate=candidate),
        ).route
        == "continue-recovery"
    )


def test_closeout_requests_authority_before_terminal_status(valid_plan: Path) -> None:
    candidate = {
        "name": "install compatible runtime",
        "source": "path-executable",
        "safe": False,
        "requires_authority": True,
        "attempted": False,
        "result": "not-run",
        "evidence_delta": "compatible runtime is not installed",
    }
    assert (
        classify_closeout(
            _contract(valid_plan),
            _closeout_evidence(
                valid_plan,
                outcome="unresolved",
                candidate=candidate,
                authority_state="required-unrequested",
            ),
        ).route
        == "request-authority"
    )


def test_closeout_rejects_narrative_only_exhaustion(valid_plan: Path) -> None:
    evidence = _closeout_evidence(
        valid_plan,
        outcome="unresolved",
        exhaustion_evidence=["no compatible interpreter is available"],
    )
    evidence["validations"][0].pop("discovery_results")  # type: ignore[index]
    with pytest.raises(ValueError, match="structured recovery"):
        classify_closeout(_contract(valid_plan), evidence)


def test_closeout_blocks_fatal_task_local_regression(valid_plan: Path) -> None:
    evidence = _closeout_evidence(
        valid_plan, fatal_conditions=["task-local regression exhausted"]
    )
    assert classify_closeout(_contract(valid_plan), evidence).route == "BLOCKED"


def test_closeout_routes_incomplete_work_and_explicit_pause(valid_plan: Path) -> None:
    active = _closeout_evidence(
        valid_plan, tasks_complete=False, tasks_remaining=["Task 2"]
    )
    paused = _closeout_evidence(
        valid_plan,
        tasks_complete=False,
        tasks_remaining=["Task 2"],
        pause_requested=True,
    )
    assert (
        classify_closeout(_contract(valid_plan), active).route == "continue-execution"
    )
    assert classify_closeout(_contract(valid_plan), paused).route == "PARTIAL"


def test_closeout_requires_review_for_pending_manual_obligation(tmp_path: Path) -> None:
    plan = _stage_valid_plan(
        tmp_path,
        _fixture("valid-plan.md")
        .read_text()
        .replace(
            '"manual_obligations": []',
            '"manual_obligations": [{"id": "owner-check", "kind": "human", "required": true, "acceptance": "Owner confirms output."}]',
        ),
    )
    evidence = _closeout_evidence(
        plan,
        manual_obligations=[
            {"id": "owner-check", "satisfied": False, "evidence": "Awaiting owner."}
        ],
    )
    assert classify_closeout(_contract(plan), evidence).route == "NEEDS_REVIEW"


@pytest.mark.parametrize(
    "route", ("continue-execution", "continue-recovery", "request-authority")
)
def test_active_route_cannot_be_serialized_as_terminal_status(route: str) -> None:
    assert status_for_route(route) is None


def test_minimal_status_is_valid(tmp_path: Path, valid_plan: Path) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(_minimal_status(valid_plan))
    assert validate_status(status) == []


def test_needs_review_requires_bound_reason(tmp_path: Path, valid_plan: Path) -> None:
    status = tmp_path / "valid-plan.NEEDS_REVIEW.md"
    status.write_text(
        _minimal_status(valid_plan, "NEEDS_REVIEW").replace(
            "Recovery exhausted for an environmental validation.", "Pending work."
        )
    )
    assert "needs-review-without-bound-reason" in {
        item.code for item in validate_status(status)
    }


def test_status_rejects_unknown_state_and_missing_headings(
    invalid_status: Path,
) -> None:
    codes = {item.code for item in validate_status(invalid_status)}
    assert "unknown-status" in codes
    assert "missing-heading" in codes


def test_resume_rejects_plan_fingerprint_drift(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    valid_plan.write_text(valid_plan.read_text() + "\nChanged after approval.\n")
    assert "plan-fingerprint-drift" in {
        item.code for item in validate_resume(valid_plan, valid_partial_status)
    }


def test_resume_accepts_matching_status_binding(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    assert validate_resume(valid_plan, valid_partial_status) == []


def test_completion_requires_done_and_no_remaining(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    findings = validate_completion(valid_plan, valid_partial_status)
    assert "not-done" in {
        item.code for item in findings
    } or "plan-fingerprint-drift" in {item.code for item in findings}


def test_compact_output_is_bounded() -> None:
    assert (
        build_compact_payload([Finding("missing-heading", "detail", "blocking")])[
            "status"
        ]
        == "failed"
    )


def test_preflight_cli_valid_fixture(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "preflight",
            str(plan),
            "--repo-root",
            str(tmp_path),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_closeout_cli_binds_plan_and_evidence(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    evidence = tmp_path / "closeout.json"
    evidence.write_text(json.dumps(_closeout_evidence(plan)))
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "closeout-check",
            str(plan),
            str(evidence),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["route"] == "DONE"


def test_closeout_cli_rejects_fingerprint_mismatch(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    evidence = tmp_path / "closeout.json"
    payload = _closeout_evidence(plan)
    payload["plan_fingerprint"] = "sha256:wrong"
    evidence.write_text(json.dumps(payload))
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "closeout-check",
            str(plan),
            str(evidence),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "fingerprint" in result.stderr


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
    plan = _stage_valid_plan(tmp_path)
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(_fixture("valid-plan.PARTIAL.md").read_text())
    plan.write_text(plan.read_text() + "\nDrifted.\n")
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
    )
    assert result.returncode != 0
    assert "plan-fingerprint-drift" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }
