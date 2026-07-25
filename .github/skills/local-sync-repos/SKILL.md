---
name: local-sync-repos
description: Use when aligning a consumer repository to this repository's managed instruction, root-policy, and shared-hygiene baseline while preserving target local-* assets.
---

# Local Sync Repos

## Referenced skills

- None.

Use this skill as the mandatory operating engine for `.github/agents/local-sync-repos.agent.md`.

## Scope

Manage only these exact target paths:

- `AGENTS.md`
- `.python-version`
- `.pre-commit-config.yaml`
- `.editorconfig`
- `.github/copilot-instructions.md`
- `.github/workflows/_pre-commit.yml`
- `.github/instructions/**` (source-authoritative; preserve target `local-*` filenames)
- `AGENTS.local.md` (create-once from template; never overwrite or delete)

Do not synchronize agents, skills, prompts, inventory, documentation, lesson ledgers, VS Code settings, or unrelated workflows.

## Commands

```bash
python3 .github/skills/local-sync-repos/scripts/sync_repos.py plan --source-root . --target-repo <path> --format compact
python3 .github/skills/local-sync-repos/scripts/sync_repos.py apply --source-root . --target-repo <path> --format compact
```

- `plan` is the default safe mode. It writes only `tmp/local-sync-repos.plan.md` in the target.
- `apply` requires an existing matching plan fingerprint and blocks on dirty managed overlap or stale plans.

## Safety Contract

- Mirror source-managed files exactly.
- Preserve target `.github/instructions/**/local-*` files byte-identical.
- Delete target-only non-local instruction files only during an explicitly requested `apply`.
- Create `AGENTS.local.md` only when missing and never overwrite or delete an existing target copy.
- Block `apply` when a dirty target path overlaps a planned managed mutation.
- Block `apply` when the saved plan fingerprint does not match the current plan.
- Do not expose `--force`, `--allow-dirty-target`, or broader category selectors.
- Do not include commit or push steps; repository history remains user-owned.

## Load On Demand

- Read `references/sync-contract.md` for exact path ownership, action semantics, error codes, and convergence criteria.

## Validation

- Focused pytest: `python3.13 -m pytest tests/github/skills/local-sync-repos -q`
- Strict skill validation: `python3.13 ./.github/scripts/validate_internal_skills.py --skill local-sync-repos --strict`
- Catalog consistency: `python3.13 ./.github/scripts/check_catalog_consistency.py --root . --include-token-risks`
