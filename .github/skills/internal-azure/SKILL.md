---
name: internal-azure
description: Use when designing, evaluating, or validating Azure platform and control-plane work, such as management groups, subscriptions, landing zones, network topology, RBAC, managed identity, PIM, Azure Policy guardrails, exceptions, rollout evidence, monitoring, recovery proof, or Azure option comparison. Route Azure DevOps pipelines to /internal-azure-devops, concrete Azure Policy definitions to /internal-cloud-policy, and Terraform code to /internal-terraform.
---

# Internal Azure

## When to use

- Place Azure resources and platform boundaries across tenant, management
  groups, subscriptions, landing zones, regions, and network topology.
- Design authorization, workload identity, privileged access, Policy
  guardrails, and governed exceptions.
- Define preflight, observability, rollout evidence, and backup, restore, or
  DR proof for an Azure change.
- Compare viable Azure options when the choice is the deliverable.

Route concrete artifacts to their owners through
[`references/adjacent-owners.md`](references/adjacent-owners.md). Hosting on
Azure alone does not make application code an Azure platform task.

## Baseline

Apply these rules to every recommendation. A deviation needs the typed
exception record from the governance reference.

- Do not grant Owner or User Access Administrator at subscription or wider
  scope without a justified, time-bound path such as PIM.
- Scope every role assignment and Policy assignment to the narrowest effective
  target, and name that scope.
- Prefer managed identity or workload identity federation over service
  principal secrets or certificates.
- Keep workload identity separate from human access.

## Workflow

1. Classify the primary concern and load its reference: structure
   Keep confirmed evidence separate from inferred evidence. Treat backup,
   restore, and DR proof as distinct.
7  supporting reference only when the same deliverable uses it.
2. State the objective and the scope: tenant, management group, subscription
   set, subscription, or resource, with the affected principals and workloads.
3. Choose the Azure mechanism from the loaded reference and state why it fits.
4. When cost or recovery is material, apply the FinOps or BC/DR lens from
   [`references/decision-mode.md`](references/decision-mode.md), even with one
   viable option. Write a comparative decision note only when two or more
   viable options remain, and state reversibility.
5. For changes with shared blast radius, name the first safe unit, the
   widening condition, and the rollback trigger.
6. Give every exception the typed record from the governance reference.
7. Keep confirmed evidence separate from inferred evidence. Treat backup,
   restore, and DR proof as distinct.
8. Hand off artifact work, such as Policy JSON, Terraform code, pricing, role
   selection, or incident diagnosis, to its owner.

## Freshness

Verify RBAC semantics, Policy effects, managed identity support, landing-zone
guidance, service limits, and regional capability against current Microsoft
documentation. Use the Microsoft Learn MCP server when it is available;
otherwise state the evidence gap.

## Output

Always return:

1. Recommendation.
2. Material risk.
3. Next validation action.

Add scope, options, reversibility, rollout unit, or exception record only when
the request makes them material.
