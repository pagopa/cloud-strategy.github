# Contributing

## Scope

This repository is the source baseline for reusable GitHub Copilot customization assets synced into consumer repositories.

## Instruction architecture

- `AGENTS.md` is the strategic entrypoint, precedence anchor, and cross-surface bridge.
- `.github/copilot-instructions.md` is the repo-wide Copilot projection for native Copilot flows.
- `.github/instructions/*.instructions.md` are path-specific or domain-specific projections.
- `.github/INVENTORY.md` owns the live catalog of managed assets; do not move volatile inventory into `AGENTS.md`.
- The default authoring language for repository artifacts is English unless a scoped instruction explicitly overrides it.

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

## Validation before PR

- `make lint`
- Run any additional stack-specific validation relevant to the touched assets.
- If a dedicated validator, sync script, or test suite for the affected behavior does not exist in the current repository, report that gap instead of assuming legacy automation still applies.

## Review flow

- Required validation before PR: `make lint` plus any stack-specific checks relevant to the touched assets.

## Release and sync metadata

- Update `VERSION` when publishing a standards release with consumer-facing impact.
- Create a git tag for released versions using the `vMAJOR.MINOR.PATCH` format.
- The sync manifest records `source_version` and `source_commit`; keep them accurate by releasing from clean commits.
