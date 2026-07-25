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

from plan_execution import (
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


def test_plan_outside_retained_plan_directory_is_rejected(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan\n")
    findings = validate_plan(plan, repo_root=tmp_path)
    assert {item.code for item in findings} >= {"plan-outside-retained-directory"}


def test_status_rejects_unknown_state_and_missing_headings(
    invalid_status: Path,
) -> None:
    findings = validate_status(invalid_status)
    codes = {item.code for item in findings}
    assert "unknown-status" in codes
    assert "missing-heading" in codes


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
