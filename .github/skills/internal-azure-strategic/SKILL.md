---
name: internal-azure-strategic
description: Use when /internal-azure selects explicit Azure decision framing, tradeoff analysis, or proportional multi-lens support.
---

# Internal Azure Strategic

Use this workflow for Azure decisions where comparing viable directions is the
immediate deliverable.

## When to use

Use when `/internal-azure` selects the strategic lane: an Azure decision,
tradeoff note, or multi-lens analysis.

## Workflow

1. State the decision statement: the Azure choice and the outcome it must
   support.
2. Record assumptions about current state, constraints, timing, ownership,
   cost, and required evidence.
3. Select the minimum lenses that can change the recommendation and make the
   active lenses explicit.
4. Compare realistic options with concrete tradeoffs, operating impact, and
   cost-value implications when material.
5. Give a recommendation and explain why it wins under the stated assumptions.
6. Record material risk, blast radius, and validation needs.
7. State reversibility and the conditions for staged adoption or rollback.
8. Verify every item in Completion criteria before finishing.

## Proportional output

- Use a quick answer for a narrow choice with one clear direction.
- Use a decision note when two or three viable options require tradeoff review.
- Use deep analysis for broad, consequential, high-risk, or explicitly detailed
  decisions.

## Current facts

Use current Microsoft documentation when freshness about service support,
landing-zone guidance, Policy behavior, regional capability, or service limits
could change the recommendation.

## References

- [`references/lens-playbook.md`](references/lens-playbook.md): load for lens
  combinations, depth selection, and decision-note structure.

## Completion criteria

Return, in this order:

1. Decision statement.
2. Assumptions.
3. Active lenses.
4. Realistic options.
5. Recommendation.
6. Material risk.
7. Reversibility.
8. Validation path.
