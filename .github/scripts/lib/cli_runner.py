"""Compatibility exports for the pre-package command-runner API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from copilot_tools.cli import FindingLike, has_severity, run_finding_cli, should_fail
