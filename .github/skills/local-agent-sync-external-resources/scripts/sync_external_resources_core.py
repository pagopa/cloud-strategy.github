from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

_COMMIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_PREPARED_SOURCE_METADATA_NAME = ".external-resource-source.tsv"
_PREPARED_SOURCE_METADATA_FIELDS = (
    "source_id",
    "repository",
    "ref",
    "paths_sha256",
)


@dataclass(frozen=True)
class InvocationPolicy:
    copilot_disable_model_invocation: bool | None = None
    codex_allow_implicit_invocation: bool | None = None
    codex_short_description: str | None = None


@dataclass(frozen=True)
class ManagedAsset:
    source: str
    upstream: str
    local: str
    canonical_name: str
    invocation_policy: InvocationPolicy | None = None


@dataclass(frozen=True)
class ManagedSource:
    source_id: str
    repository: str
    ref: str
    advertised_ref: str | None
    assets: tuple[ManagedAsset, ...]
    rewrite_skill_references: bool = False
    ensure_python_shebangs: bool = False
    skill_reference_aliases: tuple[tuple[str, str], ...] = ()
    backtick_skill_references: tuple[str, ...] = ()


@dataclass(frozen=True)
class PreparedSourceMetadata:
    source_id: str
    repository: str
    ref: str
    paths_sha256: str


def compute_prepared_source_paths_sha256(source: ManagedSource) -> str:
    upstream_paths = sorted(asset.upstream for asset in source.assets)
    return hashlib.sha256(
        ",".join(upstream_paths).encode("utf-8")
    ).hexdigest()


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


def _optional_non_empty_string(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string when provided.")
    return value.strip()


_INVOCATION_POLICY_RUNTIME_FIELDS: dict[str, tuple[str, ...]] = {
    "copilot": ("disable_model_invocation",),
    "codex": ("allow_implicit_invocation", "short_description"),
}


def _parse_invocation_policy(value: object, field: str) -> InvocationPolicy | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"{field} invocation_policy must be a mapping.")
    unknown_runtimes = sorted(set(value) - set(_INVOCATION_POLICY_RUNTIME_FIELDS))
    if unknown_runtimes:
        raise ValueError(
            f"{field} invocation_policy declares unknown runtimes: "
            f"{', '.join(unknown_runtimes)}."
        )

    parsed: dict[str, bool | str | None] = {}
    for runtime, allowed_fields in _INVOCATION_POLICY_RUNTIME_FIELDS.items():
        raw_runtime = value.get(runtime)
        if raw_runtime is None:
            continue
        if not isinstance(raw_runtime, dict):
            raise ValueError(
                f"{field} invocation_policy {runtime} must be a mapping."
            )
        unknown_fields = sorted(set(raw_runtime) - set(allowed_fields))
        if unknown_fields:
            raise ValueError(
                f"{field} invocation_policy {runtime} declares unknown fields: "
                f"{', '.join(unknown_fields)}."
            )
        for allowed_field in allowed_fields:
            raw_field = raw_runtime.get(allowed_field)
            if raw_field is None:
                continue
            if allowed_field == "short_description":
                if not isinstance(raw_field, str) or not raw_field.strip():
                    raise ValueError(
                        f"{field} invocation_policy {runtime}.{allowed_field} "
                        "must be a non-empty string."
                    )
                parsed[f"{runtime}_{allowed_field}"] = raw_field.strip()
                continue
            if not isinstance(raw_field, bool):
                raise ValueError(
                    f"{field} invocation_policy {runtime}.{allowed_field} "
                    "must be a boolean."
                )
            parsed[f"{runtime}_{allowed_field}"] = raw_field

    return InvocationPolicy(
        copilot_disable_model_invocation=parsed.get(
            "copilot_disable_model_invocation"
        ),
        codex_allow_implicit_invocation=parsed.get(
            "codex_allow_implicit_invocation"
        ),
        codex_short_description=parsed.get("codex_short_description"),
    )


