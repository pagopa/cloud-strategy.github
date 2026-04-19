from __future__ import annotations

from pathlib import Path

import yaml

CANONICAL_AGENTS = {
    "internal-delivery-operator": ".github/agents/internal-delivery-operator.agent.md",
    "internal-planning-leader": ".github/agents/internal-planning-leader.agent.md",
    "internal-review-guard": ".github/agents/internal-review-guard.agent.md",
    "internal-critical-master": ".github/agents/internal-critical-master.agent.md",
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
        assert "- `internal-agent-boundary-recommendation-engine`" in body

