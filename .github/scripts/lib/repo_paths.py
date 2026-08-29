"""Compatibility exports for the pre-package repository-path API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from __future__ import annotations

from pathlib import Path

from copilot_tools.core.repo_paths import (
    find_repo_root as _find_repo_root,
)
from copilot_tools.core.repo_paths import (
    iter_test_python_files,
    iter_test_roots,
)


def find_repo_root(start: Path) -> Path:
    return _find_repo_root(
        start,
        lambda candidate: (candidate / ".github").is_dir(),
    )
