---
name: internal-agent-operating-model-engine
description: Share the canonical boundary model, recommendation protocol, medium-task thresholds, OBRA workflow policy, skill ownership rules, and anti-overlap checks for the repository-owned operational agents. Use when `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, or `internal-critical-challenger` need the same operating model.
---

# Internal Agent Operating Model Engine

Use this skill as the shared engine for the four canonical operational agents.

This skill is intentionally shared. It owns the reusable rules that would otherwise drift across `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-challenger`. It is not a copy of the agents.

## Shared Core Rule

Check relevant OBRA skills before starting any task. If a workflow is relevant, it is mandatory, not optional. Do not preload irrelevant workflows.

Implications:

- Apply OBRA only when the task shape actually triggers the workflow.
- Keep small tasks small.
- Do not skip a relevant OBRA workflow just because the agent already knows what to do.

## Boundary Model

| Canonical owner | Owns | Does not own |
| --- | --- | --- |
| `internal-fast-executor` | Clear, local execution with concrete verification and limited risk | Strategic tradeoffs, ambiguous scope, broad authoring, review-first asks, or critical challenge |
| `internal-planning-leader` | Ambiguity resolution, decision records, plans, repository-owned authoring, rollout and governance decisions | Default local execution once the design is settled, defect-first review, or pure challenge |
| `internal-review-guard` | Review, validation, merge readiness, regression risk, evidence gaps, and defect-first findings | Implementation, initial design ownership, or open-ended strategic challenge |
| `internal-critical-challenger` | Pre-mortems, assumption stress tests, failure modes, and strong objections | Implementation, routine technical review, or final operational planning |

## Medium-Task Thresholds

`internal-fast-executor` stays owner only when all of these are true:

- The likely change touches `<= 2` files.
- The work stays within one directory family or one logical boundary.
- Routing, ownership, naming contracts, and catalog boundaries stay unchanged.
- The task does not require a real strategic comparison.

`internal-planning-leader` becomes owner when at least one of these is true:

- The change touches `>= 3` files with lateral impact.
- The change crosses more than one directory family or logical boundary.
- The change affects routing, ownership, naming contracts, or catalog boundaries.
- There are `>= 2` credible solution paths with non-trivial tradeoffs.
- The task needs rollout, regression, governance, or rollback decisions.
- The task creates a new repository-owned resource instead of a banal update to an existing one.

## Boundary Recommendation Protocol

Only `internal-router` actively routes between owners. The four canonical owners stay inside their boundary, tell the user when that boundary no longer holds, and recommend the better owner instead of delegating.

| Agent | Stay owner when | Boundary breaks when | Recommend |
| --- | --- | --- | --- |
| `internal-fast-executor` | The task is clear, local, low-risk, and concretely verifiable. | Medium-task thresholds, non-obvious tradeoffs, or routing and ownership changes appear. | `internal-planning-leader` |
| `internal-planning-leader` | Ambiguity, cross-boundary tradeoffs, repository-owned authoring, or rollout decisions still need active ownership. | The design is settled and the next step is routine local execution. | `internal-fast-executor` |
| `internal-review-guard` | The task is defect-first review, merge readiness, regression analysis, or evidence gathering. | Findings reveal missing design or weak boundaries. | `internal-planning-leader` |
| `internal-review-guard` | The task is still review-owned but weak reasoning becomes the dominant gap. | Pressure-testing the reasoning matters more than technical review. | `internal-critical-challenger` |
| `internal-critical-challenger` | The task is assumption testing, a pre-mortem, or failure-mode analysis. | The framing or plan must be reformulated. | `internal-planning-leader` |
| `internal-critical-challenger` | The task remains challenge-owned until the reasoning survives scrutiny. | Evidence-based validation becomes the next need. | `internal-review-guard` |

Recommendation should name the reason, not only the suggested owner, and the user decides whether to switch.

## Mandatory Engine vs Optional Support

Use this policy across all canonical agents:

- `## Mandatory Engine Skills` lists only the skill or skills required before the agent can operate correctly.
- `## Optional Support Skills` lists conditional helpers, tactical specialists, or OBRA workflows that matter only for some tasks.
- Do not place required engines inside the optional list.
- Do not create 1:1 decorative engine skills for symmetry alone.
- A shared engine is preferable when the same reusable rules would otherwise drift across multiple agents.

