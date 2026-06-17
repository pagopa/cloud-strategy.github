"""Tests for plan_execution.py — bundle-local CLI for retained-plan execution."""

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


def _write_profile_ledger(plan_folder: Path, profile: str = "compact") -> None:
    if profile == "compact":
        (plan_folder / "02-execution.md").write_text(
            "# Execution\n\n"
            "## Plan profile\ncompact\n\n"
            "## Target and anti-scope\n### Target\nTarget.\n### Anti-scope\nNone.\n\n"
            "## Owner and validator\nOwner.\n\n"
            "## Stop conditions\nNone.\n\n"
            "## Objective\nTest.\n\n"
            "## Chosen logic\nTest.\n\n"
            "## Key assumptions\nNone.\n\n"
            "## Executable steps\n"
            "1. Do it.\n"
            "   Target: file\n"
            "   Acceptance: done\n"
            "   Validation: pytest\n"
            "   Fallback: stop\n\n"
            "## Validation\nTest.\n\n"
            "## Source item coverage\n"
            "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| X-01 | Test | diff | diff | pytest | DONE | `none` |\n",
            encoding="utf-8",
        )
        return

    (plan_folder / "02-control.md").write_text(
        "# Control\n\n"
        "## Recommended use\napply-plan\n\n"
        "## Plan profile\nextended\n\n"
        "## File map and role\n| File | Role |\n| --- | --- |\n| `03-execution.md` | execution |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Initial evidence pass\n1. quick pass\n\n"
        "## Reading budget\n- compact\n\n"
        "## Target and anti-scope\n### Target\nTarget.\n### Anti-scope\nNone.\n\n"
        "## Owner and validator\nOwner.\n\n"
        "## Stop conditions\nNone.\n\n"
        "## Sources\n- source\n\n"
        "## Candidate targets\n- target\n\n"
        "## Validation commands\nRun in this order:\n1. pytest\n\n"
        "## Blockers and fallback rules\n- none\n\n"
        "## External pins\nno external evidence\n\n"
        "## Source item ledger\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| X-01 | Test | diff | diff | pytest | DONE | `03-execution.md` |\n",
        encoding="utf-8",
    )


def _write_compact_plan(plan_folder: Path) -> None:
    plan_folder.mkdir(parents=True, exist_ok=True)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\nTest.\n"
        "## Risultato atteso\nTest.\n"
        "## Risorse coinvolte\n| Risorsa | Azione | Scopo |\n| X | Y | Z |\n"
        "## Comportamento scelto\nTest.\n"
        "## Validazione prevista\nTest.\n"
        "## Decisione richiesta\nApprove.\n",
        encoding="utf-8",
    )
    _write_profile_ledger(plan_folder, profile="compact")


