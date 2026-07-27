---
name: internal-gcp-strategic
description: Use when /internal-gcp selects strategic decision support for a Google Cloud decision, assumptions, realistic options, tradeoffs, reversibility, or a recommendation before implementation.
---

# Internal GCP Strategic

## Purpose

Frame a Google Cloud decision with explicit assumptions, realistic options, concrete tradeoffs, reversibility, cost-value impact, and a recommendation proportional to the question.

## When to use

Use this skill when the requested deliverable is a Google Cloud decision comparison or recommendation before implementation.

## Process

1. State the decision and the assumptions that materially shape it.
2. Activate the minimum useful lenses for the decision and keep them explicit.
3. Compare two or three realistic options using concrete value, cost, risk, blast-radius, and reversibility criteria.
4. Recommend one option and explain why it wins under the stated assumptions.
5. Name the fact, proof, or current Google Cloud behavior that still requires validation.

Load `references/lens-playbook.md` only when lens choice or option comparison needs deeper structure.

## Output

Choose the lightest useful format:

- Quick answer: recommendation, short rationale, and material risk.
- Decision note: decision statement, assumptions, options, recommendation, and validation note.
- Deep analysis: context, assumptions, active lenses, options, recommendation, tradeoffs, blast radius, and validation path.

## Completion

- The decision statement is explicit and narrow enough to evaluate.
- Assumptions, active lenses, and the main tradeoff are named.
- The recommendation compares realistic options and includes reversibility or blast-radius guidance when material.
- Cost-value or operational impact is stated when it changes the recommendation.
- The remaining validation fact or proof is explicit.
