---
name: internal-github-strategic
description: Use when you need high-level GitHub platform or operating-model decision support, tradeoff framing, or multi-lens analysis before implementation, or when internal-github routes a strategic question here. Invoke manually ($internal-github-strategic) or via internal-github handoff. Do not use for clearly scoped specialist tasks with a known owner.
disable-model-invocation: true
---

# Internal GitHub Strategic

Strategic support skill for high-level GitHub platform and operating-model decision framing. Reached via `internal-github` handoff or explicit manual invocation. Identify the decision first, not the implementation tool, and hand back to `internal-github` for specialist routing once the direction is chosen.

## When to use

Use this skill for high-level GitHub platform or operating-model decision support, tradeoff framing, or multi-lens analysis before implementation. Do not use it for clearly scoped specialist tasks with a known owner; those belong to the specialists via `internal-github`.

## Optional lens activation

Do not load every lens by default.

Use only the minimum set of lenses needed for the request. If the user explicitly names one or more lenses, prioritize only those. If the user does not name lenses, infer the smallest useful set.

Available lenses include:

- security
- identity and access
- organization and repo model
- governance
- operations
- runner model
- Copilot
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

Load `references/strategic-framing.md` when the choice of GitHub lens needs worked lens combinations, decision-note depth, or worked-shape comparison before handoff.

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about delivery continuity, runner resilience, backup, recovery, or failover expectations
- the decision has clear continuity implications for build, release, or repository operations
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use current GitHub documentation only when freshness materially affects the answer. When the question is about Copilot or MCP behavior specifically, hand back to `internal-github` to route to `internal-copilot-docs-research` instead of answering from memory.

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

- Forcing a full multi-lens analysis for a small question.
- Recommending implementation tooling when the user only asked for decision framing.
- Invoking current-doc research by default for stable, generic reasoning.
- Retaining ownership after the direction is chosen instead of handing back to `internal-github` for specialist routing.

## Validation

- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm lenses, when used, are the minimum set and named explicitly when more than one is active.
- Confirm assumptions, tradeoffs, and the next owner are explicit.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact, including licensing or runner cost, is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and whether current GitHub or Copilot behavior still needs verification.
