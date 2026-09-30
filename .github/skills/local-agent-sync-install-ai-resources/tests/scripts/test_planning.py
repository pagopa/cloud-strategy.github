import json
from pathlib import Path

import pytest
from home_sync_contract import CatalogResource, HomeSyncPolicy
from home_syncing import (
    HomeSyncOperation,
    _stale_confinement_check,
    add_materialization_operation,
    add_stale_managed_operations,
    assess_skill_link,
    build_home_sync_plan,
    build_manifest_payload,
    canonical_skill_link_target,
    hash_resource,
    parse_targets,
    state_root_for_home,
)

SHARED_SKILL_ROW = {"home_path": "~/.agents/skills/<skill>/", "notes": "Shared support"}


def _demo_resource() -> CatalogResource:
    return CatalogResource(
        resource_id="demo",
        source_family="skills",
        source_path=".github/skills/demo",
        include_targets=("skills",),
        target_support="documented",
        notes="",
    )


def _repo_wins_policy() -> HomeSyncPolicy:
    return HomeSyncPolicy(
        include_local_skills=False,
        include_internal_skills=True,
        include_unlisted_skills=True,
        skill_targets=("skills",),
        excluded_skills=(),
        unmanaged_existing_skills_policy="repo-wins",
    )


def test_parse_targets_orders_cross_aliases_and_rejects_unknown() -> None:
    assert parse_targets("copilot,skills") == ("skills", "copilot")
    assert parse_targets("agents-md") == ("agents.md",)
    assert parse_targets("tutto") == (
        "agents.md",
        "skills",
        "codex",
        "copilot",
        "opencode",
    )

    with pytest.raises(ValueError, match="unknown-target: invalid"):
        parse_targets("skills,invalid")


