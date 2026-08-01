---
name: internal-github-strategic
description: Use when /internal-github routes a GitHub platform or operating-model decision that requires option comparison, tradeoff analysis, or multi-lens strategic framing.
user-invocable: false
---

# Internal GitHub Strategic

Produce a decision for GitHub platform and operating-model choices. This is a
terminal decision deliverable: make the choice legible, recommend a direction,
and state the validation needs that remain before implementation.

## When to use

Use for a GitHub platform or operating-model decision that has multiple viable
options, material tradeoffs, or a need for more than one decision lens.

## Decision workflow

1. State the decision and the outcome it must support.
2. Make assumptions explicit, including current organization model, trust
   posture, continuity needs, licensing limits, and scope.
3. Activate the minimum useful lenses. Name every active lens when more than
   one is needed.
4. Compare realistic options against the decision criteria. Do not use
   strawman alternatives.
5. Recommend one direction and explain why it wins.
6. State tradeoffs, blast radius, reversibility, cost-value impact, and facts
   requiring proof.

## Decision lenses

Use only the lenses that can change the recommendation:

- security and identity and access
- organization and repo model
- governance and compliance
- operations and runner model
- rollout and rollback and blast radius
- Copilot, FinOps, BC/DR, or maintainability

Activate BC/DR when the choice affects delivery continuity, runner resilience,
backup, recovery, or failover. Activate current documentation only when a
fresh platform fact can change the outcome.

Load `references/strategic-framing.md` when worked lens combinations or a
decision-note shape will improve the analysis.

## Adaptive output modes

### Quick answer

Use for a narrow decision with one clearly stronger option. Include the
recommendation, short rationale, and one material risk or validation need.

### Decision note

Use when two or more realistic options remain. Include the decision statement,
assumptions, options, recommendation, tradeoffs, and validation needs.

### Deep analysis

Use for broad, ambiguous, high-risk, or explicitly detailed decisions. Include
context, active lenses, options, recommendation, blast radius, reversibility,
and evidence needed before implementation.

## Completion criteria

- The decision statement is explicit and narrow enough to act on.
- Assumptions and active lenses are visible.
- Viable options are compared against concrete criteria.
- One recommendation is stated with material tradeoffs.
- Blast radius and reversibility are addressed when relevant.
- Validation needs and freshness-sensitive facts are identified.
