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
| `Continuation` | yes | `continuing` or `waiting`. |
