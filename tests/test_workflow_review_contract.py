from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_idea_gateway_owns_retained_planning() -> None:
    skill_text = read_text(
        ".github/skills/internal-gateway-idea-brainstorming/SKILL.md"
    )
    reference_text = read_text(
        ".github/skills/internal-gateway-idea-brainstorming/references/guided-decision-interview.md"
    )
    runtime_text = read_text(
        ".github/skills/internal-gateway-idea-brainstorming/agents/openai.yaml"
    )
    assert "retained plan" in skill_text
    assert "internal-gateway-writing-plans" in skill_text
    assert "stop before execution" in skill_text
    assert "Plan Approval Gate 3" in skill_text
    assert "Handoff Gate 4" in skill_text
    assert "ask whether to continue" in skill_text
    assert "Specialization Checkpoint: gated" in skill_text
    assert (
        "User insistence does not bypass Idea Gate 0 or Critical Gate 2" in skill_text
    )
    assert "go`/`ok`/`procedi" in skill_text
    assert "Plan Approval Gate 3: waiting" in reference_text
    assert "Handoff Gate 4: plan-created" in reference_text
    assert "Specialization Checkpoint: gated" in reference_text
    assert "Direct Execution vs Retained Plan Recommendation" in skill_text
    assert "direct execution via `internal-gateway-simple-task`" in skill_text
    assert "Recommendation`, `Why`, `Tradeoff`, and `Decision`" in reference_text
    assert "mini-plan" in reference_text
    assert "go/ok/procedi" in runtime_text
    assert "Specialization Checkpoint: gated" in runtime_text
    assert "Direct Execution vs Retained Plan Recommendation" in runtime_text
    assert "choose execute, plan, or an explicit override" in runtime_text
    assert "ask whether the user wants this owner to keep the task" not in skill_text
    assert "ask whether the user wants this owner to keep the task" not in reference_text
    assert "ask whether the user wants this owner to keep the task" not in runtime_text
    assert (
        "At Interview Gate 1: ready-for-critical, ask whether to continue"
        in runtime_text
    )


def test_review_gateway_exists_and_stops_before_fixes() -> None:
    skill_text = read_text(".github/skills/internal-gateway-review/SKILL.md")
    agent_text = read_text(".github/agents/internal-gateway-review.agent.md")
    review_gate_text = read_text(
        ".github/skills/internal-gateway-review/references/review-gate.md"
    )
    review_gate_lower = review_gate_text.lower()
    assert "defect-first review" in skill_text
    assert "does not apply fixes" in skill_text
    assert "internal-gateway-writing-plans" in skill_text
    assert "internal-ai-resource-review" in skill_text
    assert "internal-copilot-audit" in skill_text
    assert "Lens selection" in skill_text
    assert ".github/skills/**" in skill_text
    assert "internal-gateway-simple-task" in agent_text
    assert "Review Gate" in review_gate_text
    assert "severity" in review_gate_lower
    assert "confidence" in review_gate_lower
    assert "evidence gap" in review_gate_lower
    assert "counter-validation" in skill_text
    assert "counter-validation" in review_gate_lower
    assert "route or next owner" in review_gate_lower
    assert "decision-usefulness" in review_gate_lower
    assert "accept, patch, investigate, plan" in review_gate_lower


def test_review_usefulness_contract_is_explicit() -> None:
    gateway_text = read_text(".github/skills/internal-gateway-review/SKILL.md")
    ai_review_text = read_text(".github/skills/internal-ai-resource-review/SKILL.md")
    report_text = read_text(
        ".github/skills/internal-ai-resource-review/references/report-contract.md"
    )
    profile_text = read_text(
        ".github/skills/internal-ai-resource-review/references/review-profiles.md"
    )
    replay_text = read_text(
        ".github/skills/internal-ai-resource-review/references/review-usefulness-replay-fixture.md"
    )

    assert "decision-usefulness" in gateway_text
    assert "clear next decision" in gateway_text
    assert "Bundle coverage rules" in ai_review_text
    assert "review-usefulness-replay-fixture.md" in ai_review_text
    assert "live prompt pack, generated artifact, retained report, or fixture" in ai_review_text
    assert "evidence digest or decision trace" in ai_review_text
    assert "Adaptive layout patterns" in report_text
    assert "Evidence compression" in report_text
    assert "Missing proof handling" in report_text
    assert "test-gap" in report_text
    assert "runtime-artifact" in report_text
    assert "No-finding and low-finding reviews" in report_text
    assert "Report coverage separately from findings" in profile_text
    assert "coach-personale" in replay_text
    assert "Focused pytest execution was unavailable" in replay_text
    assert "Does not invent additional findings" in replay_text


