---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be completed quickly in one bounded run.
---

# Internal Gateway Simple Task

## Referenced skills

- `grill-me`: compact Gate 1 interview after local preflight and Initial Idea Ordering.
- `internal-gateway-critical-master`: Gate 2 challenge before non-trivial action.
- `internal-tdd`: executable or evaluable behavior changes that need repository-owned TDD routing before implementation.
- `superpowers-verification-before-completion`: final evidence gate before completion, readiness, passing, fixed, or no-gap claims.
- `addyosmani-code-simplification`: on-demand method owner only for an explicit code-simplification request or an already-approved simplification remediation.

Do not introduce other skills, agents, or workflow owners from this bundle. When stopping, explain the violated condition and let the user choose the next path.

## Core Contract

Use this skill as the fast path for concrete bounded work that should finish in the current run. It owns the decision to continue or stop, then answers, edits, diagnoses, or validates end-to-end when the target, anti-scope, and validation path are concrete enough to execute safely.

Stop only when the work becomes materially complex, too costly for the current run, ambiguous, unsafe, multi-phase, approval-bound, or not locally verifiable. Stop output must explain the boundary break instead of delegating by name.

Use local references and scripts only to keep the decision process compact and deterministic. Keep working state small, inspect bounded evidence first, and preserve direct completion ownership inside this bundle.

## When to use

- The task is concrete and repository-owned.
- The target path, requested outcome, or validation path is known or can be recovered with one focused clarification.
- One bounded run can answer, edit, diagnose, or validate the work without staged workflow changes.

## When not to use

- The request is primarily brainstorming, architecture selection, or tradeoff design.
- The request is primarily defect-first review.
- The task needs a retained plan, a multi-phase rollout, or separate execution approval.
- The task cannot be validated locally or safely with bounded evidence.

## Gate Decision

Classify the task before operational work as `trivial-skip`, `full-gate`, or `stop-with-reason`.

- Use `trivial-skip` only for a local answer, tiny edit, focused read, or validator run with no material ambiguity, no material risk, and an obvious validation path or explicit validation gap.
- Use `full-gate` for every other same-run task.
- Use `stop-with-reason` when risk, cost, ambiguity, approval, validation, or phase count breaks same-run completion.
- Depth keywords such as `full`, `idea`, and `complete` forbid `trivial-skip`.

For `stop-with-reason`, report:

- `why stopped`
- `violated condition`
- `user decision needed`
- `evidence required before continuing`

## Execution Contract

For `trivial-skip`, do not create a ledger. Name the validation path directly, or state the exact validation gap.

For `full-gate`, complete the gates in this order:

1. Inspect the nearest local evidence.
2. Confirm the task still fits one bounded run.
3. Complete Initial Idea Ordering.
4. Ask one compact `grill-me` block only when a missing bounded fact blocks the active lane.
5. Run the critical challenge before non-trivial action.
6. Write a short Readiness Brief.
7. If executable or evaluable behavior changes, load `internal-tdd` before implementation and follow its routed posture.
8. For an explicit code-simplification request or already-approved simplification remediation, establish a passing behavior baseline, then load `addyosmani-code-simplification`; do not create a simplification pass after unrelated implementation.
9. Execute the smallest coherent in-scope move.
10. Run focused validation or report the exact validation gap.
11. Use the final evidence gate before positive claims.

Initial Idea Ordering is local to this skill and must cover:

- `original request`
- `emerged requirements`
- `actual problem`
- `proposed direction`
- `hidden assumption`
- `smaller move`
- `alternative path`
- `validation signal`
- `stop signal`

The Readiness Brief must stay shorter than a retained plan and include:

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

## Gate Evidence Ledger

For `full-gate` work, keep a compact ledger before final claims. Each row must be `done`, `skipped`, or `blocked` and must include evidence or a gap.

Required rows:

- `bounded-evidence`
- `complexity-cost`
- `initial-idea-ordering`
- `clarification`
- `critical-challenge`
- `readiness-brief`
- `execution`
- `validation`
- `final-evidence`

Use `skipped` only when the gate policy allows it and the reason is explicit. Use `blocked` when the missing evidence prevents a completion, readiness, passing, fixed, or no-gap claim.

## Execution Loop

When execution is authorized, iterate with the smallest useful cycle:

1. Confirm the current goal, scope boundary, and next check.
2. Apply the smallest readable in-scope action.
3. Run the focused validation or evidence check.
4. Repair once when the failure is still in scope and improving.
5. Continue only while evidence improves.
6. Stop with reason when risk, cost, ambiguity, or validation failure crosses the boundary.

Keep the implementation posture simple:

- Complete only the concrete requested outcome.
- Do not add helpers, abstractions, options, configuration, or future-proofing without an active task need.
- Remove meaningful duplication touched by the task, but do not extract one-off logic.
- Give each changed section, helper, or code path one current reason to exist.
- When behavior changes, name the observable contract and validate it with the closest stable check.

## Deterministic Helpers

- `scripts/resolve_simple_task.py gate`: returns a deterministic gate outcome plus a local Readiness Brief.
- `scripts/resolve_simple_task.py claim`: returns evidence requirements for strong status claims.
- `scripts/suggest_support_skills.py`: returns generic method hints when the next move is still noisy.
- Script output contract: `text` for short operator summaries (default), `json` for nested or machine-consumed output, `tsv`/`csv` only for large flat tables; data on stdout, diagnostics on stderr; keep output bounded.

## Validation

- Only the five referenced skill names appear in this bundle.
- Concrete bounded work completes in the same run unless `stop-with-reason` is explicit.
- Stop output explains the exact violated condition and required evidence.
- `trivial-skip` names the validation path directly or states the exact validation gap.
- Non-trivial work completes Initial Idea Ordering before `grill-me`.
- The critical challenge runs before non-trivial action.
- Non-trivial work has a Gate Evidence Ledger entry for each required row, or an explicit blocker.
- Skipped gates record the reason that made the skip valid.
- Blocked gates prevent completion, readiness, passing, fixed, or no-gap claims.
- Executable or evaluable behavior changes load `internal-tdd` before implementation when a meaningful seam exists.
- `addyosmani-code-simplification` loads only for an explicit simplification request or already-approved remediation after a passing behavior baseline exists.
- Positive claims rely on fresh evidence before completion.
