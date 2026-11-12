"""Shared repository root discovery."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path


def find_repo_root(start: Path, marker: Callable[[Path], bool]) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if marker(current):
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


def path_exists_at_ref(root: Path, ref: str, path: str) -> bool:
    """Return whether a repository path exists at a Git ref; invalid refs are absent."""

    if not ref or ref.startswith("-"):
        return False
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{ref}:{path}"],
            cwd=root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return True


def iter_test_roots(root: Path) -> tuple[Path, ...]:
    """Return the repository and live skill test roots in stable order."""

    roots: list[Path] = []
    repository_tests = root / "tests"
    if repository_tests.is_dir():
        roots.append(repository_tests)

    skills_root = root / ".github" / "skills"
    if skills_root.is_dir():
        roots.extend(
            skill_dir / "tests"
            for skill_dir in sorted(skills_root.iterdir())
            if skill_dir.is_dir()
            and (skill_dir / "SKILL.md").is_file()
            and (skill_dir / "tests").is_dir()
        )
    return tuple(roots)


def iter_test_python_files(root: Path) -> tuple[Path, ...]:
    """Return Python files below every configured test root."""

    return tuple(
        sorted(
            path
            for test_root in iter_test_roots(root)
            for path in test_root.rglob("*.py")
            if path.is_file()
        )
    )
