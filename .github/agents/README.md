# Agents Catalog

This folder contains repository-owned Copilot custom agents.

## Active Agents

| Agent | Use when |
| --- | --- |
| `internal-gateway-critical-master` | Any plan, proposal, decision, design, workflow, requirement, or assumption set needs an adaptive critical challenge. |
| `internal-luna-executor` | Another agent assigns work that must run with Luna; install the native profiles under `~/.copilot/agents/` and `~/.codex/agents/` to expose it in both runtimes. |
| `local-sync-external-resources` | Declared external-resource refreshes need preparation, audit, planning, or application. |
| `local-sync-install-ai-resources` | Repository-owned AI resources or the portable `AGENTS.md` baseline need local-home synchronization. |
| `local-sync-repos` | Consumer repositories need managed baseline alignment or drift assessment. |

## Validation

Run `make github-catalog-validation` for the repository-owned GitHub catalog
validation.

No diagram is provided because this README lists agent entrypoints and use
conditions without a material relationship that needs a diagram.