def test_fast_mode_does_not_filter_apply_catalog(tmp_path: Path, write_refs) -> None:
    write_refs(
        tmp_path,
        rows=[{"target": "skills", "resource_family": "skills", **SHARED_SKILL_ROW}],
    )
    for skill_name in ("alpha-skill", "beta-skill"):
        skill_dir = tmp_path / ".github" / "skills" / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}\n", encoding="utf-8")

    home_root = tmp_path / "home"
    state_root = state_root_for_home(home_root)
    state_root.mkdir(parents=True)
    (state_root / "manifest.json").write_text(
        json.dumps(
            {
                "managed_resources": [
                    {
                        "target": "skills",
                        "resource_family": "skills",
                        "resource_id": "alpha-skill",
                        "target_path": str(home_root / ".agents/skills/alpha-skill"),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    normal = build_home_sync_plan(
        tmp_path, home_root, ("skills",), mode="apply", fast=False
    )
    fast = build_home_sync_plan(
        tmp_path, home_root, ("skills",), mode="apply", fast=True
    )

    assert fast.source_resources_considered == normal.source_resources_considered == 2


def test_cross_target_skill_plan_deduplicates_shared_paths(
    tmp_path: Path, write_refs
) -> None:
    targets = ("skills", "codex", "copilot", "opencode")
    write_refs(
        tmp_path,
        defaults={"skill_targets": ["codex", "copilot", "opencode"]},
        rows=[
            {"target": target, "resource_family": "skills", **SHARED_SKILL_ROW}
            for target in targets
        ],
    )
    skill_dir = tmp_path / ".github" / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("# demo-skill\n", encoding="utf-8")
    shared_path = str((tmp_path / "home/.agents/skills/demo-skill").resolve())

    plan = build_home_sync_plan(tmp_path, tmp_path / "home", targets, mode="plan")

    link_paths = [
        operation.path for operation in plan.operations if operation.action == "link"
    ]
    assert link_paths.count(shared_path) == 1
    desired_paths = [
        resource["target_path"]
        for resource in build_manifest_payload(plan)["managed_resources"]
    ]
    assert desired_paths.count(shared_path) == 1
    assert plan.source_resources_considered == 1


def test_skill_link_assessment_is_deterministic(tmp_path: Path) -> None:
    source = tmp_path / ".github/skills/demo"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    expected = canonical_skill_link_target(tmp_path, ".github/skills/demo")
    missing = tmp_path / "home/.agents/skills/demo"
    missing.parent.mkdir(parents=True)

    assert assess_skill_link(missing, expected) == ("missing", None)

    missing.symlink_to(expected)
    assert assess_skill_link(missing, expected) == ("matching", None)

    missing.unlink()
    missing.mkdir()
    assert assess_skill_link(missing, expected) == ("replace-directory", None)

    missing.rmdir()
    other_checkout = tmp_path / "other-checkout"
    other_checkout.mkdir()
    missing.symlink_to(other_checkout, target_is_directory=True)
    assert assess_skill_link(missing, expected) == ("blocked", "link-target-mismatch")

    missing.unlink()
    missing.symlink_to(tmp_path / "removed-checkout", target_is_directory=True)
    assert assess_skill_link(missing, expected) == ("blocked", "link-target-missing")


def test_skill_planning_uses_link_and_adopts_matching_link(
    tmp_path: Path, demo_skill: Path
) -> None:
    source_hash = hash_resource(demo_skill)
    target = tmp_path / "home/.agents/skills/demo"
    target.parent.mkdir(parents=True)
    operations: list[HomeSyncOperation] = []

    def plan_demo() -> None:
        add_materialization_operation(
            operations,
            target="skills",
            target_path=target,
            source_path=demo_skill,
            resource=_demo_resource(),
            source_hash=source_hash,
            manifest_index={},
            changed_only=False,
            policy=_repo_wins_policy(),
        )

    plan_demo()
    assert [operation.action for operation in operations] == ["link"]

    target.symlink_to(demo_skill.resolve(), target_is_directory=True)
    operations.clear()
    plan_demo()
    assert [operation.action for operation in operations] == ["skip"]


def test_stale_manifest_skill_link_is_unlinked_without_prune_flag(
    tmp_path: Path,
) -> None:
    target = tmp_path / "home/.agents/skills/old"
    target.parent.mkdir(parents=True)
    source = tmp_path / "repo/.github/skills/old"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("# old\n", encoding="utf-8")
    target.symlink_to(source.resolve(), target_is_directory=True)
    operations: list[HomeSyncOperation] = []

    add_stale_managed_operations(
        operations,
        {
            "schema_version": 2,
            "managed_resources": [
                {
                    "target": "skills",
                    "resource_family": "skills",
                    "resource_id": "old",
                    "source_path": ".github/skills/old",
                    "target_path": target.as_posix(),
                    "source_hash": "source",
                    "materialization": "symlink",
                    "link_target": source.resolve().as_posix(),
                    "content_hash": None,
                    "last_action": "link",
                }
            ],
        },
        [],
        ("skills",),
        (),
        "plan",
        False,
        tmp_path / "home",
        _repo_wins_policy(),
    )

    assert [(operation.action, operation.code) for operation in operations] == [
        ("unlink", None)
    ]


@pytest.mark.parametrize(
    ("target", "source_path", "home_path", "content"),
    [
        pytest.param(
            "copilot",
            ".github/agents/demo-agent.agent.md",
            "home/.copilot/agents/demo-agent.agent.md",
            "Repository agent.\n",
            id="copilot",
        ),
        pytest.param(
            "codex",
            ".codex/agents/native-agent.toml",
            "home/.codex/agents/native-agent.toml",
            'name = "native-agent"\n',
            id="codex-native",
        ),
    ],
)
def test_manifest_managed_agent_copy_migrates_to_link_when_unchanged(
    tmp_path: Path, target: str, source_path: str, home_path: str, content: str
) -> None:
    source = tmp_path / source_path
    source.parent.mkdir(parents=True)
    source.write_text(content, encoding="utf-8")
    target_path = tmp_path / home_path
    target_path.parent.mkdir(parents=True)
    target_path.write_text(content, encoding="utf-8")
    resource = CatalogResource(
        resource_id=Path(source_path).name.split(".")[0],
        source_family="agents",
        source_path=source_path,
        include_targets=(target,),
        target_support="documented",
        notes="test agent",
    )
    operations: list[HomeSyncOperation] = []

    add_materialization_operation(
        operations,
        target=target,
        target_path=target_path,
        source_path=source,
        resource=resource,
        source_hash="source-hash",
        manifest_index={
            target_path.as_posix(): {
                "materialization": "copy",
                "content_hash": hash_resource(target_path),
            }
        },
        changed_only=False,
        policy=_repo_wins_policy(),
    )

    assert [(operation.action, operation.code) for operation in operations] == [
        ("link", None)
    ]


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
