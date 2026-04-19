from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_canonical_routing_contract_keeps_deterministic_repo_owned_work_in_execution() -> (
    None
):
    delivery_operator_text = read_text(
        ".github/agents/internal-delivery-operator.agent.md"
    )
    planning_leader_text = read_text(".github/agents/internal-planning-leader.agent.md")
    operating_model_text = read_text(
        ".github/skills/internal-agent-cross-lane-engine/SKILL.md"
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
        "ambiguous entry fails safe to `internal-planning-leader`"
        in operating_model_text
    )


def test_obra_assets_use_tmp_superpowers_for_transient_paths() -> None:
    obra_paths = (
        ".github/skills/obra-brainstorming/SKILL.md",
        ".github/skills/obra-brainstorming/spec-document-reviewer-prompt.md",
        ".github/skills/obra-writing-plans/SKILL.md",
        ".github/skills/obra-subagent-driven-development/SKILL.md",
        ".github/skills/obra-requesting-code-review/SKILL.md",
    )

    for relative_path in obra_paths:
        assert "docs/superpowers" not in read_text(relative_path)

    assert "tmp/superpowers/" in read_text(".github/skills/obra-brainstorming/SKILL.md")
    assert "tmp/superpowers/" in read_text(".github/skills/obra-writing-plans/SKILL.md")


def test_obra_workflows_do_not_claim_deterministic_textual_governance_maintenance() -> (
    None
):
    brainstorming_text = read_text(".github/skills/obra-brainstorming/SKILL.md")
    writing_plans_text = read_text(".github/skills/obra-writing-plans/SKILL.md")
    tdd_text = read_text(".github/skills/obra-test-driven-development/SKILL.md")

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
    agent_development_text = read_text(
        ".github/skills/internal-agent-development/SKILL.md"
    )
    subagent_patterns_text = read_text(
        ".github/skills/internal-agent-development/references/subagent-patterns.md"
    )

    assert (
        "subagents inherit the main session agent, model, and tools"
        in agent_development_text
    )
    assert (
        "a subagent inherits the main session agent, model, and tools"
        in subagent_patterns_text
    )
