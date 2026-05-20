from __future__ import annotations

from pathlib import Path

PLAN_SKILL_PATHS = {
    "internal-writing-plans": ".github/skills/internal-writing-plans/SKILL.md",
    "internal-executing-plans": ".github/skills/internal-executing-plans/SKILL.md",
}

PLAN_TASK_PATH = "tmp/superpowers/<clear-action-or-task-name>/"


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def assert_no_plan_procedure_markers(text: str) -> None:
    disallowed_markers = [
        "01-...md",
        "01-contesto-e-vincoli.md",
        "dubbi-e-domande.md",
        "done-*",
        "macro-categories",
        "continue through the remaining numbered plan files",
    ]
    for marker in disallowed_markers:
        assert marker not in text


def test_root_policy_files_define_repository_plan_defaults() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")

    assert (
        "The default authoring language for repository artifacts is English"
        in agents_text
    )
    assert (
        "`tmp/superpowers/` and `LESSONS_LEARNED.md` may hold retained work"
        in agents_text
    )
    assert "Keep file shape, execution workflow, and ledger row rules" in agents_text
    assert "strategic operating bridge" in agents_text
    assert "tactical operating defaults" in agents_text
    assert "## Tactical Defaults" in agents_text
    assert (
        "Use `plan` mode for non-trivial repository-owned work when ambiguity, "
        "ownership, rollout, validation, or multiple credible paths remain"
        in agents_text
    )
    assert "user-selected gateway skills with visible phases" in agents_text
    assert (
        "Use `execute` mode only when the target state and validation path are concrete"
        in agents_text
    )
    assert (
        "Do not report work as complete from intent alone; cite validation evidence or name the explicit validation gap"
        in agents_text
    )
    assert "Prefer root-cause fixes over symptom workarounds" in agents_text
    assert "`internal-writing-plans`" not in agents_text
    assert "`internal-executing-plans`" not in agents_text
    assert "operational procedures, checklists, file-shape recipes" in agents_text
    assert_no_plan_procedure_markers(agents_text)
    assert "Italian" in agents_text
    assert "clear, local, quick, or banal tasks" not in agents_text
    assert "`Obiettivo`" not in agents_text
    assert "5-7 bullets when practical" not in agents_text

    assert (
        "The default authoring language for repository artifacts is English"
        in copilot_text
    )
    assert (
        "Treat retained plans and `LESSONS_LEARNED.md` as non-canonical" in copilot_text
    )
    assert (
        "dedicated retained-plan skills and scoped lessons instructions" in copilot_text
    )
    assert (
        "Use plan mode when ambiguity, ownership, rollout, validation, or "
        "multiple credible paths remain" in copilot_text
    )
    assert (
        "Use execute mode only when the target state and validation path are concrete"
        in copilot_text
    )
    assert "Do not report completion from intent alone" in copilot_text
    assert PLAN_TASK_PATH not in copilot_text
    assert "`internal-writing-plans`" not in copilot_text
    assert "`internal-executing-plans`" not in copilot_text
    assert_no_plan_procedure_markers(copilot_text)
    assert "clear, local, quick, or banal tasks" not in copilot_text
    assert "retained planning is justified" not in copilot_text
    assert "`Obiettivo`" not in copilot_text
    assert "5-7 bullets when practical" not in copilot_text


def test_gateway_operational_flow_prefers_repository_plan_wrappers() -> None:
    operational_agent_text = read_text(
        ".github/agents/internal-gateway-operational-flow.agent.md"
    )
    operational_skill_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )
    mode_contracts_text = read_text(
        ".github/skills/internal-gateway-operational-flow/references/mode-contracts.md"
    )
    writing_plans_text = read_text(".github/skills/internal-writing-plans/SKILL.md")

    assert "## Core Skill" in operational_agent_text
    assert "- `internal-gateway-operational-flow`" in operational_agent_text
    assert "internal-writing-plans" in mode_contracts_text
    assert "internal-executing-plans" in operational_skill_text
    assert "clear, local, quick, or banal" in writing_plans_text
    assert "Retained repository-owned plan authoring" in mode_contracts_text


