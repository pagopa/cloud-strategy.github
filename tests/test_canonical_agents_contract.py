from __future__ import annotations

import re
from pathlib import Path

import yaml

CANONICAL_AGENTS = {
    "internal-gateway-idea-brainstorming": ".github/agents/internal-gateway-idea-brainstorming.agent.md",
    "internal-gateway-operational-flow": ".github/agents/internal-gateway-operational-flow.agent.md",
    "internal-gateway-critical-master": ".github/agents/internal-gateway-critical-master.agent.md",
    "internal-gateway-simple-task": ".github/agents/internal-gateway-simple-task.agent.md",
}

OLD_CROSS_LANE_ENGINE = "internal-agent-" + "cross-lane-engine"

LEGACY_AGENT_HEADINGS = (
    "## Mandatory Engine Skills",
    "## Optional Support Skills",
    "## Preferred/Optional Skills",
    "## Skill Usage Contract",
)

EXPECTED_CORE_SKILLS = {
    "internal-gateway-idea-brainstorming": "internal-gateway-idea-brainstorming",
    "internal-gateway-operational-flow": "internal-gateway-operational-flow",
    "internal-gateway-critical-master": "internal-gateway-critical-master",
    "internal-gateway-simple-task": "internal-gateway-simple-task",
}

EXPECTED_HANDOFF_LABELS = {
    "internal-gateway-idea-brainstorming": [
        "Next step: Use simple fast path",
        "Next step: Continue through staged operational flow",
        "Next step: Pressure-test decision",
    ],
    "internal-gateway-operational-flow": [
        "Next step: Pressure-test decision",
        "Next action: Use simple fast path",
        "Next step: Explore idea definition",
    ],
    "internal-gateway-critical-master": [
        "Next step: Continue through staged flow",
        "Next action: Use simple fast path",
        "Next step: Reopen idea definition",
    ],
    "internal-gateway-simple-task": [
        "Next step: Use staged operational flow",
        "Next step: Pressure-test task",
        "Next step: Explore idea definition",
    ],
}

EXPECTED_HANDOFF_TARGETS = {
    "internal-gateway-idea-brainstorming": [
        "internal-gateway-simple-task",
        "internal-gateway-operational-flow",
        "internal-gateway-critical-master",
    ],
    "internal-gateway-operational-flow": [
        "internal-gateway-critical-master",
        "internal-gateway-simple-task",
        "internal-gateway-idea-brainstorming",
    ],
    "internal-gateway-critical-master": [
        "internal-gateway-operational-flow",
        "internal-gateway-simple-task",
        "internal-gateway-idea-brainstorming",
    ],
    "internal-gateway-simple-task": [
        "internal-gateway-operational-flow",
        "internal-gateway-critical-master",
        "internal-gateway-idea-brainstorming",
    ],
}

EXPECTED_AGENT_TOOLS = {
    "internal-gateway-idea-brainstorming": ["read", "edit", "search", "execute", "web"],
    "internal-gateway-operational-flow": ["read", "edit", "search", "execute", "web"],
    "internal-gateway-critical-master": ["read", "search"],
    "internal-gateway-simple-task": ["read", "edit", "search", "execute", "web"],
}

EXPECTED_CRITICAL_OUTCOMES = (
    "reformulate-plan",
    "de-escalate-to-simple",
    "execute-clear-next-step",
    "review-evidence",
    "continue-critical",
    "accept-with-risk",
)

EXPECTED_OPERATIONAL_ENTRYPOINTS = (
    "full-cycle",
    "define-first",
    "plan-only",
    "apply-plan",
    "review",
    "mode-explicit",
)

EXPECTED_GRILL_ME_GATE_STATES = (
    "grill-me required",
    "grill-me satisfied",
)

SIMPLE_GATEWAY_SKILL = ".github/skills/internal-gateway-simple-task/SKILL.md"
SIMPLE_GATEWAY_SUPPORT_ROUTING = (
    ".github/skills/internal-gateway-simple-task/references/support-routing.md"
)
SIMPLE_GATEWAY_CLARIFICATION_GATE = (
    ".github/skills/internal-gateway-simple-task/references/clarification-gate.md"
)
EXPECTED_SIMPLE_CLAIM_GATE_OWNERS = [
    "internal-debugging",
    "internal-tdd",
    "internal-performance-optimization",
    "internal-github-pr",
    "internal-code-review",
    "internal-high-level-review",
    "superpowers-verification-before-completion",
]


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    frontmatter_text = text.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter_text)


