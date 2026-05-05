from __future__ import annotations

from pathlib import Path

import yaml

CANONICAL_AGENTS = {
    "internal-delivery-operator": ".github/agents/internal-delivery-operator.agent.md",
    "internal-planning-leader": ".github/agents/internal-planning-leader.agent.md",
    "internal-review-guard": ".github/agents/internal-review-guard.agent.md",
    "internal-critical-master": ".github/agents/internal-critical-master.agent.md",
}

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


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    frontmatter_text = text.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter_text)


def read_body(relative_path: str) -> str:
    text = Path(relative_path).read_text(encoding="utf-8")
    return text.split("---\n", 2)[2]


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
    for agent_name in (
        "internal-delivery-operator",
        "internal-planning-leader",
        "internal-review-guard",
        "internal-critical-master",
    ):
        body = read_body(CANONICAL_AGENTS[agent_name])
        assert "- `internal-agent-cross-lane-engine`" in body
        assert "- `internal-agent-lane-change-engine`" in body


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


def test_next_step_package_skill_is_mandatory_only_for_planning_and_review() -> None:
    planning_body = read_body(CANONICAL_AGENTS["internal-planning-leader"])
    review_body = read_body(CANONICAL_AGENTS["internal-review-guard"])
    delivery_body = read_body(CANONICAL_AGENTS["internal-delivery-operator"])
    critical_body = read_body(CANONICAL_AGENTS["internal-critical-master"])

    assert "## Mandatory Engine Skills" in planning_body
    assert "- `internal-agent-next-step`" in planning_body
    assert "## Mandatory Engine Skills" in review_body
    assert "- `internal-agent-next-step`" in review_body
    assert "## Optional Support Skills" in delivery_body
    assert "- `internal-agent-next-step`" in delivery_body
    assert "## Optional Support Skills" in critical_body
    assert "- `internal-agent-next-step`" in critical_body


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
    assert "Clear local edit with known validation" in readme
    assert "Catalog redesign, routing change, or retained plan" in readme
    assert "Source-side external catalog sync" in readme
    assert "If a request starts in the wrong lane" in readme
