# Resume Protocol

Use this verify-first protocol when resuming retained-plan execution through
`internal-gateway-execute-plans`.

## Verify-First Sequence

1. Resolve the retained plan folder and plan basename.
2. Look for a sibling status file named `<plan-basename>.<STATUS>.md`.
3. Read `## Status`, `## Reason`, `## Remaining`, `## Validation`, `## Next`,
   and `## Resume Notes` before editing.
4. Re-check the target files, current diff, and nearest validation command named
   in the status file or retained plan.
5. Resume through `superpowers-executing-plans` only when the status and fresh
   evidence support continuation.

## Reconciliation Rules

- If the status file says `DONE`, do not resume unless new evidence invalidates
  completion.
- If the status file says `BLOCKED`, resolve or route the blocker before
  editing.
- If the status file says `PARTIAL`, continue from the first evidenced
  remaining item.
- If the status file says `NEEDS_REVIEW`, review or validate before adding new
  work.
- If no status file exists, reconstruct the current state from retained-plan
  files, diff, and validators, then write the status file before stopping.
