# Structure

## Purpose

This document describes how the repository is organized and which areas are
authored, generated, temporary, or consumer-facing.

## Top-Level Layout

| Path | Responsibility |
| --- | --- |
| `AGENTS.md` | Strategic bridge and precedence anchor for repository-wide AI governance. |
| `.github/` | Source-managed skills, agents, prompts, templates, scripts, workflows, and policy projections. |
| `docs/` | Descriptive repository-local knowledge documents. |
| `tests/` | Contract and regression tests for governance and sync behavior. |
| `tmp/` | Retained plans, temporary analysis, and non-canonical working artifacts. |
| `graphify-out/` | Generated graph analysis outputs and cache artifacts. |

## Ownership Boundaries

- Policy ownership remains in canonical owners such as `AGENTS.md`,
  `.github/copilot-instructions.md`,
  `.github/instructions/copilot-code-review.instructions.md`, skills,
  validators, and owned files.
- `docs/` is descriptive and must not become a policy owner.
- `.github/templates/` is source-side scaffold material and is not mirrored as
  an operational catalog family.
- Consumer-local files created from templates are preserved by sync automation.

## Generated vs Authored

| Type | Paths | Handling expectation |
| --- | --- | --- |
| Authored | `AGENTS.md`, `.github/skills/`, `.github/agents/`, `docs/`, tests | Edited intentionally with contract-aware validation. |
| Generated | `.github/INVENTORY.md`, sync manifests, graph outputs | Rebuilt by scripts or tools, not manually curated as policy. |
| Temporary | `tmp/` working artifacts | Retained only when needed by workflow contracts. |

## Placement Conventions

- Keep repository-owned reusable guidance under `.github/skills/`.
- Keep route wrappers and command centers under `.github/agents/`.
- Keep script logic under `.github/scripts/` with tests in `tests/`.
- Keep retained plans under `tmp/superpowers/` and out of `docs/`.

## Unknown / To Verify

- Any legacy placement conventions still referenced by external consumers.
- Whether all generated artifacts are covered by current ignore and validation rules.
