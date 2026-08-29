"""Compatibility exports for the pre-package catalog checks API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from __future__ import annotations

from pathlib import Path

from copilot_tools.checks.catalog import (
    RESIDUAL_INSTRUCTION_REFERENCE_PATTERNS,
    SOURCE_INSTRUCTION_REVIEW_MARKER,
    check_bridge_references,
    check_broken_local_links,
    check_duplicate_frontmatter_names,
    check_external_resource_manifest,
    check_imported_asset_overrides,
    check_internal_agent_contracts,
    check_inventory_matches_filesystem,
    check_prompt_contracts,
    check_repo_owned_agent_sections,
    check_required_bridge_files,
    check_residual_instruction_family_references,
    check_source_instruction_contracts,
    check_superpowers_import_naming,
    collect_catalog_candidate_paths,
    collect_repository_owned_markdown_paths,
    normalize_agent_tools,
)
from copilot_tools.checks.catalog import (
    run_consistency_checks as _run_consistency_checks,
)
from copilot_tools.checks.token_risks import detect_token_risks
from copilot_tools.core.findings import Finding


def run_consistency_checks(
    root: Path, include_token_risks: bool = False
) -> list[Finding]:
    return _run_consistency_checks(
        root,
        include_token_risks=include_token_risks,
        token_risk_detector=detect_token_risks if include_token_risks else None,
    )
