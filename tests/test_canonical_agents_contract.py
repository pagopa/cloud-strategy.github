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
    "internal-critical-master": ["Next step: Reformulate plan"],
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
    "internal-critical-master": ["internal-planning-leader"],
}

EXPECTED_MANDATORY_SKILLS = {
    "internal-delivery-operator": [
        "internal-agent-operational-flow",
        "internal-agent-lane-change-engine",
        "internal-agent-next-step",
    ],
    "internal-planning-leader": [
        "internal-agent-operational-flow",
        "internal-agent-lane-change-engine",
        "internal-agent-next-step",
    ],
    "internal-review-guard": [
        "internal-agent-operational-flow",
        "internal-agent-lane-change-engine",
        "internal-agent-next-step",
        "internal-code-review",
    ],
    "internal-critical-master": [
        "internal-agent-critical-master",
        "internal-agent-lane-change-engine",
        "internal-agent-next-step",
    ],
}


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    frontmatter_text = text.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter_text)


def read_body(relative_path: str) -> str:
    text = Path(relative_path).read_text(encoding="utf-8")
    return text.split("---\n", 2)[2]


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
        assert "- `internal-agent-next-step`" in mandatory_section(body)


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
    assert "Good challenge requests usually involve one of these pressure points" in readme
    assert "| Hidden assumption |" in readme
    assert "#### Sync use cases" in readme
    assert "Source-side sync examples" in readme
    assert "Consumer propagation examples" in readme
    assert "Clear local edit with known validation" in readme
    assert "Catalog redesign, routing change, or retained plan" in readme
    assert "Source-side external catalog sync" in readme
    assert "If a request starts in the wrong lane" in readme


def test_skill_first_operational_core_exists_with_required_modes() -> None:
    skill_text = Path(
        ".github/skills/internal-agent-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    mode_contracts_text = Path(
        ".github/skills/internal-agent-operational-flow/references/mode-contracts.md"
    ).read_text(encoding="utf-8")
    workflow_maps_text = Path(
        ".github/skills/internal-agent-operational-flow/references/workflow-maps.md"
    ).read_text(encoding="utf-8")
    wrapper_alignment_text = Path(
        ".github/skills/internal-agent-operational-flow/references/wrapper-alignment.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-agent-operational-flow/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "name: internal-agent-operational-flow" in skill_text
    assert "`plan`, `execute`, and `review`" in skill_text
    assert "`plan`" in mode_contracts_text
    assert "`execute`" in mode_contracts_text
    assert "`review`" in mode_contracts_text
    assert "Codex plugin or Codex CLI" in workflow_maps_text
    assert "internal-planning-leader" in wrapper_alignment_text
    assert "$internal-agent-operational-flow" in metadata_text


def test_critical_master_skill_exists_with_challenge_boundary() -> None:
    skill_text = Path(
        ".github/skills/internal-agent-critical-master/SKILL.md"
    ).read_text(encoding="utf-8")
    lenses_text = Path(
        ".github/skills/internal-agent-critical-master/references/challenge-lenses.md"
    ).read_text(encoding="utf-8")
    metadata_text = Path(
        ".github/skills/internal-agent-critical-master/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "name: internal-agent-critical-master" in skill_text
    assert "Do not implement, routine-review, or finalize the plan" in skill_text
    assert "Final Consistency Gate" in lenses_text
    assert "Scope compression" in lenses_text
    assert "$internal-agent-critical-master" in metadata_text


def test_grill_me_is_conditional_plan_support_not_renamed_or_copied() -> None:
    operational_text = Path(
        ".github/skills/internal-agent-operational-flow/SKILL.md"
    ).read_text(encoding="utf-8")
    planning_body = read_body(CANONICAL_AGENTS["internal-planning-leader"])

    assert Path(".github/skills/mattpocock-grill-me/SKILL.md").exists()
    assert not Path(".github/skills/grill-me/SKILL.md").exists()
    assert "mattpocock-grill-me" in operational_text
    assert "conditional support" in operational_text
    assert "provide numbered questions with a recommended answer" in operational_text
    assert "continue one question at a time" in operational_text
    assert "- `mattpocock-grill-me`" in planning_body


def test_old_cross_lane_engine_is_not_live_catalog_contract() -> None:
    assert not Path(f".github/skills/{OLD_CROSS_LANE_ENGINE}/SKILL.md").exists()

    for relative_path in CANONICAL_AGENTS.values():
        assert OLD_CROSS_LANE_ENGINE not in read_body(relative_path)
