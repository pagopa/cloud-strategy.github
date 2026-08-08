# Status Contract

Status transition rules, required core, optional evidence, and exact sibling
filenames for `/internal-gateway-execute-plans` closeout.

The local execution gateway owns status transitions, status binding, and
closeout. Imported task mechanics may report evidence but may not pause,
resume, or create a status sibling. A terminal or paused sibling is legal only
after current-plan control inventory/no-Git binding, required validation, and
the gateway's closeout decision have passed.

## Status Transition Table

| Current condition | Status | Continuation |
| --- | --- | --- |
| All tasks and broader validation have fresh exact or classifier-approved equivalent evidence | `DONE` | none |
| All tasks and required technical validations pass while declared human or external follow-up remains pending and no material failure was observed | `DONE` | offline follow-up |
| The caller explicitly paused while executable tasks remain | `PARTIAL` | continuing |
| An exhausted fatal condition prevents safe further execution | `BLOCKED` | waiting |
| Implementation is complete, a material failure was observed, safe recovery is exhausted, and a decision or authority request remains | `NEEDS_REVIEW` | waiting for review |

Use `DONE` only when every task and every automatable or observable control
passed its transition gate, all in-scope work is complete, and required broader
validation has fresh passing evidence. Pending human or external evidence
without an observed material failure is recorded in the closeout evidence and
user-facing report as non-blocking follow-up; it does not change a successful
closeout to `NEEDS_REVIEW`. A final broad check does not retroactively validate
skipped task gates or uncovered controls.
Active classifier routes (`continue-execution`, `continue-recovery`, and
`request-authority`) do not produce status siblings.

Do not use `BLOCKED` only because a broad validation failed. Compare the same
command at baseline and closeout, record the baseline/final delta, classify the
failure, and run `closeout-check`. `DONE` accepts exact passes and equivalent
passes only when all four equivalence conditions are true. `PARTIAL` requires
`pause_requested: true`. `BLOCKED` requires an exhausted fatal condition,
unknown attribution, or unresolved task-local regression. `NEEDS_REVIEW` requires
completed implementation, an observed material failure or declined authority,
no safe recovery candidate, exhaustion evidence, and a structured
`## Review Required` request. A pending external or human follow-up is not
enough, and `environmental` alone is insufficient. Human review and unavailable
external evidence are not closeout blockers when no material failure was
observed.

## Required Core

Every status file must contain this minimal resumable core in order:

```markdown
## Status
## Plan
## Plan Fingerprint
## Completed
## Remaining
## Validation
## Next
```

The parser accepts these optional evidence headings and validates their
contents when present:

```markdown
## Reason
## Workspace Baseline
## Baseline Validation
## Files Changed
## Recovery Attempts
## Failure Classification
## Closeout Decision
## Recovery Exhaustion
## Resume Notes
## Review Required
## Review Follow-up
```

Record optional evidence when it improves reviewability, especially for broad
validation deltas, recovery attempts, failure classification, or resume
context. Its absence is not a parser failure.

- **Status** — one of `DONE`, `PARTIAL`, `BLOCKED`, or `NEEDS_REVIEW`.
- **Plan** — the exact plan file path.
- **Plan Fingerprint** — the SHA-256 hash of the approved plan, prefixed with `sha256:`.
- **Completed** — list of tasks that passed their transition gate, with task-level evidence.
- **Remaining** — list of tasks not yet complete, with the exact work remaining.
- **Validation** — list of validation commands run and their results.
- **Next** — the exact next action to resume or finish.
- **Reason** *(optional)* — why this status was chosen; name a blocker for
  `BLOCKED` or confirm fresh evidence for `DONE`.
- **Workspace Baseline** *(optional)* — branch, dirty files, and in-scope
  overlap at closeout.
- **Baseline Validation** *(optional)* — commands, exit status, and bounded
  failure summary captured before edits.
- **Files Changed** *(optional)* — files created or modified during execution.
- **Recovery Attempts** *(optional)* — bounded actions, evidence delta, and why
  recovery stopped; use `none` when no failure required recovery.
- **Failure Classification** *(optional)* — task-local regression,
  pre-existing, unrelated/external, environmental, or unknown, with evidence.
- **Resume Notes** *(optional)* — context needed to resume, including drift or
  blockers.
- **Review Required** *(conditional)* — mandatory for `NEEDS_REVIEW`; include
  `Event`, `Impact`, `Recovery`, `Evidence`, `Decision`, and `Next action`.
  This is a decision request, not a request for the user to repeat all final
  validations.
- **Review Follow-up** *(optional)* — non-blocking external or human evidence
  that remains useful after a successful `DONE` closeout; it must not be written
  as a blocker or as a request to repeat the completed validation set.

## Exact Allowed Sibling Filenames

Status files use exact allowed sibling filenames:

```text
<basename>.DONE.md
<basename>.PARTIAL.md
<basename>.BLOCKED.md
<basename>.NEEDS_REVIEW.md
```

Where `<basename>` is the plan filename without the `.md` extension. For example, if the plan is `2026-07-25-1831-self-contained-execute-plans.md`, the status file for `DONE` is `2026-07-25-1831-self-contained-execute-plans.DONE.md`.

## Replacement Rules

Before final response or pause:

1. Identify the plan basename.
2. Check for existing status siblings with the same basename.
3. If an older sibling exists, replace it by writing the new status to a temporary sibling followed by an atomic rename.
4. Replacement considers only the four exact allowed names above; preserve every other sibling.
5. Write exactly one status sibling for the current closeout.

## Resume Safety

When resuming from a `PARTIAL` or `BLOCKED` status:

1. Verify the status file exists and contains all required headings.
2. Compute the current plan fingerprint and compare it to the recorded `## Plan Fingerprint`.
3. If the fingerprints differ, the plan changed after approval; stop and record the drift.
4. If the fingerprints match, resume from the first task listed in `## Remaining`.
5. Do not resume from `DONE` unless fresh evidence invalidates the previous closeout.

When resuming from `NEEDS_REVIEW`:

1. Verify the status file exists and contains all required headings.
2. Rerun discovery because the environment may have changed.
3. Rerun the relevant discovery, repair, and validation route rather than
   asking the user to repeat the entire closeout.
4. If the material failure is repaired or the decision resolves the gap,
   update the status to `DONE` with fresh broader-validation evidence.
5. If no material failure was ever observed and only external or human
   follow-up remains, update the status to `DONE`. Use `BLOCKED` only if new
   evidence establishes a fatal condition.

## User-Facing Closeout

After writing the status sibling, give the user a concise user-facing report
with the outcome, changed work, validation, blocker or external gap, Recovery
Attempts, and exact next action. For `NEEDS_REVIEW`, repeat the structured
review request in the report. The report must stand alone; do not require the
user to open the status file or repeat validations that the gateway already ran.