def _require_commit_object_id(value: str, field: str) -> str:
    stripped = value.strip()
    if not _COMMIT_OBJECT_ID_RE.match(stripped):
        raise ValueError(
            f"{field} must be a full lowercase commit object ID, got {stripped!r}."
        )
    return stripped


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
        ref = _require_commit_object_id(
            _require_non_empty_string(
                raw_source.get("ref"), f"source {source_id} ref"
            ),
            f"source {source_id} ref",
        )
        advertised_ref = _optional_non_empty_string(
            raw_source.get("advertised_ref"),
            f"source {source_id} advertised_ref",
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

            invocation_policy = _parse_invocation_policy(
                raw_asset.get("invocation_policy"),
                f"asset {canonical_name} in source {source_id}",
            )

            assets.append(
                ManagedAsset(
                    source=source_id,
                    upstream=upstream,
                    local=local,
                    canonical_name=canonical_name,
                    invocation_policy=invocation_policy,
                )
            )

        rewrite_skill_references = raw_source.get("rewrite_skill_references", False)
        if not isinstance(rewrite_skill_references, bool):
            raise ValueError(
                f"source {source_id} rewrite_skill_references must be a boolean."
            )
        ensure_python_shebangs = raw_source.get("ensure_python_shebangs", False)
        if not isinstance(ensure_python_shebangs, bool):
            raise ValueError(
                f"source {source_id} ensure_python_shebangs must be a boolean."
            )
        raw_skill_reference_aliases = raw_source.get("skill_reference_aliases", {})
        if not isinstance(raw_skill_reference_aliases, dict):
            raise ValueError(
                f"source {source_id} skill_reference_aliases must be a mapping."
            )
        canonical_names = {asset.canonical_name for asset in assets}
        skill_reference_aliases: list[tuple[str, str]] = []
        for alias, canonical_name in raw_skill_reference_aliases.items():
            alias = _require_non_empty_string(
                alias, f"source {source_id} skill reference alias"
            )
            canonical_name = _require_non_empty_string(
                canonical_name,
                f"source {source_id} skill reference alias target",
            )
            if canonical_name not in canonical_names:
                raise ValueError(
                    f"source {source_id} skill reference alias target "
                    f"{canonical_name} is not a declared asset canonical name."
                )
            skill_reference_aliases.append((alias, canonical_name))

        raw_backtick_refs = raw_source.get("backtick_skill_references", [])
        if not isinstance(raw_backtick_refs, list):
            raise ValueError(
                f"source {source_id} backtick_skill_references must be a list."
            )
        upstream_basenames = {Path(asset.upstream).name for asset in assets}
        alias_names = {alias for alias, _ in skill_reference_aliases}
        backtick_skill_references: list[str] = []
        for raw_backtick_ref in raw_backtick_refs:
            backtick_ref = _require_non_empty_string(
                raw_backtick_ref, f"source {source_id} backtick skill reference"
            )
            if backtick_ref not in upstream_basenames and backtick_ref not in alias_names:
                raise ValueError(
                    f"source {source_id} backtick skill reference {backtick_ref} "
                    "is not a declared upstream asset basename or alias."
                )
            backtick_skill_references.append(backtick_ref)

        sources.append(
            ManagedSource(
                source_id=source_id,
                repository=repository,
                ref=ref,
                advertised_ref=advertised_ref,
                assets=tuple(assets),
                rewrite_skill_references=rewrite_skill_references,
                ensure_python_shebangs=ensure_python_shebangs,
                skill_reference_aliases=tuple(skill_reference_aliases),
                backtick_skill_references=tuple(backtick_skill_references),
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


LOCAL_COMMAND_TIMEOUT_SECONDS = 60


def _run_command(
    command: list[str],
    cwd: Path | None = None,
    timeout: int = LOCAL_COMMAND_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
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
        ["status", "--porcelain=v1", "-z", "--", *(asset.local for asset in assets)],
    )
    fields = [field for field in result.stdout.split("\0") if field]
    dirty: list[str] = []
    index = 0
    while index < len(fields):
        entry = fields[index]
        status_code = entry[:2]
        dirty.append(entry[3:])
        if status_code[0] in {"R", "C"}:
            index += 1
        index += 1
    return tuple(dirty)


def collect_missing_upstream_paths(
    resources: ManagedResources,
    sources_root: Path,
) -> tuple[str, ...]:
    missing: list[str] = []
    for source in resources.sources:
        source_dir = sources_root / source.source_id
        for asset in source.assets:
            upstream_path = source_dir / asset.upstream
            if not upstream_path.exists():
                missing.append(f"{source.source_id}:{asset.upstream}")
    return tuple(missing)


def validate_prepared_sources(
    resources: ManagedResources,
    sources_root: Path,
) -> None:
    missing: list[str] = []
    for source in resources.sources:
        metadata_path = (
            sources_root / source.source_id / _PREPARED_SOURCE_METADATA_NAME
        )
        if not metadata_path.exists():
            missing.append(source.source_id)
            continue
        _validate_prepared_source(source, metadata_path)
    if missing:
        raise ValueError(
            "Missing prepared source metadata: "
            + ", ".join(missing)
            + ". Expected prepared sources under "
            + sources_root.as_posix()
            + ". Run prepare before plan/apply."
        )


def _read_prepared_source_metadata(
    metadata_path: Path,
) -> PreparedSourceMetadata:
    try:
        with metadata_path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if reader.fieldnames != list(_PREPARED_SOURCE_METADATA_FIELDS):
                raise ValueError(
                    f"Invalid prepared source metadata header in {metadata_path}"
                )
            rows = list(reader)
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Invalid prepared source metadata encoding in {metadata_path}"
        ) from exc

    if len(rows) != 1:
        raise ValueError(
            f"Invalid prepared source metadata row count in {metadata_path}"
        )

    row = rows[0]
    if None in row:
        raise ValueError(
            f"Invalid prepared source metadata column count in {metadata_path}"
        )
    values: dict[str, str] = {}
    for field in _PREPARED_SOURCE_METADATA_FIELDS:
        value = row.get(field)
        if value is None or not value:
            raise ValueError(
                f"Invalid prepared source metadata field {field} in {metadata_path}"
            )
        values[field] = value

    return PreparedSourceMetadata(
        source_id=values["source_id"],
        repository=values["repository"],
        ref=values["ref"],
        paths_sha256=values["paths_sha256"],
    )


def _validate_prepared_source(
    source: ManagedSource,
    metadata_path: Path,
) -> None:
    actual = _read_prepared_source_metadata(metadata_path)
    expected = PreparedSourceMetadata(
        source_id=source.source_id,
        repository=source.repository,
        ref=source.ref,
        paths_sha256=compute_prepared_source_paths_sha256(source),
    )
    mismatches = [
        f"{field} expected {getattr(expected, field)!r}, got {getattr(actual, field)!r}"
        for field in _PREPARED_SOURCE_METADATA_FIELDS
        if getattr(expected, field) != getattr(actual, field)
    ]
    if mismatches:
        raise ValueError(
            f"Prepared source metadata mismatch for {source.source_id}: "
            + "; ".join(mismatches)
        )


def materialize_candidate(
    resources: ManagedResources,
    workspace: Path,
    candidate: Path,
    sources_root: Path | None = None,
) -> None:
    if candidate.exists():
        shutil.rmtree(candidate)
    candidate.mkdir(parents=True)

    if sources_root is None:
        sources_root = workspace / "sources"

    validate_prepared_sources(resources, sources_root)

    missing = collect_missing_upstream_paths(resources, sources_root)
    if missing:
        details = "; ".join(missing)
        raise ValueError(
            "Missing upstream paths: "
            f"{details}. Expected prepared sources under {sources_root.as_posix()}. "
            "Prepare the missing source checkout under that root or pass --source-root."
        )

    for source in resources.sources:
        source_dir = sources_root / source.source_id
        for asset in source.assets:
            upstream_path = source_dir / asset.upstream
            target_path = candidate / asset.local
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if upstream_path.is_dir():
                shutil.copytree(upstream_path, target_path)
            else:
                shutil.copy2(upstream_path, target_path)


_FRONTMATTER_NAME_RE = re.compile(r"^(name\s*:\s*).*$", re.MULTILINE)
_SUPERPOWERS_SKILL_REF_RE = re.compile(r"\bsuperpowers:([a-z0-9][a-z0-9-]*)")
_SLASH_SKILL_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_-])/(?P<name>[a-z0-9][a-z0-9-]*)\b"
)
_BACKTICK_SKILL_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_-])`(?P<name>[a-z0-9][a-z0-9-]*)`"
)
_SKILL_FRONTMATTER_BLOCK_RE = re.compile(
    r"\A---\n(?P<frontmatter>.*?)\n---\n",
    re.DOTALL,
)
_SKILL_DISABLE_MODEL_INVOCATION_RE = re.compile(
    r"^disable-model-invocation\s*:\s*.*(?:\n|$)",
    re.MULTILINE,
)
_CODEX_METADATA_TEMPLATE = """\
interface:
  display_name: {display_name}
  short_description: {short_description}
policy:
  allow_implicit_invocation: {allow_implicit_invocation}
"""
_MATTPOCOCK_SOURCE = "mattpocock-skills"
_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_START = (
    "<!-- local-sync:mattpocock-git-autonomy:start -->"
)
_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_END = "<!-- local-sync:mattpocock-git-autonomy:end -->"
_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_GIT_AUTONOMY_CONTRACT = f"""\
{_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_START}
## Local Git-autonomy contract

- Keep completed changes in the working tree for user review.
- You may stage only changes owned by the current task when staging helps inspect the exact diff.
- Leave changes uncommitted and unpushed unless the current user explicitly requests the specific commit or push action.
- Keep pre-existing or unrelated user changes out of the index.
{_MATTPOCOCK_GIT_AUTONOMY_CONTRACT_END}"""
_MATTPOCOCK_LEGACY_PATHS = {
    ".scratch/": "tmp/.issues/",
    ".out-of-scope/": "tmp/.out-of-scope/",
    "tmp/handoff/": "tmp/.handoff/",
    "./tmp/teach/": "./tmp/.teach/",
    "./tmp/codebase-improve/": "./tmp/.codebase-improve/",
}
_MATTPOCOCK_WAYFINDER_SKILL = "mattpocock-wayfinder"
_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_START = (
    "<!-- local-sync:wayfinder-workspace:start -->"
)
_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_END = (
    "<!-- local-sync:wayfinder-workspace:end -->"
)
_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT = f"""\
{_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_START}
## Local Wayfinder workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Keep each Wayfinder analysis unit under `tmp/.wayfinder/<analysis-slug>/`.
- Keep its map at `tmp/.wayfinder/<analysis-slug>/map.md` and its child tickets
  under `tmp/.wayfinder/<analysis-slug>/issues/`.
- Keep analysis, research findings, prototypes, and supporting assets inside the
  same active Wayfinder workspace.
{_MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_END}"""
_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_START = (
    "<!-- local-sync:wayfinder-critical-validation:start -->"
)
_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_END = (
    "<!-- local-sync:wayfinder-critical-validation:end -->"
)
_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT = f"""\
{_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_START}
## Local critical-validation contract

Apply one critical-validation gate to one analysis unit. One analysis unit is a
charting batch, one claimed ticket's resolution batch, or a proposal batch for
a research or prototype artifact. The gate covers the entire batch of
content-producing writes derived from unchanged analysis; do not rerun it before
each artifact in that batch.

The required ticket claim remains the first coordination action and is exempt
from this gate because it reserves work without publishing analysis or decision
content.

1. Form the analysis and proposed decisions as internal working state.
2. Invoke `/internal-gateway-critical-master` once to challenge that analysis.
3. Counter-validate every material critique against the destination, repository
   evidence, explicit constraints, success criteria, and anti-scope. Do not
   accept an unsupported or conflicting instruction merely because the critic
   proposed it.
4. Update the analysis by following every supported instruction from the critic.
   Record rejected instructions and their evidence internally.
5. If a supported material objection remains unresolved, stop the artifact
   batch. Do not rerun the critic against unchanged evidence; first obtain new
   evidence or make a materially supported revision.
6. Run another critical challenge only when new evidence or that supported
   revision changes a material claim. Once supported objections are resolved or
   recorded as an explicit accepted risk, create the whole related artifact
   batch without another gate while the analysis remains unchanged.

Place the gate at these lifecycle boundaries:

- While charting, run it after naming the destination and mapping the frontier,
  immediately before creating the map and its ticket batch.
- While working a map, claim the ticket first. Run the gate after resolving the
  ticket in working state and before the resolution comment, closure,
  Decisions-so-far update, or newly surfaced ticket batch.
- Before producing a research or prototype artifact, challenge its proposal as
  one unit. Treat the resulting findings or human reaction as new evidence that
  requires a fresh gate only before a later decision-artifact batch.
{_MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_END}"""
_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_START = (
    "<!-- local-sync:wayfinder-grilling:start -->"
)
_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_END = (
    "<!-- local-sync:wayfinder-grilling:end -->"
)
_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT = f"""\
{_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_START}
## Local Wayfinder grilling contract

This contract applies to every Grilling ticket and every `/grill-me` or
upstream `/grilling` invocation made while charting or working a map. It
overrides any earlier one-question-at-a-time instruction.

- Ask all currently known questions together in one numbered bulk block,
  ordered by decision dependency.
- For every numbered question, include `Question`, `Recommendation`, `Why`, and
  `Default if accepted`.
- Make `Recommendation` the suggested answer and `Why` the concrete reason for
  that suggestion. Treat the default as accepted unless the user overrides it.
- Put newly discovered or unresolved follow-up questions together in another
  numbered bulk block. If only one blocking question remains, use a numbered
  one-item block.
{_MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_END}"""
_MATTPOCOCK_WAYFINDER_LEGACY_BRANCH_RE = re.compile(
    r"captur(?:e|ing)\s+(?:its\s+)?findings\s+on\s+a\s+throwaway\s+"
    r"`research/<name>`\s+branch",
    re.IGNORECASE,
)
_MATTPOCOCK_RESEARCH_SKILL = "mattpocock-research"
_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_START = (
    "<!-- local-sync:research-workspace:start -->"
)
_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_END = (
    "<!-- local-sync:research-workspace:end -->"
)
_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT = f"""\
{_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_START}
## Local research-workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Save the default one-file research output to `tmp/.research/YYYY-MM-DD-<slug>.md`.
- An explicit caller-owned output path may override this default.
{_MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_END}"""
_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_START = (
    "<!-- local-sync:research-delegation:start -->"
)
_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_END = (
    "<!-- local-sync:research-delegation:end -->"
)
_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT = f"""\
{_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_START}
## Local research-delegation contract

This repository-owned contract replaces the generic background-agent
instruction for research execution.

- Delegate every research run to the `internal-luna-executor` subagent.
- Give Luna a self-contained brief with the question, context, primary-source
  and citation requirements, output path, and validation expectations.
- Luna must research the question and write the single Markdown report directly
  to the requested path. The caller verifies the result and does not repeat the
  research or write a second report.
- Verify that the report exists, is non-empty, and includes source citations.
- If `internal-luna-executor` is unavailable or cannot complete the brief,
  report a blocker instead of switching to another agent.
- This contract applies only where the named agent is available. Other runtimes
  must report that the required executor is unsupported.
{_MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_END}"""
_MATTPOCOCK_RESEARCH_DESCRIPTION_START = (
    "# local-sync:research-description:start"
)
_MATTPOCOCK_RESEARCH_DESCRIPTION_END = "# local-sync:research-description:end"
_MATTPOCOCK_RESEARCH_DESCRIPTION_CONTRACT_RE = re.compile(
    r"(?ms)^[ \t]*"
    + re.escape(_MATTPOCOCK_RESEARCH_DESCRIPTION_START)
    + r".*?^[ \t]*"
    + re.escape(_MATTPOCOCK_RESEARCH_DESCRIPTION_END)
    + r"[ \t]*$"
)
_MATTPOCOCK_RESEARCH_DESCRIPTION_LINE_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)short_description:.*$"
)
_MATTPOCOCK_RESEARCH_DESCRIPTION = (
    "Research from high-trust sources via Luna"
)
_MATTPOCOCK_HANDOFF_SKILL = "mattpocock-handoff"
_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_START = (
    "<!-- local-sync:handoff-workspace:start -->"
)
_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_END = (
    "<!-- local-sync:handoff-workspace:end -->"
)
_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_RE = re.compile(
    re.escape(_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_START)
    + r".*?"
    + re.escape(_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_END),
    re.DOTALL,
)
_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT = f"""\
{_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_START}
## Local handoff-workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Save handoff documents under `tmp/.handoff/`.
- Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.
{_MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_END}"""
_GUIDED_QUESTION_SKILLS = frozenset({"superpowers-brainstorming", "grill-me"})
_GUIDED_QUESTION_CONTRACT_START = "<!-- local-sync:guided-questions:start -->"
_GUIDED_QUESTION_CONTRACT_END = "<!-- local-sync:guided-questions:end -->"
_GUIDED_QUESTION_CONTRACT_RE = re.compile(
    re.escape(_GUIDED_QUESTION_CONTRACT_START)
    + r".*?"
    + re.escape(_GUIDED_QUESTION_CONTRACT_END),
    re.DOTALL,
)
_GUIDED_QUESTION_CONTRACT = f"""\
{_GUIDED_QUESTION_CONTRACT_START}
## Local guided-question contract

This repository-owned contract overrides any earlier instruction to ask one question at a time.

- Ask all currently known questions in numbered bulk question blocks.
- Use `Question`, `Recommendation`, `Why`, and `Default if accepted` for every
  numbered question.
- Make `Recommendation` the suggested answer and `Why` its concrete rationale.
- Keep each question, recommendation, and reason brief, clear, and
  decision-ready.
- Put unresolved follow-ups in another numbered block. If only one blocking
  question remains, present it as a numbered one-item block.
{_GUIDED_QUESTION_CONTRACT_END}"""

