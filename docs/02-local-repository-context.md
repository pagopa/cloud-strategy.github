# Repository Context

> Purpose: provides stable local context for this repository's AI governance work.
> Keep operational facts, glossary entries, ownership notes, and durable interpretation aids here when they help humans
> and agents understand the repository.
> Do not use this file to create binding policy.

## Where Adjacent Content Belongs

- System boundaries, component responsibilities, architecture flow, and validation surfaces live in
  `docs/01-local-architecture.md`.
- Binding rules live in `AGENTS.md`, `.github/copilot-instructions.md`, skills, agents, prompts, validators, or owned files.
- Runtime workflow behavior lives in relevant skills, especially
  `internal-gateway-idea-brainstorming`, `internal-gateway-review`,
  `internal-gateway-simple-task`, and `internal-gateway-execute-plans`.
- Lessons that are still pending codification live in `LESSONS_LEARNED.md`.

## Scope

This file is repo-specific and descriptive. It may inform interpretation, but it must not override `AGENTS.md`,
`.github/copilot-instructions.md`, skills, agents, prompts, validators, owned files, or consumer-local override files.
When a runtime assembles manual context, this document is equivalent to a `<context policy="false">` block. It can
explain local facts, but it is not an instruction source.

Consumer repositories may receive a scaffold for their own `docs/02-local-repository-context.md`, but sync must preserve
their target-owned content after creation.

## Local Operating Context

- This repository is the standards repository for shared GitHub Copilot and AI-agent customization assets.
- Source-managed assets in this repository can be synchronized into consumer repositories through the local sync
  workflow.
- `internal-*` resources are repository-owned canonical assets in this standards repository.
- `local-*` resources are consumer-local assets in target repositories. In this standards repository, `local-*` also
  identifies source-owned sync tooling that must stay source-only.
- Imported upstream resources remain support depth unless a repository-owned wrapper or replacement explicitly owns the
  local behavior.

## Stable Decisions

| Decision | Status | Policy owner |
| --- | --- | --- |
| Keep policy, Copilot projection, inventory, architecture, local context, and skill-owned workflows separate. | Active | `AGENTS.md`, `.github/copilot-instructions.md`, `docs/01-local-architecture.md` |
| Scaffold `docs/01-local-architecture.md` and `docs/02-local-repository-context.md` into consumers only when missing, then preserve them. | Active | Sync automation and `references/sync-contract.md` |
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

- This file describes why a local convention exists. Binding behavior lives in the canonical owner listed in the
  architecture or policy files.
- When context here contradicts a canonical owner, treat the contradiction as documentation drift.
  Correct the drift in this file or in the canonical owner.
