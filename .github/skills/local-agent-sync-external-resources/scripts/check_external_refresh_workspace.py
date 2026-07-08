#!/usr/bin/env python3
"""Validate external-refresh staging before graphify or catalog completion."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_GRAPHIFY_PATTERNS = ("tmp/", "/tmp/", "tmp/external-refresh/", "**/.git/")
REPO_LOCAL_REFRESH_DIRS = ("tmp/external-refresh", "tmp/upstream-refresh")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that external refresh work is staged outside the repository."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--workspace", help="External refresh workspace path.")
    parser.add_argument(
        "--check-graphifyignore",
        action="store_true",
        help="Require graphify ignore coverage for temporary refresh paths.",
    )
    return parser.parse_args()


def display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_graphifyignore(root: Path) -> set[str]:
    path = root / ".graphifyignore"
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def missing_graphifyignore_patterns(root: Path) -> list[str]:
    configured = read_graphifyignore(root)
    return [pattern for pattern in REQUIRED_GRAPHIFY_PATTERNS if pattern not in configured]


def validate_workspace(root: Path, workspace: Path | None) -> list[str]:
    if workspace is None:
        return []
    root_resolved = root.resolve()
    workspace_resolved = workspace.resolve()
    if workspace_resolved == root_resolved or workspace_resolved.is_relative_to(root_resolved):
        return [
            "External refresh workspace must be outside the repository: "
            f"{display_path(root, workspace)}"
        ]
    return []


def find_repo_local_refresh_dirs(root: Path) -> list[str]:
    found: list[str] = []
    tmp_dir = root / "tmp"
    if tmp_dir.is_dir():
        for child in tmp_dir.iterdir():
            if child.is_dir() and (child / ".git").exists():
                found.append(child.relative_to(root).as_posix())
    for relative in REPO_LOCAL_REFRESH_DIRS:
        path = root / relative
        if path.exists() and path.as_posix() not in {f for f in found}:
            found.append(relative)
    return found


def collect_findings(
    root: Path, workspace: Path | None, check_graphifyignore: bool
) -> list[str]:
    findings: list[str] = []
    findings.extend(validate_workspace(root, workspace))
    leftovers = find_repo_local_refresh_dirs(root)
    if leftovers:
        findings.append(
            "Remove or move repo-local external refresh directories before graphify: "
            + ", ".join(leftovers)
        )
    if check_graphifyignore:
        missing = missing_graphifyignore_patterns(root)
        if missing:
            findings.append("Missing .graphifyignore refresh patterns: " + ", ".join(missing))
    return findings


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root)
    workspace = Path(args.workspace) if args.workspace else None
    findings = collect_findings(root, workspace, args.check_graphifyignore)
    if findings:
        for finding in findings:
            print(f"[blocking] {finding}", file=sys.stderr)
        return 1
    print("External refresh workspace guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
