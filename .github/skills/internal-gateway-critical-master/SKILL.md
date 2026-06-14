---
name: internal-gateway-critical-master
description: Use when a repository-owned plan, proposal, or decision needs a critical challenge, pre-mortem, hidden-assumption test, failure-mode analysis, or lateral reframe before action.
---

# Internal Gateway Critical Master

Use this skill as the portable core for critical challenge work.

## When to use

- A repository-owned plan, proposal, decision, or assumption set needs pressure before action.

## When not to use

- The next step is retained planning, implementation, or evidence-first review; use `internal-gateway-idea-brainstorming`, `internal-gateway-simple-task`, `internal-gateway-execute-plans`, or `internal-gateway-review`.

## Boundaries

- Use `internal-gateway-idea-brainstorming` when the main job is reformulating the plan.
- Use `internal-gateway-simple-task` when the critique leaves a concrete local task.
- Use `internal-gateway-execute-plans` for approved `compact` and `extended` retained-plan execution.
- Use `internal-gateway-review` when the next step is evidence-based validation of a concrete change.

## Claim Discipline

- Classify material claims as `confirmed`, `inference`, or `estimate`.
- Do not present unsupported numeric precision as measured fact.
- Preserve traceability between original intent and emerged requirements; do not rewrite emerged constraints as original intent.
- Keep claim labeling lightweight and focused on material decisions, critiques, and risk framing.

## Outcome Routing

| Outcome | Use when | Recommended next owner |
| --- | --- | --- |
| `reformulate-plan` | Planning must be rewritten. | `internal-gateway-idea-brainstorming` |
| `de-escalate-to-simple` | A concrete local task remains. | `internal-gateway-simple-task` |
| `execute-clear-next-step` | Execution is approved and clear. | `internal-gateway-simple-task` or `internal-gateway-execute-plans` |
| `review-evidence` | The next risk is correctness evidence. | `internal-gateway-review` |
| `continue-critical` | Another pressure-test loop is needed. | `internal-gateway-critical-master` |
| `accept-with-risk` | The user may proceed while accepting a named residual risk. | Current workflow with explicit risk note |
