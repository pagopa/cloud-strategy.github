"""Shared repository root discovery."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


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
