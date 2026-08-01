"""Manifest-driven CLI for auditing, planning, and applying external resource syncs."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources_core import (  # noqa: E402
    ManagedAsset,
    ManagedResources,
    OverrideResult,
    SyncCommandError,
    find_dirty_targets,
    load_managed_resources,
    load_overrides,
    materialize_candidate,
    normalize_candidate,
    replay_overrides,
    validate_external_workspace,
    validate_override_patches,
)
from sync_output_core import (  # noqa: E402
    OutputRecord,
    render_tsv,
)
from source_prepare_core import (  # noqa: E402
    PrepareSourceResult,
    prepare_sources,
)

DEFAULT_MANIFEST = (
    SCRIPT_DIR.parent / "references" / "managed-resources.yaml"
).as_posix()
DEFAULT_SNAPSHOT_ROOT = Path("tmp/external-sync-resources-snapshots")

DEFAULT_OVERRIDES = (
    SCRIPT_DIR.parent / "references" / "imported-asset-overrides.yaml"
).as_posix()


@dataclass(frozen=True)
class SyncOutcome:
    mode: Literal["prepare", "audit", "plan", "apply"]
    workspace: str | None
    managed_assets: int
    changed_paths: tuple[str, ...]
    override_results: tuple[OverrideResult, ...]
    validations: tuple[str, ...]
    blockers: tuple[str, ...]
    repository_changed: bool
    source_results: tuple[PrepareSourceResult, ...] = ()
    source_root: str | None = None

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "mode": self.mode,
            "workspace": self.workspace,
            "managed_assets": self.managed_assets,
            "changed_paths": list(self.changed_paths),
            "override_results": [
                {
                    "override_id": r.override_id,
                    "status": r.status,
                    "target_path": r.target_path,
                }
                for r in self.override_results
            ],
            "validations": list(self.validations),
            "blockers": list(self.blockers),
            "repository_changed": self.repository_changed,
        }
        if self.source_root is not None:
            result["source_root"] = self.source_root
        if self.source_results:
            result["source_results"] = [
                {
                    "source_id": r.source_id,
                    "repository": r.repository,
                    "ref": r.ref,
                    "cache_status": r.cache_status,
                    "fetch_strategy": r.fetch_strategy,
                    "materialized_files": r.materialized_files,
                    "materialized_bytes": r.materialized_bytes,
                    "cache_bytes_added": r.cache_bytes_added,
                    "duration_ms": r.duration_ms,
                }
                for r in self.source_results
            ]
        return result

    def to_records(self) -> tuple[OutputRecord, ...]:
        records: list[OutputRecord] = []
        records.append(
            OutputRecord("summary", "mode", "ok", self.mode)
        )
        records.append(
            OutputRecord(
                "summary", "managed_assets", "ok", str(self.managed_assets)
            )
        )
        records.append(
            OutputRecord(
                "summary", "changed_paths", "ok", str(len(self.changed_paths))
            )
        )
        records.append(
            OutputRecord(
                "summary",
                "override_results",
                "ok",
                str(len(self.override_results)),
            )
        )
        records.append(
            OutputRecord(
                "summary",
                "repository_changed",
                "ok",
                str(self.repository_changed).lower(),
            )
        )
        if self.workspace is not None:
            records.append(
                OutputRecord("summary", "workspace", "ok", self.workspace)
            )
        if self.source_root is not None:
            records.append(
                OutputRecord("summary", "source_root", "ok", self.source_root)
            )
        for validation in self.validations:
            records.append(
                OutputRecord("validation", validation, "ok", "")
            )
        for blocker in self.blockers:
            records.append(
                OutputRecord("blocker", blocker, "fail", "")
            )
        for path in self.changed_paths:
            records.append(
                OutputRecord("change", path, "ok", "")
            )
        for result in self.override_results:
            records.append(
                OutputRecord(
                    "override",
                    result.override_id,
                    result.status,
                    result.target_path,
                )
            )
        for sr in self.source_results:
            records.append(
                OutputRecord(
                    "source",
                    sr.source_id,
                    sr.cache_status,
                    sr.ref,
                )
            )
            for metric_name, metric_value in (
                ("materialized_files", sr.materialized_files),
                ("materialized_bytes", sr.materialized_bytes),
                ("cache_bytes_added", sr.cache_bytes_added),
                ("duration_ms", sr.duration_ms),
            ):
                records.append(
                    OutputRecord(
                        "metric",
                        f"{sr.source_id}.{metric_name}",
                        "ok",
                        str(metric_value),
                    )
                )
            records.append(
                OutputRecord(
                    "validation",
                    f"{sr.source_id}.fetch_strategy",
                    "ok",
                    sr.fetch_strategy,
                )
            )
        return tuple(records)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit, plan, or apply declared external resource refreshes."
    )
    parser.add_argument("mode", choices=("prepare", "audit", "plan", "apply"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--workspace")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--overrides", default=DEFAULT_OVERRIDES)
    parser.add_argument(
        "--source-root",
        help="Use prepared source checkouts instead of network fetch.",
    )
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--format", choices=("text", "tsv", "json"), default="text")
    parser.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Force rebuild of the Git object cache (prepare mode only).",
    )
    return parser


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise SyncCommandError(["git", *args], result.returncode, result.stderr)
    return result


def _materialize_managed_repo_snapshot(
    repo_root: Path, resources: ManagedResources, snapshot: Path
) -> None:
    snapshot.mkdir(parents=True, exist_ok=True)
    for asset in resources.assets:
        src = repo_root / asset.local
        dst = snapshot / asset.local
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


def _build_candidate_patch(
    repo_root: Path, candidate: Path, resources: ManagedResources
) -> str:
    with tempfile.TemporaryDirectory(prefix="sync-snapshot-") as raw_snapshot:
        snapshot = Path(raw_snapshot) / "snapshot"
        _materialize_managed_repo_snapshot(repo_root, resources, snapshot)
        diff_result = subprocess.run(
            [
                "git",
                "diff",
                "--no-index",
                "--binary",
                "--",
                str(snapshot),
                str(candidate),
            ],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    return _rewrite_patch_paths(
        diff_result.stdout, str(snapshot), str(candidate)
    )


def _rewrite_patch_paths(
    patch_text: str, snapshot_prefix: str, candidate_prefix: str
) -> str:
    prefixes = (
        "a" + snapshot_prefix,
        "b" + snapshot_prefix,
        "a" + candidate_prefix,
        "b" + candidate_prefix,
        snapshot_prefix,
        candidate_prefix,
    )

    def _to_relative(path: str) -> str:
        if path == "/dev/null":
            return path
        value = path.strip().strip('"')
        for prefix in prefixes:
            if value.startswith(prefix):
                return value[len(prefix) :].lstrip("/")
        if value.startswith("a/") or value.startswith("b/"):
            return value[2:].lstrip("/")
        return value.lstrip("/")

    lines = patch_text.splitlines(keepends=True)
    result: list[str] = []
    for line in lines:
        if line.startswith("diff --git "):
            parts = line.strip().split()
            if len(parts) >= 4:
                old_path = _to_relative(parts[2])
                new_path = _to_relative(parts[3])
                line = f"diff --git a/{old_path} b/{new_path}\n"
            result.append(line)
        elif line.startswith("--- "):
            path = line[4:].strip()
            relative = _to_relative(path)
            if relative == "/dev/null":
                result.append("--- /dev/null\n")
            else:
                result.append(f"--- a/{relative}\n")
        elif line.startswith("+++ "):
            path = line[4:].strip()
            relative = _to_relative(path)
            if relative == "/dev/null":
                result.append("+++ /dev/null\n")
            else:
                result.append(f"+++ b/{relative}\n")
        elif line.startswith("Binary files ") and " and " in line and " differ" in line:
            payload = line[len("Binary files ") :].rstrip("\n")
            left, right = payload.removesuffix(" differ").split(" and ", 1)
            left_rel = _to_relative(left)
            right_rel = _to_relative(right)
            if left_rel != "/dev/null":
                left_rel = f"a/{left_rel}"
            if right_rel != "/dev/null":
                right_rel = f"b/{right_rel}"
            result.append(f"Binary files {left_rel} and {right_rel} differ\n")
        else:
            result.append(line)
    return "".join(result)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _snapshot_managed_targets(
    repo_root: Path, resources: ManagedResources
) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for asset in resources.assets:
        target = repo_root / asset.local
        if target.is_file():
            snapshot[asset.local] = _sha256_file(target)
        elif target.is_dir():
            for file_path in sorted(target.rglob("*")):
                if file_path.is_file():
                    rel = file_path.relative_to(repo_root).as_posix()
                    snapshot[rel] = _sha256_file(file_path)
    return snapshot


def _apply_candidate_patch(
    repo_root: Path, patch_text: str, resources: ManagedResources
) -> bool:
    if not patch_text.strip():
        return False
    result = subprocess.run(
        ["git", "apply", "--check", "-"],
        cwd=repo_root,
        input=patch_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Patch check failed: {result.stderr[:500]}")
    before = _snapshot_managed_targets(repo_root, resources)
    subprocess.run(
        ["git", "apply", "-"],
        cwd=repo_root,
        input=patch_text,
        check=True,
        capture_output=True,
        text=True,
    )
    after = _snapshot_managed_targets(repo_root, resources)
    if before != after:
        return True
    raise ValueError(
        "Patch applied but no managed target files changed in the repository."
    )


def _prepare(
    repo_root: Path,
    workspace: Path,
    resources: ManagedResources,
    rebuild_cache: bool,
) -> SyncOutcome:
    validate_external_workspace(repo_root, workspace)
    sources_root = _resolve_sources_root(repo_root, None)

    results = prepare_sources(
        resources,
        workspace,
        sources_root,
        rebuild_cache=rebuild_cache,
    )

    return SyncOutcome(
        mode="prepare",
        workspace=str(workspace),
        managed_assets=len(resources.assets),
        changed_paths=(),
        override_results=(),
        validations=("manifest-pins-validated", "sources-prepared"),
        blockers=(),
        repository_changed=False,
        source_results=results,
        source_root=str(sources_root),
    )


def _audit(
    repo_root: Path,
    resources: ManagedResources,
    overrides_path: Path,
) -> SyncOutcome:
    blockers: list[str] = []
    dirty = find_dirty_targets(repo_root, resources.assets)
    if dirty:
        blockers.append(f"dirty managed targets: {', '.join(dirty)}")

    validations: list[str] = ["manifest-parsed"]
    if overrides_path.exists():
        overrides = load_overrides(overrides_path)
        validations.append("overrides-parsed")
        bundle_root = overrides_path.parent.parent
        try:
            validate_override_patches(overrides, bundle_root)
            validations.append("override-patches-exist")
        except ValueError as exc:
            blockers.append(str(exc))
    else:
        overrides = ()

    return SyncOutcome(
        mode="audit",
        workspace=None,
        managed_assets=len(resources.assets),
        changed_paths=(),
        override_results=(),
        validations=tuple(validations),
        blockers=tuple(blockers),
        repository_changed=False,
    )


def _resolve_sources_root(repo_root: Path, source_root: Path | None) -> Path:
    return (
        source_root
        if source_root is not None
        else repo_root / DEFAULT_SNAPSHOT_ROOT
    )


def _is_missing_prepared_sources_error(error: ValueError) -> bool:
    return str(error).startswith(
        ("Missing prepared source metadata:", "Missing upstream paths:")
    )


def _materialize_candidate_with_auto_prepare(
    resources: ManagedResources,
    workspace: Path,
    candidate: Path,
    sources_root: Path,
) -> tuple[PrepareSourceResult, ...]:
    try:
        materialize_candidate(
            resources, workspace, candidate, sources_root=sources_root
        )
    except ValueError as exc:
        if not _is_missing_prepared_sources_error(exc):
            raise
        source_results = prepare_sources(
            resources,
            workspace,
            sources_root,
        )
        materialize_candidate(
            resources, workspace, candidate, sources_root=sources_root
        )
        return tuple(source_results)
    return ()


def _plan(
    repo_root: Path,
    workspace: Path,
    resources: ManagedResources,
    overrides_path: Path,
    source_root: Path | None,
) -> SyncOutcome:
    validate_external_workspace(repo_root, workspace)

    sources_root = _resolve_sources_root(repo_root, source_root)
    candidate = workspace / "candidate"
    source_results = _materialize_candidate_with_auto_prepare(
        resources, workspace, candidate, sources_root
    )
    changed = normalize_candidate(resources, candidate)
    validations = (
        "prepared-sources-validated",
        "candidate-built",
        "normalized",
        "overrides-replayed",
    )
    if source_results:
        validations = ("sources-auto-prepared", *validations)

    override_results: tuple[OverrideResult, ...] = ()
    if overrides_path.exists():
        overrides = load_overrides(overrides_path)
        bundle_root = overrides_path.parent.parent
        validate_override_patches(overrides, bundle_root)
        override_results = replay_overrides(candidate, overrides, bundle_root)

    return SyncOutcome(
        mode="plan",
        workspace=str(workspace),
        managed_assets=len(resources.assets),
        changed_paths=tuple(changed),
        override_results=override_results,
        validations=validations,
        blockers=(),
        repository_changed=False,
        source_results=source_results,
        source_root=str(sources_root),
    )


def _apply(
    repo_root: Path,
    workspace: Path,
    resources: ManagedResources,
    overrides_path: Path,
    source_root: Path | None,
    allow_dirty: bool,
) -> SyncOutcome:
    validate_external_workspace(repo_root, workspace)
    sources_root = _resolve_sources_root(repo_root, source_root)

    dirty = find_dirty_targets(repo_root, resources.assets)
    if dirty and not allow_dirty:
        return SyncOutcome(
            mode="apply",
            workspace=str(workspace),
            managed_assets=len(resources.assets),
            changed_paths=(),
            override_results=(),
            validations=(),
            blockers=(f"dirty managed targets: {', '.join(dirty)}",),
            repository_changed=False,
            source_root=str(sources_root),
        )

    candidate = workspace / "candidate"
    source_results = _materialize_candidate_with_auto_prepare(
        resources, workspace, candidate, sources_root
    )
    changed = normalize_candidate(resources, candidate)
    validations = (
        "prepared-sources-validated",
        "candidate-built",
        "normalized",
        "overrides-replayed",
        "patch-applied",
    )
    if source_results:
        validations = ("sources-auto-prepared", *validations)

    override_results: tuple[OverrideResult, ...] = ()
    if overrides_path.exists():
        overrides = load_overrides(overrides_path)
        bundle_root = overrides_path.parent.parent
        validate_override_patches(overrides, bundle_root)
        override_results = replay_overrides(candidate, overrides, bundle_root)

    patch_text = _build_candidate_patch(repo_root, candidate, resources)
    repository_changed = _apply_candidate_patch(repo_root, patch_text, resources)

    return SyncOutcome(
        mode="apply",
        workspace=str(workspace),
        managed_assets=len(resources.assets),
        changed_paths=tuple(changed),
        override_results=override_results,
        validations=validations,
        blockers=(),
        repository_changed=repository_changed,
        source_results=source_results,
        source_root=str(sources_root),
    )


def _format_text(outcome: SyncOutcome) -> str:
    lines = [
        f"Mode: {outcome.mode}",
        f"Workspace: {outcome.workspace or 'n/a'}",
        f"Managed assets: {outcome.managed_assets}",
        f"Changed paths: {len(outcome.changed_paths)}",
        f"Override results: {len(outcome.override_results)}",
        f"Validations: {', '.join(outcome.validations) or 'none'}",
        f"Repository changed: {outcome.repository_changed}",
    ]
    if outcome.blockers:
        lines.append(f"Blockers: {'; '.join(outcome.blockers)}")
    return "\n".join(lines)


def _requested_format(argv: Sequence[str] | None) -> str:
    values = list(argv) if argv is not None else sys.argv[1:]
    for index, value in enumerate(values):
        if value == "--format" and index + 1 < len(values):
            return values[index + 1]
        if value.startswith("--format="):
            return value.split("=", 1)[1]
    return "text"


def _emit_failure(fmt: str, message: str) -> None:
    if fmt == "json":
        print(json.dumps({"blockers": [message], "repository_changed": False}, indent=2))
    elif fmt == "tsv":
        print(render_tsv((OutputRecord("blocker", message, "fail", ""),)), end="")
    else:
        print(f"Blockers: {message}")


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    overrides_path = Path(args.overrides)
    if not overrides_path.is_absolute():
        overrides_path = repo_root / overrides_path

    resources = load_managed_resources(manifest_path)

    if args.mode == "prepare":
        if not args.workspace:
            parser.error("prepare mode requires --workspace")
        outcome = _prepare(
            repo_root,
            Path(args.workspace).resolve(),
            resources,
            args.rebuild_cache,
        )
    elif args.mode == "audit":
        if args.rebuild_cache:
            parser.error("--rebuild-cache is only valid for prepare mode")
        outcome = _audit(repo_root, resources, overrides_path)
    elif args.mode == "plan":
        if not args.workspace:
            parser.error("plan mode requires --workspace")
        if args.rebuild_cache:
            parser.error("--rebuild-cache is only valid for prepare mode")
        outcome = _plan(
            repo_root,
            Path(args.workspace).resolve(),
            resources,
            overrides_path,
            Path(args.source_root).resolve() if args.source_root else None,
        )
    elif args.mode == "apply":
        if not args.workspace:
            parser.error("apply mode requires --workspace")
        if args.rebuild_cache:
            parser.error("--rebuild-cache is only valid for prepare mode")
        outcome = _apply(
            repo_root,
            Path(args.workspace).resolve(),
            resources,
            overrides_path,
            Path(args.source_root).resolve() if args.source_root else None,
            args.allow_dirty,
        )
    else:
        parser.error(f"unknown mode: {args.mode}")

    if args.format == "json":
        print(json.dumps(outcome.to_dict(), indent=2))
    elif args.format == "tsv":
        print(render_tsv(outcome.to_records()), end="")
    else:
        print(_format_text(outcome))

    if args.mode == "audit":
        return 0
    if args.mode == "prepare":
        return 0
    if outcome.blockers:
        return 2
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return run(argv)
    except (ValueError, SyncCommandError) as exc:
        _emit_failure(_requested_format(argv), str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
