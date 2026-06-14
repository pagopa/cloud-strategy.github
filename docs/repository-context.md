# Repository Context

## Purpose

This document captures stable local context for this repository. It explains
what the repository is for, who it serves, and which outcomes it supports.

## Scope

The content here is descriptive and repository-local. It must not override
`AGENTS.md`, `.github/copilot-instructions.md`, skills, agents, prompts,
validators, or owned files.

## Repository Role

`cloud-strategy.github` is the standards repository for shared GitHub Copilot
customization assets, skill-first architecture guidance, catalog governance,
and source-side sync tooling.

## Responsibilities

- Maintain the shared baseline for repository-owned AI guidance and governance.
- Provide source-side automation to plan and apply baseline sync into consumer
  repositories.
- Keep catalog inventory and consistency checks aligned with filesystem state.
- Preserve consumer-local assets during sync, including `local-*.instructions.md`
  and consumer-local knowledge documents.

## Capabilities

- Skill and agent governance under `.github/skills/` and `.github/agents/`.
- Catalog generation and validation from `.github/scripts/` and `tests/`.
- Sync contract support through source templates and sync automation.
- Retained-plan and retained-learning governance through owned workflows.

## Consumers And Stakeholders

- Primary consumers: repositories that import or align to this baseline.
- Primary maintainers: contributors managing AI governance and sync behavior.
- Secondary stakeholders: engineers relying on stable AI customization
  contracts and predictable sync outcomes.

## Goals

- Keep policy, bridge, review baseline, inventory, context, and workflows
  clearly separated.
- Keep sync behavior safe for target-owned local knowledge and local overrides.
- Keep validations close to contract changes.

## Non-Goals

- Running product workloads.
- Owning consumer repository runtime operations.
- Replacing canonical policy owners with descriptive docs.

## Domain Vocabulary

| Term | Meaning |
| --- | --- |
| Standards repository | This repository, which owns source-side AI baseline and sync tooling. |
| Consumer repository | A target repository receiving the baseline while preserving local assets. |
| Source-managed | Content mirrored from this repository into consumers. |
| Consumer-local | Content owned by the target and preserved across sync runs. |
| Bridge | Compact routing layer for Copilot surfaces, such as `.github/copilot-instructions.md`. |
| Scaffold | Initial target file materialized from a source template only when missing. |

## Unknown / To Verify

- Consumer adoption coverage by repository and cadence.
- Any external dependencies not represented in this repository.
