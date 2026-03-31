# Contributing

## Scope
This repository is the source baseline for reusable GitHub Copilot customization assets synced into consumer repositories.

## Naming conventions
- External upstream assets use `<short-repo>-<original-resource-name>` in both filenames and `name:` values.
- Source-owned assets created in this repository use the `internal-` prefix in both filenames and `name:` values.
- Source-owned assets created in other local repositories use the `local-` prefix in both filenames and `name:` values.
- Keep legacy aliases only when backward compatibility requires them, and document them explicitly in the sync flow.

## Adding or updating assets
- Instructions: keep frontmatter `description` and `applyTo`, use repository-agnostic wording, and avoid stack duplication already covered by a skill.
- Prompts: require `name`, `description`, `agent`, and `argument-hint`, plus `## Instructions`, `## Validation`, and `## Minimal example`.
- Skills: keep `name`, `description`, `## When to use`, and one validation/testing section.
- Agents: keep `name`, `description`, `tools`, `## Objective`, and `## Restrictions`.
- Sync behavior changes must include test coverage under `tests/`.

## Validation before PR
- `make lint`
- `make validate`
- `make test`
- Run any additional stack-specific validation relevant to the touched assets.

## Review flow
- Required validation before PR (`make lint`, `make test`, and any stack-specific checks)

## Release and sync metadata
- Update `VERSION` when publishing a standards release with consumer-facing impact.
- Create a git tag for released versions using the `vMAJOR.MINOR.PATCH` format.
- The sync manifest records `source_version` and `source_commit`; keep them accurate by releasing from clean commits.
