from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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
