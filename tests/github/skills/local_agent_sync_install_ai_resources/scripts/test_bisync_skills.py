from __future__ import annotations

import importlib.util
import json
import os
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
apply_bisync_plan = bisync_skills.apply_bisync_plan
build_bisync_plan = bisync_skills.build_bisync_plan
BisyncDriftEntry = bisync_skills.BisyncDriftEntry
BisyncPlan = bisync_skills.BisyncPlan


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    write_file(root / "AGENTS.md", "# AGENTS\n")
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


def commit_all(root: Path, message: str) -> None:
    subprocess.run(
        ["git", "add", "-A"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", message],
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
        "interface:\n"
        f'  display_name: "{skill_name}"\n'
        '  short_description: "Test skill"\n'
        f'  default_prompt: "Use ${skill_name}."\n',
    )
    return skill_dir


def set_tree_mtime(root: Path, timestamp: float) -> None:
    for path in sorted(root.rglob("*")):
        os.utime(path, (timestamp, timestamp))
    os.utime(root, (timestamp, timestamp))


def test_build_plan_in_sync_with_ignored_runtime_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(source / ".github" / "skills", "alpha-skill", "# Alpha\n")
    home_skill = make_skill(home / ".agents" / "skills", "alpha-skill", "# Alpha\n")
    write_file(source_skill / "__pycache__" / "ignored.pyc", "source\n")
    write_file(home_skill / "__pycache__" / "ignored.pyc", "home\n")
    write_file(source_skill / ".venv" / "marker.txt", "source\n")
    write_file(home_skill / ".venv" / "marker.txt", "home\n")

    plan = build_bisync_plan(source, home, mode="plan")

    assert plan.drifts == []
    assert plan.blocked_codes == []
    assert plan.verification["status"] == "ok"


def test_build_plan_detects_repo_to_home_direction(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "beta-skill", "# Beta source\n"
    )
    home_skill = make_skill(home / ".agents" / "skills", "beta-skill", "# Beta home\n")
    set_tree_mtime(home_skill, 100.0)
    set_tree_mtime(source_skill, 200.0)

    plan = build_bisync_plan(source, home, mode="plan")

    assert len(plan.drifts) == 1
    drift = plan.drifts[0]
    assert drift.skill_name == "beta-skill"
    assert drift.drift_type == "drift"
    assert drift.direction == "repo-to-home"


def test_build_plan_detects_home_to_repo_direction(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "gamma-skill", "# Gamma source\n"
    )
    home_skill = make_skill(
        home / ".agents" / "skills", "gamma-skill", "# Gamma home\n"
    )
    set_tree_mtime(source_skill, 100.0)
    set_tree_mtime(home_skill, 200.0)

    plan = build_bisync_plan(source, home, mode="plan")

    assert len(plan.drifts) == 1
    drift = plan.drifts[0]
    assert drift.skill_name == "gamma-skill"
    assert drift.drift_type == "drift"
    assert drift.direction == "home-to-repo"


def test_build_plan_blocks_equal_mtime(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "equal-skill", "# Equal source\n"
    )
    home_skill = make_skill(
        home / ".agents" / "skills", "equal-skill", "# Equal home\n"
    )
    set_tree_mtime(source_skill, 100.0)
    set_tree_mtime(home_skill, 100.0)

    plan = build_bisync_plan(source, home, mode="plan")

    assert len(plan.drifts) == 1
    assert plan.drifts[0].drift_type == "equal-mtime"
    assert plan.blocked_codes == ["bisync-equal-mtime"]
    assert plan.next_action["allowed"] is False


def test_build_plan_blocks_only_repo_and_only_home(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "repo-only", "# Repo only\n")
    make_skill(home / ".agents" / "skills", "home-only", "# Home only\n")

    plan = build_bisync_plan(source, home, mode="plan")

    drift_types = {drift.skill_name: drift.drift_type for drift in plan.drifts}
    assert drift_types == {"repo-only": "only-repo", "home-only": "only-home"}
    assert plan.blocked_codes == ["bisync-only-home", "bisync-only-repo"]


def test_excludes_local_agent_sync_bundles_from_scan(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    make_skill(
        source / ".github" / "skills",
        "local-agent-sync-install-ai-resources",
        "# Sync bundle\n",
    )
    make_skill(
        home / ".agents" / "skills",
        "local-agent-sync-install-ai-resources",
        "# Diverged sync bundle\n",
    )
    make_skill(source / ".github" / "skills", "normal-skill", "# Normal\n")
    make_skill(home / ".agents" / "skills", "normal-skill", "# Normal\n")

    plan = build_bisync_plan(source, home, mode="plan")

    assert {drift.skill_name for drift in plan.drifts} == set()


def test_apply_blocks_dirty_repository_without_writes(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "dirty-skill", "# Source\n"
    )
    home_skill = make_skill(home / ".agents" / "skills", "dirty-skill", "# Home\n")
    set_tree_mtime(home_skill, 100.0)
    set_tree_mtime(source_skill, 200.0)
    write_file(source / "dirty.txt", "dirty\n")

    plan = build_bisync_plan(source, home, mode="plan")
    result = apply_bisync_plan(source, home, plan)

    assert result.blocked_codes == ["bisync-repo-dirty"]
    assert result.verification["code"] == "bisync-repo-dirty"
    assert (home_skill / "SKILL.md").read_text(encoding="utf-8") == "# Home\n"


def test_apply_repo_to_home_blocks_without_manifest_reconciliation(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "apply-skill", "# Source\n"
    )
    home_skill = make_skill(home / ".agents" / "skills", "apply-skill", "# Home\n")
    set_tree_mtime(home_skill, 100.0)
    set_tree_mtime(source_skill, 200.0)
    commit_all(source, "add apply-skill")

    plan = build_bisync_plan(source, home, mode="plan")
    result = apply_bisync_plan(source, home, plan)

    assert result.blocked_codes == ["bisync-manifest-reconcile-failed"]
    assert result.verification["code"] == "bisync-manifest-reconcile-failed"
    assert (home_skill / "SKILL.md").read_text(encoding="utf-8") == "# Source\n"
    assert result.next_action["allowed"] is False


def test_apply_home_to_repo_converges(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(source / ".github" / "skills", "return-skill", "# Repo\n")
    home_skill = make_skill(home / ".agents" / "skills", "return-skill", "# Home\n")
    set_tree_mtime(source_skill, 100.0)
    set_tree_mtime(home_skill, 200.0)
    commit_all(source, "add return-skill")

    plan = build_bisync_plan(source, home, mode="plan")
    result = apply_bisync_plan(source, home, plan)

    assert result.blocked_codes == []
    assert result.verification["status"] == "converged"
    assert (source_skill / "SKILL.md").read_text(encoding="utf-8") == "# Home\n"
    verify_plan = build_bisync_plan(source, home, mode="plan")
    assert verify_plan.drifts == []


def test_apply_reports_verify_failure_with_stable_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "verify-skill", "# Source\n"
    )
    home_skill = make_skill(home / ".agents" / "skills", "verify-skill", "# Home\n")
    set_tree_mtime(home_skill, 100.0)
    set_tree_mtime(source_skill, 200.0)
    commit_all(source, "add verify-skill")

    plan = build_bisync_plan(source, home, mode="plan")
    original_hash_bundle = bisync_skills.hash_bundle

    def fake_hash_bundle(path: Path) -> str:
        if path == home_skill:
            return "bad-hash"
        return original_hash_bundle(path)

    monkeypatch.setattr(bisync_skills, "hash_bundle", fake_hash_bundle)
    result = apply_bisync_plan(source, home, plan)

    assert result.blocked_codes == ["bisync-verify-failed"]
    assert result.verification["code"] == "bisync-verify-failed"
    assert result.verification["skill"] == "verify-skill"


def test_apply_reports_residual_drift_with_stable_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    source_skill = make_skill(
        source / ".github" / "skills", "residual-skill", "# Source\n"
    )
    home_skill = make_skill(home / ".agents" / "skills", "residual-skill", "# Home\n")
    set_tree_mtime(home_skill, 100.0)
    set_tree_mtime(source_skill, 200.0)
    commit_all(source, "add residual-skill")

    state_root = home / ".sync/cloud-strategy-governance/home-ai-resources"
    state_root.mkdir(parents=True, exist_ok=True)
    manifest_path = state_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": "2026-06-09T00:00:00Z",
                "source_root": source.as_posix(),
                "source_revision": "initial",
                "state_root": state_root.as_posix(),
                "targets": ["skills"],
                "managed_resources": [
                    {
                        "target": "skills",
                        "resource_family": "skills",
                        "resource_id": "residual-skill",
                        "source_path": ".github/skills/residual-skill",
                        "target_path": home_skill.as_posix(),
                        "source_hash": bisync_skills.hash_bundle(source_skill),
                        "content_hash": bisync_skills.hash_bundle(home_skill),
                        "last_action": "copy",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    plan = build_bisync_plan(source, home, mode="plan")
    original_build_bisync_plan = bisync_skills.build_bisync_plan

    def fake_build_bisync_plan(
        source_root: Path,
        home_root: Path,
        *,
        mode: str = "plan",
    ) -> BisyncPlan:
        if mode == "verify":
            return BisyncPlan(
                source_root=source_root,
                home_root=home_root,
                source_skills_root=source_root / ".github" / "skills",
                home_skills_root=home_root / ".agents" / "skills",
                mode=mode,
                drifts=[
                    BisyncDriftEntry(
                        skill_name="residual-skill",
                        drift_type="drift",
                        direction="repo-to-home",
                        repo_path=(
                            source_root / ".github" / "skills" / "residual-skill"
                        ).as_posix(),
                        home_path=(
                            home_root / ".agents" / "skills" / "residual-skill"
                        ).as_posix(),
                    )
                ],
                blocked_codes=[],
            )
        return original_build_bisync_plan(source_root, home_root, mode=mode)

    monkeypatch.setattr(bisync_skills, "build_bisync_plan", fake_build_bisync_plan)
    result = apply_bisync_plan(source, home, plan)

    assert "bisync-residual-drift" in result.blocked_codes
    assert result.verification["code"] == "bisync-residual-drift"
    assert result.next_action["allowed"] is False


def test_plan_json_output_contains_structured_next_action(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    (home / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    make_skill(source / ".github" / "skills", "json-skill", "# JSON test\n")

    plan = build_bisync_plan(source, home, mode="plan")
    payload = plan.to_dict()
    json_str = json.dumps(payload, sort_keys=True)

    assert "json-skill" in json_str
    assert payload["next_action"]["action"] == "resolve_blockers"
    assert payload["next_action"]["allowed"] is False
    assert payload["next_action"]["requires_explicit_approval"] is True


def test_emit_text_output_groups_repo_home_buckets(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    init_git_repo(source)
    make_skill(source / ".github" / "skills", "repo-only", "# Repo only\n")
    make_skill(home / ".agents" / "skills", "home-only", "# Home only\n")
    source_skill = make_skill(source / ".github" / "skills", "direction-skill", "# Repo\n")
    home_skill = make_skill(home / ".agents" / "skills", "direction-skill", "# Home\n")
    set_tree_mtime(home_skill, 100.0)
    set_tree_mtime(source_skill, 200.0)

    plan = build_bisync_plan(source, home, mode="plan")
    bisync_skills._emit_bisync_output(plan, "text")
    output = capsys.readouterr().out

    assert "repo-only" in output
    assert "home-only" in output
    assert "repo-to-home" in output
    assert "winner: repo" in output
    assert "loser: home" in output
    assert "blocker: bisync-only-repo" in output


def test_source_root_missing_skills_dir_returns_blocker(tmp_path: Path) -> None:
    source = tmp_path / "source"
    home = tmp_path / "home"
    source.mkdir()
    home.mkdir()

    plan = build_bisync_plan(source, home, mode="plan")

    assert "bisync-source-missing" in plan.blocked_codes
    assert plan.next_action["allowed"] is False
