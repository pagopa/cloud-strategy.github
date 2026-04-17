from __future__ import annotations

from pathlib import Path

import yaml


CANONICAL_AGENTS = {
    "internal-router": ".github/agents/internal-router.agent.md",
    "internal-fast-executor": ".github/agents/internal-fast-executor.agent.md",
    "internal-planning-leader": ".github/agents/internal-planning-leader.agent.md",
    "internal-review-guard": ".github/agents/internal-review-guard.agent.md",
    "internal-critical-challenger": ".github/agents/internal-critical-challenger.agent.md",
}


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    frontmatter_text = text.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter_text)


def read_body(relative_path: str) -> str:
    text = Path(relative_path).read_text(encoding="utf-8")
    return text.split("---\n", 2)[2]


def test_canonical_agents_keep_required_frontmatter_and_engine_contracts() -> None:
    expected_router_agents = {
        "internal-fast-executor",
        "internal-planning-leader",
        "internal-review-guard",
        "internal-critical-challenger",
    }

    for agent_name, relative_path in CANONICAL_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        body = read_body(relative_path)

        assert frontmatter["name"] == agent_name
        assert isinstance(frontmatter.get("description"), str)
        assert frontmatter.get("tools")
        assert "## Mandatory Engine Skills" in body
        assert "## Output Expectations" in body

    router_frontmatter = load_frontmatter(CANONICAL_AGENTS["internal-router"])
    challenger_frontmatter = load_frontmatter(CANONICAL_AGENTS["internal-critical-challenger"])

    assert set(router_frontmatter.get("agents", [])) == expected_router_agents
    assert challenger_frontmatter.get("agents") == ["internal-router"]

    for agent_name in (
        "internal-fast-executor",
        "internal-planning-leader",
        "internal-review-guard",
    ):
        frontmatter = load_frontmatter(CANONICAL_AGENTS[agent_name])
        agents = frontmatter.get("agents")
        assert agents in (None, [])


def test_canonical_agents_keep_expected_engine_skill_assignments() -> None:
    router_body = read_body(CANONICAL_AGENTS["internal-router"])
    assert "- `internal-agent-routing-engine`" in router_body

    for agent_name in (
        "internal-fast-executor",
        "internal-planning-leader",
        "internal-review-guard",
        "internal-critical-challenger",
    ):
        body = read_body(CANONICAL_AGENTS[agent_name])
        assert "- `internal-agent-operating-model-engine`" in body
