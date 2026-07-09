from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml


@dataclass(frozen=True)
class ManagedAsset:
    source: str
    upstream: str
    local: str
    canonical_name: str


@dataclass(frozen=True)
class ManagedSource:
    source_id: str
    repository: str
    ref: str
    assets: tuple[ManagedAsset, ...]


@dataclass(frozen=True)
class TextReplacement:
    source: str
    old: str
    new: str


@dataclass(frozen=True)
class WatchItem:
    source_family: str
    upstream_id: str
    local_owner: str
    reason: str


@dataclass(frozen=True)
class ManagedResources:
    sources: tuple[ManagedSource, ...]
    replacements: tuple[TextReplacement, ...]
    watchlist: tuple[WatchItem, ...]

    @property
    def assets(self) -> tuple[ManagedAsset, ...]:
        return tuple(asset for source in self.sources for asset in source.assets)


def _require_non_empty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    return value.strip()


def load_managed_resources(path: Path) -> ManagedResources:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Managed resources must be a version 1 YAML mapping.")

    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, dict) or not raw_sources:
        raise ValueError("Managed resources must declare a non-empty sources mapping.")

    raw_normalizations = payload.get("normalizations")
    if raw_normalizations is not None and not isinstance(raw_normalizations, list):
        raise ValueError("normalizations must be a list.")

    raw_watchlist = payload.get("watchlist")
    if not isinstance(raw_watchlist, list):
        raise ValueError("watchlist must be a list.")

    seen_local_paths: set[str] = set()
    seen_canonical_names: set[str] = set()
    sources: list[ManagedSource] = []

    for source_id, raw_source in raw_sources.items():
        source_id = _require_non_empty_string(source_id, "source id")
        if not isinstance(raw_source, dict):
            raise ValueError(f"Source {source_id} must be a mapping.")

        repository = _require_non_empty_string(
            raw_source.get("repository"), f"source {source_id} repository"
        )
        ref = _require_non_empty_string(
            raw_source.get("ref"), f"source {source_id} ref"
        )
        raw_assets = raw_source.get("assets")
        if not isinstance(raw_assets, list) or not raw_assets:
            raise ValueError(
                f"Source {source_id} must declare a non-empty assets list."
            )

        assets: list[ManagedAsset] = []
        for raw_asset in raw_assets:
            if not isinstance(raw_asset, dict):
                raise ValueError(
                    f"Each asset in source {source_id} must be a mapping."
                )
            upstream = _require_non_empty_string(
                raw_asset.get("upstream"),
                f"asset upstream in source {source_id}",
            )
            local = _require_non_empty_string(
                raw_asset.get("local"),
                f"asset local in source {source_id}",
            )
            canonical_name = _require_non_empty_string(
                raw_asset.get("canonical_name"),
                f"asset canonical_name in source {source_id}",
            )

            if local in seen_local_paths:
                raise ValueError(f"duplicate local path: {local}")
            seen_local_paths.add(local)

            if canonical_name in seen_canonical_names:
                raise ValueError(f"duplicate canonical name: {canonical_name}")
            seen_canonical_names.add(canonical_name)

            assets.append(
                ManagedAsset(
                    source=source_id,
                    upstream=upstream,
                    local=local,
                    canonical_name=canonical_name,
                )
            )

        sources.append(
            ManagedSource(
                source_id=source_id,
                repository=repository,
                ref=ref,
                assets=tuple(assets),
            )
        )

    replacements: list[TextReplacement] = []
    if raw_normalizations:
        for raw_norm in raw_normalizations:
            if not isinstance(raw_norm, dict):
                raise ValueError("Each normalization must be a mapping.")
            norm_source = _require_non_empty_string(
                raw_norm.get("source"), "normalization source"
            )
            if norm_source not in {s.source_id for s in sources}:
                raise ValueError(
                    f"normalization source {norm_source} is not a declared source"
                )
            old = _require_non_empty_string(
                raw_norm.get("from"), "normalization from"
            )
            new = _require_non_empty_string(
                raw_norm.get("to"), "normalization to"
            )
            replacements.append(
                TextReplacement(source=norm_source, old=old, new=new)
            )

    watchlist: list[WatchItem] = []
    for raw_item in raw_watchlist:
        if not isinstance(raw_item, dict):
            raise ValueError("Each watchlist item must be a mapping.")
        source_family = _require_non_empty_string(
            raw_item.get("source_family"), "watchlist source_family"
        )
        upstream_id = _require_non_empty_string(
            raw_item.get("upstream_id"), "watchlist upstream_id"
        )
        local_owner = _require_non_empty_string(
            raw_item.get("local_owner"), "watchlist local_owner"
        )
        reason = _require_non_empty_string(
            raw_item.get("reason"), "watchlist reason"
        )
        watchlist.append(
            WatchItem(
                source_family=source_family,
                upstream_id=upstream_id,
                local_owner=local_owner,
                reason=reason,
            )
        )

    return ManagedResources(
        sources=tuple(sources),
        replacements=tuple(replacements),
        watchlist=tuple(watchlist),
    )


