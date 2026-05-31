from __future__ import annotations

from pathlib import Path

PLAN_SKILL_PATHS = {
    "internal-writing-plans": ".github/skills/internal-writing-plans/SKILL.md",
    "internal-executing-plans": ".github/skills/internal-executing-plans/SKILL.md",
}

PLAN_TASK_PATH = "tmp/superpowers/<clear-action-or-task-name>/"

WRITING_REFERENCES = {
    "compact-plan-contract": ".github/skills/internal-writing-plans/references/compact-plan-contract.md",
    "scope-challenge": ".github/skills/internal-writing-plans/references/scope-challenge.md",
    "plan-review-gate": ".github/skills/internal-writing-plans/references/plan-review-gate.md",
}

EXECUTING_REFERENCES = {
    "legacy-plan-compatibility": ".github/skills/internal-executing-plans/references/legacy-plan-compatibility.md",
    "plan-handoff": ".github/skills/internal-executing-plans/references/plan-handoff.md",
    "resume-protocol": ".github/skills/internal-executing-plans/references/resume-protocol.md",
    "completion-report": ".github/skills/internal-executing-plans/references/completion-report.md",
}


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def assert_no_plan_procedure_markers_in_agents(text: str) -> None:
    disallowed_in_agents = [
        "01-...md",
        "01-context-and-constraints.md",
        "01-change-summary.md",
        "02-source-item-ledger.md",
        "questions.md",
        "doubts-and-questions.md",
        "done-*",
        "macro-categories",
        "continue through the remaining numbered plan files",
    ]
    for marker in disallowed_in_agents:
        assert marker not in text, f"AGENTS.md must not contain plan procedure marker: {marker}"


def assert_no_plan_procedure_markers_in_copilot(text: str) -> None:
    # copilot-instructions.md may contain operational references to done-*
    # (repo-specific checkpoint). Exclude done-* from this check.
    disallowed_in_copilot = [
        "01-...md",
        "01-context-and-constraints.md",
        "01-change-summary.md",
        "02-source-item-ledger.md",
        "questions.md",
        "doubts-and-questions.md",
        "macro-categories",
        "continue through the remaining numbered plan files",
    ]
    for marker in disallowed_in_copilot:
        assert marker not in text, f"copilot-instructions.md must not contain plan procedure marker: {marker}"


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
    assert_no_plan_procedure_markers_in_agents(agents_text)
    assert "English" in agents_text
    assert "clear, local, quick, or banal tasks" not in agents_text
    assert "`Objective`" not in agents_text
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
    assert_no_plan_procedure_markers_in_copilot(copilot_text)
    assert "clear, local, quick, or banal tasks" not in copilot_text
    assert "retained planning is justified" not in copilot_text
    assert "`Objective`" not in copilot_text
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
    assert "Clear, local, quick tasks" in writing_plans_text
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
    compact_contract_text = read_text(WRITING_REFERENCES["compact-plan-contract"])
    scope_challenge_text = read_text(WRITING_REFERENCES["scope-challenge"])
    review_gate_text = read_text(WRITING_REFERENCES["plan-review-gate"])
    legacy_compat_text = read_text(EXECUTING_REFERENCES["legacy-plan-compatibility"])

    # Writing skill — profile selection and core contract
    assert "## When to use" in writing_skill_text
    assert PLAN_TASK_PATH in writing_skill_text
    assert "crosses turns" in writing_skill_text
    assert "## Profile Selection" in writing_skill_text
    assert "`compact`" in writing_skill_text
    assert "`extended`" in writing_skill_text
    assert "`legacy`" in writing_skill_text
    assert "01-change-summary.md" in writing_skill_text
    assert "02-source-item-ledger.md" in writing_skill_text
    assert "03-execution.md" in writing_skill_text
    assert "04-implementation-contract.md" in writing_skill_text
    assert "questions.md" in writing_skill_text
    assert "English" in writing_skill_text
    assert "Use English file names" in writing_skill_text
    assert "`Recommended use`" in writing_skill_text
    assert "`Plan profile`" in writing_skill_text or "Plan profile" in writing_skill_text
    assert "`File map and role`" in writing_skill_text
    assert "`Initial evidence pass`" in writing_skill_text
    assert "`Reading budget`" in writing_skill_text
    assert "source-item coverage" in writing_skill_text
    assert "stable item id" in writing_skill_text
    assert "clarification gate" in writing_skill_text
    assert "`done-*`" in writing_skill_text
    assert "final packaging" in writing_skill_text
    assert "outside the plan-and-apply loop" not in writing_skill_text
    assert "scope-challenge.md" in writing_skill_text
    assert "plan-review-gate.md" in writing_skill_text
    assert "Decision Brief" in writing_skill_text

    # Executing skill — core algorithm and ledger tracking
    assert "## When to use" in executing_skill_text
    assert "retained numbered plans" in executing_skill_text
    assert "Read `01-change-summary.md`" in executing_skill_text
    assert "02-source-item-ledger.md" in executing_skill_text
    assert "04-implementation-contract.md" in executing_skill_text
    assert "classify" in executing_skill_text.lower()
    assert "evidence pass" in executing_skill_text.lower()
    assert "ledger" in executing_skill_text.lower()
    assert "`done-*`" in executing_skill_text
    assert "packaging" in executing_skill_text
    assert "evidence-envelope.md" in executing_skill_text
    assert "completion-report.md" in executing_skill_text
    assert "DONE" in executing_skill_text
    assert "PENDING" in executing_skill_text
    assert "questions.md" in executing_skill_text
    assert "Stop only for real blockers" in executing_skill_text
    assert "No `SHIPPED`" in executing_skill_text

    # Compact plan reference — schema and escalation
    assert "## Compact File Shape" in compact_contract_text
    assert "## Escalation To Extended" in compact_contract_text
    assert "## Template: 01-change-summary.md" in compact_contract_text
    assert "## Template: 03-execution.md" in compact_contract_text
    assert "## Legacy Folder Classification" in compact_contract_text
    assert "`Plan profile`" in compact_contract_text

    # Scope challenge — profile-aware
    assert "## Required Questions" in scope_challenge_text
    assert "`coverage`: How does `02-source-item-ledger.md`" in scope_challenge_text
    assert "`extended` profiles" in scope_challenge_text
    assert "`compact` profiles" in scope_challenge_text
    assert "`implementation contract`" in scope_challenge_text
    assert "`profile`" in scope_challenge_text

    # Plan review gate — profile-aware
    assert "| Implementation contract |" in review_gate_text
    assert "| Profile |" in review_gate_text
    assert "missing source-item coverage for requested work" in review_gate_text

    # Legacy compatibility reference
    assert "## Profile Classification" in legacy_compat_text
    assert "legacy" in legacy_compat_text.lower()
    assert "## Legacy File Name Mappings" in legacy_compat_text
    assert "01-summary-direction-and-decision.md" in legacy_compat_text


