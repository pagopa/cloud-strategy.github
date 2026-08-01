# Execution Contract

This reference maps repository-local hooks around the delegated
`/superpowers-executing-plans` loop. It does not duplicate that skill's plan
review, todo, task execution, or core stop procedure.

## Before the delegated loop

- Require the exact retained plan path under `tmp/superpowers/plans/`.
- Accept `Preflight Gate` as the canonical plan heading and
  `Repository Preflight` or `Preflight` as compatibility aliases.
- Confirm explicit user approval is present in the current conversation.
- Compute and record the SHA-256 plan fingerprint with `scripts/plan_execution.py`.
- Record branch, dirty files, and in-scope overlap before editing.
- Name the local task dependency set and focused validation command.
- Record the native authoritative command for baseline and focused validation;
  an optional accelerator may optimize an invocation but must not replace the
  command or its evidence label.
- Run every broad validation named by `Baseline Validation` before edits and
  retain its command, exit status, and bounded failure summary.
- Preserve the no-Git-mutation rule throughout execution.

## Mechanical safety boundary

The bundled validator blocks only when it cannot safely identify or inspect the
retained plan, when the plan has no actionable task, or when status binding,
fingerprint, or completion checks fail. Missing `Goal`, `Global Constraints`,
preflight aliases, and legacy execution fields are notices; the gateway uses
its conversational approval and runtime safety responsibilities as defaults.
The validator does not interpret textual states such as `Draft-only`.

## Before each delegated task

- State the task's observable outcome, dependency set, and focused validation.
- For executable or evaluable behavior, load `/internal-tdd` and establish
  red-first evidence before the first implementation edit.
- Keep repository-owned routing, status, fixtures, and approval gates in scope;
  do not edit imported core skills.

## After each delegated task

- Run the plan-specified focused validation command.
- When a command is unresolved, attribute the failure and run the discovery and
  retry phases in `recovery-contract.md` before considering a stop.
- Require a distinct evidence delta for every retry; a warning alone is not recovery.
- Confirm the dependency set no longer asserts the replaced behavior.
- Retain fresh evidence before transitioning to the next task.
- When graphify is unavailable, stale, or fails, record the bounded evidence
  question, fallback strategy, bounded result, and stop condition. Do not copy
  full search output into status files.
- Classify each failure as `task-local regression`, `pre-existing`,
  `unrelated/external`, `environmental`, or `unknown`.
- Attempt bounded recovery only when it is directly required by the current
  task or its validation, stays inside approved scope, and evidence improves.
  Record recovery as an auxiliary execution task without changing the approved
  plan or fingerprint.
- Run `closeout-check` after recovery evidence changes. Continue without writing
  an intermediate status while it returns `continue-execution` or
  `continue-recovery`.
- If the plan authorizes simplification, `/addyosmani-code-simplification`
  may be loaded at that task's explicit gate.

## Execution discipline

- **TF (tight feedback):** Within the current approved task, treat the smallest
  coherent dependency set as one execution unit. Keep coupled edits, such as a
  signature, its callers, and its implementation, together; keep unrelated plan
  tasks separate. Use the task's focused validation as its transition gate.
- **FFD (fail fast on fatal conditions):** Stop the delegated loop on plan
  drift, owner conflict, missing required validation, unapproved scope
  expansion, unsafe continuation, unknown failure attribution, or an unresolved
  task-local regression after bounded recovery.
- A baseline failure classified as pre-existing or unrelated/external is not a
  fatal condition. Continue independent tasks and validations, preserve the
  baseline/final delta, and report the unresolved external gap.
- Do not stop for an environmental failure until one discovery pass and every
  safe in-scope recovery candidate have been recorded.
- Stop recovery when evidence no longer improves or the next action would cross
  scope, safety, approval, ownership, or Git-mutation boundaries.

## Pause and resume

- On pause, record the exact status sibling, remaining tasks, validation gap,
  and next action using `references/status-contract.md`.
- On resume, run `resume-check` and require the recorded fingerprint to match
  the retained plan before continuing.
- If the plan changed after approval, stop and record plan drift until the
  approval and fingerprint are refreshed.
- A status file needs only the required resumable core; optional evidence is
  validated when present and should be recorded when it improves handoff or
  failure attribution.

## Closeout

- Run all broader validation required by the retained plan.
- Use the same commands as the baseline and record the baseline/final delta.
- Preserve the native authoritative command and evidence label even when an
  optional accelerator optimized the invocation; require fallback execution
  and result validation before treating recovery as complete.
- Load `/superpowers-verification-before-completion` before claiming completion.
- Run `git diff --check` and verify no Git mutation was performed.
- Replace older status siblings for the same plan basename and write exactly
  one allowed status sibling.
- Use `NEEDS_REVIEW`, not `BLOCKED`, when all in-scope tasks are complete and a
  broad validation still has a proven pre-existing or unrelated failure.
- Give the user a concise user-facing report containing outcome, changed work,
  validation, blocker or external gap, Recovery Attempts, and next action; do
  not require the user to open the status sibling.
- Run `completion-check` only when every task and broader check has fresh
  passing evidence.
