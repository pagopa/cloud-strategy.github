from __future__ import annotations

from pathlib import Path

import yaml

CANONICAL_AGENTS = {
    "internal-delivery-operator": ".github/agents/internal-delivery-operator.agent.md",
    "internal-planning-leader": ".github/agents/internal-planning-leader.agent.md",
    "internal-review-guard": ".github/agents/internal-review-guard.agent.md",
    "internal-critical-master": ".github/agents/internal-critical-master.agent.md",
}

OLD_CROSS_LANE_ENGINE = "internal-agent-" + "cross-lane-engine"

EXPECTED_HANDOFF_LABELS = {
    "internal-delivery-operator": ["Next step: Review result"],
    "internal-planning-leader": [
        "Next step: Implement plan",
        "Next step: Pressure-test plan",
    ],
    "internal-review-guard": [
        "Next action: Apply local fixes",
        "Next action: Re-plan larger changes",
        "Next action: Pressure-test unresolved decision",
    ],
    "internal-critical-master": [
        "Next step: Reformulate plan",
        "Next step: Implement clear next step",
        "Next step: Review evidence",
    ],
}

EXPECTED_HANDOFF_TARGETS = {
    "internal-delivery-operator": ["internal-review-guard"],
    "internal-planning-leader": [
        "internal-delivery-operator",
        "internal-critical-master",
    ],
    "internal-review-guard": [
        "internal-delivery-operator",
        "internal-planning-leader",
        "internal-critical-master",
    ],
    "internal-critical-master": [
        "internal-planning-leader",
        "internal-delivery-operator",
        "internal-review-guard",
    ],
}

EXPECTED_MANDATORY_SKILLS = {
    "internal-delivery-operator": [
        "internal-gateway-operational-flow",
        "internal-agent-support-lane-change-engine",
        "internal-agent-support-next-step",
    ],
    "internal-planning-leader": [
        "internal-gateway-operational-flow",
        "internal-agent-support-lane-change-engine",
        "internal-agent-support-next-step",
    ],
    "internal-review-guard": [
        "internal-gateway-operational-flow",
        "internal-agent-support-lane-change-engine",
        "internal-agent-support-next-step",
        "internal-code-review",
    ],
    "internal-critical-master": [
        "internal-gateway-critical-master",
        "internal-agent-support-lane-change-engine",
        "internal-agent-support-next-step",
    ],
}


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
            "grill-with-docs",
            "setup-matt-pocock-skills",
        )
    )


def mandatory_section(body: str) -> str:
    section = body.split("## Mandatory Engine Skills", 1)[1]
    return section.split("## ", 1)[0]


def test_canonical_agents_keep_required_frontmatter_and_engine_contracts() -> None:
    for agent_name, relative_path in CANONICAL_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        body = read_body(relative_path)

        assert frontmatter["name"] == agent_name
        assert isinstance(frontmatter.get("description"), str)
        assert frontmatter.get("tools")
        assert frontmatter.get("disable-model-invocation") is True
        assert "agent" not in frontmatter.get("tools", [])
        assert frontmatter.get("agents") in (None, [])
        assert "## Mandatory Engine Skills" in body
        assert "## Output Expectations" in body


def test_canonical_agents_keep_expected_engine_skill_assignments() -> None:
    for agent_name, expected_skills in EXPECTED_MANDATORY_SKILLS.items():
        body = read_body(CANONICAL_AGENTS[agent_name])
        mandatory_skills = mandatory_section(body)

        for expected_skill in expected_skills:
            assert f"- `{expected_skill}`" in mandatory_skills

        assert f"- `{OLD_CROSS_LANE_ENGINE}`" not in mandatory_skills


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


def test_next_step_package_skill_is_mandatory_for_all_operational_wrappers() -> None:
    for relative_path in CANONICAL_AGENTS.values():
        body = read_body(relative_path)

        assert "## Mandatory Engine Skills" in body
        assert "- `internal-agent-support-next-step`" in mandatory_section(body)


