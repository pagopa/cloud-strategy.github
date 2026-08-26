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
upstream release. Release/tag values and `advertised_ref` are informational
and never replace `ref`. Commit dates and tag metadata are not tracked here;
read them from the manifest or the upstream commit.

## Modes

- `prepare` fetches pinned Git content into a repository-keyed partial-clone
  cache and exports manifest-declared paths into verified snapshots.
- `audit` validates registries, local paths, canonical names, hashes, watchlist
  shape, and dirty state. It does not fetch or write.
- `plan` requires an external workspace, prepares missing snapshots, builds and
  validates the complete candidate, and emits a changed-path summary.
- `apply` performs `plan`, prepares missing snapshots, rejects dirty targets
  unless `--allow-dirty`, generates and checks one patch, applies once, rebuilds
  inventory, and reruns scoped validation.

## Pinned Content Only

- The manifest full commit SHA is the sole accepted source identity.
- Only manifest-declared `upstream` paths are materialized.
- No tags, submodules, local branches, or remote-tracking branches.
- No `git pull`, argumentless `git fetch`, or `git remote update`.
- No package managers (`pip`, `uv`, `npm`, `brew`, `yarn`, `pnpm`) are allowed.

## Managed Skill Reference Normalization

- A source may set `rewrite_skill_references: true` to rewrite slash commands
  and backtick skill references from declared upstream basenames to declared
  `canonical_name` values.
- `skill_reference_aliases` are source-local and point only at declared
  canonical names.
- The `mattpocock-skills` source uses the `mattpocock-` prefix. Upstream
  `/grilling` is normalized to `grill-me` through a declared source
  replacement, not an alias.
- References to undeclared skills remain unchanged and are reported as
  unresolved dependencies.

## Managed Skill Frontmatter

- Normalize managed `SKILL.md` files for Codex and GitHub Copilot while
  preserving `/skill-name` references.
- Remove `disable-model-invocation` by default because it is not standard Codex
  skill metadata.
- Apply `invocation_policy` generically per asset. Its fields are
  `copilot.disable_model_invocation` and `codex.allow_implicit_invocation`;
  do not hardcode per-asset exceptions.
- `superpowers-brainstorming` is the declared exception: keep
  `disable-model-invocation: true` in `SKILL.md` and set
  `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
- After refresh, manually verify that no policy-managed skill is implicitly
  selected in either runtime.

## Executable Python Normalization

- A source may set `ensure_python_shebangs: true` to prepend
  `#!/usr/bin/env python3` to executable `.py` files without a shebang.
- The Anthropic source enables this normalization.
- Preserve existing shebangs, non-executable Python modules, and non-Python
  executables unchanged.

## Guided Question Contract

- Append a repository-owned contract to `superpowers-brainstorming` and
  `grill-me` whenever either canonical skill is managed, regardless of source.
- Require numbered bulk question blocks. Every question includes a brief
  `Recommendation`, `Why`, and `Default if accepted`.
- Explicitly override upstream one-question-at-a-time pacing. A single
  remaining blocker is a numbered one-item block.
- Use a marker-based idempotent append, never a context-sensitive replay patch.

## Wayfinder Critical Validation And Grilling Contracts

- Append two repository-owned contracts to `mattpocock-wayfinder`.
- Before artifact creation or update, `internal-gateway-critical-master` must
  challenge the analysis. Counter-validate every material critique against
  evidence and constraints, incorporate every supported instruction, and stop
  when a supported objection remains unresolved.
- One gate covers one analysis unit and its related content-producing write
  batch. The required ticket claim is exempt and remains the first coordination
  action. Rerun the critic only after new evidence or a materially supported
  revision; never against unchanged evidence.
- Every Wayfinder Grilling ticket and `grill-me` invocation asks numbered bulk
  blocks with `Question`, `Recommendation`, `Why`, and `Default if accepted`.
- Both contracts are canonical-name-scoped, marker-based, idempotent, and never
  replay patches.

## Repository-Owned Skill Contracts

- Express additive behavior, workspace, and output-path requirements as
  canonical-name-scoped, marker-based candidate normalizations.
- Each normalization replaces its own marked block, is idempotent, and
  preserves unrelated upstream content.
- Matt Pocock handoff output path and PRD-aware non-duplication wording are
  canonical marked normalizations, not replay-patch ownership.
- Reserve replay patches for irreducible upstream-line edits. Record why a
  normalization is insufficient before registering an exception.
- Register each approved in-place override in
  `references/imported-asset-overrides.yaml` with a replay patch and expected
  content hash.
- Replay runs clean `git apply --check` first, then `--3way --check` only when
  declared. Stop for review if neither applies.

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
- `summary.source_root` names the snapshot directory.
- `--format text` is the default; `--format json` retains backward-compatible
  keys.

## Safety

- Dirty managed targets block `apply` unless `--allow-dirty`.
- Override replay is atomic: any override verification failure means no
  candidate changes reach the repository.
- Do not modify repository targets until the complete candidate tree,
  normalizations, overrides, and generated patch pass validation.

## Workflow

1. Run `audit` to validate the manifest, overrides, and local dirty state.
2. Run `plan` with `--workspace` and confirm the candidate can be built.
3. Review the changed-path summary, metrics, and override replay results.
4. Run `apply` to produce and apply the validated repository patch.

## Canonical Commands

```bash
python3 scripts/sync_external_resources.py prepare --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 scripts/sync_external_resources.py audit --format tsv
python3 scripts/sync_external_resources.py plan --workspace ../cloud-strategy.github-external-refresh --format tsv
python3 scripts/sync_external_resources.py apply --workspace ../cloud-strategy.github-external-refresh --format tsv
```

## Live Network Benchmark (Separate Authorization Required)

The two largest sources are `github-awesome-copilot` (242 MiB) and
`sickn33-antigravity` (318 MiB). Require at least 90% reduction in
`materialized_bytes`; the second run must report `cached` with zero added cache
bytes. Do not alter manifest refs or repository targets, and never run without
separate authorization.

## Validation

- `python3 -m compileall scripts`
- `python3 -m pytest -q tests/github/skills/local-agent-sync-external-resources/scripts`
- `python3 .github/scripts/validate_internal_skills.py --skill local-agent-sync-external-resources --strict`
- `make inventory-build`
- `make token-risks`

## Output

Report: mode, workspace, source root when used, managed count, changed paths,
override results, source metrics, validation, and blockers.

## Anti-Scope

- Do not refresh or modify imported skills while implementing sync tooling.
- Do not add a plugin system, concurrency, compatibility aliases, legacy
  fallback paths, or a generic sync framework.
- Do not perform network refreshes outside the declared pinned prepare flow.
- The live benchmark requires separate authorization.
- Do not use mutable branch updates in any sync mode.
