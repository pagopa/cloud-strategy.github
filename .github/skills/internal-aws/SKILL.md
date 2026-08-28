---
name: internal-aws
description: Use first for every AWS request. Classify the primary deliverable and invoke the minimum specialist lane for AWS structure, governance, operations, Lambda, current documentation or IAM evidence, strategic decisions, or cost optimization.
---

# Internal AWS

Classify the requested result and invoke the minimum specialist lane. This
router owns composition; it supplies no AWS domain answer of its own.

## When to use

## Destinations

| Primary deliverable | Invoke |
| --- | --- |
| Account, OU, delegated administrator, StackSets, or structural network placement | `/internal-aws-organization-structure` |
| IAM, trust, federation, SCP, permission boundary, or access guardrail | `/internal-aws-governance` |
| Monitoring, rollout proof, backup, restore, DR evidence, reporting, or audit evidence | `/internal-aws-operations` |
| Lambda handler, event source, runtime, packaging, retry, or cold-start behavior | `/internal-aws-lambda` |
| Current AWS documentation, regional availability, service behavior, IAM observation, or policy simulation | `/internal-aws-mcp-research` |
| AWS option comparison, tradeoff, cost-value decision, blast radius, or reversibility | `/internal-aws-strategic` |
| AWS spend analysis or savings opportunity as the primary result | `/antigravity-aws-cost-optimizer` |

## Workflow

1. Identify the requested result.
2. Select one primary lane from the destination table.
3. Ask one focused question only when two lanes remain equally plausible because the requested result is missing.
4. Invoke the selected `/skill-name` and continue under its instructions.
5. Sequence another lane only for a second explicit deliverable. Research may precede a decision when a current fact controls the recommendation; operations may follow a design lane when proof is explicitly requested.

Load `references/routing-matrix.md` when the owner choice is not obvious.

## Completion

Every requested deliverable has one owner, the minimum sequence was invoked, and
this router supplied no AWS domain answer of its own.
