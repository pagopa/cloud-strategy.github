"""Tests for plan_authoring.py — bundle-local CLI for retained-plan authoring."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

AUTHORING_CLI = Path(".github/skills/internal-writing-plans/scripts/plan_authoring.py").resolve()


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUTHORING_CLI), *[str(a) for a in args]],
        capture_output=True,
        text=True,
    )


# init


def test_init_creates_compact_scaffold(tmp_path: Path) -> None:
    plan_folder = tmp_path / "my-plan"
    result = run_cli("init", plan_folder)

    assert result.returncode == 0
    assert (plan_folder / "01-change-summary.md").is_file()
    assert (plan_folder / "02-source-item-ledger.md").is_file()
    assert (plan_folder / "03-execution.md").is_file()
    assert (plan_folder / "questions.md").is_file()

    summary = (plan_folder / "01-change-summary.md").read_text(encoding="utf-8")
    assert "Problema da risolvere" in summary
    assert "Risorse coinvolte" in summary
    assert "| Risorsa | Azione | Scopo |" in summary
    assert "Decisione richiesta" in summary

    ledger = (plan_folder / "02-source-item-ledger.md").read_text(encoding="utf-8")
    assert "Plan profile" in ledger
    assert "compact" in ledger
    assert "Source item ledger" in ledger


def test_init_rejects_existing_folder(tmp_path: Path) -> None:
    plan_folder = tmp_path / "exists"
    plan_folder.mkdir()
    result = run_cli("init", plan_folder)
    assert result.returncode != 0
    assert "already exists" in result.stderr


# audit


def _write_compact_plan(plan_folder: Path) -> None:
    plan_folder.mkdir(parents=True, exist_ok=True)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\nTest.\n"
        "## Risultato atteso\nTest.\n"
        "## Risorse coinvolte\n| Risorsa | Azione | Scopo |\n| --- | --- | --- |\n| X | Y | Z |\n"
        "## Comportamento scelto\nTest.\n"
        "## Validazione prevista\nTest.\n"
        "## Decisione richiesta\nApprove.\n",
        encoding="utf-8",
    )
    (plan_folder / "02-source-item-ledger.md").write_text(
        "# Ledger\n\n"
        "## Recommended use\napply-plan\n\n"
        "## Plan profile\ncompact\n\n"
        "## File map and role\n| File | Role |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Target and anti-scope\nTarget.\n\n"
        "## Owner and validator\nOwner.\n\n"
        "## Stop conditions\nNone.\n\n"
        "## Source item ledger\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| X-01 | Test | diff | diff | pytest | PENDING | 03 |\n",
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text(
        "# Execution\n\n## Objective\nTest.\n\n## Chosen logic\nTest.\n\n"
        "## Key assumptions\nNone.\n\n## Executable steps\n1. Do it.\n\n## Validation\nTest.\n",
        encoding="utf-8",
    )
    (plan_folder / "questions.md").write_text("# Questions\n\n- none\n", encoding="utf-8")


def _write_extended_plan(plan_folder: Path) -> None:
    _write_compact_plan(plan_folder)
    (plan_folder / "02-source-item-ledger.md").write_text(
        "# Ledger\n\n"
        "## Recommended use\napply-plan\n\n"
        "## Plan profile\nextended\n\n"
        "## File map and role\n| File | Role |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Target and anti-scope\nTarget.\n\n"
        "## Owner and validator\nOwner.\n\n"
        "## Stop conditions\nNone.\n\n"
        "## Source item ledger\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| X-01 | Test | diff | diff | pytest | PENDING | 03 |\n",
        encoding="utf-8",
    )
    (plan_folder / "04-implementation-contract.md").write_text(
        "# Implementation Contract\n\n## Purpose\nTest.\n", encoding="utf-8"
    )


def test_audit_compact_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("audit", plan_folder)

    assert result.returncode == 0


def test_audit_compact_json(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("audit", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ready"] is True


def test_audit_missing_required_file(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "02-source-item-ledger.md").write_text(
        "## Plan profile\ncompact\n", encoding="utf-8"
    )
    result = run_cli("audit", plan_folder)
    assert result.returncode != 0
    assert "missing-required-files" in result.stdout


def test_audit_missing_ledger_fields(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "01-change-summary.md").write_text("## Problema da risolvere\nx\n", encoding="utf-8")
    (plan_folder / "02-source-item-ledger.md").write_text(
        "## Plan profile\ncompact\n\nJust profile.\n", encoding="utf-8"
    )
    (plan_folder / "03-execution.md").write_text("# Execution\n", encoding="utf-8")
    (plan_folder / "questions.md").write_text("- none\n", encoding="utf-8")
    result = run_cli("audit", plan_folder)
    assert result.returncode != 0
    assert "missing-ledger-fields" in result.stdout


def test_audit_unsupported_profile(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    result = run_cli("audit", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


def test_audit_missing_summary_sections(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    (plan_folder / "01-change-summary.md").write_text("# Bare\n", encoding="utf-8")
    (plan_folder / "02-source-item-ledger.md").write_text(
        "# Ledger\n\n## Plan profile\ncompact\n\n"
        "## Recommended use\napply-plan\n\n"
        "## File map and role\nTable.\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Target and anti-scope\nT.\n\n"
        "## Owner and validator\nT.\n\n"
        "## Stop conditions\nT.\n\n",
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text("# Execution\n", encoding="utf-8")
    (plan_folder / "questions.md").write_text("- none\n", encoding="utf-8")
    result = run_cli("audit", plan_folder)
    assert "missing-summary-section" in result.stdout


def test_audit_extended_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_extended_plan(plan_folder)
    result = run_cli("audit", plan_folder)
    assert result.returncode == 0


def test_audit_extended_missing_ic(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "02-source-item-ledger.md").write_text(
        "# Ledger\n\n## Plan profile\nextended\n\n", encoding="utf-8"
    )
    result = run_cli("audit", plan_folder)
    assert result.returncode != 0
    assert "missing-implementation-contract" in result.stdout


# handoff-check


def test_handoff_check_compact_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("handoff-check", plan_folder)
    assert result.returncode == 0


def test_handoff_check_compact_json(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("handoff-check", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ready"] is True


def test_handoff_check_clarification_required(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "02-source-item-ledger.md").write_text(
        "# Ledger\n\n"
        "## Recommended use\napply-plan\n\n"
        "## Plan profile\ncompact\n\n"
        "## File map and role\n| File | Role |\n| --- | --- |\n| 01 | summary |\n\n"
        "## Clarification gate\nclarification required\n\n"
        "## Target and anti-scope\nT.\n\n"
        "## Owner and validator\nT.\n\n"
        "## Stop conditions\nT.\n\n"
        "## Source item ledger\n| ID | Source item | Acceptance | Evidence | Status | Route |\n",
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder)
    assert result.returncode != 0
    assert "clarification-required" in result.stdout


def test_handoff_check_missing_resource_table(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\nTest.\n"
        "## Risultato atteso\nTest.\n"
        "## Comportamento scelto\nTest.\n"
        "## Validazione prevista\nTest.\n"
        "## Decisione richiesta\nApprove.\n",
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder)
    assert result.returncode != 0
    assert "missing-resource-table" in result.stdout


def test_handoff_check_unsupported_profile(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()
    result = run_cli("handoff-check", plan_folder)
    assert result.returncode != 0
    assert "unsupported-plan-contract" in result.stdout


def test_handoff_check_missing_summary_language(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "01-change-summary.md").write_text(
        "## Risorse coinvolte\n| Risorsa | Azione | Scopo |\n| X | Y | Z |\n", encoding="utf-8"
    )
    result = run_cli("handoff-check", plan_folder)
    assert result.returncode != 0
    assert "missing-summary-section" in result.stdout


# tokens


def test_tokens_estimates_plan_files(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("tokens", plan_folder)

    assert result.returncode == 0
    assert "Total estimated tokens" in result.stdout


def test_tokens_json_output(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("tokens", plan_folder, "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert "total_tokens_estimate" in payload
    assert "files" in payload


# Isolated copy test


def test_copied_bundle_runs_independently(tmp_path: Path) -> None:
    """A copied skill bundle runs its CLI with ambient Python stdlib only."""
    bundle_copy = tmp_path / "internal-writing-plans"
    shutil.copytree(
        Path(".github/skills/internal-writing-plans"), bundle_copy
    )
    cli = bundle_copy / "scripts" / "plan_authoring.py"

    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)

    result = subprocess.run(
        [sys.executable, str(cli), "audit", str(plan_folder)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_copied_bundle_no_cross_bundle_import(tmp_path: Path) -> None:
    """Verify no import of sibling bundle or .github/scripts/lib."""
    import ast

    authoring_code = AUTHORING_CLI.read_text(encoding="utf-8")
    tree = ast.parse(authoring_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "internal-executing-plans" in alias.name or "retained_plans" in alias.name:
                    pytest.fail(f"Cross-bundle import found: {ast.dump(node)}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "internal-executing-plans" in module or "retained_plans" in module:
                pytest.fail(f"Cross-bundle import found: {ast.dump(node)}")


def test_shared_parity_unsupported_contract_rejected(tmp_path: Path) -> None:
    """Both CLIs reject unsupported profiles with same finding code."""
    plan_folder = tmp_path / "plan"
    plan_folder.mkdir()

    authoring_result = run_cli("handoff-check", plan_folder)
    assert "unsupported-plan-contract" in authoring_result.stdout

    executing_cli = Path(".github/skills/internal-executing-plans/scripts/plan_execution.py").resolve()
    exec_result = subprocess.run(
        [sys.executable, str(executing_cli), "inspect", str(plan_folder)],
        capture_output=True,
        text=True,
    )
    assert "unsupported-plan-contract" in exec_result.stdout


def test_shared_parity_compact_accepted(tmp_path: Path) -> None:
    """Both CLIs accept compact profiles."""
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)

    authoring_result = run_cli("handoff-check", plan_folder)
    assert authoring_result.returncode == 0

    executing_cli = Path(".github/skills/internal-executing-plans/scripts/plan_execution.py").resolve()
    exec_result = subprocess.run(
        [sys.executable, str(executing_cli), "inspect", str(plan_folder)],
        capture_output=True,
        text=True,
    )
    assert exec_result.returncode == 0
