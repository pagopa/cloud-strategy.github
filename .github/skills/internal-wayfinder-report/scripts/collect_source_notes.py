#!/usr/bin/env python3
"""Collect a deterministic, bounded structural index of Wayfinder sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")
REQUIRED_FILES = ("map.md", "analysis.md", "report/report.json")


class CollectorError(ValueError):
    """Raised when the workspace cannot be inspected safely."""


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_workspace(workspace: Path) -> Path:
    try:
        root = workspace.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise CollectorError(f"workspace cannot be resolved: {exc}") from exc
    if not root.is_dir():
        raise CollectorError("workspace must be an existing directory")
    return root


def _resolve_required_path(root: Path, relative_path: str, kind: str) -> Path:
    candidate = root / relative_path
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise CollectorError(f"required {kind} cannot be resolved") from exc
    if not _within(resolved, root):
        raise CollectorError(f"required {kind} must resolve inside workspace")
    return resolved


def _check_required_paths(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        resolved = _resolve_required_path(root, relative_path, "path")
        if not resolved.is_file():
            raise CollectorError(f"missing required file: {relative_path}")

    issues = _resolve_required_path(root, "issues", "directory")
    if not issues.is_dir():
        raise CollectorError("missing required directory: issues")


def _source_paths(root: Path) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = []
    candidates = sorted(
        root.rglob("*"), key=lambda path: path.relative_to(root).as_posix()
    )
    for candidate in candidates:
        relative = candidate.relative_to(root)
        if "report" in relative.parts:
            continue
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError, ValueError) as exc:
            raise CollectorError("source path cannot be resolved") from exc
        if not _within(resolved, root):
            raise CollectorError("source path must resolve inside workspace")
        if candidate.is_dir():
            continue
        if not resolved.is_file():
            raise CollectorError("source path must be a regular file")
        paths.append((relative.as_posix(), resolved))
    return paths


def _without_line_ending(line: str) -> str:
    if line.endswith("\n"):
        line = line[:-1]
        if line.endswith("\r"):
            line = line[:-1]
    elif line.endswith("\r"):
        line = line[:-1]
    return line


def _extract_structure(
    lines: list[str], max_preview_lines: int
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    headings: list[tuple[int, str]] = []
    for index, raw_line in enumerate(lines):
        line = _without_line_ending(raw_line)
        match = HEADING_RE.match(line)
        if match:
            headings.append((index, match.group(2)))

    heading_output = [
        {"line": index + 1, "text": text} for index, text in headings
    ]
    windows: list[dict[str, object]] = []
    for heading_index, (start, text) in enumerate(headings):
        section_end = (
            headings[heading_index + 1][0]
            if heading_index + 1 < len(headings)
            else len(lines)
        )
        end = min(section_end, start + max_preview_lines)
        windows.append(
            {
                "heading": text,
                "start_line": start + 1,
                "lines": [_without_line_ending(line) for line in lines[start:end]],
            }
        )
    return heading_output, windows


def collect_source_notes(root: Path, max_preview_lines: int) -> dict[str, object]:
    _check_required_paths(root)
    sources: list[dict[str, object]] = []
    for relative_path, source_path in _source_paths(root):
        try:
            source_bytes = source_path.read_bytes()
            source_text = source_bytes.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise CollectorError(f"source cannot be read as UTF-8: {relative_path}") from exc
        lines = source_text.splitlines(keepends=True)
        headings, windows = _extract_structure(lines, max_preview_lines)
        sources.append(
            {
                "path": relative_path,
                "bytes": len(source_bytes),
                "lines": len(lines),
                "headings": headings,
                "windows": windows,
            }
        )
    return {"sources": sources}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect bounded structural notes for Wayfinder source files."
    )
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--max-preview-lines", required=True, type=int)
    args = parser.parse_args()
    if args.max_preview_lines <= 0:
        parser.error("--max-preview-lines must be positive")
    return args


def main() -> int:
    args = _parse_args()
    try:
        root = _resolve_workspace(args.workspace)
        payload = collect_source_notes(root, args.max_preview_lines)
    except CollectorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    json.dump(payload, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
