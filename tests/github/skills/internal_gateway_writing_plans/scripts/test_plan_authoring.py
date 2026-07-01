from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

AUTHORING_CLI = Path(
    ".github/skills/internal-gateway-writing-plans/scripts/plan_authoring.py"
).resolve()


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUTHORING_CLI), *[str(a) for a in args]],
        capture_output=True,
        text=True,
    )


def _write_compact_plan(plan_folder: Path) -> None:
    plan_folder.mkdir(parents=True, exist_ok=True)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\nRidurre l'ambiguita di handoff.\n"
        "## Risultato atteso\nUn executor puo partire senza riletture larghe.\n"
        "## Risorse coinvolte\n| Risorsa | Azione | Scopo |\n| --- | --- | --- |\n| Skill | update | Tighten handoff |\n"
        "## Decisione richiesta\nApprovare l'esecuzione del piano.\n"
        "## Decisioni aperte\nnone\n",
        encoding="utf-8",
    )
    (plan_folder / "02-execution.md").write_text(
        "# Execution\n\n"
        "## Plan profile\ncompact\n\n"
        "## Target and anti-scope\n"
        "### Target\n- Tighten plan handoff validation.\n"
        "### Anti-scope\n- Do not add model policy.\n\n"
        "## Owner and validator\n- Owner: internal-gateway-writing-plans.\n- Validator: pytest.\n\n"
        "## Stop conditions\n- Stop if checks require subjective prose scoring.\n\n"
        "## Objective\nDeliver a compact executable handoff contract.\n\n"
        "## Chosen logic\nValidate semantic minima instead of heading presence only.\n\n"
        "## Key assumptions\nThe bundle-local CLI remains stdlib-only.\n\n"
        "## Executable steps\n"
        "1. Tighten the semantic audit in `plan_authoring.py`.\n"
        "   Target: `.github/skills/internal-gateway-writing-plans/scripts/plan_authoring.py`\n"
        "   Acceptance: empty sections fail.\n"
        "   Validation: pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py\n"
        "   Fallback: stop if the rule requires subjective prose scoring.\n\n"
        "## Validation\n- Run the focused pytest target.\n\n"
        "## Source item coverage\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| PLAN-01 | Empty-section detection | `handoff-check` rejects empty sections | repository | failing then passing test | PENDING | `02-execution.md` |\n",
        encoding="utf-8",
    )


