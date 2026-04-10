---
name: internal-azure-operations
description: Use when the user needs Azure operational guidance for monitoring, logging, backup and restore, Site Recovery or DR validation, preflight checks, post-rollout validation, reporting, or audit evidence after a structure or governance decision has already been made.
---

# Internal Azure Operations

Use this skill when the next need is to validate, observe, or operationalize an Azure platform decision.

This skill owns the operational side of the platform: monitoring, evidence, preflight, and post-rollout verification. It does not replace strategic framing, structure design, or governance design.

## When to use

- The user needs operational readiness guidance after a design choice.
- The user needs Azure Monitor, Log Analytics, backup, restore, or DR validation guidance.
- The user needs preflight or post-rollout validation patterns.
- The user needs reporting, export, compliance evidence, or operational proof.

## When not to use

- The main problem is still choosing the high-level direction.
- The main problem is management-group, landing-zone, or subscription structure.
- The main problem is RBAC, managed identity, PIM, or Policy design.
- The task is a narrow implementation change with no operational design question.

## Main domains covered

- monitoring and observability posture
- Azure Monitor and Log Analytics evidence paths
- backup and restore expectations
- Site Recovery or DR validation
- preflight checks before rollout
- post-rollout validation
- export and reporting for platform operations
- operational proof that a governance or structure change behaved as expected

## Core rules

- Keep validation proportional to blast radius.
- Treat backup posture and restore evidence as different things.
- Prefer preflight and staged validation before wide rollout when identity, policy, or platform automation could break.
- Keep monitoring, evidence, and reporting tied to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` when the user needs a deeper checklist for preflight, rollout validation, or DR evidence.

## Use of current facts

Use current Microsoft documentation when the answer depends on current Azure Monitor, Backup, Site Recovery, Policy compliance, or service-behavior details.

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
- recovery or DR note when relevant
- open operational risks

## Relationship to adjacent skills

- `internal-azure-strategic`
  Use first when the core decision is still unsettled.
- `internal-azure-organization-structure`
  Use when the operations question is actually about management-group, subscription, or topology placement.
- `internal-azure-governance`
  Use when the operations question is actually about RBAC, managed identity, Policy, or guardrail design rather than validation.

## Anti-patterns

- treating monitoring as proof that restore or recovery works
- skipping preflight for high-blast-radius rollout
- reporting only control intent without operational evidence
- mixing validation advice with new governance design instead of keeping the boundary clear
- giving a DR answer without making the business criticality assumption visible
