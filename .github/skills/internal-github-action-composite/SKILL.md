---
name: internal-github-action-composite
description: Use when creating or modifying a reusable GitHub composite action under `.github/actions/`, especially when input validation, shell safety, or contract compatibility matters.
---

# GitHub Composite Action Skill

## When to use
- Create a new reusable composite action under `.github/actions/`.
- Modify an existing composite action and preserve compatibility.
- Deepen a GitHub Actions task that has already been classified as composite-action authoring.

## Relationship to the umbrella skill
- `internal-github-actions` is the default entry point for GitHub Actions authoring.
- Load this skill when the work is specifically a composite action or when the umbrella skill decides the reusable unit should move here.

## Composite action vs reusable workflow

| Factor | Composite action | Reusable workflow |
|---|---|---|
| Granularity | Step-level reuse inside a job | Job-level orchestration |
| Secrets access | Inherited from the caller job | Passed explicitly to the called workflow |
| Outputs | Step outputs only | Workflow outputs |
| Best for | Shared validation, setup, or step logic | Pipelines with their own jobs, runners, or environments |

## Mandatory rules
- Follow `.github/instructions/internal-github-action-composite.instructions.md`.
- Pass expression inputs via `env:` instead of interpolating `${{ }}` directly in `run:`.
- Keep `shell: bash` explicit on composite steps.
- Start shell blocks with `set -euo pipefail`.
- Extract long shell logic into a dedicated script early.
- Preserve backward compatibility when modifying existing inputs or outputs.

## Minimal template

Load `references/minimal-template.md` when you need the starter `action.yml` shape. Keep the initial template small, validate required inputs early, and move longer logic into a script instead of growing a large inline `run:` block.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Interpolating `${{ inputs.x }}` directly in `run:` | Crafted input values can turn into shell injection | Pass the value through `env:` and use quoted shell variables |
| Missing `set -euo pipefail` in `run:` blocks | Silent failures and partial execution become hard to spot | Make strict mode the first line of every shell block |
| Large inline `run:` blocks | They are hard to read, lint, and review | Extract the logic into a dedicated script early |
| No input validation before the main logic | Failures surface later with weaker error messages | Validate required inputs in the first step and fail fast |
| Forgetting `shell: bash` on composite steps | Runner defaults can differ and change behavior | Keep `shell: bash` explicit |
| Breaking an existing input or output contract | Callers can fail without a clear migration path | Add new fields compatibly and preserve the old contract where possible |

## Cross-references

- **internal-github-actions** (`.github/skills/internal-github-actions/SKILL.md`): for the umbrella GitHub Actions lane and reuse-pattern selection.
- **internal-script-bash** (`.github/skills/internal-script-bash/SKILL.md`): for extracted shell scripts inside the action.

## Validation

- Inputs are explicit and validated early.
- Shell code uses `set -euo pipefail`, quoted variables, and explicit `shell: bash`.
- Longer logic moves into a dedicated script instead of staying inline.
- Existing input and output contracts remain backward compatible.