def read_body(relative_path: str) -> str:
    text = Path(relative_path).read_text(encoding="utf-8")
    return text.split("---\n", 2)[2]


def retired_mattpocock_ids() -> tuple[str, ...]:
    return tuple(
        f"mattpocock-{suffix}"
        for suffix in (
            "diagnose",
            "tdd",
            "improve-codebase-architecture",
            "zoom-out",
            "grill-with-docs",
            "setup-matt-pocock-skills",
        )
    )


def section_between(body: str, heading: str) -> str:
    section = body.split(heading, 1)[1]
    return section.split("\n## ", 1)[0]


def referenced_skills_from_skill(skill_text: str) -> list[str]:
    section = section_between(skill_text, "## Referenced skills")
    return re.findall(r"^- `([^`]+)`: ", section, flags=re.MULTILINE)


def claim_gate_owners_from_skill(skill_text: str) -> list[str]:
    section = section_between(skill_text, "## Claim Gates")
    return re.findall(r"^- Load `([^`]+)` before", section, flags=re.MULTILINE)


def claim_gate_owners_from_reference(reference_text: str) -> list[str]:
    section = section_between(reference_text, "## Claim Gates")
    owners: list[str] = []

    for line in section.splitlines():
        if not line.startswith("| "):
            continue

        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue

        owner = cells[1]
        if owner.startswith("`") and owner.endswith("`"):
            owners.append(owner.strip("`"))

    return owners


def core_skill(relative_path: str) -> str:
    body = read_body(relative_path)
    section = section_between(body, "## Core Skill")
    matches = re.findall(r"^- `([^`]+)`", section, flags=re.MULTILINE)

    assert len(matches) == 1
    return matches[0]


def assert_no_legacy_agent_headings(body: str) -> None:
    for heading in LEGACY_AGENT_HEADINGS:
        assert heading not in body


def assert_inline_code_tokens(text: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        assert f"`{token}`" in text


def assert_normalized_snippet(text: str, snippet: str) -> None:
    assert " ".join(snippet.split()) in " ".join(text.split())


def test_canonical_agents_keep_required_frontmatter_and_core_skill_contracts() -> None:
    for agent_name, relative_path in CANONICAL_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        body = read_body(relative_path)

        assert frontmatter["name"] == agent_name
        assert frontmatter["description"].startswith("Use this agent when")
        assert frontmatter.get("tools") == EXPECTED_AGENT_TOOLS[agent_name]
        assert frontmatter.get("disable-model-invocation") is True
        assert "agent" not in frontmatter.get("tools", [])
        assert frontmatter.get("agents") in (None, [])
        assert "## Core Skill" in body
        assert "## Output Expectations" in body
        assert_no_legacy_agent_headings(body)


def test_canonical_agents_keep_expected_core_skill_assignments() -> None:
    for agent_name, expected_skill in EXPECTED_CORE_SKILLS.items():
        relative_path = CANONICAL_AGENTS[agent_name]

        assert core_skill(relative_path) == expected_skill
        assert Path(f".github/skills/{expected_skill}/SKILL.md").exists()


def test_canonical_agents_expose_manual_next_step_handoffs() -> None:
    for agent_name, relative_path in CANONICAL_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        handoffs = frontmatter.get("handoffs")

        assert isinstance(handoffs, list)
        assert [handoff["label"] for handoff in handoffs] == EXPECTED_HANDOFF_LABELS[
            agent_name
        ]
        assert [handoff["agent"] for handoff in handoffs] == EXPECTED_HANDOFF_TARGETS[
            agent_name
        ]
        assert all(handoff.get("send") is False for handoff in handoffs)
        assert all(handoff["agent"] in CANONICAL_AGENTS for handoff in handoffs)
        assert all(isinstance(handoff.get("prompt"), str) for handoff in handoffs)


# Deleted deprecated compatibility wrappers tests
def test_operational_flow_wrapper_reports_completion_checks() -> None:
    body = read_body(CANONICAL_AGENTS["internal-gateway-operational-flow"])

    assert "State and Continuation" in body
    assert "User action required" in body
    assert "`Check 1`, `Check 2`, and `Check 3` evidence" in body
    assert "Source-item coverage against observed diff" in body
    assert "workflow-defect" in body
    assert "Next-step package" in body or "next-step package" in body


def test_operational_flow_gate_zero_projection_stays_aligned() -> None:
    skill_text = read_body(".github/skills/internal-gateway-operational-flow/SKILL.md")
    wrapper_text = read_body(CANONICAL_AGENTS["internal-gateway-operational-flow"])
    wrapper_alignment_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")
    gate_protocol_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/gate-0-protocol.md"
    ).read_text(encoding="utf-8")
    workflow_maps_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/workflow-maps.md"
    ).read_text(encoding="utf-8")

    assert "## Gate 0" in skill_text
    assert "Gate 0 is the pre-`plan` `define` gate" in skill_text
    assert "phase transition" in skill_text
    assert "request-change realignment" in skill_text
    assert "close only after a user closure signal" in skill_text
    assert_normalized_snippet(
        skill_text,
        "closing Gate 0 does not change the active phase",
    )
    assert (
        "wait for" in skill_text
        and "explicit" in skill_text
        and "planning request" in skill_text
    )
    assert "Direct `execute` is the only automatic Gate 0 exception" in skill_text
    assert "visible define pre-start gate before retained-plan execution" in skill_text
    assert "Gate 0" in wrapper_text
    assert "Gate 0 support for every non-`execute`" in wrapper_alignment_text
    assert "Restart Gate 0 before continuing" in wrapper_alignment_text
    assert "## Phase Transition Authorization" in gate_protocol_text
    assert "Closing Gate 0 changes the gate status only" in gate_protocol_text
    assert (
        "A valid transition request must directly ask for planning"
        in gate_protocol_text
    )
    assert "run the minimum evidence pass before Gate 0" in workflow_maps_text
    assert (
        "Do not restate the non-waiver or phase-transition details in maps."
        in workflow_maps_text
    )
    assert "Gate 0" in workflow_maps_text


