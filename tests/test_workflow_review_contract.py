from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_agents_and_policy_promote_conversational_gateways() -> None:
    agents_text = read_text("AGENTS.md")
    assert "internal-gateway-idea-brainstorming" in agents_text
    assert "internal-gateway-review" in agents_text
    assert "internal-gateway-operational-flow" not in agents_text


def test_idea_gateway_owns_retained_planning() -> None:
    skill_text = read_text(".github/skills/internal-gateway-idea-brainstorming/SKILL.md")
    assert "retained plan" in skill_text
    assert "internal-writing-plans" in skill_text
    assert "stop before execution" in skill_text


def test_review_gateway_exists_and_stops_before_fixes() -> None:
    skill_text = read_text(".github/skills/internal-gateway-review/SKILL.md")
    agent_text = read_text(".github/agents/internal-gateway-review.agent.md")
    assert "defect-first review" in skill_text
    assert "does not apply fixes" in skill_text
    assert "internal-writing-plans" in skill_text
    assert "internal-gateway-simple-task" in agent_text


def test_compact_and_extended_execution_owners_are_split() -> None:
    writing_text = read_text(".github/skills/internal-writing-plans/SKILL.md")
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    executing_text = read_text(".github/skills/internal-executing-plans/SKILL.md")
    assert "Recommended consumer" in writing_text
    assert "internal-gateway-simple-task" in writing_text
    assert "internal-executing-plans" in writing_text
    assert "`compact`" in simple_text
    assert "retained-plan execution" in simple_text
    assert "approved `extended`" in executing_text
    assert "internal-executing-plans" in executing_text
