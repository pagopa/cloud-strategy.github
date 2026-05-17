# Plan Completion Audit

Use this reference when review needs to map a retained plan or promised scope to
what actually changed. Keep the audit evidence-first. Do not accept a completion
claim from chat memory, a `done-*` marker, or intent alone.

## Source Pattern

- Comparative source: `tmp/external-comparison/gstack/ship/SKILL.md` Step 8.
- Use the source as inspiration only. It is not a runtime dependency and is not
  imported into this repository.

## Activation

Use the inline `Completion Checks` from `internal-gateway-operational-flow` for
small, direct tasks. Run this full audit when any condition is true:

- The retained plan has more than 6 executable items or numbered plan files.
- The diff crosses multiple repository-owned asset families.
- The change modifies always-on guidance, wrapper agents, validators, or tests.
- A completion claim depends on manual evidence, external state, or a missing
  validator.
- A reviewer asks whether the delivered diff really matches the approved plan.

## Status Vocabulary

| Status | Criteria | Route |
| --- | --- | --- |
| `DONE` | The item has direct evidence in the diff, target file, or validator output. | Keep as completed. |
| `PARTIAL` | Some required behavior shipped, but a named subpart remains absent or unverified. | Route the missing part to delivery or defer with risk. |
| `NOT_DONE` | No credible evidence shows the item was implemented. | Route to delivery or mark as an explicit non-action. |
| `CHANGED` | The item was intentionally satisfied by a different approach that still meets the approved target. | Cite the replacement and validate scope fit. |
| `UNVERIFIABLE` | The item cannot be checked from available files, diff, reachable paths, or validator output. | State the evidence gap and request proof or downgrade completion state. |

## Verification Classes

Classify each plan item before judging status:

- `DIFF_VERIFIABLE`: changed files can prove or disprove the item.
- `FILE_VERIFIABLE`: the target file or generated artifact can be read directly.
- `VALIDATOR_VERIFIABLE`: command output is required for evidence.
- `MANUAL_VERIFIABLE`: a human observation is required.
- `EXTERNAL_VERIFIABLE`: another repository or service must be inspected.

If an item is `MANUAL_VERIFIABLE` or `EXTERNAL_VERIFIABLE` and no evidence is
available, mark it `UNVERIFIABLE` instead of guessing.

## Procedure

1. Extract every executable item from the plan. Ignore `dubbi-e-domande.md`.
2. Record the declared target state, anti-scope, owner, and validation path.
3. Collect observed evidence from changed files, `git diff`, validators, and
   reachable target paths.
4. Assign a verification class and status to each item.
5. Route every `PARTIAL`, `NOT_DONE`, and `UNVERIFIABLE` item to delivery,
   planning, critical challenge, or defer.
6. Re-check whether the observed delivery introduced scope drift with
   `scope-drift.md`.

## Output Table Template

| Plan item | Verification class | Status | Evidence | Route |
| --- | --- | --- | --- | --- |
| `<item>` | `DIFF_VERIFIABLE` | `DONE` | `<file or validator evidence>` | `<none or owner>` |

## `UNVERIFIABLE` Rules

- Missing plan files, unreadable paths, missing validators, and external-only
  claims are `UNVERIFIABLE` unless independent evidence exists.
- A `done-*` file is a progress marker, not proof. Re-open the item when the
  target file or validator evidence is absent.
- Do not mark `SHIPPED` in a completion report while any required item remains
  `UNVERIFIABLE` without an explicit accepted risk.
