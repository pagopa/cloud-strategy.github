# AI Architecture Contract v1.1.0

> Purpose: defines the repository-specific architecture contract for this repository's AI governance supply chain.
> Keep component boundaries, system scope, validation surfaces, and runtime fit here when they describe this
> repository's actual architecture.

## Where Adjacent Content Belongs

- Use `docs/02-repository-context.md` for stable local operating context, glossary, ownership notes,
  and repository-specific interpretation aids.
  These aids must not override policy.
- Use `docs/03-ai-runtime-operating-model.md` for the shared runtime model.
  It explains how Codex, Copilot, ChatGPT, and other runtimes consume the AI customization surfaces.
- Use `AGENTS.md`, `.github/copilot-instructions.md`, or scoped `.github/instructions/*.instructions.md`
  for binding instruction policy.
- Use `LESSONS_LEARNED.md` only for durable lessons that are pending codification elsewhere.

## Repository

`cloud-strategy.github` is the source-of-truth repository for GitHub Copilot customization, repository instruction
architecture, catalog governance, and sync tooling used by the cloud strategy workspace.

## Purpose

The repository does not host a product runtime. It hosts an AI governance supply chain: repository-owned skills,
Copilot wrapper agents, instructions, prompts, inventory, validation scripts, and sync contracts. These assets are
authored here, then validated or projected into consumer repositories.

## System Boundaries

In scope:

- Repository-wide AI governance policy in `AGENTS.md` and `.github/copilot-instructions.md`.
- Repo-specific architecture and context documents in `docs/01-architecture.md` and `docs/02-repository-context.md`.
- Shared AI runtime operating model in `docs/03-ai-runtime-operating-model.md`.
- Live resource inventory in `.github/INVENTORY.md`.
- Agent, skill, instruction, prompt, template, and sync assets under `.github/`.
- Catalog validation and synchronization scripts under `.github/scripts/`.
- Contract and regression tests under `tests/`.
- Supporting documentation in `INTERNAL_CONTRACT.md`.

Out of scope:

- Cloud workload deployment ownership for consumer repositories.
- Consumer-local exceptions after they are materialized in target repositories.
- Product runtime operations.

## Main Components

| Component | Path | Responsibility |
| --- | --- | --- |
| Strategic bridge | `AGENTS.md` | Rule placement, precedence model, ownership prefixes, volatile artifact policy, and retained-artifact boundaries. |
| Copilot projection | `.github/copilot-instructions.md` | Repo-wide behavior visible to native Copilot flows. |
| Architecture contract | `docs/01-architecture.md` | Repo-specific architecture, boundaries, flows, and validation surface. |
| Repository context | `docs/02-repository-context.md` | Stable local context, glossary, and non-policy interpretation aids. |
| Runtime operating model | `docs/03-ai-runtime-operating-model.md` | Shared source-managed runtime consumption model for AI customization assets. |
| Catalog inventory | `.github/INVENTORY.md` | Generated catalog surface for agents, skills, instructions, prompts, and related assets. |
| Consumer-local scaffolds | `.github/templates/` | Source-side templates used by sync automation to create target-owned knowledge files and override layers. |
| Copilot wrapper agents | `.github/agents/` | VS Code route selection, tool scope, and manual handoff UX for operational skills plus repo-only sync command centers. |
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
  -> consumer repositories with local architecture/context scaffolds and optional local override layer
```

The key invariant is separation of policy, projection, inventory, local context, and runtime guidance.
`AGENTS.md` owns stable strategy. `.github/copilot-instructions.md` owns the Copilot projection.
`.github/INVENTORY.md` owns the volatile generated catalog. `docs/01-architecture.md` and
`docs/02-repository-context.md` remain repo-specific. `docs/03-ai-runtime-operating-model.md` is the
source-managed runtime model.

## Validation Surface

Observed validation entrypoints include:

- `Makefile` targets for `catalog-lint`, `github-catalog-validation`, `catalog-check`, `catalog-audit`,
  `inventory-build`, `token-risks`, `skill-lint`, `docs-lint`, and `test`.
- Workflows `_code-analysis.yml`, `_github-catalog-validation.yml`, and `_pre-commit.yml`.
- Python tests under `tests/`, including catalog, plan-policy, agent-contract, script-entrypoint, sync,
  and imported-asset override coverage.

## Operational Notes

- Treat this repository as the canonical source for shared Copilot governance.
- Do not use consumer repositories to redefine `internal-*`, `local-*`, or `internal-sync-*`.
- Do not hand-maintain catalog matrices beside `.github/INVENTORY.md` unless they are generated and validated.
- Keep transient planning artifacts under `tmp/superpowers/`, not under `docs/`.
- Scaffold consumer-local knowledge documents from templates, then preserve them after initial creation.

## Risks And Open Questions

| Risk | Current evidence | Recommended handling |
| --- | --- | --- |
| Catalog drift | Sync and inventory scripts exist, plus tests, but catalog families evolve over time. | Keep inventory generation, sync discovery, and validators updated in the same change. |
| Overloaded always-on guidance | Multiple projections and scoped resources exist. | Keep high-volume detail in skills or references, not repo-wide instructions or wrapper agents. |
| Consumer override ambiguity | Local override layer exists by contract. | Require explicit override scope, reason, and disclosure when followed. |
| Knowledge document shadow policy | `docs/02-repository-context.md` can look instruction-like if unconstrained. | Keep it descriptive and move binding behavior to canonical instruction surfaces. |

## Contract Status

This repository is ready to serve as the control-plane reference for AI Architecture Contract v1.1.0. Future changes
should preserve the policy/projection/inventory/context/runtime split. They should also keep validation tied to the
actual filesystem.
