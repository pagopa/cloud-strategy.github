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

## Managed source inventory

The table below is a quick-reference view of the repositories managed by this
skill. The canonical source of truth is
[`references/managed-resources.yaml`](references/managed-resources.yaml); its
`ref` field is the full commit object ID used by the sync. Open a hash to
inspect the exact upstream commit.

| Source ID | Repository | Pinned `ref` | Commit date (UTC) | Release/tag |
| --- | --- | --- | --- | --- |
| `antonbabenko-terraform-skill` | [`antonbabenko/terraform-skill`](https://github.com/antonbabenko/terraform-skill) | [`0a3a4a66e99001347d36a41e10260a825be3ab62`](https://github.com/antonbabenko/terraform-skill/commit/0a3a4a66e99001347d36a41e10260a825be3ab62) | 2026-07-03 | not tagged |
| `github-awesome-copilot` | [`github/awesome-copilot`](https://github.com/github/awesome-copilot) | [`aa280f28b1b73f9b6e6917b607eb92127b67b419`](https://github.com/github/awesome-copilot/commit/aa280f28b1b73f9b6e6917b607eb92127b67b419) | 2026-07-24 | not tagged |
| `obra-superpowers` | [`obra/superpowers`](https://github.com/obra/superpowers) | [`3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`](https://github.com/obra/superpowers/commit/3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9) | 2026-07-24 | [v6.2.0](https://github.com/obra/superpowers/releases/tag/v6.2.0) |
| `hashicorp-agent-skills` | [`hashicorp/agent-skills`](https://github.com/hashicorp/agent-skills) | [`8c6573abbd21e8094fab8f538eb5f97db63133fd`](https://github.com/hashicorp/agent-skills/commit/8c6573abbd21e8094fab8f538eb5f97db63133fd) | 2026-07-15 | not tagged |
| `mattpocock-skills` | [`mattpocock/skills`](https://github.com/mattpocock/skills) | [`ed37663cc5fbef691ddfecd080dff42f7e7e350d`](https://github.com/mattpocock/skills/commit/ed37663cc5fbef691ddfecd080dff42f7e7e350d) | 2026-07-21 | not tagged |
| `vercel-labs-skills` | [`vercel-labs/skills`](https://github.com/vercel-labs/skills) | [`e173b8c88f2581cfdaa1b6767c6519a08155790e`](https://github.com/vercel-labs/skills/commit/e173b8c88f2581cfdaa1b6767c6519a08155790e) | 2026-07-22 | not tagged |
| `openai-skills-curated` | [`openai/skills`](https://github.com/openai/skills) | [`49f948faa9258a0c61caceaf225e179651397431`](https://github.com/openai/skills/commit/49f948faa9258a0c61caceaf225e179651397431) | 2026-06-24 | not tagged |
| `openai-skills-retained-doc` | [`openai/skills`](https://github.com/openai/skills) | [`49f948faa9258a0c61caceaf225e179651397431`](https://github.com/openai/skills/commit/49f948faa9258a0c61caceaf225e179651397431) | 2026-06-24 | not tagged |
| `sickn33-antigravity` | [`sickn33/antigravity-awesome-skills`](https://github.com/sickn33/antigravity-awesome-skills) | [`e66fc833f2022c3534ba74af835db14c34f9a732`](https://github.com/sickn33/antigravity-awesome-skills/commit/e66fc833f2022c3534ba74af835db14c34f9a732) | 2026-07-24 | [v15.4.0](https://github.com/sickn33/agentic-awesome-skills/releases/tag/v15.4.0) |
| `addyosmani-agent-skills` | [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | [`ff2df4c07e7836a092ed28e1e9b42f4d6009280c`](https://github.com/addyosmani/agent-skills/commit/ff2df4c07e7836a092ed28e1e9b42f4d6009280c) | 2026-07-24 | [0.6.5](https://github.com/addyosmani/agent-skills/releases/tag/0.6.5) |
| `atlassian-mcp-server` | [`atlassian/atlassian-mcp-server`](https://github.com/atlassian/atlassian-mcp-server) | [`f22e7075136a62baa7c10200a64884f83bf3ebe1`](https://github.com/atlassian/atlassian-mcp-server/commit/f22e7075136a62baa7c10200a64884f83bf3ebe1) | 2026-07-08 | not tagged |
| `anthropic-skills` | [`anthropics/skills`](https://github.com/anthropics/skills) | [`b29e7cf65e5cb78a5ac33d582270551bc74a14eb`](https://github.com/anthropics/skills/commit/b29e7cf65e5cb78a5ac33d582270551bc74a14eb) | 2026-07-24 | not tagged |

Commit dates are the committer dates in UTC. Release/tag values are shown only
when an exact tag points to the pinned commit; otherwise the value is
`not tagged`. The metadata was checked on 2026-08-01.

This catalog is commit-pinned, not release-pinned:

- `ref` is the immutable upstream version identity; tags and branches are not
  accepted as the source identity.
- The top-level `version: 1` in the manifest is the manifest schema version,
  not an upstream release version.
- Release/tag is informational and never replaces `ref`. The optional
  `advertised_ref` can provide another human-readable ref when deliberately
  declared, but it never replaces `ref`.

## Modes

- `prepare`: explicitly fetches pinned Git content into a repository-keyed
  partial-clone cache and exports only manifest-declared asset paths into
  verified snapshots under the repository `tmp/` root.
- `audit`: parse all registries, validate local paths, canonical names, hashes,
  watchlist shape, and dirty state. Does not fetch or write.
- `plan`: require an external workspace, automatically run the pinned prepare
  flow when snapshots are missing, build and validate the complete candidate,
  then emit the changed-path summary without repository writes.
- `apply`: perform `plan`, automatically prepare missing snapshots, reject
  dirty targets unless `--allow-dirty`, generate one patch, run
  `git apply --check`, apply once, rebuild inventory, and rerun scoped
  validation.

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

## Managed Skill Frontmatter

- Normalize every managed `SKILL.md` for Codex and GitHub Copilot while
  preserving its `/skill-name` references.
- Remove `disable-model-invocation` from skill frontmatter. That field belongs
  to custom agents and makes the skill invalid for Codex skill discovery.
- Keep invocation policy in each bundle's `agents/openai.yaml`.

## Executable Python Normalization

- A source may set `ensure_python_shebangs: true` to prepend
  `#!/usr/bin/env python3` to executable `.py` files that have no shebang.
- The Anthropic skills source enables this normalization so refreshed
  candidates continue to pass the executable-shebang repository check.
- Preserve existing shebangs, non-executable Python modules, and non-Python
  executables unchanged.

## Guided Question Contract

- Candidate normalization appends a repository-owned contract to
  `superpowers-brainstorming` and `grill-me` whenever either canonical skill is
  managed, regardless of its source or upstream wording.
- The contract requires numbered bulk question blocks. Every question includes
  a brief `Recommendation`, `Why`, and `Default if accepted`.
- The appended contract explicitly overrides upstream one-question-at-a-time
  pacing. A single remaining blocker is still a numbered one-item block.
- The append is marker-based and idempotent. Do not replace it with a
  context-sensitive replay patch.

## Wayfinder Critical Validation And Grilling Contracts

- Candidate normalization appends two repository-owned contracts to
  `mattpocock-wayfinder`.
- Before Wayfinder creates or updates an artifact, it must have
  `internal-gateway-critical-master` challenge the analysis, counter-validate
  every material critique against evidence and constraints, incorporate every
  supported instruction, and stop when a supported objection remains unresolved.
- One gate covers one analysis unit and its related content-producing write
  batch. The required ticket claim is exempt and remains the first coordination
  action. Rerun the critic only after new evidence or a materially supported
  revision changes the analysis; never rerun it against unchanged evidence.
- Every Wayfinder Grilling ticket and `grill-me` invocation asks all currently
  known questions in numbered bulk blocks. Every question includes `Question`,
  `Recommendation`, `Why`, and `Default if accepted`.
- Both contracts are canonical-name-scoped, marker-based, and idempotent. Do
  not replace them with replay patches.

## Repository-Owned Skill Contracts

- Express additive repository-owned behavior, workspace, and output-path
  requirements as canonical-name-scoped, marker-based candidate normalizations.
- These normalizations must replace their own marked block, remain idempotent,
  and preserve unrelated upstream content when surrounding text changes.
- Matt Pocock handoff output and its PRD-aware non-duplication wording are
  canonical marked normalizations, not replay-patch ownership.
- Do not use replay patches for this class of managed-skill customization.
- Reserve replay patches for irreducible edits to upstream-owned lines that
  cannot be expressed safely as an additive marked contract. Record why a
  normalization is insufficient before registering such an exception.

## Workspace Convention

- The runtime workspace must be outside this repository.
- Use an external workspace such as `../cloud-strategy.github-external-refresh`.
- Keep prepared source snapshots under
  `<repo-root>/tmp/.cache/external-sync-resources-snapshots/` for normal CLI runs.
  `--source-root` remains an explicit override for a prepared checkout supplied
  by an operator or a test.
- The Git object cache lives under `<workspace>/cache/repositories/`.
- Each prepared source snapshot under
  `<repo-root>/tmp/.cache/external-sync-resources-snapshots/<source_id>/` contains
  `.external-resource-source.tsv` with
  the exact fields `source_id`, `repository`, `ref`, and `paths_sha256`.
- Before copying source assets, `plan` and `apply` compare all four fields with
  the manifest source. A mismatch blocks candidate creation.
- `ref` is the full manifest commit object ID. `paths_sha256` hashes only the
  sorted declared upstream path names; it is not a file-content integrity hash.
- `audit` remains registry and target-state validation and does not consume
  prepared snapshots.

## Prepare Cold and Warm Flow

- Cold `prepare` fetches each declared source SHA into the partial-clone cache,
  verifies the commit object, and exports only declared upstream paths into
  atomic snapshots under
  `<repo-root>/tmp/.cache/external-sync-resources-snapshots/<source_id>/`.
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
- `summary.source_root` identifies the snapshot directory used by the run.
- `--format text` remains the default for operators.
- `--format json` retains backward-compatible keys.

## Safety

- Workspace must be outside the repository; the default snapshot root is the
  repository's disposable `tmp/.cache/external-sync-resources-snapshots/` directory.
- Dirty managed targets block `apply` unless `--allow-dirty` is supplied.
- Missing snapshots trigger the declared pinned prepare flow in `plan` and
  `apply`; invalid or mismatched snapshots stop before candidate creation.
- Override replay is atomic: if any override fails verification, no candidate
  changes reach the repository.
- Do not modify repository targets until the complete candidate tree,
  normalizations, overrides, and generated patch pass validation.

## Workflow

1. Run `audit` to validate the manifest, overrides, and local dirty-state.
2. Run `plan` with `--workspace`; it prepares missing pinned content
  automatically and confirms the candidate can be built.
3. Review the changed-path summary, source metrics, and override replay
  results.
4. Run `apply`; it reuses valid snapshots or prepares missing ones before the
  repository patch.

Automatic preparation is limited to missing source metadata or missing
upstream paths. Invalid metadata and mismatched attestations remain blockers.

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

- Do not register a replay patch for an additive repository-owned skill
  contract; implement a canonical-name-scoped marked normalization instead.
- Do not register the former Matt Pocock handoff replay patch; its output path
  and non-duplication wording are supplied by candidate normalization.
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
- Do not perform network refreshes outside the declared pinned prepare flow.
  The live benchmark still requires separate authorization.
- Do not use package managers or mutable branch updates in any sync mode.
