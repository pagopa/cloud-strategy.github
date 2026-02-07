---
description: Build a complete pull request body using the existing repository PR template
name: cs-pr-description
agent: agent
argument-hint: title=<text> intent=<text> changed_files=<comma-separated paths> [validation=<commands/results>] [risk=<Low|Medium|High>] [links=<issue/docs/runbook>]
---

# Pull Request Description Task

## Context
Create or update a pull request body using the existing template at `.github/PULL_REQUEST_TEMPLATE.md`, including a short list of key changes.

## Required inputs
- **Title**: ${input:title}
- **Intent**: ${input:intent}
- **Changed files**: ${input:changed_files}
- **Validation**: ${input:validation:Not provided}
- **Risk**: ${input:risk:Low,Medium,High}
- **Links**: ${input:links:N/A}

## Required section headings
- `## Summary`
- `## Scope`
- `## Changes`
- `## Validation`
- `## Security and Compliance`
- `## Risk and Rollback`
- `## Related Links`
- `## Reviewer Notes`

## Instructions
1. Use `.github/skills/pr-writing/SKILL.md`.
2. Use the existing repository template at `.github/PULL_REQUEST_TEMPLATE.md`.
3. Follow template section order and headings exactly.
4. Do not remove required sections from the template.
5. Fill all sections; if a section is not applicable, use `N/A`.
6. In `Changes`, provide a brief bullet list of the most relevant modifications from `changed_files`.
7. In `Scope`, check only applicable categories.
8. Keep content concise, concrete, and in English.

## Minimal example
- Input: `title="Add JSON report support in validator" intent="Improve CI visibility" changed_files=".github/scripts/validate-copilot-customizations.sh, .github/workflows/validate-copilot-customizations.yml" validation="bash -n scripts/*.sh; shellcheck -s bash scripts/*.sh; .github/scripts/validate-copilot-customizations.sh --scope root --mode strict" risk=Low links="Issue: N/A"`
- Expected output:
  - Full PR markdown body aligned with `.github/PULL_REQUEST_TEMPLATE.md`.
  - `Changes` section with short bullets summarizing the real modifications.
  - `Validation` section containing commands and outcomes.

## Validation
- Confirm all required section headings are present and non-empty (or `N/A`).
- Confirm `Changes` bullets are brief and aligned with modified files.
- Confirm risk level and rollback plan are explicitly included.
