---
name: internal-agent-routing-engine
description: Route repository-owned operational requests between the four canonical owners using intent classification, confidence thresholds, medium-task rules, old-to-new mapping, and fail-safe dispatch. Use when a generic or ambiguous request must be routed to execute, plan, review, or challenge.
---

# Internal Agent Routing Engine

Use this skill as the mandatory engine for `internal-router`.

This skill owns the reusable routing logic. The router stays short: classify, ask at most one high-value question when needed, hand off, and stop. The router never implements.

## Core Rules

- Classify first by intent: execution, planning, review, or challenge.
- Then classify by scale, ambiguity, risk, and boundary-crossing.
- Ask at most one targeted clarification question, and only when it materially improves routing confidence.
- If confidence does not reach a safe routing decision after that question, fail safe to `internal-planning-leader`.
- Do not implement through the router.

## Primary Route Labels

| Label | Canonical owner | Route when |
| --- | --- | --- |
| `route-to-execute` | `internal-fast-executor` | The task is clear, local, low-risk, and has concrete verification. |
| `route-to-plan` | `internal-planning-leader` | The task is ambiguous, cross-boundary, strategic, or changes repository-owned contracts. |
| `route-to-review` | `internal-review-guard` | The user asks for review, validation, merge readiness, regression analysis, or evidence checks. |
| `route-to-challenge` | `internal-critical-challenger` | The user wants assumptions challenged, a pre-mortem, or failure modes surfaced. |

## Confidence Model

| Confidence | Meaning | Router action |
| --- | --- | --- |
| `high` | The request has one clear owner and the boundary is stable. | Route immediately. |
| `medium` | Two owners are plausible, but one short question could remove the ambiguity. | Ask one targeted question, then route or fail safe. |
| `low` | The request is underspecified, cross-boundary, or risky enough that premature routing would be noise. | Route directly to `internal-planning-leader`. |

Use these heuristics:

- Treat explicit review language such as `review`, `audit`, `validate`, `risk`, `merge readiness`, or `regression` as `route-to-review` unless the user clearly asks for implementation.
- Treat explicit challenge language such as `challenge this`, `pre-mortem`, `stress-test`, `what am I missing`, or `failure modes` as `route-to-challenge`.
- Treat repository-owned authoring of agents, skills, prompts, instructions, routing, or governance as planning unless the change is trivially local and already designed.
- Treat vague implementation requests as planning when scale, ownership, or rollout is not yet clear.

## Decision Matrix

| Task shape | Signals | Route |
| --- | --- | --- |
| Clear execution | One concrete outcome, local scope, obvious validation path, no strategy tradeoff | `route-to-execute` |
| Medium execution | Mostly concrete, but some uncertainty remains about scale or boundaries | Ask one question or route to `internal-planning-leader` |
| Ambiguous or strategic | Cross-file, cross-boundary, naming or ownership changes, or multiple credible options | `route-to-plan` |
| Review-oriented | The output should be findings, evidence, risk, or merge readiness | `route-to-review` |
| Challenge-oriented | The output should be objections, pressure tests, assumptions, or failure modes | `route-to-challenge` |

## Medium-Task Thresholds

Route away from execution and into planning when any of these are true:

- The change is likely to touch `>= 3` files with lateral impact.
- The change crosses more than one directory family or logical boundary.
- The change affects routing, ownership, naming contracts, or catalog boundaries.
- There are `>= 2` credible solution paths with non-trivial tradeoffs.
- The task needs rollout, regression, governance, or rollback decisions.
- The task creates a new repository-owned resource instead of making a banal update to an existing one.

Stay with `route-to-execute` only when all of these remain true:

- The likely change touches `<= 2` files.
- The work stays within one directory family or one logical boundary.
- Routing, ownership, naming contracts, and catalog boundaries stay unchanged.
- The task does not require a real strategic comparison.

## High-Value Clarification Question Rule

Only ask one question when the answer will change the owner.

Good questions:

- `Is your goal to implement the change now, or to decide the right design and rollout first?`
- `Do you want a defect-first review, or do you want the change implemented?`
- `Should this route stress-test the proposal, or produce the final execution plan?`

Bad questions:

- Broad interviews with multiple subquestions.
- Questions that gather details the selected owner should inspect alone.
- Questions that delay an already safe `route-to-plan` fail-safe.

## Retired To Canonical Mapping

| Retired route | Canonical route |
| --- | --- |
| `internal-ai-resource-creator` | `internal-planning-leader` |
| `internal-architect` | `internal-planning-leader` |
| `internal-developer` | `internal-fast-executor` |
| `internal-infrastructure` | `internal-fast-executor` or `internal-planning-leader` when design or rollout dominates |
| `internal-cicd` | `internal-fast-executor` or `internal-planning-leader` when orchestration or tradeoffs dominate |
| `internal-code-review` | `internal-review-guard` |
| `internal-quality-engineering` | `internal-review-guard` for validation and risk, `internal-fast-executor` for a clear fix |
| `internal-aws-*`, `internal-azure-*`, `internal-gcp-*` | `internal-planning-leader` for strategy or design, `internal-fast-executor` for clear local execution |

Do not use `internal-sync-*` or `awesome-*` assets as canonical operational owners in this routing model.

## Owner Examples

### `internal-fast-executor`

Positive examples:

- `Update the validator to reject missing frontmatter in one script and one test file.`
- `Fix this broken prompt reference and run the relevant tests.`

Negative examples:

- `Decide how to redesign the operational catalog.`
- `Figure out whether we should split or merge these command centers.`

### `internal-planning-leader`

Positive examples:

- `Rationalize the internal agent catalog and define the new routing model.`
- `Create a new repository-owned skill and decide where the shared logic should live.`

Negative examples:

- `Change this one test assertion in place.`
- `Review my diff for regressions.`

### `internal-review-guard`

Positive examples:

- `Review this change for merge readiness and regression risk.`
- `Validate whether the new catalog leaves stale references or weak evidence.`

Negative examples:

- `Implement the missing routing engine.`
- `Challenge whether the strategy itself is sound before we review code.`

### `internal-critical-challenger`

Positive examples:

- `Stress-test this operating model before we adopt it.`
- `Give me the strongest objections and failure modes for this plan.`

Negative examples:

- `Write the implementation plan and apply the changes.`
- `Perform a normal code review of the diff.`

## Fail-Safe Rule

When routing is not safely clear, select `route-to-plan` and hand off to `internal-planning-leader`.

Routing conservatively is cheaper than dispatching the user to the wrong owner and forcing a second triage cycle.

## Output Expectations

- Selected route label
- Selected canonical owner
- Confidence level
- One-sentence routing rationale
- Single clarification question only when the decision was medium confidence
- Explicit confirmation that no implementation was performed

## Common Mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Routing generic requests straight to execution | Medium tasks silently expand and cause ownership drift | Fail safe to `internal-planning-leader` when boundaries are not stable |
| Asking multiple clarification questions | The router becomes a hidden planner | Ask at most one question that changes the owner |
| Treating review and challenge as the same lane | Findings and pressure tests have different outputs and escalation paths | Keep `review` and `challenge` distinct |
| Letting retired agents stay mentally canonical | Users keep landing on the old overlap model | Translate old names through the old-to-new table and route to a canonical owner |
| Continuing into implementation after routing | The router turns into a fifth generalist | Stop after dispatch |