_TEACH_WORKSPACE_SKILL = "mattpocock-teach"
_TEACH_WORKSPACE_CONTRACT_START = "<!-- local-sync:teach-workspace:start -->"
_TEACH_WORKSPACE_CONTRACT_END = "<!-- local-sync:teach-workspace:end -->"
_TEACH_WORKSPACE_CONTRACT_RE = re.compile(
    re.escape(_TEACH_WORKSPACE_CONTRACT_START)
    + r".*?"
    + re.escape(_TEACH_WORKSPACE_CONTRACT_END),
    re.DOTALL,
)
_TEACH_WORKSPACE_CONTRACT = f"""\
{_TEACH_WORKSPACE_CONTRACT_START}
## Local teaching-workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Create or reuse one self-contained workspace at
  `./tmp/.teach/<lesson-name>/`.
- Derive `<lesson-name>` from the learning goal as a stable dash-case slug.
  Reuse it when later sessions continue the same goal.
- Resolve every generated path against that workspace root. Keep all teaching
  state, lessons, references, learning records, and supporting assets inside it.
- Do not create teaching resources in the repository root or outside the active
  teaching workspace.
{_TEACH_WORKSPACE_CONTRACT_END}"""

_CODEBASE_IMPROVE_SKILL = "mattpocock-improve-codebase-architecture"
_CODEBASE_IMPROVE_FILES = frozenset({"SKILL.md", "HTML-REPORT.md"})
_CODEBASE_IMPROVE_CONTRACT_START = (
    "<!-- local-sync:codebase-improve-workspace:start -->"
)
_CODEBASE_IMPROVE_CONTRACT_END = "<!-- local-sync:codebase-improve-workspace:end -->"
_CODEBASE_IMPROVE_CONTRACT_RE = re.compile(
    re.escape(_CODEBASE_IMPROVE_CONTRACT_START)
    + r".*?"
    + re.escape(_CODEBASE_IMPROVE_CONTRACT_END),
    re.DOTALL,
)
_CODEBASE_IMPROVE_CONTRACT = f"""\
{_CODEBASE_IMPROVE_CONTRACT_START}
## Local codebase-improvement workspace contract

This repository-owned contract overrides earlier workspace and output-path
instructions.

- Create or reuse `./tmp/.codebase-improve/` as the parent workspace.
- Resolve every generated artifact against that workspace root. Keep reports,
    diagrams, analysis, working state, and supporting files inside it.
- Do not create codebase-improvement artifacts outside the active workspace.
{_CODEBASE_IMPROVE_CONTRACT_END}"""

