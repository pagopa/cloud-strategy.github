from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


AUTHORING_CLI = Path(".github/skills/internal-writing-plans/scripts/plan_authoring.py").resolve()


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(AUTHORING_CLI), *[str(a) for a in args]], capture_output=True, text=True)


def _write_compact_plan(plan_folder: Path) -> None:
    plan_folder.mkdir(parents=True, exist_ok=True)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\nX\n## Risultato atteso\nY\n## Risorse coinvolte\n| Risorsa | Azione | Scopo |\n| --- | --- | --- |\n| A | B | C |\n## Comportamento scelto\nZ\n## Validazione prevista\nV\n## Decisione richiesta\nD\n",
        encoding="utf-8",
    )
    (plan_folder / "02-source-item-ledger.md").write_text(
        "## Recommended use\nexecute after explicit approval\n\n## Recommended consumer\ninternal-gateway-simple-task\n\n## Plan profile\ncompact\n\n## File map and role\nx\n\n## Clarification gate\nclarification satisfied\n\n## Target and anti-scope\nx\n\n## Owner and validator\nx\n\n## Stop conditions\nx\n",
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text("# Execution\n", encoding="utf-8")
    (plan_folder / "questions.md").write_text("# Questions\n\n- none\n", encoding="utf-8")


def _write_extended_plan(plan_folder: Path) -> None:
    _write_compact_plan(plan_folder)
    (plan_folder / "02-source-item-ledger.md").write_text(
        "## Recommended use\nexecute after explicit approval\n\n## Recommended consumer\ninternal-executing-plans\n\n## Plan profile\nextended\n\n## File map and role\nx\n\n## Clarification gate\nclarification satisfied\n\n## Target and anti-scope\nx\n\n## Owner and validator\nx\n\n## Stop conditions\nx\n",
        encoding="utf-8",
    )
    (plan_folder / "04-implementation-contract.md").write_text("# Implementation Contract\n", encoding="utf-8")


def test_init_creates_compact_scaffold(tmp_path: Path) -> None:
    plan_folder = tmp_path / "my-plan"
    result = run_cli("init", plan_folder)
    assert result.returncode == 0
    ledger = (plan_folder / "02-source-item-ledger.md").read_text(encoding="utf-8")
    assert "internal-gateway-simple-task" in ledger


def test_audit_compact_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    result = run_cli("audit", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["ready"] is True


def test_audit_rejects_profile_consumer_mismatch(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_compact_plan(plan_folder)
    ledger_path = plan_folder / "02-source-item-ledger.md"
    ledger_path.write_text(ledger_path.read_text(encoding="utf-8").replace("internal-gateway-simple-task", "internal-executing-plans"), encoding="utf-8")
    result = run_cli("audit", plan_folder)
    assert "profile-consumer-mismatch" in result.stdout


def test_handoff_check_extended_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "plan"
    _write_extended_plan(plan_folder)
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["ready"] is True
