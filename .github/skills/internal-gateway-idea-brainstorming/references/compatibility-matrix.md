# Compatibility Matrix

Use this reference when `internal-gateway-idea-brainstorming` must decide how a request maps to entrypoints, realignment, or transitions.

## Entrypoint Routing

| Entrypoint | Use when | Active phase |
| --- | --- | --- |
| `idea-define` | Substantive idea needs definition, convergence, or handoff. | `discover` |
| `brainstorm` | Open-ended exploration with several credible directions. | `discover` |
| `clarify-first` | Success criteria or constraints are not yet confirmed. | `discover` |
| `direct execute` | Not owned here. After Idea Gate 0 and Critical Gate 2 close, recommend `internal-gateway-simple-task` or `internal-gateway-operational-flow` `execute` when the lane is already concrete, then stop for manual user invocation. | N/A |
| `apply-plan` | Not owned here. After Idea Gate 0 and Critical Gate 2 close, recommend `internal-gateway-operational-flow` `apply-plan` when a retained plan is already approved, then stop for manual user invocation. | N/A |
| `review` | Not owned here. After Idea Gate 0 and Critical Gate 2 close, recommend `internal-gateway-operational-flow` `review` for defect-first review, then stop for manual user invocation. | N/A |
| `plan-only` | A validated Definition Brief exists and needs operational planning. Recommend `internal-gateway-operational-flow` `plan` only after Idea Gate 0, Interview Gate 1, Critical Gate 2, and Handoff Gate 3 conditions are met, then stop for manual user invocation. | N/A |
| `full-cycle` | If the idea gateway produced a validated Definition Brief, recommend `internal-gateway-operational-flow` `full-cycle` only after Idea Gate 0, Interview Gate 1, Critical Gate 2, and Handoff Gate 3 conditions are met, then stop for manual user invocation. | N/A |

## Realignment Rules

| Realignment type | Behavior |
| --- | --- |
| Scope-changing realignment | Invalidates the prior brief. Route visibly back to this gateway. |
| Operational-only realignment | Stays inside `internal-gateway-operational-flow`. |
| Mixed unclassifiable ambiguity | Enters `internal-gateway-operational-flow` conservatively, which may recommend this gateway visibly after substantive idea work is proved. |

## Validated Definition Brief Intake

A Definition Brief produced by this gateway may enter `internal-gateway-operational-flow` `plan` without repeating operational-flow Gate 0 or the Pre-Plan Critical Pass when all of these conditions hold:

- Origin: produced by `internal-gateway-idea-brainstorming`.
- Idea Gate 0: `grill-me satisfied` in the current cycle.
- Interview Gate 1: `ready-for-critical` was declared before critical challenge.
- Critical Gate 2: `confident`.
- Scope unchanged: no realignment changed scope, owner, target state, validation, or anti-scope since the last critical pass.
- Explicit checkpoint: the gateway stopped at `Handoff Gate 3: ready-for-owner-change`.
- Handoff lock cleared: the user explicitly invoked the recommended owner or gave unambiguous imperative approval for the named action and scope.

When these conditions hold, the operational flow consumer accepts the intake and continues with the next phase without re-running Gate 0 or the critical pass. The user confirms and invokes `internal-gateway-operational-flow` manually in a separate turn.

If the next user message after handoff only proposes wording, suggests an
alternative, or refines the idea, the handoff lock remains active. Stay in this
gateway, update the brief if needed, ask one direct confirmation question, and
do not perform delivery work.

If realignment later changes scope, owner, target state, validation, or anti-scope, the intake is invalidated. Restart the relevant gate in the owning gateway. Operational-flow consumers restart Gate 0 and the Pre-Plan Critical Pass in `define`.

## Simple Task Handoff

- When the idea resolves to one quick concrete lane, emit a chat-only `Simple Task Brief` and recommend `internal-gateway-simple-task` only after Idea Gate 0 is `grill-me satisfied` and Critical Gate 2 is `confident`.
- Stop and ask the user to confirm and invoke `internal-gateway-simple-task` manually in a separate turn.
- Do not treat a proposal, preference, or suggested edit as confirmation unless it also explicitly approves the named owner/action/scope.
- Do not create a retained mini-plan.

## Optional Exploration Supports

When multiple credible concept directions remain and the choice is concept-heavy, use `idea-shaping-frameworks.md` and `idea-evaluation-criteria.md` selectively before convergence.

| Support | Positive trigger | Return behavior |
| --- | --- | --- |
| `superpowers-brainstorming` | Design or spec approval workflow is needed. | Return to this gateway before convergence. |
| `grill-me` | Mandatory Idea Gate 0 after every evidence pass. | Return to this gateway before convergence. |

Deterministic maintenance loads none of the above.
