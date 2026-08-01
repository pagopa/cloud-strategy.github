from __future__ import annotations

import hashlib
import io
import os
import stat
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from source_prepare_core import (  # noqa: E402
    _build_fetch_command,
    _cache_key_for_repository,
    _extract_archive,
    _validate_upstream_paths,
    prepare_sources,
)
from sync_external_resources_core import (  # noqa: E402
    ManagedAsset,
    ManagedResources,
    ManagedSource,
    validate_prepared_sources,
)

_FULL_SHA40 = "a" * 40


def _write_prepared_metadata(
    sources_root: Path,
    source: ManagedSource,
    *,
    source_id: str | None = None,
    repository: str | None = None,
    ref: str | None = None,
    paths_sha256: str | None = None,
) -> None:
    source_dir = sources_root / source.source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    upstream_paths = sorted(asset.upstream for asset in source.assets)
    expected_paths_sha256 = hashlib.sha256(
        ",".join(upstream_paths).encode("utf-8")
    ).hexdigest()
    row = {
        "source_id": source_id or source.source_id,
        "repository": repository or source.repository,
        "ref": ref or source.ref,
        "paths_sha256": paths_sha256 or expected_paths_sha256,
    }
    metadata = (
        "source_id\trepository\tref\tpaths_sha256\n"
        f"{row['source_id']}\t{row['repository']}\t{row['ref']}\t"
        f"{row['paths_sha256']}\n"
    )
    (source_dir / ".external-resource-source.tsv").write_text(
        metadata, encoding="utf-8"
    )


def _metadata_resources() -> ManagedResources:
    asset = ManagedAsset(
        source="test-source",
        upstream="skills/example",
        local=".github/skills/example",
        canonical_name="example",
    )
    source = ManagedSource(
        source_id="test-source",
        repository="https://example.com/repo.git",
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset,),
    )
    return ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )


def _run_git(cwd: Path, args: list[str]) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_all(repo: Path) -> str:
    _run_git(repo, ["add", "-A"])
    _run_git(repo, ["commit", "-m", "snapshot", "--allow-empty"])
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_cache_key_is_deterministic_sha256() -> None:
    url = "https://github.com/example/repo.git"
    key = _cache_key_for_repository(url)
    expected = hashlib.sha256(url.encode("utf-8")).hexdigest()
    assert key == expected


def test_cache_key_shared_across_source_ids() -> None:
    url = "https://github.com/openai/skills.git"
    assert _cache_key_for_repository(url) == _cache_key_for_repository(url)


def test_fetch_command_includes_required_flags() -> None:
    sha = "a" * 40
    cmd = _build_fetch_command(sha)
    cmd_str = " ".join(cmd)
    assert "--filter=blob:none" in cmd_str
    assert "--no-tags" in cmd_str
    assert "--no-recurse-submodules" in cmd_str
    assert "--no-write-fetch-head" in cmd_str
    assert "--refmap=" in cmd_str
    assert "-c" in cmd
    idx = cmd.index("-c")
    assert cmd[idx + 1] == "fetch.fsckObjects=true"