def test_operational_flow_phase_local_contracts_and_templates_stay_defined() -> None:
    skill_text = read_body(".github/skills/internal-gateway-operational-flow/SKILL.md")
    mode_contracts_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/mode-contracts.md"
    ).read_text(encoding="utf-8")

    assert "## Phase State Machine" in skill_text
    assert (
        "| Phase | Enters when | Gate 0 | May do | Must not do | Delegates | Completion evidence |"
        in skill_text
    )
    assert "`define`" in skill_text
    assert "Define Check 1" in skill_text
    assert "## Phase-Local Output Template" in mode_contracts_text
    assert "State" in mode_contracts_text
    assert "Continuation" in mode_contracts_text
    assert "Gate 0 status" in mode_contracts_text
    assert "Definition Brief status" in mode_contracts_text
    assert "Lessons: none retained." in mode_contracts_text


def test_agents_readme_documents_ascii_workflows_and_usage_examples() -> None:
    readme = Path(".github/agents/README.md").read_text(encoding="utf-8")

    assert "## ASCII Workflow Map" in readme
    assert "These maps describe the expected human-visible flow" in readme
    assert "+-----------------------------+" in readme
    assert "internal-gateway-operational-flow" in readme
    assert "internal-gateway-critical-master" in readme
    assert "internal-gateway-simple-task" in readme
    assert "internal-gateway-idea-brainstorming" in readme
    assert "### 5. Sync Workflows" in readme
    assert "local-sync-external-resources" in readme
    assert "local-sync-global-copilot-configs-into-repo" in readme
    assert "## Use Examples" in readme
    assert "Apply the approved retained plan" in readme
    assert "Review these agent changes for routing regressions" in readme
    assert "Attack this plan before I apply it" in readme
    assert "If a request starts in the wrong lane" in readme


