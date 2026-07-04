"""Tests for plan_execution.py status-file validation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EXECUTING_CLI = Path(
    ".github/skills/internal-gateway-execute-plans/scripts/plan_execution.py"
).resolve()


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(EXECUTING_CLI), *[str(a) for a in args]],
        capture_output=True,
        text=True,
    )


def write_plan(plan_folder: Path) -> None:
    plan_folder.mkdir(parents=True, exist_ok=True)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\nTest.\n"
        "## Risultato atteso\nTest.\n",
        encoding="utf-8",
    )
    (plan_folder / "02-execution.md").write_text(
        "# Execution\n\n"
        "Plan profile: compact\n\n"
        "Target: test\n"
        "Anti-scope: none\n"
        "Validation: pytest\n",
        encoding="utf-8",
    )


def write_status(plan_folder: Path, status: str = "DONE") -> Path:
    status_path = plan_folder / f"{plan_folder.name}.{status}.md"
    status_path.write_text(
        f"# {plan_folder.name} Status\n\n"
        "## Status\n\n"
        f"{status}\n\n"
        "## Reason\n\n"
        "Evidence supports this state.\n\n"
        "## Completed\n\n"
        "- Contract checked.\n\n"
        "## Remaining\n\n"
        "- None.\n\n"
        "## Validation\n\n"
        "- `pytest` passed.\n\n"
        "## Next\n\n"
        "- No action required.\n\n"
        "## Resume Notes\n\n"
        "- Re-run validation after new edits.\n",
        encoding="utf-8",
    )
    return status_path


def test_inspect_reports_plan_without_status(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)

    result = run_cli("inspect", plan_folder)

    assert result.returncode == 0
    assert "sample-plan" in result.stdout
    assert "status_file_present: False" in result.stdout


def test_status_check_accepts_done_status_file(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    write_status(plan_folder, "DONE")

    result = run_cli("status-check", plan_folder)

    assert result.returncode == 0
    assert "DONE" in result.stdout


def test_completion_check_is_status_check_compatibility_alias(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    write_status(plan_folder, "DONE")

    result = run_cli("completion-check", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ready"] is True
    assert payload["status"] == "DONE"


def test_status_check_rejects_missing_status_file(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)

    result = run_cli("status-check", plan_folder)

    assert result.returncode != 0
    assert "missing-status-file" in result.stdout


def test_status_check_rejects_legacy_plan_state_marker(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    (plan_folder / "DONE-plan-state.md").write_text(
        "Plan State\nState: DONE\nContinuation: none\n",
        encoding="utf-8",
    )

    result = run_cli("status-check", plan_folder)

    assert result.returncode != 0
    assert "legacy-plan-state-marker" in result.stdout


def test_status_check_rejects_invalid_status(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    (plan_folder / "sample-plan.CANCELLED.md").write_text(
        "# sample-plan Status\n\n"
        "## Status\n\n"
        "CANCELLED\n\n"
        "## Reason\n\n"
        "Cancelled.\n\n"
        "## Completed\n\n"
        "- None.\n\n"
        "## Remaining\n\n"
        "- All.\n\n"
        "## Validation\n\n"
        "- Not run.\n\n"
        "## Next\n\n"
        "- Author a new plan.\n\n"
        "## Resume Notes\n\n"
        "- Closed.\n",
        encoding="utf-8",
    )

    result = run_cli("status-check", plan_folder)

    assert result.returncode != 0
    assert "invalid-status-file-name" in result.stdout


def test_status_check_rejects_missing_heading(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    status_path = write_status(plan_folder, "NEEDS_REVIEW")
    status_path.write_text(
        status_path.read_text(encoding="utf-8").replace("## Resume Notes\n\n", ""),
        encoding="utf-8",
    )

    result = run_cli("status-check", plan_folder)

    assert result.returncode != 0
    assert "missing-required-heading" in result.stdout


def test_status_check_rejects_multiple_status_files(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    write_status(plan_folder, "PARTIAL")
    write_status(plan_folder, "BLOCKED")

    result = run_cli("status-check", plan_folder)

    assert result.returncode != 0
    assert "multiple-status-files" in result.stdout


def test_resume_reports_existing_status(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    write_status(plan_folder, "PARTIAL")

    result = run_cli("resume", plan_folder)

    assert result.returncode == 0
    assert "PARTIAL" in result.stdout


def test_checkpoint_reports_status_requirement(tmp_path: Path) -> None:
    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)

    result = run_cli("checkpoint", plan_folder)

    assert result.returncode == 0
    assert "status_file_required: True" in result.stdout


def test_copied_bundle_runs_independently(tmp_path: Path) -> None:
    bundle_copy = tmp_path / "internal-gateway-execute-plans"
    shutil.copytree(Path(".github/skills/internal-gateway-execute-plans"), bundle_copy)
    cli = bundle_copy / "scripts" / "plan_execution.py"

    plan_folder = tmp_path / "sample-plan"
    write_plan(plan_folder)
    write_status(plan_folder, "DONE")

    result = subprocess.run(
        [sys.executable, str(cli), "status-check", str(plan_folder)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "DONE" in result.stdout


def test_copied_bundle_no_cross_bundle_import() -> None:
    import ast

    executing_code = EXECUTING_CLI.read_text(encoding="utf-8")
    tree = ast.parse(executing_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if (
                    "internal-gateway-writing-plans" in alias.name
                    or "retained_plans" in alias.name
                ):
                    pytest.fail(f"Cross-bundle import found: {ast.dump(node)}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "internal-gateway-writing-plans" in module or "retained_plans" in module:
                pytest.fail(f"Cross-bundle import found: {ast.dump(node)}")
