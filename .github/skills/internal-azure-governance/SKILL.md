---
name: internal-azure-governance
description: Use when the user needs Azure RBAC operating models, managed identity boundaries, PIM or PAM posture, Azure Policy and initiatives, naming and tagging guardrails, or exception-handling design after the Azure structure is chosen. Do not use for tenant or subscription layout; monitoring, backup, or rollout validation; Azure DevOps pipelines; or materially ambiguous requests with no clear governance deliverable.
---

# Internal Azure Governance

## Handoffs

| To | When |
|---|---|
| `internal-azure` | material routing uncertainty prevents selecting a primary Azure specialist |
| `internal-azure-organization-structure` | where a capability should live |
| `internal-azure-operations` | preflight, reporting, evidence after design |
| `awesome-copilot-azure-role-selector` | least-privilege role selection depth |

Use this skill when the next need is to define or review Azure identity, access, and guardrail decisions.

This skill owns governance logic after the broad structure is known. It helps separate tenant or management-group guardrails from subscription or workload grants and keeps permission decisions auditable.

## When to use

- The user needs RBAC model guidance across management groups or subscriptions.
- The user needs managed identity or privileged-access posture guidance.
- The user needs Azure Policy, initiative, naming, or tagging guardrails.
- The user needs a review of guardrail design, exceptions, or access governance.

## When not to use

- The main problem is management-group, landing-zone, or subscription layout.
- The request is materially ambiguous and no primary Azure owner can be named → `internal-azure`.
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

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating Azure Policy as if it grants access | Preventive controls get confused with authorization paths | Pair Policy guidance with the RBAC or identity model that actually grants access |
| Answering a governance question without naming scope | Management-group, subscription, and resource scopes behave differently | State the exact scope before recommending a mechanism |
| Mixing tenant-wide guardrails and subscription-level authorization into one vague recommendation | Reviewers cannot see what prevents versus what grants | Separate Policy or PIM posture from RBAC assignments and workload identity design |
| Proposing emergency access without boundaries, audit expectations, or privileged-access posture | Break-glass becomes a standing exception instead of controlled elevation | Define who can elevate, how long it lasts, and what evidence must exist |
| Recommending rollout without staged validation when the blast radius is high | Wide RBAC or Policy errors can block operations quickly | Use scoped rollout, compliance checks, and explicit rollback triggers |
| Treating managed identities as a reason to skip scope design | Identity becomes secretless but still over-privileged | Keep identity type and authorization scope as separate decisions |

## Validation

- Confirm the governance scope is explicit: management group, subscription set, or single subscription.
- Confirm the recommended mechanism is clear about whether it prevents, grants, or constrains privileged access.
- Confirm identity boundaries and exception paths are explicit for human and workload access.
- Confirm staged rollout validation is named before high-blast-radius Policy, RBAC, or PIM changes.
- Confirm the answer says when operational proof should move to `internal-azure-operations` and when least-privilege role depth should move to `awesome-copilot-azure-role-selector`.
