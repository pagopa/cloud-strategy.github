---
name: local-agent-sync-global-copilot-configs-into-repo
description: Use when aligning a consumer repository to this repository's managed GitHub Copilot baseline, shared repository-hygiene files, and retained-learning ledger template.
---

# Internal Agent Sync Global Copilot Configs Into Repo

## Referenced skills

- None.

Use this skill as the mandatory operating engine for `.github/agents/local-sync-global-copilot-configs-into-repo.agent.md`.

This skill owns the reusable sync procedure. Keep the paired agent short; do not duplicate the analyze, plan, apply, reporting, or automation rules there.

The paired agent should not restate default mode handling, preserved `local-*` behavior, `internal-sync-*` exclusions, plan-file lifecycle, or automation entrypoints from this skill.

## When to use

- Align a consumer repository with the managed GitHub Copilot baseline from this repository.
- Refresh target `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md` to the current root-policy and review-only model after mirroring.
- Refresh shared repository-hygiene files that are part of the managed sync baseline, currently `.editorconfig`, `.pre-commit-config.yaml`, `.github/workflows/_pre-commit.yml`, `.github/copilot-commit-message-instructions.md`, `.github/security-baseline.md`, `.github/DEPRECATION.md`, and `.github/repo-profiles.yml`.
- Refresh repository-root `LESSONS_LEARNED.md` from the source structure while preserving and, when needed, migrating target-authored pending lesson rows.
- Run or interpret `./.github/scripts/run.sh sync_copilot_catalog` or `.github/scripts/sync_copilot_catalog.py`.
- Audit source-target drift before or after a sync.

## Core Operating Contract

- Treat this repository as the source of truth.
- Keep target assumptions narrow: GitHub Copilot assets live under `.github/` and `AGENTS.md` stays at repository root.
- Preserve target `local-*` assets under mirrored categories and delete target-only non-local assets there during `apply`.
- When consumer-local creator bundles depend on shared runtime-critical rules, mirror those rules inside each creator bundle as source-managed files and keep the mirror paths registered in the source inventory and target manifest; do not rely on cross-bundle references or unsynced local-only resources for creator runtime behavior.
- When the source baseline includes an approved imported-asset override registry plus replay patches, mirror that governance bundle as source-managed state instead of recreating target-local hidden forks on imported assets.
- Exclude source resources named `internal-sync-*` from consumer mirroring and remove any target copies of those resources during `apply`.
- Create consumer-local `docs/README.md`, `docs/repository-context.md`, `docs/architecture.md`, `docs/tech.md`, and `docs/structure.md` from `.github/templates/` only when missing, then preserve target-authored content on later sync runs.
- Delete retired standalone runtime operating model documents from consumers; runtime workflow guidance now travels through root guidance and skills.
- Keep root guidance layered: `AGENTS.md` is the agent policy entrypoint, `.github/copilot-instructions.md` is review-only for GitHub.com Copilot code review, and `.github/INVENTORY.md` is the live catalog.
- Treat `LESSONS_LEARNED.md` as a source-managed retained-learning template: create it when missing, keep its structure aligned with the source contract, and preserve target-authored pending lessons instead of overwriting them with source rows.
- Mirror only the explicitly shared repository-hygiene files declared in `references/sync-contract.md`; do not widen workflow or root-file mirroring implicitly.
- Ensure the target repository `.gitignore` contains an ignore rule for `tmp/superpowers/`.
- Treat `.vscode/settings.json` as consumer-owned JSONC and manage only the Copilot settings required to disable instruction-file loading.
- When moving from `plan` to `apply` against the same target, pass `--allow-dirty-target` only when the generated `tmp/copilot-sync.plan.md` is the sole target diff left by the planning run.
- Prefer the bundled sync automation when it matches the requested mode instead of re-deriving the workflow manually.
- Keep detailed operating rules in `references/sync-contract.md` instead of re-expanding them in the agent body.

## Default Workflow

1. Analyze the source baseline, target catalog, target git state, and preserved local assets.
2. Write `tmp/copilot-sync.plan.md` in the target repository with the pending operations and any manual follow-up that remains outside automation.
3. In `apply`, mirror source-managed assets, merge target `LESSONS_LEARNED.md` rows into the current source structure, rebuild the target inventory, write the target manifest, and clear the tracking plan when nothing remains pending.
4. Re-run the closest existing validation and report any blockers or gaps.

## Mode Selection

- `plan`: default mode and safest starting point.
- `apply`: explicit only, after reviewing a conflict-safe plan and current source findings.
- `audit`: use when source or target drift needs diagnosis before deciding whether to plan or apply; prefer `./.github/scripts/run.sh audit_copilot_catalog` plus the sync planner evidence instead of inventing a third sync mode.

## Agent-facing output modes

- For model-facing runs, prefer bounded output over full detail when the script supports it.
- Use `python3 ./.github/scripts/sync_copilot_catalog.py plan --target-repo <repo> --format compact` for planner runs, and summarize only status, blockers, warnings, managed mutation counts, and next action in agent responses.
- Use `python3 ./.github/scripts/sync_copilot_catalog.py apply --target-repo <repo> --format compact` only after explicit approval, and keep apply reporting bounded to blockers, warnings, changed path evidence, validation status, and next action.
- Reserve full `--format json` output for durable artifacts, audits, debugging, or explicit user request.
- For validator and consistency commands that do not support compact, keep output bounded by using the narrowest target scope and report concise summaries instead of raw log dumps.

## Evidence Budget

Collect the minimum evidence set before moving past analysis or approving `apply`:

- selected mode: `plan`, `apply`, or `audit`
- target git state, including planner-reported relevant `dirty_paths`
- planner output, from `tmp/copilot-sync.plan.md`, JSON output, or both
- preserved target-owned assets covered by the sync contract, including `local-*` assets and consumer-local knowledge documents
- planner-reported `managed_mutation_paths` plus any `dirty_managed_overlap`
- latest validation result for the touched sync behavior

Keep manual inspection narrow. Review only:

- paths whose planned action is `create`, `update`, `ensure`, `rebuild`, or `delete`
- dirty paths that overlap planned managed mutations

If `dirty_managed_overlap` is empty, `--allow-dirty-target` can stay eligible when the other gates are green. If overlap is non-empty, reconcile those paths first or require explicit approval before `apply`.

## Load On Demand

- Read `references/sync-contract.md` for exact mirrored categories, exclusions, root-guidance ownership, plan-file lifecycle, automation entrypoints, validation sequence, and reporting requirements.

## Validation

- For source-side baseline changes, prefer `./.github/scripts/run.sh check_catalog_consistency --root . --include-token-risks`.
- Rebuild `.github/INVENTORY.md` when touched catalog paths require it by using `./.github/scripts/run.sh build_inventory --root .`.
- For sync automation changes, run `pytest tests/test_sync_and_token_risks.py`.
- If a dedicated sync-contract test does not exist for the touched behavior, say so explicitly and use the closest existing verification.