def test_agents_readme_documents_ascii_workflows_and_usage_examples() -> None:
    readme = Path(".github/agents/README.md").read_text(encoding="utf-8")

    assert "## ASCII Workflow Map" in readme
    assert "These maps describe the expected human-visible flow" in readme
    assert "+----------------------------+" in readme
    assert "| internal-delivery-operator |" in readme
    assert "internal-planning-leader" in readme
    assert "internal-review-guard" in readme
    assert "internal-critical-master" in readme
    assert "### 5. Source and consumer sync workflows" in readme
    assert "local-sync-external-resources" in readme
    assert "local-sync-global-copilot-configs-into-repo" in readme
    assert "## Use Examples" in readme
    assert "#### Delivery use cases" in readme
    assert "Good delivery requests usually name one of these surfaces" in readme
    assert "| Documentation |" in readme
    assert "| Agent contract |" in readme
    assert "Delivery can still cross multiple adjacent files" in readme
    assert "#### Planning use cases" in readme
    assert "Good planning requests usually involve one of these questions" in readme
    assert "| Ownership |" in readme
    assert "#### Review use cases" in readme
    assert "Good review requests usually name one of these review surfaces" in readme
    assert "| Merge readiness |" in readme
    assert "#### Critical challenge use cases" in readme
    assert (
        "Good challenge requests usually involve one of these pressure points" in readme
    )
    assert "| Hidden assumption |" in readme
    assert "#### Sync use cases" in readme
    assert "Source-side sync examples" in readme
    assert "Consumer propagation examples" in readme
    assert "Clear local edit with known validation" in readme
    assert "Catalog redesign, routing change, or retained plan" in readme
    assert "Source-side external catalog sync" in readme
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
    imported_support_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/imported-support-routing.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-gateway-operational-flow/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "name: internal-gateway-operational-flow" in skill_text
    assert "## Skill-First Staged Entry Points" in skill_text
    assert "`full-cycle`" in skill_text
    assert "`plan-only`" in skill_text
    assert "`apply-plan`" in skill_text
    assert "`mode-explicit`" in skill_text
    assert "Decision Brief" in skill_text
    assert "explicit checkpoint before moving from `plan`" in skill_text
    assert "multiple credible paths" in skill_text
    assert "`plan`" in mode_contracts_text
    assert "`execute`" in mode_contracts_text
    assert "`review`" in mode_contracts_text
    assert "`apply-plan`" in mode_contracts_text
    assert "Codex plugin or Codex CLI" in workflow_maps_text
    assert "Retained Plan Application" in workflow_maps_text
    assert "internal-planning-leader" in wrapper_alignment_text
    assert "mattpocock-zoom-out" in imported_support_text
    assert "mattpocock-caveman" in imported_support_text
    assert "internal-debugging" in mode_contracts_text
    assert "internal-tdd" in mode_contracts_text
    assert "internal-performance-optimization" in mode_contracts_text
    for retired_id in retired_mattpocock_ids():
        assert retired_id not in imported_support_text
    assert "$internal-gateway-operational-flow" in metadata_text

    planning_frontmatter = load_frontmatter(
        CANONICAL_AGENTS["internal-planning-leader"]
    )
    planning_body = read_body(CANONICAL_AGENTS["internal-planning-leader"])
    assert "unclear target state" in planning_frontmatter["description"]
    assert "multiple credible paths" in planning_frontmatter["description"]
    assert "multiple credible paths remain" in planning_body


