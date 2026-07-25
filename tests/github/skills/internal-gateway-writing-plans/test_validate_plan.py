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


def test_invalid_fixture_reports_every_objective_rule() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_copy = Path(tmpdir) / "invalid-name.md"
        shutil.copy(INVALID, invalid_copy)
        codes = {finding["code"] for finding in _module().validate_plan(invalid_copy)}
        assert codes == {
            "filename",
            "preflight",
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
