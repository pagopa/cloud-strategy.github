---
name: internal-aws
description: Use only when an AWS task cannot be routed confidently to a specific AWS skill because the request is materially ambiguous, has multiple AWS domains with no clear primary owner, or requires clarification before selecting the correct specialist. Do not use for clearly scoped organization structure, governance or IAM, operations or validation, Lambda, or current AWS documentation research tasks.
---

# Internal AWS

Fallback router for AWS tasks that cannot be assigned confidently to one specialist. Do not activate only because the task concerns AWS; activate only when material routing uncertainty blocks owner selection.

## When to use

- Material ambiguity prevents selecting one primary AWS specialist.
- Multiple AWS domains are material and no primary owner can be identified safely.
- The user explicitly invokes `$internal-aws`.
- The task asks which AWS lane should own the work before requesting a domain solution.

## Routing threshold

Activate only when at least one holds:
- the request is materially ambiguous and clarification is required before an AWS owner can be selected;
- multiple AWS domains are material and no primary owner can be identified safely;
- the task asks which AWS problem-solving lane should own the work.

Explicit `$internal-aws` invocation remains valid.

## Handoffs

| To | Owns |
|---|---|
| `internal-aws-organization-structure` | account, OU, delegated admin, StackSets, platform network topology |
| `internal-aws-governance` | IAM, trust, SCP, federation, guardrails |
| `internal-aws-operations` | monitoring, validation, backup, recovery, reporting, evidence |
| `internal-aws-lambda` | Lambda runtime, handler, trigger, packaging, retry |
| `internal-aws-mcp-research` | current AWS documentation and safe IAM inspection |
| `antigravity-aws-cost-optimizer` | AWS-specific cost analysis when cost data is the primary problem |

## Dispatch contract

1. State the routing uncertainty.
2. Identify candidate AWS owners.
3. Select the minimum specialist set.
4. Keep strategic comparison here only while needed to choose the owner.
5. Hand the resolved task to the primary specialist instead of retaining ownership.

Load `references/lens-playbook.md` only when the fallback trigger fires and the choice of AWS owner needs structured comparison. Load `references/routing-matrix.md` for the routing decision tree.

## Anti-scope

- Do not use this fallback for a clearly scoped account/OU request, IAM/SCP design, operational validation, Lambda implementation, current AWS documentation research, or AWS-specific cost analysis. Route those directly to their specialist.

## Validation

- State why the request could not be assigned to one primary AWS specialist.
- Confirm the selected specialist set is the minimum needed to resolve the uncertainty.
- Confirm the resolved task is handed to a primary specialist.
- Keep assumptions, tradeoffs, and the next owner explicit.
