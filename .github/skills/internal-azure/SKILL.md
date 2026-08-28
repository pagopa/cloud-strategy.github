---
name: internal-azure
description: Use first for every Azure request. Classify the primary deliverable and select the minimum specialist lane for governance, DevOps pipelines, operations, organization structure, or strategic decisions.
---

# Internal Azure

The Azure platform entry point. Select the smallest specialist workflow for the
user's immediate deliverable and invoke it with its `/skill-name`.

## When to use

Use for Azure platform and control-plane requests where the next deliverable
belongs to an Azure family specialist.

## Routing workflow

1. Identify the immediate deliverable: organization structure, governance,
   operations evidence, Azure DevOps delivery, or strategic decision framing.
2. Ask one clarifying question only when the answer changes the owner.
3. Invoke one primary specialist with `/skill-name`. Add another specialist
   only for a second independently owned deliverable.
4. Load `references/routing-matrix.md` when lane choice is not obvious,
   including adjacent-owner cases and multi-deliverable order.

## Direct specialists

- `/internal-azure-organization-structure` — hierarchy, subscriptions,
  landing zones, residency, and platform topology.
- `/internal-azure-governance` — RBAC, workload identity, PIM/PAM, Policy,
  tagging, guardrails, and exceptions.
- `/internal-azure-operations` — preflight, observability, rollout evidence,
  backup/restore proof, continuity validation, and reporting.
- `/internal-azure-devops` — Azure DevOps pipelines, environments, and project
  automation.
- `/internal-azure-strategic` — explicit Azure decision framing, options,
  proportional lenses, and recommendation.

## Completion criteria

The selected specialist owns the requested deliverable, any secondary owner is
independently justified, and the response includes the specialist's required
validation or evidence conditions.
