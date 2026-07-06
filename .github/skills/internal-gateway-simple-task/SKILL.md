---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be completed quickly in one bounded run.
---

# Internal Gateway Simple Task

## Referenced skills

- `grill-me`: compact Gate 1 interview after local preflight and Initial Idea Ordering.
- `internal-gateway-critical-master`: Gate 2 challenge before non-trivial action.
- `superpowers-verification-before-completion`: final evidence gate before completion, readiness, passing, fixed, or no-gap claims.

Do not name other skills, agents, or workflow owners from this bundle; when stopping, explain the violated condition and let the user choose the next path.

Use this skill as the fast path for concrete bounded work that should finish in the current run. It should answer, edit, diagnose, or validate end-to-end by default when the target, anti-scope, and validation path are concrete enough to execute safely.

Stop only when the work becomes materially complex, too costly for the current run, ambiguous, unsafe, multi-phase, approval-bound, or not locally verifiable. When stopping, report the exact boundary break instead of delegating by name.

Use local references and scripts only to keep the decision process compact and deterministic. Keep the working state small, prefer bounded evidence, and preserve direct completion ownership inside this bundle.

## When to use

- The task is concrete and repository-owned.
- The target path, requested outcome, or validation path is already known or can be recovered with one focused clarification.
- One bounded run can answer, edit, diagnose, or validate the work without staged workflow changes.

## When not to use

- The request is primarily brainstorming, architecture selection, or tradeoff design.
- The request is primarily defect-first review.
- The task needs a retained plan, a multi-phase rollout, or separate execution approval.
- The task cannot be validated locally or safely with bounded evidence.

## Autonomous Completion Rule

Complete the task in the current run when it is concrete, bounded, and locally validatable. Do not stop merely because a supporting method exists.

When the task cannot safely continue, stop with these fields:

- `why stopped`
- `violated condition`
- `user decision needed`
- `evidence required before continuing`

Stop output must not name another skill, agent, or owner.

## Initial Idea Ordering

Complete this local ordering before `grill-me` for any non-trivial task:

- `original request`
- `emerged requirements`
- `actual problem`
- `proposed direction`
- `hidden assumption`
- `smaller move`
- `alternative path`
- `validation signal`
- `stop signal`

This ordering is local to this skill. Do not import it from any other bundle.

## Gate Policy

Classify the task before operational work as `trivial-skip`, `full-gate`, or `stop-with-reason`.

- Use `trivial-skip` only for a local answer, tiny edit, focused read, or validator run with no material ambiguity, no material risk, and an obvious validation path or explicit validation gap.
- Use `full-gate` for everything else that still fits same-run completion.
- Use `stop-with-reason` when the work becomes too complex, too costly, ambiguous, unsafe, approval-bound, multi-phase, or likely incomplete in the current run.

Gate order:

1. Bounded evidence.
2. Complexity and cost gate.
3. Initial Idea Ordering.
4. `grill-me` when needed.
5. Critical challenge.
6. Readiness Brief.
7. Execution.
8. Validation.
9. Final evidence gate.

Depth keywords such as `full`, `idea`, and `complete` forbid `trivial-skip`.

## Readiness Brief

Before operational work, produce a short local brief with no placeholders:

- `Task`
- `Goal`
- `Scope`
- `Anti-scope`
- `Files expected`
- `Approach`
- `Executable behavior`
- `Validation path`
- `Main risk`
- `Stop conditions`
- `Approval`

This brief must stay shorter than a retained plan.

## Simple Procedure

1. Inspect the nearest local evidence first.
2. Decide whether the task is `trivial-skip`, `full-gate`, or `stop-with-reason`.
3. For non-trivial work, complete Initial Idea Ordering before `grill-me`.
4. Ask one compact `grill-me` block only when it is needed to continue the active lane.
5. Run the critical challenge before non-trivial action.
6. Build the Readiness Brief.
7. Execute the smallest coherent in-scope move.
8. Run focused validation or report the exact validation gap.
9. Use the final evidence gate before positive claims.

## Execution Loop

When execution is authorized, iterate with the smallest useful cycle:

1. Confirm the current goal, scope boundary, and next check.
2. Apply the smallest in-scope action.
3. Run the focused validation or evidence check.
4. Repair once when the failure is still in scope and improving.
5. Continue only while evidence improves.
6. Stop with reason when risk, cost, ambiguity, or validation failure crosses the boundary.

## Generic Executable Behavior Rule

When executable behavior changes, use a generic test-first loop:

1. Identify the observable behavior.
2. Choose the smallest useful stable check.
3. Make it fail first when practical.
4. Implement the minimum change.
5. Re-run the focused check.
6. Refactor only after passing.
7. Finish with the closest broader validation.

If no useful seam exists, state the seam gap explicitly.

## Deterministic Helpers

- `scripts/resolve_simple_task.py gate`: returns a deterministic gate outcome plus a local Readiness Brief.
- `scripts/resolve_simple_task.py claim`: returns evidence requirements for strong status claims.
- `scripts/suggest_support_skills.py`: returns generic method hints when the next move is still noisy.

## Validation

- Only the three retained skill names appear in this bundle.
- Initial Idea Ordering is completed before `grill-me` for non-trivial work.
- The critical challenge runs before non-trivial action.
- Concrete bounded work completes in the same run unless `stop-with-reason` is explicit.
- Stop output explains the exact violated condition and required evidence.
- Executable behavior changes follow the generic test-first loop when a useful seam exists.
- Positive claims rely on fresh evidence before completion.
