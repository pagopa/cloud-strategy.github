"""Shared repository root discovery."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")
