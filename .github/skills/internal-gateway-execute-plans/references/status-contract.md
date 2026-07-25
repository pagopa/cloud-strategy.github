# Status Contract

Status transition rules, required headings, and exact sibling filenames for plan closeout.

## Status Transition Table

| Current condition | Status | Continuation |
| --- | --- | --- |
| All tasks and broader validation have fresh passing evidence | `DONE` | none |
| At least one task is complete and executable tasks remain | `PARTIAL` | continuing |
| A named blocker prevents further execution | `BLOCKED` | waiting |
| Execution is complete but a human or external verification remains | `NEEDS_REVIEW` | waiting |

Use `DONE` only when every task passed its transition gate, all in-scope work is complete, and required broader validation has fresh passing evidence. A final broad check does not retroactively validate skipped task gates.

For any gap, use the status that best explains the remaining action and record the exact evidence needed to resume or finish.

## Required Headings

Every status file must contain these headings in order:

```markdown
## Status
## Plan
## Plan Fingerprint
## Reason
## Workspace Baseline
## Files Changed
## Completed
## Remaining
## Validation
## Next
## Resume Notes
```

- **Status** — one of `DONE`, `PARTIAL`, `BLOCKED`, or `NEEDS_REVIEW`.
- **Plan** — the exact plan file path.
- **Plan Fingerprint** — the SHA-256 hash of the approved plan, prefixed with `sha256:`.
- **Reason** — why this status was chosen; for `BLOCKED`, name the blocker; for `DONE`, confirm all evidence is fresh.
- **Workspace Baseline** — branch, dirty files, and in-scope overlap at the time of closeout.
- **Files Changed** — list of files created or modified during execution.
- **Completed** — list of tasks that passed their transition gate, with task-level evidence.
- **Remaining** — list of tasks not yet complete, with the exact work remaining.
- **Validation** — list of validation commands run and their results.
- **Next** — the exact next action to resume or finish.
- **Resume Notes** — context needed to resume execution, including any drift or blockers.

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
4. If verification failed, update the status to `BLOCKED` with the failure details.
