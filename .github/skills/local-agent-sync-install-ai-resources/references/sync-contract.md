# Home Sync Contract

Use this reference when the paired agent or skill needs the exact sync rules rather than the compact summary in `SKILL.md`.

## Scope

- Source root: this repository.
- Target roots: runtime home resource directories for supported AI runtimes.
- Managed families in v1: allowlisted `skills` and `agents`.
- Excluded in v1: non-`skills` and non-`agents` runtime resources and undocumented families.

## State Root

Keep local state under `~/.sync/cloud-strategy-governance/home-ai-resources/`.

Expected state files:

- `manifest.json`
- `last-plan.json`
- `last-audit.json`
- `locks/home-ai-resources.lock`

Optional debug logs may live under `logs/` when the implementation needs durable operator evidence.

## Managed Resource Rules

- Copy files and directories. Do not create symlinks in v1.
- Preserve unmanaged target-local files.
- Record one manifest row per managed target resource.
- Prune only resources that were previously manifest-managed and are now absent from the new plan, including resources whose source bundle disappeared from the repo after an earlier sync.
- Require explicit prune approval before deleting stale managed resources.
- Treat `--retire-targets` as the explicit declaration that a previously active runtime should leave the managed target set on the next plan or apply.
- Exclude runtime-generated bundle artifacts from hashes and copies: `.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, and `.pyo`.

## Manifest Fields

Minimum fields:

- `schema_version`
- `generated_at`
- `source_root`
- `source_revision`
- `state_root`
- `targets`
- `managed_resources[]`

Each `managed_resources[]` item should capture:

- `target`
- `resource_family`
- `resource_id`
- `source_path`
- `target_path`
- `source_hash`
- `content_hash`
- `last_action`

## Target Path Rules

- Resolve every target path under the selected home directory.
- Block paths that escape the expected home root.
- Block unsupported symlink hops.
- Treat missing runtime roots as `needs-directory-create` in `plan` and `doctor`.
- Allow directory creation in `apply` only with explicit approval.

## Reporting Contract

Deterministic report output (`--format report`) and JSON reporting should expose at least:

- `selected_targets`
- `mode`
- `source_resources_considered`
- `copied`
- `skipped`
- `blocked`
- `conflicts`
- `unsupported_families_by_target`
- `missing_dirs`
- `validation`
- `residual_drift`
- `next_step`
- `next_action` (structured object with `action`, `allowed`, `requires_explicit_approval`, `command`, `reason`)

Text reports must use a table-first layout rather than a raw field dump.

### Shared Header

Always start with a short status line that includes:

- mode
- selected targets
- overall result or status
- blocker count
- `next_action.action`

### Doctor And Readiness Report

After the shared header, include a short readiness summary and a single table with this shape:

| Check or path | Status | Why it matters | What blocks next | Recommended action |
| --- | --- | --- | --- | --- |

Use this table for missing roots, documentation gaps, manifest problems, permission failures, and unsafe paths.

### Plan, Audit, And Bisync Plan Report

After the shared header, show one change-oriented table and one blocker table when they are non-empty.

Planned changes table:

| Resource or path | Lane | Planned action | Why this will change | Evidence or winner |
| --- | --- | --- | --- | --- |

Typical reasons include repo bundle newer than home, home bundle newer than repo, first-run install into a missing directory, stale managed resource marked for optional prune, or unmanaged content preserved by policy.

Blockers and skips table:

| Code or status | Resource or path | Why blocked or skipped | Required user action |
| --- | --- | --- | --- |

Populate `Why blocked or skipped` from the error-code meaning plus rationale, not from the code alone.

### Apply And Bisync Apply Completion Report

After the shared header, show one completed-actions table and one residual-issues table when needed.

Completed actions table:

| Resource or path | Action performed | Why it was done | Result | Verification |
| --- | --- | --- | --- | --- |

Allowed action labels include `copied`, `updated`, `pruned`, `preserved`, `skipped`, and `no-op`.

Residual issues table:

| Resource or path | Residual issue | Why it remains | Required follow-up |
| --- | --- | --- | --- |

`Verification` should state the strongest evidence available, for example hash match, manifest updated, post-apply plan clean, or explicit validation gap.

### No-Op Reporting

When no changes are proposed or applied, report `no-op` explicitly with the reason and still surface validation and `next_action`.

### Next Action Schema

```json
{
  "action": "apply|resolve_blockers|review|done|unknown",
  "allowed": true,
  "requires_explicit_approval": true,
  "command": "apply --targets codex --home-root ~",
  "reason": "Plan is ready with zero blockers. Run apply when ready."
}
```

## Automation Entry Points

- Bundled CLI: `scripts/sync_home_ai_resources.py`
- Bundled dependency bootstrap: `scripts/run.sh`
- Bundled implementation: `scripts/home_syncing.py`
- Bundled bisync engine: `scripts/bisync_skills.py`
- Bundled reference loader: `scripts/home_sync_contract.py`
- Bundled dependency lock: `scripts/requirements.txt`
- Repository wrapper: `.github/scripts/sync_home_ai_resources.py`
- Repository Bash wrapper: `.github/scripts/sync_home_ai_resources.sh`

Prefer the bundled scripts when the skill is direct-copied into a home runtime. Prefer the repository wrappers when running from this source repository because they reuse the repository maintenance-tool environment.

## Install Sync Contract

The install lane provides unidirectional `repo -> home` materialization of allowlisted resources.

### Install Modes

- `plan`: dry run that produces a readable diff and machine-readable state. Read-only.
- `audit`: compare source, manifest, and managed target paths. Read-only.
- `doctor`: verify runtime roots, permissions, symlink posture, and manifest health. Read-only.
- `apply`: materialize approved operations. Writes to home only.
- `dry-run`: alias of `plan`.

### Safety

- Block `apply` when `blocked_codes` are present.
- Block `apply` when runtime targets are undocumented and `--experimental-targets` is not set.
- Block `apply` on unmanaged overwrite, modified managed files, and stale-content drift.
- Block planning and apply when a target appears in both `--targets` and `--retire-targets`.
- Block `apply` when source root falls under home sync state directory.
- Block `apply` when manifest is corrupt.

### Post-apply

- Verify every copied resource by hash comparison.
- Write updated manifest with content hashes.
- When `bisync apply` copies a repo-wins bundle into home and the install manifest tracks that target, refresh the matching manifest entry so the next install plan does not report a stale `target-modified-managed` blocker for the verified copy.
- If reconciliation cannot be proven safe after a bisync copy, return `bisync-manifest-reconcile-failed` and keep the blocker visible instead of claiming convergence.
- Rewrite the manifest target set to the requested active targets only; retired targets are removed from manifest state after a successful apply.
- Report residual drift entries.

## Bisync Contract

The `bisync` lane provides explicit bidirectional reconciliation between `.github/skills/` and `~/.agents/skills/`. It is a separate lane from install sync.

### Bisync Modes

- `bisync plan`: detect drift. Read-only. Produces a drift list with entries for `repo-to-home`, `home-to-repo`, `only-repo`, `only-home`, and `equal-mtime`.
- `bisync apply`: resolve drift by copying winner to loser. Writes to both repo and home as needed.

### Logic

1. Scan both directories and collect all skill names (union).
2. Exclude bundles whose name starts with `local-agent-sync-`.
3. For each skill present in both sides:
   - Compute content hash (excluding `.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, `.pyo`).
   - If hashes match, the skill is `in-sync` (not reported).
   - If hashes differ, compare max mtime across all files in the bundle:
     - `repo_mtime > home_mtime` -> `repo-to-home`
     - `home_mtime > repo_mtime` -> `home-to-repo`
     - `repo_mtime == home_mtime` -> `equal-mtime` blocker
