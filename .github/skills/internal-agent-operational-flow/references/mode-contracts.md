# Mode Contracts

Use this reference when the `plan`, `execute`, or `review` boundary needs more detail than the main skill should carry.

## Mode Boundaries

| Mode | Owns | Does not own |
| --- | --- | --- |
| `plan` | Ambiguity resolution, decision records, retained plans, rollout shape, governance calls, and non-trivial repository-owned authoring. | Routine local execution once the target state is settled, defect-first validation, or pure pressure testing. |
| `execute` | Clear local implementation, deterministic realignment, nearby documentation/test updates, and concrete validation. | Strategic tradeoffs, unresolved ownership, non-trivial rollout decisions, review-first asks, or assumption challenge. |
| `review` | Findings, severity, confidence, causal layer, validation evidence, regression risk, and fix routing. | Applying fixes, designing the initial solution, or open-ended challenge. |

If two modes still plausibly fit, choose `plan` and make the uncertainty explicit.

## Medium-Task Thresholds

`execute` mode remains valid only when all of these are true:

- The desired outcome is already concrete.
- Verification is concrete enough to run locally or to name as an explicit gap.
- The work applies an already-decided contract rather than redesigning ownership, routing, or catalog boundaries.
- Adjacent file changes stay within one coherent maintenance area.

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
| `internal-agent-operational-flow` | Shared by `plan`, `execute`, and `review` | Portable operational workflow core across Copilot, ChatGPT, Codex, and other runtimes. |
| `internal-agent-critical-master` | Critical wrapper and pressure-test workflows | Challenge, pre-mortem, hidden assumptions, failure modes, and reframing. |
| `internal-agent-support-lane-change-engine` | Shared by operational wrappers and sync command centers | Stop-and-recommend protocol when the selected mode or lane no longer fits. |
| `internal-agent-support-next-step` | All operational wrappers | Shared user-visible package for already-selected owner, scope, action, validation, and risk. |
| `internal-code-review` | `review` mode | Tactical review engine for defect-first findings and code or catalog review. |
| `mattpocock-grill-me` | Conditional support for `plan` mode | User-requested or ambiguity-driven question pressure before plan finalization. |
| `internal-writing-plans` | `plan` mode | Retained repository-owned plan authoring under `tmp/superpowers/<clear-action-or-task-name>/`. |
| `internal-executing-plans` | `plan` mode oversight | Repository-owned plan application with `done-*` tracking and blocker stops. |
| Runtime-specific internal skills | `execute` for local implementation, `plan` when design dominates | Tactical delivery versus strategy split. |
| `obra-*` workflows | Conditional support | Mandatory only when the task shape actually triggers the workflow. |

## Retired To Current Ownership Mapping

| Retired or old owner | Current owner |
| --- | --- |
| `internal-agent-cross-lane-engine` | `internal-agent-operational-flow` for plan/execute/review boundaries plus `internal-agent-support-lane-change-engine` for stop-and-recommend behavior. |
| `internal-ai-resource-creator` | `plan` mode through `internal-planning-leader` or direct skill use. |
| `internal-architect` | `plan` mode through `internal-planning-leader` or direct skill use. |
| `internal-developer` | `execute` mode when target state is clear. |
| `internal-infrastructure` | `execute` for clear local changes, `plan` when design or rollout dominates. |
| `internal-cicd` | `execute` for deterministic changes, `plan` when orchestration or tradeoffs dominate. |
| `internal-quality-engineering` | `review` for validation and risk, `execute` for a clear local fix. |

## Mode Exit Rules

- `plan` exits to `execute`, `review`, or critical challenge only through a visible next-step package.
- `execute` exits to `review` when correctness evidence or merge readiness is the main next need.
- `review` exits to `execute`, `plan`, critical challenge, or deferred follow-up for each actionable finding.
- Any mode may stop and recommend a better lane through `internal-agent-support-lane-change-engine` when the boundary breaks.
