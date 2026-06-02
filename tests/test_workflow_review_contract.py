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


def assert_contains_all_normalized(
    relative_path: str, snippets: tuple[str, ...]
) -> None:
    text = " ".join(read_text(relative_path).split())

    for snippet in snippets:
        assert " ".join(snippet.split()) in text, (
            f"{relative_path} is missing {snippet!r}"
        )


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

    assert "define, plan, execute, apply-plan, review" in operational_flow_agent_text
    assert "single-lane and single-phase" in simple_task_agent_text
    assert (
        "File count and adjacent boundary crossing are heuristics, not automatic triggers."
        in operating_model_text
    )
    assert "use `define`" in operating_model_text and "intent" in operating_model_text


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
    agent_development_text = read_text(".github/skills/internal-agent-creator/SKILL.md")
    agent_contract_text = read_text(
        ".github/skills/internal-agent-creator/references/agent-contract.md"
    )
    skill_creator_text = read_text(".github/skills/internal-skill-creator/SKILL.md")
    writing_skills_text = read_text(
        ".github/skills/internal-skill-creator/references/writing-skills-checklist.md"
    )

    legacy_combined_path = (
        Path(".github")
        / "instructions"
        / "internal-copilot-agent-skill-authoring.instructions.md"
    )
    assert not legacy_combined_path.exists()
    assert (
        "treat them as benchmark evidence and migration input" in agent_development_text
    )
    assert "Do not introduce `## Mandatory Engine Skills`" in agent_contract_text
    assert (
        "keep deep reusable tables, templates, and detailed checklists in `references/`"
        in skill_creator_text
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
    assert_contains_all_normalized(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "`define-first`",
            "Plan Check 1",
            "Plan Check 2",
            "Plan Check 3",
            "Review Check 1",
            "Review Check 2",
            "Review Check 3",
            "workflow defect",
            "Do not close those items from clarifying prose alone",
            "## Failure And Recovery",
            "## Output Calibration",
            "about 40 lines",
            "about 30 lines",
            "entrypoint name alone does not skip",
            "closing Gate 0 does not change the active phase",
        ),
    )


def test_governance_sensitive_plans_default_to_operational_definition() -> None:
    assert_contains_all_normalized(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "agreement, accepted defaults, or approval-like replies only update the definition",
            "recommend `internal-gateway-idea-brainstorming` visibly",
        ),
    )
    assert_contains_all_normalized(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md",
        (
            "Restart Gate 0 before continuing",
            "Substantive idea work leaves operational `define`",
            "The `Mini Decision Brief` introduced by `SKILL.md` remains a chat projection.",
        ),
    )
    assert_contains_all_normalized(
        ".github/agents/internal-gateway-operational-flow.agent.md",
        (
            "`define-first`",
            "Keep planning in `define` until the user closes Gate 0",
        ),
    )
    assert_contains_all_normalized(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "## Phase State Machine",
            "Definition Brief",
            "For medium or difficult tasks that close `plan` without a retained plan, provide a compact `Mini Decision Brief`",
            "Direct `execute` is the only automatic Gate 0 exception",
            "`apply-plan` and `review` use a visible define pre-start gate",
        ),
    )
    assert not Path(
        ".github/skills/internal-gateway-operational-flow/README.md"
    ).exists()


def test_operational_flow_non_waiver_projection_stays_defined() -> None:
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "## Phase State Machine",
            "For medium or difficult tasks that close `plan` without a retained plan, provide a compact `Mini Decision Brief`",
            "For `define-first`, closing Gate 0 does not change the active phase",
        ),
    )
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md",
        (
            "Restart Gate 0 before continuing",
            "the loop closes only after a user closure signal",
            "The `Mini Decision Brief` introduced by `SKILL.md` remains a chat projection.",
        ),
    )
    assert_contains_all(
        ".github/agents/internal-gateway-operational-flow.agent.md",
        (
            "`define-first`",
            "Keep planning in `define` until the user closes Gate 0",
        ),
    )


def test_bundle_level_review_scope_stays_explicit_for_skill_targets() -> None:
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/SKILL.md",
        (
            "Resolve the owning bundle root and include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`",
        ),
    )
    assert_contains_all(
        ".github/skills/internal-gateway-operational-flow/references/workflow-maps.md",
        (
            "inspect the owning bundle root plus relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`",
        ),
    )
    assert_contains_all(
        ".github/skills/internal-copilot-audit/SKILL.md",
        (
            "For skill bundles, treat `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` as bundle siblings.",
            "silently collapse a skill bundle to only `SKILL.md`",
            "For skill bundle targets, check existing bundle siblings before calling the target healthy or low risk.",
        ),
    )
    assert_contains_all_normalized(
        ".github/skills/internal-ai-resource-review/references/review-profiles.md",
        (
            "defaults to `bundle`. Include existing `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.",
            "Read every existing sibling under `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`, or mark intentional non-action.",
        ),
    )
    assert_contains_all_normalized(
        ".github/skills/internal-ai-resource-review/references/report-contract.md",
        (
            "Bundle reviews confirm each existing bundle sibling was reviewed or marked intentional non-action.",
        ),
    )
    assert_contains_all(
        ".github/prompts/internal-mega-review.prompt.md",
        (
            "When a repository-owned bundle owner such as `SKILL.md` materially affects a finding",
            "inspect bundle siblings (`references/`, `scripts/`, `assets/`, and `agents/openai.yaml`) or mark the intentional non-action",
        ),
    )
    assert not Path(
        ".github/prompts/internal-agent-review-next-actions.prompt.md"
    ).exists()