def test_plan_wrapper_skills_are_listed_in_ownership_map_and_inventory() -> None:
    ownership_map_text = read_text(
        ".github/skills/internal-gateway-operational-flow/references/mode-contracts.md"
    )
    inventory_text = read_text(".github/INVENTORY.md")

    assert "| `internal-writing-plans` | `plan` mode |" in ownership_map_text
    assert (
        "| `internal-executing-plans` | `apply-plan` execution engine |"
        in ownership_map_text
    )
    assert PLAN_TASK_PATH in ownership_map_text

    for skill_path in PLAN_SKILL_PATHS.values():
        assert f"- `{skill_path}`" in inventory_text

    assert (
        "- `.github/skills/internal-gateway-operational-flow/SKILL.md`"
        in inventory_text
    )
    assert (
        "- `.github/skills/internal-gateway-critical-master/SKILL.md`" in inventory_text
    )


def test_plan_wrapper_skills_define_local_plan_contracts() -> None:
    writing_skill_text = read_text(PLAN_SKILL_PATHS["internal-writing-plans"])
    executing_skill_text = read_text(PLAN_SKILL_PATHS["internal-executing-plans"])

    assert "## When to use" in writing_skill_text
    assert PLAN_TASK_PATH in writing_skill_text
    assert "crosses turns" in writing_skill_text
    assert "handoff, tracking, or provenance" in writing_skill_text
    assert (
        "strategic, review-only, or monolithic retained plan into an executable retained plan"
        in writing_skill_text
    )
    assert "01-riassunto-direzione-e-decisione.md" in writing_skill_text
    assert "`Uso consigliato`" in writing_skill_text
    assert "`Mappa file e ruolo`" in writing_skill_text
    assert "`Evidence pass iniziale`" in writing_skill_text
    assert "`Budget lettura`" in writing_skill_text
    assert "control file" in writing_skill_text
    assert "02-esecuzione.md" in writing_skill_text
    assert "02-matrice-operativa.md" in writing_skill_text
    assert "macro-category" in writing_skill_text
    assert "monolithic" in writing_skill_text
    assert "dubbi-e-domande.md" in writing_skill_text
    assert "Italian" in writing_skill_text
    assert (
        "done-*`, `evidence-envelope.md`, and `completion-report.md`"
        in writing_skill_text
    )
    assert "## Local retained-plan contract" in writing_skill_text
    assert (
        "preserve the source decision inventory before compression"
        in writing_skill_text
    )
    assert "traceability file must map every source item" in writing_skill_text
    assert (
        "Do not retire, delete, or replace the source strategic artifact"
        in writing_skill_text
    )
    assert "## File-role conventions" in writing_skill_text
    assert (
        "traceability owner for strategic-to-operational conversions"
        in writing_skill_text
    )
    assert "## Token And Reading Discipline" in writing_skill_text
    assert "Coverage before compression" in writing_skill_text
    assert "Classify the folder before broad reading" in writing_skill_text
    assert (
        "Limit the first pass to target existence, the riskiest claim"
        in writing_skill_text
    )
    assert "rg --no-ignore" in writing_skill_text
    assert "Use `grill-me` only after the evidence pass" in writing_skill_text
    assert "## Numbered-file shape" in writing_skill_text
    assert "### Summary control file" in writing_skill_text
    assert "### Executable numbered files" in writing_skill_text
    assert "scanability and decision review" in writing_skill_text
    assert "`Obiettivo`" in writing_skill_text
    assert "`Direzione proposta`" in writing_skill_text
    assert "`Decisione richiesta`" in writing_skill_text
    assert "`Uso consigliato`" in writing_skill_text
    assert "`Mappa file e ruolo`" in writing_skill_text
    assert "`Evidence pass iniziale`" in writing_skill_text
    assert "`Budget lettura`" in writing_skill_text
    assert "`Stop conditions`" in writing_skill_text
    assert "`Logica scelta`" in writing_skill_text
    assert "`Assunzioni chiave`" in writing_skill_text
    assert "`Passi eseguibili`" in writing_skill_text
    assert "`Validazione`" in writing_skill_text
    assert "numbered control file, not as an executable task list" in writing_skill_text
    assert "5-7 bullets when practical" in writing_skill_text
    assert "1-2 lines when practical" in writing_skill_text
    assert "outside the plan-and-apply loop" in writing_skill_text
    assert (
        "source-item coverage through `02-matrice-operativa.md`" in writing_skill_text
    )
    assert "Compressing or deleting a strategic source plan" in writing_skill_text

    assert "## When to use" in executing_skill_text
    assert "retained numbered plans" in executing_skill_text
    assert "Read `01-riassunto-direzione-e-decisione.md` first" in executing_skill_text
    assert (
        "Use the summary file to classify folder purpose and file roles"
        in executing_skill_text
    )
    assert "source-item coverage owner" in executing_skill_text
    assert "Evidence pass iniziale" in executing_skill_text
    assert "Budget lettura" in executing_skill_text
    assert (
        "target existence, riskiest claim, and nearest validator"
        in executing_skill_text
    )
    assert "rg --no-ignore" in executing_skill_text
    assert (
        "classification, reading-budget, and evidence-pass role" in executing_skill_text
    )
    assert 'generic request such as "analyze this plan"' in executing_skill_text
    assert "done-<source-file-name>.md" in executing_skill_text
    assert "dubbi-e-domande.md" in executing_skill_text
    assert "move it into the matching `done-*` file" in executing_skill_text
    assert "remove it from the active plan file" in executing_skill_text
    assert "Delete an active plan file" in executing_skill_text
    assert "Continue automatically" in executing_skill_text
    assert "Stop only for real blockers" in executing_skill_text
    assert (
        "Strategic-to-operational conversions used `02-matrice-operativa.md`"
        in executing_skill_text
    )
    assert (
        "traceability matrix has preserved source-item coverage" in executing_skill_text
    )


