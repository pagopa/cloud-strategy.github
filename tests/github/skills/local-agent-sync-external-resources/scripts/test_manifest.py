import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources_core import (  # noqa: E402
    load_managed_resources,
    load_overrides,
    validate_override_patches,
)


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


def test_live_manifest_preserves_declared_scope(repo_root: Path) -> None:
    manifest = load_managed_resources(
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )

    assert len(manifest.assets) == 45
    assert len(manifest.watchlist) == 13
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
    assert {
        item.local
        for item in manifest.assets
        if item.source == "addyosmani-agent-skills"
    } == {
        ".github/skills/addyosmani-code-review-and-quality",
        ".github/skills/addyosmani-code-simplification",
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


def test_live_override_registry_patch_paths_exist(repo_root: Path) -> None:
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )
    bundle_root = repo_root / ".github/skills/local-agent-sync-external-resources"

    overrides = load_overrides(overrides_path)
    validate_override_patches(overrides, bundle_root)


def test_live_override_targets_sit_under_managed_assets(repo_root: Path) -> None:
    manifest = load_managed_resources(
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )

    managed_local_paths = {asset.local for asset in manifest.assets}
    overrides = load_overrides(overrides_path)

    for override in overrides:
        matched = any(
            override.target_path == local
            or override.target_path.startswith(local + "/")
            for local in managed_local_paths
        )
        assert matched, (
            f"Override {override.override_id} target {override.target_path} "
            f"does not sit under any managed local asset"
        )


def test_live_handoff_override_forces_repo_tmp_handoff(repo_root: Path) -> None:
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )
    bundle_root = repo_root / ".github/skills/local-agent-sync-external-resources"

    overrides = load_overrides(overrides_path)
    handoff = next(
        override
        for override in overrides
        if override.target_path == ".github/skills/mattpocock-handoff/SKILL.md"
    )

    assert handoff.override_id == "mattpocock-handoff-tmp-path"
    patch_text = (bundle_root / handoff.patch_path).read_text(encoding="utf-8")
    assert "tmp/handoff/" in patch_text
