---
name: internal-github-action-composite
description: Use when /internal-github routes composite-action work under `.github/actions/`, including inputs, outputs, shell safety, tests, documentation, and compatibility.
user-invocable: false
---

# GitHub Composite Action Skill

Own the concrete composite-action contract under `.github/actions/`: inputs,
outputs, shell behavior, compatibility, documentation, and validation.

## When to use

- Create or modify an `action.yml` composite action.
- Preserve compatibility while changing inputs or outputs.
- Document or test a composite action.

## Composite-action contract

Input validation is the first contract step; validate required values before
the action performs its main logic.

- Pass expression inputs through `env:` instead of interpolating them directly
  in `run:`.
- Keep `shell: bash` explicit on every composite step.
- Start shell blocks with `set -euo pipefail`.
- Validate required inputs before the main logic and fail clearly.
- Forward caller-visible values through `outputs:` mapped from `$GITHUB_OUTPUT`.
- Use `$GITHUB_ENV` only for step-to-step state inside the action.
- Extract long shell logic into a dedicated script early.
- Preserve backward compatibility for existing inputs and outputs, or treat a
  breaking contract as a versioning event.

## Conditional review contributor

When this skill is conditionally loaded by `/internal-review-code`, contribute
observations only for `action.yml` or `action.yaml` surfaces. Inspect linked
caller workflow, inputs, outputs, expressions, environment forwarding,
repository scripts, compatibility/versioning, documentation, smoke checks,
and failure paths.

Return only the wrapper protocol fields: `domain`,
`changed_contract_surfaces`, `observations`, `probes`,
`applicable_validations`, `compatibility_risks`, and `evidence_gaps`. Focus
observations and probes on input/output contracts, safe expression and
environment handling, explicit Bash and strict mode, `$GITHUB_OUTPUT`,
supported runtime versions, documentation, smoke behavior, and failure-path
evidence.

This contributor does not issue a verdict, severity, approval, merge decision,
remediation plan, or replacement review procedure. Addy remains the sole
substantive review engine and `internal-review-code` remains the single
public-verdict owner. Static action.yml evidence cannot prove live runner
health or runtime loading; record that limitation as an evidence gap.

## Reference map

- Load [minimal template](references/minimal-template.md) for the smallest safe
  starter `action.yml`.
- Load [multi-step template](references/multi-step-template.md) when the action
  shares state and exposes caller-visible outputs.
- Load [output forwarding pattern](references/output-forwarding-pattern.md)
  when a step result becomes an action output.
- Load [testing pattern](references/testing-pattern.md) for smoke, failure-path,
  and contract checks.
- Load [action README template](references/action-readme-template.md) for
  inputs, outputs, side effects, and usage documentation.
- Load [versioning strategy](references/versioning-strategy.md) for published
  or compatibility-sensitive actions.

## Completion criteria

- `action.yml` inputs and outputs are explicit and validated early.
- Expressions are passed safely through environment variables.
- Shell uses strict mode and explicit Bash.
- Caller-visible outputs are documented and forwarded through
  `$GITHUB_OUTPUT`.
- Smoke and failure-path validation cover the contract.
- Existing compatibility is preserved or versioned deliberately.
