---
name: internal-azure-governance
description: Use when the user needs Azure governance guidance for RBAC operating models, managed identity boundaries, PIM or PAM posture, Azure Policy and initiatives, naming and tagging guardrails, exception handling, or other controls that define what principals can do after the Azure structure is chosen.
---

# Internal Azure Governance

Use this skill when the next need is to define or review Azure identity, access, and guardrail decisions.

This skill owns governance logic after the broad structure is known. It helps separate tenant or management-group guardrails from subscription or workload grants and keeps permission decisions auditable.

## When to use

- The user needs RBAC model guidance across management groups or subscriptions.
- The user needs managed identity or privileged-access posture guidance.
- The user needs Azure Policy, initiative, naming, or tagging guardrails.
- The user needs a review of guardrail design, exceptions, or access governance.

## When not to use

- The main problem is management-group, landing-zone, or subscription layout.
- The main problem is strategic option framing before the governance surface is clear.
- The main problem is monitoring, reporting, backup, or post-rollout validation.
- The task is implementation-only.

## Main domains covered

- RBAC operating model
- Entra group and role-assignment strategy
- managed identity boundaries
- PIM and PAM posture
- Azure Policy and initiatives
- naming and tagging guardrails
- security baseline tied to identity and access decisions
- exception handling at governance level

## Core rules

- Keep tenant or management-group guardrails distinct from subscription or resource-level grants.
- Treat Azure Policy as preventive or detective governance, not as permission grants.
- Prefer managed identities and federated workload access over long-lived secrets unless there is a proven reason not to.
- Make scope explicit: management group, subscription set, or single subscription.
- Make exception handling explicit when a control is not universal.

Load `references/guardrail-map.md` when the correct governance surface is ambiguous or when the user needs a deeper split between RBAC, managed identities, PIM/PAM, and Policy controls.

## Use of current facts

Use current Microsoft documentation when the answer depends on current Azure RBAC semantics, managed identity support, Policy effects, or privileged-access behavior.

## Output expectations

For narrow asks, return:

- recommended governance mechanism
- short reason
- main risk or validation note

For broader asks, return:

- governance objective
- scope
- candidate mechanisms
- recommended control stack
- exception or blast-radius note
- what should be validated before rollout

## Relationship to adjacent skills

- `internal-azure-strategic`
  Use first when the user still needs option framing or lens selection.
- `internal-azure-organization-structure`
  Use when the governance question is actually about where a capability should live.
- `internal-azure-operations`
  Use when the next need is preflight, reporting, validation, or operational evidence after the governance design is chosen.

## Anti-patterns

- treating Azure Policy as if it grants access
- answering a governance question without naming scope
- mixing tenant-wide guardrails and subscription-level authorization into one vague recommendation
- proposing emergency access without boundaries, audit expectations, or privileged-access posture
- recommending rollout without staged validation when the blast radius is high