def test_critical_master_skill_exists_with_challenge_boundary() -> None:
    skill_text = Path(
        ".github/skills/internal-gateway-critical-master/SKILL.md"
    ).read_text(encoding="utf-8")
    lenses_text = Path(
        ".github/skills/internal-gateway-critical-master/references/challenge-lenses.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-gateway-critical-master/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "name: internal-gateway-critical-master" in skill_text
    assert "Do not implement, routine-review, or finalize the plan" in skill_text
    assert "## Outcome Routing" in skill_text
    assert "`de-escalate-to-simple`" in skill_text
    assert "`execute-clear-next-step`" in skill_text
    assert "`review-evidence`" in skill_text
    assert "`accept-with-risk`" in skill_text
    assert "Final Consistency Gate" in lenses_text
    assert "Scope compression" in lenses_text
    assert "Explicit outcome" in lenses_text
    assert "$internal-gateway-critical-master" in metadata_text


def test_simple_gateway_covers_fast_path_and_misuse_boundaries() -> None:
    skill_text = Path(".github/skills/internal-gateway-simple-task/SKILL.md").read_text(
        encoding="utf-8"
    )
    metadata_text = Path(
        ".github/skills/internal-gateway-simple-task/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "## Protected Trigger" in skill_text
    assert "## Support-Skill Discovery" in skill_text
    assert "## Misuse Tests" in skill_text
    assert "de-escalates because the remaining work is concrete" in skill_text
    assert "`apply-plan` through `internal-gateway-operational-flow`" in skill_text
    assert "$internal-gateway-simple-task" in metadata_text


def test_prompt_examples_reference_live_gateway_skills() -> None:
    prompt_paths = [
        Path(".github/prompts/internal-agent-pressure-test-plan.prompt.md"),
        Path(".github/prompts/internal-agent-review-next-actions.prompt.md"),
        Path(".github/prompts/internal-agent-plan-next-step.prompt.md"),
    ]
    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in prompt_paths)

    assert "internal-gateway-operational-flow/SKILL.md" in combined_text
    assert "internal-gateway-critical-master/SKILL.md" in combined_text
    assert "internal-agent-support-next-step/SKILL.md" in combined_text
    assert "internal-agent-operational-flow" not in combined_text
    assert "internal-agent-critical-master" not in combined_text
    assert "internal-agent-next-step" not in combined_text
    assert "internal-agent-lane-change-engine" not in combined_text


def test_grill_me_is_conditional_plan_support_not_renamed_or_copied() -> None:
    operational_text = Path(
        ".github/skills/internal-gateway-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    planning_body = read_body(CANONICAL_AGENTS["internal-planning-leader"])

    assert Path(".github/skills/grill-me/SKILL.md").exists()
    assert not Path(".github/skills/mattpocock-grill-me/SKILL.md").exists()
    assert "grill-me" in operational_text
    assert "non-trivial retained plan" in operational_text
    assert "provide numbered questions with a recommended answer" in operational_text
    assert "continue one question at a time" in operational_text
    assert "- `grill-me`" in planning_body


def test_gateway_support_uses_internal_owners_after_extraction() -> None:
    planning_body = read_body(CANONICAL_AGENTS["internal-planning-leader"])
    delivery_body = read_body(CANONICAL_AGENTS["internal-delivery-operator"])
    review_body = read_body(CANONICAL_AGENTS["internal-review-guard"])
    imported_support_text = Path(
        ".github/skills/internal-gateway-operational-flow/references/imported-support-routing.md"
    ).read_text(encoding="utf-8")

    assert "- `mattpocock-zoom-out`" in planning_body
    assert "- `internal-debugging`" in delivery_body
    assert "- `internal-tdd`" in delivery_body
    assert "- `internal-performance-optimization`" in delivery_body
    assert "- `mattpocock-zoom-out`" in review_body
    assert "- `internal-debugging`" in review_body
    assert "- `internal-systems-review`" in review_body

    for wrapper_body in (planning_body, delivery_body, review_body):
        for retired_id in retired_mattpocock_ids():
            assert f"- `{retired_id}`" not in wrapper_body

    assert (
        "Failure diagnosis now belongs to `internal-debugging`" in imported_support_text
    )
    assert "Test-first delivery now belongs to `internal-tdd`" in imported_support_text
    for retired_id in retired_mattpocock_ids():
        assert retired_id not in imported_support_text


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
