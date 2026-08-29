"""Compatibility exports for the pre-package sync-exclusion API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from copilot_tools.core.sync_exclusions import (
    RUNTIME_SYNC_IGNORED_PARTS,
    RUNTIME_SYNC_IGNORED_SUFFIXES,
    should_ignore_sync_path,
    sync_copytree_ignore,
)

IGNORED_SYNC_PARTS = RUNTIME_SYNC_IGNORED_PARTS
IGNORED_SYNC_SUFFIXES = RUNTIME_SYNC_IGNORED_SUFFIXES
