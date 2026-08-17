---
name: internal-azure-governance
description: Use when /internal-azure selects Azure authorization, workload identity, privileged access, Policy, guardrail, or exception work.
---

# Internal Azure Governance

Use this workflow to define auditable Azure identity, access, and guardrail
decisions.

## When to use

Arrive here only when /internal-azure selects the governance lane: Azure
authorization, workload identity, privileged access, Policy, guardrails, or
governed exceptions.

## Workflow

1. State the governance objective: the access, prevention, detection, or
   privileged-elevation outcome required.
2. Set the control scope: management group, subscription set, subscription, or
   resource, with the affected principals and workloads.
3. Design the authorization model and distinguish grants, preventive controls,
   detective controls, workload identity, and privileged elevation.
4. Define the exception path with an owner, business reason, compensating
   control, expiry or review date, and audit evidence.
5. Stage the rollout with a safe scope, compliance or access checks, rollback
   triggers, and evidence collection.
6. Verify every item in Completion criteria before finishing.

## Azure governance patterns

- Use Azure Policy and initiatives for preventive or detective guardrails.
- Use RBAC role assignments for authorization with explicit scope.
- Use managed identities or federation for workload access and keep runtime
  identity separate from human access grants.
- Use PIM or PAM for time-bound, approved, and reviewable elevation.
- Use naming and tagging controls when metadata consistency is part of the
  governance objective.

## Current facts

Use current Microsoft documentation when the recommendation depends on Azure
RBAC semantics, managed identity support, Policy effects, or privileged-access
behavior.

Load `references/guardrail-map.md` for control patterns, identity examples, and
exception evidence.

## Completion criteria

Return the governance objective, control scope, recommended mechanism, exception
path, rollout evidence, and remaining validation risks.
