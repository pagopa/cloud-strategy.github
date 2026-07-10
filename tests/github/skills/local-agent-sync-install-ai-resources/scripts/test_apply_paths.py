import sys
from pathlib import Path

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
    _stale_confinement_check,
    apply_home_sync_plan,
    hash_resource,
)


def _setup_skill_source(tmp_path: Path) -> tuple[Path, str]:
    skill_dir = tmp_path / ".github" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# demo\ncontent\n", encoding="utf-8")
    content_hash = hash_resource(skill_dir)
    return skill_dir, content_hash


def test_apply_copies_skill_to_home(tmp_path: Path) -> None:
    _, content_hash = _setup_skill_source(tmp_path)
    home_root = tmp_path / "home"
    target_path = home_root / ".agents" / "skills" / "demo"
    target_path.parent.mkdir(parents=True)
    state_root = tmp_path / "state"
    state_root.mkdir()

    resource = ManagedResource(
        target="skills",
        resource_id="demo",
        resource_family="skills",
        source_path=".github/skills/demo",
        target_path=str(target_path),
        source_hash="abc",
        content_hash=content_hash,
        last_action="copy",
    )
    operation = HomeSyncOperation(
        target="skills",
        action="copy",
        path=str(target_path),
        reason="first install",
        source_path=".github/skills/demo",
        resource_id="demo",
    )
    plan = HomeSyncPlan(
        source_root=tmp_path,
        home_root=home_root,
        state_root=state_root,
        mode="apply",
        selected_targets=("skills",),
        retired_targets=(),
        source_revision="abc",
        source_resources_considered=1,
        operations=(operation,),
        desired_resources=(resource,),
        missing_dirs=(),
        unsupported_families_by_target={},
        residual_drift=(),
    )

    manifest_path = apply_home_sync_plan(plan)
    assert manifest_path.is_file()
    assert (target_path / "SKILL.md").is_file()
    assert hash_resource(target_path) == content_hash


def test_apply_delete_with_prune(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    stale_path = home_root / ".agents" / "skills" / "old-skill"
    stale_path.mkdir(parents=True)
    (stale_path / "SKILL.md").write_text("# old\n", encoding="utf-8")
    state_root = tmp_path / "state"
    state_root.mkdir()

    operation = HomeSyncOperation(
        target="skills",
        action="delete",
        path=str(stale_path),
        reason="stale managed resource",
        code="stale-managed",
    )
    plan = HomeSyncPlan(
        source_root=tmp_path,
        home_root=home_root,
        state_root=state_root,
        mode="apply",
        selected_targets=("skills",),
        retired_targets=(),
        source_revision="abc",
        source_resources_considered=0,
        operations=(operation,),
        desired_resources=(),
        missing_dirs=(),
        unsupported_families_by_target={},
        residual_drift=(),
    )

    apply_home_sync_plan(plan, prune_managed=True)
    assert not stale_path.exists()


def test_apply_delete_without_prune_preserves_file(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    stale_path = home_root / ".agents" / "skills" / "old-skill"
    stale_path.mkdir(parents=True)
    (stale_path / "SKILL.md").write_text("# old\n", encoding="utf-8")
    state_root = tmp_path / "state"
    state_root.mkdir()

    operation = HomeSyncOperation(
        target="skills",
        action="delete",
        path=str(stale_path),
        reason="stale managed resource",
        code="stale-managed",
    )
    plan = HomeSyncPlan(
        source_root=tmp_path,
        home_root=home_root,
        state_root=state_root,
        mode="apply",
        selected_targets=("skills",),
        retired_targets=(),
        source_revision="abc",
        source_resources_considered=0,
        operations=(operation,),
        desired_resources=(),
        missing_dirs=(),
        unsupported_families_by_target={},
        residual_drift=(),
    )

    apply_home_sync_plan(plan, prune_managed=False)
    assert stale_path.exists()


def test_stale_confinement_blocks_path_outside_home(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    home_root.mkdir()
    outside_path = tmp_path / "outside" / "skill"
    outside_path.mkdir(parents=True)

    code = _stale_confinement_check(
        item={
            "target": "skills",
            "resource_family": "skills",
            "resource_id": "x",
            "content_hash": "abc",
        },
        target_path=str(outside_path),
        home_root=home_root,
        mode="plan",
    )
    assert code == "unsafe-home-path"


def test_stale_confinement_blocks_symlink(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    home_root.mkdir()
    target_root = home_root / ".agents" / "skills"
    target_root.mkdir(parents=True)
    outside = tmp_path / "outside-target"
    outside.mkdir()
    symlink = target_root / "linked-skill"
    symlink.symlink_to(outside)

    code = _stale_confinement_check(
        item={
            "target": "skills",
            "resource_family": "skills",
            "resource_id": "x",
            "content_hash": "abc",
        },
        target_path=str(symlink),
        home_root=home_root,
        mode="plan",
    )
    assert code == "symlink-not-allowed"


def test_stale_confinement_detects_corrupt_manifest_entry(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    home_root.mkdir()

    code = _stale_confinement_check(
        item={"target": "skills"},
        target_path=str(home_root / ".agents" / "skills" / "x"),
        home_root=home_root,
        mode="plan",
    )
    assert code == "manifest-corrupt"