4. For skills only on one side:
  - report `only-repo` as an actionable repo-to-home creation candidate;
  - report `only-home` as a blocker that requires manual review.

### Preflight

Before any write in `bisync apply`:

1. Verify `git status --porcelain --untracked-files=all` on the source repository.
2. Block `apply` if the repository is not clean.
3. Block `apply` if any `only-home` or `equal-mtime` entry exists in the current plan.

### Apply

- Process `repo-to-home`, `home-to-repo`, and actionable `only-repo` drift entries.
- Copy the winner bundle (with runtime artifact exclusions) to the loser path.
- Remove the loser directory before copying to ensure a clean replacement.
- Verify the target hash matches the winner hash after copy.

### Post-apply Verification

- Re-run `bisync plan` after all copies complete.
- Accept success only when zero drift entries and zero blocked codes remain.
- Report residual drift with blocker codes on failure.

### Exclusions

- Runtime artifacts: `.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, `.pyo`.
- Bundle prefix: `local-agent-sync-*` bundles are excluded from bisync scanning and copying.

### Output

The `bisync` payload includes:

- `drifts`: list of drift entries with `skill`, `type`, `direction`, `repo`, `home`.
- `blocked_codes`: list of active blocker codes.
- `next_step`: human-readable next instruction.
- `next_action`: structured object with `action`, `allowed`, `requires_explicit_approval`, `command`, `reason`.
- `verification`: post-apply status with `status` and optional `reason` or `residual_drifts`.
