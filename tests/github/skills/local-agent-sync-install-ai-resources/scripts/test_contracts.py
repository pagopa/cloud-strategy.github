import argparse
import json
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from agent_translation import target_extension, translate_agent_for_target  # noqa: E402
from home_sync_contract import (  # noqa: E402
    load_home_sync_catalog,
    load_home_sync_policy,
)
from home_syncing import (  # noqa: E402
    HomeSyncOperation,
    HomeSyncPlan,
    ManagedResource,
    build_home_sync_plan,
    build_manifest_payload,
    load_manifest,
    parse_targets,
    state_root_for_home,
)
from sync_home_ai_resources import (  # noqa: E402
    install_auto_apply_blockers,
    parse_args,
)
from sync_output import (  # noqa: E402
    build_compact_install_output,
    render_doctor_report,
    render_install_report,
    render_sync_report,
)


def test_parse_args_rejects_removed_bisync_and_preserves_supported_modes() -> None:
    for command in ("sync", "plan", "apply", "audit", "doctor", "dry-run"):
        assert parse_args([command]).command == command

    with pytest.raises(SystemExit):
        parse_args(["bisync", "plan"])


def test_install_payload_reports_linked_and_unlinked_without_bisync() -> None:
    compact = build_compact_install_output(
        {
            "mode": "plan",
            "validation": "ok",
            "linked": ["/home/.agents/skills/alpha"],
            "unlinked": ["/home/.agents/skills/removed"],
            "operations": [],
        }
    )

    assert compact["counts"]["linked"] == 1
    assert compact["counts"]["unlinked"] == 1
    assert "bisync" not in compact


def test_live_catalog_discovers_all_non_local_agents_for_copilot() -> None:
    resources = load_home_sync_catalog(REPO_ROOT)

    expected_paths = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / ".github/agents").glob("*.agent.md")
        if not path.name.startswith("local-")
    }
    agent_resources = {
        resource.source_path
        for resource in resources
        if resource.source_family == "agents"
    }

    assert agent_resources == expected_paths
    assert all(
        resource.include_targets == ("codex", "copilot", "opencode")
        for resource in resources
        if resource.source_family == "agents"
    )
    assert not any(
        resource.source_path.endswith("local-sync-external-resources.agent.md")
        for resource in resources
    )


def test_agent_discovery_excludes_local_agents_and_keeps_runtime_targets(
    tmp_path: Path,
) -> None:
    references = (
        tmp_path / ".github/skills/local-agent-sync-install-ai-resources/references"
    )
    references.mkdir(parents=True)
    (references / "home-sync-catalog.yaml").write_text(
        "version: 1\ndefaults:\n  include_unlisted_skills: false\nresources: []\n",
        encoding="utf-8",
    )
    agents_root = tmp_path / ".github/agents"
    agents_root.mkdir(parents=True)
    (agents_root / "review.agent.md").write_text(
        "---\nname: review\n---\n", encoding="utf-8"
    )
    (agents_root / "local-review.agent.md").write_text(
        "---\nname: local-review\n---\n", encoding="utf-8"
    )

    resources = load_home_sync_catalog(tmp_path)

    assert [resource.source_path for resource in resources] == [
        ".github/agents/review.agent.md"
    ]
    assert resources[0].include_targets == ("codex", "copilot", "opencode")


def test_empty_manifest_defaults_to_schema_v2(tmp_path: Path) -> None:
    payload, error = load_manifest(tmp_path / "manifest.json")

    assert error is None
    assert payload == {"schema_version": 2, "managed_resources": []}


