from __future__ import annotations

import re
from pathlib import Path

import yaml
from common.constants import INVENTORY_PATH
from common.files import write_text
from common.paths import path_list

MANAGED_RESOURCES_RELATIVE_PATH = (
    ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
)
SECTION_ORDER = (
    "Instructions",
    "Skills",
    "Imported Skill Provenance",
    "Scripts",
    "Agents",
    "Prompts",
)
EMPTY_MESSAGES = {
    "Instructions": "No instruction files currently ship in the live catalog.",
    "Skills": "No skill files currently ship in the live catalog.",
    "Imported Skill Provenance": (
        "No imported skill provenance is available; declare sources in the "
        "external resource manifest."
    ),
    "Scripts": "No script files currently ship in the live catalog.",
    "Agents": "No agent files currently ship in the live catalog.",
    "Prompts": "No prompt files currently ship in the live catalog.",
}
SCRIPT_GLOB_PATTERNS = (".github/scripts/**/*.py", ".github/scripts/**/*.sh")
IGNORED_SCRIPT_PARTS = frozenset(
    {".venv", ".pytest_cache", "__pycache__", "graphify-out", "tests"}
)
DOCUMENT_SUPPORT_ONLY_SKILLS = (
    ".github/skills/anthropic-docx/SKILL.md",
    ".github/skills/anthropic-pdf/SKILL.md",
    ".github/skills/anthropic-pptx/SKILL.md",
    ".github/skills/anthropic-xlsx/SKILL.md",
)
IGNORED_SCRIPT_BASENAMES = {"__init__.py"}


def _repo_display(repository: str) -> str:
    value = repository
    if "://" in value:
        value = value.split("://", 1)[1]
    if value.endswith(".git"):
        value = value[: -len(".git")]
    parts = [part for part in value.split("/") if part]
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return value


def _manifest_provenance_groups(root: Path) -> list[dict[str, object]]:
    manifest_path = root / MANAGED_RESOURCES_RELATIVE_PATH
    if not manifest_path.exists():
        return []
    try:
        payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(payload, dict):
        return []
    sources = payload.get("sources")
    if not isinstance(sources, dict):
        return []

    groups: list[dict[str, object]] = []
    for source_id in sorted(sources):
        source = sources[source_id]
        if not isinstance(source, dict):
            continue
        repository = str(source.get("repository") or "")
        ref = str(source.get("ref") or "")
        raw_assets = source.get("assets") or []
        paths = sorted(
            f"{asset['local']}/SKILL.md"
            for asset in raw_assets
            if isinstance(asset, dict) and asset.get("local")
        )
        if not repository or not ref or not paths:
            continue
        groups.append(
            {
                "repository": _repo_display(repository),
                "ref": ref[:12],
                "tag": str(source.get("advertised_ref")) if source.get("advertised_ref") else None,
                "commit_date": str(source.get("commit_date")) if source.get("commit_date") else None,
                "paths": paths,
            }
        )
    return groups


def _format_provenance_heading(group: dict[str, object]) -> str:
    parts = [f"{group['repository']} — ref {group['ref']}"]
    if group.get("tag"):
        parts.append(f"tag {group['tag']}")
    if group.get("commit_date"):
        parts.append(str(group["commit_date"]))
    parts.append(f"{len(group['paths'])} skills")
    return " · ".join(parts)


def collect_inventory_sections(root: Path) -> dict[str, list[str]]:
    skills = path_list(root, ".github/skills/**/SKILL.md")
    imported = {
        path
        for group in _manifest_provenance_groups(root)
        for path in group["paths"]
    }
    provenance = sorted(set(skills) & imported)
    return {
        "Instructions": path_list(root, ".github/instructions/**/*.instructions.md"),
        "Skills": skills,
        "Imported Skill Provenance": provenance,
        "Scripts": _collect_script_paths(root),
        "Agents": path_list(root, ".github/agents/*.agent.md"),
        "Prompts": path_list(root, ".github/prompts/*.prompt.md"),
    }


