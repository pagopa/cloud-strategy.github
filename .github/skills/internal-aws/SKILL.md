---
name: internal-aws
description: Use only when an AWS task cannot be routed confidently to a specific AWS skill because the request is materially ambiguous, has multiple AWS domains with no clear primary owner, or requires clarification before selecting the correct specialist. Do not use for clearly scoped organization structure, governance or IAM, operations or validation, Lambda, or current AWS documentation research tasks.
---

# Internal AWS

## Referenced skills

- `internal-aws-organization-structure`: account, OU, delegated administrator, and platform-topology owner.
- `internal-aws-governance`: IAM, trust, SCP, federation, and guardrail owner.
- `internal-aws-operations`: monitoring, validation, backup, recovery, reporting, and evidence owner.
- `internal-aws-lambda`: Lambda runtime, handler, trigger, packaging, and retry owner.
- `internal-aws-mcp-research`: current AWS documentation and safe IAM-inspection support.
- `antigravity-aws-cost-optimizer`: AWS-specific cost-analysis depth when cost data is the primary problem.

Use this skill only as a fallback under material routing uncertainty. Do not activate only because the task concerns AWS. Do not activate when one specialist clearly owns the next step.

## When to use

- Use this fallback when material ambiguity prevents selecting one primary AWS specialist.
- Use it when multiple AWS domains are material and no primary owner can be identified safely.
- Use it when the user explicitly invokes `$internal-aws`.

## Routing threshold

Activate only when at least one condition holds:

- the request is materially ambiguous and clarification is required before an AWS owner can be selected;
- multiple AWS domains are material and no primary owner can be identified safely;
- the task asks which AWS problem-solving lane should own the work before requesting a domain solution.

Explicit `$internal-aws` invocation remains valid.

## Dispatch contract

1. State the routing uncertainty.
2. Identify the candidate AWS owners.
3. Select the minimum specialist set.
4. Keep strategic comparison here only while it is needed to choose the owner.
5. Hand the resolved task to the primary specialist instead of retaining ownership.

## Strategic lens

Use `references/lens-playbook.md` only when the fallback trigger fires and the choice of AWS owner needs structured comparison. Keep the active lenses explicit and limit them to the uncertainty being resolved.

Do not use this fallback for a clearly scoped account or OU request, IAM or SCP design, operational validation, Lambda implementation or troubleshooting, current AWS documentation research, or AWS-specific cost analysis. Route those requests directly to their specialist.

## Validation

- State why the request could not be assigned to one primary AWS specialist.
- Confirm that the selected specialist set is the minimum needed to resolve the uncertainty.
- Confirm that the resolved task is handed to a primary specialist.
- Keep assumptions, tradeoffs, and the next owner explicit.
