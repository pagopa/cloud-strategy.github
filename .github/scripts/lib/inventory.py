from __future__ import annotations

import re
from pathlib import Path

from .shared import INVENTORY_PATH, path_list, write_text

SECTION_ORDER = ("Instructions", "Prompts", "Skills", "Agents")
EMPTY_MESSAGES = {
    "Instructions": "No instruction files currently ship in the live catalog.",
    "Prompts": "No prompt files currently ship in the live catalog.",
    "Skills": "No skill files currently ship in the live catalog.",
    "Agents": "No agent files currently ship in the live catalog.",
}


def collect_inventory_sections(root: Path) -> dict[str, list[str]]:
    return {
        "Instructions": path_list(root, ".github/instructions/**/*.instructions.md"),
        "Prompts": path_list(root, ".github/prompts/**/*.prompt.md"),
        "Skills": path_list(root, ".github/skills/**/SKILL.md"),
        "Agents": path_list(root, ".github/agents/*.agent.md"),
    }


def sections_from_catalog_paths(paths: list[str]) -> dict[str, list[str]]:
    sections = {section: [] for section in SECTION_ORDER}
    for relative_path in sorted(paths):
        if relative_path.startswith(".github/instructions/") and relative_path.endswith(".instructions.md"):
            sections["Instructions"].append(relative_path)
        elif relative_path.startswith(".github/prompts/") and relative_path.endswith(".prompt.md"):
            sections["Prompts"].append(relative_path)
        elif relative_path.startswith(".github/skills/") and relative_path.endswith("/SKILL.md"):
            sections["Skills"].append(relative_path)
        elif relative_path.startswith(".github/agents/") and relative_path.endswith(".agent.md"):
            sections["Agents"].append(relative_path)
    return {section: sorted(entries) for section, entries in sections.items()}


def render_inventory_markdown(sections: dict[str, list[str]]) -> str:
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
        if entries:
            lines.extend(f"- `{entry}`" for entry in entries)
        else:
            lines.append(EMPTY_MESSAGES[section])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_inventory_markdown(root: Path) -> str:
    return render_inventory_markdown(collect_inventory_sections(root))


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