def _enforce_marked_contract(
    content: str,
    contract_re: re.Pattern[str],
    contract: str,
) -> str:
    if contract_re.search(content):
        return contract_re.sub(contract, content, count=1)
    return content.rstrip() + "\n\n" + contract + "\n"


def _enforce_guided_question_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _GUIDED_QUESTION_CONTRACT_RE,
        _GUIDED_QUESTION_CONTRACT,
    )


def _normalize_mattpocock_legacy_paths(content: str) -> str:
    for legacy_path, canonical_path in _MATTPOCOCK_LEGACY_PATHS.items():
        legacy_pattern = re.compile(
            r"(?<!tmp/)" + re.escape(legacy_path)
        )
        content = legacy_pattern.sub(canonical_path, content)
    return content


def _normalize_mattpocock_wayfinder_legacy_instruction(content: str) -> str:
    return _MATTPOCOCK_WAYFINDER_LEGACY_BRANCH_RE.sub(
        "keeping findings in the caller-owned Wayfinder workspace",
        content,
    )


def _enforce_mattpocock_git_autonomy_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_GIT_AUTONOMY_CONTRACT_RE,
        _MATTPOCOCK_GIT_AUTONOMY_CONTRACT,
    )


def _enforce_mattpocock_wayfinder_workspace_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT_RE,
        _MATTPOCOCK_WAYFINDER_WORKSPACE_CONTRACT,
    )


