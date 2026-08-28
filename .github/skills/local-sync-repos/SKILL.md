---
name: local-sync-repos
description: Use when aligning a consumer repository to this repository's managed instruction, root-policy, shared-hygiene, and workspace Copilot approval baseline while preserving target local-* assets.
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
- `.vscode/settings.json`
- `.github/copilot-instructions.md`
- `.github/workflows/_pre-commit.yml`
- `.github/workflows/_pr-title.yml`
- `.github/instructions/**` (source-authoritative; preserve target `local-*` filenames)
- `AGENTS.local.md` (create-once header-only seed from template; never overwrite or delete)

Do not synchronize agents, skills, prompts, inventory, documentation, lesson ledgers, or unrelated workflows.

## Copilot approval posture

- `.vscode/settings.json` is a source-managed workspace profile. It carries the requested `chat.permissions.default` and approval settings as exact JSON values.
- `Agent` is the general-purpose agent role that can reason and invoke enabled tools; it is not an approval policy.
- `Default Approvals` uses the configured approval rules and pauses for tool confirmation or clarification when needed.
- `Bypass Approvals` auto-approves tool calls but still asks clarifying questions.
- `Autopilot` is an agent mode, not a permission level. It auto-approves tools, retries errors, and can auto-respond to questions, so it must not be selected when a human decision is required.
- `chat.agent.maxRequests` only limits the number of agent-loop iterations/requests; it does not disable automatic answers or make the agent wait for the user.
- Workspace settings apply only to this repository. To apply the same posture to every workspace, copy the profile into VS Code User Settings (JSON); repository sync never edits the user's home settings.
- Approval settings govern tool execution, not every generated sentence. A workflow that must stop after a decision question also needs an active instruction or agent contract that requires waiting for the user's reply.
- When this workflow needs a user decision, ask one explicit question and stop; do not invent a default, continue, edit files, or run commands until the user replies.

## Commands

```bash
python3 scripts/sync_repos.py plan --source-root . --target-repo <path> --format compact
python3 scripts/sync_repos.py apply --source-root . --target-repo <path> --format compact
```

- `plan` is the default safe mode. It writes only `tmp/local-sync-repos.plan.md` in the target.
- `apply` requires an existing matching plan fingerprint and blocks on dirty managed overlap or stale plans.

## Safety Contract

- Mirror source-managed files exactly.
- Preserve target `.github/instructions/**/local-*` files byte-identical.
- Delete target-only non-local instruction files only during an explicitly requested `apply`.
- Create a header-only `AGENTS.local.md` only when missing and never overwrite or delete an existing target copy.
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
