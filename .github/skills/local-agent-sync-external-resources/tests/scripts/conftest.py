import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
# Test modules import the bundle scripts at collection time.
if SCRIPT_DIR.as_posix() not in sys.path:
    sys.path.insert(0, SCRIPT_DIR.as_posix())


def _run_git(cwd: Path, args: list[str]) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_all(repo: Path) -> None:
    _run_git(repo, ["add", "-A"])
    _run_git(repo, ["commit", "-m", "snapshot", "--allow-empty"])


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def script_dir() -> Path:
    return SCRIPT_DIR


@pytest.fixture
def run_git() -> Callable[[Path, list[str]], None]:
    return _run_git


@pytest.fixture
def commit_all() -> Callable[[Path], None]:
    return _commit_all
