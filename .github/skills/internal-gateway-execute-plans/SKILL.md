---
name: internal-gateway-execute-plans
description: "Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/plans/."
---

# Internal Gateway Execute Plans

## Bundle References

- `references/execution-contract.md` — repository hooks around the delegated execution loop.
- `references/recovery-contract.md` — continuation-first recovery and closeout decision ladder.
- `references/status-contract.md` — status transition table, required headings, and exact sibling filenames.
- `scripts/plan_execution.py` — read-only stdlib-only CLI for strict plan binding, structured recovery classification, status shape, resume safety, and completion readiness.

## Referenced skills

- `/superpowers-executing-plans` supplies only critical plan review, todo tracking, and task-by-task mechanics.
- `/internal-tdd` owns executable-behavior test-first guidance at the local task gate.
- `/superpowers-verification-before-completion` owns final evidence before completion claims.
- `/addyosmani-code-simplification` is conditional and may be loaded only when the approved task explicitly authorizes simplification.

## When to use

- Execute or resume an approved retained plan under `tmp/superpowers/plans/`.
- Apply repository-local preflight, task hooks, status handling, and closeout around the delegated core loop.

## When not to use

- Writing, reformulating, reviewing, or challenging a plan.
- Running same-chat work that is not driven by an approved retained plan.
- Changing imported execution behavior or replacing the delegated core workflow.

## Safety Boundary

The bundled CLI proves only mechanical safety: the plan is in the canonical
retained directory, readable, actionable, and contains exactly one supported
execution contract; status files are bound to the plan and fingerprint; and
completion state is consistent. Missing required headings, execution fields,
or contract data are blocking findings. Status files require the minimal
resumable core plus closeout evidence for serialized routes. Conversational
approval and runtime safety remain gateway responsibilities.

## Control coverage

Before the delegated loop, read the plan's `## Control Inventory` or
reconstruct the same inventory from its tasks, acceptance criteria, and
versioned `## Execution Contract`. Classify every obligation exactly once as
`automatable-local`, `observable-runtime`, `external-capability`,
`authority-or-scope`, or `genuine-human-judgment`. Do not confuse these control
classes with the six executor-owned runtime discovery categories.

- `automatable-local` and `observable-runtime` controls must use a required
  executable validation or capability probe with a clear pass/fail signal and
  reproducible evidence, and the check must fail when the requirement is
  violated. Establish red-first evidence before implementation when the control
  changes executable or evaluable behavior.
- `external-capability` controls fail closed for the capability decision. Probe
  explicitly and use a safe fallback only when the plan permits it; do not
  treat an unavailable capability as a technical pass. When no material
  feature failure is observed, record the unavailable evidence as a
  non-blocking follow-up rather than routing the completed feature to
  `NEEDS_REVIEW`. If the probe observes a material contract failure, classify
  it as unresolved or regression and enter recovery.
- `authority-or-scope` controls use the plan's authority boundary. Do not
  expand scope or modify the approved plan without the required approval and a
  refreshed fingerprint.
- `genuine-human-judgment` controls remain explicit human obligations with
  acceptance evidence, but their verification is an offline follow-up and does
  not block `DONE` after execution and required validations complete. Do not
  disguise them as automated validation. Authority and approval gates needed
  before execution remain gateway preconditions.

Every control row must map to a contract validation, manual obligation, or
authority boundary and retain its requirement, owner, trigger, pass/fail
signal, evidence, and fallback. An uncovered local/runtime control is a plan
gap: stop before editing or request the plan-authorized correction; never mark
it satisfied to reach `DONE`. If correcting or completing the plan is explicitly
authorized, add the missing control or gate without weakening the requirement,
rerun preflight, and obtain refreshed approval and fingerprint before execution.
Otherwise, do not modify the approved plan.

Ask the user only after local checks are exhausted and only for new authority,
access, a product or scope choice, or an explicit requirement conflict. Report
the checks already performed and ask one focused question; never ask the user
to run a local check or certify technical output. Record pending human
judgment as offline follow-up after a successful closeout.

## Gateway boundary

`/internal-gateway-execute-plans` is the authoritative local execution route. It
controls routing, recovery, stopping, worktree and finishing decisions, status
transitions, and closeout. The imported `/superpowers-executing-plans` bundle is
delegated only critical review, todo tracking, and task-by-task mechanics; it
does not regain any local gateway responsibility.

- bind the exact plan path and explicit approval state;
- compute the SHA-256 fingerprint, run dirty-worktree preflight, and capture
  the plan-required validation baseline;
- verify control coverage before execution and preserve the mapping from each
  obligation to its executable validation, external/human obligation, or
  authority boundary;
- apply task-level `/internal-tdd` and evidence hooks;
- decide routing, recovery candidates, stop conditions, and worktree/finishing
  behavior;
- classify closeout evidence with `closeout-check`, continue while a safe route
  exists, retry distinct safe repairs while evidence improves, and preserve
  the baseline/final delta;
- enforce the no-Git-mutation policy;
- replace the exact `DONE`, `PARTIAL`, `BLOCKED`, or `NEEDS_REVIEW` sibling;
- run resume and completion checks through `scripts/plan_execution.py`.

