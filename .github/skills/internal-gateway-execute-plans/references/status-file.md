# Status File

Use this reference when `internal-gateway-execute-plans` finishes, pauses, or
blocks retained-plan execution.

The gateway writes exactly one sibling status file in the retained plan folder:

```text
<plan-basename>.<STATUS>.md
```

`<plan-basename>` is the retained plan folder name. `STATUS` must be one of:

- `DONE`
- `BLOCKED`
- `PARTIAL`
- `NEEDS_REVIEW`

## Required Headings

- `## Status`
- `## Reason`
- `## Completed`
- `## Remaining`
- `## Validation`
- `## Next`
- `## Resume Notes`

## Template

```markdown
# <plan-basename> Status

## Status

DONE

## Reason

All in-scope work is complete and required validation passed.

## Completed

- <completed item and evidence path>

## Remaining

- None.

## Validation

- `<command>` passed.

## Next

- No action required.

## Resume Notes

- Re-run `<command>` if new changes appear before merge.
```

## Status Selection

- Use `DONE` only when all in-scope work is complete and required validation
  passed.
- Use `BLOCKED` when safe continuation requires external input, approval,
  missing credentials, dependency access, or a non-repairable blocker.
- Use `PARTIAL` when some planned work remains incomplete or intentionally
  deferred.
- Use `NEEDS_REVIEW` when edits were applied but review, validation, or evidence
  coverage is still required.

Historical `done-*`, `completion-report.md`, `evidence-envelope.md`, and
`<STATE>-plan-state.md` files may be read as evidence. Do not create them as
new gateway closeout artifacts.