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
        "## Comportamento scelto\nControlli semantici minimi e deterministici.\n"
        "## Validazione prevista\nPytest focalizzato e handoff-check.\n"
        "## Esecuzione prevista\nProfilo: compact. Prefisso cartella: mini-plan-*. File esecutivo: 03-execution.md. Strategia esecuzione: inferita da internal-gateway-execute-plans.\n"
        "## Decisione richiesta\nApprovare l'esecuzione del piano.\n",
        encoding="utf-8",
    )
    (plan_folder / "02-source-item-ledger.md").write_text(
        "## Recommended use\nexecute after explicit approval\n\n"
        "## Plan profile\ncompact\n\n"
        "## File map and role\n| File | Role |\n| --- | --- |\n| `03-execution.md` | executable |\n\n"
        "## Clarification gate\nclarification satisfied\n\n"
        "## Initial evidence pass\n1. Verified the bundle-local CLI exists.\n\n"
        "## Reading budget\n- Start from summary, ledger, and execution only.\n\n"
        "## Target and anti-scope\n### Target\n- Tighten plan handoff validation.\n### Anti-scope\n- Do not add model policy.\n\n"
        "## Owner and validator\n- Owner: internal-gateway-writing-plans.\n- Validator: pytest.\n\n"
        "## Stop conditions\n- Stop if checks require subjective prose scoring.\n\n"
        "## Source item ledger\n| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n| --- | --- | --- | --- | --- | --- | --- |\n| PLAN-01 | Empty-section detection | `handoff-check` rejects empty sections | repository | failing then passing test | PENDING | `03-execution.md` |\n",
        encoding="utf-8",
    )
    (plan_folder / "03-execution.md").write_text(
        "# Execution\n\n"
        "## Objective\nDeliver a compact executable handoff contract.\n\n"
        "## Chosen logic\nValidate semantic minima instead of heading presence only.\n\n"
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
    (plan_folder / "questions.md").write_text(
        "# Questions\n\n- none\n", encoding="utf-8"
    )


def _write_extended_plan(plan_folder: Path) -> None:
    _write_compact_plan(plan_folder)
    ledger_text = (plan_folder / "02-source-item-ledger.md").read_text(encoding="utf-8")
    (plan_folder / "02-source-item-ledger.md").write_text(
        ledger_text.replace("compact", "extended"),
        encoding="utf-8",
    )
    summary_path = plan_folder / "01-change-summary.md"
    summary_path.write_text(
        summary_path.read_text(encoding="utf-8").replace(
            "Profilo: compact. Prefisso cartella: mini-plan-*. File esecutivo: 03-execution.md. Strategia esecuzione: inferita da internal-gateway-execute-plans.",
            "Profilo: extended. File esecutivo: 03-execution.md. Contratto: 04-implementation-contract.md. Strategia esecuzione: inferita da internal-gateway-execute-plans.",
        ),
        encoding="utf-8",
    )
    (plan_folder / "04-implementation-contract.md").write_text(
        "# Implementation Contract\n\n"
        "## Sources\n- `.github/skills/internal-gateway-writing-plans/scripts/plan_authoring.py`\n\n"
        "## Candidate targets\n- The bundle-local authoring CLI and focused fixtures.\n\n"
        "## Validation commands\nRun in this order:\n1. pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py\n\n"
        "## Blockers and fallback rules\n- Stop if validation would require subjective scoring.\n\n"
        "## External pins\nno external evidence\n",
        encoding="utf-8",
    )


def test_init_creates_compact_scaffold(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-my-plan"
    result = run_cli("init", plan_folder)
    assert result.returncode == 0
    ledger = (plan_folder / "02-source-item-ledger.md").read_text(encoding="utf-8")
    assert "Recommended consumer" not in ledger
    summary = (plan_folder / "01-change-summary.md").read_text(encoding="utf-8")
    assert "Esecuzione prevista" in summary


def test_init_rejects_non_prefixed_compact_folder(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "handoff-plan"
    result = run_cli("init", plan_folder)
    assert result.returncode != 0
    assert "mini-plan-*" in result.stderr


def test_init_creates_extended_scaffold(tmp_path: Path) -> None:
    plan_folder = tmp_path / "my-extended-plan"
    result = run_cli("init", plan_folder, "--profile", "extended")
    assert result.returncode == 0
    ledger = (plan_folder / "02-source-item-ledger.md").read_text(encoding="utf-8")
    assert "Recommended consumer" not in ledger
    assert (plan_folder / "04-implementation-contract.md").is_file()


def test_audit_compact_ready(tmp_path: Path) -> None:
    plan_folder = (
        tmp_path / "tmp" / "superpowers" / "mini-plan-improve-handoff-contract"
    )
    _write_compact_plan(plan_folder)
    result = run_cli("audit", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["ready"] is True


def test_audit_allows_legacy_recommended_consumer_field(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-legacy-consumer"
    _write_compact_plan(plan_folder)
    ledger_path = plan_folder / "02-source-item-ledger.md"
    ledger_path.write_text(
        "## Recommended use\nexecute after explicit approval\n\n"
        "## Recommended consumer\ninternal-gateway-simple-task\n\n"
        + ledger_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
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
    (plan_folder / "03-execution.md").write_text(
        "# Execution\n\n## Objective\nTODO\n", encoding="utf-8"
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(
        f["code"] == "execution-placeholder" or f["code"] == "missing-executable-steps"
        for f in payload["findings"]
    )


def test_handoff_check_rejects_impossible_execution_order(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-impossible-order-plan"
    _write_extended_plan(plan_folder)
    (plan_folder / "03-execution.md").write_text(
        "# Execution\n\n"
        "## Objective\nDeliver the analyzer safely.\n\n"
        "## Chosen logic\nSequence creation before consumption.\n\n"
        "## Key assumptions\nThe analyzer output is local.\n\n"
        "## Executable steps\n"
        "1. Review analyzer output.\n"
        "   Target: `tmp/analyzer-summary.json`\n"
        "   Acceptance: review is possible.\n"
        "   Validation: manual evidence.\n"
        "   Fallback: stop if the file does not exist.\n"
        "   Consumes: `tmp/analyzer-summary.json`\n\n"
        "2. Create analyzer output.\n"
        "   Target: `.github/scripts/analyze_copilot_debug_logs.py`\n"
        "   Acceptance: summary file can be emitted.\n"
        "   Validation: pytest.\n"
        "   Fallback: stop if schema is unknown.\n"
        "   Creates: `tmp/analyzer-summary.json`\n\n"
        "## Validation\n- pytest\n",
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(f["code"] == "impossible-execution-order" for f in payload["findings"])


def test_handoff_check_rejects_heading_only_extended_contract(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "heading-only-extended-plan"
    _write_extended_plan(plan_folder)
    (plan_folder / "04-implementation-contract.md").write_text(
        "# Implementation Contract\n", encoding="utf-8"
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(
        f["code"].startswith("implementation-contract-") for f in payload["findings"]
    )


def test_handoff_check_rejects_missing_route_targets(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-missing-route-target"
    _write_compact_plan(plan_folder)
    ledger_path = plan_folder / "02-source-item-ledger.md"
    ledger_path.write_text(
        ledger_path.read_text(encoding="utf-8").replace(
            "`03-execution.md`", "`07-non-existent.md`"
        ),
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(f["code"] == "missing-route-target" for f in payload["findings"])


def test_handoff_check_blocks_open_questions(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-open-question"
    _write_compact_plan(plan_folder)
    (plan_folder / "questions.md").write_text(
        "# Questions\n\n- confirm route ownership\n", encoding="utf-8"
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(f["code"] == "open-questions-blocking" for f in payload["findings"])


def test_handoff_check_warns_on_oversized_compact_execution(tmp_path: Path) -> None:
    plan_folder = tmp_path / "tmp" / "superpowers" / "mini-plan-heavy-execution"
    _write_compact_plan(plan_folder)
    heavy_block = "A" * 2800
    (plan_folder / "03-execution.md").write_text(
        "# Execution\n\n"
        "## Objective\nKeep compact validation deterministic.\n\n"
        "## Chosen logic\nLarge payload to trigger warning.\n\n"
        "## Key assumptions\nThe test controls markdown size.\n\n"
        "## Executable steps\n"
        f"1. Trim oversized execution content. {heavy_block}\n"
        "   Target: `03-execution.md`\n"
        "   Acceptance: warning appears for compact profile.\n"
        "   Validation: handoff-check json output.\n"
        "   Fallback: escalate to extended profile.\n\n"
        "## Validation\n- handoff-check\n",
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert any(
        "Compact execution file is oversized" in warning
        for warning in payload["warnings"]
    )


def test_handoff_check_rejects_extended_contract_without_ordered_validation(
    tmp_path: Path,
) -> None:
    plan_folder = tmp_path / "extended-without-ordered-validation"
    _write_extended_plan(plan_folder)
    contract_path = plan_folder / "04-implementation-contract.md"
    contract_path.write_text(
        contract_path.read_text(encoding="utf-8").replace(
            "Run in this order:\n1. pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py",
            "- pytest -q tests/github/skills/internal_gateway_writing_plans/scripts/test_plan_authoring.py",
        ),
        encoding="utf-8",
    )
    result = run_cli("handoff-check", plan_folder, "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(
        f["code"] == "implementation-contract-validation-order"
        for f in payload["findings"]
    )
