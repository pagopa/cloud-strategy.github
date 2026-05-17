from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def assert_contains_all(relative_path: str, snippets: tuple[str, ...]) -> None:
    text = read_text(relative_path)

    for snippet in snippets:
        assert snippet in text, f"{relative_path} is missing {snippet!r}"


def test_canonical_routing_contract_keeps_deterministic_repo_owned_work_in_execution() -> (
    None
):
    delivery_operator_text = read_text(
        ".github/agents/internal-delivery-operator.agent.md"
    )
    planning_leader_text = read_text(".github/agents/internal-planning-leader.agent.md")
    operating_model_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )

    assert (
        "deterministic realignment across adjacent repository-owned assets"
        in delivery_operator_text
    )
    assert (
        "Boundary crossing alone does not make the task planning-owned."
        in planning_leader_text
    )
    assert (
        "File count and adjacent boundary crossing are heuristics, not automatic planning triggers."
        in operating_model_text
    )
    assert (
        "If the entry point or phase is unclear, use `plan` as the safe fallback"
        in operating_model_text
    )


def test_superpowers_assets_use_tmp_superpowers_for_transient_paths() -> None:
    superpowers_paths = (
        ".github/skills/superpowers-brainstorming/SKILL.md",
        ".github/skills/superpowers-brainstorming/spec-document-reviewer-prompt.md",
        ".github/skills/superpowers-writing-plans/SKILL.md",
        ".github/skills/superpowers-subagent-driven-development/SKILL.md",
        ".github/skills/superpowers-requesting-code-review/SKILL.md",
    )

    for relative_path in superpowers_paths:
        assert "docs/superpowers" not in read_text(relative_path)

    assert "tmp/superpowers/" in read_text(".github/skills/superpowers-brainstorming/SKILL.md")
    assert "tmp/superpowers/" in read_text(".github/skills/superpowers-writing-plans/SKILL.md")


def test_superpowers_workflows_do_not_claim_deterministic_textual_governance_maintenance() -> (
    None
):
    brainstorming_text = read_text(".github/skills/superpowers-brainstorming/SKILL.md")
    writing_plans_text = read_text(".github/skills/superpowers-writing-plans/SKILL.md")
    tdd_text = read_text(".github/skills/superpowers-test-driven-development/SKILL.md")

    assert (
        "Do not use this workflow for deterministic repository-owned maintenance of prompt, skill, agent, instruction, or Markdown assets"
        in brainstorming_text
    )
    assert (
        "Do not use this workflow as the default gate for deterministic repository-owned maintenance or realignment"
        in writing_plans_text
    )
    assert "- New features" in tdd_text
    assert "- Bug fixes" in tdd_text
    assert (
        "Do not treat this workflow as the default for prompt, skill, agent, instruction, or Markdown authoring"
        in tdd_text
    )


def test_agent_authoring_docs_preserve_subagent_inherited_defaults_note() -> None:
    agent_development_text = read_text(".github/skills/internal-agent-creator/SKILL.md")
    subagent_patterns_text = read_text(
        ".github/skills/internal-agent-creator/references/subagent-patterns.md"
    )

    assert (
        "subagents inherit the main session agent, model, and tools"
        in agent_development_text
    )
    assert (
        "a subagent inherits the main session agent, model, and tools"
        in subagent_patterns_text
    )


def test_repo_owned_agent_and_reference_authoring_guardrails_stay_scoped() -> None:
    agent_instruction_text = read_text(
        ".github/instructions/internal-copilot-agent-authoring.instructions.md"
    )
    reference_instruction_text = read_text(
        ".github/instructions/internal-copilot-skill-reference-authoring.instructions.md"
    )
    agent_development_text = read_text(".github/skills/internal-agent-creator/SKILL.md")
    agent_contract_text = read_text(
        ".github/skills/internal-agent-creator/references/agent-contract.md"
    )
    skill_creator_text = read_text(".github/skills/internal-skill-creator/SKILL.md")
    writing_skills_text = read_text(
        ".github/skills/internal-skill-creator/references/writing-skills-checklist.md"
    )

    assert not Path(
        ".github/instructions/internal-copilot-agent-skill-authoring.instructions.md"
    ).exists()
    assert (
        'applyTo: ".github/agents/internal-*.agent.md,.github/agents/local-*.agent.md"'
        in agent_instruction_text
    )
    assert (
        'applyTo: ".github/skills/internal-*/references/**/*.md,.github/skills/local-*/references/**/*.md"'
        in reference_instruction_text
    )
    assert ".github/skills/**/SKILL.md" not in agent_instruction_text
    assert ".github/skills/**/SKILL.md" not in reference_instruction_text
    assert "Treat `## Preferred/Optional Skills` as legacy" in agent_instruction_text
    assert (
        "Use references as the deep owner for reusable tables, templates, and detailed checklists."
        in reference_instruction_text
    )
    assert (
        "When a paired skill or reference is the detailed contract owner"
        in agent_development_text
    )
    assert (
        "If an agent points to a paired skill or reference as the detailed contract owner"
        in agent_contract_text
    )
    assert (
        "When a skill sits behind a paired agent or local references"
        in skill_creator_text
    )
    assert "If the skill sits behind a paired agent" in writing_skills_text