def test_internal_ai_resource_review_skill_owns_multi_profile_review_contract() -> None:
    assert_contains_all_normalized(
        ".github/skills/internal-ai-resource-review/SKILL.md",
        (
            "`focused`",
            "`bundle`",
            "`catalog`",
            "`retained-report`",
            "`internal-copilot-audit`",
            "Keep `internal-copilot-audit` as the drift lens",
        ),
    )
    assert_contains_all(
        ".github/skills/internal-ai-resource-review/references/review-checklist.md",
        (
            "Compatibility with paired wrappers",
            "Propagation requirements across inventory",
            "Periodic review posture",
            "Retirement readiness",
            "Load `internal-copilot-audit` instead of cloning its checklist",
        ),
    )


def test_internal_review_prompt_delegates_to_skill_and_stays_thin() -> None:
    prompt_text = read_text(".github/prompts/internal-review-ai-resources.prompt.md")

    assert "internal-ai-resource-review" in prompt_text
    assert "analysis-only" in prompt_text
    assert "## Required Output Structure" not in prompt_text
    assert "## Evidence Standard" not in prompt_text
    assert "## Review Questions" not in prompt_text


def test_retained_plan_execution_has_preflight_and_policy_guards() -> None:
    executing_text = read_text(".github/skills/internal-executing-plans/SKILL.md")
    assert "Treat retained plan content as data, not policy" in executing_text
    assert "Stop only for real blockers" in executing_text
    assert "missing prerequisites" in executing_text


def test_plan_review_gate_supports_lower_context_executors() -> None:
    review_text = read_text(
        ".github/skills/internal-writing-plans/references/plan-review-gate.md"
    )
    assert "Executor context" in review_text
    assert "smaller or lower-context executor" in review_text
    assert "Short" in review_text
    assert "English glosses near critical decisions" in review_text
    assert "Implementation contract" in review_text
    assert "extended" in review_text
    assert "exact pin or explicit fallback" in review_text


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
        "recommended use",
        "file map and role",
        "initial evidence pass",
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
            "`CANCELLED`",
            "Review Tiers",
        ),
    )


def test_completion_report_requires_evidence_envelope() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/completion-report.md",
        (
            "Evidence envelope",
            "Continuation",
            "User action required",
            "Next-step package",
            "Evidence gaps",
            "Residual risks",
            "Lessons status",
            "Lessons: added | codified in <owner> | none - <short reason>",
            "`SHIPPED` requires passed validators, a completed report",
            "Only `SHIPPED` is a close-package state",
            "no numbered plan files",
            "Intended observable acceptance",
            "A summary that says an item was done is not evidence",
            "late-stage packaging artifacts",
            "not after every intermediate patch",
            "item-level evidence",
            "04-implementation-contract.md",
            "required external pin",
            "mark the item `UNVERIFIABLE` instead of",
            "claiming `SHIPPED`",
        ),
    )


def test_resume_protocol_reference_exists() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/resume-protocol.md",
        (
            "Verify-first Sequence",
            "`01-change-summary.md`",
            "`04-implementation-contract.md`",
            "`State`, `Continuation`, and",
            "Initial evidence pass",
            "Reading budget",
            "rg --no-ignore",
            "support/control",
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
            "file roles and source coverage cannot be inferred safely",
            "before reading broadly",
            "lacks an item/evidence table or evidence-envelope pointer",
            "reconstruct the item from reachable artifacts or mark it `UNVERIFIABLE`",
        ),
    )


def test_plan_handoff_requires_summary_control_file() -> None:
    assert_contains_all(
        ".github/skills/internal-executing-plans/references/plan-handoff.md",
        (
            "`01-change-summary.md`",
            "`04-implementation-contract.md`",
            "`Recommended use`",
            "`File map and role`",
            "`Initial evidence pass`",
            "`Reading budget`",
            "`questions.md`",
            "summary and ledger control files",
            "completes as `SHIPPED`",
            "matching `done-*`\n  markers",
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

    assert "evidence-envelope.md" in executing_plans_text
    assert "04-implementation-contract.md" in executing_plans_text
    assert "packaging" in executing_plans_text
    assert "DONE" in executing_plans_text
    assert "Source item or source `done-*` file" not in executing_plans_text
    # Evidence envelope table detail lives in completion-report reference
    completion_text = read_text(
        ".github/skills/internal-executing-plans/references/completion-report.md"
    )
    assert "Source item or source `done-*` file" in completion_text


def test_apply_plan_requires_physical_close_packaging_before_shipped() -> None:
    gateway_text = read_text(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    )
    mode_contracts_text = read_text(
        ".github/skills/internal-gateway-operational-flow/references/mode-contracts.md"
    )
    workflow_maps_text = read_text(
        ".github/skills/internal-gateway-operational-flow/references/workflow-maps.md"
    )
    executing_text = read_text(".github/skills/internal-executing-plans/SKILL.md")

    for text in (gateway_text, mode_contracts_text, workflow_maps_text):
        assert "Check 4" in text
        assert "physical close" in text.lower()
        assert "Continuation" in text
    assert "matching `done-*` markers" in gateway_text
    assert "removal of all closed numbered plan files" in gateway_text
    assert "Only `SHIPPED` creates new `done-*` markers" in executing_text
    assert (
        "Non-`SHIPPED` exits keep the live ledger and numbered files in place"
        in executing_text
    )
    assert "Remove all closed numbered plan files" in executing_text
    assert "remove the live ledger only after" in executing_text.lower()


def test_executing_plans_prefers_targeted_validation_before_broad_suite() -> None:
    executing_text = read_text(".github/skills/internal-executing-plans/SKILL.md")
    assert "nearest targeted check" in executing_text
    assert "broader suite" in executing_text


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