def test_plan_gates_require_traceability_for_strategic_conversions() -> None:
    scope_challenge_text = read_text(
        ".github/skills/internal-writing-plans/references/scope-challenge.md"
    )
    review_gate_text = read_text(
        ".github/skills/internal-writing-plans/references/plan-review-gate.md"
    )

    assert "## Required Questions" in scope_challenge_text
    assert (
        "`coverage`: Which traceability matrix or equivalent owner"
        in scope_challenge_text
    )
    assert (
        "`02-matrice-operativa.md` or an equivalently clear traceability owner"
        in scope_challenge_text
    )
    assert (
        "Coverage: <traceability owner, explicit not-applicable, or blocker>"
        in scope_challenge_text
    )
    assert (
        "For strategic-to-operational conversions, `READY` also requires explicit source-item coverage"
        in scope_challenge_text
    )

    assert "| Semantic coverage |" in review_gate_text
    assert "coverage review comes before shape-only validation" in review_gate_text
    assert (
        "missing source-item coverage in a strategic-to-operational conversion"
        in review_gate_text
    )


def test_plan_wrapper_skills_ship_openai_metadata() -> None:
    writing_metadata_text = read_text(
        ".github/skills/internal-writing-plans/agents/openai.yaml"
    )
    executing_metadata_text = read_text(
        ".github/skills/internal-executing-plans/agents/openai.yaml"
    )

    for metadata_text in (writing_metadata_text, executing_metadata_text):
        assert "interface:" in metadata_text
        assert "display_name:" in metadata_text
        assert "short_description:" in metadata_text

    assert "$internal-writing-plans" in writing_metadata_text
    assert (
        "always starting with 01-riassunto-direzione-e-decisione.md"
        in writing_metadata_text
    )
    assert "$internal-executing-plans" in executing_metadata_text
    assert (
        "classify retained plan folders from 01-riassunto-direzione-e-decisione.md"
        in executing_metadata_text
    )