def test_skill_first_operational_core_exists_with_required_staged_entrypoints() -> None:
    skill_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    mode_contracts_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/mode-contracts.md"
    ).read_text(encoding="utf-8")
    workflow_maps_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/workflow-maps.md"
    ).read_text(encoding="utf-8")
    wrapper_alignment_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-gateway-operational-flow/agents/openai.yaml"
    ).read_text(encoding="utf-8")
    metadata = yaml.safe_load(metadata_text)
    interface = metadata["interface"]

    assert "name: internal-gateway-operational-flow" in skill_text
    assert "## Entry Points" in skill_text
    assert (
        "Load these skills by name only when the active phase requires them. "
        "This list is an index, not a bundle to preload." in skill_text
    )
    assert "Load `grill-me` when Gate 0 activates." in skill_text
    assert "Load `internal-agent-support-next-step` when a transition" in skill_text
    assert (
        "Load every other skill only when its phase, handoff, or failure condition becomes active."
        in skill_text
    )
    assert_inline_code_tokens(skill_text, EXPECTED_OPERATIONAL_ENTRYPOINTS)
    assert_inline_code_tokens(skill_text, EXPECTED_GRILL_ME_GATE_STATES)
    assert "entrypoint name alone does not skip" in skill_text
    assert "approved retained plan" in skill_text
    assert "Decision Brief" in skill_text
    assert "explicit checkpoint before moving" in skill_text
    assert (
        "Keep direct entry and manual transitions visible. "
        "Do not create hidden front-door routers or hidden peer dispatch."
        in skill_text
    )
    assert "Future Security Lens" in skill_text
    assert "## Completion Checks" in skill_text
    assert "`Check 1`" in skill_text
    assert "`Check 2`" in skill_text
    assert "`Check 3`" in skill_text
    assert "`Check 4`" in skill_text
    assert (
        "State:` and `Continuation:`" in skill_text
        or "`State:` and `Continuation:`" in skill_text
    )
    assert "## Output Calibration" in skill_text
    assert "Required output" in skill_text
    assert "Must not include" in skill_text
    assert "Lessons" in skill_text
    assert "`plan`" in mode_contracts_text
    assert "`execute`" in mode_contracts_text
    assert "`review`" in mode_contracts_text
    assert "`apply-plan`" in mode_contracts_text
    assert "CLI or plugin runtime" in workflow_maps_text
    assert "Apply/Execute Plan" in workflow_maps_text
    assert "internal-gateway-operational-flow" in wrapper_alignment_text
    assert not Path(
        ".github/skills/internal-gateway-operational-flow/references/imported-support-routing.md"
    ).exists()
    assert "## Imported Support" in wrapper_alignment_text
    assert "mattpocock-caveman" in wrapper_alignment_text
    assert "mattpocock-zoom-out" not in wrapper_alignment_text
    assert "## Future Security Lens" in wrapper_alignment_text
    assert "internal-debugging" in mode_contracts_text
    assert "internal-tdd" in mode_contracts_text
    assert "internal-performance-optimization" in mode_contracts_text
    for retired_id in retired_mattpocock_ids():
        assert retired_id not in wrapper_alignment_text
    assert interface["display_name"] == "Internal Gateway Operational Flow"
    assert "workflow" in interface["short_description"]
    assert "$internal-gateway-operational-flow" in interface["default_prompt"]
    assert "state" in interface["default_prompt"].lower()
    assert "continuation" in interface["default_prompt"].lower()
    assert "stay in define" in interface["default_prompt"].lower()

    operational_frontmatter = load_frontmatter(
        CANONICAL_AGENTS["internal-gateway-operational-flow"]
    )
    operational_body = read_body(CANONICAL_AGENTS["internal-gateway-operational-flow"])
    assert (
        "define, plan, execute, apply-plan, review"
        in operational_frontmatter["description"]
    )
    assert "multiple credible paths" in skill_text
    assert "full-cycle" in operational_body


def test_operational_flow_referenced_skills_stay_live_and_one_per_bullet() -> None:
    skill_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    referenced_skills = referenced_skills_from_skill(skill_text)

    assert referenced_skills
    assert "internal-security-review" not in referenced_skills
    assert all("," not in skill_id for skill_id in referenced_skills)
    assert all(
        Path(f".github/skills/{skill_id}/SKILL.md").is_file()
        for skill_id in referenced_skills
    )


def test_operational_flow_readme_is_not_required_when_bundle_references_own_detail() -> (
    None
):
    assert not Path(
        ".github/skills/internal-gateway-operational-flow/README.md"
    ).exists()


def test_internal_contract_documents_gateway_wrapper_entrypoints() -> None:
    contract_text = Path("INTERNAL_CONTRACT.md").read_text(encoding="utf-8")

    assert (
        "`internal-gateway-idea-brainstorming`, `internal-gateway-operational-flow`, "
        "`internal-gateway-simple-task`, and `internal-gateway-critical-master` remain the current Copilot wrapper entrypoints"
        in contract_text
    )
    assert "fails safe to `internal-gateway-operational-flow`" in contract_text
    assert "internal-planning-leader` or the `plan` phase" not in contract_text


