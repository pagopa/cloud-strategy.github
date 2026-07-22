---
name: internal-aws
description: Use when an AWS task cannot be routed confidently to a specific AWS skill because the request is materially ambiguous, has multiple AWS domains with no clear primary owner, or requires clarification before selecting the correct specialist, or when the user needs high-level AWS platform decision support or tradeoff framing before implementation. Do not use for clearly scoped organization structure, governance or IAM, operations or validation, Lambda, or current AWS documentation research tasks.
---

# Internal AWS

Fallback router for AWS tasks that cannot be assigned confidently to one specialist, and strategic support skill for high-level AWS decision framing. Do not activate only because the task concerns AWS; activate only when material routing uncertainty blocks owner selection or when the user needs decision support before the next step is structure, governance, operations, or delivery.

## When to use

- Material ambiguity prevents selecting one primary AWS specialist.
- Multiple AWS domains are material and no primary owner can be identified safely.
- The user explicitly invokes `$internal-aws`.
- The task asks which AWS lane should own the work before requesting a domain solution.
- The user needs high-level AWS decision support or tradeoff framing before implementation.

## When not to use

- The task is already a clear implementation change.
- The user only needs detailed IAM, SCP, monitoring, backup, or Lambda implementation detail.
- The task is purely post-rollout validation or evidence gathering.
- The request is narrow and operational with no real decision to frame.

## Routing threshold

Activate only when at least one holds:

- the request is materially ambiguous and clarification is required before an AWS owner can be selected;
- multiple AWS domains are material and no primary owner can be identified safely;
- the task asks which AWS problem-solving lane should own the work;
- the user needs strategic decision framing and the next step is not yet structure, governance, operations, or delivery.

Do not activate when one specialist clearly owns the next step; route directly to that specialist instead. Explicit `$internal-aws` invocation remains valid.

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

Load `references/routing-matrix.md` for the routing decision tree. Load `references/lens-playbook.md` when the fallback trigger fires and the choice of AWS owner or lens needs structured comparison, or when the user wants a deeper decision-framing aid.

## Optional lens activation

Do not load every lens by default.

Use only the minimum set of lenses needed for the request. If the user explicitly names one or more lenses, prioritize only those. If the user does not name lenses, infer the smallest useful set.

Available lenses include:

- security
- identity and access
- organization-structure
- governance
- operations
- monitoring and observability
- BC/DR
- FinOps
- compliance
- rollout and rollback
- blast radius
- maintainability

Rules:

- Start narrow.
- Expand only when the request is broad, risky, or ambiguous.
- If another lens would materially improve the recommendation, suggest it briefly instead of forcing it.
- Keep the active lenses explicit when more than one is in play.

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about resilience, backup, recovery, failover, RTO, RPO, or multi-region design
- the decision has clear continuity implications
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use `internal-aws-mcp-research` when the answer depends on current AWS documentation, service behavior, IAM semantics, support boundaries, limits, or updated best-practice guidance.

Do not invoke research by default for stable, generic reasoning. Use it when freshness materially affects the answer.

## Mandatory behavior

- Identify the decision first, not the implementation tool.
- Make assumptions explicit.
- Compare realistic options, not strawmen.
- Keep tradeoffs concrete.
- Surface material risk, blast radius, and reversibility when relevant.
- Include cost-value considerations when they matter to the decision.
- Stay proportional to the size of the question.

## Adaptive output modes

Choose the lightest output that fits the request.

### Quick answer

Use for narrow asks.

Include:

- direct recommendation
- short rationale
- optional risk or follow-up note

### Decision note

Use for normal strategic support.

Include:

- decision statement
- key options or tradeoff
- recommended direction
- main risk or validation note

### Deep analysis

Use only for broad, ambiguous, high-risk, or explicitly detailed requests.

Include:

- context and assumptions
- options considered
- active lenses used
- recommendation and why it wins
- main risks and blast radius
- validation or follow-up path

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Forcing a full multi-lens analysis for a small question | The answer becomes heavier than the decision requires | Start with the smallest useful lens set and widen only if risk or ambiguity justifies it |
| Treating BC/DR as mandatory for every answer | Continuity language crowds out the actual AWS tradeoff | Activate BC/DR only when recovery posture or multi-region continuity changes the recommendation |
| Recommending a direction without current-source verification when freshness matters | AWS support boundaries, limits, or service behavior may have changed | Call out the freshness dependency and route to `internal-aws-mcp-research` when it can change the decision |
| Confusing decision support with implementation guidance | The user loses the strategic framing they asked for | Keep the answer at decision level and hand off only after the direction is chosen |
| Expanding into tool or IaC selection when the user did not ask for it | The response drifts from AWS platform tradeoffs into execution detail | Keep the recommendation centered on the AWS choice, not the delivery tooling |
| Activating the fallback when one specialist clearly owns the next step | The router delays work a direct specialist should own | Route directly to the specialist and keep the fallback for genuine uncertainty |
| Giving generic best-practice advice without context, tradeoff, or cost implication | Generic guidance is hard to act on and easy to misapply | Tie the recommendation to assumptions, viable options, and cost-value consequences |

## Validation

- State why the request could not be assigned to one primary AWS specialist, or name the decision being framed.
- Confirm the selected specialist set is the minimum needed to resolve the uncertainty.
- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm assumptions, active lenses, and the main tradeoff are named instead of implied.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and whether `internal-aws-mcp-research` should be used.
- Confirm the resolved task is handed to a primary specialist.
