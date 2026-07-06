---
name: internal-gateway-critical-master
description: Use when a repository-owned plan, proposal, or decision needs a critical challenge, pre-mortem, hidden-assumption test, failure-mode analysis, or lateral reframe before action.
---

# Internal Gateway Critical Master

## Referenced skills

- None.

Use this skill as the portable core for critical challenge work. The calling
gateway decides when to invoke it; this skill challenges only.

## When to use

- A repository-owned plan, proposal, decision, or assumption set needs pressure before action.

## When not to use

- The next step is retained planning, implementation, or evidence-first review.

## Boundaries

- This skill challenges; it does not edit files, run commands, or author retained plans.

## Critical Procedure

Run exactly three phases. Do not skip a phase and do not loop back unless new evidence appears.

### Phase 1: Discover

- Read only the smallest evidence needed to understand the proposal, decision, or assumption set.
- Identify the material claims, constraints, success criteria, and anti-scope.
- Output: a one-paragraph summary of what is being challenged and why it matters now.

### Phase 2: Challenge

- Select **2-3 lenses** from the table below based on the highest-risk gaps in the summary.
- The **third lens must be lateral**: `analogy` or `reverse assumption`.
- Apply one optional pre-mortem pass if failure modes are material and not covered by the selected lenses.
- Lead with the strongest supported objection first. Stop at one finding when that objection controls the decision; do not pad findings.
- Ask exactly one concise root question only when the answer would materially change the critique.
- Output: 1-3 raw findings, each with a claim class and a note on evidence quality.

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

Trigger a pre-mortem when at least one of these is true:

- The proposal depends on coordination across teams, systems, or sync cycles.
- A missed assumption could cause rollback, incident, or governance breach.
- The plan introduces a new operational owner, on-call rotation, or handoff.
- The change affects a production path and cannot be rolled back in under one hour.

For a pre-mortem, state one concrete failure, list the 2-3 most likely root causes with classification and probability, and define a required mitigation for each `high` or `medium` cause.

### Phase 3: Synthesize

- Run the Final Consistency Gate: name the strongest supported objection, downgrade weak claims to hypotheses, and surface unresolved uncertainty.
- When the user has already defended the proposal, include the strongest defense and the remaining vulnerability inside the synthesis.
- Format the result using the contract in `references/output-contract.md`.
- Recommend exactly one outcome from `## Outcome meanings`.

## Token Budget

- Target output: **600 words or fewer** per challenge cycle.
- Maximum findings: **3**.
- Maximum per finding: **150 words**.
- Maximum synthesis: **300 words**.
- If the topic demands more depth, split the work into another critical cycle.

## Claim Discipline

- Classify material claims as `confirmed`, `inference`, or `estimate`.
- Do not present unsupported numeric precision as measured fact.
- Preserve traceability between original intent and emerged requirements; do not rewrite emerged constraints as original intent.
- Keep claim labeling lightweight and focused on material decisions, critiques, and risk framing.

## Tooling

- Optional: `scripts/validate_critical_output.py` checks a rendered output against the contract in `references/output-contract.md`.
- The optional validator and its pure helper live inside this skill bundle so the skill can be copied without depending on repo-global Python modules.
- Reuse `fixtures/critical_output_valid.md` and sibling fixture samples instead of repeating long inline payloads.
- Follow `references/maintenance-guidance.md` for fixture reuse, cache-aware search discipline, and analyzer boundary checks.
- Keep this bundle self-contained: do not require instructions, examples, or enforcement rules from outside this directory.

## Outcome meanings

| Outcome | Use when |
| --- | --- |
| `reformulate-plan` | Planning must be rewritten. |
| `de-escalate-to-simple` | A concrete local task remains. |
| `execute-clear-next-step` | Execution is approved and clear. |
| `review-evidence` | The next risk is correctness evidence. |
| `continue-critical` | Another pressure-test loop is needed. |
| `accept-with-risk` | The user may proceed while accepting a named residual risk. |
