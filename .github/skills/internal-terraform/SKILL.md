---
name: internal-terraform
description: Use when a Terraform/OpenTofu request needs classification and routing to the narrowest specialist.
---

# Terraform Router

## Referenced files

- `references/review-anti-patterns.md`: Local Terraform review overlay with ID-tagged patterns. Load only when a review needs the repository's local anti-pattern vocabulary.
- `references/decision-guide.md`: Local feature-versus-module triage aid. Load when placement is the immediate decision before routing module work.

The referenced skills are routing targets, not a preload bundle:

- `internal-tf`: Terraform/OpenTofu language, HCL, `.tf`, `.tfvars`, and typed configuration.
- `ibm-terraform-test`: Native Terraform/OpenTofu tests and mock-provider scenarios.
- `antonbabenko-terraform-skill`: Modules, state, plans, delivery, scans, upgrades, recovery, and operational risk.

## When to use

Use this skill for any Terraform/OpenTofu request that is ambiguous, crosses language and operations, or needs the correct specialist selected before work begins.

- Classify a request involving `.tf`, `.tfvars`, `.tfvars.json`, `.tftest.hcl`, modules, state, CI, providers, scans, or drift.
- Route an infrastructure change to the narrowest owner without loading unrelated depth.
- Coordinate a mixed request where a language edit and an operational, test, or provider decision are independently required.

## Routing contract

Choose exactly one primary owner from the immediate deliverable. Add a secondary owner only when its deliverable is independently requested.

| Immediate deliverable | Primary owner | Selection signal |
| --- | --- | --- |
| HCL syntax, expressions, types, variables, outputs, `.tfvars`, file layout, or formatting | `/internal-tf` | The question is about configuration language or shape. |
| Native `.tftest.hcl` or `.tftest.json`, `run`, `assert`, mock providers, test modes, or `terraform test`/`tofu test` | `/ibm-terraform-test` | The artifact or command is the native Terraform test framework. |
| Module architecture, state, drift, plan/apply, CI/CD, scans, security, provider upgrades, recovery, or risk diagnosis | `/antonbabenko-terraform-skill` | The answer depends on infrastructure lifecycle or operational risk. |

### Boundary examples

- "Fix the type constraint in a variable" routes to `/internal-tf`.
- "Correct a `module` block's HCL syntax" routes to `/internal-tf`; choosing module boundaries routes to `/antonbabenko-terraform-skill`.
- "Write a `.tftest.hcl` file with a mock provider" routes to `/ibm-terraform-test`.
- "Review why a module refactor will destroy resources" routes to `/antonbabenko-terraform-skill`.
- "Change an Azure resource in Terraform" routes to the router first; add an Azure specialist only when an Azure topology or governance decision is independently requested.

IBM's scope is deliberately narrow: it owns native Terraform/OpenTofu test artifacts and execution guidance, not general Terraform testing strategy, CI design, security scanning, or infrastructure diagnosis.

## Context before handoff

Collect only the context required by the selected owner:

| Owner | Required context |
| --- | --- |
| `internal-tf` | File type, Terraform or OpenTofu runtime, version when a feature floor matters, and the language construct in scope. |
| `ibm-terraform-test` | Runtime and version, test file or run block, `plan` versus `apply`, mock versus real provider, credentials, and cleanup expectations. |
| `antonbabenko-terraform-skill` | Runtime and exact version, providers, backend, local/CI/Cloud execution path, environment criticality, and risk category. |

Do not ask for state, credentials, or cloud context for a language-only request when those details cannot affect the answer.

## Handoff protocol

Before invoking a specialist, state:

1. `Primary`: the selected skill.
2. `Secondary`: only an independently requested adjacent owner, otherwise `none`.
3. `Reason`: the immediate deliverable and the signal that selected it.
4. `Context`: the known runtime, files, and risk details; mark missing facts explicitly.
5. `Validation`: the narrowest check expected from the selected owner.

The selected specialist owns the final domain response. The router supplies classification and context, but does not duplicate the specialist's full workflow or response contract.

## Guardrails

- Preserve `/internal-terraform` as the stable entrypoint for existing callers.
- Keep imported skills upstream-authoritative; do not edit `ibm-terraform-test` or `antonbabenko-terraform-skill` from this router change.
- Prefer the smallest valid owner and avoid invoking all Terraform skills by default.
- If no Terraform/OpenTofu context is present, route to the language or platform owner that actually owns the artifact instead of forcing a Terraform specialist.
- Never recommend a production apply without the reviewed plan and approval controls required by the operational specialist.
