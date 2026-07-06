# Simple Task Lanes

Use this reference when the task stays simple but the execution shape still needs a quick decision.

## Lane Selection

| Lane | Use when | Method posture | Validation |
| --- | --- | --- | --- |
| `answer` | The user needs a direct explanation, decision, or repository-context answer. | Inspect the nearest evidence and answer directly. | Cite the inspected evidence or state the gap. |
| `edit` | The target file and desired outcome are clear. | Make the smallest coherent change. | Run the closest validator, test, syntax check, or bounded manual check. |
| `diagnose` | A bug, failure, drift, or unexpected behavior is present. | Reproduce first, then test one falsifiable hypothesis at a time. | The original loop must pass after the fix, or the blocker must be explicit. |
| `validate` | The main job is checking an existing artifact, command, or result. | Stay read-first and report exact outcomes. | Name the exact check, result, and remaining gap. |

If cost or complexity exceeds same-run execution, stop and recommend a retained plan instead of stretching the lane. If the boundary break is broader than that, stop with reason.

## Output Shapes

For `answer`, return the answer, evidence, and uncertainty.

For `edit`, return `lane`, `files-touched`, validation, and residual risk.

For `diagnose`, return `lane`, reproduced failure, root cause, fix or blocker, and evidence.

For `validate`, return `lane`, check, result, and any follow-up gap.

For `stop-with-reason`, return:

- `boundary break`
- `why stopped`
- `user decision needed`
- `evidence required`

## Multi-Source Mismatch Procedure

When the same symptom may come from multiple sources or transformation layers:

1. Name the target artifact or mismatch.
2. List candidate sources of truth.
3. Map the transformation layers.
4. Choose the cheapest check that can falsify one layer at a time.
5. Stop expanding once one failing layer is proven or source authority stays unclear.

Patch only the proven failing layer.

## Diagnose Deterministic Failure Procedure

When a failure report already contains exact test names, file paths, symbols, or expected strings:

1. Extract the exact anchors.
2. Search those anchors.
3. Read only nearby controlling context.
4. State one falsifiable hypothesis and the cheapest check.
5. Verify the exact context of each intended edit.
6. Apply the smallest grounded edit.
7. Immediately run focused validation.
8. Expand only if the check falsifies the hypothesis or leaves material ambiguity.
