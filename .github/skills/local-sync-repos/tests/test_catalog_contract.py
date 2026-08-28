from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


NEW_BUNDLE_PATHS = (
    ".github/agents/local-sync-repos.agent.md",
    ".github/skills/local-sync-repos/SKILL.md",
    ".github/skills/local-sync-repos/scripts/sync_contract.py",
    ".github/skills/local-sync-repos/scripts/sync_repos.py",
    ".github/skills/local-sync-repos/references/sync-contract.md",
    ".github/skills/local-sync-repos/templates/AGENTS.local.md",
    ".github/skills/local-sync-repos/agents/openai.yaml",
)


def test_local_sync_repos_agent_metadata_is_structurally_valid() -> None:
    text = (REPO_ROOT / ".github/agents/local-sync-repos.agent.md").read_text()
    metadata = yaml.safe_load(text.split("---", 2)[1])

    assert metadata["name"] == "local-sync-repos"
    assert metadata["agents"] == []
    assert metadata["disable-model-invocation"] is True


def test_new_bundle_paths_are_present() -> None:
    missing = [p for p in NEW_BUNDLE_PATHS if not (REPO_ROOT / p).exists()]
    assert missing == []
