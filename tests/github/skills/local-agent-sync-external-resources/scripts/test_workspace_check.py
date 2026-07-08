import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from check_external_refresh_workspace import (  # noqa: E402
    validate_workspace,
    find_repo_local_refresh_dirs,
)


def test_validate_workspace_blocks_inside_repo(tmp_path: Path) -> None:
    workspace = tmp_path / "subdir"
    workspace.mkdir()
    findings = validate_workspace(tmp_path, workspace)
    assert len(findings) == 1
    assert "outside the repository" in findings[0]


def test_validate_workspace_allows_outside_repo(tmp_path: Path) -> None:
    workspace = tmp_path / "external-workspace"
    workspace.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    findings = validate_workspace(repo, workspace)
    assert findings == []


def test_validate_workspace_no_check_when_none(tmp_path: Path) -> None:
    findings = validate_workspace(tmp_path, None)
    assert findings == []


def test_find_repo_local_refresh_dirs_detects_leftovers(tmp_path: Path) -> None:
    (tmp_path / "tmp" / "external-refresh").mkdir(parents=True)
    dirs = find_repo_local_refresh_dirs(tmp_path)
    assert "tmp/external-refresh" in dirs


def test_find_repo_local_refresh_dirs_empty_when_clean(tmp_path: Path) -> None:
    dirs = find_repo_local_refresh_dirs(tmp_path)
    assert dirs == []
