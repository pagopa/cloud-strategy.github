from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_root_policy_files_keep_retained_plan_defaults_outside_always_on_detail() -> (
    None
):
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")
    assert "tmp/superpowers/" in agents_text
    assert "retained-plan" in agents_text
    assert "tmp/superpowers/" not in copilot_text


def test_writing_plans_declares_profile_only_handoff_contract() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    compact_reference = read_text(
        ".github/skills/internal-gateway-writing-plans/references/compact-plan-contract.md"
    )
    assert "Recommended consumer" not in writing_text
    assert "internal-gateway-simple-task" in writing_text
    assert "internal-gateway-execute-plans" in writing_text
    assert "mini-plan-*" in compact_reference
    assert "Decisioni aperte" in compact_reference
    assert "2,000 estimated tokens" in compact_reference
    assert "completeness over compression" in writing_text
    assert "Escalate to `extended`" in writing_text
    assert "prefer splitting into numbered files over compression" in writing_text
    assert "data-contract.md" in writing_text


def test_executing_plans_accepts_compact_and_extended_consumers() -> None:
    executing_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")
    assert "approved `compact`" in executing_text
    assert "approved `extended`" in executing_text
    assert "infer the execution strategy" in executing_text
    assert (
        "Reject `compact` folders outside the `mini-plan-*` convention"
        in executing_text
    )
    assert "mandatory requirements that are applicable" in executing_text
    assert "Block item closure and block `SHIPPED`" in executing_text
    assert "Establish execution state" in executing_text
    assert "Avoid repeated full rereads" in executing_text


def test_gateway_handoff_references_use_canonical_execution_owner() -> None:
    compatibility_text = read_text(
        ".github/skills/internal-gateway-idea-brainstorming/references/compatibility-matrix.md"
    )
    handoff_text = read_text(
        ".github/skills/internal-gateway-execute-plans/references/plan-handoff.md"
    )
    assert "internal-gateway-execute-plans" in compatibility_text
    assert "internal-executing-plans" not in compatibility_text
    assert "internal-gateway-execute-plans" in handoff_text
    assert "internal-executing-plans" not in handoff_text


def test_wrapper_prompts_respect_compact_and_extended_consumers() -> None:
    writing_wrapper = read_text(
        ".github/skills/internal-gateway-writing-plans/agents/openai.yaml"
    )
    simple_wrapper = read_text(
        ".github/skills/internal-gateway-simple-task/agents/openai.yaml"
    )
    execute_wrapper = read_text(
        ".github/skills/internal-gateway-execute-plans/agents/openai.yaml"
    )
    assert "Recommended consumer field" in writing_wrapper
    assert "Do not" in writing_wrapper
    assert "best execution path" in writing_wrapper
    assert "validation path" in writing_wrapper
    assert (
        "Route approved retained-plan execution to internal-gateway-execute-plans"
        in simple_wrapper
    )
    assert (
        "approved compact mini-plan-* plans and approved extended plans"
        in execute_wrapper
    )


def test_new_retained_plan_file_model_is_declared() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    compact_reference = read_text(
        ".github/skills/internal-gateway-writing-plans/references/compact-plan-contract.md"
    )
    execute_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")

    assert "02-execution.md" in writing_text
    assert "02-control.md" in writing_text
    assert "merged into `02-control.md`" in writing_text
    assert "02-execution.md" in compact_reference
    assert "02-control.md" in execute_text


def test_gateway_skills_preserve_compact_context_discipline() -> None:
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")

    assert "Preserve compact working state" in simple_text
    assert "Escalation trigger" in simple_text
    assert "Preserve known-context handoff quality" in writing_text
    assert "run targeted rereads" in writing_text


def test_writing_plans_counter_validation_contract_is_explicit() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    compact_reference = read_text(
        ".github/skills/internal-gateway-writing-plans/references/compact-plan-contract.md"
    )
    review_gate = read_text(
        ".github/skills/internal-gateway-writing-plans/references/plan-review-gate.md"
    )
    scope_challenge = read_text(
        ".github/skills/internal-gateway-writing-plans/references/scope-challenge.md"
    )

    assert "counter-validation-critical facts" in writing_text
    assert "counter-validation-critical facts" in compact_reference
    assert "counter-validate coverage without reading `02-execution.md` or `02-control.md`" in review_gate
    assert "counter-validate the plan without reading the control file" in scope_challenge
