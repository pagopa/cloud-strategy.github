import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.sync_exclusions import (  # noqa: E402
    IGNORED_SYNC_PARTS,
    IGNORED_SYNC_SUFFIXES,
    should_ignore_sync_path,
)


def test_ignored_parts_contain_venv_and_pycache() -> None:
    assert ".venv" in IGNORED_SYNC_PARTS
    assert "__pycache__" in IGNORED_SYNC_PARTS
    assert ".pytest_cache" in IGNORED_SYNC_PARTS


def test_ignored_suffixes_contain_pyc_and_pyo() -> None:
    assert ".pyc" in IGNORED_SYNC_SUFFIXES
    assert ".pyo" in IGNORED_SYNC_SUFFIXES


def test_should_ignore_venv_path() -> None:
    assert should_ignore_sync_path(Path(".venv/lib/site.py"))


def test_should_ignore_pycache() -> None:
    assert should_ignore_sync_path(Path("skills/foo/__pycache__/mod.pyc"))


def test_should_not_ignore_normal_path() -> None:
    assert not should_ignore_sync_path(Path("skills/foo/SKILL.md"))
