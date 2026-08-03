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

- `/superpowers-executing-plans` owns critical plan review, todo tracking, task execution, and its core stop behavior.
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
- `external-capability` controls fail closed when the service, network,
  credential, or tool is unavailable. Use a safe fallback only when the plan
  permits it; otherwise keep the obligation unresolved and request authority
  or route to the contract's review state. A warning or user certification is
  not a technical pass.
- `authority-or-scope` controls use the plan's authority boundary. Do not
  expand scope or modify the approved plan without the required approval and a
  refreshed fingerprint.
- `genuine-human-judgment` controls remain explicit human obligations with
  acceptance evidence; do not disguise them as automated validation.

Every control row must map to a contract validation, manual obligation, or
authority boundary and retain its requirement, owner, trigger, pass/fail
signal, evidence, and fallback. An uncovered local/runtime control is a plan
gap: stop before editing or request the plan-authorized correction; never mark
it satisfied to reach `DONE`. If correcting or completing the plan is explicitly
authorized, add the missing control or gate without weakening the requirement,
rerun preflight, and obtain refreshed approval and fingerprint before execution.
Otherwise, do not modify the approved plan.

Ask the user only after local checks are exhausted and only for new authority,
access, a product or scope choice, genuine human judgment, or an explicit
requirement conflict. Report the checks already performed and ask one focused
question; never ask the user to run a local check or certify technical output.

## Gateway boundary

The gateway is a repository-owned extension of `/superpowers-executing-plans`. The
delegated owner supplies the core review, todo, execution, and stop loop. Keep
only these local responsibilities here:

- bind the exact plan path and explicit approval state;
- compute the SHA-256 fingerprint, run dirty-worktree preflight, and capture
  the plan-required validation baseline;
- verify control coverage before execution and preserve the mapping from each
  obligation to its executable validation, external/human obligation, or
  authority boundary;
- apply task-level `/internal-tdd` and evidence hooks;
- classify closeout evidence with `closeout-check`, continue while a safe route exists,
  and preserve the baseline/final delta;
- enforce the no-Git-mutation policy;
- replace the exact `DONE`, `PARTIAL`, `BLOCKED`, or `NEEDS_REVIEW` sibling;
- run resume and completion checks through `scripts/plan_execution.py`.

## Gateway phases

1. **Bind** the approved retained plan, fingerprint, workspace overlap, control
   inventory, and native validation commands. Completion: preflight passes,
   every control has an owner, and the baseline is recorded.
2. **Execute** the delegated plan task-by-task with task-level red-first gates.
   Completion: each task and control has fresh focused evidence or a recorded
   safe pause.
3. **Recover** through `references/recovery-contract.md` whenever validation or
   execution is unresolved. Completion: the next candidate was tried, authority
   was requested when required, or exhaustion evidence is complete.
4. **Decide** with `closeout-check`. Completion: continue immediately on a
  `continue-*` or `request-authority` route, or write one legal status sibling for a terminal or explicit
   pause route.
5. **Close** with broader validation, `git diff --check`, status binding, and the
   verification-before-completion gate. Completion: the status sibling and report
   contain the same fresh evidence.

## Delegation checkpoints

Before loading `/superpowers-executing-plans`, bind the retained plan, record
approval, fingerprint the plan, capture the workspace baseline, and run the
plan's broad baseline validation. At each
task boundary, load `/internal-tdd` when the task changes executable or
evaluable behavior and require its red-first evidence before implementation.
After each delegated task, run the plan's focused validation, retain fresh
evidence, classify failures, and attempt bounded recovery while evidence
improves. Pre-existing or unrelated broad failures do not stop independent
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
execution active and does not produce a status sibling. The final report must
also name control gates added or updated, their evidence, and any residual gap.
