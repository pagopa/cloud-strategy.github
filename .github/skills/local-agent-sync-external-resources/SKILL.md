---
name: local-agent-sync-external-resources
description: Use when preparing, auditing, planning, or applying declared external resource refreshes through the staged, manifest-driven sync CLI.
---

# Local Agent Sync External Resources

## Contract

This skill owns the manifest-driven CLI that stages, validates, and applies
declared external resource refreshes safely. The single public entrypoint is
`scripts/sync_external_resources.py`. Bundle siblings are `references/`,
`patches/`, `agents/openai.yaml`, and `scripts/`.

## Managed Source Inventory

The canonical source of truth is
[`references/managed-resources.yaml`](references/managed-resources.yaml).
The `ref` field is the full commit object ID and the sole accepted source
identity. Top-level `version: 1` is the manifest schema version, not an
upstream release. Release/tag values (`advertised_ref`) are informational and
never replace `ref`.

- The comment table between the `managed-sources-summary:start` and `:end`
  markers is the per-source readability index: source, repository, pinned
  short SHA, tag when declared, commit date, and imported skill count. A test
  verifies that the table always matches the parsed sources.
- `commit_date` records the committer date of the pinned commit in
  `YYYY-MM-DD` form. The date is a property of the frozen SHA, so it never
  drifts; record it when pinning a new ref. `prepare` verifies it against the
  cached commit, and `plan`/`apply` re-verify against the local cache when it
  exists. A mismatch is a blocker that names the fix: update `commit_date` in
  the manifest or re-pin the ref.

## Modes

- `prepare` fetches pinned Git content into a repository-keyed partial-clone
  cache and exports manifest-declared paths into verified snapshots.
- `audit` validates registries, local paths, canonical names, hashes, watchlist
  shape, and dirty state. It is offline and does not fetch or write.
- `plan` requires an external workspace, prepares missing snapshots, builds and
  validates the complete candidate, and emits a changed-path summary.
- `apply` performs `plan`, prepares missing snapshots, rejects dirty targets
  unless `--allow-dirty`, generates and checks one patch, applies once, rebuilds
  inventory, and reruns scoped validation.
- `--source <source-id>` limits any mode to one declared source and may be
  repeated. Unknown IDs fail before execution. Plan and apply validate and
  replay only overrides whose target belongs to a selected asset. Omitting the
  option preserves the complete-catalog behavior.
- `audit --allow-dirty` suppresses only the dirty-target blocker while retaining
  manifest and override validation. `apply --allow-dirty` remains an explicit
  authorization to replace explained local target changes.

## Pinned Content Only

- The manifest full commit SHA is the sole accepted source identity.
- Only manifest-declared `upstream` paths are materialized.
- No tags, submodules, local branches, or remote-tracking branches.
- No `git pull`, argumentless `git fetch`, or `git remote update`.
- No package managers (`pip`, `uv`, `npm`, `brew`, `yarn`, `pnpm`) are allowed.

## Skill Normalizations

Imported-skill normalization policy (reference rewriting, invocation
frontmatter, Python shebangs, guided questions, and repository-owned skill
contracts) lives in
[`references/skill-normalizations.md`](references/skill-normalizations.md).
Reserve replay patches for irreducible upstream-line edits; register approved
in-place overrides in `references/imported-asset-overrides.yaml`.

## Workspace And Snapshot Flow

- Keep the runtime workspace outside this repository, such as
  `../cloud-strategy.github-external-refresh`.
- Keep the Git object cache under `<workspace>/cache/repositories/`.
- Keep prepared snapshots under
  `<repo-root>/tmp/.cache/external-sync-resources-snapshots/`. `--source-root`
  is an explicit operator or test override.
- Each snapshot contains `.external-resource-source.tsv` with exact fields
  `source_id`, `repository`, `ref`, `paths_sha256`.
- Before copying, `plan` and `apply` compare all four fields. A mismatch blocks
  candidate creation. `ref` is the full commit object ID; `paths_sha256` hashes
  sorted declared upstream path names only.
- `audit` does not consume snapshots.
- Cold `prepare` fetches the declared SHA into the partial-clone cache, verifies
  the commit object, and atomically exports only declared paths.
- Warm `prepare` reports `cached` with zero added bytes.
- `--rebuild-cache` builds beside the active cache and reports `rebuilt` only
  after verified replacement.
- Missing snapshots trigger pinned `prepare` automatically in `plan` and
  `apply`, limited to missing metadata or missing upstream paths. Invalid
  metadata or mismatched attestation remains a blocker.

## TSV Output

- `--format tsv` emits escaped, deterministic, lexically sorted records.
- Header: `record\tkey\tstatus\tvalue`.
- Record types: `summary`, `source`, `metric`, `change`, `override`,
  `validation`, `blocker`.
- Metric and per-source validation rows use key `<source_id>.<name>`, status
  `ok` or `fail`, and the value in `value`.
- Provenance metric rows, derived from the manifest in every mode, use keys
  `<source_id>.repository` (owner/repo form), `<source_id>.ref`,
  `<source_id>.commit_date`, `<source_id>.advertised_ref`, and
  `<source_id>.skills_count`; an undeclared tag or date is reported as `-`.
- `summary.source_root` names the snapshot directory.
- `--format text` is the default; `--format json` retains backward-compatible
  keys and adds a `source_provenance` list.

## Safety

- Dirty managed targets block `apply` unless `--allow-dirty`.
- Override replay is atomic: any override verification failure means no
  candidate changes reach the repository.
- Do not modify repository targets until the complete candidate tree,
  normalizations, overrides, and generated patch pass validation.

## Workflow

1. Run `audit` to validate the manifest, overrides, and local dirty state.
2. Run `plan` with `--workspace` and confirm the candidate can be built.
3. Review the changed-path summary, provenance rows, metrics, and override
   replay results.
4. Run `apply` to produce and apply the validated repository patch.

## Canonical Commands

```bash
python3 scripts/sync_external_resources.py prepare --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 scripts/sync_external_resources.py audit --format tsv
python3 scripts/sync_external_resources.py plan --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 scripts/sync_external_resources.py apply --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 scripts/sync_external_resources.py plan --source mattpocock-skills --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 scripts/sync_external_resources.py apply --source mattpocock-skills --workspace ../cloud-strategy.github-external-refresh --format tsv
```

## Live Network Benchmark (Separate Authorization Required)

The two largest sources are `github-awesome-copilot` (242 MiB) and
`sickn33-antigravity` (318 MiB). Require at least 90% reduction in
`materialized_bytes`; the second run must report `cached` with zero added cache
bytes. Do not alter manifest refs or repository targets, and never run without
separate authorization.

## Validation

- `python3 -m compileall scripts`
- `python3 -m pytest -q .github/skills/local-agent-sync-external-resources/tests/scripts`
- `./.github/tools/run.sh validate-internal-skills --skill local-agent-sync-external-resources --strict`
- `make inventory-build`
- `make token-risks`

## Output

Report: mode, workspace, source root when used, managed count, changed paths,
override results, provenance rows, source metrics, validation, and blockers.

## Anti-Scope

- Do not refresh or modify imported skills while implementing sync tooling.
- Do not add a plugin system, concurrency, compatibility aliases, legacy
  fallback paths, or a generic sync framework.
- Do not perform network refreshes outside the declared pinned prepare flow.
- The live benchmark requires separate authorization.
- Do not use mutable branch updates in any sync mode.
