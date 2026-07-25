---
name: local-agent-sync-external-resources
description: Audit, plan, or apply declared external resource refreshes through the staged sync CLI.
---

# Local Agent Sync External Resources

## Contract

This skill owns the manifest-driven CLI that stages, validates, and applies
declared external resource refreshes safely. The single public entrypoint is
`scripts/sync_external_resources.py`. Bundle siblings: `references/`,
`patches/`, `agents/openai.yaml`, `scripts/`.

## Modes

- `prepare`: the only mode that uses the network. Fetches pinned Git content
  into a repository-keyed partial-clone cache and exports only manifest-declared
  asset paths into verified snapshots under `sources/`. All other modes are
  offline and consume these verified snapshots.
- `audit`: parse all registries, validate local paths, canonical names, hashes,
  watchlist shape, and dirty state. Does not fetch or write.
- `plan`: require an external workspace, build and validate the complete
  candidate, then emit the changed-path summary without repository writes.
- `apply`: perform `plan`, reject dirty targets unless `--allow-dirty`,
  generate one patch, run `git apply --check`, apply once, rebuild inventory,
  and rerun scoped validation.

## Pinned Content Only

- The manifest full commit SHA is the sole accepted source identity.
- Only manifest-declared `upstream` paths are materialized.
- No tags, no submodules, no local branches, no remote-tracking branches.
- No `git pull`, no argumentless `git fetch`, no `git remote update`.
- No package managers: `pip`, `uv`, `npm`, `brew`, `yarn`, `pnpm` are forbidden.

## Managed Skill Reference Normalization

- A source may set `rewrite_skill_references: true` to rewrite slash commands and
  backtick skill references from each declared upstream asset basename to its
  declared `canonical_name` during candidate normalization.
- Use `skill_reference_aliases` for upstream command names that do not match an
  asset basename. Keep aliases source-local and point them only at declared
  canonical names.
- The `mattpocock-skills` source uses the `mattpocock-` canonical prefix for
  every imported skill. The upstream `/grilling` reference is normalized to
  the repository-owned `grill-me` through a declared source replacement,
  not through a source-local alias.
- References to undeclared skills remain unchanged and must be reported as
  unresolved dependencies; do not silently import or rewrite them.

## Workspace Convention

- The runtime workspace must be outside this repository.
- Use an external workspace such as `../cloud-strategy.github-external-refresh`.
- Keep prepared source snapshots under the workspace `sources/` directory,
  unless an explicit `--source-root` is supplied.
- The Git object cache lives under `<workspace>/cache/repositories/`.

## Prepare Cold and Warm Flow

- Cold `prepare` fetches each declared source SHA into the partial-clone cache,
  verifies the commit object, and exports only declared upstream paths into
  atomic snapshots under `<workspace>/sources/<source_id>/`.
- Warm `prepare` finds the pin ref already cached and performs no fetch,
  reporting `cached` status and zero added cache bytes.
- `--rebuild-cache` forces a fresh cache rebuild beside the active one,
  replacing it only after verification. The rebuild reports `cache_status`
  `rebuilt` only after the fresh cache replaces the active one.

## TSV Output

- `--format tsv` emits escaped, deterministic, lexically sorted records.
- Header: `record\tkey\tstatus\tvalue`.
- Record types: `summary`, `source`, `metric`, `change`, `override`,
  `validation`, `blocker`.
- `metric` and per-source `validation` rows use `key` `<source_id>.<name>`,
  `status` `ok` or `fail`, and the measured value in `value`.
- `--format text` remains the default for operators.
- `--format json` retains backward-compatible keys.

## Safety

- Workspace must be outside the repository.
- Dirty managed targets block `apply` unless `--allow-dirty` is supplied.
- Override replay is atomic: if any override fails verification, no candidate
  changes reach the repository.
- Do not modify repository targets until the complete candidate tree,
  normalizations, overrides, and generated patch pass validation.

## Workflow

1. Run `prepare` to fetch pinned content into verified snapshots.
2. Run `audit` to validate the manifest, overrides, and local dirty-state.
3. Run `plan` with `--workspace` to confirm the candidate can be built.
4. Review the changed-path summary and override replay results.
5. Run `apply` only after `plan` succeeds; `apply` does not fetch sources.

If `plan` or `apply` reports `Missing prepared source metadata`, run `prepare`
first.

## Canonical Commands

```bash
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py prepare --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py audit --format tsv
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py plan --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 .github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py apply --workspace ../cloud-strategy.github-external-refresh --format tsv
```

## Live Network Benchmark (Separate Authorization Required)

Run `prepare` (see `## Canonical Commands`) against the two largest sources
(`github-awesome-copilot` and `sickn33-antigravity`) with 242 MiB and 318 MiB
baselines. Require at least 90% reduction in `materialized_bytes`. Run again
and require `cached` with zero added cache bytes. The command must not alter
manifest refs or repository targets. Do not run without separate authorization.

## Override Rules

- Every approved imported in-place override must be registered in
  `references/imported-asset-overrides.yaml` with a replay patch and expected
  content hash.
- Replay uses clean `git apply --check` first, then `--3way --check` only when
  declared.
- Stop for review if neither path applies cleanly.

## Validation

- `python3 -m compileall .github/skills/local-agent-sync-external-resources/scripts`
- `python3 -m pytest -q tests/github/skills/local-agent-sync-external-resources/scripts`
- `python3 .github/scripts/validate_internal_skills.py --skill local-agent-sync-external-resources --strict`
- `make inventory-build`
- `make token-risks`

## Output

Report: mode, workspace, source root when used, managed count, changed paths,
override results, source metrics, validation, and blockers.

## Anti-Scope

- Do not refresh or modify any imported skill while implementing sync tooling.
- Do not add a plugin system, concurrency, compatibility aliases, legacy
  fallback paths, or a generic sync framework.
- Do not perform a live network refresh unless the user separately authorizes it.
- Do not use package managers or mutable branch updates in any sync mode.
