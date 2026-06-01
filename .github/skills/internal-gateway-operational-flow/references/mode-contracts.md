# Mode Contracts

Use this reference when the staged `define`, `plan`, `execute`, `apply-plan`, `review`, or critical boundary needs more detail than the main skill should carry.

## Mode Boundaries

| Entrypoint / Mode | Owns | Must not own |
| --- | --- | --- |
| `define` | Initial brainstorming, user intent, success criteria, constraints, anti-scope, option exploration, Gate 0 closure, Definition Briefs, and Pre-Plan Critical Pass. | Implementation plans, retained-plan authoring, local edits, or proof of completion. |
| `plan` | Ambiguity resolution after the definition is confirmed with `pre-plan critical: confident`, decision records, retained plans, rollout shape, governance calls, and non-trivial repository-owned authoring. | Routine local execution, defect-first validation, open-ended brainstorming, or pure pressure testing. |
| `execute` | Clear local implementation, deterministic realignment, nearby documentation/test updates, and concrete validation. | Strategic tradeoffs, unresolved ownership, non-trivial rollout decisions, review-first asks, or assumption challenge. |
| `apply-plan` | Repository-owned retained plan folder application with `done-*` tracking, source-item ledger coverage, blocker handling, cross-file continuation, completion checks, and physical close packaging. | Creating or approving the plan, applying inline plans without checkpoint, silently expanding scope, executing `questions.md`, or reporting `SHIPPED` before close packaging. |
| `review` | Findings, severity, confidence, causal layer, validation evidence, regression risk, systems risk, fix routing, and Review Gate. | Applying fixes, designing the initial solution, or open-ended challenge. |
| `critical` | Challenge, pre-mortem, hidden-assumption tests, failure modes, and reframing. | Implement or routine-review. |

The entrypoint table in `internal-gateway-operational-flow` `SKILL.md` maps user-visible entrypoints to the first active mode. This reference owns the mode boundary contracts.

If intent or success criteria are not confirmed, choose `define`. If two post-definition modes still plausibly fit, choose `plan` and make the uncertainty explicit.

## Medium-Task Thresholds

`execute` mode remains valid only when all of these are true:

- The desired outcome is already concrete.
- Verification is concrete enough to run locally or name as an explicit gap.
- The work applies an already-decided contract rather than redesigning ownership, routing, or catalog boundaries.
- Adjacent file changes stay within one coherent maintenance area.
- For retained plans, the input is an approved `tmp/superpowers/<clear-action-or-task-name>/` folder and the remaining work is execution.

`plan` mode becomes the safer owner when at least one of these is true:

- Real ambiguity remains about shape, contract, rollout, or ownership.
- There are at least two credible solution paths with non-trivial tradeoffs.
- The change materially alters routing, ownership, naming contracts, or catalog boundaries.
- The task creates a new repository-owned resource and the boundary has not already been approved.
- Rollout, regression, governance, or rollback decisions are still open.

File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

## Skill Ownership Model

| Skill | Primary mode or wrapper | When it wins |
| --- | --- | --- |
| `internal-gateway-operational-flow` | Skill-first staged workflow | Portable operational workflow core across runtimes. |
| `internal-agent-support-lane-change-engine` | Shared by operational wrappers | Stop-and-recommend when the selected mode no longer fits. |
| `internal-agent-support-next-step` | All operational wrappers | User-visible package for owner, scope, action, validation, and risk. |
| `internal-code-review` | `review` mode code lens | Tactical review engine for code defects, regressions, tests, and findings. |
| `internal-high-level-review` | `review` mode systems lens | Architecture, workflow, cross-cutting impact, operational fit, blind spots. |
| `internal-debugging` | `execute` or `review` support | Root-cause diagnosis for bugs, test failures, validator drift, sync failures. |
| `internal-tdd` | `execute` support | Red-green-refactor through public interfaces when an executable seam exists. |
| `internal-performance-optimization` | `execute` or `review` support | Measured latency, throughput, profiling, and regression-budget work. |
| `grill-me` | Gate 0 support for every non-`execute` entrypoint inside `define` | Question pressure after minimum evidence pass. Follow `references/gate-0-protocol.md`. |
| `internal-idea-define-advisor` | Conditional `define` support | Pre-action fit questions about tools, skills, agents, workflow, owners. |
| `superpowers-brainstorming` | Conditional `define` support | Creative or design-ambiguous work needs option exploration; skip for deterministic maintenance. |
| `internal-writing-plans` | `plan` mode | Retained repository-owned plan authoring under `tmp/superpowers/<clear-action-or-task-name>/`. |
| `internal-executing-plans` | `apply-plan` execution engine | Repository-owned plan application with `done-*` tracking under `tmp/superpowers/<clear-action-or-task-name>/`. |
| Runtime-specific internal skills | `execute` for local, `plan` when design dominates | Tactical delivery versus strategy split. |
| `superpowers-*` workflows | Conditional support | Mandatory only when the task shape actually triggers the workflow. |

