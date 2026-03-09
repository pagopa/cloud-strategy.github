# Contributing

## Scope
This repository is the source baseline for reusable GitHub Copilot customization assets synced into consumer repositories.

## Naming conventions
- Canonical source-owned instructions, prompts, skills, and agents use the `tech-ai-` filename prefix.
- Canonical prompt, skill, and agent `name:` values use the `TechAI` prefix.
- Repo-only standards agents use the `TechAIGlobal` prefix and must stay source-only.
- Consumer-local assets use the `local-` prefix in both filenames and `name:` values.

## Adding or updating assets
- Instructions: keep frontmatter `description` and `applyTo`, use repository-agnostic wording, and avoid stack duplication already covered by a skill.
- Prompts: require `name`, `description`, `agent`, and `argument-hint`, plus `## Instructions`, `## Validation`, and `## Minimal example`.
- Skills: keep `name`, `description`, `## When to use`, and one validation/testing section.
- Agents: keep `name`, `description`, `tools`, `## Objective`, and `## Restrictions`.
- Sync or validator behavior changes must include test coverage under `tests/`.

## Validation before PR
- `make lint`
- `make validate`
- `make test`
- Run any additional stack-specific validation relevant to the touched assets.

## Review flow
- Author customization changes with `TechAIGlobalCustomizationBuilder`.
- Review them with `TechAIGlobalCustomizationAuditor`.
- Record notable lifecycle or behavior changes in `.github/CHANGELOG.md`.

## Release and sync metadata
- Update `VERSION` when publishing a standards release with consumer-facing impact.
- Create a git tag for released versions using the `vMAJOR.MINOR.PATCH` format.
- The sync manifest records `source_version` and `source_commit`; keep them accurate by releasing from clean commits.
