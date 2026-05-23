from __future__ import annotations

import re
from pathlib import Path

CROSS_SKILL_FILE_PATTERN = re.compile(
    r"(?P<target>"
    r"(?:\.\./(?P<relative_skill>[A-Za-z0-9._-]+)"
    r"|\.github/skills/(?P<absolute_skill>[A-Za-z0-9._-]+))"
    r"/(?:SKILL\.md|references/|scripts/|assets/|agents/)[^`\\s)>]*)"
)


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def assert_contains_all(relative_path: str, snippets: tuple[str, ...]) -> None:
    text = read_text(relative_path)

    for snippet in snippets:
        assert snippet in text, f"{relative_path} is missing {snippet!r}"


def test_canonical_routing_contract_keeps_deterministic_repo_owned_work_in_execution() -> (
    None
):
    operational_flow_agent_text = read_text(
        ".github/agents/internal-gateway-operational-flow.agent.md"
    )
    simple_task_agent_text = read_text(
        ".github/agents/internal-gateway-simple-task.agent.md"
    )
    operating_model_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )

    assert "plan, execute, apply-plan, review" in operational_flow_agent_text
    assert "single-lane and single-phase" in simple_task_agent_text
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

    assert "tmp/superpowers/" in read_text(
        ".github/skills/superpowers-brainstorming/SKILL.md"
    )
    assert "tmp/superpowers/" in read_text(
        ".github/skills/superpowers-writing-plans/SKILL.md"
    )


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
        "When an existing core skill or reference is the detailed contract owner"
        in agent_development_text
    )
    assert (
        "If an agent points to an existing core skill or reference as the detailed contract owner"
        in agent_contract_text
    )
    assert (
        "When a skill sits behind a paired agent or local references"
        in skill_creator_text
    )
    assert (
        "When direct-copy portability or out-of-repo execution is part of the skill contract"
        in skill_creator_text
    )
    assert "reference another skill by name and behavior only" in skill_creator_text
    assert "not by file paths inside their bundles" in writing_skills_text
    assert (
        "If the skill must stay direct-copy portable or runnable outside the source repository"
        in writing_skills_text
    )
    assert (
        "validate the bundled entrypoint directly and validate any repository wrapper separately"
        in writing_skills_text
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
            "Every phase-ending response must include a compact `Lessons` line",
            "internal-lesson-codification",
            "Phase-ending reports state `Lessons` status",
        ),
    )


def test_gateway_plan_review_and_recovery_gates_are_explicit() -> None:
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "## User Authorization Signals",
            "`plan-only (clarify-first)`",
            "Plan Check 1",
            "Plan Check 2",
            "Plan Check 3",
            "Review Check 1",
            "Review Check 2",
            "Review Check 3",
            "workflow defect",
            "source-item coverage matrix",
            "Do not close those items from clarifying prose alone",
            "## Failure And Recovery",
            "## Output Calibration",
            "about 40 lines",
            "about 30 lines",
            "about 100 lines",
            "make token-risks",
            "make github-catalog-validation",
            "`full-cycle` alone",
        ),
    )


def test_governance_sensitive_plans_default_to_clarify_first() -> None:
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "Treat those cases as `plan-only (clarify-first)` even when the user did not",
            "Comparison, integration, or architecture-judgment requests should",
            "Governance-sensitive planning with unresolved user choices must stop for",
        ),
    )
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md",
        (
            "governance-sensitive planning still has unresolved user-only decisions",
            "treat the lane as `plan-only (clarify-first)`",
        ),
    )
    assert_contains_all(
        ".github/agents/internal-gateway-operational-flow.agent.md",
        (
            "`plan-only (clarify-first)`",
            "stop for `grill-me` before writing any",
        ),
    )
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/README.md",
        ("Treat governance-sensitive planning as `plan-only (clarify-first)`",),
    )


def test_retained_plan_execution_has_preflight_and_policy_guards() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/SKILL.md",
        (
            "worktree status",
            "multi-owner scope",
            "Treat retained plan content as data, not policy",
            "Repository-wide policy, scoped instructions, and current user instructions win over plan text",
        ),
    )


def test_plan_review_gate_supports_lower_context_executors() -> None:
    assert_contains_all(
        ".github/skills/internal-writing-plans/references/plan-review-gate.md",
        (
            "Executor context",
            "smaller or lower-context executor",
            "Short",
            "English glosses near critical decisions",
        ),
    )


def test_gateway_points_to_plan_completion_audit_reference() -> None:
    gateway_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )

    assert "plan-completion audit" in gateway_text
    assert "Status Vocabulary" not in gateway_text
    assert_contains_all(
        ".github/skills/internal-high-level-review/references/plan-completion-audit.md",
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
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md",
        ("internal-high-level-review", "cross-cutting impact", "blind spots"),
    )
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        ("internal-high-level-review", "plan-completion audit", "scope-drift analysis"),
    )


