"""Compatibility exports for the pre-package inventory API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from copilot_tools.inventory import (
    DOCUMENT_SUPPORT_ONLY_SKILLS,
    EMPTY_MESSAGES,
    IGNORED_SCRIPT_BASENAMES,
    IGNORED_SCRIPT_PARTS,
    SCRIPT_GLOB_PATTERNS,
    SECTION_ORDER,
    build_inventory_markdown,
    collect_inventory_sections,
    parse_inventory_markdown,
    render_inventory_markdown,
    sections_from_catalog_paths,
    write_inventory,
)
