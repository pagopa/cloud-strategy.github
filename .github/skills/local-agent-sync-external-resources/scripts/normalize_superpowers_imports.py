#!/usr/bin/env python3
"""Normalize imported obra/superpowers assets to local `superpowers-*` ids.

Dependency decision note:
- Candidates: JSON in the standard library, PyYAML.
- Final choice: PyYAML.
- Why: the repository already uses YAML for sync registries, so the normalizer
  can share the catalog reference format without adding a new dependency.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_REFERENCE = (
    ".github/skills/local-agent-sync-external-resources/references/superpowers-normalization.yaml"
)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".jsonc", ".py", ".patch"}


@dataclass(frozen=True)
class ManagedSkill:
    upstream: str
    legacy_local: str
    local: str


@dataclass(frozen=True)
class ManagedPatch:
    legacy_path: str
    path: str


@dataclass(frozen=True)
class NormalizationConfig:
    reference_path: Path
    managed_skills: tuple[ManagedSkill, ...]
    managed_patches: tuple[ManagedPatch, ...]
    scan_includes: tuple[str, ...]
    ignored_files: frozenset[str]


@dataclass(frozen=True)
class NormalizationChange:
    kind: str
    path: str
    detail: str

    def render(self) -> str:
        return f"{self.kind}: {self.path} ({self.detail})"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize imported obra/superpowers assets to local superpowers-* ids."
    )
    parser.add_argument(
        "--repo-root",
        help="Repository root. Defaults to the nearest parent that contains .github/.",
    )
    parser.add_argument(
        "--reference",
        default=DEFAULT_REFERENCE,
        help="Path to superpowers-normalization.yaml, relative to the repository root by default.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Report drift without writing changes.")
    mode.add_argument("--apply", action="store_true", help="Rewrite paths and text in place.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(Path(args.repo_root)) if args.repo_root else find_repo_root(Path.cwd())
    reference_path = resolve_reference_path(repo_root, Path(args.reference))
    config = load_config(reference_path)

    if args.check:
        changes = detect_drift(repo_root, config)
        if not changes:
            print("✅ Superpowers import naming is normalized.")
            return 0
        print("❌ Superpowers import naming drift found:", file=sys.stderr)
        for change in changes:
            print(f"- {change.render()}", file=sys.stderr)
        return 1

    try:
        changes = apply_normalization(repo_root, config)
    except FileExistsError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 1

    if not changes:
        print("✅ Superpowers import naming was already normalized.")
        return 0

    print(f"✅ Applied {len(changes)} superpowers normalization change(s).")
    for change in changes:
        print(f"- {change.render()}")
    return 0


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


def resolve_reference_path(repo_root: Path, raw_reference_path: Path) -> Path:
    if raw_reference_path.is_absolute():
        return raw_reference_path
    return repo_root / raw_reference_path


def load_config(reference_path: Path) -> NormalizationConfig:
    payload = yaml.safe_load(reference_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("Normalization reference must be a YAML mapping.")

    managed_skills = tuple(load_managed_skills(payload))
    managed_patches = tuple(load_managed_patches(payload))
    live_scan = payload.get("live_scan") if isinstance(payload.get("live_scan"), dict) else {}
    raw_includes = live_scan.get("include") if isinstance(live_scan, dict) else None
    scan_includes = tuple(item for item in raw_includes or () if isinstance(item, str) and item.strip())
    raw_ignored_files = live_scan.get("ignored_files") if isinstance(live_scan, dict) else None
    ignored_files = {"README.md", "CHANGELOG.md", reference_path.name}
    if isinstance(raw_ignored_files, list):
        ignored_files.update(item for item in raw_ignored_files if isinstance(item, str) and item.strip())

    return NormalizationConfig(
        reference_path=reference_path,
        managed_skills=managed_skills,
        managed_patches=managed_patches,
        scan_includes=scan_includes,
        ignored_files=frozenset(ignored_files),
    )


def load_managed_skills(payload: dict[str, object]) -> list[ManagedSkill]:
    raw_entries = payload.get("managed_skills")
    if not isinstance(raw_entries, list):
        raise ValueError("Normalization reference must define a managed_skills list.")

    managed_skills: list[ManagedSkill] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("Each managed skill entry must be a mapping.")
        upstream = require_string(raw_entry, "upstream")
        legacy_local = require_string(raw_entry, "legacy_local")
        local = require_string(raw_entry, "local")
        managed_skills.append(ManagedSkill(upstream=upstream, legacy_local=legacy_local, local=local))
    return managed_skills


def load_managed_patches(payload: dict[str, object]) -> list[ManagedPatch]:
    raw_entries = payload.get("managed_patches", [])
    if not isinstance(raw_entries, list):
        raise ValueError("managed_patches must be a list when present.")

    managed_patches: list[ManagedPatch] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("Each managed patch entry must be a mapping.")
        legacy_path = require_string(raw_entry, "legacy_path")
        path = require_string(raw_entry, "path")
        managed_patches.append(ManagedPatch(legacy_path=legacy_path, path=path))
    return managed_patches


def require_string(raw_entry: dict[str, object], key: str) -> str:
    value = raw_entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing non-empty `{key}` in normalization reference.")
    return value.strip()


def detect_drift(repo_root: Path, config: NormalizationConfig) -> list[NormalizationChange]:
    changes: list[NormalizationChange] = []
    for old_relative_path, new_relative_path in path_renames(config):
        if (repo_root / old_relative_path).exists():
            changes.append(
                NormalizationChange("legacy-path", old_relative_path, f"rename to {new_relative_path}")
            )

    for file_path in collect_scan_files(repo_root, config):
        relative_path = file_path.relative_to(repo_root).as_posix()
        text = file_path.read_text(encoding="utf-8")
        for old_text, new_text in text_replacements(config):
            if old_text in text:
                changes.append(NormalizationChange("legacy-reference", relative_path, f"{old_text} -> {new_text}"))

    return changes


def apply_normalization(repo_root: Path, config: NormalizationConfig) -> list[NormalizationChange]:
    changes: list[NormalizationChange] = []
    for old_relative_path, new_relative_path in path_renames(config):
        old_path = repo_root / old_relative_path
        new_path = repo_root / new_relative_path
        if not old_path.exists():
            continue
        if new_path.exists():
            raise FileExistsError(
                f"Cannot rename {old_relative_path} to {new_relative_path}: target already exists."
            )
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)
        changes.append(NormalizationChange("renamed-path", old_relative_path, f"to {new_relative_path}"))

    replacements = text_replacements(config)
    for file_path in collect_scan_files(repo_root, config):
        original_text = file_path.read_text(encoding="utf-8")
        updated_text = original_text
        applied_replacements: list[str] = []
        for old_text, new_text in replacements:
            if old_text not in updated_text:
                continue
            updated_text = updated_text.replace(old_text, new_text)
            applied_replacements.append(f"{old_text} -> {new_text}")
        if updated_text == original_text:
            continue
        file_path.write_text(updated_text, encoding="utf-8")
        relative_path = file_path.relative_to(repo_root).as_posix()
        changes.append(NormalizationChange("updated-text", relative_path, "; ".join(applied_replacements)))

    return changes


def path_renames(config: NormalizationConfig) -> list[tuple[str, str]]:
    skill_renames = [
        (f".github/skills/{entry.legacy_local}", f".github/skills/{entry.local}")
        for entry in config.managed_skills
    ]
    patch_root = config.reference_path.parent.parent.relative_to(find_repo_root(config.reference_path))
    patch_renames = [
        ((patch_root / entry.legacy_path).as_posix(), (patch_root / entry.path).as_posix())
        for entry in config.managed_patches
    ]
    return skill_renames + patch_renames


def text_replacements(config: NormalizationConfig) -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    for entry in config.managed_skills:
        replacements.append((entry.legacy_local, entry.local))
        replacements.append((f"superpowers:{entry.upstream}", entry.local))
    for entry in config.managed_patches:
        replacements.append((entry.legacy_path, entry.path))
    return replacements


def collect_scan_files(repo_root: Path, config: NormalizationConfig) -> list[Path]:
    paths: set[Path] = set()
    for include in config.scan_includes:
        candidate = repo_root / include
        if candidate.is_file() and should_scan(candidate, repo_root, config):
            paths.add(candidate)
            continue
        if not candidate.is_dir():
            continue
        for child in candidate.rglob("*"):
            if child.is_file() and should_scan(child, repo_root, config):
                paths.add(child)
    return sorted(paths)


def should_scan(path: Path, repo_root: Path, config: NormalizationConfig) -> bool:
    relative_parts = path.relative_to(repo_root).parts
    if path.name in config.ignored_files:
        return False
    if "__pycache__" in relative_parts or ".venv" in relative_parts:
        return False
    return path.suffix in TEXT_SUFFIXES


if __name__ == "__main__":
    raise SystemExit(main())