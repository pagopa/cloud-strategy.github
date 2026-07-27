---
name: internal-azure-strategic
description: Use when you need high-level Azure decision support, tradeoff framing, or multi-lens analysis before implementation, or when internal-azure routes a strategic question here. Invoke manually ($internal-azure-strategic) or via internal-azure handoff. Do not use for clearly scoped specialist tasks with a known owner.
disable-model-invocation: true
---

# Internal Azure Strategic

Strategic support skill for high-level Azure decision framing. Reached via `internal-azure` handoff or explicit manual invocation. Identify the decision first, not the implementation tool, and hand back to `internal-azure` for specialist routing once the direction is chosen.

## When to use

Use this skill for high-level Azure decision support, tradeoff framing, or multi-lens analysis before implementation. Do not use it for clearly scoped specialist tasks with a known owner; those belong to the specialists via `internal-azure`.

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

Load `references/lens-playbook.md` when the user wants a deeper framing aid or when the choice of lenses is not obvious.

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about resilience, backup, recovery, failover, RTO, RPO, Site Recovery, or regional continuity
- the decision has clear continuity implications
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use current Microsoft documentation only when freshness materially affects the answer, especially for Azure service support, landing-zone guidance updates, Policy behavior, RBAC semantics, regional capability, or service limits.

Do not invoke current-doc research by default for stable, generic reasoning.

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

## Anti-patterns

- forcing a full multi-lens analysis for a small question
- treating BC/DR as mandatory for every answer
- recommending a direction without current-source verification when freshness matters
- expanding into tool selection when the user did not ask for it
- giving generic best-practice advice without context, tradeoff, or cost implication
- retaining ownership after the direction is chosen instead of handing back to `internal-azure` for specialist routing

## Validation

- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm assumptions, active lenses, and the main tradeoff are named instead of implied.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and which current Microsoft fact still needs validation.
