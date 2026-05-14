# Repository Context

> Purpose: stable local context for this repository's AI governance work. Keep operational facts, glossary entries, ownership notes, and durable interpretation aids here when they help humans and agents understand the repository but do not create binding policy.

## Where Adjacent Content Belongs

- Use `docs/01-architecture.md` for system boundaries, component responsibilities, architecture flow, and validation surfaces.
- Use `docs/03-ai-runtime-operating-model.md` for shared guidance on how assistant runtimes consume instructions, skills, prompts, and agents.
- Use `AGENTS.md`, `.github/copilot-instructions.md`, scoped instructions, skills, or agents for binding rules.
- Use `LESSONS_LEARNED.md` for lessons that are still pending codification.

## Scope

This file is repo-specific and descriptive. It may inform interpretation, but it must not override `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, or consumer-local override files.

Consumer repositories may receive a scaffold for their own `docs/02-repository-context.md`, but sync must preserve their target-owned content after creation.

## Local Operating Context

- This repository is the standards repository for shared GitHub Copilot and AI-agent customization assets.
- Source-managed assets in this repository can be synchronized into consumer repositories through the local sync workflow.
- `internal-*` resources are repository-owned canonical assets in this standards repository.
- `local-*` resources are consumer-local assets in target repositories; in this standards repository, `local-*` also identifies source-owned sync tooling that must stay source-only.
- Imported upstream resources remain support depth unless a repository-owned wrapper or replacement explicitly owns the local behavior.

## Stable Decisions

| Decision | Status | Policy owner |
| --- | --- | --- |
| Keep policy, Copilot projection, inventory, architecture, local context, and runtime model separate. | Active | `AGENTS.md`, `.github/copilot-instructions.md`, `docs/01-architecture.md` |
| Scaffold `docs/01-architecture.md` and `docs/02-repository-context.md` into consumers only when missing, then preserve them. | Active | Sync automation and `references/sync-contract.md` |
| Keep `docs/03-ai-runtime-operating-model.md` source-managed and synchronized to consumers. | Active | Sync automation and `docs/03-ai-runtime-operating-model.md` |
| Keep `.github/templates/` as standards-repository sync source material, not a synced target catalog. | Active | Sync automation and `references/sync-contract.md` |

## Glossary

| Term | Meaning |
| --- | --- |
| Standards repository | This repository, which owns the shared baseline and sync automation. |
| Consumer repository | A target repository that receives the shared baseline while preserving declared local assets. |
| Source-managed | Content copied or structurally aligned from this repository into targets. |
| Consumer-local | Content created or preserved in the target repository and not overwritten by later sync runs. |
| Projection | A surface-specific expression of canonical rules, such as the Copilot projection in `.github/copilot-instructions.md`. |
| Scaffold | Initial file content created from a template only when the target file is missing. |

## Non-Policy Notes

- This file can explain why a local convention exists, but binding behavior must live in the canonical owner listed in the architecture or policy files.
- When context here contradicts a canonical instruction surface, follow the canonical instruction and update this file or the canonical owner in the same change.
