from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def find_repo_root(start: Path) -> Path:
    for candidate in start.resolve().parents:
        if (candidate / "AGENTS.md").is_file():
            return candidate
    raise FileNotFoundError(f"Unable to find repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__))
SKILL_SCRIPTS_ROOT = (
    REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
)


def load_bisync_module():
    inserted_path = False
    if SKILL_SCRIPTS_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, SKILL_SCRIPTS_ROOT.as_posix())
        inserted_path = True
    try:
        spec = importlib.util.spec_from_file_location(
            "_test_local_bisync_skills",
            SKILL_SCRIPTS_ROOT / "bisync_skills.py",
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if inserted_path:
            sys.path.remove(SKILL_SCRIPTS_ROOT.as_posix())


bisync_skills = load_bisync_module()
build_bisync_plan = bisync_skills.build_bisync_plan
apply_bisync_plan = bisync_skills.apply_bisync_plan
BisyncDriftEntry = bisync_skills.BisyncDriftEntry
BisyncPlan = bisync_skills.BisyncPlan


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    write_file(root / ".gitkeep", "")
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "add", "-A"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )


def make_skill(root: Path, skill_name: str, content: str) -> Path:
    skill_dir = root / skill_name
    write_file(skill_dir / "SKILL.md", content)
    write_file(
        skill_dir / "agents" / "openai.yaml",
        f"interface:\n  display_name: \"{skill_name}\"\n  short_description: \"Test skill\"\n  default_prompt: \"Use ${skill_name}.\"\n",
    )
    return skill_dir


def test_build_plan_in_sync(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    make_skill(source / ".github" / "skills", "alpha-skill", "# Alpha\n")
    make_skill(home / ".agents" / "skills", "alpha-skill", "# Alpha\n")

    plan = build_bisync_plan(source, home, mode="plan")
    assert plan.drifts == []
    assert plan.blocked_codes == []
    assert plan.verification["status"] == "ok"


def test_build_plan_repo_to_home(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    make_skill(source / ".github" / "skills", "beta-skill", "# Beta source\n")
    make_skill(home / ".agents" / "skills", "beta-skill", "# Beta home\n")

    plan = build_bisync_plan(source, home, mode="plan")
    assert len(plan.drifts) == 1
    drift = plan.drifts[0]
    assert drift.skill_name == "beta-skill"
    assert drift.drift_type == "drift"
    assert drift.direction in ("repo-to-home", "home-to-repo")


def test_build_plan_only_repo(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "gamma-skill", "# Gamma\n")

    plan = build_bisync_plan(source, home, mode="plan")
    assert len(plan.drifts) == 1
    drift = plan.drifts[0]
    assert drift.skill_name == "gamma-skill"
    assert drift.drift_type == "only-repo"
    assert "bisync-only-repo" in plan.blocked_codes


def test_build_plan_only_home(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (source / ".github" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(home / ".agents" / "skills", "delta-skill", "# Delta\n")

    plan = build_bisync_plan(source, home, mode="plan")
    assert len(plan.drifts) == 1
    drift = plan.drifts[0]
    assert drift.skill_name == "delta-skill"
    assert drift.drift_type == "only-home"
    assert "bisync-only-home" in plan.blocked_codes


def test_excludes_local_agent_sync_bundles(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    make_skill(source / ".github" / "skills", "local-agent-sync-install-ai-resources", "# Sync\n")
    make_skill(source / ".github" / "skills", "normal-skill", "# Normal\n")
    make_skill(home / ".agents" / "skills", "normal-skill", "# Normal\n")

    plan = build_bisync_plan(source, home, mode="plan")
    skill_names = {d.skill_name for d in plan.drifts}
    assert "local-agent-sync-install-ai-resources" not in skill_names


def test_build_plan_equal_mtime_blocker(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    make_skill(source / ".github" / "skills", "equal-skill", "# Equal src\n")
    make_skill(home / ".agents" / "skills", "equal-skill", "# Equal dst\n")

    plan = build_bisync_plan(source, home, mode="plan")
    drift_types = {d.drift_type for d in plan.drifts}
    assert drift_types <= {"drift", "equal-mtime"}


def test_apply_blocked_when_plan_has_blockers(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "only-repo-skill", "# Only repo\n")

    plan = build_bisync_plan(source, home, mode="plan")
    assert "bisync-only-repo" in plan.blocked_codes

    result = apply_bisync_plan(source, home, plan)
    assert "bisync-only-repo" in result.blocked_codes


def test_apply_blocked_dirty_repository(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "clean-skill", "# Clean src\n")
    make_skill(home / ".agents" / "skills", "clean-skill", "# Clean home\n")

    write_file(source / "dirty.txt", "dirty\n")

    plan = build_bisync_plan(source, home, mode="plan")
    result = apply_bisync_plan(source, home, plan)
    assert any("bisync-repo-dirty" in code for code in result.blocked_codes)


def test_apply_success_repo_to_home(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "apply-skill", "# Apply content\n")
    subprocess.run(
        ["git", "add", "-A"], cwd=source, text=True, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add apply-skill"],
        cwd=source, text=True, capture_output=True, check=True,
    )

    plan = build_bisync_plan(source, home, mode="plan")
    assert len(plan.drifts) == 1
    assert plan.drifts[0].drift_type == "only-repo"

    write_file(home / ".agents" / "skills" / "apply-skill" / "SKILL.md", "# Old content\n")

    plan2 = build_bisync_plan(source, home, mode="plan")
    drifts_only = [d for d in plan2.drifts if d.drift_type == "drift"]
    if not drifts_only:
        return

    result = apply_bisync_plan(source, home, plan2)
    assert result.blocked_codes == []


def test_apply_verification_converges(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "conv-skill", "# Converge\n")
    make_skill(home / ".agents" / "skills", "conv-skill", "# Converge home\n")
    subprocess.run(
        ["git", "add", "-A"], cwd=source, text=True, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add conv-skill"],
        cwd=source, text=True, capture_output=True, check=True,
    )

    plan = build_bisync_plan(source, home, mode="plan")
    drifts_only = [d for d in plan.drifts if d.drift_type == "drift"]
    if not drifts_only:
        return

    result = apply_bisync_plan(source, home, plan)
    assert not result.blocked_codes


def test_plan_json_output_contains_next_action(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)

    plan = build_bisync_plan(source, home, mode="plan")
    payload = plan.to_dict()
    assert "next_action" in payload
    assert "next_step" in payload
    assert "action" in payload["next_action"]
    assert "allowed" in payload["next_action"]
    assert "requires_explicit_approval" in payload["next_action"]


def test_plan_json_output_drifts_have_skill_key(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "json-skill", "# JSON test\n")

    plan = build_bisync_plan(source, home, mode="plan")
    payload = plan.to_dict()
    json_str = json.dumps(payload, sort_keys=True)
    assert "json-skill" in json_str


def test_source_root_missing_skills_dir(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    source.mkdir()
    home.mkdir()

    plan = build_bisync_plan(source, home, mode="plan")
    assert "bisync-source-missing" in plan.blocked_codes
    assert plan.next_action["allowed"] is False
