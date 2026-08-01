"""Detect changes to protected external skill bundles."""

from __future__ import annotations

import os
import posixpath
import subprocess
from pathlib import Path
from typing import Iterable

from .shared import Finding

_SKILLS_PREFIX = ".github/skills/"


def _normalize_repo_path(path: str) -> str | None:
    if not isinstance(path, str) or not path or "\x00" in path:
        return None
    if path.startswith("/") or "\\" in path:
        return None

    raw_parts = path.split("/")
    if ".." in raw_parts:
        return None
    normalized = posixpath.normpath(path)
    if normalized in {"", "."} or normalized.startswith("../") or normalized == "..":
        return None
    return normalized


def protected_skill_bundle(path: str) -> str | None:
    """Return the protected direct skill bundle containing *path*, if any."""

    normalized = _normalize_repo_path(path)
    if normalized is None or not normalized.startswith(_SKILLS_PREFIX):
        return None

    parts = normalized.split("/")
    if len(parts) < 4 or parts[0:2] != [".github", "skills"]:
        return None

    bundle = parts[2]
    if bundle.startswith(("internal-", "local-")):
        return None
    return f"{_SKILLS_PREFIX}{bundle}"


def validate_allowlist(entries: Iterable[str]) -> tuple[str, ...]:
    """Validate and normalize exact protected bundle allowlist entries."""

    normalized_entries: set[str] = set()
    for entry in entries:
        if not isinstance(entry, str) or any(marker in entry for marker in "*?["):
            raise ValueError(f"Allowlist entry is not an exact bundle path: {entry!r}")
        if entry != entry.strip() or entry.endswith("/"):
            raise ValueError(f"Allowlist entry is not an exact bundle path: {entry!r}")
        normalized = _normalize_repo_path(entry)
        if normalized != entry:
            raise ValueError(f"Allowlist entry is not an exact bundle path: {entry!r}")
        parts = entry.split("/")
        if len(parts) != 3 or parts[:2] != [".github", "skills"]:
            raise ValueError(f"Allowlist entry is not an exact bundle path: {entry!r}")
        bundle = parts[2]
        if not bundle or bundle.startswith(("internal-", "local-")):
            raise ValueError(f"Allowlist entry is not a protected bundle: {entry!r}")
        normalized_entries.add(entry)
    return tuple(sorted(normalized_entries))


def _git_paths(root: Path, *args: str) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return tuple(os.fsdecode(value) for value in result.stdout.split(b"\0") if value)


def collect_changed_paths(root: Path, base_ref: str | None = None) -> tuple[str, ...]:
    """Collect current worktree and optional committed changes as repo paths."""

    paths: set[str] = set()
    for args in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        paths.update(_git_paths(root, *args))
    if base_ref:
        paths.update(_git_paths(root, "diff", "--name-only", "-z", f"{base_ref}...HEAD"))
    return tuple(sorted(paths))


def detect_protected_skill_changes(
    changed_paths: Iterable[str],
    allowed_bundles: Iterable[str],
) -> list[Finding]:
    """Create one blocking finding for each unallowed protected bundle."""

    allowed = set(validate_allowlist(allowed_bundles))
    bundles = {
        bundle
        for path in changed_paths
        if (bundle := protected_skill_bundle(path)) is not None
    }
    return [
        Finding(
            severity="blocking",
            code="protected-skill-change",
            path=bundle,
            message=f"Protected skill bundle has changed without an exact allowlist entry: {bundle}",
            suggestion=(
                "Obtain explicit current-user authorization for the exact bundle, "
                "or revert the protected-skill change."
            ),
        )
        for bundle in sorted(bundles - allowed)
    ]
