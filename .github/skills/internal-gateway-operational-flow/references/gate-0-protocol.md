# Gate 0 Protocol

Use this reference when Gate 0 activation, status, blocking, closure, or
request-change realignment needs more detail than the main gateway skill should
carry.

## Activation

- Run the minimum evidence pass first, then start Gate 0 inside `define` for
  pre-`plan` entrypoints (`define-first`, `plan-only`, `full-cycle` without a
  confirmed definition).
- Gate 0 applies before plan output and recommendations for every
  non-`execute` operational-flow entrypoint. Direct `execute` is the only
  automatic Gate 0 exception. `apply-plan` and `review` run a visible define
  pre-start gate before the operational phase begins.
- Rich prompts, concrete tasks, mechanical tasks, retained-plan approval,
  recoverable repository evidence, and pre-start signals do not waive Gate 0
  for pre-`plan` entrypoints. For mechanical work, ask a minimal, clear, and
  concise `grill-me` question set instead of skipping the gate.

## Status

| Status | Use when | Effect |
| --- | --- | --- |
| `grill-me required` | The mandatory Gate 0 loop has not been explicitly closed by the user for the current request, context, and environment. | Stop before plan output, recommendation, review output, or retained-plan application; ask the `grill-me` question set. Does not block direct `execute`. |
| `grill-me satisfied` | The user answered or explicitly accepted defaults in the current Gate 0 loop, gave a closure or proceed signal, the answers still match the current scope, and no unresolved user-only decision remains. | Continue with the current phase while the request remains stable. |

`grill-me` supplies the interview shape. `internal-gateway-operational-flow`
owns Gate 0 status labels and blocking semantics.

## Blocking And Closure

- Declare exactly one Gate 0 status before downstream plan output or
  recommendation.
- Keep `plan` and planning output blocked while the result is
  `grill-me required`. Direct `execute` is the only automatic Gate 0
  exception. `apply-plan` and `review` run a visible define pre-start gate
  before the operational phase begins.
- When the gate is `grill-me required`, stop and ask numbered questions using
  `Question`, `Recommendation`, `Why`, and `Default if accepted`.
- Only the user may close or stop the loop. The agent may recommend closure,
  but must wait for a user closure signal such as "ok", "go", "proceed",
  "close", accepted defaults, or an equivalent proceed instruction.

### Short Confirmation Semantics

Short confirmations such as "ok" confirm only the immediately preceding complete checkpoint when that checkpoint already states owner, action, and scope. A short confirmation does not authorize work introduced after the confirmed package or clear an ambiguous handoff lock. Keep explicit invocations and unambiguous imperatives as the strongest authorization signals.

## Phase Transition Authorization

- Closing Gate 0 changes the gate status only. It does not change the active
  phase.
- For `define-first`, the
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

## Validated Definition Brief Intake

A Definition Brief produced by `internal-gateway-idea-brainstorming` may enter
`plan` without repeating Gate 0 or the Pre-Plan Critical Pass when all of these
conditions hold:

- Origin: produced by `internal-gateway-idea-brainstorming`.
- Idea Gate 0: `grill-me satisfied` in the current cycle.
- Interview Gate 1: `ready-for-critical` was declared before critical challenge.
- Critical Gate 2: `confident`.
- Scope unchanged: no realignment changed scope, owner, target state,
  validation, or anti-scope since the last critical pass.
- Explicit checkpoint: the idea gateway stopped at
  `Handoff Gate 3: ready-for-owner-change`.
- Handoff lock cleared: the user explicitly invoked this owner or gave
  unambiguous imperative approval for the named action and scope.

When these conditions hold, the operational flow consumer accepts the intake,
treats `Idea Gate 0: grill-me satisfied` and `Critical Gate 2: confident` as
already met, and continues with the next phase. Generic non-`execute`
entrypoints that do not meet every condition still require Gate 0.

If the next user message after the idea-gateway handoff only proposes wording,
suggests an alternative, or refines the idea, the handoff lock is not cleared.
Return to the idea gateway state or ask one direct confirmation question before
planning or delivery output.

If realignment later changes scope, owner, target state, validation, or
anti-scope, the intake is invalidated. Restart Gate 0 and the Pre-Plan Critical
Pass in `define`.

## Realignment

- If request, target path, context, environment, tool output, dependency
  state, validation posture, or dirty-worktree ownership changes during a
  `define` or `plan` phase, run the minimum new evidence pass, restart Gate 0,
  and stop again while the result is `grill-me required`.
- After Gate 0 is re-satisfied following a realignment, re-run the Pre-Plan
  Critical Pass. The previous `confident` outcome is invalidated because the
  definition it challenged has changed. Do not carry a stale `confident`
  forward into `plan`.
- Realignment does not restart Gate 0 or the Pre-Plan Critical Pass during
  active `execute`. After the visible `apply-plan` pre-start gate closes,
  retained-plan execution continues without restarting Gate 0 unless the lane
  changes back to `define` or `plan`.

### Material-Decision Realignment

Review or critical findings that introduce a new material choice affecting
scope, owner, target state, validation, rollout, or anti-scope reopen Gate 0
before planning or delivery recommendation. Resume only affected branches when
impact is local. Do not let repository evidence silently choose between
materially different rollout or ownership strategies.
