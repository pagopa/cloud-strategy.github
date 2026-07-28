import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-writing-plans"
SCRIPT = BUNDLE / "scripts/validate_plan.py"
VALID = BUNDLE / "fixtures/2026-07-25-1829-valid-plan.md"
INVALID = BUNDLE / "fixtures/2026-07-25-1829-invalid-plan.md"


def _module():
    spec = importlib.util.spec_from_file_location("validate_plan", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_valid_fixture_has_no_objective_findings() -> None:
    assert _module().validate_plan(VALID) == []


def test_plan_requires_delegated_header_sections(tmp_path: Path) -> None:
    plan = tmp_path / "2026-07-27-2000-missing-header.md"
    text = VALID.read_text().replace(
        "## Goal\n\nValidate the plan execution CLI against a realistic plan shape.\n\n"
        "## Global Constraints\n\n- Preserve fixture integrity.\n\n",
        "",
        1,
    )
    plan.write_text(text)

    codes = {finding["code"] for finding in _module().validate_plan(plan)}

    assert "preflight" in codes


def test_invalid_fixture_reports_every_objective_rule() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_copy = Path(tmpdir) / "invalid-name.md"
        shutil.copy(INVALID, invalid_copy)
        codes = {finding["code"] for finding in _module().validate_plan(invalid_copy)}
        assert codes == {
            "filename",
            "preflight",
            "execution_recovery",
            "ordered_tasks",
            "file_targets",
            "validation",
            "git_mutation",
            "execution_owner",
        }


def test_cli_is_quiet_on_success_and_bounded_on_failure() -> None:
    passed = subprocess.run(
        [sys.executable, str(SCRIPT), str(VALID)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    failed = subprocess.run(
        [sys.executable, str(SCRIPT), str(INVALID)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert passed.returncode == 0
    assert "PASS" in passed.stdout
    assert failed.returncode == 1
    assert failed.stdout.count("\n") <= 10


def test_accepted_writer_fixture_passes_executor_preflight(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    staged_plan = retained / VALID.name
    shutil.copy(VALID, staged_plan)

    result = subprocess.run(
        [
            sys.executable,
            str(
                REPO_ROOT
                / ".github/skills/internal-gateway-execute-plans/scripts/plan_execution.py"
            ),
            "preflight",
            str(staged_plan),
            "--repo-root",
            str(tmp_path),
            "--format",
            "compact",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_recovery_fields_require_actionable_content(tmp_path: Path) -> None:
    plan = tmp_path / "2026-07-27-2000-weak-recovery.md"
    text = VALID.read_text()
    text = text.replace(
        "- Recovery policy: fix only failures caused by the planned changes",
        "- Recovery policy: TBD",
    )
    text = text.replace(
        "- Escalation conditions: stop on unsafe continuation or unresolved task-local regression",
        "- Escalation conditions: stop on failure",
    )
    plan.write_text(text)

    codes = {finding["code"] for finding in _module().validate_plan(plan)}

    assert "execution_recovery" in codes
