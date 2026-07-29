# Status Contract

Status transition rules, required core, optional evidence, and exact sibling filenames for plan closeout.

## Status Transition Table

| Current condition | Status | Continuation |
| --- | --- | --- |
| All tasks and broader validation have fresh passing evidence | `DONE` | none |
| At least one task is complete and executable tasks remain | `PARTIAL` | continuing |
| A named fatal blocker prevents safe further execution | `BLOCKED` | waiting |
| Execution is complete but human review or a proven pre-existing, unrelated/external, or environmental validation failure remains | `NEEDS_REVIEW` | waiting |

Use `DONE` only when every task passed its transition gate, all in-scope work is complete, and required broader validation has fresh passing evidence. A final broad check does not retroactively validate skipped task gates.

Do not use `BLOCKED` only because a broad validation failed. Compare the same
command at baseline and closeout, record the baseline/final delta, and classify
the failure. Use `BLOCKED` for genuine inability or unsafe continuation,
including unresolved task-local regression, plan drift, owner conflict,
unapproved scope expansion, or unknown attribution. Use `NEEDS_REVIEW` when all
in-scope work is complete and the remaining failure is proven pre-existing or
unrelated or environmental.

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
## Resume Notes
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
2. Confirm the human or external verification is complete.
3. If verification passed, update the status to `DONE` with fresh broader-validation evidence.
4. If verification still has only a proven pre-existing or unrelated external
   failure, keep `NEEDS_REVIEW` and refresh the evidence. Use `BLOCKED` only if
   the new evidence establishes a fatal condition.

## User-Facing Closeout

After writing the status sibling, give the user a concise user-facing report
with the outcome, changed work, validation, blocker or external gap, Recovery
Attempts, and exact next action. The report must stand alone; do not require the
user to open the status file.