def test_gateway_wrapper_alignment_documents_active_gateway_wrappers() -> None:
    alignment_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")

    assert "## Wrapper Roles" in alignment_text
    assert "## Support Posture" in alignment_text
    for agent_name, expected_skill in EXPECTED_CORE_SKILLS.items():
        assert f"| `{agent_name}` | `{expected_skill}` |" in alignment_text
        assert core_skill(CANONICAL_AGENTS[agent_name]) == expected_skill


def test_gateway_catalog_fast_path_stays_local_before_optional_support() -> None:
    skill_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    workflow_maps_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/workflow-maps.md"
    ).read_text(encoding="utf-8")

    assert "`internal-gateway-simple-task` vs `execute` vs `plan` triage" in skill_text
    assert "one owner file plus one nearby validator" in skill_text
    assert "### Catalog Fast Path" in workflow_maps_text
    assert "`make catalog-fast-check`" in workflow_maps_text
    assert "`make github-catalog-validation` once at the end" in workflow_maps_text
    assert "`CATALOG_FAST_INCLUDE_TOKEN_RISKS=1`" in workflow_maps_text


def test_critical_master_skill_exists_with_challenge_boundary() -> None:
    skill_text = Path(
        ".github/skills/internal-gateway-critical-master/SKILL.md"
    ).read_text(encoding="utf-8")
    agent_body = read_body(CANONICAL_AGENTS["internal-gateway-critical-master"])
    lenses_text = Path(
        ".github/skills/internal-gateway-critical-master/references/challenge-lenses.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-gateway-critical-master/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "name: internal-gateway-critical-master" in skill_text
    assert "Do not implement, routine-review, or finalize the plan" in skill_text
    assert_normalized_snippet(
        skill_text,
        "validate a repository-wide prompt, skill, agent, workflow, or policy change before editing",
    )
    assert_normalized_snippet(
        skill_text,
        "record the strongest objection and the mitigation or condition required before switching the work back to planning or delivery",
    )
    assert "## Outcome Routing" in skill_text
    assert_inline_code_tokens(skill_text, EXPECTED_CRITICAL_OUTCOMES)
    assert_normalized_snippet(
        agent_body,
        "validate a repository-wide prompt, skill, agent, workflow, or policy change before editing",
    )
    assert "Final Consistency Gate" in lenses_text
    assert "Scope compression" in lenses_text
    assert "Explicit outcome" in lenses_text
    assert (
        "Mitigation or condition required before planning or delivery resumes."
        in lenses_text
    )
    assert_inline_code_tokens(lenses_text, EXPECTED_CRITICAL_OUTCOMES)
    assert "$internal-gateway-critical-master" in metadata_text


def test_simple_gateway_covers_fast_path_and_misuse_boundaries() -> None:
    skill_text = Path(SIMPLE_GATEWAY_SKILL).read_text(encoding="utf-8")
    simple_lanes_text = Path(
        ".github/skills/internal-gateway-simple-task/references/simple-lanes.md"
    ).read_text(encoding="utf-8")
    clarification_gate_text = Path(SIMPLE_GATEWAY_CLARIFICATION_GATE).read_text(
        encoding="utf-8"
    )
    support_routing_text = Path(SIMPLE_GATEWAY_SUPPORT_ROUTING).read_text(
        encoding="utf-8"
    )
    metadata_text = Path(
        ".github/skills/internal-gateway-simple-task/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "single-lane and single-phase by design" in skill_text
    assert "already-decided contract" in skill_text
    assert "same already-decided pattern and share one validation path" in skill_text
    assert "## Escalation Triggers" in skill_text
    assert "durable lesson candidate" in skill_text
    assert "internal-lesson-codification" in skill_text
    assert "references/clarification-gate.md" in skill_text
    assert "one focused block of clarification" in skill_text
    assert (
        "relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`"
        in skill_text
    )
    assert (
        "Simple mode allows at most one focused `grill-me` block."
        in clarification_gate_text
    )
    assert "clarify-first workflow" in clarification_gate_text
    assert "`support-loaded`" in simple_lanes_text
    assert "`files-touched`" in simple_lanes_text
    assert "matching authoring owner" in support_routing_text
    assert (
        "Inspect the owning bundle and nearest contract tests" in support_routing_text
    )
    assert "validator passes" in support_routing_text
    assert "auth, config, secrets, tenant data" in support_routing_text
    assert "$internal-gateway-simple-task" in metadata_text


def test_simple_gateway_referenced_skills_stay_local_and_live() -> None:
    skill_text = Path(SIMPLE_GATEWAY_SKILL).read_text(encoding="utf-8")
    referenced_skills = referenced_skills_from_skill(skill_text)

    assert re.search(
        r"# Internal Gateway Simple Task\s+## Referenced skills", skill_text
    )
    assert "owner index, not a preload bundle" in skill_text
    assert referenced_skills
    assert all(
        Path(f".github/skills/{skill_id}/SKILL.md").is_file()
        for skill_id in referenced_skills
    )


def test_simple_gateway_claim_gate_contract_stays_in_core_skill() -> None:
    skill_text = Path(SIMPLE_GATEWAY_SKILL).read_text(encoding="utf-8")
    clarification_gate_text = Path(SIMPLE_GATEWAY_CLARIFICATION_GATE).read_text(
        encoding="utf-8"
    )
    support_routing_text = Path(SIMPLE_GATEWAY_SUPPORT_ROUTING).read_text(
        encoding="utf-8"
    )

    assert "## grill-me boundary" in skill_text
    assert "canonical simple-mode boundary" in skill_text
    assert "single source of truth for claim-gate" in skill_text
    assert (
        "Simple mode allows at most one focused `grill-me` block."
        in clarification_gate_text
    )
    assert "`grill-me` in simple mode must not decide:" in clarification_gate_text
    assert_normalized_snippet(
        support_routing_text,
        "single source of truth for claim-gate ownership in simple mode",
    )
    assert (
        claim_gate_owners_from_reference(support_routing_text)
        == EXPECTED_SIMPLE_CLAIM_GATE_OWNERS
    )


def test_prompt_examples_reference_live_gateway_skills_and_agents() -> None:
    prompt_paths = [
        Path(".github/prompts/internal-architecture-md-creator.prompt.md"),
        Path(".github/prompts/internal-mega-review.prompt.md"),
        Path(".github/prompts/internal-review-ai-resources.prompt.md"),
        Path(".github/prompts/internal-sync-plan.prompt.md"),
    ]
    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in prompt_paths)
    live_prompt_paths = {
        path.as_posix() for path in Path(".github/prompts").glob("*.prompt.md")
    }

    assert live_prompt_paths == {path.as_posix() for path in prompt_paths}
    assert 'agent: "agent"' not in combined_text
    assert "internal-gateway-operational-flow.agent.md" in combined_text
    assert "internal-gateway-operational-flow/SKILL.md" in combined_text
    assert "local-sync-global-copilot-configs-into-repo.agent.md" in combined_text
    assert "local-agent-sync-global-copilot-configs-into-repo/SKILL.md" in combined_text


def test_gateway_support_prompts_are_retired_from_the_live_catalog() -> None:
    retired_paths = (
        ".github/prompts/internal-agent-plan-next-step.prompt.md",
        ".github/prompts/internal-agent-pressure-test-plan.prompt.md",
        ".github/prompts/internal-agent-review-next-actions.prompt.md",
        ".github/prompts/internal-execute-plan.prompt.md",
    )

    assert all(not Path(relative_path).exists() for relative_path in retired_paths)


def test_grill_me_is_conditional_plan_support_not_renamed_or_copied() -> None:
    grill_me_text = Path(".github/skills/grill-me/SKILL.md").read_text(encoding="utf-8")
    operational_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-gateway-operational-flow/agents/openai.yaml"
    ).read_text(encoding="utf-8")
    wrapper_alignment_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")

    assert Path(".github/skills/grill-me/SKILL.md").exists()
    assert not Path(".github/skills/mattpocock-grill-me/SKILL.md").exists()
    assert "confirm context before starting" in grill_me_text
    assert "pre-plan or pre-start gate" not in grill_me_text
    assert "grill-me required" not in grill_me_text
    assert "Gate 0" in operational_text
    assert "grill-me" in operational_text
    assert "grill-me" in wrapper_alignment_text
    assert "Direct `execute` is the only automatic Gate 0 exception" in operational_text
    assert (
        "approved `apply-plan` still starts with the visible pre-start gate"
        in metadata_text.lower()
    )
    assert "Restart Gate 0 before continuing" in wrapper_alignment_text
    assert "non-trivial" in operational_text and "retained plan" in operational_text
    assert "Do not replace those decisions with silent assumptions" in operational_text
    assert "close only after a user closure signal" in operational_text.lower()


