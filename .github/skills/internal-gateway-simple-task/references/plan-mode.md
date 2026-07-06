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
execution only for tiny local work; otherwise switch to `plan-mode` and let
`internal-gateway-writing-plans` handle retained-writing decisions.

A cost checkpoint pauses before a new expensive tool burst, broad reread, or
multi-step execution loop. It does not interrupt ordinary conversation,
grill-me analysis, or collaborative study when no expensive tool action is
starting.

When the user explicitly asks for broader output, deeper analysis, or continued
execution, name the likely token or context impact first and then either
continue with the smallest bounded next slice or ask for confirmation before
the new expensive burst.

## Delegated retained writing

`internal-gateway-simple-task` does not choose retained-plan profile, folder
shape, or artifact internals. It only decides that same-chat execution should
stop and retained writing should begin.

When plan mode is confirmed, pass these facts to `internal-gateway-writing-plans`:

- concrete target state
- anti-scope
- nearest owner
- validation path or explicit validation gap
- cost signals that made same-chat execution less economical
- stop conditions
- observable acceptance

`internal-gateway-writing-plans` then delegates artifact decisions to
`superpowers-writing-plans`.

## Confirmation rule for implicit triggers

For implicit cost-signal triggers, emit a short statement that:

1. Names the detected cost signals.
2. Proposes `plan-mode` and names that retained writing will be delegated to
   `internal-gateway-writing-plans`.
3. Asks the user to confirm or decline the switch before writing anything.

Do not write the retained plan until the user confirms.

## Procedure inside plan mode

1. Classify the gate as `plan-mode`.
2. Run `grill-me` with one compact numbered block.
3. Load `internal-gateway-critical-master` after the user responds.
4. If critical gate returns confident, load `internal-gateway-writing-plans`.
5. Pass the preflight facts to `internal-gateway-writing-plans` and let it
   delegate the writing outcome.
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
  retained plan through `internal-gateway-writing-plans`.
- User: *"Modalità plan: riscrivi il parser dei skills"*: classify
  `plan-mode` explicit, run the full gate, write the plan, stop.
- User: *"Cosa ne pensi di rifattorizzare tutto?"*: this is not concrete; do
  not use plan mode. Escalate to `internal-gateway-idea-brainstorming`.

## Common failure modes

- Treating an implicit cost signal as a decision to write a plan without
  confirming with the user.
- Reintroducing retained-plan profile decisions instead of delegating them.
- Writing the plan but then executing it inside simple task.
- Using plan mode as a way to avoid saying that the task is actually vague or
  ownership-ambiguous.
