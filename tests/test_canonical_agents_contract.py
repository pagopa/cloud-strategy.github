from __future__ import annotations

from pathlib import Path

import yaml


CANONICAL_AGENTS = {
    "internal-gateway-idea-brainstorming": ".github/agents/internal-gateway-idea-brainstorming.agent.md",
    "internal-gateway-review": ".github/agents/internal-gateway-review.agent.md",
    "internal-gateway-critical-master": ".github/agents/internal-gateway-critical-master.agent.md",
    "internal-gateway-simple-task": ".github/agents/internal-gateway-simple-task.agent.md",
}


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1])


def test_canonical_agents_exist_and_keep_frontmatter_contracts() -> None:
    for name, relative_path in CANONICAL_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        assert frontmatter["name"] == name
        assert frontmatter["disable-model-invocation"] is True
        assert isinstance(frontmatter.get("handoffs"), list)


def test_review_gateway_is_canonical_and_operational_flow_wrapper_is_retired() -> None:
    assert Path(".github/agents/internal-gateway-review.agent.md").is_file()
    assert not Path(".github/agents/internal-gateway-operational-flow.agent.md").exists()


def test_agents_readme_mentions_review_gateway_and_extended_execution_boundary() -> None:
    readme = Path(".github/agents/README.md").read_text(encoding="utf-8")
    assert "internal-gateway-review" in readme
    assert "internal-gateway-execute-plans" in readme
    assert "internal-gateway-operational-flow" not in readme
