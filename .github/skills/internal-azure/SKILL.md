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

## Destinations

| Immediate deliverable | Invoke |
| --- | --- |
| Hierarchy, subscriptions, landing zones, residency, or platform topology | `/internal-azure-organization-structure` |
| RBAC, workload identity, PIM/PAM, Policy, tagging, guardrails, or exceptions | `/internal-azure-governance` |
| Preflight, observability, rollout evidence, backup/restore proof, continuity validation, or reporting | `/internal-azure-operations` |
| Azure DevOps pipelines, environments, or project automation | `/internal-azure-devops` |
| Explicit Azure decision framing, options, proportional lenses, or recommendation | `/internal-azure-strategic` |

## Workflow

1. Identify the immediate deliverable: organization structure, governance,
   operations evidence, Azure DevOps delivery, or strategic decision framing.
2. Ask one clarifying question only when the answer changes the owner.
3. Invoke one primary specialist from the destination table with
   `/skill-name`. Add another specialist only for a second independently owned
   deliverable.
4. Verify every item in Completion criteria before finishing.

## References

- [`references/routing-matrix.md`](references/routing-matrix.md): load when
  lane choice is not obvious, including adjacent-owner cases and
  multi-deliverable order.

## Completion criteria

- The selected specialist owns the requested deliverable.
- Any secondary owner is independently justified.
- The response includes the specialist's required validation or evidence
  conditions.