@pytest.fixture
def fixture_remote(tmp_path: Path) -> tuple[Path, str]:
    remote = tmp_path / "remote.git"
    remote.mkdir()
    _run_git(remote, ["init", "--bare"])
    _run_git(remote, ["config", "uploadpack.allowReachableSHA1InWant", "true"])
    _run_git(remote, ["config", "uploadpack.allowFilter", "true"])

    work = tmp_path / "work"
    work.mkdir()
    _run_git(work, ["init"])
    _run_git(work, ["config", "user.email", "test@test.com"])
    _run_git(work, ["config", "user.name", "Test"])

    skill_dir = work / "skills" / "target-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: target-skill\n---\nTarget content.\n",
        encoding="utf-8",
    )

    script = skill_dir / "run.sh"
    script.write_text("#!/bin/sh\necho hello\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    link_target = skill_dir / "inner.txt"
    link_target.write_text("inner\n", encoding="utf-8")
    link = skill_dir / "link-to-inner"
    link.symlink_to("inner.txt")

    decoy = work / "decoy-8mib.bin"
    decoy.write_bytes(b"\x00" * (8 * 1024 * 1024))

    other_skill = work / "skills" / "other-skill" / "SKILL.md"
    other_skill.parent.mkdir(parents=True)
    other_skill.write_text("---\nname: other\n---\n", encoding="utf-8")

    commit_sha = _commit_all(work)
    _run_git(work, ["remote", "add", "origin", str(remote)])
    _run_git(work, ["push", "origin", "HEAD:refs/heads/main"])

    return remote, commit_sha


def test_prepare_sources_cold_fetch_creates_selective_snapshot(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    asset = ManagedAsset(
        source="test-source",
        upstream="skills/target-skill",
        local=".github/skills/target-skill",
        canonical_name="target-skill",
    )
    source = ManagedSource(
        source_id="test-source",
        repository=str(remote_path),
        ref=commit_sha,
        advertised_ref=None,
        assets=(asset,),
    )
    resources = ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )

    results = prepare_sources(resources, workspace, sources_root)

    assert len(results) == 1
    result = results[0]
    assert result.source_id == "test-source"
    assert result.ref == commit_sha
    assert result.cache_status in ("fetched", "cached")
    assert result.materialized_files >= 3
    assert result.materialized_bytes > 0

    snapshot = sources_root / "test-source"
    assert snapshot.exists()

    skill_md = snapshot / "skills" / "target-skill" / "SKILL.md"
    assert skill_md.exists()
    assert "Target content." in skill_md.read_text(encoding="utf-8")

    run_sh = snapshot / "skills" / "target-skill" / "run.sh"
    assert run_sh.exists()
    assert os.access(run_sh, os.X_OK)

    link = snapshot / "skills" / "target-skill" / "link-to-inner"
    assert link.is_symlink()
    assert link.read_text(encoding="utf-8") == "inner\n"

    assert not (snapshot / ".git").exists()
    assert not (snapshot / "decoy-8mib.bin").exists()
    assert not (snapshot / "skills" / "other-skill").exists()

    metadata_path = snapshot / ".external-resource-source.tsv"
    assert metadata_path.read_text(encoding="utf-8") == (
        "source_id\trepository\tref\tpaths_sha256\n"
        f"test-source\t{remote_path}\t{commit_sha}\t"
        f"{hashlib.sha256(b'skills/target-skill').hexdigest()}\n"
    )
    validate_prepared_sources(resources, sources_root)


def test_prepare_sources_warm_run_is_cached(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    asset = ManagedAsset(
        source="test-source",
        upstream="skills/target-skill",
        local=".github/skills/target-skill",
        canonical_name="target-skill",
    )
    source = ManagedSource(
        source_id="test-source",
        repository=str(remote_path),
        ref=commit_sha,
        advertised_ref=None,
        assets=(asset,),
    )
    resources = ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )

    first = prepare_sources(resources, workspace, sources_root)
    second = prepare_sources(resources, workspace, sources_root)

    assert second[0].cache_status == "cached"
    assert second[0].cache_bytes_added == 0
    assert second[0].materialized_files == first[0].materialized_files
    assert second[0].materialized_bytes == first[0].materialized_bytes


def test_prepare_sources_cold_metrics(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    asset = ManagedAsset(
        source="test-source",
        upstream="skills/target-skill",
        local=".github/skills/target-skill",
        canonical_name="target-skill",
    )
    source = ManagedSource(
        source_id="test-source",
        repository=str(remote_path),
        ref=commit_sha,
        advertised_ref=None,
        assets=(asset,),
    )
    resources = ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )

    results = prepare_sources(resources, workspace, sources_root)
    result = results[0]

    assert result.cache_status == "fetched"
    assert result.materialized_bytes < 1 * 1024 * 1024
    assert result.cache_bytes_added > 0
    assert result.duration_ms >= 0


def test_prepare_sources_warm_metrics(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    asset = ManagedAsset(
        source="test-source",
        upstream="skills/target-skill",
        local=".github/skills/target-skill",
        canonical_name="target-skill",
    )
    source = ManagedSource(
        source_id="test-source",
        repository=str(remote_path),
        ref=commit_sha,
        advertised_ref=None,
        assets=(asset,),
    )
    resources = ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )

    first = prepare_sources(resources, workspace, sources_root)
    second = prepare_sources(resources, workspace, sources_root)

    assert second[0].cache_status == "cached"
    assert second[0].cache_bytes_added == 0
    assert second[0].materialized_files == first[0].materialized_files
    assert second[0].materialized_bytes == first[0].materialized_bytes


def test_validate_upstream_paths_rejects_absolute() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths(["/etc/passwd"])


def test_validate_upstream_paths_rejects_empty() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths([""])


def test_validate_upstream_paths_rejects_dot() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths(["."])


def test_validate_upstream_paths_rejects_dotdot() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths([".."])


def test_validate_upstream_paths_rejects_backslash() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths(["skills\\bad"])


def test_validate_upstream_paths_rejects_duplicate() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths(["skills/a", "skills/a"])


def test_validate_upstream_paths_rejects_overlapping() -> None:
    with pytest.raises(ValueError):
        _validate_upstream_paths(["skills", "skills/sub"])


def test_validate_prepared_sources_reports_missing_metadata(
    tmp_path: Path,
) -> None:
    asset = ManagedAsset(
        source="test-source",
        upstream="skills/example",
        local=".github/skills/example",
        canonical_name="example",
    )
    source = ManagedSource(
        source_id="test-source",
        repository="https://example.com/repo.git",
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset,),
    )
    resources = ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    with pytest.raises(ValueError) as exc_info:
        validate_prepared_sources(resources, sources_root)
    message = str(exc_info.value)
    assert "Missing prepared source metadata:" in message
    assert "Run prepare before audit/plan/apply." in message


