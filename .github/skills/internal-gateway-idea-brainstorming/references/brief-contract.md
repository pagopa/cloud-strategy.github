# Brief Contract

Use this reference for the exact fields expected in `internal-gateway-idea-brainstorming` output artifacts.

## Definition Brief

Produced at the end of `converge` and consumed by `internal-gateway-operational-flow` `plan`.

| Field | Required | Description |
| --- | --- | --- |
| `Intent` | yes | What the user is trying to decide or achieve. |
| `Recovered evidence` | yes | Files, repository facts, or source facts used. |
| `Resolved decisions` | yes | Branches closed through the interview or evidence. |
| `Open decisions` | yes | User-only decisions or `none`. |
| `Direction or options` | yes | The chosen path or the narrowed set. |
| `Anti-scope` | yes | What must not happen yet. |
| `Validation path or gap` | yes | Command, review path, or explicit gap. |
| `Risk` | yes | Residual risk or rollback note. |
| `Stop & checkpoint` | yes | Where to pause and the exact approval needed. |

## Simple Task Brief

Produced when the idea resolves to one quick concrete lane. Chat-only; not a retained plan artifact.

| Field | Required | Description |
| --- | --- | --- |
| `Target` | yes | What should be done. |
| `Action` | yes | One concrete action. |
| `Validation` | yes | Focused validation path or explicit gap. |
| `Risk` | yes | Residual risk. |
| `Next owner` | yes | `internal-gateway-simple-task`. |

## Recommended Next Owner

Produced at `handoff` when the critical pass is `confident`.

| Field | Required | Description |
| --- | --- | --- |
| `Recommended next owner` | yes | Exact agent or skill owner. |
| `Reason` | yes | Why this owner fits the resolved idea. |
| `Scope` | yes | Files, directories, artifacts, or decision surface in scope. |
| `Action` | yes | One concrete next action. |
| `Validation` | yes | Command, review path, evidence, or explicit gap. |
| `Risk` | yes | Residual risk or rollback note. |
| `Continuation` | yes | Always `waiting` at a next-owner transition. |
| `User action required` | yes | Ask the user to confirm the recommended gate and invoke the named owner manually in a separate turn. State that proposals or wording preferences alone do not authorize delivery work. |

The gateway stops after emitting this package. It must not invoke, simulate, or execute the recommended owner internally.

## Handoff Lock

`Continuation: waiting` activates a handoff lock. The lock stays active until the
user explicitly invokes the recommended owner or gives unambiguous imperative
approval for the named action and scope.

Messages that only propose wording, suggest an option, discuss an alternative,
or refine the idea do not clear the lock. In that case, keep the work inside
`internal-gateway-idea-brainstorming`, update the brief or ledger if useful,
ask one direct confirmation question, and stop without editing files.
