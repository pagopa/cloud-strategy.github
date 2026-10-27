from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
AGENT_PATH = REPO_ROOT / ".github" / "agents" / "local-sync-repos.agent.md"


def test_local_sync_repos_agent_metadata_is_structurally_valid() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    metadata = yaml.safe_load(text.split("---", 2)[1])

    assert metadata["name"] == "local-sync-repos"
    assert metadata["agents"] == []
    assert metadata["disable-model-invocation"] is True
