from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

SKILL_ROOT_RELATIVE = Path(".github/skills/local-agent-sync-install-ai-resources")
BUNDLED_SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SUPPORT_MATRIX_PATH = Path("references/runtime-support-matrix.yaml")
HOME_SYNC_CATALOG_PATH = Path("references/home-sync-catalog.yaml")
STATE_ROOT_RELATIVE = Path(".sync/cloud-strategy-governance/home-ai-resources")
TARGET_ORDER = ("skills", "codex", "copilot", "opencode")
TARGET_SKILL_ROOTS = {
    "skills": Path(".agents/skills"),
    "codex": Path(".agents/skills"),
    "copilot": Path(".agents/skills"),
    "opencode": Path(".agents/skills"),
}
TARGET_AGENT_ROOTS = {
    "codex": Path(".codex/agents"),
    "copilot": Path(".copilot/agents"),
    "opencode": Path(".config/opencode/agents"),
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
    matrix_path = resolve_skill_reference(source_root, RUNTIME_SUPPORT_MATRIX_PATH)
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
    catalog_path = resolve_skill_reference(source_root, HOME_SYNC_CATALOG_PATH)
    payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    resources = payload.get("resources", [])
    defaults = payload.get("defaults", {})
    include_local = bool(defaults.get("include_local_skills", False))
    filtered = []
    for resource in resources:
        rid = resource.get("resource_id", "")
        if not include_local and rid.startswith("local-"):
            continue
        filtered.append(resource)
    return [
        CatalogResource(
            resource_id=resource["resource_id"],
            source_family=resource["source_family"],
            source_path=resource["source_path"],
            include_targets=tuple(resource.get("include_targets", [])),
            target_support=resource.get("target_support", "Unknown / To verify"),
            notes=resource.get("notes", ""),
        )
        for resource in filtered
    ]


def resolve_skill_reference(source_root: Path, relative_path: Path) -> Path:
    source_candidate = source_root / SKILL_ROOT_RELATIVE / relative_path
    if source_candidate.exists():
        return source_candidate

    bundled_candidate = BUNDLED_SKILL_ROOT / relative_path
    if bundled_candidate.exists():
        return bundled_candidate

    raise FileNotFoundError(f"Unable to find bundled reference: {relative_path.as_posix()}")


def state_root_for_home(home_root: Path) -> Path:
    return home_root / STATE_ROOT_RELATIVE


def runtime_skill_root(home_root: Path, target: str) -> Path:
    return home_root / TARGET_SKILL_ROOTS[target]


def runtime_agent_root(home_root: Path, target: str) -> Path:
    return home_root / TARGET_AGENT_ROOTS[target]


def has_agent_root(target: str) -> bool:
    return target in TARGET_AGENT_ROOTS


def load_agent_catalog(source_root: Path) -> list[CatalogResource]:
    catalog = load_home_sync_catalog(source_root)
    return [resource for resource in catalog if resource.source_family == "agents"]


def resolve_support_row(
    rows: list[RuntimeSupportRow], target: str, resource_family: str
) -> RuntimeSupportRow | None:
    for row in rows:
        if row.target == target and row.resource_family == resource_family:
            return row
    return None
