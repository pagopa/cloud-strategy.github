name: internal-agent-sync-global-copilot-configs-into-repo
description: Mirror the managed GitHub Copilot baseline into consumer repositories with source-authoritative mirroring, `local-*` preservation, root-guidance alignment, retained plan tracking, and script-backed plan or apply automation.
---

# Internal Agent Sync Global Copilot Configs Into Repo

Use this skill as the mandatory operating engine for `.github/agents/internal-sync-global-copilot-configs-into-repo.agent.md`.

This skill owns the reusable sync procedure. Keep the paired agent short; do not duplicate the analyze, plan, apply, reporting, or automation rules there.

The paired agent should not restate default mode handling, preserved `local-*` behavior, `internal-sync-*` exclusions, plan-file lifecycle, or automation entrypoints from this skill.

## When to use

- Align a consumer repository with the managed GitHub Copilot baseline from this repository.
- Refresh target `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md` to the current bridge model after mirroring.
- Run or interpret `.github/scripts/sync_copilot_catalog.sh` or `.github/scripts/sync_copilot_catalog.py`.
- Audit source-target drift before or after a sync.

## Core Operating Contract

- Treat this repository as the source of truth.
- Keep target assumptions narrow: GitHub Copilot assets live under `.github/` and `AGENTS.md` stays at repository root.
- Preserve target `local-*` assets under mirrored categories and delete target-only non-local assets there during `apply`.
- Exclude source resources named `internal-sync-*` from consumer mirroring and remove any target copies of those resources during `apply`.
- Keep root guidance layered: `AGENTS.md` is the bridge, `.github/copilot-instructions.md` is the repo-wide projection, and `.github/INVENTORY.md` is the live catalog.
- Ensure the target repository `.gitignore` contains an ignore rule for `docs/superpowers/`.
- Prefer the bundled sync automation when it matches the requested mode instead of re-deriving the workflow manually.
- Keep detailed operating rules in `references/sync-contract.md` instead of re-expanding them in the agent body.

## Default Workflow

1. Analyze the source baseline, target catalog, target git state, and preserved local assets.
2. Write `tmp/copilot-sync.plan.md` in the target repository with the pending operations and any manual follow-up that remains outside automation.
3. In `apply`, mirror source-managed assets, rebuild the target inventory, write the target manifest, and clear the tracking plan when nothing remains pending.
4. Re-run the closest existing validation and report any blockers or gaps.

## Mode Selection

- `plan`: default mode and safest starting point.
- `apply`: explicit only, after reviewing a conflict-safe plan and current source findings.
- `audit`: use when source or target drift needs diagnosis before deciding whether to plan or apply.

## Load On Demand

- Read `references/sync-contract.md` for exact mirrored categories, exclusions, root-guidance ownership, plan-file lifecycle, automation entrypoints, validation sequence, and reporting requirements.

## Validation

- For source-side baseline changes, prefer `./.github/scripts/check_catalog_consistency.sh --root . --include-token-risks`.
- Rebuild `.github/INVENTORY.md` when touched catalog paths require it by using `./.github/scripts/build_inventory.sh --root .`.
- For sync automation changes, run `pytest tests/test_sync_and_token_risks.py`.
- If a dedicated sync-contract test does not exist for the touched behavior, say so explicitly and use the closest existing verification.
