import pytest
from pathlib import Path
import sys

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.repo_paths import find_repo_root


def test_find_repo_root_from_nested_path(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    assert find_repo_root(nested) == tmp_path


def test_find_repo_root_raises_when_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Unable to find repository root"):
        find_repo_root(tmp_path)