def test_v1_manifest_rows_are_normalized_as_copy_without_rewrite(
    tmp_path: Path,
) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "managed_resources": [
                    {
                        "target": "skills",
                        "resource_family": "skills",
                        "resource_id": "demo",
                        "source_path": ".github/skills/demo",
                        "target_path": str(tmp_path / "home/demo"),
                        "source_hash": "source",
                        "content_hash": "content",
                        "last_action": "copy",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload, error = load_manifest(path)

    assert error is None
    assert payload["managed_resources"][0]["materialization"] == "copy"
    assert payload["managed_resources"][0]["link_target"] is None
    assert path.read_text(encoding="utf-8").startswith('{"schema_version": 1')


@pytest.mark.parametrize(
    ("row", "expected_error"),
    [
        (
            {
                "target": "skills",
                "resource_family": "skills",
                "materialization": "copy",
                "link_target": None,
                "content_hash": None,
                "target_path": "/home/.agents/skills/demo",
            },
            "manifest-corrupt",
        ),
        (
            {
                "target": "skills",
                "resource_family": "skills",
                "materialization": "symlink",
                "link_target": None,
                "content_hash": None,
                "target_path": "/home/.agents/skills/demo",
            },
            "manifest-corrupt",
        ),
        (
            {
                "target": "codex",
                "resource_family": "agents",
                "materialization": "copy",
                "link_target": "/repo/.github/agents/demo.agent.md",
                "content_hash": "hash",
                "target_path": "/home/.codex/agents/demo.toml",
            },
            "manifest-corrupt",
        ),
    ],
)
def test_manifest_rejects_inconsistent_v2_rows(
    tmp_path: Path, row: dict[str, object], expected_error: str
) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"schema_version": 2, "managed_resources": [row]}),
        encoding="utf-8",
    )

    _, error = load_manifest(path)

    assert error == expected_error


def test_valid_v2_manifest_rows_load_unchanged(tmp_path: Path) -> None:
    rows = [
        {
            "target": "skills",
            "resource_family": "skills",
            "materialization": "symlink",
            "link_target": (tmp_path / "repo/.github/skills/demo").as_posix(),
            "content_hash": None,
            "target_path": (tmp_path / "home/.agents/skills/demo").as_posix(),
        },
        {
            "target": "codex",
            "resource_family": "agents",
            "materialization": "copy",
            "link_target": None,
            "content_hash": "agent-content",
            "target_path": (tmp_path / "home/.codex/agents/review.toml").as_posix(),
        },
        {
            "target": "copilot",
            "resource_family": "agents",
            "materialization": "symlink",
            "link_target": (
                tmp_path / "repo/.github/agents/review.agent.md"
            ).as_posix(),
            "content_hash": None,
            "target_path": (
                tmp_path / "home/.copilot/agents/review.agent.md"
            ).as_posix(),
        },
    ]
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"schema_version": 2, "managed_resources": rows}), encoding="utf-8"
    )

    payload, error = load_manifest(path)

    assert error is None
    assert payload["schema_version"] == 2
    assert payload["managed_resources"] == rows


def test_manifest_serialization_emits_v2_link_and_copy_rows(tmp_path: Path) -> None:
    skill = ManagedResource(
        target="skills",
        resource_id="demo",
        resource_family="skills",
        source_path=".github/skills/demo",
        target_path=str(tmp_path / "home/.agents/skills/demo"),
        source_hash="source",
        materialization="symlink",
        link_target=str(tmp_path / ".github/skills/demo"),
        content_hash=None,
        last_action="link",
    )
    agent = ManagedResource(
        target="codex",
        resource_id="review",
        resource_family="agents",
        source_path=".github/agents/review.agent.md",
        target_path=str(tmp_path / "home/.codex/agents/review.toml"),
        source_hash="source-agent",
        materialization="copy",
        link_target=None,
        content_hash="content-agent",
        last_action="copy",
    )
    plan = HomeSyncPlan(
        source_root=tmp_path,
        home_root=tmp_path / "home",
        state_root=tmp_path / "state",
        mode="apply",
        selected_targets=("skills", "codex"),
        retired_targets=(),
        source_revision=None,
        source_resources_considered=2,
        operations=(),
        desired_resources=(skill, agent),
        missing_dirs=(),
        unsupported_families_by_target={},
        residual_drift=(),
    )

    payload = build_manifest_payload(plan)

    assert payload["schema_version"] == 2
    assert payload["managed_resources"] == [skill.to_dict(), agent.to_dict()]


def test_translate_agent_for_codex_preserves_body_and_handoffs(tmp_path: Path) -> None:
    source_path = tmp_path / "review.agent.md"
    source_path.write_text(
        textwrap.dedent(
            """\
            ---
            name: review-agent
            description: Review changes carefully.
            handoffs:
              - label: Escalate
                agent: review-specialist
                prompt: Include the risky files.
            ---
            Main body instructions.
            """
        ),
        encoding="utf-8",
    )

    translated = translate_agent_for_target(source_path, "codex")
    payload = tomllib.loads(translated)

    assert target_extension("codex") == ".toml"
    assert payload["name"] == "review-agent"
    assert "Main body instructions." in payload["developer_instructions"]
    assert "## Handoffs" in payload["developer_instructions"]
    assert "review-specialist" in payload["developer_instructions"]


