import json
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from home_sync_contract import CatalogResource, HomeSyncPolicy  # noqa: E402
from home_syncing import (  # noqa: E402
    HomeSyncOperation,
    HomeSyncPlan,
    ManagedResource,
    _stale_confinement_check,
    add_materialization_operation,
    add_stale_managed_operations,
    apply_home_sync_plan,
    assess_skill_link,
    canonical_skill_link_target,
    hash_resource,
)
from sync_home_ai_resources import parse_args, run  # noqa: E402


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


def test_skill_planning_uses_link_and_adopts_matching_link(tmp_path: Path) -> None:
    source, source_hash = _setup_skill_source(tmp_path)
    target = tmp_path / "home/.agents/skills/demo"
    target.parent.mkdir(parents=True)
    operations: list[HomeSyncOperation] = []

    add_materialization_operation(
        operations,
        target="skills",
        target_path=target,
        source_path=source,
        resource=_demo_resource(),
        source_hash=source_hash,
        manifest_index={},
        changed_only=False,
        policy=_repo_wins_policy(),
    )
    assert [operation.action for operation in operations] == ["link"]

    target.symlink_to(source.resolve(), target_is_directory=True)
    operations.clear()
    add_materialization_operation(
        operations,
        target="skills",
        target_path=target,
        source_path=source,
        resource=_demo_resource(),
        source_hash=source_hash,
        manifest_index={},
        changed_only=False,
        policy=_repo_wins_policy(),
    )
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


def test_temporary_home_sync_links_skills_preserves_home_only_and_copies_agents(
    tmp_path: Path, capsys
) -> None:
    refs = tmp_path / ".github/skills/local-agent-sync-install-ai-resources/references"
    refs.mkdir(parents=True)
    (refs / "home-sync-catalog.yaml").write_text(
        """version: 1
defaults:
  include_internal_skills: true
  include_local_skills: false
  include_unlisted_skills: true
  unmanaged_existing_skills_policy: repo-wins
  excluded_skills: [graphify]
  skill_targets: [codex]
resources:
  - resource_id: demo-agent
    source_family: agents
    source_path: .github/agents/demo-agent.agent.md
    include_targets: [codex]
    target_support: documented
    notes: test agent
""",
        encoding="utf-8",
    )
    (refs / "runtime-support-matrix.yaml").write_text(
        """version: 1
rows:
  - target: skills
    resource_family: skills
    support_level: Documented
    home_path: ~/.agents/skills/<skill>/
    direct_copy_possible: true
    translation_required: false
    include_in_v1: true
    evidence: []
    notes: test
  - target: codex
    resource_family: skills
    support_level: Documented
    home_path: ~/.agents/skills/<skill>/
    direct_copy_possible: true
    translation_required: false
    include_in_v1: true
    evidence: []
    notes: test
  - target: codex
    resource_family: agents
    support_level: Documented
    home_path: ~/.codex/agents/
    direct_copy_possible: false
    translation_required: true
    include_in_v1: true
    evidence: []
    notes: test
""",
        encoding="utf-8",
    )
    source_skill = tmp_path / ".github/skills/demo"
    source_skill.mkdir(parents=True)
    (source_skill / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    for skill_id in ("graphify", "local-private"):
        skill = tmp_path / ".github/skills" / skill_id
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")
    agent = tmp_path / ".github/agents/demo-agent.agent.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\nname: demo-agent\ndescription: test\n---\nTest agent.\n", encoding="utf-8"
    )

    home = tmp_path / "home"
    divergent = home / ".agents/skills/demo"
    divergent.mkdir(parents=True)
    (divergent / "SKILL.md").write_text("# divergent\n", encoding="utf-8")
    for skill_id in ("graphify", "home-only"):
        skill = home / ".agents/skills" / skill_id
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")

    assert (
        run(
            parse_args(
                [
                    "sync",
                    "--source-root",
                    str(tmp_path),
                    "--home-root",
                    str(home),
                    "--targets",
                    "skills,codex",
                    "--create-missing-dirs",
                ]
            )
        )
        == 0
    )

    target_skill = home / ".agents/skills/demo"
    assert target_skill.is_symlink()
    assert target_skill.resolve() == source_skill.resolve()
    assert (home / ".agents/skills/graphify/SKILL.md").is_file()
    assert (home / ".agents/skills/home-only/SKILL.md").is_file()
    assert (home / ".codex/agents/demo-agent.toml").is_file()
    (source_skill / "SKILL.md").write_text("# repo edit\n", encoding="utf-8")
    assert (target_skill / "SKILL.md").read_text(encoding="utf-8") == "# repo edit\n"
    (target_skill / "SKILL.md").write_text("# home write\n", encoding="utf-8")
    assert (source_skill / "SKILL.md").read_text(encoding="utf-8") == "# home write\n"

    import shutil

    shutil.rmtree(source_skill)
    assert (
        run(
            parse_args(
                [
                    "sync",
                    "--source-root",
                    str(tmp_path),
                    "--home-root",
                    str(home),
                    "--targets",
                    "skills,codex",
                    "--create-missing-dirs",
                ]
            )
        )
        == 0
    )
    capsys.readouterr()
    assert not target_skill.exists()
    assert not target_skill.is_symlink()
    for mode in ("plan", "audit", "doctor"):
        assert (
            run(
                parse_args(
                    [
                        mode,
                        "--source-root",
                        str(tmp_path),
                        "--home-root",
                        str(home),
                        "--targets",
                        "skills,codex",
                    ]
                )
            )
            == 0
        )
        payload = json.loads(capsys.readouterr().out)
        assert payload.get("blocked_codes", []) == []
        assert payload["counts"]["linked"] == 0
        assert payload["counts"]["unlinked"] == 0
        assert payload["counts"]["blocked"] == 0
        assert payload["counts"]["residual"] == 0


