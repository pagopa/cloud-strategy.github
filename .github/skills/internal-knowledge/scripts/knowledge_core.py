#!/usr/bin/env python3
"""Repository knowledge discovery, reporting, and manifest helpers."""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

import yaml


PROTECTED_WRITES = frozenset({"AGENTS.md", "AGENTS.local.md"})
ADR_FILE_RE = re.compile(r"^(?P<number>\d{4})-[a-z0-9][a-z0-9-]*\.md$")
ADR_HEADING_RE = re.compile(r"^# ADR-(?P<number>\d{4}): .+", re.MULTILINE)
STATUS_RE = re.compile(r"^- Status: (?P<status>.+)$", re.MULTILINE)
REQUIRED_ADR_SECTIONS = ("## Decision", "## Rationale", "## Consequences")
RESOURCE_RE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')
DATA_RE = re.compile(r'data\s+"([^"]+)"\s+"([^"]+)"')
MODULE_SOURCE_RE = re.compile(r'source\s*=\s*"([^"]+)"')
USES_RE = re.compile(r"""uses:\s*['\"]?([^\s'\"]+)""")
RUN_PATH_RE = re.compile(r"""(?:\./)?((?:src/)?scripts/[^\s'\"]+)""")
BACKEND_RE = re.compile(r"\bbackend\s+\"")
CONFIG_FIELDS = (
    "scan_roots",
    "exclusions",
    "expected_assets",
    "canonical_documents",
    "coverage_rules",
)
COVERAGE_REQUIREMENTS = ("readme",)


class KnowledgeConfigError(ValueError):
    """Raised when an explicitly supplied knowledge config is invalid."""


def empty_knowledge_config() -> dict[str, object]:
    return {
        "scan_roots": [],
        "exclusions": [],
        "expected_assets": {},
        "canonical_documents": [],
        "coverage_rules": {},
    }


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise KnowledgeConfigError(f"{field} must be a list of strings")
    return [item.strip() for item in value]