Imported support and the future security lens are not gateway owners. Their approved use, compression guardrails, and promotion posture live in `wrapper-alignment.md`.

## Support Activation Rules

Use these rules when deciding whether a support skill belongs in `SKILL.md`, a reference, or the support skill itself.

| Material | Owner |
| --- | --- |
| Phase selection, `define` state, and completion evidence | `internal-gateway-operational-flow` `SKILL.md` |
| Gate 0 status, blocking semantics, closure, and realignment | `references/gate-0-protocol.md` |
| Support-skill trigger, boundary, and expected return shape | `internal-gateway-operational-flow` `SKILL.md` or this reference |
| Detailed support procedure, checklist, examples, scripts, and templates | The named support skill or its own references |
| Runtime wrapper wording, handoff labels, and imported-support posture | `references/wrapper-alignment.md` |
| Flow diagrams, scratchpad shapes, and host-runtime assembly maps | `references/workflow-maps.md` |

- Load `grill-me` when Gate 0 activates. Load `internal-agent-support-next-step` when a transition package is needed.
- Follow `references/gate-0-protocol.md` for Gate 0 depth, closure, and realignment.
- Load `internal-idea-define-advisor` inside `define` for pre-action fit questions.
- Load `superpowers-brainstorming` only when `define` needs option exploration; skip it for deterministic repository-owned maintenance.
- Load every other support skill only when the active phase, failure condition, handoff, review lens, or validation gap makes that owner necessary.
- Prefer delegating to the named skill over copying its method.
- When a support contract needs more than trigger, boundary, and return shape, move the detail to the support skill or bundle references instead of expanding `SKILL.md`.

## Mode Exit Rules

- `define` exits to `plan`, `review`, or critical challenge only through a Definition Brief, a Pre-Plan Critical Pass with `confident` outcome, visible next-step package, and checkpoint unless the user explicitly requested `define-first` only. When the Pre-Plan Critical Pass returns `reopen`, the workflow re-enters `define` with the critical findings before any exit. Use `gate-0-protocol.md` for transition authorization.
- `plan` exits to `execute`, `apply-plan`, `review`, or critical challenge only through a visible next-step package and checkpoint unless the user authorized end-to-end work.
- `execute` exits to `review` when correctness evidence or merge readiness is the main next need. Any non-complete stop must declare explicit `State`, `Continuation`, and a visible next-step package.
- `apply-plan` exits as `SHIPPED` only after all executable retained-plan items are completed and Check 4 verifies the physical close package. A real blocker or validation gap exits only with its explicit non-shipped state, `Continuation`, and visible next-step package. Only `SHIPPED` creates new `done-*` markers. Non-`SHIPPED` exits keep the live ledger and numbered files in place.
- `review` exits to `execute`, `define`, `plan`, critical challenge, or deferred follow-up for each actionable finding only after the Review Gate is satisfied.
- Critical challenge exits with `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`.
- Any mode may stop and recommend a better lane through `internal-agent-support-lane-change-engine` when the boundary breaks.

## Phase-Local Output Template

Use the active phase-local contract as the compact response frame for non-trivial `plan`, `execute`, or `apply-plan` work.

- Phase and entrypoint
- State
- Continuation
- User action required when `Continuation: waiting`
- Gate 0 status
- Definition Brief status when `define` applies
- Review Gate status when `review` applies
- Compact decision frame: target, anti-scope, and validation path
- Current slice or completed change
- Next checkpoint or next slice
- Next-step package when stopping without terminal completion
- Residual risk and `Lessons` line

Example:

```text
Phase: execute (`apply-plan`)
State: BLOCKED
Continuation: waiting
User action required: install the missing dependency, then approve the next apply step
Gate 0: satisfied (user closed the mandatory pre-start `grill-me` loop for this approved retained plan)
Definition Brief: satisfied (approved retained plan already defines target and anti-scope)
Decision frame: target = run sync plan after repository validation; anti-scope = no manual home copy; validation = sync plan, then sync audit
Current slice: repository-owned patch and focused validation completed; sync plan blocked on missing prerequisite.
Next-step package: Owner=internal-gateway-operational-flow; Scope=runtime sync branch; Action=resume from the blocked sync step; Validation=rerun sync plan then sync audit; Risk=manual closeout would misreport the retained-plan state.
Residual risk: medium (plan stays live until the external prerequisite is resolved).
Lessons: none retained.
```
