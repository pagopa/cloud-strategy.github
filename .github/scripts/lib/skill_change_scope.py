"""Compatibility exports for the pre-package protected-skill API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from copilot_tools.checks.skill_change_scope import (
    collect_changed_paths,
    detect_protected_skill_changes,
    protected_skill_bundle,
    validate_allowlist,
)
