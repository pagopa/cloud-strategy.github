from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

SKILL_ROOT = Path(".github/skills/local-agent-sync-home-ai-resources")
RUNTIME_SUPPORT_MATRIX_PATH = SKILL_ROOT / "references/runtime-support-matrix.yaml"
HOME_SYNC_CATALOG_PATH = SKILL_ROOT / "references/home-sync-catalog.yaml"
STATE_ROOT_RELATIVE = Path(".sync/cloud-strategy-governance/home-ai-resources")
TARGET_ORDER = ("codex", "vscode", "antigravity")
TARGET_SKILL_ROOTS = {
    "codex": Path(".agents/skills"),
    "vscode": Path(".copilot/skills"),
    "antigravity": Path(".gemini/antigravity/skills"),
}


@dataclass(frozen=True)
class RuntimeSupportRow:
    target: str
    resource_family: str
    support_level: str
    home_path: str | None
    direct_copy_possible: bool
    translation_required: bool
    include_in_v1: bool
    evidence: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class CatalogResource:
    resource_id: str
    source_family: str
    source_path: str
    include_targets: tuple[str, ...]
    target_support: str
    notes: str


def load_runtime_support_matrix(source_root: Path) -> list[RuntimeSupportRow]:
    matrix_path = source_root / RUNTIME_SUPPORT_MATRIX_PATH
    payload = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    rows = payload.get("rows", [])
    return [
        RuntimeSupportRow(
            target=row["target"],
            resource_family=row["resource_family"],
            support_level=row["support_level"],
            home_path=row.get("home_path"),
            direct_copy_possible=bool(row.get("direct_copy_possible")),
            translation_required=bool(row.get("translation_required")),
            include_in_v1=bool(row.get("include_in_v1")),
            evidence=tuple(row.get("evidence", [])),
            notes=row.get("notes", ""),
        )
        for row in rows
    ]


def load_home_sync_catalog(source_root: Path) -> list[CatalogResource]:
    catalog_path = source_root / HOME_SYNC_CATALOG_PATH
    payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    resources = payload.get("resources", [])
    return [
        CatalogResource(
            resource_id=resource["resource_id"],
            source_family=resource["source_family"],
            source_path=resource["source_path"],
            include_targets=tuple(resource.get("include_targets", [])),
            target_support=resource.get("target_support", "Unknown / To verify"),
            notes=resource.get("notes", ""),
        )
        for resource in resources
    ]


def state_root_for_home(home_root: Path) -> Path:
    return home_root / STATE_ROOT_RELATIVE


def runtime_skill_root(home_root: Path, target: str) -> Path:
    return home_root / TARGET_SKILL_ROOTS[target]


def resolve_support_row(
    rows: list[RuntimeSupportRow], target: str, resource_family: str
) -> RuntimeSupportRow | None:
    for row in rows:
        if row.target == target and row.resource_family == resource_family:
            return row
    return None
