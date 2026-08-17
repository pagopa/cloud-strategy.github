---
name: internal-aws-strategic
description: Use when /internal-aws selects the AWS strategic lane for option comparison, multi-lens tradeoffs, cost-value analysis, blast radius, or reversibility before implementation.
---

# Internal AWS Strategic

Frame AWS decisions at the option and tradeoff level. Produce a recommendation
with explicit assumptions, relevant lenses, cost-value implications, blast
radius, reversibility, and remaining evidence requirements.

## When to use

Use this lane when the requested result is an AWS option comparison, tradeoff,
cost-value decision, or risk decision before implementation. Keep clearly
scoped structure, governance, operations, research, and Lambda work in its
positive domain lane.

## Optional lens activation

Use only the minimum set of lenses needed for the request. If the user names
lenses, prioritize those. Otherwise infer the smallest useful set from the
decision.

Start narrow and expand only when the request is broad, risky, or ambiguous.
Keep active lenses explicit when more than one is in play.

For lens selection or combination guidance, load
`references/lens-playbook.md`. Activate BC/DR only when resilience, backup,
recovery, failover, RTO, RPO, or multi-region continuity changes the
recommendation; otherwise state that the continuity lens was not material.

## Freshness dependency

When current AWS documentation, service behavior, IAM semantics, support
boundaries, limits, or updated guidance can change the decision, state the
required current-fact evidence and the affected assumption. Do not present an
unverified current fact as settled.

## Mandatory behavior

- Identify the decision before discussing implementation tools.
- Make assumptions explicit.
- Compare two or three realistic options, not strawmen.
- Keep tradeoffs concrete.
- Surface material risk, blast radius, and reversibility.
- Include cost-value considerations when they matter.
- Stay proportional to the size of the question.

## Adaptive output modes

### Quick answer

Use for narrow asks. Include a direct recommendation, short rationale, and an
optional risk or evidence note.

### Decision note

Use when at least two viable options exist. Include the decision statement,
assumptions, options, recommendation, strongest tradeoff, and validation note.

### Deep analysis

Use for broad, ambiguous, high-risk, or explicitly detailed requests. Include
context, assumptions, active lenses, options, recommendation, risks, blast
radius, reversibility, and evidence requirements.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Forcing full multi-lens analysis for a small question | The answer becomes heavier than the decision requires | Start with the smallest useful lens set |
| Recommending a direction without current-source verification when freshness matters | Support boundaries or limits may have changed | Call out the freshness dependency and unresolved evidence |
| Confusing decision support with implementation guidance | The requested decision becomes hard to evaluate | Keep the answer at decision level |
| Expanding into tool or IaC selection without a request | The response drifts from AWS platform tradeoffs | Center the recommendation on the AWS choice |
| Giving generic advice without context or cost implication | The result is hard to act on and easy to misapply | Tie it to assumptions, options, tradeoffs, and value |

## Completion contract

- The decision statement is explicit and narrow enough to evaluate.
- Assumptions, active lenses, and strongest tradeoff are named.
- Reversibility or blast-radius guidance is included when material.
- Cost-value or operational impact is called out when it changes the decision.
- Freshness dependencies and unresolved evidence gaps are visible.
