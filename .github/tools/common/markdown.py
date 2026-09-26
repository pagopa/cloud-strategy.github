from __future__ import annotations

import re
from pathlib import Path

import yaml

FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---"):
        return {}, text

    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, text

    frontmatter_text = match.group(1)
    try:
        parsed = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    return parsed, text[match.end() :]


def load_frontmatter(path: Path) -> dict[str, object]:
    return split_frontmatter(path.read_text(encoding="utf-8"))[0]


def strip_frontmatter(text: str) -> str:
    return split_frontmatter(text)[1]


def markdown_link_targets(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def normalize_markdown_text(text: str) -> str:
    normalized_lines: list[str] = []
    in_code_block = False
    for raw_line in strip_frontmatter(text).splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        cleaned = re.sub(r"^[#>*\-\d\.)\s]+", "", line).replace("`", "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
        if cleaned:
            normalized_lines.append(cleaned)
    return "\n".join(normalized_lines)


def significant_text_lines(text: str) -> set[str]:
    return {
        line
        for line in normalize_markdown_text(text).splitlines()
        if len(line) >= 18 and not line.startswith("http")
    }