def test_plan_gates_require_traceability_for_strategic_conversions() -> None:
    scope_challenge_text = read_text(
        ".github/skills/internal-writing-plans/references/scope-challenge.md"
    )
    review_gate_text = read_text(
        ".github/skills/internal-writing-plans/references/plan-review-gate.md"
    )

    assert "## Required Questions" in scope_challenge_text
    assert "`coverage`: How does `02-source-item-ledger.md`" in scope_challenge_text
    assert "`implementation contract`" in scope_challenge_text
    assert "For `extended` profiles" in scope_challenge_text
    assert "For `compact` profiles" in scope_challenge_text
    assert "`observable acceptance`: Which diff" in scope_challenge_text
    assert (
        "`02-source-item-ledger.md` or an equivalently" in scope_challenge_text
    )
    assert (
        "Coverage: <ledger coverage, explicit not-applicable, or blocker>"
        in scope_challenge_text
    )
    assert (
        "Implementation contract: <complete, not applicable (compact), missing (extended), or blocker>"
        in scope_challenge_text
    )
    assert (
        "For non-trivial retained plans, `READY` also requires explicit source-item"
        in scope_challenge_text
    )
    assert (
        "Profile: <compact, extended, or legacy>" in scope_challenge_text
    )

    assert "| Semantic coverage |" in review_gate_text
    assert "| Summary focus |" in review_gate_text
    assert "| File naming |" in review_gate_text
    assert "| Observable acceptance |" in review_gate_text
    assert "| Implementation contract |" in review_gate_text
    assert "| Profile |" in review_gate_text
    assert "clarification-only completion for executable verbs" in review_gate_text
    assert "coverage review comes before shape-only validation" in review_gate_text
    assert "missing source-item coverage for requested work" in review_gate_text
    assert "observable acceptance" in scope_challenge_text
    assert "observable acceptance" in review_gate_text


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
    assert "compact" in writing_metadata_text.lower()
    assert "$internal-executing-plans" in executing_metadata_text
    assert "classify retained plan folders" in executing_metadata_text