def _enforce_mattpocock_wayfinder_critical_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT_RE,
        _MATTPOCOCK_WAYFINDER_CRITICAL_CONTRACT,
    )


def _enforce_mattpocock_wayfinder_grilling_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT_RE,
        _MATTPOCOCK_WAYFINDER_GRILLING_CONTRACT,
    )


def _enforce_mattpocock_research_workspace_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT_RE,
        _MATTPOCOCK_RESEARCH_WORKSPACE_CONTRACT,
    )


def _enforce_mattpocock_research_delegation_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT_RE,
        _MATTPOCOCK_RESEARCH_DELEGATION_CONTRACT,
    )


def _enforce_mattpocock_research_description(content: str) -> str:
    def replace_description(match: re.Match[str]) -> str:
        indent = match.groupdict().get("indent") or "  "
        return "\n".join(
            (
                f"{indent}{_MATTPOCOCK_RESEARCH_DESCRIPTION_START}",
                f'{indent}short_description: "{_MATTPOCOCK_RESEARCH_DESCRIPTION}"',
                f"{indent}{_MATTPOCOCK_RESEARCH_DESCRIPTION_END}",
            )
        )

    if _MATTPOCOCK_RESEARCH_DESCRIPTION_CONTRACT_RE.search(content):
        return _MATTPOCOCK_RESEARCH_DESCRIPTION_CONTRACT_RE.sub(
            replace_description, content, count=1
        )
    return _MATTPOCOCK_RESEARCH_DESCRIPTION_LINE_RE.sub(
        replace_description, content, count=1
    )


