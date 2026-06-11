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
    assert "internal-gateway-writing-plans" in agents_text
    assert "tmp/superpowers/" not in copilot_text


def test_writing_plans_declares_profile_consumer_contract() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    compact_reference = read_text(
        ".github/skills/internal-gateway-writing-plans/references/compact-plan-contract.md"
    )
    assert "Recommended consumer" in writing_text
    assert "internal-gateway-simple-task" in writing_text
    assert "internal-gateway-execute-plans" in writing_text
    assert "mini-plan-*" in compact_reference
    assert "Esecuzione prevista" in compact_reference


def test_executing_plans_accepts_only_extended_consumers() -> None:
    executing_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")
    assert "approved `extended`" in executing_text
    assert (
        "Reject any folder whose recommended consumer is not `internal-gateway-execute-plans`"
        in executing_text
    )


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
    assert "route compact plans to internal-gateway-simple-task" in writing_wrapper
    assert "extended plans to internal-gateway-execute-plans" in writing_wrapper
    assert "Approved compact retained plans are supported" in simple_wrapper
    assert (
        "Compact execution belongs to internal-gateway-simple-task" in execute_wrapper
    )
