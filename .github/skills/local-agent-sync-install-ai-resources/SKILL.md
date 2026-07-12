---
name: local-agent-sync-install-ai-resources
description: Use when planning, auditing, or applying repository-owned AI resources or the portable AGENTS.md baseline to local home runtimes.
---

# Local Agent Sync Home AI Resources

## Referenced skills

- None.

Use this skill as the operating engine for `.github/agents/local-sync-install-ai-resources.agent.md`.
The repository is the only source of truth for managed resources. Home is a
runtime projection: a write through a managed skill link writes the repository
bundle directly.

## Scope

- Repository skill bundles are materialized only as absolute links under
  `~/.agents/skills/`.
- Root `AGENTS.md` is projected to `~/.agents/AGENTS.md` as a managed copy with
  the complete `<standards-repository-local-rules>` block removed.
- Copilot agents are absolute links back to `.github/agents/`; Codex and
  OpenCode agents retain their translated copy paths.
- Home-only skills are unmanaged and preserved. This includes catalog-excluded
  `graphify` and every `local-*` bundle.
- Reverse synchronization, reconciliation, and copied-skill fallback are
  forbidden.

## Commands

Use `.github/skills/local-agent-sync-install-ai-resources/scripts/run.sh`.

| Request | Command |
| --- | --- |
| Update the global `AGENTS.md` baseline | `sync --targets agents.md` |
| Default repository-to-home sync | `sync --targets skills` |
| Dry review | `plan --targets skills` |
| Explicit materialization | `apply --targets skills` |
| Drift inspection | `audit --targets skills` |
| Readiness check | `doctor --targets skills` |

`dry-run` is an alias for `plan`. The repository dispatcher
`./.github/scripts/run.sh sync_home_ai_resources ...` remains a delegating
compatibility entrypoint.

When the user calls this skill with an `agents.md` request, `agents.md` means `sync --targets agents.md`.
Accept `agents-md` as a CLI alias for the same target.

## Operating Contract

- Keep `~/.agents/skills/` a real directory. Never replace the root with a
  link.
- Treat repository root `AGENTS.md` as the only source of truth for the managed
  `~/.agents/AGENTS.md` projection. Adopt and overwrite an unmanaged target
  file, but never include `<standards-repository-local-rules>` in the result.
- Keep `~/.copilot/agents/` a real directory. Never replace the root with a
  link.
- Create one canonical absolute link for every eligible repository skill.
- Create one canonical absolute link for every eligible Copilot agent.
- Migrate a manifest-managed unchanged Copilot copy to its canonical link;
  block unmanaged or locally modified copies.
- A colliding home directory with an eligible repository skill ID is removed
  without backup and replaced by that link.
- A matching unmanaged link is adopted into the manifest without replacement.
- A broken link or a link to another checkout blocks the operation.
- Manifest-v2 stale managed links are unlinked automatically; copied translated
  agents retain explicit `--prune-managed` safety.
- Unsupported symlink capability blocks the operation. Never copy a skill as a
  fallback.
- If the repository checkout moves, rerun sync so links point to the new
  canonical source paths.
- Do not run a real-home command unless the user requested a home change. Use
  a temporary home for tests and acceptance checks.

## Mode Selection

- `sync` may auto-apply clean repository-to-home work, including `agents.md`.
  It stops for blockers,
  missing-directory approval, or copied-agent prune gates.
- `plan` and `audit` are read-only.
- `apply` needs an explicit request; `--create-missing-dirs` and
  `--prune-managed` remain explicit.
- `doctor` is read-only and checks roots, support, catalog sources, and state.

## Reporting

Use `--format compact` for automation. Reports must summarize linked resources,
unlinked resources, copied translated agents, unchanged resources, and blockers. Do not list
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
