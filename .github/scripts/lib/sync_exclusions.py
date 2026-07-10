"""Shared sync exclusion rules for runtime artifacts."""

from __future__ import annotations

from pathlib import Path

IGNORED_SYNC_PARTS: frozenset[str] = frozenset({
    ".venv",
    "__pycache__",
    ".pytest_cache",
})

IGNORED_SYNC_SUFFIXES: frozenset[str] = frozenset({
    ".pyc",
    ".pyo",
})


def should_ignore_sync_path(path: Path) -> bool:
    parts = path.parts
    if any(part in IGNORED_SYNC_PARTS for part in parts):
        return True
    if path.suffix in IGNORED_SYNC_SUFFIXES:
        return True
    return False


def sync_copytree_ignore(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        candidate = Path(directory) / name
        if should_ignore_sync_path(candidate):
            ignored.add(name)
    return ignored
