# Plan Completion Audit

Use this reference when review needs to map a retained plan or promised scope to
what actually changed. Keep the audit evidence-first. Do not accept a completion
claim from chat memory or intent alone.

## Source Pattern

- Comparative source: `tmp/external-comparison/gstack/ship/SKILL.md` Step 8.
- Use the source as inspiration only. It is not a runtime dependency and is not
  imported into this repository.

## Activation

Use the inline completion evidence from the active gateway owner for
small, direct tasks. Run this full audit when any condition is true:

- The retained plan has more than 6 executable items.
- The diff crosses multiple repository-owned asset families.
- The change modifies always-on guidance, wrapper agents, validators, or tests.
- A completion claim depends on manual evidence, external state, or a missing
  validator.
- A reviewer asks whether the delivered diff really matches the approved plan.

## Inputs

The audit requires:

- **Exact plan file** — the approved retained plan under `tmp/superpowers/plans/`.
- **Exact status sibling** — the `<plan-basename>.<STATUS>.md` file produced by the executor.
- **Matching fingerprint** — the SHA-256 hash in the status file must match the plan file.

Use the status sibling's `## Completed`, `## Remaining`, and `## Validation` sections as the item-level evidence source.

## Status Vocabulary

| Status | Criteria | Route |
| --- | --- | --- |
| `DONE` | Every required item has direct evidence in the diff, target file, or validator output. | Keep as completed. |
| `PARTIAL` | Some required behavior shipped, but a named subpart remains absent or unverified. | Route the missing part to delivery or defer with risk. |
| `NEEDS_REVIEW` | Execution is complete but a human or external verification remains. | State the evidence gap and request proof. |
| `BLOCKED` | A named blocker prevents further execution. | Route to delivery or mark as an explicit non-action. |

## Verification Classes

Classify each plan item before judging status:

- `DIFF_VERIFIABLE`: changed files can prove or disprove the item.
- `FILE_VERIFIABLE`: the target file or generated artifact can be read directly.
- `VALIDATOR_VERIFIABLE`: command output is required for evidence.
- `MANUAL_VERIFIABLE`: a human observation is required.
- `EXTERNAL_VERIFIABLE`: another repository or service must be inspected.

If an item is `MANUAL_VERIFIABLE` or `EXTERNAL_VERIFIABLE` and no evidence is
available, mark it `NEEDS_REVIEW` instead of guessing.

## Procedure

1. Verify the status sibling fingerprint matches the plan file.
2. Extract every executable item from the plan.
3. Read the `## Completed`, `## Remaining`, and `## Validation` sections from the status sibling.
4. Record the declared target state, anti-scope, owner, and validation path.
5. Collect observed evidence from changed files, `git diff`, validators, and
   reachable target paths.
6. Assign a verification class and status to each item.
7. Route every `PARTIAL` and `NEEDS_REVIEW` item to delivery,
   planning, critical challenge, or defer.
8. Re-check whether the observed delivery introduced scope drift with
   `scope-drift.md`.

## Output Table Template

| Plan item | Verification class | Status | Evidence | Route |
| --- | --- | --- | --- | --- |
| `<item>` | `DIFF_VERIFIABLE` | `DONE` | `<file or validator evidence>` | `<none or owner>` |

## `NEEDS_REVIEW` Rules

- Missing validators, unreadable paths, and external-only
  claims are `NEEDS_REVIEW` unless independent evidence exists.
- Do not mark `DONE` while any required item remains
  `NEEDS_REVIEW` without an explicit accepted risk.
- `DONE` only when every required item is evidence-backed.
