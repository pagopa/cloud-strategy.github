import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.shared import git_dirty_paths, git_revision, is_git_dirty


def test_git_revision_handles_timeout(tmp_path: Path) -> None:
    with patch(
        "lib.shared.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)
    ):
        result = git_revision(tmp_path)
    assert result is None


def test_is_git_dirty_handles_timeout(tmp_path: Path) -> None:
    with patch(
        "lib.shared.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)
    ):
        result = is_git_dirty(tmp_path)
    assert result is False


def test_git_dirty_paths_handles_timeout(tmp_path: Path) -> None:
    with patch(
        "lib.shared.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)
    ):
        result = git_dirty_paths(tmp_path)
    assert result == []
