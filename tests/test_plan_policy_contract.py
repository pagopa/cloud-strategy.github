from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_root_policy_files_keep_retained_plan_paths_outside_always_on_detail() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")
    assert "tmp/superpowers/" not in agents_text
    assert "retained-plan" not in agents_text
    assert "tmp/superpowers/" not in copilot_text


def test_writing_plans_resets_to_superpowers_wrapper_contract() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    wrapper_text = read_text(
        ".github/skills/internal-gateway-writing-plans/agents/openai.yaml"
    )

    assert "superpowers-writing-plans" in writing_text
    assert "delegate" in writing_text.lower()
    assert "decide whether to create a retained plan" in writing_text
    assert "tmp/superpowers/plans/YYYY-MM-DD-<feature-name>.md" in writing_text
    assert "Target" in writing_text
    assert "Anti-scope" in writing_text
    assert "Nearest owner" in writing_text
    assert "Validation path" in writing_text
    assert "Stop conditions" in writing_text
    assert "Observable acceptance" in writing_text
    assert "Execution-readiness check" in writing_text
    assert "task order" in writing_text
    assert "file targets" in writing_text
    assert "handoff readiness" in writing_text
    assert "superpowers-writing-plans" in wrapper_text
    assert "delegate" in wrapper_text.lower()


def test_writing_plans_wrapper_rejects_legacy_protocol_terms() -> None:
    tracked_paths = [
        ".github/skills/internal-gateway-writing-plans/SKILL.md",
        ".github/skills/internal-gateway-writing-plans/agents/openai.yaml",
    ]
    banned_terms = [
        "`compact`",
        "`extended`",
        "mini-plan-*",
        "01-change-summary.md",
        "02-execution.md",
        "02-control.md",
        "handoff-check",
        "plan_authoring.py",
        "Recommended consumer",
        "Plan-only mode",
        "force plan-only mode",
        "stop after plan creation",
    ]

    for relative_path in tracked_paths:
        text = read_text(relative_path)
        for banned in banned_terms:
            assert banned not in text, f"{relative_path} still contains {banned}"


def test_writing_plans_preserves_short_preflight_context_discipline() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    assert "short preflight" in writing_text
    assert "targeted rereads" in writing_text
    assert "known-context handoff quality" in writing_text


def test_executing_plans_is_lightweight_superpowers_wrapper() -> None:
    executing_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")
    assert "gateway-only wrapper" in executing_text
    assert "superpowers-executing-plans" in executing_text
    assert "<plan-basename>.<STATUS>.md" in executing_text
    assert "DONE" in executing_text
    assert "BLOCKED" in executing_text
    assert "PARTIAL" in executing_text
    assert "NEEDS_REVIEW" in executing_text
    assert "Legacy Contract Boundary" in executing_text


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