def test_compact_and_extended_execution_owner_is_unified() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    critical_text = read_text(
        ".github/skills/internal-gateway-critical-master/SKILL.md"
    )
    executing_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")
    assert "Recommended consumer" not in writing_text
    assert "internal-gateway-execute-plans" in writing_text
    assert "internal-gateway-simple-task" in writing_text
    assert "mini-plan-*" in executing_text
    assert "`compact`" in executing_text
    assert "retained plans" in executing_text
    assert "internal-gateway-execute-plans" in simple_text
    assert "internal-executing-plans" not in simple_text
    assert "internal-gateway-execute-plans" in critical_text
    assert "internal-executing-plans" not in critical_text
    assert "approved `compact`" in executing_text
    assert "approved `extended`" in executing_text
    assert "internal-gateway-execute-plans" in executing_text


def test_gateway_compliance_audit_contract_is_explicit() -> None:
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    executing_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")

    assert "mandatory applicable requirements" in simple_text
    assert "pre-close compliance audit" in simple_text
    assert "Block completion claims" in simple_text
    assert "single-lane and single-phase" in simple_text

    assert "item-level compliance audit" in executing_text
    assert "block `SHIPPED`" in executing_text
    assert "undefined validation strategy" in executing_text
    assert "stdlib-only CLI launcher" in executing_text


def test_simple_gateway_direct_execution_control_contract_is_explicit() -> None:
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    lanes_text = read_text(
        ".github/skills/internal-gateway-simple-task/references/simple-lanes.md"
    )
    runtime_text = read_text(
        ".github/skills/internal-gateway-simple-task/agents/openai.yaml"
    )

    assert "Direct Execution Control" in simple_text
    assert "Direct Completion Control" in simple_text
    assert "original intent, separated from emerged requirements" in simple_text
    assert "all in-scope source items" in runtime_text
    assert "mandatory applicable requirements are closed" in runtime_text
    assert "direct-control status" in lanes_text
    assert "One successful validator" in simple_text
    assert "emerged in-scope requirements" in simple_text


def test_critical_master_claim_discipline_contract() -> None:
    critical_text = read_text(
        ".github/skills/internal-gateway-critical-master/SKILL.md"
    )

    assert "Claim Discipline" in critical_text
    assert "confirmed" in critical_text
    assert "inference" in critical_text
    assert "estimate" in critical_text
    assert "unsupported numeric precision" in critical_text
    assert "original intent" in critical_text
    assert "emerged requirements" in critical_text


def test_gateway_wrappers_route_compact_and_extended_to_execute_plans() -> None:
    simple_wrapper = read_text(
        ".github/skills/internal-gateway-simple-task/agents/openai.yaml"
    )
    execute_wrapper = read_text(
        ".github/skills/internal-gateway-execute-plans/agents/openai.yaml"
    )
    completion_reference = read_text(
        ".github/skills/internal-gateway-execute-plans/references/completion-report.md"
    )
    assert (
        "Route approved retained-plan execution to internal-gateway-execute-plans"
        in simple_wrapper
    )
    assert "infer the best execution strategy from plan profile" in execute_wrapper
    assert (
        "`compact` and `extended` execution both use `internal-gateway-execute-plans`"
        in completion_reference.lower()
    )


def test_simple_gateway_readiness_brief_and_approval_gate_contract() -> None:
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    clarification_text = read_text(
        ".github/skills/internal-gateway-simple-task/references/clarification-gate.md"
    )

    assert "Readiness Brief" in simple_text
    assert "explicit user approval" in simple_text
    assert "before operational" in simple_text
    assert "Simple Gate Policy" in simple_text
    assert "`full`, `idea`, and `complete`" in simple_text
    assert "Trivial-skip proof" in simple_text
    assert "Run `grill-me` first" in simple_text
    assert "critical gate" in simple_text

    assert "compact focused `grill-me` block" in clarification_text
    assert "internal-gateway-critical-master" in clarification_text
    assert "material risk" in clarification_text
    assert "Depth Keyword Override" in clarification_text
    assert "Do not use `trivial-skip`" in clarification_text


def test_writing_plans_scaffold_first_and_audit_early_contract() -> None:
    writing_text = read_text(".github/skills/internal-gateway-writing-plans/SKILL.md")
    runtime_text = read_text(
        ".github/skills/internal-gateway-writing-plans/agents/openai.yaml"
    )

    assert "run bundle-local `init` first" in writing_text
    assert "Run `audit` first, then run `handoff-check`" in writing_text
    assert "token warnings as review inputs" in writing_text
    assert "init scaffold first" in runtime_text
    assert "audit first" in runtime_text
    assert "handoff-check" in runtime_text
    assert "second" in runtime_text
