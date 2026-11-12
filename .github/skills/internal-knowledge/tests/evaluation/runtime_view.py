"""Build a sanitized runtime workspace with fixture gold kept outside it."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path, PurePosixPath
from typing import Any

from knowledge_graders.core import load_strict_json

TREE_FIELDS = frozenset({"schema", "id", "description", "files"})


def _safe_tree_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"unsafe fixture path: {value!r}")
    parts = value.split("/")
    if (
        value.startswith("./")
        or value.startswith("/")
        or any(part in {"", ".", ".."} for part in parts)
        or (len(value) >= 2 and value[1] == ":")
    ):
        raise ValueError(f"unsafe fixture path: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or pure.as_posix() != value:
        raise ValueError(f"unsafe fixture path: {value!r}")
    return value


def _runtime_sources(bundle_root: Path) -> list[Path]:
    sources = [bundle_root / "SKILL.md"]
    for directory in (bundle_root / "references", bundle_root / "agents"):
        if directory.exists():
            if directory.is_symlink() or not directory.is_dir():
                raise ValueError(f"runtime directory is not a real directory: {directory}")
            sources.extend(sorted(directory.rglob("*")))
    if not sources[0].is_file() or sources[0].is_symlink():
        raise ValueError("bundle must contain a regular SKILL.md")
    for source in sources[1:]:
        if source.is_symlink():
            raise ValueError(f"runtime view cannot include symlinks: {source}")
        if not source.is_dir() and not source.is_file():
            raise ValueError(f"unsupported runtime file type: {source}")
    return [source for source in sources if source.is_file()]


def build_runtime_view(
    bundle_root: Path, tree_file: Path, destination: Path
) -> dict[str, str]:
    """Copy the runtime contract and fixture tree, returning file SHA-256s."""
    bundle = Path(bundle_root).resolve(strict=True)
    requested_target = Path(destination).absolute()
    if any(path.is_symlink() for path in (requested_target, *requested_target.parents)):
        raise ValueError("runtime view destination cannot pass through a symlink")
    target = requested_target.resolve(strict=False)
    if target == bundle or target.is_relative_to(bundle):
        raise ValueError("runtime view destination must be outside the bundle")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError("runtime view destination must be absent or empty")
    tree = load_strict_json(Path(tree_file))
    if set(tree) != TREE_FIELDS or tree.get("schema") != "knowledge-fixture-tree/v1":
        raise ValueError("fixture tree has invalid fields or schema")
    if not isinstance(tree.get("id"), str) or not tree["id"].strip():
        raise ValueError("fixture tree id must be non-empty text")
    if not isinstance(tree.get("description"), str) or not tree["description"].strip():
        raise ValueError("fixture tree description must be non-empty text")
    files = tree.get("files")
    if not isinstance(files, dict):
        raise ValueError("fixture tree files must be an object")
    safe_files: dict[str, str] = {}
    for raw_path, content in files.items():
        path = _safe_tree_path(raw_path)
        if not isinstance(content, str):
            raise ValueError(f"fixture content must be text: {raw_path}")
        safe_files[path] = content
    names = set(safe_files)
    for name in names:
        parent = PurePosixPath(name).parent
        while parent.as_posix() != ".":
            if parent.as_posix() in names:
                raise ValueError(f"fixture file is also a parent directory: {parent}")
            parent = parent.parent

    sources = _runtime_sources(bundle)
    runtime_root = target / "skill" / "internal-knowledge"
    workspace_root = target / "workspace"
    runtime_root.mkdir(parents=True, exist_ok=True)
    workspace_root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    for source in sources:
        relative = source.relative_to(bundle)
        destination_file = runtime_root / relative
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination_file)
        manifest[(Path("skill") / "internal-knowledge" / relative).as_posix()] = hashlib.sha256(
            destination_file.read_bytes()
        ).hexdigest()
    for relative, content in safe_files.items():
        destination_file = workspace_root.joinpath(*PurePosixPath(relative).parts)
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        destination_file.write_text(content, encoding="utf-8")
        manifest[(Path("workspace") / relative).as_posix()] = hashlib.sha256(
            destination_file.read_bytes()
        ).hexdigest()
    return manifest


def assert_gold_unreachable(destination: Path, bundle_root: Path) -> None:
    """Assert no runtime file is byte-identical to fixture or eval gold data."""
    runtime = Path(destination).resolve(strict=True)
    bundle = Path(bundle_root).resolve(strict=True)
    if not runtime.is_dir():
        raise AssertionError(f"runtime view is not a directory: {runtime}")
    sensitive_roots = [bundle / "tests" / "evaluation", bundle / "evals"]
    hashes: dict[str, str] = {}
    for root in sensitive_roots:
        if not root.exists():
            continue
        for source in sorted(root.rglob("*")):
            if source.is_symlink() or not source.is_file():
                continue
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            hashes.setdefault(digest, source.relative_to(bundle).as_posix())
    for current, directories, filenames in os.walk(runtime, followlinks=False):
        current_path = Path(current)
        if any((current_path / name).is_symlink() for name in directories):
            raise AssertionError(f"runtime view contains a symlink directory: {current_path}")
        for filename in filenames:
            candidate = current_path / filename
            if candidate.is_symlink():
                raise AssertionError(f"runtime view contains a symlink: {candidate}")
            if not candidate.is_file():
                continue
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if digest in hashes:
                raise AssertionError(
                    f"runtime file {candidate.relative_to(runtime)} matches sealed data {hashes[digest]}"
                )
