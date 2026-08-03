# Execution Contract

This reference maps repository-local hooks around the delegated
`/superpowers-executing-plans` loop. It does not duplicate that skill's plan
review, todo, task execution, or core stop procedure.

## Before the delegated loop

- Require the exact retained plan path under `tmp/superpowers/plans/`.
- Treat the writer-owned versioned `## Execution Contract` as authoritative.
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

## Control coverage

Build a control inventory from the plan's `## Control Inventory`, tasks, and
acceptance criteria before loading the delegated loop. Assign each obligation
exactly one class: `automatable-local`, `observable-runtime`,
`external-capability`, `authority-or-scope`, or `genuine-human-judgment`.

- Map local and observable-runtime controls to required plan validations with a
  native command or capability probe, pass/fail condition, and reproducible
  evidence. The check must fail when the requirement is violated; a warning or
  printout is not a gate.
- For external capabilities, probe explicitly and fail closed when unavailable.
  Use only a plan-permitted safe fallback; otherwise preserve the unresolved
  external obligation and follow the authority/review route.
- Map authority or scope controls to the plan's approval boundary and genuine
  human judgment to a declared human obligation. Do not use a user assertion,
  warning, or narrative-only note as a technical pass.
- Keep stable IDs and traceability to the existing `Execution Contract`; do not
  introduce a competing schema. If a local/runtime obligation has no gate,
  stop before editing or obtain the plan-authorized correction. An authorized
  correction must preserve the requirement, pass preflight, and refresh
  approval and fingerprint before execution; otherwise the approved plan is
  immutable.

Ask the user only after local checks are exhausted and only for new authority,
access, a product or scope choice, genuine human judgment, or an explicit
requirement conflict. Report the checks already performed and ask one focused
question; never ask the user to run a local check or certify technical output.

## Mechanical safety boundary

The bundled validator blocks when it cannot safely identify or inspect the
retained plan, when the plan has no actionable task, when the strict versioned
execution contract is missing or malformed, or when status binding,
fingerprint, or completion checks fail. Required plan headings and execution
fields are blocking. The validator does not interpret textual states such as
`Draft-only`.

## Before each delegated task

- State the task's observable outcome, dependency set, and focused validation.
- For executable or evaluable behavior, load `/internal-tdd` and establish
  red-first evidence before the first implementation edit.
- Keep repository-owned routing, status, fixtures, and approval gates in scope;
  do not edit imported core skills.

## After each delegated task

- Run the plan-specified focused validation command.
- Confirm every changed task and control has fresh evidence before transition;
  an uncovered automatable or observable-runtime control is a plan gap, not a
  manual checkbox.
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
- Run `closeout-check <plan-file> <evidence-file>` after recovery evidence
  changes. Continue without writing an intermediate status while it returns
  `continue-execution`, `continue-recovery`, or `request-authority`.
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
  control gates and evidence, validation, blocker or external gap, Recovery
  Attempts, and next action; do not require the user to open the status
  sibling.
- Run `completion-check` only when every task and broader check has fresh
  passing evidence and every automatable or observable-runtime control is
  covered. Pending external or human obligations remain `NEEDS_REVIEW` unless
  the contract records the required evidence.
