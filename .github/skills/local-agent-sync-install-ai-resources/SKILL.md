---
name: local-agent-sync-install-ai-resources
description: Use when planning, auditing, or applying allowlisted home-directory sync of repository-owned AI runtime resources to local Codex, Copilot, or OpenCode targets.
---

# Local Agent Sync Home AI Resources

## Referenced skills

- None.

Use this skill as the operating engine for `.github/agents/local-sync-install-ai-resources.agent.md`.
The paired agent is only a thin UX wrapper; this skill owns mode selection,
approval posture, safety gates, and report interpretation for repo-to-home sync
and bisync. Keep user-visible output deterministic, bounded, and summary-first.

Canonical command examples use `python3 ./.github/scripts/sync_home_ai_resources.py --format report`.

## When to use

- Plan a local home-directory sync for supported AI runtime resources, including shared skills and runtime-specific agents.
- Audit drift between repository-managed resources and the local runtime copies under the user home directory.
- Run readiness or doctor checks before touching runtime-owned directories.
- Apply an already reviewed plan for supported direct-copy skill families and allowlisted agent translations.
- Run bidirectional drift detection and reconciliation between `.github/skills/` and `~/.agents/skills/`.

## When not to use

- Source-side catalog governance in this repository; use `local-sync-external-resources` instead.
- Consumer-repository baseline sync; use `local-sync-global-copilot-configs-into-repo` instead.
- Personal configuration merge, runtime adapter generation, or general dotfiles management.
- Undocumented runtime families outside the allowlisted direct-copy skills and translated agents for OpenCode and Codex.

## Deterministic Operator Protocol

Every mode has exactly one command. Do not infer the mode, do not skip blockers, and do not treat `next_action` as user approval for `apply`. Plain `apply` and `bisync apply` still require an explicit user request. The `sync` command is the only auto-execute exception: it may write only through the install lane after a zero-blocker, no-drift preflight.

### Command Map

| User request | Lane | Command |
| --- | --- | --- |
| Generic `sync`, `repo→home`, or `repo wins` | Auto-run safe repo-to-home install for `skills`, then review only home-owned or ambiguous bisync drift | `python3 ./.github/scripts/sync_home_ai_resources.py sync --targets skills --home-root ~ --format report` |
| Explicit `home→repo` | Review home-newer drift, then use explicit bisync commands with a git-clean repo | `python3 ./.github/scripts/sync_home_ai_resources.py bisync plan --home-root ~ --format report` then `python3 ./.github/scripts/sync_home_ai_resources.py bisync apply --home-root ~ --format report` |
| Readiness check | Verify roots, support matrix, catalog, and state root without writes | `python3 ./.github/scripts/sync_home_ai_resources.py doctor --targets skills --home-root ~ --format report` |
| Dry install review | Show repo-to-home changes without writes | `python3 ./.github/scripts/sync_home_ai_resources.py plan --targets skills --home-root ~ --format report` |
| Explicit install write | Materialize a reviewed install plan | `python3 ./.github/scripts/sync_home_ai_resources.py apply --targets skills --home-root ~ --format report` |

For bundle direct-copy, replace `./.github/scripts/sync_home_ai_resources.py` with `./scripts/run.sh`, keep `--format report` on model-facing runs, and omit `--home-root` because it defaults to `$HOME`.

### Mode Selection

- `sync`: default safe automation for shared skills. Auto-apply clean repo-to-home install work, then stop only on home-owned or ambiguous bisync drift.
- `doctor`: read-only readiness checks for runtime roots, support matrix, catalog paths, and sync state.
- `plan` or `dry-run`: install-lane dry run.
- `audit`: compare source, manifest, and managed target paths without writing runtime files.
- `apply`: explicit install-lane materialization. Never run from `next_action` alone.
- `bisync plan`: read-only drift detection between `.github/skills/` and `~/.agents/skills/`.
- `bisync apply`: explicit bidirectional drift resolution after reviewed plan and clean repo preflight.

### Default Sync Sequence

When the user says "sync" without a mode:

1. Run `sync` for the default `skills` target.
2. The command builds an install-lane `apply` plan and stops before writing when blockers, missing directory creation, stale managed resources, destructive cleanup, or other manual gates are present.
3. If the install lane is clean, the command applies repo-to-home materialization and reports copied, skipped, validation, state, and manifest evidence.
4. After install, the command runs `bisync plan` as a review gate. Stop and ask for user direction only when bisync reports `home-to-repo`, `only-home`, or `equal-mtime` drift, or another non-safe blocker.
5. `repo-to-home` and `only-repo` bisync entries are safe informational leftovers for the default lane. Report them, but do not stop the sync run for them. Do not run `bisync apply` automatically.

Install must run before bisync because bisync modifies `~/.agents/skills/` directories that the install manifest tracks. Running install first copies fresh content from the repo with matching manifest hashes; bisync then finds both sides already aligned, avoiding spurious `target-modified-managed` blockers.

### Stop Conditions

Stop and report when any of these occur:

- A blocker code is present in the output.
- `next_action.allowed` is `false`, except for `sync` reports that have already completed their safe install-lane work and are reporting `done`.
- `next_action.requires_explicit_approval` is `true` and the user has not explicitly approved, except for the `sync` command's built-in install-lane auto-execute path.
- `sync` reports install-lane residual drift, missing directory creation without `--create-missing-dirs`, stale managed resources, or any install blocker.
- `sync` reports `home-to-repo`, `only-home`, `equal-mtime`, or another non-safe bisync blocker after install. Treat this as a review state, not an apply failure.
- `bisync apply` was requested without a prior `bisync plan`.
- The source repository has uncommitted or untracked changes during `bisync apply`.
- After `bisync apply` modifies `~/.agents/skills/` files that the install lane also manages, re-run install `plan`. Verified repo-to-home bisync copies refresh the manifest state; if `target-modified-managed` still appears, treat it as a real local divergence and review the path instead of deleting it as a routine recovery step.
- If `bisync apply` is blocked by `bisync-repo-dirty` and the local workspace has unrelated uncommitted changes, run bisync from a clean detached worktree at the same commit and pass it through `--source-root`.

## Core Operating Contract

- For the install lane, treat this repository as the source of truth for allowlisted home-sync resources.
- Install sync is unidirectional: repo -> home only. Block any attempt to sync from home to repo.
- Default generic sync requests to `sync`; keep plain `apply`, prune, directory creation, and all `bisync apply` writes explicit unless the user provided the matching flags or request.
- Limit v1 materialization to documented direct-copy skill families and allowlisted agent translations for Codex and OpenCode.
- Preserve unmanaged target-local files and directories.
- Prune stale managed assets only when explicit approval is present and the manifest entry passes schema validation, path confinement, and content-hash drift checks.
- Keep local sync state under `~/.sync/cloud-strategy-governance/home-ai-resources/`.
- Block writes when runtime support is undocumented, target paths are unsafe, ownership evidence is missing, the manifest is corrupt, or the source root sits under home sync state.
- Use `--retire-targets` when the managed target set should shrink, for example removing `opencode` while keeping `codex` and `copilot`.
- Accept `codex`, `copilot`, `opencode`, comma-separated combinations, `cross`, `all`, or `tutto`; normalize and order targets deterministically.
- Keep `references/home-sync-catalog.yaml` as policy and explicit non-skill resources only; skill bundles are auto-discovered from `.github/skills/` when `include_unlisted_skills` is true.

## Bisync Lane

The `bisync` lane provides explicit bidirectional synchronization between `.github/skills/` and `~/.agents/skills/`. It is a separate lane from install sync.