def test_agents_md_sync_removes_repository_local_rules_and_overwrites_home_copy(
    tmp_path: Path, capsys
) -> None:
    refs = tmp_path / ".github/skills/local-agent-sync-install-ai-resources/references"
    refs.mkdir(parents=True)
    (refs / "home-sync-catalog.yaml").write_text(
        """version: 1
defaults:
  include_internal_skills: false
  include_local_skills: false
  include_unlisted_skills: false
  unmanaged_existing_skills_policy: repo-wins
  excluded_skills: []
  skill_targets: []
resources:
  - resource_id: global-agents
    source_family: agents-md
    source_path: AGENTS.md
    include_targets: [agents.md]
    target_support: documented
    notes: Portable global agent baseline.
""",
        encoding="utf-8",
    )
    (refs / "runtime-support-matrix.yaml").write_text(
        """version: 1
rows:
  - target: agents.md
    resource_family: agents-md
    support_level: Documented
    home_path: ~/.agents/AGENTS.md
    direct_copy_possible: true
    translation_required: false
    include_in_v1: true
    evidence: []
    notes: Portable global agent baseline.
""",
        encoding="utf-8",
    )
    source = tmp_path / "AGENTS.md"
    source.write_text(
        """# Global agent policy

`<shared-baseline>`

Shared policy.

`</shared-baseline>`

`<standards-repository-local-rules>`

Repository-only policy.

`</standards-repository-local-rules>`
""",
        encoding="utf-8",
    )
    home = tmp_path / "home"
    target = home / ".agents/AGENTS.md"
    target.parent.mkdir(parents=True)
    target.write_text("old local policy\n", encoding="utf-8")

    assert (
        run(
            parse_args(
                [
                    "sync",
                    "--source-root",
                    str(tmp_path),
                    "--home-root",
                    str(home),
                    "--targets",
                    "agents.md",
                ]
            )
        )
        == 0
    )
    capsys.readouterr()

    assert (
        target.read_text(encoding="utf-8")
        == """# Global agent policy

`<shared-baseline>`

Shared policy.

`</shared-baseline>`
"""
    )
    manifest = json.loads(
        (
            home / ".sync/cloud-strategy-governance/home-ai-resources/manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["managed_resources"][0]["target"] == "agents.md"
    assert manifest["managed_resources"][0]["resource_family"] == "agents-md"


def test_copilot_agents_are_symlinked_with_write_through(
    tmp_path: Path, capsys
) -> None:
    refs = tmp_path / ".github/skills/local-agent-sync-install-ai-resources/references"
    refs.mkdir(parents=True)
    (refs / "home-sync-catalog.yaml").write_text(
        """version: 1
defaults:
  include_internal_skills: true
  include_local_skills: false
  include_unlisted_skills: true
  unmanaged_existing_skills_policy: repo-wins
  excluded_skills: []
  skill_targets: [copilot]
resources:
  - resource_id: demo-agent
    source_family: agents
    source_path: .github/agents/demo-agent.agent.md
    include_targets: [copilot]
    target_support: documented
    notes: test agent
""",
        encoding="utf-8",
    )
    (refs / "runtime-support-matrix.yaml").write_text(
        """version: 1
rows:
  - target: copilot
    resource_family: agents
    support_level: Documented
    home_path: ~/.copilot/agents/
    direct_copy_possible: true
    translation_required: false
    include_in_v1: true
    evidence: []
    notes: test
""",
        encoding="utf-8",
    )
    source = tmp_path / ".github/agents/demo-agent.agent.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "---\nname: demo-agent\n---\nRepository agent.\n", encoding="utf-8"
    )

    home = tmp_path / "home"
    assert (
        run(
            parse_args(
                [
                    "sync",
                    "--source-root",
                    str(tmp_path),
                    "--home-root",
                    str(home),
                    "--targets",
                    "copilot",
                    "--create-missing-dirs",
                ]
            )
        )
        == 0
    )
    capsys.readouterr()

    target = home / ".copilot/agents/demo-agent.agent.md"
    assert target.is_symlink()
    assert target.resolve() == source.resolve()
    source.write_text(
        "---\nname: demo-agent\n---\nUpdated in repository.\n", encoding="utf-8"
    )
    assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
    target.write_text(
        "---\nname: demo-agent\n---\nUpdated through home.\n", encoding="utf-8"
    )
    assert (
        source.read_text(encoding="utf-8")
        == "---\nname: demo-agent\n---\nUpdated through home.\n"
    )


def test_manifest_managed_copilot_copy_migrates_to_link_when_unchanged(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".github/agents/demo-agent.agent.md"
    source.parent.mkdir(parents=True)
    source.write_text("Repository agent.\n", encoding="utf-8")
    target = tmp_path / "home/.copilot/agents/demo-agent.agent.md"
    target.parent.mkdir(parents=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    resource = CatalogResource(
        resource_id="demo-agent",
        source_family="agents",
        source_path=".github/agents/demo-agent.agent.md",
        include_targets=("copilot",),
        target_support="documented",
        notes="test agent",
    )
    operations: list[HomeSyncOperation] = []

    add_materialization_operation(
        operations,
        target="copilot",
        target_path=target,
        source_path=source,
        resource=resource,
        source_hash="source-hash",
        manifest_index={
            target.as_posix(): {
                "materialization": "copy",
                "content_hash": hash_resource(target),
            }
        },
        changed_only=False,
        policy=_repo_wins_policy(),
    )

    assert [(operation.action, operation.code) for operation in operations] == [
        ("link", None)
    ]


def _setup_skill_source(tmp_path: Path) -> tuple[Path, str]:
    skill_dir = tmp_path / ".github" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# demo\ncontent\n", encoding="utf-8")
    content_hash = hash_resource(skill_dir)
    return skill_dir, content_hash


def test_apply_links_skill_to_home_with_write_through(tmp_path: Path) -> None:
    source, _ = _setup_skill_source(tmp_path)
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
        materialization="symlink",
        link_target=source.resolve().as_posix(),
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
    assert target_path.is_symlink()
    assert target_path.resolve() == source.resolve()
    assert (target_path / "SKILL.md").is_file()
    (source / "SKILL.md").write_text("# changed in repo\n", encoding="utf-8")
    assert (target_path / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "# changed in repo\n"
    (target_path / "SKILL.md").write_text("# changed through home\n", encoding="utf-8")
    assert (source / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "# changed through home\n"


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
