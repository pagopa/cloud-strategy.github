# Contributing

## Scope

This repository is the source baseline for reusable GitHub Copilot customization assets synced into consumer repositories.

## Skill-first architecture

- `AGENTS.md` is the strategic entrypoint, precedence anchor, and runtime agent policy surface.
- `.github/copilot-instructions.md` is review-only for GitHub.com Copilot code review.
- `.github/skills/` owns reusable technical baselines, workflow depth, and specialist procedures.
- `.github/agents/` owns wrapper selection, tool scope, and user-visible handoff UX.
- Prompts, validators, docs, and owned files carry their own local contracts when they are the smallest valid owner.
- `.github/INVENTORY.md` owns the live catalog of managed assets; do not move volatile inventory into `AGENTS.md`.
- The default authoring language for repository artifacts is English unless a narrower owned file or local exception explicitly overrides it.

## Naming conventions

- External upstream assets use `<short-repo>-<original-resource-name>` in both filenames and `name:` values.
- Source-owned assets created in this repository use the `internal-` prefix in both filenames and `name:` values.
- Source-owned assets created in other local repositories use the `local-` prefix in both filenames and `name:` values.
- Keep legacy aliases only when backward compatibility requires them, and document them explicitly in the sync flow.

## Adding or updating assets

- Skills: keep `name`, `description`, `## When to use`, and one validation/testing section.
- Agents: keep `name`, `description`, `tools`, and the current section structure used in this repository: `## Role`, `## Mandatory Engine Skills`, `## Optional Support Skills`, `## Core Rules`, `## Routing Rules`, `## Boundary Definition`, and `## Output Expectations`.
- Prompts: keep frontmatter `name`, `agent`, and `description`, plus explicit input placeholders.

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