def _write_completed_plan(plan_folder: Path) -> None:
    plan_folder.mkdir(parents=True, exist_ok=True)
    (plan_folder / "done-01-sample.md").write_text("# Done\n", encoding="utf-8")
    (plan_folder / "evidence-envelope.md").write_text(
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01-sample.md` | DONE | `pytest` |\n"
        "| RPV-01 | DONE | `pytest` |\n",
        encoding="utf-8",
    )
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\n"
        "Plan profile: compact\n"
        "Active phase and owner: execute\n"
        "State: DONE\n"
        "Continuation: none\n"
        "User action required: none\n"
        "Files changed: test\n"
        "Completed items: all\n"
        "Intentional non-actions: none\n"
        "Validators: pytest\n"
        "Evidence envelope: evidence-envelope.md\n"
        "Source-item ledger: all closed\n"
        "Evidence gaps: none\n"
        "Residual risks: none\n"
        "Next-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )


def _write_lightweight_plan_state(
    plan_folder: Path, state: str = "DONE", continuation: str = "none"
) -> None:
    marker_name = f"{state}-plan-state.md"
    (plan_folder / marker_name).write_text(
        f"Plan State\nState: {state}\nContinuation: {continuation}\n",
        encoding="utf-8",
    )


# inspect


def test_inspect_compact_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("inspect", plan_folder)

    assert result.returncode == 0
    assert "compact" in result.stdout
    assert "02-execution.md" in result.stdout or "02" in result.stdout


def test_inspect_compact_json(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("inspect", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["profile"] == "compact"


def test_inspect_unsupported_rejected(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    result = run_cli("inspect", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


def test_inspect_missing_folder(tmp_path: Path) -> None:
    result = run_cli("inspect", tmp_path / "nonexistent")
    assert result.returncode != 0
    assert "Not a directory" in result.stderr


# resume


def test_resume_active_plan(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("resume", plan_folder)

    assert result.returncode == 0
    assert "resumable" in result.stdout.lower()


def test_resume_live_folder_state(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\nState: PARTIAL\nContinuation: continuing\n",
        encoding="utf-8",
    )
    result = run_cli("resume", plan_folder)
    assert result.returncode == 0
    assert "PARTIAL" in result.stdout


def test_resume_unsupported_rejected(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    result = run_cli("resume", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


# checkpoint


def test_checkpoint_active_plan(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("checkpoint", plan_folder)

    assert result.returncode == 0
    assert "can_checkpoint" in result.stdout.lower()


def test_checkpoint_unsupported_rejected(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    result = run_cli("checkpoint", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


# completion-check


def test_completion_check_shipped_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_completed_plan(plan_folder)
    result = run_cli("completion-check", plan_folder)

    assert result.returncode == 0


def test_completion_check_lightweight_shipped_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    _write_lightweight_plan_state(plan_folder)

    result = run_cli("completion-check", plan_folder)

    assert result.returncode == 0


def test_completion_check_shipped_json(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_completed_plan(plan_folder)
    result = run_cli("completion-check", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ready"] is True


def test_completion_check_lightweight_json(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    _write_lightweight_plan_state(plan_folder)

    result = run_cli("completion-check", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ready"] is True


def test_completion_rejects_active_numbered_files(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_completed_plan(plan_folder)
    # Add a profile file so the profile gate passes
    (plan_folder / "02-execution.md").write_text(
        "## Plan profile\ncompact\n",
        encoding="utf-8",
    )
    (plan_folder / "03-still-active.md").write_text("# Active\n", encoding="utf-8")
    result = run_cli("completion-check", plan_folder)

    assert result.returncode != 0
    assert "active-numbered-files" in result.stdout


def test_completion_rejects_open_statuses(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "done-01.md").write_text("# Done\n", encoding="utf-8")
    (plan_folder / "evidence-envelope.md").write_text(
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01.md` | PENDING | `pytest` |\n",
        encoding="utf-8",
    )
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\nPlan profile: compact\nState: DONE\n"
        "Continuation: none\nUser action required: none\nFiles changed: test\n"
        "Completed items: all\nIntentional non-actions: none\nValidators: pytest\n"
        "Evidence envelope: evidence-envelope.md\nSource-item ledger: all closed\n"
        "Evidence gaps: none\nResidual risks: none\nNext-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "open-status" in result.stdout


