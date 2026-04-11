---
name: internal-agent-routing-engine
description: Use when `internal-router` must classify an ambiguous operational request and dispatch it to execution, planning, review, or challenge without doing the domain work itself.
---

# Internal Agent Routing Engine

Use this skill as the mandatory engine for `internal-router`.

This skill owns the reusable routing logic. The router stays short: classify, ask at most one high-value question when needed, hand off to one canonical owner, and stay out of the domain work. The router never implements.

## Core Rules

- Classify first by intent: execution, planning, review, or challenge.
- Then classify by scale, ambiguity, risk, and boundary-crossing.
- Ask at most one targeted clarification question with two clear options, and only when it materially improves routing confidence.
- If confidence does not reach a safe routing decision after that question, fail safe to `internal-planning-leader` and hand off there.
- Dispatch only to the four canonical owners: `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-challenger`.
- If the router is entered as an explicit second parallel lane from another canonical owner, preserve that current lane as context and classify only the parallel operational request.
- Preserve the user's exact request plus any already-collected evidence instead of forcing the selected owner to re-triage from scratch.
- Treat the routing turn as incomplete until the delegated owner's result is attached in the same turn, or one blocking clarification question is asked because the selected owner cannot safely proceed without it.
- Do not present route selection or the handoff package alone as a completed response.
- If auto-dispatch is interrupted, yields no usable owner result, or the delegated result is missing from the response, retry once when safe. If it still does not complete, state that delegation did not complete, surface the preserved handoff package, and ask one blocking question only when user input is required.
- Do not implement through the router.

## Primary Route Labels

| Label | Canonical owner | Route when |
| --- | --- | --- |
| `route-to-execute` | `internal-fast-executor` | The task is clear, local, low-risk, and has concrete verification. |
| `route-to-plan` | `internal-planning-leader` | The task is ambiguous, cross-boundary, strategic, or changes repository-owned contracts. |
| `route-to-review` | `internal-review-guard` | The user asks for review, validation, merge readiness, regression analysis, or evidence checks. |
| `route-to-challenge` | `internal-critical-challenger` | The user wants assumptions challenged, a pre-mortem, alternative framings pressure-tested, or failure modes surfaced. |

## Confidence Model

| Confidence | Meaning | Router action |
| --- | --- | --- |
| `high` | The request has one clear owner and the boundary is stable. | Select the owner and auto-dispatch there. |
| `medium` | Two owners are plausible, but one short question could remove the ambiguity. | Ask one targeted question, then dispatch or fail safe. |
| `low` | The request is underspecified, cross-boundary, or risky enough that premature routing would be noise. | Fail safe to `internal-planning-leader` and auto-dispatch there. |

Use these heuristics:

- Treat explicit review language such as `review`, `audit`, `validate`, `risk`, `merge readiness`, or `regression` as `route-to-review` unless the user clearly asks for implementation.
- Treat explicit challenge language such as `challenge this`, `pre-mortem`, `stress-test`, `what am I missing`, `failure modes`, `reframe this`, or `think laterally` as `route-to-challenge`.
- Treat repository-owned authoring of agents, skills, prompts, instructions, routing, or governance as planning unless the change is trivially local and already designed.
- Treat vague implementation requests as planning when scale, ownership, or rollout is not yet clear.

## Decision Matrix

| Task shape | Signals | Route |
| --- | --- | --- |
| Clear execution | One concrete outcome, local scope, obvious validation path, no strategy tradeoff | `route-to-execute` |
| Medium execution | Mostly concrete, but some uncertainty remains about scale or boundaries | Ask one question or route to `internal-planning-leader` |
| Ambiguous or strategic | Cross-file, cross-boundary, naming or ownership changes, or multiple credible options | `route-to-plan` |
| Review-oriented | The output should be findings, evidence, risk, or merge readiness | `route-to-review` |
| Challenge-oriented | The output should be objections, pressure tests, assumption gaps, alternative framings, or failure modes | `route-to-challenge` |

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

Prefer A-or-B questions with two clear options over open-ended interviews. If a safe two-option question is not obvious, fail safe to `internal-planning-leader`.

Good questions:

- `Is your goal to implement the change now, or to decide the right design and rollout first?`
- `Do you want a defect-first review, or do you want the change implemented?`
- `Should this route stress-test the proposal, or produce the final execution plan?`

Bad questions:

- Broad interviews with multiple subquestions.
- Questions that gather details the selected owner should inspect alone.
- Questions that delay an already safe `route-to-plan` fail-safe.

## Handoff Protocol

After selecting the canonical owner, hand off a compact package that includes:

- `selected_owner`
- `route_label`
- `confidence`
- `routing_rationale`
- `current_lane` when the router was entered as a second parallel lane
- `user_request`
- `relevant_constraints`
- `already_collected_evidence`
- `expected_output_shape`

Keep the handoff compact, preserve the user's wording, and include only the evidence that materially reduces re-triage.

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

Load `references/owner-examples.md` only when the matrix and confidence model still leave two plausible owners and you need concrete examples to break the tie.

## Fail-Safe Rule

When routing is not safely clear, select `route-to-plan` and hand off to `internal-planning-leader`.

Routing conservatively is cheaper than dispatching the user to the wrong owner and forcing a second triage cycle.

## Output Expectations

- Selected route label
- Selected canonical owner
- Confidence level
- One-sentence routing rationale
- Handoff package summary with preserved request, constraints, and already-collected evidence
- Delegated owner's result, prefixed by a short routing note
- Explicit blocking explanation plus preserved handoff package when delegation did not complete
- Single clarification question only when medium-confidence routing or degraded dispatch truly needs user input
- Explicit confirmation that the router delegated instead of performing the domain work

## Common Mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Routing generic requests straight to execution | Medium tasks silently expand and cause ownership drift | Fail safe to `internal-planning-leader` when boundaries are not stable |
| Asking multiple clarification questions | The router becomes a hidden planner | Ask at most one question that changes the owner |
| Treating review and challenge as the same lane | Findings and pressure tests have different outputs and escalation paths | Keep `review` and `challenge` distinct |
| Letting retired agents stay mentally canonical | Users keep landing on the old overlap model | Translate old names through the old-to-new table and route to a canonical owner |
| Dispatching to non-canonical owners | The front door stops being predictable and enforceable | Dispatch only to the four canonical owners |
| Continuing into implementation after routing | The router turns into a fifth generalist | Hand off to the selected owner and keep the router out of domain work |
