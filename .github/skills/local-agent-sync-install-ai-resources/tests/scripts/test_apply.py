from pathlib import Path

import pytest
from home_syncing import (
    HomeSyncOperation,
    ManagedResource,
    apply_home_sync_plan,
    probe_symlink_support,
)


def _demo_link_plan(make_plan, demo_skill: Path, target_path: Path):
    resource = ManagedResource(
        target="skills",
        resource_id="demo",
        resource_family="skills",
        source_path=".github/skills/demo",
        target_path=str(target_path),
        source_hash="abc",
        materialization="symlink",
        link_target=demo_skill.resolve().as_posix(),
        content_hash=None,
        last_action="link",
    )
    operation = HomeSyncOperation(
        target="skills",
        action="link",
        path=str(target_path),
        reason="first install",
        source_path=".github/skills/demo",
        resource_id="demo",
    )
    return make_plan(
        source_resources_considered=1,
        operations=(operation,),
        desired_resources=(resource,),
    )


def test_apply_links_skill_to_home_with_write_through(
    tmp_path: Path, make_plan, demo_skill: Path
) -> None:
    target_path = tmp_path / "home/.agents/skills/demo"
    target_path.parent.mkdir(parents=True)
    (tmp_path / "state").mkdir()

    manifest_path = apply_home_sync_plan(
        _demo_link_plan(make_plan, demo_skill, target_path)
    )

    assert manifest_path.is_file()
    assert target_path.is_symlink()
    assert target_path.resolve() == demo_skill.resolve()
    assert (target_path / "SKILL.md").is_file()
    (demo_skill / "SKILL.md").write_text("# changed in repo\n", encoding="utf-8")
    assert (target_path / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "# changed in repo\n"
    (target_path / "SKILL.md").write_text("# changed through home\n", encoding="utf-8")
    assert (demo_skill / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "# changed through home\n"


@pytest.mark.parametrize(
    ("prune_managed", "expect_exists"),
    [pytest.param(True, False, id="prune"), pytest.param(False, True, id="no-prune")],
)
def test_apply_delete_honors_prune_flag(
    tmp_path: Path, make_plan, prune_managed: bool, expect_exists: bool
) -> None:
    stale_path = tmp_path / "home/.agents/skills/old-skill"
    stale_path.mkdir(parents=True)
    (stale_path / "SKILL.md").write_text("# old\n", encoding="utf-8")
    (tmp_path / "state").mkdir()
    operation = HomeSyncOperation(
        target="skills",
        action="delete",
        path=str(stale_path),
        reason="stale managed resource",
        code="stale-managed",
    )

    apply_home_sync_plan(
        make_plan(operations=(operation,)), prune_managed=prune_managed
    )

    assert stale_path.exists() is expect_exists


def test_apply_blocks_path_escaping_home_root(
    tmp_path: Path, make_plan, demo_skill: Path
) -> None:
    plan = _demo_link_plan(make_plan, demo_skill, tmp_path / "outside/skills/demo")
    (tmp_path / "state").mkdir()

    with pytest.raises(RuntimeError, match="unsafe-home-path"):
        apply_home_sync_plan(plan)


def test_apply_blocks_symlink_escape(
    tmp_path: Path, make_plan, demo_skill: Path
) -> None:
    outside = tmp_path / "outside-target"
    outside.mkdir()
    symlink_path = tmp_path / "home/.agents/skills/demo"
    symlink_path.parent.mkdir(parents=True)
    symlink_path.symlink_to(outside)
    plan = _demo_link_plan(make_plan, demo_skill, symlink_path)
    (tmp_path / "state").mkdir()

    with pytest.raises(RuntimeError, match="link-target-mismatch"):
        apply_home_sync_plan(plan)


def test_probe_symlink_support_returns_blocker_when_os_rejects_link_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def reject_symlink(*args: object, **kwargs: object) -> None:
        raise OSError("not supported")

    monkeypatch.setattr("home_syncing.os.symlink", reject_symlink)

    assert probe_symlink_support(tmp_path) == "symlink-unsupported"
