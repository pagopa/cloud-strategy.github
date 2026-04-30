from __future__ import annotations

from pathlib import Path

import yaml

SYNC_AGENTS = {
    "local-sync-external-resources": ".github/agents/local-sync-external-resources.agent.md",
    "local-sync-global-copilot-configs-into-repo": ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md",
}


def load_frontmatter(relative_path: str) -> dict[str, object]:
    text = Path(relative_path).read_text(encoding="utf-8")
    frontmatter_text = text.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter_text)


def read_body(relative_path: str) -> str:
    text = Path(relative_path).read_text(encoding="utf-8")
    return text.split("---\n", 2)[2]


def test_repo_only_sync_agents_keep_boundary_and_tool_contracts() -> None:
    for agent_name, relative_path in SYNC_AGENTS.items():
        frontmatter = load_frontmatter(relative_path)
        body = read_body(relative_path)

        assert frontmatter["name"] == agent_name
        assert isinstance(frontmatter.get("description"), str)
        assert frontmatter.get("tools")
        assert "agent" not in frontmatter.get("tools", [])
        assert frontmatter.get("disable-model-invocation") is True
        assert frontmatter.get("agents") in (None, [])
        assert "## Mandatory Engine Skills" in body
        assert "## Boundary Definition" in body
        assert "- `internal-agent-boundary-recommendation-engine`" in body


def test_repo_only_sync_agents_keep_their_named_operating_engines() -> None:
    sync_control_center = read_body(
        ".github/agents/local-sync-external-resources.agent.md"
    )
    sync_global = read_body(
        ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md"
    )

    assert "- `local-agent-sync-external-resources`" in sync_control_center
    assert "- `local-agent-sync-global-copilot-configs-into-repo`" in sync_global


def test_direct_entry_model_keeps_removed_router_assets_out_of_live_catalog() -> None:
    assert not Path(".github/agents/internal-router.agent.md").exists()
    assert not Path(".github/skills/internal-agent-routing-engine").exists()
