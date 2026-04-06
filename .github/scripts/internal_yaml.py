#!/usr/bin/env python3
"""Shared YAML and frontmatter helpers for repository-owned Python scripts."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


FRONTMATTER_PATTERN = re.compile(r"(?s)\A---\n(.*?)\n---(?:\n|\Z)")


def load_yaml_document(path: Path) -> object:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Failed to read YAML file {path}: {exc}") from exc

    if not content.strip():
        return {}

    try:
        loaded = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc

    if loaded is None:
        return {}

    return loaded


def coerce_frontmatter_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, list):
        rendered_items = [coerce_frontmatter_value(item).strip() for item in value]
        return ", ".join(item for item in rendered_items if item)
    return ""


def parse_frontmatter_text(text: str, *, source_name: str = "<memory>") -> dict[str, str]:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}

    try:
        loaded = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid frontmatter YAML in {source_name}: {exc}") from exc

    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected frontmatter to be a YAML mapping in {source_name}")

    frontmatter: dict[str, str] = {}
    for key, value in loaded.items():
        if not isinstance(key, str) or not key or " " in key:
            continue
        frontmatter[key] = coerce_frontmatter_value(value).strip()

    return frontmatter


def load_frontmatter(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Failed to read frontmatter file {path}: {exc}") from exc

    return parse_frontmatter_text(content, source_name=str(path))


def split_frontmatter_list(raw_value: str) -> list[str]:
    return [pattern.strip() for pattern in raw_value.split(",") if pattern.strip()]
