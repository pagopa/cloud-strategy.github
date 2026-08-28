import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.repo_paths import (  # noqa: E402
    find_repo_root,
    iter_test_python_files,
    iter_test_roots,
)


def test_find_repo_root_from_nested_path(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    assert find_repo_root(nested) == tmp_path


def test_find_repo_root_raises_when_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Unable to find repository root"):
        find_repo_root(tmp_path)


def test_iter_test_roots_includes_root_and_live_skill_tests(tmp_path: Path) -> None:
    repository_tests = tmp_path / "tests"
    repository_tests.mkdir()
    skill_tests = tmp_path / ".github/skills/internal-example/tests"
    skill_tests.mkdir(parents=True)
    (skill_tests.parent / "SKILL.md").write_text("# Example\n", encoding="utf-8")
    (repository_tests / "test_root.py").write_text("\n", encoding="utf-8")
    skill_test = skill_tests / "test_skill.py"
    skill_test.write_text("\n", encoding="utf-8")

    assert iter_test_roots(tmp_path) == (repository_tests, skill_tests)
    assert iter_test_python_files(tmp_path) == (
        skill_test,
        repository_tests / "test_root.py",
    )