def _write_extended_plan(plan_folder: Path) -> None:
    _write_compact_plan(plan_folder)
    (plan_folder / "02-execution.md").unlink()
    (plan_folder / "02-control.md").write_text(
        "# Source Item Control\n\n"
        "## Recommended use\nexecute after explicit approval\n\n"
        "## Plan profile\nextended\n\n"
        "## File map and role\n| File | Role |\n| --- | --- |\n| `03-execution.md` | executable |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Initial evidence pass\n1. Verified the bundle-local CLI exists.\n\n"
        "## Reading budget\n- Start from summary, control, and execution only.\n\n"
        "## Target and anti-scope\n### Target\n- Tighten plan handoff validation.\n### Anti-scope\n- Do not add model policy.\n\n"
        "## Owner and validator\n- Owner: internal-gateway-writing-plans.\n- Validator: pytest.\n\n"
        "## Stop conditions\n- Stop if checks require subjective prose scoring.\n\n"
        "## Sources\n- `.github/skills/internal-gateway-writing-plans/scripts/plan_authoring.py`\n\n"
        "## Candidate targets\n- The bundle-local authoring CLI and focused fixtures.\n\n"
        "## Validation commands\nRun in this order:\n1. pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py\n\n"
        "## Blockers and fallback rules\n- Stop if validation would require subjective scoring.\n\n"
        "## External pins\nno external evidence\n\n"
        "## Source item ledger\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| PLAN-01 | Empty-section detection | `handoff-check` rejects empty sections | repository | failing then passing test | PENDING | `03-execution.md` |\n",
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text(
        "# Execution\n\n"
        "## Objective\nDeliver an extended executable handoff contract.\n\n"
        "## Chosen logic\nKeep control facts in 02-control and execution in 03-execution.\n\n"
        "## Key assumptions\nThe bundle-local CLI remains stdlib-only.\n\n"
        "## Executable steps\n"
        "1. Tighten the semantic audit in `plan_authoring.py`.\n"
        "   Target: `.github/skills/internal-gateway-writing-plans/scripts/plan_authoring.py`\n"
        "   Acceptance: empty sections fail.\n"
        "   Validation: pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py\n"
        "   Fallback: stop if the rule requires subjective prose scoring.\n\n"
        "## Validation\n- Run the focused pytest target.\n",
        encoding="utf-8",
    )


def test_init_creates_compact_scaffold(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-my-plan"
    result = run_cli("init", plan_folder)
    assert result.returncode == 0
    assert (plan_folder / "02-execution.md").is_file()
    assert not (plan_folder / "questions.md").exists()
    summary_text = (plan_folder / "01-change-summary.md").read_text(encoding="utf-8")
    assert "## Decisioni aperte" in summary_text
    assert "## Comportamento scelto" not in summary_text
    assert "## Validazione prevista" not in summary_text
    assert "## Esecuzione prevista" not in summary_text


def test_init_rejects_non_prefixed_compact_folder(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "handoff-plan"
    result = run_cli("init", plan_folder)
    assert result.returncode != 0
    assert "mini-plan-*" in result.stderr


def test_init_creates_extended_scaffold(tmp_path: Path) -> None:
    plan_folder = tmp_path / "my-extended-plan"
    result = run_cli("init", plan_folder, "--profile", "extended")
    assert result.returncode == 0
    assert (plan_folder / "02-control.md").is_file()
    assert (plan_folder / "03-execution.md").is_file()


def test_audit_compact_ready(tmp_path: Path) -> None:
    plan_folder = (
        tmp_path / "tmp" / "superpowers" / "mini-plan-improve-handoff-contract"
    )
    _write_compact_plan(plan_folder)
    result = run_cli("audit", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["ready"] is True


def test_handoff_check_extended_ready(tmp_path: Path) -> None:
    plan_folder = tmp_path / "lower-context-compatible-plan"
    _write_extended_plan(plan_folder)
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["ready"] is True


def test_handoff_check_rejects_placeholder_sections(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-placeholder-plan"
    _write_compact_plan(plan_folder)
    (plan_folder / "02-execution.md").write_text(
        "# Execution\n\n## Plan profile\ncompact\n\n## Objective\nTODO\n",
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(
        f["code"] == "execution-placeholder" or f["code"] == "missing-executable-steps"
        for f in payload["findings"]
    )


def test_handoff_check_rejects_missing_route_targets(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-missing-route-target"
    _write_compact_plan(plan_folder)
    execution_path = plan_folder / "02-execution.md"
    execution_path.write_text(
        execution_path.read_text(encoding="utf-8").replace(
            "`02-execution.md`", "`07-non-existent.md`"
        ),
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(f["code"] == "missing-route-target" for f in payload["findings"])


def test_handoff_check_warns_on_oversized_compact_execution(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-heavy-execution"
    _write_compact_plan(plan_folder)
    heavy_block = "A" * 6200
    (plan_folder / "02-execution.md").write_text(
        "# Execution\n\n"
        "## Plan profile\ncompact\n\n"
        "## Target and anti-scope\n### Target\n- Keep compact validation deterministic.\n### Anti-scope\n- none\n\n"
        "## Owner and validator\n- owner\n\n"
        "## Stop conditions\n- none\n\n"
        "## Objective\nKeep compact validation deterministic.\n\n"
        "## Chosen logic\nLarge payload to trigger warning.\n\n"
        "## Key assumptions\nThe test controls markdown size.\n\n"
        "## Executable steps\n"
        f"1. Trim oversized execution content. {heavy_block}\n"
        "   Target: `02-execution.md`\n"
        "   Acceptance: warning appears for compact profile.\n"
        "   Validation: handoff-check json output.\n"
        "   Fallback: escalate to extended profile.\n\n"
        "## Validation\n- handoff-check\n\n"
        "## Source item coverage\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| PLAN-01 | oversized warning | warning appears | validator | handoff-check | PENDING | `02-execution.md` |\n",
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert any(
        "Compact execution file is oversized" in warning
        for warning in payload["warnings"]
    )


def test_handoff_check_warns_on_oversized_compact_summary(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-heavy-summary"
    _write_compact_plan(plan_folder)
    heavy_summary = "A" * 1400
    summary_path = plan_folder / "01-change-summary.md"
    summary_path.write_text(
        summary_path.read_text(encoding="utf-8").replace(
            "Ridurre l'ambiguita di handoff.",
            f"Ridurre l'ambiguita di handoff. {heavy_summary}",
        ),
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert any(
        "Compact 01-change-summary.md is oversized" in warning
        for warning in payload["warnings"]
    )


def test_audit_warns_when_summary_hides_counter_validation_facts(
    tmp_path: Path,
) -> None:
    plan_folder = (
        tmp_path / "tmp" / "superpowers" / "mini-plan-counter-validation-warning"
    )
    _write_compact_plan(plan_folder)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\n"
        "Allineare il piano a un nuovo contratto dati per output generati.\n"
        "## Risultato atteso\n"
        "- Gli output rigenerati rispettano il nuovo schema e correggono i dati.\n"
        "## Risorse coinvolte\n"
        "| Risorsa | Azione | Scopo |\n"
        "| --- | --- | --- |\n"
        "| Aggregate + slide outputs | update | Allineare gli output |\n"
        "## Decisione richiesta\n"
        "Approvare il piano.\n"
        "## Decisioni aperte\n"
        "none\n",
        encoding="utf-8",
    )
    execution_path = plan_folder / "02-execution.md"
    execution_path.write_text(
        execution_path.read_text(encoding="utf-8").replace(
            "| PLAN-01 | Empty-section detection | `handoff-check` rejects empty sections | repository | failing then passing test | PENDING | `02-execution.md` |",
            "| PLAN-01 | Aggregate and slide data contract | `impacted_platforms` and `impacted_subscriptions` become the first aggregate columns; `technology_or_service` stays before `retiring_feature`; `source_links` never stays empty and missing values trigger a blocking diagnostic; rows 27-33 are restored with no row-count loss | repository | audit plus focused file diff | PENDING | `02-execution.md` |",
        ),
        encoding="utf-8",
    )

    result = run_cli("audit", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["ready"] is True
    assert any(
        f["code"] == "summary-missing-counter-validation-facts"
        and f["severity"] == "WARNING"
        for f in payload["findings"]
    )


def test_audit_accepts_summary_with_counter_validation_facts(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-counter-validation-ok"
    _write_compact_plan(plan_folder)
    (plan_folder / "01-change-summary.md").write_text(
        "## Problema da risolvere\n"
        "Allineare il piano a un nuovo contratto dati per output generati.\n"
        "## Risultato atteso\n"
        "- Aggregate TSV con `impacted_platforms` e `impacted_subscriptions` come prime colonne.\n"
        "- `technology_or_service` resta prima di `retiring_feature`; `source_links` e sempre valorizzato oppure scatta una diagnostica bloccante.\n"
        "- Le righe 27-33 vengono ripristinate senza perdita di righe.\n"
        "## Risorse coinvolte\n"
        "| Risorsa | Azione | Scopo |\n"
        "| --- | --- | --- |\n"
        "| Aggregate + slide outputs | update | Preservare ordine colonne, campi obbligatori e integrita dati |\n"
        "## Decisione richiesta\n"
        "Approvare il piano.\n"
        "## Decisioni aperte\n"
        "none\n",
        encoding="utf-8",
    )
    execution_path = plan_folder / "02-execution.md"
    execution_path.write_text(
        execution_path.read_text(encoding="utf-8").replace(
            "| PLAN-01 | Empty-section detection | `handoff-check` rejects empty sections | repository | failing then passing test | PENDING | `02-execution.md` |",
            "| PLAN-01 | Aggregate and slide data contract | `impacted_platforms` and `impacted_subscriptions` become the first aggregate columns; `technology_or_service` stays before `retiring_feature`; `source_links` never stays empty and missing values trigger a blocking diagnostic; rows 27-33 are restored with no row-count loss | repository | audit plus focused file diff | PENDING | `02-execution.md` |",
        ),
        encoding="utf-8",
    )

    result = run_cli("audit", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["ready"] is True
    assert not any(
        f["code"] == "summary-missing-counter-validation-facts"
        for f in payload["findings"]
    )


def test_handoff_check_rejects_extended_control_without_ordered_validation(
    tmp_path: Path,
) -> None:
    plan_folder = tmp_path / "extended-without-ordered-validation"
    _write_extended_plan(plan_folder)
    control_path = plan_folder / "02-control.md"
    control_path.write_text(
        control_path.read_text(encoding="utf-8").replace(
            "Run in this order:\n1. pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py",
            "- pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py",
        ),
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(f["code"] == "control-validation-order" for f in payload["findings"])
