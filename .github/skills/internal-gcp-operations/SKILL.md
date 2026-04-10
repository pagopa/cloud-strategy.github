---
name: internal-gcp-operations
description: Use when the user needs Google Cloud operational guidance for monitoring, logging, backup and restore, DR validation, asset inventory, preflight checks, post-rollout validation, reporting, or audit evidence after a structure or governance decision has already been made.
---

# Internal GCP Operations

Use this skill when the next need is to validate, observe, or operationalize a GCP platform decision.

This skill owns the operational side of the platform: monitoring, evidence, inventory, preflight, and post-rollout verification. It does not replace strategic framing, structure design, or governance design.

## When to use

- The user needs operational readiness guidance after a design choice.
- The user needs Cloud Monitoring, Cloud Logging, backup, restore, or DR validation guidance.
- The user needs asset inventory, reporting, or export guidance.
- The user needs preflight or post-rollout validation patterns.

## When not to use

- The main problem is still choosing the high-level direction.
- The main problem is org, folder, project, or Shared VPC structure.
- The main problem is IAM, workload identity, service account, or Org Policy design.
- The task is a narrow implementation change with no operational design question.

## Main domains covered

- monitoring and observability posture
- Cloud Monitoring and Cloud Logging evidence paths
- backup and restore expectations
- DR validation and recovery evidence
- asset inventory and reporting
- preflight checks before rollout
- post-rollout validation
- operational proof that a governance or structure change behaved as expected

## Core rules

- Keep validation proportional to blast radius.
- Treat backup posture and restore evidence as different things.
- Prefer preflight and staged validation before wide rollout when identity, policy, or shared networking could break.
- Keep monitoring, inventory, evidence, and reporting tied to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` when the user needs a deeper checklist for preflight, rollout validation, asset inventory, or DR evidence.

## Use of current facts

Use current Google Cloud documentation when the answer depends on current Monitoring, Logging, Backup and DR behavior, asset-inventory capability, or service-specific validation details.

## Output expectations

For narrow asks, return:

- recommended validation or evidence path
- short reason
- main operational risk

For broader asks, return:

- operational objective
- preflight checks
- rollout-stage validation path
- post-rollout evidence path
- recovery, DR, or inventory note when relevant
- open operational risks

## Relationship to adjacent skills

- `internal-gcp-strategic`
  Use first when the core decision is still unsettled.
- `internal-gcp-organization-structure`
  Use when the operations question is actually about org, project, or topology placement.
- `internal-gcp-governance`
  Use when the operations question is actually about IAM, workload identity, Org Policy, or guardrail design rather than validation.

## Anti-patterns

- treating monitoring as proof that restore or recovery works
- skipping preflight for high-blast-radius rollout
- reporting only control intent without operational evidence
- mixing validation advice with new governance design instead of keeping the boundary clear
- giving a DR answer without making the business criticality assumption visible
