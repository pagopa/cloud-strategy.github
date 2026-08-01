from __future__ import annotations

import fcntl
import hashlib
import io
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sync_external_resources_core import (
    ManagedResources,
    ManagedSource,
    SyncCommandError,
    _run_command,
    compute_prepared_source_paths_sha256,
)


NETWORK_COMMAND_TIMEOUT_SECONDS = 1800


@dataclass(frozen=True)
class PrepareSourceResult:
    source_id: str
    repository: str
    ref: str
    cache_status: Literal["cached", "fetched", "rebuilt"]
    fetch_strategy: Literal["cache", "direct-sha", "advertised-ref"]
    materialized_files: int
    materialized_bytes: int
    cache_bytes_added: int
    duration_ms: int


def _cache_key_for_repository(repository: str) -> str:
    return hashlib.sha256(repository.encode("utf-8")).hexdigest()


def _build_fetch_command(sha: str) -> list[str]:
    return [
        "git",
        "-c",
        "fetch.fsckObjects=true",
        "fetch",
        "origin",
        sha,
        "--no-tags",
        "--no-recurse-submodules",
        "--no-write-fetch-head",
        "--filter=blob:none",
        "--refmap=",
    ]


_FORBIDDEN_UPSTREAM_CHARS = {"\\", "\x00"}


def _validate_upstream_paths(paths: list[str] | tuple[str, ...]) -> None:
    if not paths:
        raise ValueError("upstream paths must not be empty")

    normalized: list[str] = []
    for path in paths:
        if not path:
            raise ValueError("upstream path must not be empty")
        if path in (".", ".."):
            raise ValueError(f"upstream path must not be . or ..: {path!r}")
        if path.startswith("/"):
            raise ValueError(f"upstream path must not be absolute: {path!r}")
        if any(ch in path for ch in _FORBIDDEN_UPSTREAM_CHARS):
            raise ValueError(
                f"upstream path contains forbidden character: {path!r}"
            )
        parts = path.split("/")
        if ".." in parts:
            raise ValueError(
                f"upstream path must not contain ..: {path!r}"
            )
        normalized.append(path)

    seen: set[str] = set()
    for path in sorted(normalized):
        for existing in seen:
            if path.startswith(existing + "/"):
                raise ValueError(
                    f"overlapping upstream paths: {existing!r} and {path!r}"
                )
        if path in seen:
            raise ValueError(f"duplicate upstream path: {path!r}")
        seen.add(path)


def _cache_dir(workspace: Path, repository: str) -> Path:
    key = _cache_key_for_repository(repository)
    return workspace / "cache" / "repositories" / key


def _lock_path(cache: Path) -> Path:
    return cache.parent / f"{cache.name}.lock"


def _acquire_lock(lock_file: Path) -> int:
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _release_lock(fd: int, lock_file: Path) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _init_bare_cache(cache: Path, repository: str) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    _run_command(["git", "init", "--bare"], cwd=cache)
    _run_command(
        ["git", "config", "remote.origin.url", repository],
        cwd=cache,
    )
    _run_command(
        ["git", "config", "remote.origin.fetch", ""],
        cwd=cache,
    )
    _run_command(
        ["git", "config", "remote.origin.tagOpt", "--no-tags"],
        cwd=cache,
    )
    _run_command(
        ["git", "config", "core.repositoryFormatVersion", "1"],
        cwd=cache,
    )
    _run_command(
        ["git", "config", "extensions.partialClone", "origin"],
        cwd=cache,
    )
    _run_command(
        ["git", "config", "remote.origin.promisor", "true"],
        cwd=cache,
    )


def _pin_ref(sha: str) -> str:
    return f"refs/cache/pins/{sha}"