## Skill Ownership Model

| Skill | Primary owner | When it wins |
| --- | --- | --- |
| `internal-agent-routing-engine` | `internal-router` | Front-door classification and dispatch |
| `internal-agent-operating-model-engine` | Shared by the four canonical agents | Shared boundary, recommendation, and anti-overlap logic |
| `internal-code-review` | `internal-review-guard` | Tactical review engine for findings and defect-first analysis |
| `internal-agent-development` | `internal-planning-leader` | Non-trivial repository-owned agent authoring |
| `internal-agents-md-bridge` | `internal-planning-leader` | Root bridge changes and AGENTS alignment |
| `internal-copilot-audit` | `internal-planning-leader` | Catalog audit, drift analysis, and stale-reference review |
| `internal-copilot-docs-research` | `internal-planning-leader` | Contract questions that depend on current GitHub Copilot or MCP behavior |
| `internal-pair-architect` | `internal-planning-leader` | Change-impact and architecture-risk analysis |
| `internal-terraform`, `internal-cicd-workflow`, and runtime-specific internal skills | `internal-fast-executor` for local execution, `internal-planning-leader` when design or rollout dominates | Tactical delivery versus strategy split |
| `obra-*` workflows | Cross-agent support | Mandatory when relevant, absent when irrelevant |

## Relationship Model

- `internal-router` owns the front door only. It does not implement, plan, review, or challenge by itself.
- `internal-planning-leader` absorbs the role previously covered by `internal-ai-resource-creator` when the work is non-trivial repository-owned authoring.
- `internal-review-guard` must reuse `internal-code-review` instead of restating the review playbook in the agent body.
- `internal-fast-executor` should stay light and load runtime or domain skills only when the task already belongs to execution.
- `internal-critical-challenger` should stay narrow: challenge the reasoning, synthesize the pressure test, and tell the user when planning should resume.
- `internal-sync-*` and `awesome-*` assets stay outside this canonical operational model.

## Retired To Canonical Ownership Mapping

| Retired owner | Canonical owner |
| --- | --- |
| `internal-ai-resource-creator` | `internal-planning-leader` |
| `internal-architect` | `internal-planning-leader` |
| `internal-developer` | `internal-fast-executor` |
| `internal-infrastructure` | `internal-fast-executor` or `internal-planning-leader` when design or rollout dominates |
| `internal-cicd` | `internal-fast-executor` or `internal-planning-leader` when orchestration or tradeoffs dominate |
| `internal-code-review` | `internal-review-guard` |
| `internal-quality-engineering` | `internal-review-guard` for validation and risk, `internal-fast-executor` for a clear fix |
| `internal-aws-*`, `internal-azure-*`, `internal-gcp-*` | `internal-planning-leader` for strategy or design, `internal-fast-executor` for clear local execution |

## Anti-Overlap Checklist

Before finalizing any operational routing or agent edit, check these questions:

- Is the request primarily execution, planning, review, or challenge?
- Would the same request cause two canonical agents to claim ownership?
- Is a required engine hiding inside `## Optional Support Skills`?
- Is a new skill being created only for symmetry instead of real shared logic?
- Is the agent body repeating logic that belongs in a shared skill?
- Is an imported or sync-only asset being treated as a canonical operational owner?
- Would a power user know when to pick this agent directly without reading three files?

If any answer points to overlap, narrow the agent or move the shared logic into a skill.

## Common Mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Letting `internal-fast-executor` keep medium tasks by momentum | Execution becomes accidental planning | Tell the user the boundary broke and recommend `internal-planning-leader` on the first medium-task threshold hit |
| Letting `internal-planning-leader` execute by default | The planner becomes a catch-all generalist | Tell the user when the design is settled and recommend `internal-fast-executor` |
| Rewriting the review playbook inside `internal-review-guard` | Review logic drifts from the tactical skill | Reuse `internal-code-review` as the mandatory tactical engine |
| Treating challenge as generic negativity | The agent stops producing useful decision pressure | Keep one challenge thread, then synthesize clear failure modes |
| Creating one dedicated engine skill per agent for symmetry | The catalog grows without adding real structure | Use shared engines or existing skills unless a real gap exists |

## Output Expectations

- Current owner and boundary rationale
- Whether the boundary still holds and why
- Which OBRA workflows are relevant for this task
- Which tactical internal skill should be loaded next, if any