def _enforce_mattpocock_handoff_workspace_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT_RE,
        _MATTPOCOCK_HANDOFF_WORKSPACE_CONTRACT,
    )


def _enforce_teach_workspace_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _TEACH_WORKSPACE_CONTRACT_RE,
        _TEACH_WORKSPACE_CONTRACT,
    )


def _enforce_codebase_improve_workspace_contract(content: str) -> str:
    return _enforce_marked_contract(
        content,
        _CODEBASE_IMPROVE_CONTRACT_RE,
        _CODEBASE_IMPROVE_CONTRACT,
    )


def _codex_display_name(canonical_name: str) -> str:
    words = canonical_name.split("-")
    if words and words[0] in {"superpowers", "mattpocock"}:
        words = words[1:]
    return " ".join(word.capitalize() for word in words) or canonical_name


def _ensure_codex_invocation_metadata(
    content: str,
    asset: ManagedAsset,
    allow_implicit_invocation: bool,
    short_description: str | None = None,
) -> str:
    if not content.strip():
        return _CODEX_METADATA_TEMPLATE.format(
            display_name=_codex_display_name(asset.canonical_name),
            short_description=(
                short_description or _codex_display_name(asset.canonical_name)
            ),
            allow_implicit_invocation=str(allow_implicit_invocation).lower(),
        )

    parsed = yaml.safe_load(content)
    if not isinstance(parsed, dict):
        raise ValueError(
            f"{asset.canonical_name} agents/openai.yaml must be a mapping."
        )

    policy = parsed.get("policy")
    if not isinstance(policy, dict):
        policy = {}
    policy["allow_implicit_invocation"] = allow_implicit_invocation
    parsed["policy"] = policy
    return yaml.safe_dump(parsed, sort_keys=False)


