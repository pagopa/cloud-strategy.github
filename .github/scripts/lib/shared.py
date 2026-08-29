"""Compatibility exports for the pre-package script API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from __future__ import annotations

from pathlib import Path

from copilot_tools.core.constants import (
    ARCHITECTURE_PATH,
    ARCHITECTURE_TEMPLATE_PATH,
    CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES,
    CONSUMER_SYNC_EXCLUDED_PATH_PREFIXES,
    CONSUMER_SYNC_EXCLUDED_PREFIX,
    DOCS_README_PATH,
    DOCS_README_TEMPLATE_PATH,
    IMPORTED_ASSET_OVERRIDES_PATH,
    INVENTORY_PATH,
    LEGACY_AGENT_TOOL_IDS,
    LEGACY_ARCHITECTURE_PATH,
    LEGACY_LOCAL_ARCHITECTURE_PATH,
    LEGACY_LOCAL_REPOSITORY_CONTEXT_PATH,
    LEGACY_REPOSITORY_CONTEXT_PATH,
    LEGACY_RUNTIME_FIT_PATH,
    LESSONS_PATH,
    MANAGED_EXTERNAL_RESOURCES_PATH,
    MANAGED_ROOT_FILES,
    MANAGED_WORKFLOW_FILES,
    REPOSITORY_CONTEXT_PATH,
    REPOSITORY_CONTEXT_TEMPLATE_PATH,
    RETIRED_RUNTIME_OPERATING_MODEL_PATH,
    STRUCTURE_PATH,
    STRUCTURE_TEMPLATE_PATH,
    TECH_PATH,
    TECH_TEMPLATE_PATH,
    VSCODE_SETTINGS_PATH,
)
from copilot_tools.core.files import read_text, sha256_file, write_text
from copilot_tools.core.findings import (
    Finding,
    SyncOperation,
    SyncPlan,
    action_sort_key,
    finding_sort_key,
)
from copilot_tools.core.markdown import (
    FRONTMATTER_PATTERN,
    load_frontmatter,
    markdown_link_targets,
    normalize_markdown_text,
    significant_text_lines,
    split_frontmatter,
    strip_frontmatter,
)
from copilot_tools.core.output import (
    log_error,
    log_info,
    log_success,
    log_warn,
    render_json,
)
from copilot_tools.core.paths import (
    CATALOG_IGNORED_FILENAMES,
    CATALOG_IGNORED_PARTS,
    all_files_under,
    dedupe_preserve_order,
    is_consumer_sync_excluded_path,
    is_imported_asset,
    is_local_asset,
    iter_markdown_assets,
    path_list,
    resolve_markdown_target,
)
from copilot_tools.core.repo_paths import find_repo_root as _find_repo_root

IGNORED_SYNC_FILENAMES = CATALOG_IGNORED_FILENAMES
IGNORED_SYNC_PARTS = CATALOG_IGNORED_PARTS


def find_repo_root(start: Path) -> Path:
    return _find_repo_root(
        start,
        lambda candidate: (
            (candidate / ".github").is_dir() or (candidate / ".git").exists()
        ),
    )


def is_ignored_sync_path(relative_path: str) -> bool:
    candidate = Path(relative_path)
    return (
        candidate.name in IGNORED_SYNC_FILENAMES
        or candidate.suffix == ".pyc"
        or any(part in IGNORED_SYNC_PARTS for part in candidate.parts)
    )