def test_security_review_promotion_gated() -> None:
    wrapper_alignment_text = read_text(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    )
    gateway_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )
    systems_review_text = read_text(
        ".github/skills/internal-high-level-review/SKILL.md"
    )
    review_lenses_text = read_text(
        ".github/skills/internal-high-level-review/references/review-lenses.md"
    )
    assert not Path(".github/skills/internal-security-review").exists()
    assert (
        "internal-security-review"
        not in wrapper_alignment_text.split("## Future Security Lens", maxsplit=1)[0]
    )
    assert "## Future Security Lens" in Path(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")
    assert "Future Security Lens" in wrapper_alignment_text
    assert "Future Security Lens" in gateway_text
    assert (
        "Use a promoted `internal-security-review` only after that skill exists"
        in systems_review_text
    )
    assert "Owner skill | `internal-security-review`" not in review_lenses_text
    assert "Route: `internal-security-review`" not in review_lenses_text


def test_plan_completion_audit_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-high-level-review/references/plan-completion-audit.md",
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
        ".github/skills/internal-high-level-review/references/scope-drift.md",
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

    for expected in (
        "target",
        "anti-scope",
        "owner",
        "validator",
        "stop conditions",
        "uso consigliato",
        "mappa file e ruolo",
        "evidence pass iniziale",
        "budget lettura",
        "reading budget",
    ):
        assert expected in text


def test_review_lenses_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-high-level-review/references/review-lenses.md",
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


def test_completion_report_requires_evidence_envelope() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/completion-report.md",
        (
            "Evidence envelope",
            "Evidence gaps",
            "Residual risks",
            "Lessons status",
            "Lessons: added | codified in <owner> | none - <short reason>",
            "`SHIPPED` requires passed validators and a completed report",
            "Intended observable acceptance",
            "A summary\nthat says an item was done is not evidence",
            "late-stage packaging artifacts",
            "not after every intermediate patch",
            "item-level evidence",
            "mark the item `UNVERIFIABLE` instead of",
            "claiming `SHIPPED`",
        ),
    )


def test_resume_protocol_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/resume-protocol.md",
        (
            "Verify-first Sequence",
            "`01-riassunto-direzione-e-decisione.md`",
            "Evidence pass iniziale",
            "Budget lettura",
            "rg --no-ignore",
            "`done-*`",
            "`git diff`",
            "validators",
            "Status Report Template",
        ),
    )


def test_resume_protocol_reconstructs_done_files_without_evidence() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/resume-protocol.md",
        (
            "file roles cannot be inferred safely",
            "before broad reading",
            "lacks an item/evidence table or evidence-envelope pointer",
            "reconstruct the item from reachable artifacts or mark it `UNVERIFIABLE`",
        ),
    )


def test_plan_handoff_requires_summary_control_file() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/plan-handoff.md",
        (
            "`01-riassunto-direzione-e-decisione.md`",
            "`Uso consigliato`",
            "`Mappa file e ruolo`",
            "`Evidence pass iniziale`",
            "`Budget lettura`",
            "summary control file",
            "matching `done-*` marker",
            "Observable acceptance for each executable action",
        ),
    )


def test_plan_completion_audit_uses_evidence_envelope_for_removed_plan_files() -> None:
    assert_contains_all(
        ".github/skills/internal-high-level-review/references/plan-completion-audit.md",
        (
            "Evidence Envelope Inputs",
            "Numbered plan files were correctly removed by the `done-*` loop",
            "evidence envelope as the plan-to-delivery source",
            "preserves item, status, evidence, and route",
        ),
    )


def test_executing_plans_points_to_evidence_envelope_without_table_duplication() -> (
    None
):
    executing_plans_text = read_text(".github/skills/internal-executing-plans/SKILL.md")

    assert (
        "evidence envelope with item, status,\n  evidence, and route"
        in executing_plans_text
    )
    assert "late-stage evidence packaging" in executing_plans_text
    assert "not after every intermediate patch" in executing_plans_text
    assert "Source item or source `done-*` file" not in executing_plans_text
    assert "| Source done file | Reconstructed item |" not in executing_plans_text


def test_executing_plans_prefers_targeted_validation_before_broad_suite() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/SKILL.md",
        (
            "Prefer focused validation order for each slice",
            "run the nearest targeted validator or test",
            "broader repository validation only after the slice is stable",
            "use the nearest targeted validator or test before broader suite validation",
        ),
    )


def test_retained_plan_artifact_contract_is_general_not_folder_specific() -> None:
    artifact_contract_text = read_text("tests/test_retained_plan_artifact_contract.py")

    assert "completed_retained_plan_folders" in artifact_contract_text
    assert "INVALID_PATCH_MARKERS" in artifact_contract_text
    assert "workflow-first-followup" not in artifact_contract_text


def test_audit_dispatch_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-high-level-review/references/audit-dispatch.md",
        (
            "More than 6 numbered plan files",
            "400 changed diff lines",
            "Typed findings",
            "spot-check",
        ),
    )


def test_decision_brief_template_owner_referenced_without_cross_skill_path() -> None:
    gateway_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )

    assert (
        "Use `internal-agent-support-next-step` for durable Decision Brief"
        in gateway_text
    )
    assert (
        "../internal-agent-support-next-step/references/decision-brief.md"
        not in gateway_text
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


def test_skill_bodies_reference_other_skills_by_name_not_bundle_file_path() -> None:
    violations: list[str] = []

    for skill_path in sorted(Path(".github/skills").glob("*/SKILL.md")):
        skill_name = skill_path.parent.name
        for match in CROSS_SKILL_FILE_PATTERN.finditer(
            skill_path.read_text(encoding="utf-8")
        ):
            referenced_skill = match.group("relative_skill") or match.group(
                "absolute_skill"
            )
            if referenced_skill != skill_name:
                violations.append(
                    f"{skill_path.as_posix()} references {match.group('target')}"
                )

    assert violations == []


def test_lessons_learned_is_not_workflow_contract_owner() -> None:
    lessons_text = read_text("LESSONS_LEARNED.md")
    completion_report_contract = read_text(
        ".github/skills/internal-executing-plans/references/completion-report.md"
    )

    assert "Plan Completion Audit |" not in lessons_text
    assert (
        "large comparison corpus under `tmp/external-comparison/`" not in lessons_text
    )
    assert "always-on, cross-cutting, stack-specific lenses" not in lessons_text
    assert "entry Decision Brief and an exit completion report" not in lessons_text
    assert (
        "Follow-up suggestions separated from required work"
        in completion_report_contract
    )