def _ensure_copilot_disable_model_invocation(
    content: str,
    asset: ManagedAsset,
) -> str:
    match = _SKILL_FRONTMATTER_BLOCK_RE.match(content)
    if match is None:
        raise ValueError(
            f"{asset.canonical_name} SKILL.md must contain YAML frontmatter."
        )

    frontmatter = match.group("frontmatter")
    normalized_frontmatter, replacements = _SKILL_DISABLE_MODEL_INVOCATION_RE.subn(
        "disable-model-invocation: true\n",
        frontmatter,
        count=1,
    )
    if replacements == 0:
        normalized_frontmatter = (
            "disable-model-invocation: true\n" + frontmatter
        )
    return (
        content[: match.start("frontmatter")]
        + normalized_frontmatter
        + content[match.end("frontmatter") :]
    )


def normalize_candidate(
    resources: ManagedResources,
    candidate: Path,
) -> tuple[str, ...]:
    replacements_by_source: dict[str, list[TextReplacement]] = {}
    for replacement in resources.replacements:
        replacements_by_source.setdefault(replacement.source, []).append(replacement)

    changed: list[str] = []
    sources_by_id = {source.source_id: source for source in resources.sources}
    skill_references_by_source: dict[str, dict[str, str]] = {}
    backtick_references_by_source: dict[str, dict[str, str]] = {}
    for source in resources.sources:
        if not source.rewrite_skill_references:
            continue
        skill_references = {
            Path(asset.upstream).name: asset.canonical_name
            for asset in source.assets
        }
        skill_references.update(dict(source.skill_reference_aliases))
        skill_references_by_source[source.source_id] = skill_references
        declared_backticks = set(source.backtick_skill_references)
        backtick_references_by_source[source.source_id] = {
            name: canonical
            for name, canonical in skill_references.items()
            if name in declared_backticks
        }

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
            source = sources_by_id[asset.source]
            if (
                source.ensure_python_shebangs
                and file_path.suffix == ".py"
                and file_path.stat().st_mode & 0o111
                and not content.startswith("#!")
            ):
                content = "#!/usr/bin/env python3\n" + content

            if file_path.suffix in {".md", ".yaml", ".yml"}:
                content = _FRONTMATTER_NAME_RE.sub(
                    rf"\g<1>{asset.canonical_name}", content, count=1
                )
                if asset.source == "obra-superpowers":
                    content = _SUPERPOWERS_SKILL_REF_RE.sub(
                        r"superpowers-\1", content
                    )

                skill_references = skill_references_by_source.get(asset.source, {})
                if skill_references:
                    content = _SLASH_SKILL_REF_RE.sub(
                        lambda match: "/"
                        + skill_references.get(
                            match.group("name"), match.group("name")
                        ),
                        content,
                    )
                backtick_references = backtick_references_by_source.get(asset.source, {})
                if backtick_references:
                    content = _BACKTICK_SKILL_REF_RE.sub(
                        lambda match: "`"
                        + backtick_references.get(
                            match.group("name"), match.group("name")
                        )
                        + "`",
                        content,
                    )

            if asset.source == _MATTPOCOCK_SOURCE:
                content = _normalize_mattpocock_legacy_paths(content)
                if (
                    asset.canonical_name == _MATTPOCOCK_WAYFINDER_SKILL
                    and file_path == asset_dir / "SKILL.md"
                ):
                    content = _normalize_mattpocock_wayfinder_legacy_instruction(
                        content
                    )

            if (
                asset.canonical_name in _GUIDED_QUESTION_SKILLS
                and file_path == asset_dir / "SKILL.md"
            ):
                content = _enforce_guided_question_contract(content)
            if (
                asset.canonical_name == _TEACH_WORKSPACE_SKILL
                and file_path == asset_dir / "SKILL.md"
            ):
                content = _enforce_teach_workspace_contract(content)
            if (
                asset.canonical_name == _CODEBASE_IMPROVE_SKILL
                and file_path.name in _CODEBASE_IMPROVE_FILES
                and file_path.parent == asset_dir
            ):
                content = _enforce_codebase_improve_workspace_contract(content)
            if (
                asset.source == _MATTPOCOCK_SOURCE
                and asset.canonical_name == _MATTPOCOCK_WAYFINDER_SKILL
                and file_path == asset_dir / "SKILL.md"
            ):
                content = _enforce_mattpocock_wayfinder_workspace_contract(content)
                content = _enforce_mattpocock_wayfinder_critical_contract(content)
                content = _enforce_mattpocock_wayfinder_grilling_contract(content)
            if (
                asset.source == _MATTPOCOCK_SOURCE
                and asset.canonical_name == _MATTPOCOCK_RESEARCH_SKILL
                and file_path == asset_dir / "SKILL.md"
            ):
                content = _enforce_mattpocock_research_workspace_contract(content)
                content = _enforce_mattpocock_research_delegation_contract(content)
            if (
                asset.source == _MATTPOCOCK_SOURCE
                and asset.canonical_name == _MATTPOCOCK_RESEARCH_SKILL
                and file_path == asset_dir / "agents/openai.yaml"
            ):
                content = _enforce_mattpocock_research_description(content)
            if (
                asset.source == _MATTPOCOCK_SOURCE
                and asset.canonical_name == _MATTPOCOCK_HANDOFF_SKILL
                and file_path == asset_dir / "SKILL.md"
            ):
                content = _enforce_mattpocock_handoff_workspace_contract(content)
            if (
                asset.source == _MATTPOCOCK_SOURCE
                and file_path == asset_dir / "SKILL.md"
            ):
                content = _enforce_mattpocock_git_autonomy_contract(content)
            for replacement in replacements_by_source.get(asset.source, []):
                content = content.replace(replacement.old, replacement.new)

            if file_path == asset_dir / "SKILL.md":
                content = _SKILL_DISABLE_MODEL_INVOCATION_RE.sub(
                    "", content, count=1
                )
                if (
                    asset.invocation_policy is not None
                    and asset.invocation_policy.copilot_disable_model_invocation
                    is True
                ):
                    content = _ensure_copilot_disable_model_invocation(
                        content, asset
                    )

            if content != original:
                file_path.write_text(content, encoding="utf-8")
                changed.append(file_path.relative_to(candidate).as_posix())

        if (
            asset.invocation_policy is not None
            and asset.invocation_policy.codex_allow_implicit_invocation is not None
        ):
            metadata_path = asset_dir / "agents/openai.yaml"
            original_metadata = (
                metadata_path.read_text(encoding="utf-8")
                if metadata_path.exists()
                else ""
            )
            metadata = _ensure_codex_invocation_metadata(
                original_metadata,
                asset,
                asset.invocation_policy.codex_allow_implicit_invocation,
                asset.invocation_policy.codex_short_description,
            )
            if metadata != original_metadata:
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                metadata_path.write_text(metadata, encoding="utf-8")
                changed.append(metadata_path.relative_to(candidate).as_posix())

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