def test_gateway_contains_completion_checks() -> None:
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "## Completion Checks",
            "`Check 1`: Plan coverage",
            "`Check 2`: Contract coverage",
            "`Check 3`: Evidence coverage",
        ),
    )


def test_gateway_points_to_plan_completion_audit_reference() -> None:
    gateway_text = read_text(".github/skills/internal-gateway-operational-flow/SKILL.md")

    assert "plan-completion-audit.md" in gateway_text
    assert "Status Vocabulary" not in gateway_text
    assert_contains_all(
        ".github/skills/internal-systems-review/references/plan-completion-audit.md",
        (
            "Status Vocabulary",
            "`DONE`",
            "`PARTIAL`",
            "`NOT_DONE`",
            "`CHANGED`",
            "`UNVERIFIABLE`",
        ),
    )


def test_systems_review_lens_referenced() -> None:
    assert_contains_all(
        ".github/agents/internal-review-guard.agent.md",
        ("internal-systems-review", "review lenses", "scope drift", "audit dispatch"),
    )
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        ("internal-systems-review", "plan-completion-audit.md", "scope-drift.md"),
    )


def test_security_review_promotion_gated() -> None:
    review_guard_text = read_text(".github/agents/internal-review-guard.agent.md")
    optional_support = review_guard_text.split("## Optional Support Skills", maxsplit=1)[1]
    optional_support = optional_support.split("## Core Rules", maxsplit=1)[0]

    assert not Path(".github/skills/internal-security-review").exists()
    assert "internal-security-review" not in optional_support
    assert "Treat `internal-security-review` as unavailable until promoted" in review_guard_text


def test_plan_completion_audit_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-systems-review/references/plan-completion-audit.md",
        (
            "`DONE`",
            "`PARTIAL`",
            "`NOT_DONE`",
            "`CHANGED`",
            "`UNVERIFIABLE`",
            "Verification Classes",
            "Output Table Template",
        ),
    )


def test_scope_drift_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-systems-review/references/scope-drift.md",
        (
            "`ON_SCOPE`",
            "`EXPANDED`",
            "`REDUCED`",
            "`DRIFTED`",
            "Declared intent",
            "Observed deliverable",
        ),
    )


def test_scope_challenge_gate_reference_exists() -> None:
    text = read_text(
        ".github/skills/internal-writing-plans/references/scope-challenge.md"
    ).lower()

    for expected in ("target", "anti-scope", "owner", "validator", "stop conditions"):
        assert expected in text


def test_review_lenses_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-systems-review/references/review-lenses.md",
        (
            "## Always-on Lenses",
            "## Cross-cutting Lenses",
            "## Stack-specific Lenses",
            "Trigger",
            "Owner skill",
            "`speculative`",
            "`plausible`",
            "`likely`",
            "`verified`",
        ),
    )


def test_completion_report_states_present() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/completion-report.md",
        (
            "`SHIPPED`",
            "`APPLIED_UNVERIFIED`",
            "`PARTIAL`",
            "`BLOCKED`",
            "`ROLLED_BACK`",
            "Review Tiers",
        ),
    )


def test_resume_protocol_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/resume-protocol.md",
        ("Verify-first Sequence", "`done-*`", "`git diff`", "validators", "Status Report Template"),
    )


def test_audit_dispatch_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-systems-review/references/audit-dispatch.md",
        ("More than 6 numbered plan files", "400 changed diff lines", "Typed findings", "spot-check"),
    )


def test_decision_brief_template_referenced() -> None:
    assert "references/decision-brief.md" in read_text(
        ".github/skills/internal-agent-support-next-step/SKILL.md"
    )
    assert_contains_all(
        ".github/skills/internal-agent-support-next-step/references/decision-brief.md",
        (
            "Target state",
            "Anti-scope",
            "Suggested owner",
            "Evidence source",
            "Validation path",
            "Known risks",
            "Stop conditions",
        ),
    )


def test_lessons_learned_is_not_workflow_contract_owner() -> None:
    lessons_text = read_text("LESSONS_LEARNED.md")
    checklist_text = read_text("tmp/superpowers/workflow-first-followup/promotion-checklist.md")

    assert "Plan Completion Audit |" not in lessons_text
    assert "No new `LESSONS_LEARNED.md` row is added by default" in checklist_text
