from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

CATALOG_IGNORED_FILENAMES = {"README.md", "CHANGELOG.md"}
CATALOG_IGNORED_PARTS = frozenset({"__pycache__", ".venv"})
CONSUMER_SYNC_EXCLUDED_PREFIX = "internal-sync-"
CONSUMER_SYNC_EXCLUDED_PATH_PREFIXES = frozenset()


def iter_markdown_assets(root: Path) -> Iterator[Path]:
    candidates = [root / "AGENTS.md"]
    github_root = root / ".github"
    if github_root.exists():
        candidates.extend(
            path
            for path in github_root.rglob("*.md")
            if path.is_file()
            and not any(part in CATALOG_IGNORED_PARTS for part in path.parts)
        )
    for path in candidates:
        if path.exists():
            yield path


def is_ignored_catalog_path(relative_path: str) -> bool:
    path = Path(relative_path)
    if path.name in CATALOG_IGNORED_FILENAMES:
        return True
    if path.suffix == ".pyc":
        return True
    return any(part in CATALOG_IGNORED_PARTS for part in path.parts)


def is_local_asset(relative_path: str) -> bool:
    path = Path(relative_path)
    parts = path.parts
    if len(parts) < 3 or parts[0] != ".github":
        return False
    if parts[1] == "skills":
        return len(parts) >= 3 and parts[2].startswith("local-")
    return path.name.startswith("local-")


def is_imported_asset(relative_path: str) -> bool:
    path = Path(relative_path)
    parts = path.parts
    if len(parts) < 3 or parts[0] != ".github":
        return False
    if parts[1] == "skills":
        prefix = parts[2]
        return not prefix.startswith(("internal-", "local-"))
    if parts[1] in {"agents", "instructions"}:
        return not path.name.startswith(("internal-", "local-"))
    return False


def is_consumer_sync_excluded_path(relative_path: str) -> bool:
    path = Path(relative_path)
    if any(part.startswith(CONSUMER_SYNC_EXCLUDED_PREFIX) for part in path.parts):
        return True
    for excluded_prefix in CONSUMER_SYNC_EXCLUDED_PATH_PREFIXES:
        if (
            relative_path.startswith(excluded_prefix + "/")
            or relative_path == excluded_prefix
        ):
            return True
    return False


def resolve_markdown_target(root: Path, current_file: Path, target: str) -> Path | None:
    clean_target = target.split("#", maxsplit=1)[0].strip()
    if not clean_target:
        return None
    if "://" in clean_target or clean_target.startswith(("mailto:", "file:")):
        return None
    if clean_target.startswith("/"):
        return None
    if clean_target.startswith((".github/", "docs/")) or clean_target == "AGENTS.md":
        return root / clean_target
    return (current_file.parent / clean_target).resolve()


def path_list(root: Path, pattern: str) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.glob(pattern)
        if path.is_file()
    )


def all_files_under(root: Path, relative_dir: str) -> list[str]:
    base_dir = root / relative_dir
    if not base_dir.exists():
        return []
    results: list[str] = []
    for path in base_dir.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root).as_posix()
        if is_ignored_catalog_path(relative_path):
            continue
        results.append(relative_path)
    return sorted(results)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
