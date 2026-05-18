# Simple Task Lanes

Use this reference when `SKILL.md` confirms the task is simple, but the active
lane or output shape still needs a quick decision.

## Lane Selection

| Lane | Use when | Typical support | Validation |
| --- | --- | --- | --- |
| `answer` | The user needs a direct explanation, decision, or repository-context answer. | Scoped instructions and the nearest domain skill only if facts depend on them. | Cite inspected files or state the evidence gap. |
| `edit` | The target file and desired outcome are clear. | File-type or domain owner such as Python, Terraform, GitHub Actions, Markdown, or cloud support. | Run the closest validator, test, lint, or syntax check. |
| `diagnose` | A failure, bug, drift, or unexpected behavior is present. | `internal-debugging`; add runtime support only after reproducing the symptom. | Original failing loop must pass after the fix, or the blocker is explicit. |
| `validate` | The main job is checking an existing artifact or command result. | Domain owner for the validation surface. | Report the exact command, result, and remaining gap. |
| `escalate` | The task becomes planning, review, critical challenge, or retained-plan execution. | The owning gateway or review skill. | Provide owner, scope, action, validation path, and risk. |

## Coding Examples

- Small script change: inspect existing script layout, load the script skill,
  edit, then run the script or compile/syntax check.
- Bugfix with a known failure: load `internal-debugging`, reproduce first, then
  fix. Use `internal-tdd` for a regression seam when executable behavior changed.
- Behavior feature with an obvious public interface: use `internal-tdd` when the
  user asked for TDD or the seam is valuable enough to protect.
- Terraform or workflow edit: load the matching domain skill, apply the smallest
  contract change, and run the nearest formatter, validator, or catalog check.

## Non-Coding Examples

- Skill or agent copyedit with stable target: inspect the paired asset and
  scoped instructions, edit only the requested owner, then run the local
  skill or catalog validator when available.
- Markdown guidance clarification: use scoped Markdown rules and the nearest
  owner. Do not create a retained plan for a clear local wording fix.
- Catalog or inventory drift: if the fix is generated inventory only, run the
  existing inventory builder. If the drift changes managed scope, leave simple
  mode and use the sync owner.
- Advisory answer: inspect repository evidence first, answer in chat, and name
  what was not validated if no command was run.

## Output Shapes

For `answer`, return the answer, evidence, and any uncertainty.

For `edit`, return files changed, focused validation, and residual risk.

For `diagnose`, return the reproduced failure, root cause, fix, and evidence.

For `validate`, return the command or check, result, and any follow-up owner.

For `escalate`, return the boundary break, next owner, scope, action,
validation path, and risk.
