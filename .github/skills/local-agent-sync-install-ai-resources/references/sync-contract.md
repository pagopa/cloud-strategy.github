# Home Sync Contract

Use this reference when the paired agent or skill needs the exact sync rules rather than the compact summary in `SKILL.md`.

## Scope

- Source root: this repository.
- Target roots: runtime home resource directories for supported AI runtimes.
- Managed families in v1: allowlisted `skills` and `agents`.
- Excluded in v1: non-`skills` and non-`agents` runtime resources and undocumented families.
- Skill resources are normally auto-discovered from `.github/skills/` according to `home-sync-catalog.yaml` defaults. The catalog should list policy defaults and explicit non-skill resources, not serialize every skill bundle. Defaults may also exclude specific home-kept skill IDs from install and bisync and may declare whether unmanaged home skill bundles stay blocked or are adopted with repo-wins behavior.

## State Root

Keep local state under `~/.sync/cloud-strategy-governance/home-ai-resources/`.

Expected state files:

- `manifest.json`
- `last-plan.json`
- `last-audit.json`
- `last-bisync-plan.json`
- `locks/home-ai-resources.lock`

Optional debug logs may live under `logs/` when the implementation needs durable operator evidence.

## Managed Resource Rules

- Copy files and directories. Do not create symlinks in v1.
- Preserve unmanaged target-local files unless the active catalog policy explicitly adopts unmanaged skill bundles with repo-wins behavior.
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

`--format compact` is the default and the preferred format for AI/tool
iteration. It emits a single-line JSON object with status, counts, blockers,
next action, and a small bounded evidence sample. Use `--format report` only
when a human-readable command report is explicitly needed. In chat, agents
should translate compact output into concise Markdown instead of asking the CLI
to spend tokens on tables.

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

Text reports must use a summary-first layout rather than a raw field dump. Use tables where columns clarify changes, blockers, or completed actions; use short bullets for counts and state summaries.

Human-readable report tables should stay bounded for routine change and completed-action rows. Keep all blocker, attention, and readiness-failure rows visible. When rows are omitted, add an explicit omitted-count row and point to `--format json` for full detail.

## Canonical Chat Template

Use this template when you need to answer the user directly in chat. Keep the wording plain and convert the labels into the conversation language when appropriate.

### Problem Report

Use this structure when the sync is not yet finished or when the user needs to choose a direction:

1. `Status`
  - One short line with the overall result.
2. `What is happening`
  - One short paragraph that explains the current state in plain language.
3. `Differences`
  - List only the actionable changes.
  - Number the items when the user may need to choose between them.
  - Summarize unchanged or skipped resources by count unless the user asked for the full list.
4. `Why it stops`
  - Explain the smallest real blocker, not the internal code name.
  - Include only the drift or policy item that prevents the next step.
5. `Choices`
  - Present only the actions the user can actually take now.
  - Use numbered options.
  - Put the recommended choice first.
  - Keep each option to one line when possible.

### Completion Report

Use this structure when the work is finished:

1. `Result`
  - Say whether the run completed, applied changes, or ended as no-op.
2. `What changed`
  - One short paragraph with the concrete outcome.
3. `Final verification`
  - State the strongest evidence available, such as a clean plan, hash match, or zero residual drift.
4. `Residuals`
  - Include only if something still needs attention.
  - If nothing remains, say `none`.
5. `Next step`
  - If the run is done, say there is nothing else to do.
  - If the run is blocked, name the single next action.

### Shared Header

Always start with a short status line that includes:

- mode
- human-friendly lane label, such as `repo-to-home install` for install or `repo-home drift` for bisync
- selected targets
- overall result or status
- blocker count
- `next_action.action`

### Summary-First Layout

Use these stable sections when rendering model-facing reports:

- `Summary`: target, resource, drift, blocked, and already-aligned counts.
- `Readiness`: doctor-only non-ok checks with why they matter, what blocks next, and the recommended action.
- `Changes`: proposed or completed writes, with one row per changed resource.
- `Attention`: blockers, ambiguous drift, or decisions that need a user.
- `Validation`: strongest available evidence such as hash match, manifest path, state path, or post-apply clean plan.
- `Remaining Work`: include only when something remains.
- `Next`: structured next action and reason.

Do not list every unchanged managed resource in model-facing reports. Summarize skipped or already-aligned resources by count unless the user asks for full audit detail or selects JSON output.

### Doctor And Readiness Report

After the shared header, include a short readiness summary and a single table with this shape:

| Check or path | Status | Why it matters | What blocks next | Recommended action |
| --- | --- | --- | --- | --- |

Use this table for missing roots, documentation gaps, manifest problems, permission failures, and unsafe paths.

### Sync, Plan, Audit, And Bisync Plan Report

For top-level `sync`, use this compact chat order: `Status`, `Summary`, `Auto-applied` or `Planned repo-to-home copies`, `Stopped on`, `Validation`, and `Next`.

After the shared header and summary, show one change-oriented table and one attention table when they are useful.

Planned changes table:

| Resource or path | Lane | Planned action | Why this will change | Evidence or winner |
| --- | --- | --- | --- | --- |

Typical reasons include repo bundle newer than home, home bundle newer than repo, first-run install into a missing directory, stale managed resource marked for optional prune, or unmanaged content preserved by policy.

Attention table:

| Code or status | Resource or path | Why it needs attention | Required user action |
| --- | --- | --- | --- |

Populate `Why it needs attention` from the error-code meaning plus rationale, not from the code alone. Include skips only when they are exceptional; routine unchanged resources belong in the summary count.

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

### Top-Level Sync Mode

The `sync` command is the only auto-execute mode.

Behavior:

1. Build an install-lane `apply` plan for the selected targets, defaulting to `skills`.
2. Stop before writing when install blockers, residual drift, stale managed resources, missing directory creation without `--create-missing-dirs`, or destructive cleanup gates are present.
3. If the install lane is clean, apply repo-to-home materialization and verify hashes plus manifest state.
4. For the default `skills` target, run `bisync plan` after install.
5. Stop and report `needs_review` when bisync reports `home-to-repo`, `only-home`, `equal-mtime`, or another non-safe blocker. Do not run `bisync apply` automatically.
6. Treat `repo-to-home` and `only-repo` bisync entries as safe informational leftovers for default `sync`; report them without stopping the sync run.
7. Report `done` when install succeeded or had no work and bisync has no home-owned or ambiguous drift.

Exit behavior:

- Return `0` when `sync` reaches `done`.
- Return non-zero when `sync` stops for blocker, missing approval, or bisync review.

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

- Bundled dependency bootstrap and canonical CLI: `scripts/run.sh`
- Bundled Python CLI: `scripts/sync_home_ai_resources.py`
- Bundled implementation: `scripts/home_syncing.py`
- Bundled bisync engine: `scripts/bisync_skills.py`
- Bundled reference loader: `scripts/home_sync_contract.py`
- Bundled dependency lock: `scripts/requirements.txt`
- Repository dispatcher compatibility path: `.github/scripts/run.sh sync_home_ai_resources ...`

Prefer the bundled runner in this repository and after direct-copy into a home
runtime. The repository dispatcher exists only as a compatibility path and must
delegate to the bundled runner instead of carrying duplicate sync logic.

## Install Sync Contract

The install lane provides unidirectional `repo -> home` materialization of allowlisted resources.

### Install Modes

- `sync`: safe top-level automation that may apply only clean repo-to-home install work before running the bisync review gate.
- `plan`: dry run that produces a readable diff and machine-readable state. Read-only.
- `audit`: compare source, manifest, and managed target paths. Read-only.
- `--fast`: manifest-focused shortcut for `plan` and `audit` only. It must not change `apply` or `sync` source discovery.
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
- `bisync apply`: resolve drift by copying winner to loser. Writes to both repo and home as needed, but only after a reviewed matching `bisync plan` snapshot exists for the same repo and home roots.

### Logic

1. Scan both directories and collect all skill names (union).
2. Exclude bundles whose name starts with `local-`.
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

1. Require a reviewed `last-bisync-plan.json` snapshot that matches the current drift plan for the same repo and home roots.
2. Verify `git status --porcelain --untracked-files=all` on the source repository.
3. Block `apply` if the repository is not clean.
4. Block `apply` if any `only-home` or `equal-mtime` entry exists in the current plan.

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
- Bundle prefix: `local-*` bundles are excluded from bisync scanning and copying.

### Output

The `bisync` payload includes:

- `drifts`: list of drift entries with `skill`, `type`, `direction`, `repo`, `home`.
- `blocked_codes`: list of active blocker codes.
- `next_step`: human-readable next instruction.
- `next_action`: structured object with `action`, `allowed`, `requires_explicit_approval`, `command`, `reason`.
- `verification`: post-apply status with `status` and optional `reason` or `residual_drifts`.
- `bisync-plan-required`: emitted when `bisync apply` is requested without a matching reviewed snapshot.
