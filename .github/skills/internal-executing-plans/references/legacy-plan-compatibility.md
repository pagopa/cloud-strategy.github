# Legacy Plan Compatibility

Load this reference only when executing or validating a retained plan folder
without a declared `Plan profile`.

## Profile Classification

When a folder lacks `Plan profile` in `02-source-item-ledger.md`, classify as
`legacy`. Legacy classification does not block execution; use backward-compatible
reading rules.

## Legacy File Name Mappings

| Legacy name | Current name | Treatment |
| --- | --- | --- |
| `01-summary-direction-and-decision.md` | `01-change-summary.md` | Read as summary. |
| `02-operational-matrix.md` | `02-source-item-ledger.md` | Read as ledger when present. |
| `02-execution.md` | Executable numbered file | Read as executable. |
| `doubts-and-questions.md` | `questions.md` | Read for accepted decisions; exclude from execution loop. |

## Backward-Compatible Reading Order

For legacy folders:

1. Read `01-summary-direction-and-decision.md` or `01-change-summary.md` first.
2. Read `02-operational-matrix.md` or `02-source-item-ledger.md` for classification.
3. If missing `Plan profile`, treat as `legacy` and infer required files from
   what exists on disk.
4. Read `04-implementation-contract.md` when present.
5. Read remaining numbered executable files in order.
6. Ignore `doubts-and-questions.md` or `questions.md` during execution.

## Field Inference

When legacy files lack fields required by the current contract:

| Missing field | Fallback |
| --- | --- |
| `Recommended use` | Infer from folder state: `approved-to-apply` if user explicitly requested execution, `review` otherwise. |
| `Plan profile` | Classify as `legacy`. |
| `File map and role` | Infer from file names on disk. |
| `Initial evidence pass` | Use target existence, riskiest claim, nearest validator. |
| `Reading budget` | Confine to the active folder; exclude sibling `tmp/superpowers/` folders. |
| `Clarification gate` | If gate status is missing and user explicitly requested execution, infer `clarification satisfied`. Otherwise stop and reopen. |
| Source-item coverage | Reconstruct from executable file items and explicit non-actions. Missing coverage is a handoff gap for non-trivial plans. |

## Non-Blocking Compatibility

Legacy classification is not a stop condition. Execute legacy folders when:

- The user explicitly requested execution.
- All required plan files exist on disk (even under legacy names).
- Source-item coverage can be reconstructed or the plan is simple enough that
  coverage reconstruction is not needed.
- No mandatory field absence blocks safe continuation.

Stop only when a mandatory input is missing and cannot be reconstructed from
reachable evidence.
