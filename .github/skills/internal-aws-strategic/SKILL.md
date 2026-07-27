---
name: internal-aws-strategic
description: Use when you need high-level AWS decision support, tradeoff framing, or multi-lens analysis before implementation, or when internal-aws routes a strategic question here. Invoke manually ($internal-aws-strategic) or via internal-aws handoff. Do not use for clearly scoped specialist tasks with a known owner.
disable-model-invocation: true
---

# Internal AWS Strategic

Strategic support skill for high-level AWS decision framing. Reached via `internal-aws` handoff or explicit manual invocation. Identify the decision first, not the implementation tool, and hand back to `internal-aws` for specialist routing once the direction is chosen.

## When to use

Use this skill for high-level AWS decision support, tradeoff framing, or multi-lens analysis before implementation. Do not use it for clearly scoped specialist tasks with a known owner; those belong to the specialists via `internal-aws`.

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

Load `references/lens-playbook.md` when the choice of AWS lens needs structured comparison or when the user wants a deeper decision-framing aid.

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
| Confusing decision support with implementation guidance | The user loses the strategic framing they asked for | Keep the answer at decision level and hand back to `internal-aws` after the direction is chosen |
| Expanding into tool or IaC selection when the user did not ask for it | The response drifts from AWS platform tradeoffs into execution detail | Keep the recommendation centered on the AWS choice, not the delivery tooling |
| Giving generic best-practice advice without context, tradeoff, or cost implication | Generic guidance is hard to act on and easy to misapply | Tie the recommendation to assumptions, viable options, and cost-value consequences |

## Validation

- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm assumptions, active lenses, and the main tradeoff are named instead of implied.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and whether `internal-aws-mcp-research` should be used.
