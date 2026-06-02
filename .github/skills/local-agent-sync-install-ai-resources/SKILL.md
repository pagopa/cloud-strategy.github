---
name: local-agent-sync-install-ai-resources
description: Use when planning, auditing, or applying allowlisted home-directory sync of repository-owned AI runtime resources to local Codex, Copilot, Claude Code, or OpenCode targets.
---

# Local Agent Sync Home AI Resources

## Referenced skills

- None.

Use this skill as the operating engine for `.github/agents/local-sync-install-ai-resources.agent.md`.

The paired agent is a thin UX wrapper; this skill owns all business logic, sequencing, approval posture, safety gates, and reporting. Keep detailed tables and checklists in `references/`. Keep deterministic execution helpers in `scripts/` so the skill remains portable as a direct-copy bundle.

## When to use

- Plan a local home-directory sync for supported AI runtime resources, including skills and agents.
- Audit drift between repository-managed resources and the local runtime copies under the user home directory.
- Run readiness or doctor checks before touching runtime-owned directories.
- Apply an already reviewed plan for supported direct-copy skill families and allowlisted agent translations.
- Run bidirectional drift detection and reconciliation between `.github/skills/` and `~/.agents/skills/`.

## When not to use

- Source-side catalog governance in this repository; use `local-sync-external-resources` instead.
- Consumer-repository baseline sync; use `local-sync-global-copilot-configs-into-repo` instead.
- Personal configuration merge, runtime adapter generation, or general dotfiles management.
- Undocumented runtime families outside the allowlisted direct-copy skills and translated agents for Claude, OpenCode, and Codex.

## Deterministic Operator Protocol

Every mode has exactly one command. Do not infer the mode, do not skip blockers, and do not treat `next_action` as user approval for `apply`. Each `apply` requires an explicit user request.

### Lane Selection

| User request | Lane | Command |
| --- | --- | --- |
| Generic `sync` without a mode | Run `bisync plan` first, stop on blockers, then run install `plan` | See `Default Sync Sequence` below |
| `bisync plan` | Bidirectional drift detection (read-only) | `./.github/scripts/sync_home_ai_resources.py bisync plan --home-root ~` |
| `bisync apply` | Bidirectional drift resolution (writes to both sides) | `./.github/scripts/sync_home_ai_resources.py bisync apply --home-root ~` |
| `plan` | Install lane dry run | `./.github/scripts/sync_home_ai_resources.py plan --targets <targets> --home-root ~` |
| `audit` | Compare source, manifest, and target paths | `./.github/scripts/sync_home_ai_resources.py audit --targets <targets> --home-root ~` |
| `doctor` | Readiness checks for runtime roots and support matrix | `./.github/scripts/sync_home_ai_resources.py doctor --targets <targets> --home-root ~` |
| `apply` | Install lane materialization | `./.github/scripts/sync_home_ai_resources.py apply --targets <targets> --home-root ~` |

For bundle direct-copy, replace `./.github/scripts/sync_home_ai_resources.py` with `./scripts/run.sh` and omit `--home-root` (defaults to `$HOME`).
When the desired active runtimes change, pair `--retire-targets <targets>` with `--prune-managed` to remove runtime-specific managed copies and drop those targets from the manifest while keeping the remaining targets active.

### Default Sync Sequence

When the user says "sync" without a mode:

1. Run install `plan` for the requested targets. Stop on blockers.
2. Resolve any install-lane blockers before proceeding.
3. Run `bisync plan`. Stop on blockers.
4. Report both results. Do not apply automatically.
5. Wait for explicit user request to apply either lane.

Install must run before bisync because bisync modifies `~/.agents/skills/` directories that the install manifest tracks. Running install first copies fresh content from the repo with matching manifest hashes; bisync then finds both sides already aligned, avoiding spurious `target-modified-managed` blockers.

When applying, run install `apply` first, then `bisync apply`. Both lanes must be explicitly requested.

### Stop Conditions

Stop and report when any of these occur:

- A blocker code is present in the output.
- `next_action.allowed` is `false`.
- `next_action.requires_explicit_approval` is `true` and the user has not explicitly approved.
- `bisync apply` was requested without a prior `bisync plan`.
- The source repository has uncommitted or untracked changes during `bisync apply`.
- After `bisync apply` modifies `~/.agents/skills/` files that the install lane also manages, re-run install `plan` and resolve any `target-modified-managed` blockers caused by stale manifest hashes before considering the sync complete.