class SyncCommandError(Exception):
    def __init__(self, command: list[str], exit_code: int, stderr: str) -> None:
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(
            f"Command {command!r} exited {exit_code}: {stderr.strip()[:500]}"
        )


def _run_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise SyncCommandError(command, result.returncode, result.stderr)
    return result


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return _run_command(["git", *args], cwd=repo_root)


def validate_external_workspace(repo_root: Path, workspace: Path) -> None:
    repo = repo_root.resolve()
    external = workspace.resolve()
    if external == repo or external.is_relative_to(repo):
        raise ValueError(
            f"External refresh workspace must be outside the repository: {workspace}"
        )


def find_dirty_targets(
    repo_root: Path,
    assets: tuple[ManagedAsset, ...],
) -> tuple[str, ...]:
    if not assets:
        return ()
    result = _run_git(
        repo_root,
        ["status", "--porcelain=v1", "--", *(asset.local for asset in assets)],
    )
    return tuple(
        line[3:]
        for line in result.stdout.splitlines()
        if len(line) > 3
    )


def materialize_candidate(
    resources: ManagedResources,
    workspace: Path,
    candidate: Path,
) -> None:
    if candidate.exists():
        shutil.rmtree(candidate)
    candidate.mkdir(parents=True)

    for source in resources.sources:
        source_root = workspace / "sources" / source.source_id
        for asset in source.assets:
            upstream_path = source_root / asset.upstream
            if not upstream_path.exists():
                raise ValueError(
                    f"Missing upstream path: {asset.upstream} in source {source.source_id}"
                )
            target_path = candidate / asset.local
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if upstream_path.is_dir():
                shutil.copytree(upstream_path, target_path)
            else:
                shutil.copy2(upstream_path, target_path)


_FRONTMATTER_NAME_RE = re.compile(r"^(name\s*:\s*).*$", re.MULTILINE)


def normalize_candidate(
    resources: ManagedResources,
    candidate: Path,
) -> tuple[str, ...]:
    replacements_by_source: dict[str, list[TextReplacement]] = {}
    for replacement in resources.replacements:
        replacements_by_source.setdefault(replacement.source, []).append(replacement)

    changed: list[str] = []
    for asset in resources.assets:
        asset_dir = candidate / asset.local
        if not asset_dir.exists():
            continue
        for file_path in sorted(asset_dir.rglob("*")):
            if not file_path.is_file():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                continue

            original = content
            if file_path.suffix in {".md", ".yaml", ".yml"}:
                content = _FRONTMATTER_NAME_RE.sub(
                    rf"\g<1>{asset.canonical_name}", content, count=1
                )

            for replacement in replacements_by_source.get(asset.source, []):
                content = content.replace(replacement.old, replacement.new)

            if content != original:
                file_path.write_text(content, encoding="utf-8")
                changed.append(file_path.relative_to(candidate).as_posix())

    return tuple(sorted(changed))


@dataclass(frozen=True)
class ImportedOverride:
    override_id: str
    target_path: str
    patch_path: str
    apply_strategy: str
    expected_content_hash: str


@dataclass(frozen=True)
class OverrideResult:
    override_id: str
    status: Literal["applied", "already-applied"]
    target_path: str


