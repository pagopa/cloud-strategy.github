# AI Architecture Contract v1.1.0

## Repository

`cloud-strategy.github` is the source-of-truth repository for GitHub Copilot customization, repository instruction architecture, catalog governance, and sync tooling used by the cloud strategy workspace.

## Purpose

The repository does not host a product runtime. Its primary system is an AI governance supply chain: repository-owned skills, Copilot wrapper agents, instructions, prompts, inventory, validation scripts, and sync contracts are authored here and then validated or projected into consumer repositories.

## System Boundaries

In scope:

- Repository-wide AI governance policy in `AGENTS.md` and `.github/copilot-instructions.md`.
- Live resource inventory in `.github/INVENTORY.md`.
- Agent, skill, instruction, and prompt assets under `.github/`.
- Catalog validation and synchronization scripts under `.github/scripts/`.
- Contract and regression tests under `tests/`.
- Supporting documentation in `INTERNAL_CONTRACT.md` and `docs/runtime-fit.md`.

Out of scope:

- Cloud workload deployment ownership for consumer repositories.
- Consumer-local exceptions after they are materialized in target repositories.
- Product runtime operations.

## Main Components

| Component | Path | Responsibility |
| --- | --- | --- |
| Strategic bridge | `AGENTS.md` | Precedence model, ownership prefixes, volatile artifact policy, and retained-learning boundary. |
| Copilot projection | `.github/copilot-instructions.md` | Repo-wide behavior visible to native Copilot flows. |
| Catalog inventory | `.github/INVENTORY.md` | Generated catalog surface for agents, skills, instructions, prompts, and related assets. |
| Copilot wrapper agents | `.github/agents/` | VS Code route selection, tool scope, and manual handoff UX for the operational skills plus repo-only sync command centers. |
| Reusable skills | `.github/skills/` | Skill-first operational core, on-demand workflows, references, validation guidance, and sync support depth. |
| Scoped instructions | `.github/instructions/` | Path or domain-specific authoring rules. |
| Automation scripts | `.github/scripts/` | Inventory build, catalog consistency, token-risk detection, skill validation, and sync planning. |
| Regression tests | `tests/` | Contract checks for agents, inventory, imported assets, plan policy, scripts, and completion reports. |

## Architecture Flow

```text
Repository-owned AI assets
  -> skill-first operational core and Copilot wrapper projections
  -> inventory and consistency builders
  -> validation tests and Makefile targets
  -> sync planning and consumer projection
  -> consumer repositories with optional local override layer
```

The key invariant is separation of policy, projection, and inventory. `AGENTS.md` owns stable strategy, `.github/copilot-instructions.md` owns the Copilot projection, and `.github/INVENTORY.md` owns the volatile generated catalog.

## Validation Surface

Observed validation entrypoints include:

- `Makefile` targets for `catalog-lint`, `github-catalog-validation`, `catalog-check`, `catalog-audit`, `inventory-build`, `token-risks`, `skill-lint`, `docs-lint`, and `test`.
- Workflows `_code-analysis.yml`, `_github-catalog-validation.yml`, and `_pre-commit.yml`.
- Python tests under `tests/`, including catalog, plan-policy, agent-contract, script-entrypoint, and imported-asset override coverage.

## Operational Notes

- Treat this repository as the canonical source for shared Copilot governance.
- Do not use consumer repositories to redefine the meaning of `internal-*`, `local-*`, or `internal-sync-*`.
- Do not hand-maintain catalog matrices beside `.github/INVENTORY.md` unless generated and validated.
- Keep transient planning artifacts under `tmp/superpowers/`, not `docs/`.

## Risks And Open Questions

| Risk | Current evidence | Recommended handling |
| --- | --- | --- |
| Catalog drift | Sync and inventory scripts exist, plus tests, but catalog families evolve over time. | Keep inventory generation, sync discovery, and validators updated in the same change. |
| Overloaded always-on guidance | Multiple projections and scoped resources exist. | Keep high-volume detail in skills or references, not repo-wide instructions or wrapper agents. |
| Consumer override ambiguity | Local override layer exists by contract. | Require explicit override scope, reason, and disclosure when followed. |

## Contract Status

This repository is ready to serve as the control-plane reference for AI Architecture Contract v1.1.0. Future changes should preserve the policy/projection/inventory split and keep validation tied to the actual filesystem.
