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

## When not to use

- Source-side catalog governance in this repository; use `local-sync-external-resources` instead.
- Consumer-repository baseline sync; use `local-sync-global-copilot-configs-into-repo` instead.
- Personal configuration merge, runtime adapter generation, or general dotfiles management.
- Undocumented runtime families outside the allowlisted direct-copy skills and translated agents for Claude, OpenCode, and Codex.

## Core Operating Contract

- Treat this repository as the source of truth for allowlisted home-sync resources.
- Sync is unidirectional: repo → home only. Block any attempt to sync from home to repo.
- Default to `plan` and keep `apply` explicit.
- Limit v1 default materialization to documented direct-copy skill families and allowlisted agent translations for Codex, Claude, and OpenCode.
- Preserve unmanaged target-local files and directories.
- Prune only stale managed assets, and only when explicit approval is present and the manifest entry passes schema validation, path confinement, and content-hash drift checks.
- Keep local sync state under `~/.sync/cloud-strategy-governance/home-ai-resources/`.
- Block `apply` when runtime support is undocumented, target paths are unsafe, or ownership evidence is missing.
- Keep runtime support evidence explicit through the paired references instead of inferring undocumented home paths.

## Output Expectations

- Selected mode, selected targets, and why that mode is valid.
- Source resources considered and the runtime support evidence used.
- Missing directories, conflicts, or documentation gates that block `apply`.
- Managed versus preserved target-local outcomes and any approved prune behavior.
- Validation results, remaining blockers, and explicit validation gaps.

## Mode Selection

- `plan`: produce a readable dry run and machine-readable state.
- `audit`: compare source, manifest, and managed target paths without writing runtime files.
- `doctor`: verify runtime roots, permissions, symlink posture, manifest health, and support-matrix readiness.
- `apply`: explicit only. Materialize only approved and safe operations.
- `dry-run`: alias of `plan`, not a separate behavior.
- `bisync`: bidirectional sync between `.github/skills/` and `~/.agents/skills/` using mtime resolution. Use `bisync plan` to detect drift and `bisync apply` to resolve it.

## Default Sync Sequence

When the user says "sync" without specifying a mode, follow this sequence in order:

1. **bisync plan** — detect mtime drift between `.github/skills/` and `~/.agents/skills/`. Resolve any `only-repo` or `only-home` drift before continuing.
2. **plan** — produce the full sync plan for all targets. Surface blocked paths early.
3. **audit** — if plan shows blocked paths, run audit to diagnose the exact conflicts.
4. **Resolve blockers** — remove or reconcile conflicting home files before attempting apply. `apply` refuses to run when any `blocked_codes` exist.
5. **apply** — only on explicit user request, only after zero blockers remain.

Do not skip bisync. Do not attempt apply without first confirming zero blockers via plan or audit.

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
- Exclude runtime-generated bundle artifacts such as `.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, and `.pyo` from hashes and copies.

## Bundled Automation

- Prefer `scripts/sync_home_ai_resources.py` for deterministic `plan`, `audit`, `doctor`, and `apply` behavior.
- Use `scripts/run.sh` when a portable skill-local environment is needed; it installs the locked `PyYAML` dependency from `scripts/requirements.txt`.
- In this source repository, `.github/scripts/sync_home_ai_resources.py` and `.github/scripts/sync_home_ai_resources.sh` are thin wrappers around the bundled skill script.
- Keep library behavior inside `scripts/home_syncing.py` and reference loading inside `scripts/home_sync_contract.py`.

## Safety Gates

- Block unmanaged overwrite.
- Block managed overwrite when the target content diverged from the last recorded manifest.
- Block stale managed delete when the manifest entry is invalid, escapes the expected runtime root, or the file content drifted from the recorded hash.
- Block unsafe home paths, unsupported symlink hops, missing target roots without explicit create approval, and undocumented runtime claims.
- Keep the canonical error taxonomy in `references/error-codes.md`.
- Keep the doctor checklist in `references/doctor-checks.md`.

## Conflict Resolution

When plan or audit reports blocked paths, resolve them before apply:

- `target-exists-unmanaged`: the target file or directory exists at home but is not in the sync manifest. Remove it manually so sync can recreate it from source.
- `target-modified-managed`: the target is in the manifest but its content diverged from the last recorded hash. Remove it manually so sync can restore the source-of-truth version.
- After removing conflicting files, re-run plan to confirm zero blockers before applying.

## Load On Demand

- Read `references/runtime-support-matrix.md` when the runtime family or support level decides the mode.
- Read `references/sync-contract.md` for state files, manifest fields, materialization rules, and reporting requirements.
- Read `references/error-codes.md` when the correct blocking code or remediation must be surfaced.
- Read `references/doctor-checks.md` when readiness validation or local remediation steps matter.

## Validation

- Rebuild `.github/INVENTORY.md` when the bundle or related scripts change by using `./.github/scripts/build_inventory.sh --root .`.
- Run `./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks` after bundle or automation changes.
- Run `bash -n .github/skills/local-agent-sync-install-ai-resources/scripts/run.sh .github/scripts/sync_home_ai_resources.sh` after shell wrapper changes.
- Run focused agent or skill contract tests for the touched bundle.
- Run focused sync tests for target parsing, support-matrix policy, manifest handling, overwrite gates, and missing-directory behavior when automation changes.