def _collect_script_paths(root: Path) -> list[str]:
    entries: set[str] = set()
    for pattern in SCRIPT_GLOB_PATTERNS:
        for path in root.glob(pattern):
            relative_path = path.relative_to(root)
            if (
                not path.is_file()
                or path.name in IGNORED_SCRIPT_BASENAMES
                or any(part in IGNORED_SCRIPT_PARTS for part in relative_path.parts)
            ):
                continue
            entries.add(relative_path.as_posix())
    return sorted(entries)


def sections_from_catalog_paths(paths: list[str]) -> dict[str, list[str]]:
    sections = {section: [] for section in SECTION_ORDER}
    for relative_path in sorted(paths):
        if relative_path.startswith(".github/instructions/") and relative_path.endswith(
            ".instructions.md"
        ):
            sections["Instructions"].append(relative_path)
        elif relative_path.startswith(".github/skills/") and relative_path.endswith(
            "/SKILL.md"
        ):
            sections["Skills"].append(relative_path)
        elif (
            relative_path.startswith(".github/scripts/")
            and (relative_path.endswith(".py") or relative_path.endswith(".sh"))
            and not relative_path.endswith("__init__.py")
        ):
            sections["Scripts"].append(relative_path)
        elif relative_path.startswith(".github/agents/") and relative_path.endswith(
            ".agent.md"
        ):
            sections["Agents"].append(relative_path)
        elif relative_path.startswith(".github/prompts/") and relative_path.endswith(
            ".prompt.md"
        ):
            sections["Prompts"].append(relative_path)
    return {section: sorted(entries) for section, entries in sections.items()}


def render_inventory_markdown(
    sections: dict[str, list[str]],
    provenance_groups: list[dict[str, object]] | None = None,
) -> str:
    lines = [
        "# Copilot Inventory",
        "",
        "This file is the exact path inventory for the live GitHub Copilot catalog in this repository.",
        "",
    ]
    for section in SECTION_ORDER:
        lines.append(f"## {section}")
        lines.append("")
        entries = sections.get(section, [])
        if section == "Imported Skill Provenance" and provenance_groups is not None:
            if provenance_groups:
                for group in provenance_groups:
                    lines.append(f"### {_format_provenance_heading(group)}")
                    lines.append("")
                    lines.extend(f"- `{path}`" for path in group["paths"])
                    lines.append("")
            else:
                lines.append(EMPTY_MESSAGES[section])
                lines.append("")
            continue
        if entries:
            lines.extend(f"- `{entry}`" for entry in entries)
            if section == "Skills":
                doc_entries = [
                    entry for entry in entries if entry in DOCUMENT_SUPPORT_ONLY_SKILLS
                ]
                if doc_entries:
                    lines.append("")
                    lines.append("### Support-only imported document skills")
                    lines.append("")
                    lines.append(
                        "These vendor-prefixed imported document skills remain support-only depth for repositories that explicitly need document workflows."
                    )
        else:
            lines.append(EMPTY_MESSAGES[section])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_inventory_markdown(root: Path) -> str:
    return render_inventory_markdown(
        collect_inventory_sections(root),
        _manifest_provenance_groups(root),
    )


def write_inventory(root: Path) -> Path:
    inventory_path = root / INVENTORY_PATH
    write_text(inventory_path, build_inventory_markdown(root))
    return inventory_path


def parse_inventory_markdown(text: str) -> dict[str, set[str]]:
    section_lookup = {section.lower(): section for section in SECTION_ORDER}
    sections = {section: set() for section in SECTION_ORDER}
    current_section: str | None = None

    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip().lower()
            current_section = section_lookup.get(heading)
            continue
        if current_section is None:
            continue
        match = re.match(r"^- `([^`]+)`$", line.strip())
        if match:
            sections[current_section].add(match.group(1))

    return sections
