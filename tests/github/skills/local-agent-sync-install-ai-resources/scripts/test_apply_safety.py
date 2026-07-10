import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from home_syncing import (  # noqa: E402
    HomeSyncOperation,
    HomeSyncPlan,
    ManagedResource,
    apply_home_sync_plan,
)


def _make_plan(tmp_path: Path, target_path: Path) -> HomeSyncPlan:
    source_skill = tmp_path / ".github" / "skills" / "demo"
    source_skill.mkdir(parents=True)
    (source_skill / "SKILL.md").write_text("# demo\n", encoding="utf-8")

    resource = ManagedResource(
        target="skills",
        resource_id="demo",
        resource_family="skills",
        source_path=".github/skills/demo",
        target_path=str(target_path),
        source_hash="abc",
        content_hash="abc",
        last_action="copy",
    )
    operation = HomeSyncOperation(
        target="skills",
        action="copy",
        path=str(target_path),
        reason="first install",
        code=None,
        source_path=".github/skills/demo",
        resource_id="demo",
    )
    return HomeSyncPlan(
        source_root=tmp_path,
        home_root=tmp_path / "home",
        state_root=tmp_path / "state",
        mode="apply",
        selected_targets=("skills",),
        retired_targets=(),
        source_revision="abc1234",
        source_resources_considered=1,
        operations=(operation,),
        desired_resources=(resource,),
        missing_dirs=(),
        unsupported_families_by_target={},
        residual_drift=(),
    )


def test_apply_blocks_path_escaping_home_root(tmp_path: Path) -> None:
    escape_path = tmp_path / "outside" / "skills" / "demo"
    plan = _make_plan(tmp_path, escape_path)
    (tmp_path / "state").mkdir()

    with pytest.raises(RuntimeError, match="unsafe-home-path"):
        apply_home_sync_plan(plan)


def test_apply_blocks_symlink_escape(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    outside = tmp_path / "outside-target"
    outside.mkdir()
    symlink_path = home / ".agents" / "skills" / "demo"
    symlink_path.parent.mkdir(parents=True, exist_ok=True)
    symlink_path.symlink_to(outside)

    plan = _make_plan(tmp_path, symlink_path)
    (tmp_path / "state").mkdir()

    with pytest.raises(RuntimeError, match="symlink-not-allowed|unsafe-home-path"):
        apply_home_sync_plan(plan)