def test_load_home_sync_catalog_autodiscovers_skills_and_honors_policy(
    tmp_path: Path,
) -> None:
    refs_dir = (
        tmp_path
        / ".github"
        / "skills"
        / "local-agent-sync-install-ai-resources"
        / "references"
    )
    refs_dir.mkdir(parents=True)
    (refs_dir / "home-sync-catalog.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            defaults:
              include_internal_skills: true
              include_local_skills: false
              include_unlisted_skills: true
              unmanaged_existing_skills_policy: repo-wins
              excluded_skills:
                - graphify
              skill_targets:
                - codex
                - copilot
            resources: []
            """
        ),
        encoding="utf-8",
    )

    skills_root = tmp_path / ".github" / "skills"
    for skill_name in ("alpha-skill", "internal-gamma", "local-beta", "graphify"):
        skill_dir = skills_root / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}\n", encoding="utf-8")

    policy = load_home_sync_policy(tmp_path)
    catalog = load_home_sync_catalog(tmp_path)

    assert policy.unmanaged_existing_skills_policy == "repo-wins"
    assert policy.excluded_skills == ("graphify",)
    assert {resource.resource_id for resource in catalog} == {
        "alpha-skill",
        "internal-gamma",
    }
    assert all(resource.include_targets == ("codex", "copilot") for resource in catalog)


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


def test_render_install_report_omits_empty_sections_and_uses_emoji_headings() -> None:
    report = render_install_report(
        {
            "mode": "plan",
            "selected_targets": ["skills"],
            "status": "ok",
            "validation": "ok",
            "blocked_codes": [],
            "operations": [],
            "source_resources_considered": 0,
            "state_path": "/tmp/state",
            "next_action": {
                "action": "done",
                "allowed": True,
                "requires_explicit_approval": False,
                "command": "",
                "reason": "No work.",
            },
        }
    )

    assert "🚦 Status:" in report
    assert "## 🧭 Summary" in report
    assert "## 🛠️ Changes" not in report
    assert "## ✅ Completed" not in report
    assert "## ⚠️ Attention" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report


def test_render_doctor_report_omits_readiness_when_everything_is_ok() -> None:
    report = render_doctor_report(
        {
            "selected_targets": ["skills"],
            "status": "ok",
            "validation": "ok",
            "checks": [
                {
                    "name": "runtime root",
                    "path": "/tmp/home/.agents/skills",
                    "status": "ok",
                }
            ],
            "state_path": "/tmp/state",
            "next_action": {
                "action": "done",
                "allowed": True,
                "requires_explicit_approval": False,
                "command": "",
                "reason": "No work.",
            },
        }
    )

    assert "🚦 Status:" in report
    assert "## 🧭 Summary" in report
    assert "## 🩺 Readiness" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report


def test_render_sync_report_omits_empty_action_sections() -> None:
    report = render_sync_report(
        {
            "status": "done",
            "reason": "No work.",
            "install": {
                "selected_targets": ["skills"],
                "operations": [],
                "validation": "ok",
                "state_path": "/tmp/state",
                "manifest_path": "/tmp/manifest",
            },
            "next_action": {
                "action": "done",
                "allowed": True,
                "requires_explicit_approval": False,
                "command": "",
                "reason": "No work.",
            },
        }
    )

    assert "🚦 Status:" in report
    assert "## 🧭 Summary" in report
    assert "## 🚀 Auto-applied" not in report
    assert "## 📋 Planned changes" not in report
    assert "## ⛔ Stopped on" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report
    assert "bisync" not in report


def test_install_auto_apply_blockers_require_explicit_review() -> None:
    class DummyPlan:
        def __init__(self) -> None:
            self.operations = (
                HomeSyncOperation(
                    target="skills",
                    action="mkdir",
                    path="/tmp/home/.agents/skills",
                    reason="Missing runtime root.",
                ),
                HomeSyncOperation(
                    target="skills",
                    action="warning",
                    path="/tmp/home/.agents/skills/demo",
                    reason="Home drift persists.",
                    code="install-warning",
                ),
            )

        def blocked_codes(self) -> list[str]:
            return []

    blockers = install_auto_apply_blockers(
        DummyPlan(),
        argparse.Namespace(create_missing_dirs=False),
    )

    assert blockers == ["install-residual-drift", "needs-directory-create"]


def test_skill_run_sh_should_quiet_only_for_compact_modes() -> None:
    run_sh = (
        (
            REPO_ROOT
            / ".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
        )
        .resolve()
        .as_posix()
    )
    script = textwrap.dedent(
        f"""\
        source "{run_sh}"
        set +e
        should_quiet --format compact
        compact_status="$?"
        should_quiet --format text
        text_status="$?"
        printf '%s,%s\\n' "$compact_status" "$text_status"
        """
    )

    result = subprocess.run(
        ["bash", "-lc", script],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "0,1"


def test_fast_mode_does_not_filter_apply_catalog(tmp_path: Path) -> None:
    refs_dir = (
        tmp_path
        / ".github"
        / "skills"
        / "local-agent-sync-install-ai-resources"
        / "references"
    )
    refs_dir.mkdir(parents=True)
    (refs_dir / "home-sync-catalog.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            defaults:
              include_internal_skills: true
              include_local_skills: false
              include_unlisted_skills: true
              unmanaged_existing_skills_policy: repo-wins
              excluded_skills: []
              skill_targets:
                - codex
            resources: []
            """
        ),
        encoding="utf-8",
    )
    (refs_dir / "runtime-support-matrix.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            rows:
              - target: skills
                resource_family: skills
                support_level: Documented
                home_path: ~/.agents/skills/<skill>/
                direct_copy_possible: true
                translation_required: false
                include_in_v1: true
                evidence: []
                notes: Shared support
            """
        ),
        encoding="utf-8",
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
    tmp_path: Path,
) -> None:
    refs_dir = (
        tmp_path
        / ".github"
        / "skills"
        / "local-agent-sync-install-ai-resources"
        / "references"
    )
    refs_dir.mkdir(parents=True)
    (refs_dir / "home-sync-catalog.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            defaults:
              include_internal_skills: true
              include_local_skills: false
              include_unlisted_skills: true
              unmanaged_existing_skills_policy: repo-wins
              excluded_skills: []
              skill_targets:
                - codex
                - copilot
                - opencode
            resources: []
            """
        ),
        encoding="utf-8",
    )
    (refs_dir / "runtime-support-matrix.yaml").write_text(
        textwrap.dedent(
            """\
            version: 1
            rows:
              - target: skills
                resource_family: skills
                support_level: Documented
                home_path: ~/.agents/skills/<skill>/
                direct_copy_possible: true
                translation_required: false
                include_in_v1: true
                evidence: []
                notes: Shared support
              - target: codex
                resource_family: skills
                support_level: Documented
                home_path: ~/.agents/skills/<skill>/
                direct_copy_possible: true
                translation_required: false
                include_in_v1: true
                evidence: []
                notes: Shared support
              - target: copilot
                resource_family: skills
                support_level: Documented
                home_path: ~/.agents/skills/<skill>/
                direct_copy_possible: true
                translation_required: false
                include_in_v1: true
                evidence: []
                notes: Shared support
              - target: opencode
                resource_family: skills
                support_level: Documented
                home_path: ~/.agents/skills/<skill>/
                direct_copy_possible: true
                translation_required: false
                include_in_v1: true
                evidence: []
                notes: Shared support
            """
        ),
        encoding="utf-8",
    )
    skill_dir = tmp_path / ".github" / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("# demo-skill\n", encoding="utf-8")

    plan = build_home_sync_plan(
        tmp_path,
        tmp_path / "home",
        ("skills", "codex", "copilot", "opencode"),
        mode="plan",
    )

    link_paths = [
        operation.path for operation in plan.operations if operation.action == "link"
    ]
    assert (
        link_paths.count(
            str((tmp_path / "home" / ".agents" / "skills" / "demo-skill").resolve())
        )
        == 1
    )

    manifest_payload = build_manifest_payload(plan)
    desired_paths = [
        resource["target_path"] for resource in manifest_payload["managed_resources"]
    ]
    assert (
        desired_paths.count(
            str((tmp_path / "home" / ".agents" / "skills" / "demo-skill").resolve())
        )
        == 1
    )
    assert plan.source_resources_considered == 1
