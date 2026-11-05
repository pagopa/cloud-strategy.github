---
name: local-agent-sync-external-resources
description: Use when refreshing declared upstream resources into the repository through the pinned sync CLI, or auditing their manifest. Home installation belongs to local-agent-sync-install-ai-resources.
---

# Local Agent Sync External Resources

## Contract

This skill owns the manifest-driven CLI that stages, validates, and applies
declared external resource refreshes safely. The single public entrypoint is
`scripts/sync_external_resources.py`. Bundle siblings are `references/`,
`patches/`, `agents/openai.yaml`, and `scripts/`.

## Destination Before Mode

Resolve the destination before preparing sources or selecting a mutating mode.

- Repository: use this workflow for declared upstream imports into the
  repository.
- Home: route missing runtime links or installation under `~/.agents/skills/`
  to /local-agent-sync-install-ai-resources. A repository audit does not inspect
  the home projection.
- Unclear: ask whether the missing resource is in the repository or the home
  installation before fetching or writing. An explicit skill invocation alone
  does not answer that question.
- Authorization: routing does not authorize network access, home mutation,
  dirty-target replacement, or changes to the declared catalog.

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
- Network access happens only in the pinned `prepare` flow, including the
  automatic `prepare` inside `plan` and `apply`.
- No `git pull`, argumentless `git fetch`, `git remote update`, or other
  mutable branch updates in any mode.
- No package managers (`pip`, `uv`, `npm`, `brew`, `yarn`, `pnpm`) are allowed.

## Skill Normalizations

Imported-skill normalization policy (reference rewriting, invocation
frontmatter, Python shebangs, guided questions, and repository-owned skill
contracts) lives in
[`references/skill-normalizations.md`](references/skill-normalizations.md).
Do not create new Git replay patches for imported-skill customizations.
Append approved instruction overrides as one marked note at the end of each
affected `SKILL.md`, explicitly overriding conflicting upstream information.
For paths, search the declared target bundle and apply bounded path
replacements without depending on surrounding prose or line numbers. Record
the scope, search rule, destination, and checks in the normalization reference
and candidate normalizer so every later refresh reapplies them.
The local issue-tracker normalization rewrites project-root `.scratch/`
references to `tracker/` only in the four Matt Pocock bundles declared in
that reference.
The plan-output normalization keeps implementation plans in `tmp/.plans/`
with one embedded task list and automatic checkpoints. The two retired
Superpowers plan skills are no longer imported; their authorized callers route
through the repository gateways without manufacturing execution approval.
The override registry and replay engine support existing legacy entries only;
do not add new entries or extend their scope. The generated apply diff is a
transport for a validated candidate, not a retained customization patch.

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
- Address bare caches explicitly with `--git-dir`; keep
  `safe.bareRepository=explicit` effective. Missing objects may trigger prepare;
  configuration, access, and command failures remain blockers.
- `--rebuild-cache` builds beside the active cache and reports `rebuilt` only
  after verified replacement.
- Missing snapshots trigger pinned `prepare` automatically in `plan` and
  `apply`, limited to missing metadata or missing upstream paths. Invalid
  metadata or mismatched attestation remains a blocker.

## TSV Output

- `--format tsv` emits escaped, deterministic, lexically sorted records.
- Header: `record\tkey\tstatus\tvalue`.
- Record types: `summary`, `source`, `metric`, `change`, `normalization`, `override`,
  `validation`, `blocker`.
- Metric and per-source validation rows use key `<source_id>.<name>`, status
  `ok` or `fail`, and the value in `value`.
- Provenance metric rows, derived from the manifest in every mode, use keys
  `<source_id>.repository` (owner/repo form), `<source_id>.ref`,
  `<source_id>.commit_date`, `<source_id>.advertised_ref`, and
  `<source_id>.skills_count`; an undeclared tag or date is reported as `-`.
- `summary.source_root` names the snapshot directory.
- `--format text` is the default; `--format json` retains backward-compatible
  keys and includes `source_provenance` and `normalized_paths` lists.

## Delta And Normalization

Report the final repository delta separately from candidate normalization.

- `changed_paths` and TSV `change` rows describe the sorted, unique
  candidate-versus-repository paths after normalizations and override replay.
  This corrects the former normalization-only meaning of `changed_paths`.
- `normalized_paths` and TSV `normalization` rows describe normalization work,
  not repository drift. Both TSV summary counts and text counts stay separate.
- Plan: report the proposed delta without modifying targets.
- Apply: report the delta used to build the applied patch, including additions,
  deletions, binary changes, and permission changes.
- Prepare and audit: return empty path lists because they do not compare a
  complete candidate. This is not proof of upstream equality or home alignment.
- Local caches: omit ignored, untracked Python bytecode and `__pycache__`
  contents only when the candidate does not own those paths. Preserve them on
  disk without reading their contents. Keep tracked, candidate-owned,
  nonignored, and non-cache content visible to the comparison.
- Errors: failed comparisons are blockers, never an empty successful delta.

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
   replay results. Keep normalization counts separate from actual changes.
4. Run `apply` to produce and apply the validated repository patch.

## Canonical Commands

Run from the repository root: `--repo-root` defaults to `.`, and
`--workspace` resolves against the current directory.

```bash
CLI=.github/skills/local-agent-sync-external-resources/scripts/sync_external_resources.py
WS=../cloud-strategy.github-external-refresh
python3 "$CLI" prepare --workspace "$WS" --format tsv
python3 "$CLI" audit --format tsv
python3 "$CLI" plan --workspace "$WS" --format tsv
python3 "$CLI" apply --workspace "$WS" --format tsv
python3 "$CLI" plan --source mattpocock-skills --workspace "$WS" --format tsv
python3 "$CLI" apply --source mattpocock-skills --workspace "$WS" --format tsv
```

## Live Network Benchmark (Separate Authorization Required)

The two largest sources are `github-awesome-copilot` (242 MiB) and
`sickn33-antigravity` (318 MiB). Require at least 90% reduction in
`materialized_bytes`; the second run must report `cached` with zero added cache
bytes. Do not alter manifest refs or repository targets, and never run without
separate authorization.

## Validation

- `python3 -m compileall .github/skills/local-agent-sync-external-resources/scripts`
- `python3 -m pytest -q .github/skills/local-agent-sync-external-resources/tests/scripts`
- `./.github/tools/run.sh validate-internal-skills --skill local-agent-sync-external-resources --strict`
- `make inventory-build`
- `make token-risks`

## Output

Report: mode, workspace, source root when used, managed count, changed paths,
normalized paths, override results, provenance rows, source metrics, validation,
and blockers. Lead with the bounded summary; disclose per-path or per-source
detail when relevant, without dropping blockers or provenance from the full
machine-readable report.

## Anti-Scope

- Do not refresh or modify imported skills while implementing sync tooling.
- Do not add a plugin system, concurrency, compatibility aliases, legacy
  fallback paths, or a generic sync framework.
- Network access and source identity follow Pinned Content Only; the live
  benchmark follows its own authorization rule.
