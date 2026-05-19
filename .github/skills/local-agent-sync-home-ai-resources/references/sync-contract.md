# Home Sync Contract

Use this reference when the paired agent or skill needs the exact sync rules rather than the compact summary in `SKILL.md`.

## Scope

- Source root: this repository.
- Target roots: runtime home directories for supported AI runtimes.
- Managed families in v1: allowlisted `skills` only.
- Excluded in v1: runtime config, global overrides, prompt files, undocumented families, and any translated output.

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
