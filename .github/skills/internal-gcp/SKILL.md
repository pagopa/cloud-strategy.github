---
name: internal-gcp
description: Use first for every Google Cloud request. Classify the primary deliverable and select the minimum specialist lane (organization structure, governance, operations, strategic).
---

# Internal GCP

`internal-gcp` routes Google Cloud work.

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

For multi-domain requests, load `references/routing-matrix.md` when more than one lane could claim the request.

## Completion

- One primary owner is selected for the active lane.
- Any later lane is ordered by deliverable dependency.
