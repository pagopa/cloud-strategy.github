---
name: internal-gcp
description: Use first for every Google Cloud request. Classify the primary deliverable and select the minimum specialist lane (organization structure, governance, operations, strategic).
---

# Internal GCP

The Google Cloud entry point. Classify the primary deliverable and invoke the
specialist that owns it.

## When to use

Use for any Google Cloud request whose primary deliverable must be classified.

## Destinations

| Primary deliverable | Invoke |
| --- | --- |
| Organization, folder, billing-account, project, Shared VPC, environment, or regional placement | `/internal-gcp-organization-structure` |
| IAM, workload identity, service-account, Org Policy, inherited guardrail, or governed exception | `/internal-gcp-governance` |
| Monitoring, logging, backup, restore, recovery, inventory, rollout validation, reporting, or evidence | `/internal-gcp-operations` |
| Decision framing, option comparison, tradeoff analysis, or recommendation before implementation | `/internal-gcp-strategic` |

## Workflow

1. Identify the next concrete deliverable.
2. Select one primary owner for that lane.
3. Ask one clarifying question only when the deliverable cannot be determined.
4. Invoke the selected skill and apply its instructions for the remainder of
   the lane.

## References

- [`references/routing-matrix.md`](references/routing-matrix.md): load when
  more than one lane could claim a multi-domain request.

## Completion criteria

- One primary owner is selected for the active lane.
- Any later lane is ordered by deliverable dependency.
