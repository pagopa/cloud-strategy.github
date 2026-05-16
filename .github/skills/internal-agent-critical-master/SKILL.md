---
name: internal-agent-critical-master
description: Use when a repository-owned plan, proposal, or decision needs a critical challenge, pre-mortem, hidden-assumption test, failure-mode analysis, or lateral reframe before action.
---

# Internal Agent Critical Master

Use this skill as the portable core for critical challenge work. Copilot may expose `internal-critical-master` as a wrapper agent, but the reusable pressure-test method lives here so runtimes without agent UI can still use it directly.

## When to use

- A repository-owned plan, proposal, decision, or assumption set needs pressure before action.
- The main risk is weak reasoning, hidden assumptions, failure modes, or overfit framing.
- A runtime without Copilot agent UI needs the critical challenge method directly from a skill.
- A Copilot critical wrapper needs the shared semantic owner for challenge behavior.

## When not to use

- The next step is final planning, implementation, or evidence-first review; use the relevant mode in `internal-agent-operational-flow`.
- The user wants open-ended brainstorming without a proposal or decision to challenge.
- The task is source-side sync governance or consumer baseline propagation.

## Core Contract

- Challenge one proposal, plan, decision, or assumption set at a time.
- Open with the strongest objection or assumption gap, not a broad list.
- Pressure-test upside as well as downside: identify what the current framing may be preventing, overcomplicating, or falsely treating as mandatory.
- Do not implement, routine-review, or finalize the plan through this skill.
- Use `internal-agent-support-next-step` when the challenge ends with a recommended owner, scope, action, validation path, and risk note.
- Use `internal-agent-support-lane-change-engine` when the main need has shifted to planning, delivery, or evidence-first review.

## Challenge Workflow

1. Identify the single strongest objection or assumption gap.
2. Explain why it matters now.
3. Apply one useful lens: inversion, counterfactual, role reversal, scope compression, time shift, or opportunity cost.
4. Produce a closing synthesis instead of endless skepticism.
5. Run the final consistency gate: ask what is most likely correct and what may be incorrect, contradictory, overstated, or hallucinated.
6. Reconcile the gate before responding, preserving supported pressure points and downgrading uncertainty.

## Boundaries

- Use `internal-agent-operational-flow` `plan` mode when the main job is reformulating the plan.
- Use `internal-agent-operational-flow` `execute` mode when the next step is a clear implementation.
- Use `internal-agent-operational-flow` `review` mode when the next step is evidence-based validation of a concrete change.
- Stay here only while the primary need is pressure-testing reasoning, assumptions, or failure modes.

## References

- Read `references/challenge-lenses.md` for detailed lenses, engagement rules, final gate prompts, and output patterns.

## Validation

- The response challenges one artifact or assumption set.
- The strongest supported objection leads.
- Unsupported claims are downgraded or named as uncertainty.
- The skill does not implement fixes or act as a routine code reviewer.
- The next owner is recommended visibly when the challenge lane no longer fits.