def load_overrides(path: Path) -> tuple[ImportedOverride, ...]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Override registry must be a version 1 YAML mapping.")

    raw_overrides = payload.get("overrides")
    if not isinstance(raw_overrides, list):
        raise ValueError("Override registry must declare an overrides list.")

    overrides: list[ImportedOverride] = []
    for entry in raw_overrides:
        if not isinstance(entry, dict):
            raise ValueError("Each override entry must be a mapping.")
        overrides.append(
            ImportedOverride(
                override_id=_require_non_empty_string(
                    entry.get("id"), "override id"
                ),
                target_path=_require_non_empty_string(
                    entry.get("target_path"), "override target_path"
                ),
                patch_path=_require_non_empty_string(
                    entry.get("patch_path"), "override patch_path"
                ),
                apply_strategy=_require_non_empty_string(
                    entry.get("apply_strategy"), "override apply_strategy"
                ),
                expected_content_hash=_require_non_empty_string(
                    entry.get("expected_content_hash"),
                    "override expected_content_hash",
                ),
            )
        )
    return tuple(overrides)


def select_overrides(
    overrides: tuple[ImportedOverride, ...],
    requested_ids: tuple[str, ...],
) -> tuple[ImportedOverride, ...]:
    by_id = {o.override_id: o for o in overrides}
    selected: list[ImportedOverride] = []
    for rid in requested_ids:
        if rid not in by_id:
            raise ValueError(f"unknown override id: {rid}")
        selected.append(by_id[rid])
    return tuple(selected)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_override_hash(
    candidate_repo: Path, override: ImportedOverride
) -> None:
    target = candidate_repo / override.target_path
    if not target.exists():
        raise ValueError(
            f"Override target missing on disk: {override.target_path}"
        )
    actual = _sha256_file(target)
    if actual != override.expected_content_hash:
        raise ValueError(
            f"content hash mismatch for {override.target_path}: "
            f"expected {override.expected_content_hash}, got {actual}"
        )


def _replay_one_override(
    trial_repo: Path,
    override: ImportedOverride,
    patches_root: Path,
) -> OverrideResult:
    patch_file = patches_root / override.patch_path
    if not patch_file.exists():
        raise ValueError(f"Override patch missing: {override.patch_path}")

    patch_text = patch_file.read_text(encoding="utf-8")
    target = trial_repo / override.target_path
    before_content = target.read_text(encoding="utf-8") if target.exists() else ""

    check_result = subprocess.run(
        ["git", "apply", "--check", "--", str(patch_file)],
        cwd=trial_repo,
        capture_output=True,
        text=True,
        check=False,
    )

    if check_result.returncode == 0:
        _run_command(["git", "apply", "--", str(patch_file)], cwd=trial_repo)
        after_content = target.read_text(encoding="utf-8")
        if after_content == before_content:
            return OverrideResult(
                override_id=override.override_id,
                status="already-applied",
                target_path=override.target_path,
            )
        return OverrideResult(
            override_id=override.override_id,
            status="applied",
            target_path=override.target_path,
        )

    if override.apply_strategy == "git-apply-3way":
        check_3way = subprocess.run(
            ["git", "apply", "--3way", "--check", "--", str(patch_file)],
            cwd=trial_repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if check_3way.returncode == 0:
            _run_command(
                ["git", "apply", "--3way", "--", str(patch_file)],
                cwd=trial_repo,
            )
            return OverrideResult(
                override_id=override.override_id,
                status="applied",
                target_path=override.target_path,
            )

    raise ValueError(
        f"Override {override.override_id} patch does not apply cleanly"
    )


def _replace_tree_contents(dest: Path, source: Path) -> None:
    for item in dest.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in source.iterdir():
        if item.name == ".git":
            continue
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def replay_overrides(
    candidate_repo: Path,
    overrides: tuple[ImportedOverride, ...],
    patches_root: Path | None = None,
) -> tuple[OverrideResult, ...]:
    if patches_root is None:
        patches_root = candidate_repo
    with tempfile.TemporaryDirectory(prefix="external-override-") as raw_trial:
        trial = Path(raw_trial) / "candidate"
        shutil.copytree(candidate_repo, trial)
        results: list[OverrideResult] = []
        for item in overrides:
            result = _replay_one_override(trial, item, patches_root)
            results.append(result)
        for item in overrides:
            verify_override_hash(trial, item)
        _replace_tree_contents(candidate_repo, trial)
        return tuple(results)