def _resolve_override_patch(bundle_root: Path, patch_path: str) -> Path:
    return bundle_root / patch_path


def validate_override_patches(
    overrides: tuple[ImportedOverride, ...],
    bundle_root: Path,
) -> None:
    missing: list[str] = []
    for override in overrides:
        resolved = _resolve_override_patch(bundle_root, override.patch_path)
        if not resolved.exists():
            missing.append(override.patch_path)
    if missing:
        raise ValueError(f"Override patch missing: {', '.join(missing)}")


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


def _content_hash(path: Path) -> str:
    raw_bytes = path.read_bytes()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        normalized_bytes = raw_bytes
    else:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized_lines = [line.rstrip() for line in normalized.split("\n")]
        while normalized_lines and normalized_lines[-1] == "":
            normalized_lines.pop()
        normalized_bytes = ("\n".join(normalized_lines) + "\n").encode("utf-8")
    return hashlib.sha256(normalized_bytes).hexdigest()


def verify_override_hash(
    candidate_repo: Path, override: ImportedOverride
) -> None:
    target = candidate_repo / override.target_path
    if not target.exists():
        raise ValueError(
            f"Override target missing on disk: {override.target_path}"
        )
    actual = _content_hash(target)
    if actual != override.expected_content_hash:
        raise ValueError(
            f"content hash mismatch for {override.target_path}: "
            f"expected {override.expected_content_hash}, got {actual}"
        )


def _init_trial_git_repo(trial: Path) -> None:
    _run_command(["git", "init"], cwd=trial)
    _run_command(["git", "config", "user.email", "test@test.com"], cwd=trial)
    _run_command(["git", "config", "user.name", "Test"], cwd=trial)
    _run_command(["git", "add", "-A"], cwd=trial)
    _run_command(
        ["git", "commit", "-m", "trial-baseline", "--allow-empty"],
        cwd=trial,
    )


def _replay_one_override(
    trial_repo: Path,
    override: ImportedOverride,
    patches_root: Path,
) -> OverrideResult:
    patch_file = _resolve_override_patch(patches_root, override.patch_path)
    if not patch_file.exists():
        raise ValueError(f"Override patch missing: {override.patch_path}")

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
        _init_trial_git_repo(trial)
        results: list[OverrideResult] = []
        for item in overrides:
            result = _replay_one_override(trial, item, patches_root)
            results.append(result)
        for item in overrides:
            verify_override_hash(trial, item)
        _replace_tree_contents(candidate_repo, trial)
        return tuple(results)
