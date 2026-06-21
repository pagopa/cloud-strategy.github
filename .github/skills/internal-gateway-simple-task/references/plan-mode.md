# Simple Task Plan Mode

Use this reference when `internal-gateway-simple-task` is about to classify a
concrete task as `plan-mode` instead of executing it in the same chat.

## What plan mode is

Plan mode keeps the task inside `internal-gateway-simple-task` but changes the
output shape: the agent writes a retained plan and stops before execution. The
task must remain concrete and single-lane; only the delivery mode changes.

## Activation

### Mandatory explicit trigger

If the user asks for a plan with any of these signals, switch to plan mode and
honor the request without trying to execute:

- `plan`, `piano`, `modalità plan`, `retained plan`
- `scrivi il piano`, `scrivi un plan`, `fammi il piano`
- `non eseguire ancora`, `stop prima dell'esecuzione`
- `salva il piano`, `persistilo`, `plan mode`

### Implicit cost-signal trigger

If the user does not mention a plan, but the following signals show that
same-chat execution would be less economical than a retained plan, declare the
signal and ask for explicit confirmation before switching to plan mode.

### Cost-signal checklist

- The user hints at continuation across chats, e.g. *"continuiamo dopo"*,
  *"in un'altra chat"*, *"domani"*, *"salva per dopo"*, *"persistilo"*.
- The task requires more than roughly 5-7 concrete executable steps.
- The task touches more than roughly 3 unrelated files or path families.
- The task has multiple independent validators or validation surfaces.
- The task depends on external pins that may not resolve in this chat
  (tokens, API availability, runner state, human approval, third-party
  provisioning).
- There is material risk that context pressure or chat limits will interrupt
  the work before it can be validated.
- The task centers on large `.csv`, `.tsv`, `.xlsx`, JSON log exports,
  repeated tool output, or broad file changes that would bloat chat context.
- The user is asking for a large refactor, migration, or cross-file mechanical
  change that is safer as a tracked plan.

Do not switch to plan mode implicitly without declaring the detected signals
and asking for user confirmation.

### Token Budget Gate

When the cost signals come mainly from context pressure instead of task count,
prefer a compact evidence posture rather than a raw-output posture. Keep same-chat
execution only for tiny local work; otherwise switch to `plan-mode` and let the
profile guard choose whether `compact` is still safe.

## Profile selection

- **Default `compact`**: use only when the task stays within a single owner,
  concrete target, one primary validation path, one execution lane, and low
  completeness risk. Folder name follows `tmp/superpowers/mini-plan-*` and
  contains `01-change-summary.md` and `02-execution.md`.
- **Plan Profile Selection Guard**: escalate to `extended` when context or
  completeness risk is material, especially for cross-skill token-discipline
  work, validator-impacting changes, exports or generated reports, datasets
  that need non-trivial reconciliation, several independent validators, an
  articulated anti-scope, or external pins that must be tracked in a control
  file.

When profile safety is in doubt, prefer `extended` and state why. Prefer
`compact` only when the plan can record the contrary evidence that keeps
lower-context execution safe.

## Confirmation rule for implicit triggers

For implicit cost-signal triggers, emit a short statement that:

1. Names the detected cost signals.
2. Proposes `plan-mode` with the safest profile suggested by the signals,
   defaulting to `compact` only when the profile guard stays clear.
3. Asks the user to confirm, decline, or choose `extended`.

Do not write the retained plan until the user confirms.

## Procedure inside plan mode

1. Classify the gate as `plan-mode`.
2. Run `grill-me` with one compact numbered block.
3. Load `internal-gateway-critical-master` after the user responds.
4. If critical gate returns confident, load `internal-gateway-writing-plans`.
5. Choose the profile and write the retained plan following the
   `internal-gateway-writing-plans` contract.
6. Stop before execution. Report the plan folder and hand off to
   `internal-gateway-execute-plans` for future execution.

## Boundaries

- Do not use plan mode to avoid ownership ambiguity. If the target, anti-scope,
  or validation strategy is unclear, `escalate` to `internal-gateway-idea-brainstorming`
  or `internal-gateway-review`.
- Do not use plan mode for vague ideas or substantive tradeoffs; those belong
  to `internal-gateway-idea-brainstorming`.
- Do not execute the plan inside `internal-gateway-simple-task`. Execution is
  owned by `internal-gateway-execute-plans`.
- Do not silently downgrade an explicit user request for a plan into a
  same-chat execution.

## Examples

- User: *"Aggiungi un nuovo campo al modello e al database"* with 8 files and
  a migration: classify `plan-mode` implicit, ask confirmation, then write a
  `compact` plan.
- User: *"Modalità plan: riscrivi il parser dei skills"*: classify
  `plan-mode` explicit, run the full gate, write the plan, stop.
- User: *"Cosa ne pensi di rifattorizzare tutto?"*: this is not concrete; do
  not use plan mode. Escalate to `internal-gateway-idea-brainstorming`.

## Common failure modes

- Treating an implicit cost signal as a decision to write a plan without
  confirming with the user.
- Choosing `extended` for a task that only needs `compact`.
- Writing the plan but then executing it inside simple task.
- Using plan mode as a way to avoid saying that the task is actually vague or
  ownership-ambiguous.