## Gateway phases

1. **Bind** the approved retained plan, fingerprint, workspace overlap, control
   inventory, and native validation commands. Completion: preflight passes,
   every control has an owner, and the baseline is recorded.
2. **Execute** the delegated plan task-by-task with the posture returned by
  `/internal-tdd`. Require red-first gates only for `mandatory-test-first`;
  `feature-first` requires focused validation before task transition and
  reachable evidence before production-ready completion. Completion: each
  task and control has fresh focused evidence or a recorded safe pause.
3. **Recover** through `references/recovery-contract.md` whenever validation or
   execution is unresolved. Completion: each distinct safe candidate was tried,
   authority was requested when required, or exhaustion evidence is complete.
4. **Decide** with `closeout-check`. Completion: continue immediately on a
  `continue-*` or `request-authority` route, or write one legal status sibling
  for a terminal or explicit pause route. Pending human or external evidence
  without an observed material failure is recorded as non-blocking follow-up
  on `DONE`. `NEEDS_REVIEW` is reserved for a material failure, exhausted
  recovery, and a concrete decision or authority request.
5. **Close** with broader validation, `git diff --check`, status binding, and the
   verification-before-completion gate. Completion: the status sibling and report
   contain the same fresh evidence.

## Delegation checkpoints

Before delegating task mechanics to `/superpowers-executing-plans`, bind the
retained plan, record approval, fingerprint the plan, capture the workspace
baseline, and run the plan's broad baseline validation. The binding gate must
also confirm the current plan has `## Control Inventory` and an explicit no-Git
constraint. A document identified as `legacy/imported` is non-actionable until
the writing gateway reconstructs it and approval and fingerprint are refreshed.
At each task boundary, load `/internal-tdd` when the task changes executable or
evaluable behavior, record and apply its selected posture, and require
red-first evidence before implementation only for `mandatory-test-first`.
For `feature-first`, require focused validation before task transition and
reachable evidence before production-ready completion.
After each delegated task, run the plan's focused validation, retain fresh
evidence, classify failures, and try each distinct safe repair or recovery
candidate while evidence improves. Do not repeat an unchanged attempt as
recovery. Pre-existing or unrelated broad failures do not stop independent
tasks. Load `/superpowers-verification-before-completion` before any positive
completion claim; load `/addyosmani-code-simplification` only when explicitly
authorized by the plan.

Before a task transition or closeout, apply
`references/recovery-contract.md`. Preserve the native authoritative command,
continue on a safe `continue-*` route, keep bounded search and retry evidence,
and do not convert an uncovered or unresolved control into a user question
when a local check or probe can still be performed.

On pause or resume, preserve the plan fingerprint and use the status and resume
checks from `scripts/plan_execution.py`. At closeout, run the required broader
validation with the same commands used at baseline, record the baseline/final
delta, verify `git diff --check`, and write exactly one status sibling according
to `references/status-contract.md`. Always provide a concise user-facing report
with the outcome, changed work, validation, blocker or gap, recovery attempts,
and exact next action.

## Subagent model selection

Before any plan-writing or plan-execution delegation, probe whether
`gpt-5.6-luna` is available at `max` reasoning. If it is unavailable, select the
least expensive available model that is suitable for the specific task. Record
the timestamp and context, probe and availability result, selected model,
reasoning level, suitability evidence, and cost/fallback rationale. The known
drafting fallback is `gpt-5.6-terra` at `high` reasoning; it is not a guarantee
or a substitute for the probe. Luna's absence alone is not a blocker when the
fallback evidence is complete; lack of a suitable approved fallback is.

## No-Commit Rule

Do not run `git add`, `git commit`, `git push`, `git merge`, or another Git
mutation while executing, pausing, or closing out a plan. Leave executed
changes uncommitted for the user to review. If a retained plan contains Git
mutation steps, skip them and record the plan drift in the status sibling.

## Validation

- `git diff --check`
- `python3 scripts/plan_execution.py preflight <plan-file> --format compact`
- `python3 scripts/plan_execution.py status-check <status-file> --format compact`
- `python3 scripts/plan_execution.py resume-check <plan-file> <status-file> --format compact`
- `python3 scripts/plan_execution.py closeout-check <plan-file> <evidence-file> --format compact`
- `python3 scripts/plan_execution.py completion-check <plan-file> <status-file> --format compact`
- Confirm no live repository references point to removed bundle files.

The writer-owned versioned `## Execution Contract` is authoritative for
validation IDs, native commands, required flags, equivalence policy, manual
obligations, and authority boundaries. The control inventory is a traceability
layer over that contract, not a competing schema. The executor owns all six
discovery categories, recovery candidates, attempts, rejection evidence,
authority state, and closeout routing. `DONE` requires fresh evidence for every
task and every automatable or observable control; `request-authority` keeps
execution active and does not produce a status sibling. Unavailable external
evidence without an observed material failure is reported as non-blocking
follow-up and does not route to `NEEDS_REVIEW`. `NEEDS_REVIEW` requires a
material failure observed after safe recovery is exhausted, and its status
sibling must contain a structured `## Review Required` request. The final
report must also name control gates added or updated, their evidence, and any
residual gap.
