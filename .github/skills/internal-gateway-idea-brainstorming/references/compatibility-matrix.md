# Compatibility Matrix

Use this reference when `internal-gateway-idea-brainstorming` must decide how a request maps to entrypoints, realignment, or transitions.

## Entrypoint Routing

| Entrypoint | Use when | Active phase |
| --- | --- | --- |
| `idea-define` | Substantive idea needs definition, convergence, or handoff. | `discover` |
| `brainstorm` | Open-ended exploration with several credible directions. | `discover` |
| `clarify-first` | Success criteria or constraints are not yet confirmed. | `discover` |
| `direct execute` | Not owned here. Route to `internal-gateway-simple-task` or `internal-gateway-operational-flow` `execute` when the lane is already concrete. | N/A |
| `apply-plan` | Not owned here. Route to `internal-gateway-operational-flow` `apply-plan` when a retained plan is already approved. | N/A |
| `review` | Not owned here. Route to `internal-gateway-operational-flow` `review` for defect-first review. | N/A |
| `plan-only` | A validated Definition Brief exists and needs operational planning. Hand off to `internal-gateway-operational-flow` `plan` without repeating ideation. | N/A |
| `full-cycle` | If the idea gateway produced a validated Definition Brief, hand off to `internal-gateway-operational-flow` `full-cycle` without repeating ideation or critical pass. | N/A |

## Realignment Rules

| Realignment type | Behavior |
| --- | --- |
| Scope-changing realignment | Invalidates the prior brief. Route visibly back to this gateway. |
| Operational-only realignment | Stays inside `internal-gateway-operational-flow`. |
| Mixed unclassifiable ambiguity | Enters `internal-gateway-operational-flow` conservatively, which may recommend this gateway visibly after substantive idea work is proved. |

## Validated Definition Brief Intake

- A Definition Brief produced by this gateway and passing critical challenge may enter `internal-gateway-operational-flow` `plan` after an explicit checkpoint.
- Operational flow must not repeat ideation or its critical pass.
- If the brief is later invalidated by realignment, route back to this gateway.

## Simple Task Handoff

- When the idea resolves to one quick concrete lane, emit a chat-only `Simple Task Brief` and recommend `internal-gateway-simple-task`.
- Do not create a retained mini-plan.

## Optional Exploration Supports

| Support | Positive trigger | Return behavior |
| --- | --- | --- |
| `idea-refine` | Multiple credible concept directions remain and the choice is concept-heavy. | Return to this gateway before convergence. |
| `superpowers-brainstorming` | Design or spec approval workflow is needed. | Return to this gateway before convergence. |
| `grill-me` | Unresolved user-only decisions after evidence pass. | Return to this gateway before convergence. |

Deterministic maintenance loads none of the above.