def test_gateway_support_uses_internal_owners_after_extraction() -> None:
    wrapper_alignment_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")
    systems_review_text = Path(
        ".github/skills/internal-high-level-review/SKILL.md"
    ).read_text(encoding="utf-8")

    assert "Failure diagnosis belongs to `internal-debugging`" in wrapper_alignment_text
    assert "Test-first delivery belongs to `internal-tdd`" in wrapper_alignment_text
    assert (
        "Code defect review belongs to `internal-code-review`" in wrapper_alignment_text
    )
    assert "internal-high-level-review" in wrapper_alignment_text
    assert "## Orientation Map Lens" in systems_review_text
    assert "## Orientation Output" in systems_review_text
    assert "Module map" in systems_review_text
    for retired_id in retired_mattpocock_ids():
        assert retired_id not in wrapper_alignment_text


def test_internal_debugging_and_tdd_skills_capture_extracted_workflows() -> None:
    debugging_text = Path(".github/skills/internal-debugging/SKILL.md").read_text(
        encoding="utf-8"
    )
    debugging_metadata = Path(
        ".github/skills/internal-debugging/agents/openai.yaml"
    ).read_text(encoding="utf-8")
    tdd_text = Path(".github/skills/internal-tdd/SKILL.md").read_text(encoding="utf-8")
    tdd_metadata = Path(".github/skills/internal-tdd/agents/openai.yaml").read_text(
        encoding="utf-8"
    )

    assert "name: internal-debugging" in debugging_text
    assert "Build the fastest credible pass/fail loop" in debugging_text
    assert "Rank three to five falsifiable hypotheses" in debugging_text
    assert "tag it with a unique `DEBUG-` marker" in debugging_text
    assert "regression test at the correct seam" in debugging_text
    assert "$internal-debugging" in debugging_metadata

    assert "name: internal-tdd" in tdd_text
    assert "red-green-refactor" in tdd_text
    assert "public interface" in tdd_text
    assert "Do not force TDD onto Markdown-only" in tdd_text
    assert "$internal-tdd" in tdd_metadata


