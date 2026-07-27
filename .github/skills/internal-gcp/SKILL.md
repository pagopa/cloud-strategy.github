---
name: internal-gcp
description: Route any Google Cloud request to organization structure, governance, operations, or strategic decision support. Use internal-gcp as the official and default GCP entry point for scoped, ambiguous, or cross-domain work.
---

# Internal GCP

`internal-gcp` is the official and default router for Google Cloud work.

## When to use

Use this skill for any Google Cloud request when the primary deliverable must be classified.

## Route by primary deliverable

| Primary deliverable | Invoke |
| --- | --- |
| Organization, folder, billing-account, project, Shared VPC, environment, or regional placement | `/internal-gcp-organization-structure` |
| IAM, workload identity, service-account, Org Policy, inherited guardrail, or governed exception | `/internal-gcp-governance` |
| Monitoring, logging, backup, restore, recovery, inventory, rollout validation, reporting, or evidence | `/internal-gcp-operations` |
| Decision framing, option comparison, tradeoff analysis, or recommendation before implementation | `/internal-gcp-strategic` |

## Routing process

1. Identify the next concrete deliverable.
2. Select one primary owner for that lane.
3. Ask one clarifying question only when the deliverable cannot be determined.
4. Invoke the selected skill and apply its instructions for the remainder of the lane.

For multi-domain requests, route by the primary deliverable rather than domain count. Sequence another lane only when the request contains a second independent deliverable.

Load `references/routing-matrix.md` only when the primary deliverable remains ambiguous after the first reading.

## Completion

- One primary owner is selected for the active lane.
- The selected owner is invoked using `/skill-name`.
- Any later lane is ordered by deliverable dependency.
