import argparse
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT_DIR = Path(
    ".github/skills/local-agent-sync-install-ai-resources/scripts"
).resolve()
sys.path.insert(0, SCRIPT_DIR.as_posix())

from agent_translation import target_extension, translate_agent_for_target  # noqa: E402
from bisync_skills import build_bisync_plan  # noqa: E402
from home_sync_contract import load_home_sync_catalog, load_home_sync_policy  # noqa: E402
from home_syncing import HomeSyncOperation, parse_targets  # noqa: E402
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
                agent: internal-code-review
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
    assert "internal-code-review" in payload["developer_instructions"]


def test_load_home_sync_catalog_autodiscovers_skills_and_honors_policy(tmp_path: Path) -> None:
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
    assert all(drift.skill_name not in {"local-helper", "graphify"} for drift in plan.drifts)


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
        Path(".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh")
        .resolve()
        .as_posix()
    )
    script = textwrap.dedent(
        f"""\
        source <(sed '$d' "{run_sh}")
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
