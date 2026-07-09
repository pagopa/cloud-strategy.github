import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources_core import (  # noqa: E402
    load_managed_resources,
)


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


def test_live_manifest_preserves_declared_scope(repo_root: Path) -> None:
    manifest = load_managed_resources(
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )

    assert len(manifest.assets) == 43
    assert len(manifest.watchlist) == 12
    assert {
        item.local for item in manifest.assets if item.source == "obra-superpowers"
    } == {
        ".github/skills/superpowers-brainstorming",
        ".github/skills/superpowers-dispatching-parallel-agents",
        ".github/skills/superpowers-executing-plans",
        ".github/skills/superpowers-finishing-a-development-branch",
        ".github/skills/superpowers-receiving-code-review",
        ".github/skills/superpowers-requesting-code-review",
        ".github/skills/superpowers-subagent-driven-development",
        ".github/skills/superpowers-systematic-debugging",
        ".github/skills/superpowers-test-driven-development",
        ".github/skills/superpowers-using-git-worktrees",
        ".github/skills/superpowers-using-superpowers",
        ".github/skills/superpowers-verification-before-completion",
        ".github/skills/superpowers-writing-plans",
    }


def test_manifest_rejects_duplicate_local_paths(tmp_path: Path) -> None:
    path = tmp_path / "managed-resources.yaml"
    path.write_text(
        """\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: abc123
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
      - upstream: skills/two
        local: .github/skills/example
        canonical_name: example-two
watchlist: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate local path"):
        load_managed_resources(path)