### Output

Every command produces JSON output with `--format json` and text output by default. The payload always includes:

- `next_step`: human-readable next instruction (backward compatible).
- `next_action`: structured object with `action`, `allowed`, `requires_explicit_approval`, `command`, and `reason`.

Report `next_action` to the user. Do not execute `command` from `next_action` unless the user explicitly asks.

## Core Operating Contract

- For the install lane, treat this repository as the source of truth for allowlisted home-sync resources.
- Install sync is unidirectional: repo -> home only. Block any attempt to sync from home to repo.
- Default to `plan` and keep `apply` explicit.
- Limit v1 default materialization to documented direct-copy skill families and allowlisted agent translations for Codex, Claude, and OpenCode.
- Preserve unmanaged target-local files and directories.
- Prune only stale managed assets, including manifest-managed resources whose source bundle was removed from the repo, and only when explicit approval is present and the manifest entry passes schema validation, path confinement, and content-hash drift checks.
- Keep local sync state under `~/.sync/cloud-strategy-governance/home-ai-resources/`.
- Block `apply` when runtime support is undocumented, target paths are unsafe, or ownership evidence is missing.
- Keep runtime support evidence explicit through the paired references instead of inferring undocumented home paths.
- Use `--retire-targets` when the managed target set should shrink, for example removing `claude` while keeping `codex` and `copilot`.

## Bisync Lane

The `bisync` lane provides explicit bidirectional synchronization between `.github/skills/` and `~/.agents/skills/`. It is a separate lane from install sync.

### Commands

- `bisync plan`: detect drift (read-only). Reports `repo-to-home`, `home-to-repo`, `only-repo`, `only-home`, and `equal-mtime` entries.
- `bisync apply`: resolve drift by copying the winner bundle to the loser side. Applies only `repo-to-home` and `home-to-repo` entries. Blocks on all other cases.

### Safety Gates