def test_validate_prepared_sources_accepts_exact_attestation(
    tmp_path: Path,
) -> None:
    resources = _metadata_resources()
    sources_root = tmp_path / "sources"
    _write_prepared_metadata(sources_root, resources.sources[0])

    validate_prepared_sources(resources, sources_root)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("source_id", "other-source"),
        ("repository", "https://example.com/other.git"),
        ("ref", "b" * 40),
        ("paths_sha256", "0" * 64),
    ),
)
def test_validate_prepared_sources_rejects_attestation_mismatch(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    resources = _metadata_resources()
    source = resources.sources[0]
    sources_root = tmp_path / "sources"
    _write_prepared_metadata(sources_root, source, **{field: value})

    with pytest.raises(ValueError, match=field):
        validate_prepared_sources(resources, sources_root)


def test_validate_prepared_sources_rejects_wrong_header_or_row_count(
    tmp_path: Path,
) -> None:
    resources = _metadata_resources()
    source = resources.sources[0]
    metadata_path = (
        tmp_path / "sources" / source.source_id / ".external-resource-source.tsv"
    )
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(
        "source_id\trepository\tref\n"
        f"{source.source_id}\t{source.repository}\t{source.ref}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="header"):
        validate_prepared_sources(resources, tmp_path / "sources")


def test_validate_prepared_sources_rejects_extra_data_row(
    tmp_path: Path,
) -> None:
    resources = _metadata_resources()
    source = resources.sources[0]
    metadata_path = (
        tmp_path / "sources" / source.source_id / ".external-resource-source.tsv"
    )
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(
        "source_id\trepository\tref\tpaths_sha256\n"
        f"{source.source_id}\t{source.repository}\t{source.ref}\t"
        f"{'0' * 64}\n"
        f"{source.source_id}\t{source.repository}\t{source.ref}\t"
        f"{'1' * 64}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="row count"):
        validate_prepared_sources(resources, tmp_path / "sources")


def _tar_bytes_with(info: tarfile.TarInfo, payload: bytes = b"") -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()


def test_extract_archive_rejects_parent_traversal_member(tmp_path: Path) -> None:
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    archive = _tar_bytes_with(tarfile.TarInfo("../escaped.txt"), b"escaped\n")

    with pytest.raises(tarfile.FilterError):
        _extract_archive(archive, export_dir)

    assert not (tmp_path / "escaped.txt").exists()


def test_extract_archive_rejects_absolute_member(tmp_path: Path) -> None:
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    archive = _tar_bytes_with(tarfile.TarInfo("/tmp/escaped.txt"), b"escaped\n")

    with pytest.raises(tarfile.FilterError):
        _extract_archive(archive, export_dir)


def test_extract_archive_rejects_symlink_escaping_snapshot(tmp_path: Path) -> None:
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    info = tarfile.TarInfo("link")
    info.type = tarfile.SYMTYPE
    info.linkname = "../../etc/passwd"
    archive = _tar_bytes_with(info)

    with pytest.raises(tarfile.FilterError):
        _extract_archive(archive, export_dir)


def test_advertised_ref_fallback_is_reported_as_advertised_ref(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    asset = ManagedAsset(
        source="strict-source",
        upstream="skills/target-skill",
        local=".github/skills/target-skill",
        canonical_name="target-skill",
    )
    source = ManagedSource(
        source_id="strict-source",
        repository=str(remote_path),
        ref=commit_sha,
        advertised_ref="refs/heads/main",
        assets=(asset,),
    )
    resources = ManagedResources(sources=(source,), replacements=(), watchlist=())

    import source_prepare_core

    def failing_fetch_sha(cache: Path, sha: str) -> None:
        from sync_external_resources_core import SyncCommandError

        raise SyncCommandError(["git", "fetch"], 128, "simulated failure")

    monkeypatch.setattr(source_prepare_core, "_fetch_sha", failing_fetch_sha)

    results = prepare_sources(resources, workspace, sources_root)

    assert results[0].cache_status == "fetched"
    assert results[0].fetch_strategy == "advertised-ref"
    assert (
        sources_root / "strict-source" / "skills" / "target-skill" / "SKILL.md"
    ).exists()


def _single_source_resources(remote_path: Path, commit_sha: str) -> ManagedResources:
    asset = ManagedAsset(
        source="test-source",
        upstream="skills/target-skill",
        local=".github/skills/target-skill",
        canonical_name="target-skill",
    )
    source = ManagedSource(
        source_id="test-source",
        repository=str(remote_path),
        ref=commit_sha,
        advertised_ref=None,
        assets=(asset,),
    )
    return ManagedResources(sources=(source,), replacements=(), watchlist=())


def test_rebuild_cache_refetches_even_when_pin_is_present(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()
    resources = _single_source_resources(remote_path, commit_sha)

    warm = prepare_sources(resources, workspace, sources_root)
    assert warm[0].cache_status == "fetched"

    rebuilt = prepare_sources(resources, workspace, sources_root, rebuild_cache=True)

    assert rebuilt[0].cache_status == "rebuilt"
    assert rebuilt[0].fetch_strategy == "direct-sha"
    assert rebuilt[0].cache_bytes_added > 0
    assert (
        sources_root / "test-source" / "skills" / "target-skill" / "SKILL.md"
    ).exists()


def test_rebuild_cache_leaves_no_staging_directories(
    tmp_path: Path,
    fixture_remote: tuple[Path, str],
) -> None:
    remote_path, commit_sha = fixture_remote
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()
    resources = _single_source_resources(remote_path, commit_sha)

    prepare_sources(resources, workspace, sources_root)
    prepare_sources(resources, workspace, sources_root, rebuild_cache=True)

    repositories = workspace / "cache" / "repositories"
    leftovers = [
        entry.name
        for entry in repositories.iterdir()
        if entry.name.endswith(".rebuild") or entry.name.endswith(".prior")
    ]
    assert leftovers == []


import source_prepare_core  # noqa: E402


def test_network_fetch_uses_extended_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], int]] = []

    def fake_run_command(
        command: list[str], cwd: Path | None = None, timeout: int = 60
    ):
        calls.append((command, timeout))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(source_prepare_core, "_run_command", fake_run_command)

    source_prepare_core._fetch_sha(Path("/nonexistent-cache"), _FULL_SHA40)
    source_prepare_core._fetch_advertised_ref(
        Path("/nonexistent-cache"), "refs/heads/main"
    )

    assert source_prepare_core.NETWORK_COMMAND_TIMEOUT_SECONDS >= 900
    assert all(
        timeout == source_prepare_core.NETWORK_COMMAND_TIMEOUT_SECONDS
        for _, timeout in calls
    )
    assert len(calls) == 2