def _string_map(value: object, field: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or any(
        not isinstance(key, str) or not isinstance(item, str) or not key.strip() or not item.strip()
        for key, item in value.items()
    ):
        raise KnowledgeConfigError(f"{field} must be a mapping of strings")
    return {str(key).strip(): item.strip() for key, item in value.items()}


def _coverage_rules(value: object) -> dict[str, dict[str, str]]:
    if not isinstance(value, Mapping):
        raise KnowledgeConfigError("coverage_rules must be a mapping")
    rules: dict[str, dict[str, str]] = {}
    for key, rule in value.items():
        if not isinstance(key, str) or not key.strip():
            raise KnowledgeConfigError("coverage_rules keys must be strings")
        if not isinstance(rule, Mapping) or any(
            not isinstance(rule_key, str) or not isinstance(rule_value, str)
            for rule_key, rule_value in rule.items()
        ):
            raise KnowledgeConfigError(f"coverage_rules.{key} must be a string mapping")
        normalized = {str(rule_key).strip(): rule_value.strip() for rule_key, rule_value in rule.items()}
        if set(normalized) != {"require"}:
            raise KnowledgeConfigError(f"coverage_rules.{key} must declare exactly one require key")
        if normalized["require"] not in COVERAGE_REQUIREMENTS:
            supported = ", ".join(COVERAGE_REQUIREMENTS)
            raise KnowledgeConfigError(
                f"coverage_rules.{key}.require must be one of: {supported}"
            )
        rules[key.strip()] = normalized
    return rules


def load_knowledge_config(repo_root: Path, config_path: Path | None) -> dict[str, object]:
    if config_path is None:
        return empty_knowledge_config()

    resolved = config_path if config_path.is_absolute() else repo_root / config_path
    if not resolved.is_file():
        raise KnowledgeConfigError(f"knowledge config is missing: {config_path}")
    try:
        loaded = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise KnowledgeConfigError(f"knowledge config is unreadable: {error}") from error
    if not isinstance(loaded, Mapping):
        raise KnowledgeConfigError("knowledge config must be a mapping")
    unknown = sorted(set(loaded) - set(CONFIG_FIELDS))
    missing = sorted(set(CONFIG_FIELDS) - set(loaded))
    if unknown:
        raise KnowledgeConfigError(f"knowledge config has unknown fields: {unknown}")
    if missing:
        raise KnowledgeConfigError(f"knowledge config is missing fields: {missing}")
    return {
        "scan_roots": _string_list(loaded["scan_roots"], "scan_roots"),
        "exclusions": _string_list(loaded["exclusions"], "exclusions"),
        "expected_assets": _string_map(loaded["expected_assets"], "expected_assets"),
        "canonical_documents": _string_list(
            loaded["canonical_documents"], "canonical_documents"
        ),
        "coverage_rules": _coverage_rules(loaded["coverage_rules"]),
    }


def tracked_files(repo_root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return {line for line in result.stdout.splitlines() if line}
    except (OSError, subprocess.CalledProcessError):
        return {
            file_path.relative_to(repo_root).as_posix()
            for file_path in repo_root.rglob("*")
            if file_path.is_file() and ".git" not in file_path.parts
        }


def read_declarations(manifest_path: Path) -> list[str]:
    if not manifest_path.is_file():
        return []
    return [
        line.strip().rstrip("/")
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def discover_candidates(repo_root: Path) -> list[str]:
    tracked = tracked_files(repo_root)
    candidates = {
        file_path
        for file_path in tracked
        if file_path == "README.md"
        or file_path.startswith("docs/")
        or file_path.endswith("/README.md")
    }
    candidates.update(read_declarations(repo_root / "docs" / "knowledge-components.txt"))
    candidates.update(read_declarations(repo_root / "docs" / "readme-components.txt"))
    return sorted(candidates)


def component_for_path(repo_root: Path, relative_path: str) -> dict[str, object]:
    normalized = relative_path.rstrip("/")
    target = repo_root / normalized
    is_readme = normalized == "README.md" or normalized.endswith("/README.md")
    has_readme = target.is_dir() and (target / "README.md").is_file()
    component: dict[str, object] = {
        "path": normalized,
        "why": "Tracked repository knowledge or documented component",
        "owner": "Repository maintainers",
    }
    if is_readme or has_readme:
        component["readme"] = {
            "format": "component-readme:v1" if has_readme else "standard",
            "required_sections": False,
        }
    return component


def render_manifest(repo_root: Path, relative_paths: list[str]) -> str:
    lines = [
        "schema_version: 1",
        "kind: knowledge-map",
        "metadata:",
        '  description: "Repository knowledge and component manifest"',
        "components:",
    ]
    for relative_path in sorted(dict.fromkeys(relative_paths)):
        component = component_for_path(repo_root, relative_path)
        lines.extend(
            [
                f"  - path: {json.dumps(component['path'])}",
                f"    why: {json.dumps(component['why'])}",
                f"    owner: {json.dumps(component['owner'])}",
            ]
        )
        readme = component.get("readme")
        if isinstance(readme, dict):
            lines.extend(
                [
                    "    readme:",
                    f"      format: {json.dumps(readme['format'])}",
                    f"      required_sections: {str(readme['required_sections']).lower()}",
                ]
            )
    return "\n".join(lines) + "\n"


def manifest_paths(manifest_path: Path) -> list[str]:
    if not manifest_path.is_file():
        return []
    paths: list[str] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*-\s+path:\s*(.+?)\s*$", line)
        if not match:
            continue
        value = match.group(1)
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = value.strip("'\"")
        if isinstance(parsed, str):
            paths.append(parsed.rstrip("/"))
    return paths


def write_manifest(repo_root: Path, relative_paths: list[str]) -> Path:
    manifest_path = repo_root / "docs" / "knowledge-map.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(render_manifest(repo_root, relative_paths), encoding="utf-8")
    return manifest_path


def normalize_target(repo_root: Path, raw_target: str) -> str:
    pure_path = PurePosixPath(raw_target)
    if pure_path.is_absolute() or ".." in pure_path.parts or not pure_path.parts:
        raise ValueError(f"target must be a repository-relative path: {raw_target}")
    normalized = pure_path.as_posix().rstrip("/")
    if normalized in PROTECTED_WRITES:
        raise PermissionError(f"target is report-only and never writable: {normalized}")
    resolved = (repo_root / normalized).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as error:
        raise ValueError(f"target escapes repository root: {raw_target}") from error
    return normalized


def audit_repository(
    repo_root: Path, config: Mapping[str, object] | None = None
) -> dict[str, object]:
    findings: list[str] = []
    resolved_config = dict(config) if config is not None else empty_knowledge_config()
    if not (repo_root / "docs").is_dir():
        findings.append("docs/ directory is missing")
    if not (repo_root / "docs" / "knowledge-map.yaml").is_file():
        findings.append("docs/knowledge-map.yaml is missing")

    accepted_by_number: dict[str, list[str]] = {}
    adr_dir = repo_root / "docs" / "adr"
    if adr_dir.is_dir():
        for adr_path in sorted(adr_dir.glob("*.md")):
            file_match = ADR_FILE_RE.fullmatch(adr_path.name)
            if not file_match:
                continue
            text = adr_path.read_text(encoding="utf-8")
            heading_match = ADR_HEADING_RE.search(text)
            status_match = STATUS_RE.search(text)
            if not heading_match or file_match["number"] != heading_match["number"]:
                findings.append(
                    f"ADR identity mismatch: {adr_path.relative_to(repo_root).as_posix()}"
                )
            missing_sections = [
                section for section in REQUIRED_ADR_SECTIONS if section not in text
            ]
            if missing_sections:
                findings.append(
                    f"ADR missing required sections: {adr_path.relative_to(repo_root).as_posix()}"
                )
            if status_match and status_match["status"].strip().lower() == "accepted":
                accepted_by_number.setdefault(file_match["number"], []).append(
                    adr_path.relative_to(repo_root).as_posix()
                )
    for number, accepted_paths in accepted_by_number.items():
        if len(accepted_paths) > 1:
            findings.append(f"duplicate accepted ADR-{number}: {', '.join(accepted_paths)}")

    tracked = tracked_files(repo_root)
    declared_components = set(read_declarations(repo_root / "docs" / "readme-components.txt"))
    mapped_paths = set(manifest_paths(repo_root / "docs" / "knowledge-map.yaml"))
    for readme_path in sorted(
        path for path in tracked if path == "README.md" or path.endswith("/README.md")
    ):
        component_path = str(PurePosixPath(readme_path).parent)
        if readme_path not in mapped_paths and component_path not in declared_components:
            findings.append(f"uncovered README: {readme_path}")

    status = "passed" if not findings else "missing"
    expected_assets = resolved_config.get("expected_assets")
    if not isinstance(expected_assets, Mapping):
        expected_assets = {}
    ci_assets = {
        name: {"path": relative_path, "present": (repo_root / relative_path).is_file()}
        for name, relative_path in expected_assets.items()
        if isinstance(name, str) and isinstance(relative_path, str)
    }
    return {"mode": "audit", "status": status, "findings": findings, "ci_assets": ci_assets}


def impact_report(repo_root: Path, targets: list[str]) -> dict[str, object]:
    references: dict[str, list[str]] = {target: [] for target in targets}
    for relative_path in sorted(tracked_files(repo_root)):
        candidate = repo_root / relative_path
        if not candidate.is_file():
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for target in targets:
            if target in text:
                references[target].append(relative_path)
    return {"mode": "impact", "status": "reported", "references": references}


def _config_list(config: Mapping[str, object], field: str) -> list[str]:
    value = config.get(field)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _normalize_repo_path(relative_path: str) -> str:
    path = relative_path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def _path_is_excluded(relative_path: str, exclusions: Sequence[str]) -> bool:
    path = _normalize_repo_path(relative_path)
    parts = PurePosixPath(path).parts
    for pattern in exclusions:
        raw = str(pattern).strip().strip("\"'")
        if not raw:
            continue
        if fnmatch.fnmatch(path, raw):
            return True
        if raw.endswith("/**"):
            prefix = raw[:-3]
            if prefix.startswith("**/"):
                needle = prefix[3:]
                if needle and needle in parts:
                    return True
            elif prefix and (path == prefix or path.startswith(prefix + "/")):
                return True
        if raw.startswith("**/") and raw.endswith("/**"):
            needle = raw[3:-3]
            if needle and needle in parts:
                return True
    return False


def _in_scan_roots(relative_path: str, scan_roots: Sequence[str]) -> bool:
    path = _normalize_repo_path(relative_path)
    for root in scan_roots:
        normalized = _normalize_repo_path(root).rstrip("/")
        if path == normalized or path.startswith(normalized + "/"):
            return True
    return False


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def _local_module_target(owner: str, source: str) -> str | None:
    if not source.startswith("."):
        return None
    resolved = PurePosixPath(owner) / source
    parts: list[str] = []
    for part in resolved.parts:
        if part == "..":
            if parts:
                parts.pop()
            continue
        if part in {".", ""}:
            continue
        parts.append(part)
    if not parts:
        return None
    return str(PurePosixPath(*parts))


def _component_readme_owner(path: str, repo_root: Path) -> str:
    target = repo_root / path
    if target.is_dir():
        return path
    parent = str(PurePosixPath(path).parent)
    return parent if parent != "." else path


def inventory_repository(
    repo_root: Path, config: Mapping[str, object] | None = None
) -> dict[str, object]:
    resolved = dict(config) if config is not None else empty_knowledge_config()
    scan_roots = _config_list(resolved, "scan_roots")
    exclusions = _config_list(resolved, "exclusions")
    tracked = sorted(
        path
        for path in tracked_files(repo_root)
        if _in_scan_roots(path, scan_roots) and not _path_is_excluded(path, exclusions)
    )

    components: list[dict[str, object]] = []
    findings: list[str] = []
    consumed: set[str] = set()
    terraform_dirs: dict[str, list[str]] = {}
    for relative_path in tracked:
        if relative_path.endswith(".tf") and ".terraform" not in PurePosixPath(relative_path).parts:
            terraform_dirs.setdefault(str(PurePosixPath(relative_path).parent), []).append(
                relative_path
            )

    for directory, files in sorted(terraform_dirs.items()):
        texts = [_read_text(repo_root / file_path) for file_path in files]
        kind = (
            "terraform_root"
            if any(BACKEND_RE.search(text) for text in texts)
            else "terraform_local_module"
        )
        components.append({"path": directory, "kind": kind, "evidence": files})
        consumed.update(files)
        readme = f"{directory}/README.md"
        if readme in tracked:
            consumed.add(readme)

    for relative_path in tracked:
        name = PurePosixPath(relative_path).name
        if name not in {"action.yml", "action.yaml"}:
            continue
        text = _read_text(repo_root / relative_path)
        if "using: composite" not in text and 'using: "composite"' not in text:
            continue
        directory = str(PurePosixPath(relative_path).parent)
        evidence = [relative_path]
        readme = f"{directory}/README.md"
        if readme in tracked:
            evidence.append(readme)
            consumed.add(readme)
        components.append(
            {"path": directory, "kind": "github_composite_action", "evidence": evidence}
        )
        consumed.add(relative_path)

    for relative_path in tracked:
        if not relative_path.startswith(".github/workflows/") or not relative_path.endswith(
            (".yml", ".yaml")
        ):
            continue
        components.append(
            {"path": relative_path, "kind": "github_workflow", "evidence": [relative_path]}
        )
        consumed.add(relative_path)

    tool_dirs: dict[str, list[str]] = {}
    for relative_path in tracked:
        parts = PurePosixPath(relative_path).parts
        if len(parts) >= 2 and parts[0] == "tools":
            tool_dirs.setdefault(str(PurePosixPath(parts[0], parts[1])), []).append(relative_path)
    for directory, files in sorted(tool_dirs.items()):
        if directory.endswith("/tests"):
            continue
        components.append({"path": directory, "kind": "validator_tool", "evidence": files})
        consumed.update(files)

    for relative_path in tracked:
        if relative_path in consumed:
            continue
        if relative_path.endswith(".sh") or relative_path.startswith("scripts/"):
            if relative_path.endswith("/README.md") or relative_path.endswith(".md"):
                continue
            if "/tests/" in f"/{relative_path}" or relative_path.startswith("tests/"):
                continue
            components.append(
                {"path": relative_path, "kind": "script_wrapper", "evidence": [relative_path]}
            )
            consumed.add(relative_path)
            owner = _component_readme_owner(relative_path, repo_root)
            readme = f"{owner}/README.md"
            if readme in tracked:
                consumed.add(readme)

    for relative_path in tracked:
        if relative_path in consumed:
            continue
        name = PurePosixPath(relative_path).name
        if (
            relative_path.startswith("tests/")
            or "/tests/" in relative_path
            or name.startswith("test_")
            or name.endswith("_test.py")
        ):
            components.append({"path": relative_path, "kind": "test", "evidence": [relative_path]})
            consumed.add(relative_path)

    for relative_path in tracked:
        if relative_path in consumed:
            continue
        if not relative_path.startswith("data/"):
            continue
        if relative_path.endswith((".yaml", ".yml", ".json")):
            components.append(
                {"path": relative_path, "kind": "declaration_data", "evidence": [relative_path]}
            )
            consumed.add(relative_path)

    component_dirs = [
        str(item["path"])
        for item in components
        if isinstance(item.get("path"), str) and (repo_root / str(item["path"])).is_dir()
    ]
    for relative_path in tracked:
        if relative_path in consumed:
            continue
        if any(
            relative_path == owner or relative_path.startswith(owner + "/")
            for owner in component_dirs
        ):
            consumed.add(relative_path)

    documentation_suffixes = (".md", ".yaml", ".yml", ".txt")
    for relative_path in tracked:
        if relative_path in consumed:
            continue
        if relative_path.startswith("docs/") and relative_path.endswith(documentation_suffixes):
            continue
        if relative_path.endswith("README.md"):
            continue
        findings.append(f"ambiguous classification: {relative_path}")

    capabilities: list[dict[str, object]] = []
    for component in components:
        if component["kind"] not in {"terraform_root", "terraform_local_module"}:
            continue
        evidence = component["evidence"]
        if not isinstance(evidence, list):
            continue
        resource_types: list[str] = []
        data_types: list[str] = []
        resource_count = 0
        data_count = 0
        for file_path in evidence:
            if not isinstance(file_path, str) or not file_path.endswith(".tf"):
                continue
            text = _read_text(repo_root / file_path)
            resources = RESOURCE_RE.findall(text)
            data_sources = DATA_RE.findall(text)
            resource_count += len(resources)
            data_count += len(data_sources)
            resource_types.extend(item[0] for item in resources)
            data_types.extend(item[0] for item in data_sources)
        if resource_count or data_count:
            capabilities.append(
                {
                    "owner": component["path"],
                    "resource_types": sorted(dict.fromkeys(resource_types)),
                    "data_source_types": sorted(dict.fromkeys(data_types)),
                    "static_counts": {"resource": resource_count, "data": data_count},
                }
            )

    component_paths = {str(item["path"]) for item in components}
    relationships: list[dict[str, object]] = []

    def add_relationship(rel_type: str, source: str, target: str, evidence: str) -> None:
        if target not in component_paths and rel_type != "documentation":
            if target not in component_paths:
                return
        relationships.append(
            {"type": rel_type, "from": source, "to": target, "evidence": evidence}
        )

    for component in components:
        if component["kind"] not in {"terraform_root", "terraform_local_module"}:
            continue
        evidence = component["evidence"]
        if not isinstance(evidence, list):
            continue
        owner = str(component["path"])
        for file_path in evidence:
            if not isinstance(file_path, str):
                continue
            for source in MODULE_SOURCE_RE.findall(_read_text(repo_root / file_path)):
                target = _local_module_target(owner, source)
                if target:
                    add_relationship("local_module", owner, target, file_path)

    for component in components:
        if component["kind"] != "github_workflow":
            continue
        workflow = str(component["path"])
        text = _read_text(repo_root / workflow)
        for raw_use in USES_RE.findall(text):
            used = raw_use.removeprefix("./")
            add_relationship("local_action", workflow, used, workflow)
        for script_path in RUN_PATH_RE.findall(text):
            add_relationship("wrapper_caller", workflow, script_path, workflow)

    for relative_path in tracked:
        if not relative_path.endswith(".md"):
            continue
        text = _read_text(repo_root / relative_path)
        for path in sorted(component_paths):
            if path and path in text:
                add_relationship("documentation", relative_path, path, relative_path)

    return {
        "mode": "inventory",
        "status": "reported",
        "scope": {"scan_roots": scan_roots, "exclusions": exclusions},
        "components": components,
        "relationships": relationships,
        "capabilities": capabilities,
        "findings": findings,
    }


def _knowledge_component_covers(document: str, declarations: Sequence[str]) -> bool:
    for item in declarations:
        normalized = item.rstrip("/")
        if document == normalized or document.startswith(normalized + "/"):
            return True
    return False


def check_repository(
    repo_root: Path,
    config: Mapping[str, object] | None = None,
    inventory: Mapping[str, object] | None = None,
) -> dict[str, object]:
    resolved = dict(config) if config is not None else empty_knowledge_config()
    inventory_report = (
        dict(inventory) if inventory is not None else inventory_repository(repo_root, resolved)
    )
    findings: list[str] = []
    canonical = _config_list(resolved, "canonical_documents")
    mapped = set(manifest_paths(repo_root / "docs" / "knowledge-map.yaml"))
    knowledge_components = read_declarations(repo_root / "docs" / "knowledge-components.txt")
    readme_components = set(read_declarations(repo_root / "docs" / "readme-components.txt"))
    coverage_rules = resolved.get("coverage_rules")
    if not isinstance(coverage_rules, Mapping):
        coverage_rules = {}

    for document in canonical:
        if not (repo_root / document).exists():
            findings.append(f"missing canonical document: {document}")
            continue
        if document not in mapped:
            findings.append(f"canonical document not mapped: {document}")
        if not _knowledge_component_covers(document, knowledge_components):
            findings.append(f"canonical document not in knowledge-components: {document}")

    tracked = tracked_files(repo_root)
    docs_dir = repo_root / "docs"
    if docs_dir.is_dir():
        for guide in sorted(docs_dir.glob("*.md")):
            relative = guide.relative_to(repo_root).as_posix()
            if relative in tracked and relative not in canonical:
                findings.append(f"unclassified canonical guide: {relative}")

    components = inventory_report.get("components")
    if not isinstance(components, list):
        components = []
    for component in components:
        if not isinstance(component, Mapping):
            continue
        kind = component.get("kind")
        path = component.get("path")
        if not isinstance(kind, str) or not isinstance(path, str):
            continue
        rule = coverage_rules.get(kind)
        require = rule.get("require") if isinstance(rule, Mapping) else None
        if require != "readme":
            continue
        owner = _component_readme_owner(path, repo_root)
        readme_path = f"{owner}/README.md" if (repo_root / owner).is_dir() else f"{owner}.md"
        if not (repo_root / readme_path).is_file():
            findings.append(f"missing required README: {path}")
            continue
        if owner not in readme_components and readme_path not in readme_components:
            findings.append(f"unregistered README owner: {path}")

    status = "passed" if not findings else "failed"
    return {
        "mode": "check",
        "status": status,
        "findings": findings,
        "inventory": inventory_report,
    }