def _has_pin(cache: Path, sha: str) -> bool:
    pin = _pin_ref(sha)
    result = subprocess.run(
        ["git", "rev-parse", "--verify", pin],
        cwd=cache,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return result.stdout.strip() == sha


def _verify_commit(cache: Path, sha: str) -> None:
    result = _run_command(
        ["git", "rev-parse", "--verify", f"{sha}^{{commit}}"],
        cwd=cache,
    )
    resolved = result.stdout.strip()
    if resolved != sha:
        raise ValueError(
            f"commit verification mismatch: expected {sha}, got {resolved}"
        )
    type_result = _run_command(
        ["git", "cat-file", "-t", sha],
        cwd=cache,
    )
    obj_type = type_result.stdout.strip()
    if obj_type != "commit":
        raise ValueError(f"object {sha} is {obj_type}, expected commit")


def _write_pin(cache: Path, sha: str) -> None:
    _run_command(
        ["git", "update-ref", _pin_ref(sha), sha],
        cwd=cache,
    )


def _fetch_sha(cache: Path, sha: str) -> None:
    cmd = _build_fetch_command(sha)
    _run_command(cmd, cwd=cache, timeout=NETWORK_COMMAND_TIMEOUT_SECONDS)


def _fetch_advertised_ref(cache: Path, ref: str) -> None:
    cmd = [
        "git",
        "-c",
        "fetch.fsckObjects=true",
        "fetch",
        "origin",
        ref,
        "--no-tags",
        "--no-recurse-submodules",
        "--no-write-fetch-head",
        "--filter=blob:none",
        "--refmap=",
    ]
    _run_command(cmd, cwd=cache, timeout=NETWORK_COMMAND_TIMEOUT_SECONDS)


def _cache_size(cache: Path) -> int:
    total = 0
    objects_dir = cache / "objects"
    if not objects_dir.exists():
        return 0
    for entry in objects_dir.rglob("*"):
        if entry.is_file() and not entry.name.endswith(".lock"):
            total += entry.stat().st_size
    return total


def _fetch_source(
    cache: Path,
    source: ManagedSource,
) -> tuple[Literal["cached", "fetched"], Literal["cache", "direct-sha", "advertised-ref"]]:
    if _has_pin(cache, source.ref):
        return "cached", "cache"

    fetch_strategy: Literal["direct-sha", "advertised-ref"] = "direct-sha"
    try:
        _fetch_sha(cache, source.ref)
    except SyncCommandError:
        if source.advertised_ref is None:
            raise
        _fetch_advertised_ref(cache, source.advertised_ref)
        fetch_strategy = "advertised-ref"

    _verify_commit(cache, source.ref)
    _write_pin(cache, source.ref)

    return "fetched", fetch_strategy


def _safe_filter(member: tarfile.TarInfo, dest_path: str) -> tarfile.TarInfo:
    if member.name.startswith("/"):
        raise tarfile.FilterError(f"absolute path in tar member: {member.name!r}")
    result = tarfile.data_filter(member, dest_path)
    return result


def _extract_archive(archive_bytes: bytes, export_dir: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as tar:
        tar.extractall(path=export_dir, filter=_safe_filter)


def _export_paths(
    cache: Path,
    source: ManagedSource,
    export_dir: Path,
) -> tuple[int, int]:
    upstream_paths = [asset.upstream for asset in source.assets]

    cmd = [
        "git",
        "-C",
        str(cache),
        "archive",
        source.ref,
        "--",
        *upstream_paths,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SyncCommandError(
            cmd,
            result.returncode,
            result.stderr.decode("utf-8", errors="replace")[:500],
        )

    _extract_archive(result.stdout, export_dir)

    files_count = 0
    bytes_count = 0
    for entry in export_dir.rglob("*"):
        if entry.is_file():
            files_count += 1
            bytes_count += entry.lstat().st_size
        elif entry.is_symlink():
            files_count += 1
            bytes_count += len(os.readlink(entry))

    return files_count, bytes_count


def _write_source_metadata(
    snapshot: Path,
    source: ManagedSource,
) -> None:
    digest = compute_prepared_source_paths_sha256(source)
    tsv_content = (
        f"source_id\trepository\tref\tpaths_sha256\n"
        f"{source.source_id}\t{source.repository}\t{source.ref}\t{digest}\n"
    )
    (snapshot / ".external-resource-source.tsv").write_text(
        tsv_content, encoding="utf-8"
    )


def _publish_snapshot_atomic(
    sources_root: Path,
    source_id: str,
    staging: Path,
    source: ManagedSource,
) -> None:
    target = sources_root / source_id
    prior = target.parent / f"{target.name}.prior"

    _write_source_metadata(staging, source)

    if target.exists():
        if prior.exists():
            shutil.rmtree(prior)
        target.rename(prior)

    try:
        staging.rename(target)
    except Exception:
        if prior.exists():
            prior.rename(target)
        raise

    if prior.exists():
        shutil.rmtree(prior)


def _rebuild_cache_beside(
    cache: Path,
    source: ManagedSource,
) -> tuple[Literal["direct-sha", "advertised-ref"], int]:
    staging = cache.parent / f"{cache.name}.rebuild"
    prior = cache.parent / f"{cache.name}.prior"
    if staging.exists():
        shutil.rmtree(staging)
    if prior.exists():
        shutil.rmtree(prior)

    _init_bare_cache(staging, source.repository)
    _, fetch_strategy = _fetch_source(staging, source)
    if fetch_strategy == "cache":
        raise ValueError("rebuilt cache must perform a fetch")
    rebuilt_bytes = _cache_size(staging)

    if cache.exists():
        cache.rename(prior)
    try:
        staging.rename(cache)
    except Exception:
        if prior.exists():
            prior.rename(cache)
        raise
    if prior.exists():
        shutil.rmtree(prior)

    return fetch_strategy, rebuilt_bytes


def _prepare_one_source(
    source: ManagedSource,
    workspace: Path,
    sources_root: Path,
    rebuild_cache: bool,
) -> PrepareSourceResult:
    start = time.monotonic()
    cache = _cache_dir(workspace, source.repository)
    lock_file = _lock_path(cache)
    fd = _acquire_lock(lock_file)

    try:
        needs_init = not (cache / "HEAD").exists()
        if needs_init:
            _init_bare_cache(cache, source.repository)

        if rebuild_cache and (cache / "HEAD").exists():
            fetch_strategy, rebuilt_bytes = _rebuild_cache_beside(cache, source)
            cache_status: Literal["cached", "fetched", "rebuilt"] = "rebuilt"
            bytes_added = rebuilt_bytes
        else:
            before = _cache_size(cache)
            cache_status, fetch_strategy = _fetch_source(cache, source)
            bytes_added = max(0, _cache_size(cache) - before)

        staging_dir = sources_root.parent / f".{source.source_id}.staging"
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        staging_dir.mkdir(parents=True)

        try:
            files_count, bytes_count = _export_paths(
                cache, source, staging_dir
            )
            _publish_snapshot_atomic(
                sources_root, source.source_id, staging_dir, source
            )
        except Exception:
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            raise

    finally:
        _release_lock(fd, lock_file)

    elapsed_ms = int((time.monotonic() - start) * 1000)

    return PrepareSourceResult(
        source_id=source.source_id,
        repository=source.repository,
        ref=source.ref,
        cache_status=cache_status,
        fetch_strategy=fetch_strategy,
        materialized_files=files_count,
        materialized_bytes=bytes_count,
        cache_bytes_added=bytes_added,
        duration_ms=elapsed_ms,
    )


def prepare_sources(
    resources: ManagedResources,
    workspace: Path,
    sources_root: Path,
    *,
    rebuild_cache: bool = False,
) -> tuple[PrepareSourceResult, ...]:
    sources_root.mkdir(parents=True, exist_ok=True)
    results: list[PrepareSourceResult] = []
    for source in resources.sources:
        _validate_upstream_paths(
            [asset.upstream for asset in source.assets]
        )
        result = _prepare_one_source(
            source, workspace, sources_root, rebuild_cache
        )
        results.append(result)
    return tuple(results)
