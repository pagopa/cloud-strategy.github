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

Text and JSON reporting should expose at least:

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
4. For skills only on one side, report `only-repo` or `only-home` blocker.

### Preflight

Before any write in `bisync apply`:

1. Verify `git status --porcelain --untracked-files=all` on the source repository.
2. Block `apply` if the repository is not clean.
3. Block `apply` if any `only-repo`, `only-home`, or `equal-mtime` entry exists in the current plan.

### Apply

- Process only `repo-to-home` and `home-to-repo` drift entries.
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
