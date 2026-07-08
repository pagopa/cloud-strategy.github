import argparse
import json
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from agent_translation import target_extension, translate_agent_for_target  # noqa: E402
from bisync_skills import (  # noqa: E402
    build_bisync_plan,
    run_bisync_apply,
    run_bisync_plan,
)
from home_sync_contract import (  # noqa: E402
    load_home_sync_catalog,
    load_home_sync_policy,
)
from home_syncing import (  # noqa: E402
    HomeSyncOperation,
    build_home_sync_plan,
    build_manifest_payload,
    parse_targets,
    state_root_for_home,
)
from sync_output import (  # noqa: E402
    render_doctor_report,
    render_install_report,
    render_sync_report,
)
from sync_home_ai_resources import (  # noqa: E402
    bisync_requires_review,
    install_auto_apply_blockers,
)


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
                agent: internal-review-code
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
    assert "internal-review-code" in payload["developer_instructions"]


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
    assert parse_targets("tutto") == ("skills", "codex", "copilot", "opencode")

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
            "bisync": {
                "mode": "plan",
                "drifts": [],
                "verification": {"status": "ok"},
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
    assert "## 📋 Planned repo-to-home copies" not in report
    assert "## ⛔ Stopped on" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report


def test_build_bisync_plan_filters_local_and_excluded_bundles(tmp_path: Path) -> None:
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
              include_unlisted_skills: false
              unmanaged_existing_skills_policy: block
              excluded_skills:
                - graphify
              skill_targets:
                - codex
            resources: []
            """
        ),
        encoding="utf-8",
    )

    repo_skills = tmp_path / ".github" / "skills"
    home_root = tmp_path / "home"
    home_skills = home_root / ".agents" / "skills"
    home_skills.mkdir(parents=True)

    for skill_name, root in (
        ("shared-skill", repo_skills),
        ("local-helper", repo_skills),
        ("graphify", repo_skills),
        ("home-only-skill", home_skills),
    ):
        skill_dir = root / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}\n", encoding="utf-8")

    plan = build_bisync_plan(tmp_path, home_root, mode="plan")

    assert {(drift.skill_name, drift.drift_type) for drift in plan.drifts} == {
        ("shared-skill", "only-repo"),
        ("home-only-skill", "only-home"),
    }
    assert "bisync-only-home" in plan.blocked_codes
    assert "bisync-only-repo" in plan.blocked_codes
    assert all(
        drift.skill_name not in {"local-helper", "graphify"} for drift in plan.drifts
    )


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


def test_bisync_requires_review_only_for_non_safe_drift() -> None:
    safe_plan = SimpleNamespace(
        blocked_codes=["bisync-only-repo"],
        drifts=[SimpleNamespace(drift_type="only-repo", direction="repo-to-home")],
    )
    review_plan = SimpleNamespace(
        blocked_codes=[],
        drifts=[SimpleNamespace(drift_type="drift", direction="home-to-repo")],
    )

    assert bisync_requires_review(safe_plan) is False
    assert bisync_requires_review(review_plan) is True


def test_skill_run_sh_should_quiet_only_for_compact_modes() -> None:
    run_sh = (
        REPO_ROOT
        / ".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
    ).resolve().as_posix()
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


def test_bisync_apply_requires_reviewed_plan_snapshot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo_root = tmp_path / "repo"
    home_root = tmp_path / "home"
    refs_dir = (
        repo_root
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
              include_unlisted_skills: false
              unmanaged_existing_skills_policy: block
              excluded_skills: []
              skill_targets:
                - codex
            resources: []
            """
        ),
        encoding="utf-8",
    )
    (repo_root / ".github" / "skills" / "demo-skill").mkdir(parents=True)
    (repo_root / ".github" / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# demo\n", encoding="utf-8"
    )
    (home_root / ".agents" / "skills").mkdir(parents=True)

    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "review@example.com"], cwd=repo_root, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "reviewer"], cwd=repo_root, check=True
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo_root, check=True)

    args = argparse.Namespace(
        source_root=repo_root.as_posix(),
        home_root=home_root.as_posix(),
        format="compact",
        compact=True,
    )

    assert run_bisync_apply(args) == 1
    payload = json.loads(capsys.readouterr().out)
    assert "bisync-plan-required" in payload["blockers"]


def test_bisync_apply_uses_matching_reviewed_plan_snapshot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo_root = tmp_path / "repo"
    home_root = tmp_path / "home"
    refs_dir = (
        repo_root
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
              include_unlisted_skills: false
              unmanaged_existing_skills_policy: block
              excluded_skills: []
              skill_targets:
                - codex
            resources: []
            """
        ),
        encoding="utf-8",
    )
    (repo_root / ".github" / "skills" / "demo-skill").mkdir(parents=True)
    (repo_root / ".github" / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# demo\n", encoding="utf-8"
    )
    (home_root / ".agents" / "skills").mkdir(parents=True)

    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "review@example.com"], cwd=repo_root, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "reviewer"], cwd=repo_root, check=True
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo_root, check=True)

    args = argparse.Namespace(
        source_root=repo_root.as_posix(),
        home_root=home_root.as_posix(),
        format="compact",
        compact=True,
    )

    assert run_bisync_plan(args) == 1
    _ = capsys.readouterr()

    assert run_bisync_apply(args) == 0
    assert (home_root / ".agents" / "skills" / "demo-skill" / "SKILL.md").is_file()


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

    copy_paths = [
        operation.path for operation in plan.operations if operation.action == "copy"
    ]
    assert (
        copy_paths.count(
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
