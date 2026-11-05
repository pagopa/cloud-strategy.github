"""Shared sync exclusion rules for runtime artifacts."""

from __future__ import annotations

from pathlib import Path

RUNTIME_SYNC_IGNORED_PARTS: frozenset[str] = frozenset(
    {
        ".venv",
        "__pycache__",
        ".pytest_cache",
    }
)

RUNTIME_SYNC_IGNORED_SUFFIXES: frozenset[str] = frozenset(
    {
        ".pyc",
        ".pyo",
    }
)


def should_ignore_sync_path(path: Path) -> bool:
    parts = path.parts
    if any(part in RUNTIME_SYNC_IGNORED_PARTS for part in parts):
        return True
    if path.suffix in RUNTIME_SYNC_IGNORED_SUFFIXES:
        return True
    return False


def sync_copytree_ignore(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        candidate = Path(directory) / name
        if should_ignore_sync_path(candidate):
            ignored.add(name)
    return ignored
