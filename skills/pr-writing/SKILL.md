---
name: pr-writing
description: Produce concise, complete pull request descriptions aligned with the repository PR template.
---

# PR Writing Skill

## When to use
- Create a new pull request description.
- Improve an incomplete pull request body.
- Summarize changes from modified files and checks.

## Mandatory rules
- Use English for all PR content.
- Keep summary concise and outcome-oriented.
- Include only relevant scope checkboxes.
- Provide a short bullet list of key changes.
- Include validation commands and results.
- Explicitly state risk level and rollback plan.

## Template alignment
- Use the existing repository template at `.github/pull_request_template.md`.
- Follow template sections in order and keep template headings unchanged.
- Keep unchanged sections but write `N/A` if not applicable.
- Avoid empty placeholders.

## Minimal example
- Input:
  - title: "Harden Copilot validator"
  - changed_files: ".github/scripts/validate-copilot-customizations.sh, .github/workflows/validate-copilot-customizations.yml"
  - validation: "bash -n scripts/*.sh; shellcheck -s bash scripts/*.sh"
- Expected output:
  - Complete PR body with filled `Summary`, `Scope`, `Changes`, `Validation`, `Security and Compliance`, and `Risk and Rollback`.
  - A brief and accurate bullet list under `Changes`.

## Validation
- Ensure every section from `.github/pull_request_template.md` is present.
- Ensure `Changes` has concise bullets describing the real diff.
- Ensure risk and rollback are explicit and actionable.
