---
name: local-agent-sync-install-ai-resources
description: Use when planning, auditing, or applying allowlisted repository-owned AI resources to local Codex, Copilot, or OpenCode runtimes.
---

# Local Agent Sync Home AI Resources

Use this skill as the operating engine for `.github/agents/local-sync-install-ai-resources.agent.md`.
The repository is the only source of truth for managed resources. Home is a
runtime projection: a write through a managed skill link writes the repository
bundle directly.

## Scope

- Repository skill bundles are materialized only as absolute links under
  `~/.agents/skills/`.
- Translated agent resources retain the existing repository-to-home copy path.
- Home-only skills are unmanaged and preserved. This includes catalog-excluded
  `graphify` and every `local-*` bundle.
- Reverse synchronization, reconciliation, and copied-skill fallback are
  forbidden.

## Commands

Use `.github/skills/local-agent-sync-install-ai-resources/scripts/run.sh`.

| Request | Command |
| --- | --- |
| Default repository-to-home sync | `sync --targets skills` |
| Dry review | `plan --targets skills` |
| Explicit materialization | `apply --targets skills` |
| Drift inspection | `audit --targets skills` |
| Readiness check | `doctor --targets skills` |

`dry-run` is an alias for `plan`. The repository dispatcher
`./.github/scripts/run.sh sync_home_ai_resources ...` remains a delegating
compatibility entrypoint.

## Operating Contract

- Keep `~/.agents/skills/` a real directory. Never replace the root with a
  link.
- Create one canonical absolute link for every eligible repository skill.
- A colliding home directory with an eligible repository skill ID is removed
  without backup and replaced by that link.
- A matching unmanaged link is adopted into the manifest without replacement.
- A broken link or a link to another checkout blocks the operation.
- Manifest-v2 stale managed skill links are unlinked automatically; copied
  agents retain explicit `--prune-managed` safety.
- Unsupported symlink capability blocks the operation. Never copy a skill as a
  fallback.
- If the repository checkout moves, rerun sync so links point to the new
  canonical source paths.
- Do not run a real-home command unless the user requested a home change. Use
  a temporary home for tests and acceptance checks.

## Mode Selection

- `sync` may auto-apply clean repository-to-home work. It stops for blockers,
  missing-directory approval, or copied-agent prune gates.
- `plan` and `audit` are read-only.
- `apply` needs an explicit request; `--create-missing-dirs` and
  `--prune-managed` remain explicit.
- `doctor` is read-only and checks roots, support, catalog sources, and state.

## Reporting

Use `--format compact` for automation. Reports must summarize linked skills,
unlinked skills, copied agents, unchanged resources, and blockers. Do not list
all unchanged skills. Translate blocker codes into a plain-language next
action; see `references/error-codes.md`.

## Load On Demand

- Read `references/sync-contract.md` for manifest, planning, path safety, and
  verification details.
- Read `references/error-codes.md` when a blocker or remediation is relevant.
- Read `references/home-sync-catalog.yaml` only when changing discovery policy
  or explicit agent resources.
- Read `references/runtime-support-matrix.yaml` when runtime support decides a
  mode.

## Validation

- Run focused tests under
  `tests/github/skills/local-agent-sync-install-ai-resources/scripts`.
- Run `bash -n .github/skills/local-agent-sync-install-ai-resources/scripts/run.sh .github/scripts/run.sh` after shell entrypoint changes.
- Rebuild `.github/INVENTORY.md` with `./.github/scripts/run.sh build_inventory --root .` after bundle changes.
- Run `./.github/scripts/run.sh check_catalog_consistency --root . --include-token-risks` after bundle or automation changes.