def test_old_cross_lane_engine_is_not_live_catalog_contract() -> None:
    assert not Path(f".github/skills/{OLD_CROSS_LANE_ENGINE}/SKILL.md").exists()

    for relative_path in CANONICAL_AGENTS.values():
        assert OLD_CROSS_LANE_ENGINE not in read_body(relative_path)


def test_operational_flow_pre_plan_critical_pass_and_review_gate_stay_present() -> None:
    skill_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    gate_protocol_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/gate-0-protocol.md"
    ).read_text(encoding="utf-8")

    assert "### Pre-Plan Critical Pass" in skill_text
    assert "pre-plan critical: confident" in skill_text
    assert "pre-plan critical: reopen" in skill_text
    assert_normalized_snippet(
        skill_text,
        "automatically load `internal-gateway-critical-master` and run a critical challenge against the Definition Brief",
    )
    assert "Do not skip it" in skill_text
    assert_normalized_snippet(
        skill_text,
        "plan output remains blocked until the cycle resolves",
    )
    assert "### Review Gate" in skill_text
    assert "review gate: satisfied" in skill_text
    assert "review gate: reopen" in skill_text
    assert_normalized_snippet(
        skill_text,
        "do not emit the final review verdict while the gate is `reopen`",
    )
    assert "Pre-Plan Critical Pass" in gate_protocol_text
    assert "pre-plan critical: confident" in gate_protocol_text
    assert "pre-plan critical: reopen" in gate_protocol_text


def test_entrypoint_aliases_reference_exists_and_is_linked() -> None:
    aliases_path = Path(
        ".github/skills/internal-gateway-operational-flow/references/entrypoint-aliases.md"
    )
    assert aliases_path.exists()

    aliases_text = aliases_path.read_text(encoding="utf-8")
    assert "## Alias index" in aliases_text
    assert "| `full-cycle` |" in aliases_text
    assert "| `define-first` |" in aliases_text
    assert "| `plan-only` |" in aliases_text
    assert "| `apply-plan` |" in aliases_text
    assert "| `review` |" in aliases_text

    skill_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    assert "references/entrypoint-aliases.md" in skill_text
