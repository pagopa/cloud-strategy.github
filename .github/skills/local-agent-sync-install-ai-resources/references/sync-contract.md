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
- Prune only resources that were previously manifest-managed and are now absent from the new plan.
- Require explicit prune approval before deleting stale managed resources.
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

## Automation Entry Points

- Bundled CLI: `scripts/sync_home_ai_resources.py`
- Bundled dependency bootstrap: `scripts/run.sh`
- Bundled implementation: `scripts/home_syncing.py`
- Bundled reference loader: `scripts/home_sync_contract.py`
- Bundled dependency lock: `scripts/requirements.txt`
- Repository wrapper: `.github/scripts/sync_home_ai_resources.py`
- Repository Bash wrapper: `.github/scripts/sync_home_ai_resources.sh`

Prefer the bundled scripts when the skill is direct-copied into a home runtime. Prefer the repository wrappers when running from this source repository because they reuse the repository maintenance-tool environment.

## Bisync Contract

The `bisync` mode provides bidirectional synchronization between `.github/skills/` and `~/.agents/skills/` using mtime-based conflict resolution.

### Logic

1. Scan both directories and collect all skill names (union)
2. For each skill present in both sides:
   - Compute content hash (excluding `__pycache__`, `.pyc`, `.pyo`, `.venv`, `.pytest_cache`)
   - If hashes match → `in-sync`
   - If hashes differ → compare max mtime across all files in the bundle
   - The side with the newer mtime wins
3. For skills only in one side → report as `only-repo` or `only-home` (manual action required)

### Commands

- `bisync plan`: detect drift and show direction (read-only)
- `bisync apply`: copy winner → loser for each drifted skill

### Safety

- `plan` is read-only and safe to run anytime
- `apply` copies entire skill bundles to maintain consistency
- Post-apply verification: re-run `bisync plan` to confirm 0 drift

### Exclusions

- `__pycache__`, `.pyc`, `.pyo`, `.venv`, `.pytest_cache` are excluded from hash and mtime calculations
- `local-agent-sync-*` skills are repo-only and not included in bisync
