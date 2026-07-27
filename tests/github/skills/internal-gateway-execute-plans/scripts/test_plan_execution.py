import json
import subprocess
import sys
from pathlib import Path

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
    compute_sha256,
    validate_plan,
    validate_resume,
    validate_status,
)


def _fixture(name: str) -> Path:
    return FIXTURES / name


def test_valid_plan_is_bound_to_its_sha256(valid_plan: Path) -> None:
    findings = validate_plan(valid_plan, repo_root=valid_plan.parents[3])
    assert findings == []
    assert compute_sha256(valid_plan).startswith("sha256:")


def test_plan_accepts_preflight_heading_alias(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "preflight-alias.md"
    plan.write_text(
        "# Plan\n\n"
        "## Goal\n\n- Validate the plan.\n\n"
        "## Preflight\n\n- Use the repository validator.\n\n"
        "- Baseline Validation: run `python3 validator.py` before edits.\n"
        "- Recovery Policy: repair only in-scope regressions.\n"
        "- Escalation Conditions: continue pre-existing failures; stop on unsafe or task-local regression.\n"
        "- User-Facing Report: report outcome, validation, recovery, and next action.\n\n"
        "## Global Constraints\n\n- Keep the plan unchanged.\n\n"
        "## Task 1: Validate\n\n- [ ] Run the check.\n"
    )

    assert validate_plan(plan, repo_root=tmp_path) == []


def test_plan_outside_retained_plan_directory_is_rejected(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan\n")
    findings = validate_plan(plan, repo_root=tmp_path)
    assert {item.code for item in findings} >= {"plan-outside-retained-directory"}


def test_plan_without_recovery_contract_is_blocking(tmp_path: Path) -> None:
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

    messages = {item.message for item in findings}
    missing_fields = [
        item for item in findings if item.code == "missing-execution-field"
    ]
    assert missing_fields
    assert all(item.severity == "blocking" for item in missing_fields)
    assert messages >= {
        "Plan missing required execution field: Baseline Validation",
        "Plan missing required execution field: Recovery Policy",
        "Plan missing required execution field: Escalation Conditions",
        "Plan missing required execution field: User-Facing Report",
    }


def test_plan_rejects_weak_execution_recovery_fields(tmp_path: Path) -> None:
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

    assert {item.code for item in findings} >= {"invalid-execution-field"}


def test_status_rejects_unknown_state_and_missing_headings(
    invalid_status: Path,
) -> None:
    findings = validate_status(invalid_status)
    codes = {item.code for item in findings}
    assert "unknown-status" in codes
    assert "missing-heading" in codes


def test_status_requires_baseline_delta_and_recovery_evidence(tmp_path: Path) -> None:
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

    messages = {item.message for item in findings}
    assert messages >= {
        "Status missing required heading: Baseline Validation",
        "Status missing required heading: Recovery Attempts",
        "Status missing required heading: Failure Classification",
    }


def test_status_rejects_unclassified_failure_evidence(tmp_path: Path) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(
        _fixture("valid-plan.PARTIAL.md")
        .read_text()
        .replace("None; validation passed.", "TBD")
    )

    findings = validate_status(status)

    assert {item.code for item in findings} >= {"invalid-failure-classification"}


def test_status_rejects_noncomparable_baseline_and_final_commands(
    tmp_path: Path,
) -> None:
    status = tmp_path / "valid-plan.PARTIAL.md"
    status.write_text(
        _fixture("valid-plan.PARTIAL.md")
        .read_text()
        .replace(
            "`pytest -q tests/fixture/` — passed\n\n## Recovery Attempts",
            "`make unrelated-check` — passed\n\n## Recovery Attempts",
        )
    )

    findings = validate_status(status)

    assert {item.code for item in findings} >= {"validation-delta-mismatch"}


def test_needs_review_accepts_environmental_external_gap(tmp_path: Path) -> None:
    status = tmp_path / "valid-plan.NEEDS_REVIEW.md"
    text = _fixture("valid-plan.PARTIAL.md").read_text()
    text = text.replace("`PARTIAL`", "`NEEDS_REVIEW`")
    text = text.replace(
        "- Task 2: Integration test",
        "None.",
    )
    text = text.replace(
        "None; validation passed.",
        "Environmental: validation service unavailable.",
    )
    status.write_text(text)

    findings = validate_status(status)

    assert "needs-review-classification" not in {
        item.code for item in findings
    }


def test_resume_rejects_plan_fingerprint_drift(
    valid_plan: Path, valid_partial_status: Path
) -> None:
    valid_plan.write_text(valid_plan.read_text() + "\nChanged after approval.\n")
    findings = validate_resume(valid_plan, valid_partial_status)
    assert {item.code for item in findings} >= {"plan-fingerprint-drift"}


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


def test_preflight_json_rejects_missing_current_fields(tmp_path: Path) -> None:
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
    assert result.returncode != 0
    assert payload["status"] == "failed"
    assert all(item["severity"] == "blocking" for item in payload["findings"])


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