- Blocks `apply` when the source repository has uncommitted or untracked changes.
- Blocks `apply` when any `only-home` or `equal-mtime` entry exists.
- Blocks `apply` when post-copy hash verification fails.
- Blocks `apply` when post-apply plan still shows residual drift.
- Excludes all `local-*` bundles and runtime artifacts (`.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, `.pyo`) from scanning and copying.
- `only-repo`: when not excluded, `bisync apply` can create the bundle in home from the repository side.
- `only-home`: manual intervention required. Decide whether to keep it only in home, remove it, or add it to the repository.
- `equal-mtime`: hashes differ but mtime is equal. Manual decision required because the winner cannot be determined from timestamps alone.

## Reporting Contract

Use `--format report` for model-facing runs. Do not dump raw JSON unless the user explicitly asks for it. Machine-readable output remains available as `--format compact` or `--format json` for automation and debugging.

Every report must be summary-first and start with one status line that includes mode or lane, selected targets, overall status, blocker count, and `next_action.action`.

Then follow the exact text layout in `references/sync-contract.md`:

- `doctor`: `Status`, `Summary`, `Readiness`, `Validation`, and `Next`. Show non-ok readiness checks and tell the user what blocks the next write.
- `sync`: `Status`, `Summary`, `Auto-applied` or `Planned repo-to-home copies`, `Stopped on`, `Validation`, and `Next`. Summarize counts first, then show only the copied resources when writes occurred, or the planned copies when install review stopped the run before writing, plus the exact drift or blockers that stopped completion.
- `plan`, `audit`, and `bisync plan`: a compact summary, a change table when there are changes, and an attention table when there are blockers or drift decisions. For every proposed modification, explain the decision cause, for example repo copy is newer, home copy is newer, a managed resource is stale, or runtime support is not documented enough for apply.
- `apply` and `bisync apply`: a compact summary, an actions-performed table for writes, and a residual-issues table when needed. List copied, updated, pruned, or created resources and state why they were handled that way and how they were verified. Summarize unchanged managed resources by count instead of listing every skip.

Never report blocker codes alone. Translate each code into a plain-language reason and required follow-up. Never say a resource will change without stating what evidence selected the winner or triggered the recommendation. Bounded chat reports may omit excess change rows, but they must keep all blocker and attention rows visible and point to `--format json` for full detail.

## Bundled Automation

- Prefer `python3 ./.github/scripts/sync_home_ai_resources.py` for deterministic `plan`, `audit`, `doctor`, `apply`, and `bisync plan|apply` behavior, and keep `--format report` on model-facing runs.
- Use `scripts/run.sh` when a portable skill-local environment is needed; it installs the locked `PyYAML` dependency from `scripts/requirements.txt`.
- Keep orchestration inside `scripts/sync_home_ai_resources.py`, install behavior inside `scripts/home_syncing.py`, bisync behavior inside `scripts/bisync_skills.py`, report rendering inside `scripts/sync_output.py`, and reference loading inside `scripts/home_sync_contract.py`.

## Conflict Resolution

When plan, audit, or sync reports blocked paths, resolve them before apply:

- `target-exists-unmanaged`: target content exists at home but is not manifest-managed. Review and move or remove it manually before rerunning plan.
- `target-modified-managed`: manifest-managed content diverged from the recorded hash. If home is clearly newer, let bisync surface the explicit home-to-repo decision; if it persists after verified bisync reconciliation, treat it as real local divergence.
- `stale-managed`: previously managed content is no longer planned. Re-run with `--prune-managed` only after review.
- `retire-target-overlap`: the same target was requested as active and retired. Remove the overlap and rerun.
- `bisync-only-home`: decide whether to keep it only in home, remove it, or add it to the repository.
- `bisync-equal-mtime`: choose the winning side and touch the winner to advance mtime.
- `bisync-repo-dirty`: commit or stash, or run `bisync apply` from a clean detached worktree with `--source-root`.

After any manual cleanup, re-run `plan` or `bisync plan` and require zero blockers before any explicit apply.

## Load On Demand

- Read `references/runtime-support-matrix.yaml` when the runtime family or support level decides the mode.
- Read `references/sync-contract.md` for state files, manifest fields, materialization rules, doctor readiness, bisync contract, and reporting requirements.
- Read `references/error-codes.md` when the correct blocking code or remediation must be surfaced.
- Read `references/home-sync-catalog.yaml` only when changing default discovery policy or explicit agent resources.

## Validation

- Rebuild `.github/INVENTORY.md` when the bundle or related scripts change by using `./.github/scripts/build_inventory.sh --root .`.
- Run `./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks` after bundle or automation changes.
- Run `bash -n .github/skills/local-agent-sync-install-ai-resources/scripts/run.sh .github/scripts/sync_home_ai_resources.sh` after shell wrapper changes.
- Run focused agent or skill contract tests for this bundle.
- Run focused sync tests for report layout, target parsing, support-matrix policy, manifest handling, overwrite gates, bisync protocol, and missing-directory behavior when automation changes.
