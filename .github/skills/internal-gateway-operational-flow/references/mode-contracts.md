# Mode Contracts

Use this reference when the staged `plan`, `execute`, `apply-plan`, `review`, or critical boundary needs more detail than the main skill should carry.

## Staged Entrypoints

| Entrypoint | Owns | Must not own |
| --- | --- | --- |
| `full-cycle` | Non-trivial work that needs visible planning, optional critical challenge, checkpointed delivery, and final evidence. | Hidden wrapper-agent dispatch or unapproved execute/apply after planning. |
| `plan-only` | Decisions, retained plans, Decision Briefs, and stop-before-apply workflows. | Silent implementation after the plan is written. |
| `apply-plan` | Approved retained plan folders under `tmp/superpowers/<clear-action-or-task-name>/` using `internal-executing-plans`, folder-first execution, source-item ledger coverage, and explicit completion evidence. | Inline plans without normalization or checkpoint, newly discovered improvements, or `questions.md` execution. |
| `review` | Defect-first findings, evidence gaps, and fix routing. | Applying fixes or writing the initial design. |
| `mode-explicit` | Direct user requests for `plan`, `execute`, or `review`. | Overriding the user's explicit phase unless the lane no longer fits. |

## Mode Boundaries

| Mode | Owns | Does not own |
| --- | --- | --- |
| `plan` | Ambiguity resolution, decision records, retained plans, rollout shape, governance calls, and non-trivial repository-owned authoring. | Routine local execution once the target state is settled, defect-first validation, or pure pressure testing. |
| `execute` | Clear local implementation, deterministic realignment, nearby documentation/test updates, and concrete validation. | Strategic tradeoffs, unresolved ownership, non-trivial rollout decisions, review-first asks, or assumption challenge. |
| `apply-plan` | Repository-owned retained plan folder application with `done-*` tracking, source-item ledger coverage, blocker handling, cross-file continuation, and completion checks. | Creating or approving the plan, applying inline plans without checkpoint, silently expanding scope, or executing `questions.md`. |
| `review` | Findings, severity, confidence, causal layer, validation evidence, regression risk, systems risk, and fix routing. | Applying fixes, designing the initial solution, or open-ended challenge. |

If two modes still plausibly fit, choose `plan` and make the uncertainty explicit.

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
| `internal-gateway-operational-flow` | Skill-first staged workflow for `full-cycle`, `plan-only`, `apply-plan`, `review`, and explicit modes | Portable operational workflow core across Copilot, ChatGPT, Codex, and other runtimes. |
| `internal-gateway-critical-master` | Critical wrapper and pressure-test workflows | Challenge, pre-mortem, hidden assumptions, failure modes, and reframing. |
| `internal-agent-support-lane-change-engine` | Shared by operational wrappers and sync command centers | Stop-and-recommend protocol when the selected mode or lane no longer fits. |
| `internal-agent-support-next-step` | All operational wrappers | Shared user-visible package for already-selected owner, scope, action, validation, and risk. |
| `internal-code-review` | `review` mode code lens | Tactical review engine for code defects, regressions, tests, language anti-patterns, and file/line findings. |
| `internal-high-level-review` | `review` mode systems lens and codebase orientation support | Systems-level owner for architecture, workflow, cross-cutting impact, operational fit, blind spots, and unfamiliar-code maps. |
| `internal-debugging` | `execute` or `review` support | Root-cause diagnosis for bugs, test failures, build failures, validator drift, sync failures, and unexpected behavior. |
| `internal-tdd` | `execute` support | Repository-local TDD owner for red-green-refactor work through public interfaces when an executable seam exists. |
| `internal-performance-optimization` | `execute` or `review` support | Performance owner for measured latency, throughput, profiling, query-plan, and regression-budget work. |
| `grill-me` | Conditional Gate 0 support for `plan` and governance-sensitive pre-start delivery | User-requested or ambiguity-driven question pressure before plan finalization, phase transition, or action when user-only decisions still matter. |
| `internal-writing-plans` | `plan` mode | Retained repository-owned plan authoring under `tmp/superpowers/<clear-action-or-task-name>/`. |
| `internal-executing-plans` | `apply-plan` execution engine | Repository-owned plan application with `done-*` tracking and blocker stops under `tmp/superpowers/<clear-action-or-task-name>/`. |
| Runtime-specific internal skills | `execute` for local implementation, `plan` when design dominates | Tactical delivery versus strategy split. |
| `superpowers-*` workflows | Conditional support | Mandatory only when the task shape actually triggers the workflow. |

Imported support and the future security lens are not gateway owners. Their approved use, compression guardrails, and promotion posture live in `wrapper-alignment.md`.

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

- `plan` exits to `execute`, `apply-plan`, `review`, or critical challenge only through a visible next-step package and checkpoint unless the user authorized end-to-end work.
- `execute` exits to `review` when correctness evidence or merge readiness is the main next need.
- `apply-plan` exits only after all executable retained-plan items are completed, a real blocker is packaged, or validation exposes a gap that needs another visible owner.
- `review` exits to `execute`, `plan`, critical challenge, or deferred follow-up for each actionable finding.
- Critical challenge exits with `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`.
- Any mode may stop and recommend a better lane through `internal-agent-support-lane-change-engine` when the boundary breaks.