def test_completion_lightweight_rejects_not_shipped_state(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    _write_lightweight_plan_state(
        plan_folder, state="PARTIAL", continuation="continuing"
    )

    result = run_cli("completion-check", plan_folder)

    assert result.returncode != 0
    assert "not-done-state" in result.stdout


def test_completion_lightweight_rejects_nonterminal_continuation(
    tmp_path: Path,
) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    _write_lightweight_plan_state(plan_folder, continuation="waiting")

    result = run_cli("completion-check", plan_folder)

    assert result.returncode != 0
    assert "nonterminal-continuation" in result.stdout


def test_completion_lightweight_rejects_filename_state_mismatch(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "DONE-plan-state.md").write_text(
        "Plan State\nState: PARTIAL\nContinuation: none\n",
        encoding="utf-8",
    )

    result = run_cli("completion-check", plan_folder)

    assert result.returncode != 0
    assert "not-done-state" in result.stdout
    assert "plan-state-name-mismatch" in result.stdout


def test_completion_rejects_not_shipped_state(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_completed_plan(plan_folder)
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\nPlan profile: compact\nState: PARTIAL\n"
        "Continuation: waiting\nUser action required: approve\nFiles changed: test\n"
        "Completed items: some\nIntentional non-actions: none\nValidators: pytest\n"
        "Evidence envelope: evidence-envelope.md\nSource-item ledger: open\n"
        "Evidence gaps: missing\nResidual risks: high\nNext-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "not-done-state" in result.stdout


def test_completion_missing_envelope(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\nPlan profile: compact\nState: DONE\n"
        "Continuation: none\nUser action required: none\nFiles changed: test\n"
        "Completed items: all\nIntentional non-actions: none\nValidators: pytest\n"
        "Evidence envelope: evidence-envelope.md\nSource-item ledger: all closed\n"
        "Evidence gaps: none\nResidual risks: none\nNext-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "missing-evidence-envelope" in result.stdout


def test_completion_missing_done_reference(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "done-01.md").write_text("# Done\n", encoding="utf-8")
    (plan_folder / "done-02.md").write_text("# Done\n", encoding="utf-8")
    (plan_folder / "evidence-envelope.md").write_text(
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01.md` | DONE | `pytest` |\n",
        encoding="utf-8",
    )
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\nPlan profile: compact\nState: DONE\n"
        "Continuation: none\nUser action required: none\nFiles changed: test\n"
        "Completed items: all\nIntentional non-actions: none\nValidators: pytest\n"
        "Evidence envelope: evidence-envelope.md\nSource-item ledger: all closed\n"
        "Evidence gaps: none\nResidual risks: none\nNext-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "missing-done-reference" in result.stdout


def test_completion_cancelled_not_equivalent_to_done(tmp_path: Path) -> None:
    """CANCELLED is not a DONE substitute."""
    plan_folder = tmp_path / "plan"
    _write_completed_plan(plan_folder)
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\nPlan profile: compact\nState: CANCELLED\n"
        "Continuation: none\nUser action required: none\nFiles changed: test\n"
        "Completed items: none\nIntentional non-actions: cancelled\nValidators: none\n"
        "Evidence envelope: evidence-envelope.md\nSource-item ledger: open\n"
        "Evidence gaps: all\nResidual risks: high\nNext-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "not-done-state" in result.stdout


def test_completion_unsupported_rejected(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "03-still-active.md").write_text("# Active\n", encoding="utf-8")
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


def test_completion_rejects_missing_profile_when_packaged(tmp_path: Path) -> None:
    """completion-check enforces the profile gate even with no active numbered files."""
    plan_folder = tmp_path / "plan"
    _write_completed_plan(plan_folder)
    (plan_folder / "completion-report.md").write_text(
        "Completion Report\n"
        "Active phase and owner: execute\n"
        "State: DONE\n"
        "Continuation: none\n"
        "User action required: none\n"
        "Files changed: test\n"
        "Completed items: all\n"
        "Intentional non-actions: none\n"
        "Validators: pytest\n"
        "Evidence envelope: evidence-envelope.md\n"
        "Source-item ledger: all closed\n"
        "Evidence gaps: none\n"
        "Residual risks: none\n"
        "Next-step package: none\n"
        "Follow-up suggestions: none\n",
        encoding="utf-8",
    )
    result = run_cli("completion-check", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


# Isolated copy test


def test_copied_bundle_runs_independently(tmp_path: Path) -> None:
    """A copied skill bundle runs its CLI with ambient Python stdlib only."""
    bundle_copy = tmp_path / "internal-gateway-execute-plans"
    shutil.copytree(Path(".github/skills/internal-gateway-execute-plans"), bundle_copy)
    cli = bundle_copy / "scripts" / "plan_execution.py"

    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)

    result = subprocess.run(
        [sys.executable, str(cli), "inspect", str(plan_folder)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "compact" in result.stdout


def test_copied_bundle_no_cross_bundle_import(tmp_path: Path) -> None:
    """Verify no import of sibling bundle or .github/scripts/lib."""
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
