---
name: internal-gateway-critical-master
description: Use when a repository-owned plan, proposal, or decision needs a critical challenge, pre-mortem, hidden-assumption test, failure-mode analysis, or lateral reframe before action.
---

# Internal Gateway Critical Master

Use this skill as the portable core for critical challenge work.

## Referenced skills

Load these references only when the active phase requires them.

- `references/challenge-lenses.md`: lens selection and structured challenge questions.
- `references/pre-mortem.md`: failure-mode pressure test.
- `references/output-contract.md`: required output shape and token budget.

## When to use

- A repository-owned plan, proposal, decision, or assumption set needs pressure before action.

## When not to use

- The next step is retained planning, implementation, or evidence-first review; use `internal-gateway-idea-brainstorming`, `internal-gateway-simple-task`, `internal-gateway-execute-plans`, or `internal-gateway-review`.

## Boundaries

- Use `internal-gateway-idea-brainstorming` when the main job is reformulating the plan.
- Use `internal-gateway-simple-task` when the critique leaves a concrete local task.
- Use `internal-gateway-execute-plans` for approved `compact` and `extended` retained-plan execution.
- Use `internal-gateway-review` when the next step is evidence-based validation of a concrete change.
- This skill challenges; it does not edit files, run commands, or author retained plans.

## Critical Procedure

Run exactly three phases. Do not skip a phase and do not loop back unless new evidence appears.

### Phase 1: Discover

- Read only the smallest evidence needed to understand the proposal, decision, or assumption set.
- Identify the material claims, constraints, success criteria, and anti-scope.
- Output: a one-paragraph summary of what is being challenged and why it matters now.

### Phase 2: Challenge

- Select **2-3 lenses** from `references/challenge-lenses.md` based on the highest-risk gaps in the summary.
- The **third lens must be lateral**: `analogy` or `reverse assumption`.
- Apply one optional pre-mortem pass from `references/pre-mortem.md` if failure modes are material and not covered by the selected lenses.
- Ask probing questions only when the answer changes the critique.
- Output: 1-3 raw findings, each with a claim class and a note on evidence quality.

### Phase 3: Synthesize

- Run the Final Consistency Gate from `references/challenge-lenses.md`.
- Downgrade weak claims to hypotheses; name unresolved uncertainty explicitly.
- Format the result using the contract in `references/output-contract.md`.
- Recommend exactly one outcome from `## Outcome Routing`.

## Token Budget

- Target output: **600 words or fewer** per challenge cycle.
- Maximum findings: **3**.
- Maximum per finding: **150 words**.
- Maximum synthesis: **300 words**.
- If the topic demands more depth, split the work and route to `continue-critical`.

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
