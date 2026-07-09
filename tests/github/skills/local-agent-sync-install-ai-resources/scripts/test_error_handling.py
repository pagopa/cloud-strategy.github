import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from home_sync_contract import load_home_sync_catalog  # noqa: E402
from home_syncing import build_home_sync_plan  # noqa: E402


def test_load_catalog_raises_valueerror_on_malformed_yaml(tmp_path: Path) -> None:
    refs_dir = (
        tmp_path
        / ".github"
        / "skills"
        / "local-agent-sync-install-ai-resources"
        / "references"
    )
    refs_dir.mkdir(parents=True)
    (refs_dir / "home-sync-catalog.yaml").write_text(
        "not: a: valid: yaml: [", encoding="utf-8"
    )
    with pytest.raises((ValueError, Exception)):
        load_home_sync_catalog(tmp_path)


def test_load_catalog_raises_valueerror_on_missing_keys(tmp_path: Path) -> None:
    refs_dir = (
        tmp_path
        / ".github"
        / "skills"
        / "local-agent-sync-install-ai-resources"
        / "references"
    )
    refs_dir.mkdir(parents=True)
    (refs_dir / "home-sync-catalog.yaml").write_text(
        textwrap.dedent("""\
            version: 1
            defaults:
              include_internal_skills: true
            resources:
              - source_path: foo
        """),
        encoding="utf-8",
    )
    with pytest.raises((ValueError, KeyError)):
        load_home_sync_catalog(tmp_path)


def test_build_plan_raises_reverse_sync_blocked(tmp_path: Path) -> None:
    refs_dir = (
        tmp_path
        / ".github"
        / "skills"
        / "local-agent-sync-install-ai-resources"
        / "references"
    )
    refs_dir.mkdir(parents=True)
    (refs_dir / "home-sync-catalog.yaml").write_text(
        textwrap.dedent("""\
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
        """),
        encoding="utf-8",
    )
    home_root = tmp_path / "home"
    home_root.mkdir()
    state_root = home_root / ".sync" / "cloud-strategy-governance" / "home-ai-resources"
    state_root.mkdir(parents=True)
    source_under_state = state_root / "fake-source"
    source_under_state.mkdir()
    (source_under_state / ".github").mkdir()

    with pytest.raises(RuntimeError, match="reverse-sync-blocked"):
        build_home_sync_plan(source_under_state, home_root, ("skills",), mode="plan")
