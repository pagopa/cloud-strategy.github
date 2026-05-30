# Mode Contracts

Use this reference when the staged `define`, `plan`, `execute`, `apply-plan`, `review`, or critical boundary needs more detail than the main skill should carry.

## Staged Entrypoints

| Entrypoint | Owns | Must not own |
| --- | --- | --- |
| `full-cycle` | Non-trivial work that needs visible define, planning, Gate 0, critical challenge when the plan is non-trivial or governance-sensitive, checkpointed delivery, and final evidence. | Hidden wrapper-agent dispatch or unapproved execute/apply after planning. |
| `define-first` | Pre-plan clarification, brainstorming, `grill-me`, assumption surfacing, success criteria, option narrowing, and a Definition Brief. | Implementation planning, retained-plan authoring, or silent execution. |
| `plan-only` | Confirmed definition, decisions, retained plans, Decision Briefs, required critical challenge for non-trivial or governance-sensitive plans, and stop-before-apply workflows. | Silent implementation after the plan is written. |
| `apply-plan` | Approved retained plan folders under `tmp/superpowers/<clear-action-or-task-name>/` using `internal-executing-plans`, folder-first execution, source-item ledger coverage, and explicit completion evidence. | Inline plans without normalization or checkpoint, newly discovered improvements, or `questions.md` execution. |
| `review` | Defect-first findings, evidence gaps, and fix routing. | Applying fixes or writing the initial design. |
| `mode-explicit` | Direct user requests for `define`, `plan`, `execute`, or `review`. | Overriding the user's explicit phase unless the lane no longer fits. |

## Mode Boundaries

| Mode | Owns | Does not own |
| --- | --- | --- |
| `define` | Initial brainstorming, user intent, success criteria, constraints, anti-scope, option exploration, Gate 0 closure, and Definition Briefs. | Implementation plans, retained-plan authoring, local edits, or proof of completion. |
| `plan` | Ambiguity resolution after the definition is confirmed, decision records, retained plans, rollout shape, governance calls, and non-trivial repository-owned authoring. | Routine local execution once the target state is settled, defect-first validation, open-ended brainstorming, or pure pressure testing. |
| `execute` | Clear local implementation, deterministic realignment, nearby documentation/test updates, and concrete validation. | Strategic tradeoffs, unresolved ownership, non-trivial rollout decisions, review-first asks, or assumption challenge. |
| `apply-plan` | Repository-owned retained plan folder application with `done-*` tracking, source-item ledger coverage, blocker handling, cross-file continuation, and completion checks. | Creating or approving the plan, applying inline plans without checkpoint, silently expanding scope, or executing `questions.md`. |
| `review` | Findings, severity, confidence, causal layer, validation evidence, regression risk, systems risk, and fix routing. | Applying fixes, designing the initial solution, or open-ended challenge. |

If intent or success criteria are not confirmed, choose `define`. If two post-definition modes still plausibly fit, choose `plan` and make the uncertainty explicit.

## Medium-Task Thresholds

`execute` mode remains valid only when all of these are true:

- The desired outcome is already concrete.
- Verification is concrete enough to run locally or to name as an explicit gap.
- The work applies an already-decided contract rather than redesigning ownership, routing, or catalog boundaries.
- Adjacent file changes stay within one coherent maintenance area.
- For retained plans, the input is an approved `tmp/superpowers/<clear-action-or-task-name>/` folder and the remaining work is execution, not plan approval.

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
| `internal-gateway-operational-flow` | Skill-first staged workflow for `define`, `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit modes | Portable operational workflow core across Copilot, ChatGPT, Codex, and other runtimes. |
| `internal-gateway-critical-master` | Critical wrapper and pressure-test workflows | Challenge, pre-mortem, hidden assumptions, failure modes, and reframing. |
| `internal-agent-support-lane-change-engine` | Shared by operational wrappers and sync command centers | Stop-and-recommend protocol when the selected mode or lane no longer fits. |
| `internal-agent-support-next-step` | All operational wrappers | Shared user-visible package for already-selected owner, scope, action, validation, and risk. |
| `internal-code-review` | `review` mode code lens | Tactical review engine for code defects, regressions, tests, language anti-patterns, and file/line findings. |
| `internal-high-level-review` | `review` mode systems lens and codebase orientation support | Systems-level owner for architecture, workflow, cross-cutting impact, operational fit, blind spots, and unfamiliar-code maps. |
| `internal-debugging` | `execute` or `review` support | Root-cause diagnosis for bugs, test failures, build failures, validator drift, sync failures, and unexpected behavior. |
| `internal-tdd` | `execute` support | Repository-local TDD owner for red-green-refactor work through public interfaces when an executable seam exists. |
| `internal-performance-optimization` | `execute` or `review` support | Performance owner for measured latency, throughput, profiling, query-plan, and regression-budget work. |
| `grill-me` | Gate 0 support for every non-`execute` operational-flow entrypoint inside `define` | Question pressure after the minimum evidence pass and before plan output, recommendation, review output, phase transition, or retained-plan application. Follow `references/gate-0-protocol.md` for status, closure, blocking, and realignment. |
| `internal-idea-define-advisor` | Conditional `define` support | Pre-action fit questions about tools, skills, agents, workflow, owners, overkill, and simple-task suitability before planning or execution. |
| `superpowers-brainstorming` | Conditional `define` support | Creative, product, UX, architecture, or design-ambiguous work needs divergent and convergent option exploration before planning; skip it for deterministic prompt, skill, agent, instruction, or Markdown maintenance with a concrete target state. |
| `internal-writing-plans` | `plan` mode | Retained repository-owned plan authoring under `tmp/superpowers/<clear-action-or-task-name>/`, including the detailed critical-before-plan requirement for non-trivial retained plans. |
| `internal-executing-plans` | `apply-plan` execution engine | Repository-owned plan application with `done-*` tracking and blocker stops under `tmp/superpowers/<clear-action-or-task-name>/`. |
| Runtime-specific internal skills | `execute` for local implementation, `plan` when design dominates | Tactical delivery versus strategy split. |
| `superpowers-*` workflows | Conditional support | Mandatory only when the task shape actually triggers the workflow. |

Imported support and the future security lens are not gateway owners. Their approved use, compression guardrails, and promotion posture live in `wrapper-alignment.md`.

## Support Activation Rules

Use these rules when deciding whether a support skill belongs in `SKILL.md`, a
reference, or the support skill itself.

| Material | Owner |
| --- | --- |
| Phase selection, `define` state, and completion evidence | `internal-gateway-operational-flow` `SKILL.md` |
| Gate 0 status, blocking semantics, closure, and realignment | `references/gate-0-protocol.md` |
| Support-skill trigger, boundary, and expected return shape | `internal-gateway-operational-flow` `SKILL.md` or this reference |
| Detailed support procedure, checklist, examples, scripts, and templates | The named support skill or its own references |
| Runtime wrapper wording, handoff labels, and imported-support posture | `references/wrapper-alignment.md` |
| Flow diagrams, scratchpad shapes, and host-runtime assembly maps | `references/workflow-maps.md` |

- Preload `grill-me` and `internal-agent-support-next-step` at skill start.
- Follow `references/gate-0-protocol.md` for Gate 0 question depth, closure,
  and realignment. For mechanical work, keep the question set minimal but do
  not skip the gate.
- Load `internal-idea-define-advisor` inside `define` when the main question is pre-action fit for a tool, skill, agent, workflow, owner, or simple-task path rather than requirement discovery.
- Load `superpowers-brainstorming` only when `define` needs option exploration
  or design approval before planning; do not use it as mandatory support for
  deterministic repository-owned maintenance.
- Load every other support skill only when the active phase, failure condition,
  handoff, review lens, or validation gap makes that owner necessary.
- Prefer delegating to the named skill over copying its method. This gateway may
  state what the support owner must produce, but the support owner defines how.
- When a support contract needs more than trigger, boundary, and return shape,
  move the detail to the support skill or to this bundle's references instead
  of expanding `SKILL.md`.

## Retired To Current Ownership Mapping

| Retired or old owner | Current owner |
| --- | --- |
| `internal-agent-cross-lane-engine` | `internal-gateway-operational-flow` for plan/execute/review boundaries plus `internal-agent-support-lane-change-engine` for stop-and-recommend behavior. |
| `internal-ai-resource-creator` | `plan` mode through `internal-gateway-operational-flow` or direct skill use. |
| `internal-architect` | `plan` mode through `internal-gateway-operational-flow` or direct skill use. |
| `internal-planning-leader` | Deprecated compatibility wrapper; current owner is `internal-gateway-operational-flow`. |
| `internal-delivery-operator` | Deprecated compatibility wrapper; current owner is `internal-gateway-operational-flow` or `internal-gateway-simple-task` when the task is simple. |
| `internal-review-guard` | Deprecated compatibility wrapper; current owner is `internal-gateway-operational-flow` review mode. |
| `internal-critical-master` | Deprecated compatibility wrapper; current owner is `internal-gateway-critical-master`. |
| `internal-developer` | `execute` mode when target state is clear. |
| `internal-infrastructure` | `execute` for clear local changes, `plan` when design or rollout dominates. |
| `internal-cicd` | `execute` for deterministic changes, `plan` when orchestration or tradeoffs dominate. |
| `internal-quality-engineering` | `review` for validation and risk, `execute` for a clear local fix. |

## Mode Exit Rules

- `define` exits to `plan`, `review`, or critical challenge only through a
  Definition Brief, visible next-step package, and checkpoint unless the user
  explicitly requested `define-first` only. Use `gate-0-protocol.md` for
  `define-first`, brainstorming, and `idea-first` transition authorization.
- `plan` exits to `execute`, `apply-plan`, `review`, or critical challenge only through a visible next-step package and checkpoint unless the user authorized end-to-end work; non-trivial or governance-sensitive plans run the critical challenge before the plan is finalized.
- `execute` exits to `review` when correctness evidence or merge readiness is the main next need.
- `apply-plan` exits only after all executable retained-plan items are completed, a real blocker is packaged, or validation exposes a gap that needs another visible owner.
- `review` exits to `execute`, `define`, `plan`, critical challenge, or deferred follow-up for each actionable finding.
- Critical challenge exits with `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`.
- Any mode may stop and recommend a better lane through `internal-agent-support-lane-change-engine` when the boundary breaks.

## Phase-Local Output Template

Use the active phase-local contract as the compact response frame for non-trivial `plan`, `execute`, or `apply-plan` work.

- Phase and entrypoint
- Gate 0 status
- Definition Brief status when `define` applies
- Critical challenge status when non-trivial or governance-sensitive planning applies
- Compact decision frame: target, anti-scope, and validation path
- Current slice or completed change
- Next checkpoint or next slice
- Residual risk and `Lessons` line

Example:

```text
Phase: execute (`apply-plan`)
Gate 0: satisfied (user closed the mandatory `grill-me` loop for this request)
Definition Brief: satisfied (approved retained plan already defines target and anti-scope)
Decision frame: target = move stale module under deprecated/; anti-scope = no functional change; validation = pytest tests/test_module_paths.py
Current slice: moved 3 files and updated 2 imports.
Next checkpoint: rerun targeted pytest, then ask before the next slice.
Residual risk: low (no external consumers).
Lessons: none retained.
```
