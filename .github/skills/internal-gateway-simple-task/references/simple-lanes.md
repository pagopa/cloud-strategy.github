# Simple Task Lanes

Use this reference when `SKILL.md` confirms the task is simple, but the active
lane or output shape still needs a quick decision.

## Lane Selection

| Lane | Use when | Support posture | Validation |
| --- | --- | --- | --- |
| `answer` | The user needs a direct explanation, decision, or repository-context answer. | Load only the relevant domain owner when facts depend on it. | Cite inspected files or state the evidence gap. |
| `edit` | The target file and desired outcome are clear. | Load the smallest file-type, runtime, authoring, or domain owner proved by evidence. | Run the closest validator, test, lint, syntax check, or focused manual check. |
| `diagnose` | A failure, bug, drift, or unexpected behavior is present. | Reproduce the loop first, then add runtime or domain support only if needed. | The original loop must pass after the fix, or the blocker must be explicit. |
| `validate` | The main job is checking an existing artifact, command, or result. | Load the owner for the validation surface only when needed. | Report the exact check, result, and remaining gap. |
| `plan` | The task is concrete but the user asks for a plan, or cost signals show that same-chat execution is less economical than a retained plan. | Load `internal-gateway-writing-plans` after `grill-me` and `internal-gateway-critical-master`. | The plan is written, validated against the writing contract, and the folder is ready for `internal-gateway-execute-plans`. |
| `escalate` | The task becomes staged, review-owned, retained-plan-owned, critical-challenge owned, or exceeds `references/clarification-gate.md`. | Stop and name the next owner. | Provide boundary break, owner, scope, action, validation path, and risk. |

## Examples

- Clear prose or skill wording fix: inspect the paired asset and relevant
  domain owner, edit the smallest owner, then run the closest skill or Markdown
  validation.
- Small code or script change: inspect local patterns, load the matching runtime
  support only if needed, edit, then run the focused executable check.
- Known failure: reproduce the failing loop, fix the root cause, then rerun that
  loop before claiming completion.
- Advisory answer: inspect repository evidence first, answer in chat, and name
  what was not validated if no command was run.
- Ownership ambiguity: stop at `escalate` instead of converting uncertainty into
  hidden planning.
- Plan mode: concrete task that is too large for same-chat execution or
  explicitly requested as a plan; classify `plan-mode`, delegate retained
  writing to `internal-gateway-writing-plans`, and stop before execution.
- Clarification overflow: use `escalate` when the simple clarification gate
  would need more than one focused `grill-me` block.

## Output Shapes

For `answer`, return the answer, evidence, and uncertainty.

For `edit`, return `lane`, `support-loaded`, `files-touched`, direct-control
status, focused validation, and residual risk.

For `diagnose`, return `lane`, `support-loaded`, the reproduced failure, root
cause, direct-control status, fix or blocker, and evidence.

For `validate`, return `lane`, `support-loaded`, the command or check, result,
direct-control status, and any follow-up owner.

For `escalate`, return the boundary break, next owner, scope, action, validation
path, and risk.

## Multi-Source Mismatch Procedure

When the same symptom may come from multiple sources or transformation layers,
use this lightweight procedure before patching:

1. Name the target artifact or observed mismatch.
2. List the candidate sources of truth and mark one authoritative only when
   evidence already proves it.
3. Map the transformation layers between source and target.
4. Choose the cheapest check that can falsify one source or layer at a time.
5. Stop expanding once one layer is proven wrong or source authority remains
   unproven and needs escalation.

Patch only the proven failing layer. Do not convert this generic procedure into
domain-specific incident language.

## Diagnose Deterministic Failure Procedure

When a failure report already contains exact test names, file paths, symbols, or
expected strings, use this ordered procedure before broader evidence gathering:

1. Extract exact anchors from the failure output.
2. Search those exact anchors in the repository.
3. Read only nearby controlling context around the matches.
4. State one falsifiable hypothesis and the cheapest check that can disprove it.
5. Verify the exact context of every hunk you intend to edit.
6. Apply the smallest grounded edit.
7. Immediately run focused validation.
8. Expand evidence only when the check falsifies the hypothesis or leaves material
   ambiguity.

References and neighboring owners load only when exact evidence is insufficient.
Redundant or speculative edits must not appear in the first patch. The original
failure loop remains required before any fixed or resolved claim.
