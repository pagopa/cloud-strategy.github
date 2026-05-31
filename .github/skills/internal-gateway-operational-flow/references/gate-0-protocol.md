# Gate 0 Protocol

Use this reference when Gate 0 activation, status, blocking, closure, or
request-change realignment needs more detail than the main gateway skill should
carry.

## Activation

- Run the minimum evidence pass first, then start Gate 0 inside `define` for
  pre-`plan` entrypoints (`define-first`, `plan-only`, `full-cycle` without a
  confirmed definition).
- Gate 0 applies before plan output and recommendations for every
  non-`execute` operational-flow entrypoint. Direct `execute` and `apply-plan` are the only
  automatic Gate 0 exceptions. `review` runs a define pre-start
  gate before the operational phase begins.
- Rich prompts, concrete tasks, mechanical tasks, retained-plan approval,
  recoverable repository evidence, and pre-start signals do not waive Gate 0
  for pre-`plan` entrypoints. For mechanical work, ask a minimal, clear, and
  concise `grill-me` question set instead of skipping the gate.

## Status

| Status | Use when | Effect |
| --- | --- | --- |
| `grill-me required` | The mandatory Gate 0 loop has not been explicitly closed by the user for the current request, context, and environment. | Stop before plan output or recommendation; ask the `grill-me` question set. Does not block direct `execute` or `apply-plan`. |
| `grill-me satisfied` | The user answered or explicitly accepted defaults in the current Gate 0 loop, gave a closure or proceed signal, the answers still match the current scope, and no unresolved user-only decision remains. | Continue with the current phase while the request remains stable. |

`grill-me` supplies the interview shape. `internal-gateway-operational-flow`
owns Gate 0 status labels and blocking semantics.

## Blocking And Closure

- Declare exactly one Gate 0 status before downstream plan output or
  recommendation.
- Keep `plan` and planning output blocked while the result is
  `grill-me required`. Direct `execute` and `apply-plan` are the only automatic Gate 0
  exceptions. `review` runs a define pre-start gate
  before the operational phase begins.
- When the gate is `grill-me required`, stop and ask numbered questions using
  `Question`, `Recommendation`, `Why`, and `Default if accepted`.
- Only the user may close or stop the loop. The agent may recommend closure,
  but must wait for a user closure signal such as "ok", "go", "proceed",
  "close", accepted defaults, or an equivalent proceed instruction.

## Phase Transition Authorization

- Closing Gate 0 changes the gate status only. It does not change the active
  phase.
- For `define-first`, brainstorming, and clarify-first entrypoints, the
  workflow remains in `define` after `grill-me` is satisfied.
- After Gate 0 closure and `Define Check 1-3`, the Pre-Plan Critical Pass runs
  automatically before any transition recommendation. The critical pass loads
  `internal-gateway-critical-master` and challenges the Definition Brief.
  - On `confident`: update the Definition Brief with critical insights, declare
    `pre-plan critical: confident`, and stop in `define`.
  - On `reopen`: declare `pre-plan critical: reopen`, present objections to the
    user, and re-enter `define` with the critical findings as new input. Restart
    Gate 0 if scope, owner, target state, validation, or anti-scope changed.
- The Pre-Plan Critical Pass blocks plan output the same way Gate 0 does.
  When the status is `pre-plan critical: reopen`, plan output and transition
  recommendations remain blocked until the define-critical cycle resolves to
  `confident`. Do not produce plan output while the critical pass is `reopen`.
- The agent may say that the definition looks ready and may recommend moving to
  `plan` only after the Pre-Plan Critical Pass returns `confident`. The agent
  must still wait for the user to explicitly request that phase.
- Agreement, option selection, accepted defaults, or approval-like replies only
  update the definition. They do not authorize plan output.
- A valid transition request must directly ask for planning or name the next
  phase, such as `write the plan`, `create the implementation
  plan`, or an equivalent instruction.

## Realignment

- If request, target path, context, environment, tool output, dependency
  state, validation posture, or dirty-worktree ownership changes during a
  `define` or `plan` phase, run the minimum new evidence pass, restart Gate 0,
  and stop again while the result is `grill-me required`.
- After Gate 0 is re-satisfied following a realignment, re-run the Pre-Plan
  Critical Pass. The previous `confident` outcome is invalidated because the
  definition it challenged has changed. Do not carry a stale `confident`
  forward into `plan`.
- Realignment does not restart Gate 0 or the Pre-Plan Critical Pass for
  `execute` or `apply-plan` entrypoints. If a lane-change from
  execution back to `plan` is needed, Gate 0 and the Pre-Plan Critical Pass
  restart in the new `define` or `plan` phase.
