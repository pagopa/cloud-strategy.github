---
name: local-agent-sync-home-ai-resources
description: Use when planning, auditing, or applying allowlisted home-directory sync of repository-owned AI runtime resources to local Codex, Copilot, Claude Code, or OpenCode targets.
---

# Local Agent Sync Home AI Resources

## Referenced skills

- None.

Use this skill as the operating engine for `.github/agents/local-sync-home-ai-resources.agent.md`.

Keep the paired agent short. Keep route, boundary, approval posture, and output expectations in the agent. Keep reusable sync workflow, target policy, safety gates, and reporting posture here. Keep detailed tables and checklists in `references/`. Keep deterministic execution helpers in `scripts/` so the skill remains portable as a direct-copy bundle.

## When to use

- Plan a local home-directory sync for supported AI runtime resources.
- Audit drift between repository-managed resources and the local runtime copies under the user home directory.
- Run readiness or doctor checks before touching runtime-owned directories.
- Apply an already reviewed plan for supported direct-copy resource families.

## When not to use

- Source-side catalog governance in this repository; use `local-sync-external-resources` instead.
- Consumer-repository baseline sync; use `local-sync-global-copilot-configs-into-repo` instead.
- Personal configuration merge, runtime adapter generation, or general dotfiles management.
- Undocumented runtime families that would require format translation in v1.

## Core Operating Contract

- Treat this repository as the source of truth for allowlisted home-sync resources.
- Sync is unidirectional: repo → home only. Block any attempt to sync from home to repo.
- Default to `plan` and keep `apply` explicit.
- Limit v1 default materialization to documented direct-copy resource families.
- Preserve unmanaged target-local files and directories.
- Prune only stale managed assets, and only when explicit approval is present.
- Keep local sync state under `~/.sync/cloud-strategy-governance/home-ai-resources/`.
- Block `apply` when runtime support is undocumented, target paths are unsafe, or ownership evidence is missing.

## Mode Selection

- `plan`: default mode. Produce a readable dry run and machine-readable state.
- `audit`: compare source, manifest, and managed target paths without writing runtime files.
- `doctor`: verify runtime roots, permissions, symlink posture, manifest health, and support-matrix readiness.
- `apply`: explicit only. Materialize only approved and safe operations.
- `dry-run`: alias of `plan`, not a separate behavior.

## Target Selection

- Accept `codex`, `copilot`, `claude`, `opencode`, comma-separated combinations, `cross`, `all`, or `tutto`.
- Normalize whitespace, deduplicate, and order targets deterministically.
- Resolve skill roots as `~/.agents/skills` for all targets (scenario B: unification).
- When multiple targets resolve to the same physical path, perform the copy operation only once (physical deduplication).
- After apply, verify every copied resource by re-reading the target and comparing hashes.
- Block reverse sync: source root must not be under home root.

## Source And Materialization Policy

- Read the runtime contract from `references/runtime-support-matrix.yaml` and the readable summary in `references/runtime-support-matrix.md`.
- Read the source allowlist from `references/home-sync-catalog.yaml`.
- Include only allowlisted `skills` in v1.
- Copy managed resources instead of creating symlinks.
- Preserve target-local content that is outside the manifest.
- Record source hashes and managed target paths in the local manifest.
- Exclude runtime-generated bundle artifacts such as `.venv`, `__pycache__`, `.pytest_cache`, `.pyc`, and `.pyo` from hashes and copies.

## Bundled Automation

- Prefer `scripts/sync_home_ai_resources.py` for deterministic `plan`, `audit`, `doctor`, and `apply` behavior.
- Use `scripts/run.sh` when a portable skill-local environment is needed; it installs the locked `PyYAML` dependency from `scripts/requirements.txt`.
- In this source repository, `.github/scripts/sync_home_ai_resources.py` and `.github/scripts/sync_home_ai_resources.sh` are thin wrappers around the bundled skill script.
- Keep library behavior inside `scripts/home_syncing.py` and reference loading inside `scripts/home_sync_contract.py`.

## Safety Gates

- Block unmanaged overwrite.
- Block managed overwrite when the target content diverged from the last recorded manifest.
- Block unsafe home paths, unsupported symlink hops, missing target roots without explicit create approval, and undocumented runtime claims.
- Keep the canonical error taxonomy in `references/error-codes.md`.
- Keep the doctor checklist in `references/doctor-checks.md`.

## Load On Demand

- Read `references/runtime-support-matrix.md` when the runtime family or support level decides the mode.
- Read `references/sync-contract.md` for state files, manifest fields, materialization rules, and reporting requirements.
- Read `references/error-codes.md` when the correct blocking code or remediation must be surfaced.
- Read `references/doctor-checks.md` when readiness validation or local remediation steps matter.

## Validation

- Rebuild `.github/INVENTORY.md` when the bundle or related scripts change by using `./.github/scripts/build_inventory.sh --root .`.
- Run `./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks` after bundle or automation changes.
- Run `bash -n .github/skills/local-agent-sync-home-ai-resources/scripts/run.sh .github/scripts/sync_home_ai_resources.sh` after shell wrapper changes.
- Run focused agent or skill contract tests for the touched bundle.
- Run focused sync tests for target parsing, support-matrix policy, manifest handling, overwrite gates, and missing-directory behavior when automation changes.
