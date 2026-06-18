# Challenge Lenses

Use this reference when a pressure test needs more structure than the main skill body should carry.

## Lens selection criteria

Select **2-3 lenses** from the table below. Prioritize by risk, not by completeness.

1. Read the Phase 1 summary from `SKILL.md`.
2. Pick the lens whose question most directly exposes a material failure mode or hidden assumption.
3. Add a second lens that attacks a different dimension (evidence, constraints, stakeholders, time).
4. Add the lateral lens `analogy` or `reverse assumption` if it is not already covered by step 2 or 3.

Stop at 3 lenses unless the proposal has multiple independent material risks.

## Lenses

| Lens | Question | Use when |
| --- | --- | --- |
| First principles | Which claims are evidence-backed, and which are inherited assumptions? | The plan repeats local habits as if they were constraints. |
| Constraint audit | Which limits are real, and which are defaults or untested policies? | The solution seems boxed in too early. |
| Inversion | What would we do if the stated goal were reversed or forbidden? | The current path feels inevitable. |
| Counterfactual | What would be true if the rejected option were actually better? | A tradeoff has been simplified too quickly. |
| Role reversal | What would review, delivery, planning, or the user object to? | The plan optimizes one owner at another owner's cost. |
| Time shift | What breaks after one month, one sync cycle, or one consumer rollout? | The immediate change looks correct but may age badly. |
| Scope compression | What is the smallest version that preserves most value? | The plan may be overengineered. |
| Opportunity cost | What useful path is the plan excluding? | The design is safe but may be too narrow. |
| Analogy | Which solution in a different domain already solved a structurally similar problem? | The team is stuck in familiar patterns. |
| Reverse assumption | What changes if the most obvious assumption here is false? | A key claim has not been tested recently. |

## Engagement Rules

- Keep each challenge thread narrow.
- Ask a probing question only when the answer changes the critique.
- Update the critique when repository evidence contradicts it.
- Stop adding new objections once the closing synthesis is ready.
- If the user wants implementation or plan rewriting, recommend the next owner instead of doing off-lane work.
- Respect the token budget in `SKILL.md`: max 3 findings, max 150 words per finding, max 300 words synthesis.

## Final Consistency Gate

Before closing, answer two adversarial questions internally:

- What is most likely correct in this critique?
- What may be incorrect, contradictory, overstated, or hallucinated?

Then reconcile the answer:

- Keep the strongest supported objection.
- Downgrade weak claims to hypotheses.
- Name unresolved uncertainty explicitly.
- Recommend one explicit outcome from `## Outcome Routing` in `SKILL.md` only after the challenge synthesis is complete.

## Output Pattern

For each finding, produce:

- Strongest objection or assumption gap.
- Why it matters now.
- Evidence or uncertainty.
- Mitigation or condition required before planning or delivery resumes.
- Optional lateral reframe.

Then close with:

- Synthesis after the Final Consistency Gate.
- Explicit outcome: `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`.
- Recommended owner and next-step package when another lane should act.
