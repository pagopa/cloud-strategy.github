from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

SKILL_ROOT_RELATIVE = Path(".github/skills/local-agent-sync-install-ai-resources")
BUNDLED_SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SUPPORT_MATRIX_PATH = Path("references/runtime-support-matrix.yaml")
HOME_SYNC_CATALOG_PATH = Path("references/home-sync-catalog.yaml")
STATE_ROOT_RELATIVE = Path(".sync/cloud-strategy-governance/home-ai-resources")
TARGET_ORDER = ("agents.md", "skills", "codex", "copilot", "opencode")
TARGET_SKILL_ROOTS = {
    "agents.md": Path(".agents"),
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
AGENT_TARGETS = ("codex", "copilot", "opencode")


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


@dataclass(frozen=True)
class HomeSyncPolicy:
    include_local_skills: bool
    include_internal_skills: bool
    include_unlisted_skills: bool
    skill_targets: tuple[str, ...]
    excluded_skills: tuple[str, ...]
    unmanaged_existing_skills_policy: str


def load_runtime_support_matrix(source_root: Path) -> list[RuntimeSupportRow]:
    matrix_path = resolve_skill_reference(source_root, RUNTIME_SUPPORT_MATRIX_PATH)
    try:
        payload = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"manifest-corrupt: failed to parse runtime support matrix: {exc}") from exc
    rows = payload.get("rows", [])
    result = []
    for row in rows:
        evidence_raw = row.get("evidence", [])
        if isinstance(evidence_raw, str):
            raise ValueError("manifest-corrupt: evidence must be a list, got string")
        evidence = tuple(evidence_raw) if isinstance(evidence_raw, list) else ()
        result.append(
            RuntimeSupportRow(
                target=row["target"],
                resource_family=row["resource_family"],
                support_level=row["support_level"],
                home_path=row.get("home_path"),
                direct_copy_possible=bool(row.get("direct_copy_possible")),
                translation_required=bool(row.get("translation_required")),
                include_in_v1=bool(row.get("include_in_v1")),
                evidence=evidence,
                notes=row.get("notes", ""),
            )
        )
    return result


def load_home_sync_catalog(source_root: Path) -> list[CatalogResource]:
    policy = load_home_sync_policy(source_root)
    payload = _load_home_sync_catalog_payload(source_root)
    resources = list(payload.get("resources", []))

    if policy.include_unlisted_skills:
        explicit_ids = {
            (resource.get("resource_id", ""), resource.get("source_family", ""))
            for resource in resources
            if isinstance(resource, dict)
        }
        resources.extend(
            resource
            for resource in discover_skill_resources(
                source_root,
                policy.include_local_skills,
                policy.include_internal_skills,
                policy.skill_targets,
                policy.excluded_skills,
            )
            if (resource["resource_id"], resource["source_family"]) not in explicit_ids
        )

    explicit_agent_ids = {
        (resource.get("resource_id", ""), resource.get("source_family", ""))
        for resource in resources
        if isinstance(resource, dict)
    }
    resources.extend(
        resource
        for resource in discover_agent_resources(source_root)
        if (resource["resource_id"], resource["source_family"]) not in explicit_agent_ids
    )

    filtered = []
    for resource in resources:
        rid = resource.get("resource_id", "")
        source_family = resource.get("source_family", "")
        if source_family == "skills" and rid in policy.excluded_skills:
            continue
        if (
            source_family == "skills"
            and not policy.include_local_skills
            and rid.startswith("local-")
        ):
            continue
        if not policy.include_internal_skills and rid.startswith("internal-"):
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


def load_home_sync_policy(source_root: Path) -> HomeSyncPolicy:
    payload = _load_home_sync_catalog_payload(source_root)
    defaults = payload.get("defaults", {})
    return HomeSyncPolicy(
        include_local_skills=bool(defaults.get("include_local_skills", False)),
        include_internal_skills=bool(defaults.get("include_internal_skills", False)),
        include_unlisted_skills=bool(defaults.get("include_unlisted_skills", False)),
        skill_targets=tuple(defaults.get("skill_targets", ("codex", "copilot", "opencode"))),
        excluded_skills=tuple(sorted(str(skill) for skill in defaults.get("excluded_skills", []))),
        unmanaged_existing_skills_policy=str(
            defaults.get("unmanaged_existing_skills_policy", "block")
        ),
    )


def _load_home_sync_catalog_payload(source_root: Path) -> dict[str, object]:
    catalog_path = resolve_skill_reference(source_root, HOME_SYNC_CATALOG_PATH)
    try:
        return yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"manifest-corrupt: failed to parse home sync catalog: {exc}") from exc


def discover_skill_resources(
    source_root: Path,
    include_local: bool,
    include_internal: bool,
    skill_targets: tuple[str, ...],
    excluded_skills: tuple[str, ...] = (),
) -> list[dict[str, object]]:
    skills_root = source_root / ".github" / "skills"
    if not skills_root.is_dir():
        return []

    resources: list[dict[str, object]] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        resource_id = skill_dir.name
        if resource_id in excluded_skills:
            continue
        if not include_local and resource_id.startswith("local-"):
            continue
        if not include_internal and resource_id.startswith("internal-"):
            continue
        if not (skill_dir / "SKILL.md").is_file():
            continue
        resources.append(
            {
                "resource_id": resource_id,
                "source_family": "skills",
                "source_path": skill_dir.relative_to(source_root).as_posix(),
                "include_targets": list(skill_targets),
                "target_support": "See runtime support matrix",
                "notes": "Auto-discovered skill bundle.",
            }
        )
    return resources


def discover_agent_resources(source_root: Path) -> list[dict[str, object]]:
    resources: list[dict[str, object]] = []
    discovery_roots = (
        (source_root / ".github" / "agents", "*.agent.md", AGENT_TARGETS),
        (source_root / ".codex" / "agents", "*.toml", ("codex",)),
    )
    for agents_root, pattern, targets in discovery_roots:
        if not agents_root.is_dir():
            continue
        for agent_path in sorted(agents_root.glob(pattern)):
            resource_id = agent_path.name.removesuffix(".agent.md").removesuffix(".toml")
            if resource_id.startswith("local-"):
                continue
            resources.append(
                {
                    "resource_id": resource_id,
                    "source_family": "agents",
                    "source_path": agent_path.relative_to(source_root).as_posix(),
                    "include_targets": list(targets),
                    "target_support": "See runtime support matrix",
                    "notes": "Auto-discovered native or portable agent.",
                }
            )
    return resources


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


def resolve_support_row(
    rows: list[RuntimeSupportRow], target: str, resource_family: str
) -> RuntimeSupportRow | None:
    for row in rows:
        if row.target == target and row.resource_family == resource_family:
            return row
    return None
