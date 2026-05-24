# Simple Task Lanes

Use this reference when `SKILL.md` confirms the task is simple, but the active
lane or output shape still needs a quick decision.

## Lane Selection

| Lane | Use when | Support posture | Validation |
| --- | --- | --- | --- |
| `answer` | The user needs a direct explanation, decision, or repository-context answer. | Load only scoped instructions or a domain owner when facts depend on them. | Cite inspected files or state the evidence gap. |
| `edit` | The target file and desired outcome are clear. | Load the smallest file-type, runtime, authoring, or domain owner proved by evidence. | Run the closest validator, test, lint, syntax check, or focused manual check. |
| `diagnose` | A failure, bug, drift, or unexpected behavior is present. | Reproduce the loop first, then add runtime or domain support only if needed. | The original loop must pass after the fix, or the blocker must be explicit. |
| `validate` | The main job is checking an existing artifact, command, or result. | Load the owner for the validation surface only when needed. | Report the exact check, result, and remaining gap. |
| `escalate` | The task becomes staged, review-owned, retained-plan-owned, critical-challenge owned, or exceeds `references/clarification-gate.md`. | Stop and name the next owner. | Provide boundary break, owner, scope, action, validation path, and risk. |

## Examples

- Clear prose or skill wording fix: inspect the paired asset and scoped
  instructions, edit the smallest owner, then run the closest skill or Markdown
  validation.
- Small code or script change: inspect local patterns, load the matching runtime
  support only if needed, edit, then run the focused executable check.
- Known failure: reproduce the failing loop, fix the root cause, then rerun that
  loop before claiming completion.
- Advisory answer: inspect repository evidence first, answer in chat, and name
  what was not validated if no command was run.
- Ownership ambiguity: stop at `escalate` instead of converting uncertainty into
  hidden planning.
- Clarification overflow: use `escalate` when the simple clarification gate
  would need more than one focused `grill-me` block.

## Output Shapes

For `answer`, return the answer, evidence, and uncertainty.

For `edit`, return `lane`, `support-loaded`, `files-touched`, focused
validation, and residual risk.

For `diagnose`, return `lane`, `support-loaded`, the reproduced failure, root
cause, fix or blocker, and evidence.

For `validate`, return `lane`, `support-loaded`, the command or check, result,
and any follow-up owner.

For `escalate`, return the boundary break, next owner, scope, action, validation
path, and risk.
