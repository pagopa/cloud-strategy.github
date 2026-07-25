from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


RETIRED_IDENTIFIERS = (
    "local-sync-global-copilot-configs-into-repo",
    "local-agent-sync-global-copilot-configs-into-repo",
)

RETIRED_BUNDLE_PATHS = (
    ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md",
    ".github/skills/local-agent-sync-global-copilot-configs-into-repo/SKILL.md",
    ".github/skills/local-agent-sync-global-copilot-configs-into-repo/agents/openai.yaml",
    ".github/skills/local-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md",
    ".github/prompts/internal-sync-plan.prompt.md",
    ".github/scripts/sync_copilot_catalog.py",
    ".github/scripts/lib/syncing.py",
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


def test_local_sync_repos_agent_points_to_one_core_skill() -> None:
    text = (REPO_ROOT / ".github/agents/local-sync-repos.agent.md").read_text()
    assert "name: local-sync-repos" in text
    assert "- `local-sync-repos`" in text
    assert "agents: []" in text
    assert "## Output Expectations" in text


def test_retired_sync_identifiers_have_zero_matches() -> None:
    matches: list[str] = []
    this_file = Path(__file__).resolve()
    for path in REPO_ROOT.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or "tmp" in path.parts
            or "graphify-out" in path.parts
            or "__pycache__" in path.parts
        ):
            continue
        if path.resolve() == this_file:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(identifier in text for identifier in RETIRED_IDENTIFIERS):
            matches.append(path.relative_to(REPO_ROOT).as_posix())
    assert matches == []


def test_retired_bundle_paths_are_absent() -> None:
    missing = [p for p in RETIRED_BUNDLE_PATHS if (REPO_ROOT / p).exists()]
    assert missing == []


def test_new_bundle_paths_are_present() -> None:
    missing = [p for p in NEW_BUNDLE_PATHS if not (REPO_ROOT / p).exists()]
    assert missing == []