- Blocks `apply` when the source repository has uncommitted or untracked changes.
- Blocks `apply` when any `only-repo`, `only-home`, or `equal-mtime` entry exists.
- Blocks `apply` when post-copy hash verification fails.
- Blocks `apply` when post-apply plan still shows residual drift.
- Excludes `local-agent-sync-*` bundles and runtime artifacts (`.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, `.pyo`) from scanning and copying.

### Conflict Resolution

- `only-repo` and `only-home`: manual intervention required. Decide which side to keep or remove.
- `equal-mtime`: hashes differ but mtime is equal. Manual decision required because the winner cannot be determined from timestamps alone.

## Output Expectations

- Selected mode, selected targets, and why that mode is valid.
- Source resources considered and the runtime support evidence used.
- Missing directories, conflicts, or documentation gates that block `apply`.
- For every blocked path, conflict, stale-managed entry, or non-ok doctor check, include a human-readable motivation that explains the policy or safety reason behind the recommendation.
- Managed versus preserved target-local outcomes and any approved prune behavior.
- Validation results, remaining blockers, and explicit validation gaps.
- `next_step` (text) and `next_action` (structured object).

## Mode Selection

- `plan`: produce a readable dry run and machine-readable state.
- `audit`: compare source, manifest, and managed target paths without writing runtime files.
- `doctor`: verify runtime roots, permissions, symlink posture, manifest health, and support-matrix readiness.
- `apply`: explicit only. Materialize only approved and safe operations.
- `dry-run`: alias of `plan`, not a separate behavior.
- `bisync plan`: bidirectional drift detection between `.github/skills/` and `~/.agents/skills/`.
- `bisync apply`: bidirectional drift resolution. Write only after preflight passes.

## Target Selection

- Accept `codex`, `copilot`, `claude`, `opencode`, comma-separated combinations, `cross`, `all`, or `tutto`.
- Normalize whitespace, deduplicate, and order targets deterministically.
- Resolve skill roots as `~/.agents/skills` for all targets (scenario B: unification).
- When multiple targets resolve to the same physical path, perform the copy operation only once (physical deduplication).
- After apply, verify every copied resource by re-reading the target and comparing hashes.
- Block reverse sync: source root must not be under the home sync state directory.

## Source And Materialization Policy

- Read the runtime contract from `references/runtime-support-matrix.yaml` and the readable summary in `references/runtime-support-matrix.md`.
- Read the source allowlist from `references/home-sync-catalog.yaml`.
- Include only allowlisted `skills` and `agents` in v1.
- Copy managed resources instead of creating symlinks.
- Translate allowlisted `.agent.md` sources deterministically for Codex, Claude, and OpenCode targets.
- Preserve target-local content that is outside the manifest.
- Record source hashes, expected content hashes, and managed target paths in the local manifest.
- Keep the manifest target set aligned with the requested active targets; retired targets leave the manifest only through an explicit run that names them in `--retire-targets`.
- Exclude runtime-generated bundle artifacts such as `.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, and `.pyo` from hashes and copies.

## Bundled Automation

- Prefer `./.github/scripts/sync_home_ai_resources.py` for deterministic `plan`, `audit`, `doctor`, `apply`, and `bisync plan|apply` behavior.
- Use `scripts/run.sh` when a portable skill-local environment is needed; it installs the locked `PyYAML` dependency from `scripts/requirements.txt`.
- Keep library behavior inside `scripts/home_syncing.py`, bisync logic inside `scripts/bisync_skills.py`, and reference loading inside `scripts/home_sync_contract.py`.

## Install Safety Gates

- Block unmanaged overwrite.
- Block managed overwrite when the target content diverged from the last recorded manifest.
- Block stale managed delete when the manifest entry is invalid, escapes the expected runtime root, or the file content drifted from the recorded hash.
- Block unsafe home paths, unsupported symlink hops, missing target roots without explicit create approval, and undocumented runtime claims.
- Block `bisync apply` on dirty repository, `only-repo`, `only-home`, `equal-mtime`, and post-apply verification failure.
- Keep the canonical error taxonomy in `references/error-codes.md`.
- Keep the doctor checklist in `references/doctor-checks.md`.

## Install Conflict Resolution

When plan or audit reports blocked paths, resolve them before apply:

- `target-exists-unmanaged`: the target file or directory exists at home but is not in the sync manifest. Remove it manually so sync can recreate it from source.
- `target-modified-managed`: the target is in the manifest but its content diverged from the last recorded hash. Remove it manually so sync can restore the source-of-truth version.
- `stale-managed` with a removed source bundle: the resource was managed previously but its source bundle no longer exists in the repo. Re-run with `--prune-managed` after review to remove the stale managed copy.
- `retire-target-overlap`: the same target was requested as both active and retired. Remove the overlap and re-run.
- After removing conflicting files, re-run plan to confirm zero blockers before applying.

When `bisync plan` reports blocker entries, resolve them before `bisync apply`:

- `bisync-only-repo`: the skill exists only in the source repo. Copy it into home manually (preferred when the skill is newer in repo) or decide the repo-only status is intentional and skip it.
- `bisync-only-home`: the skill exists only in the home directory. Remove from home manually or decide to add to repo.
- `bisync-equal-mtime`: hashes differ but mtime is equal for both sides. Decide which side wins and touch the winner to advance mtime.

## Load On Demand

- Read `references/runtime-support-matrix.md` when the runtime family or support level decides the mode.
- Read `references/sync-contract.md` for state files, manifest fields, materialization rules, bisync contract, and reporting requirements.
- Read `references/error-codes.md` when the correct blocking code or remediation must be surfaced.
- Read `references/doctor-checks.md` when readiness validation or local remediation steps matter.

## Validation

- Rebuild `.github/INVENTORY.md` when the bundle or related scripts change by using `./.github/scripts/build_inventory.sh --root .`.
- Run `./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks` after bundle or automation changes.
- Run `bash -n .github/skills/local-agent-sync-install-ai-resources/scripts/run.sh .github/scripts/sync_home_ai_resources.sh` after shell wrapper changes.
- Run focused agent or skill contract tests for the touched bundle.
- Run focused sync tests for target parsing, support-matrix policy, manifest handling, overwrite gates, bisync protocol, and missing-directory behavior when automation changes.
