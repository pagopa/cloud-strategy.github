---
name: internal-gateway-critical-master
description: Use when a repository-owned plan, proposal, or decision needs a critical challenge, pre-mortem, hidden-assumption test, failure-mode analysis, or lateral reframe before action.
---

# Internal Gateway Critical Master

Use this skill as the portable core for critical challenge work. Copilot may expose `internal-gateway-critical-master` as a wrapper agent, but the reusable pressure-test method lives here so runtimes without agent UI can still use it directly.

## When to use

- A repository-owned plan, proposal, decision, or assumption set needs pressure before action.
- The main risk is weak reasoning, hidden assumptions, failure modes, or overfit framing.
- A runtime without Copilot agent UI needs the critical challenge method directly from a skill.
- A Copilot critical wrapper needs the shared semantic owner for challenge behavior.

## When not to use

- The next step is final planning, implementation, or evidence-first review; use the relevant mode in `internal-gateway-operational-flow`.
- The user wants open-ended brainstorming without a proposal or decision to challenge.
- The task is source-side sync governance or consumer baseline propagation.

## Core Contract

- Challenge one proposal, plan, decision, or assumption set at a time.
- Open with the strongest objection or assumption gap, not a broad list.
- Use the artifact and the smallest local evidence needed for the challenge.
  Do not open validators, tests, or neighboring references unless a specific
  claim depends on their exact content.
- Pressure-test upside as well as downside: identify what the current framing may be preventing, overcomplicating, or falsely treating as mandatory.
- Do not implement, routine-review, or finalize the plan through this skill.
- Close with one explicit outcome: `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`.
- Use `internal-agent-support-next-step` when the challenge ends with a recommended owner, scope, action, validation path, and risk note.
- Use `internal-agent-support-lane-change-engine` when the main need has shifted to planning, delivery, or evidence-first review.

## Challenge Workflow

Before applying a lens, name the claim, decision, or artifact under challenge in one sentence and separate it from prior reasoning.

1. Identify the single strongest objection or assumption gap.
2. Explain why it matters now.
3. Apply one useful lens: inversion, counterfactual, role reversal, scope compression, time shift, or opportunity cost.
4. Produce a closing synthesis instead of endless skepticism.
5. Run the final consistency gate: ask what is most likely correct and what may be incorrect, contradictory, overstated, or hallucinated.
6. Reconcile the gate before responding, preserving supported pressure points and downgrading uncertainty.

## Boundaries

- Use `internal-gateway-operational-flow` `plan-only` or `full-cycle` when the main job is reformulating the plan.
- Use `internal-gateway-simple-task` when the critique shows the remaining work is concrete and does not need staged planning.
- Use `internal-gateway-operational-flow` `execute` or `apply-plan` when the next step is a clear implementation with a visible checkpoint.
- Use `internal-gateway-operational-flow` `review` when the next step is evidence-based validation of a concrete change.
- Stay here only while the primary need is pressure-testing reasoning, assumptions, or failure modes.

## Outcome Routing

| Outcome | Use when | Recommended next owner |
| --- | --- | --- |
| `reformulate-plan` | The critique changes scope, assumptions, owner, or validation enough that planning must rewrite the plan. | `internal-gateway-operational-flow` `plan-only` or `full-cycle` |
| `de-escalate-to-simple` | The strongest objection removes process weight and leaves a concrete local task. | `internal-gateway-simple-task` |
| `execute-clear-next-step` | The plan survives the challenge and the user has approved execute/apply or the prompt already allowed end-to-end work. | `internal-gateway-operational-flow` `execute` or `apply-plan` |
| `review-evidence` | The next risk is correctness evidence for an existing artifact or validation result. | `internal-gateway-operational-flow` `review` |
| `continue-critical` | The first challenge exposes another unresolved assumption that still belongs to pressure testing. | `internal-gateway-critical-master` |
| `accept-with-risk` | The user may proceed while accepting a named residual risk. | Current workflow with explicit risk note |

Use `internal-agent-support-next-step` for every outcome that asks another owner to act. Keep `accept-with-risk` explicit; it is not a success claim.

## References

- Read `references/challenge-lenses.md` for detailed lenses, engagement rules, final gate prompts, and output patterns.

## Validation

- The response challenges one artifact or assumption set.
- The strongest supported objection leads.
- Unsupported claims are downgraded or named as uncertainty.
- The skill does not implement fixes or act as a routine code reviewer.
- The outcome is one of the explicit routing outcomes.
- The next owner is recommended visibly when the challenge lane no longer fits.
