---
name: internal-gateway-writing-plans
description: Use when an approved design, reviewed spec, or direct requirement needs one retained implementation plan.
---

# Internal Gateway Writing Plans

This gateway wraps `/addyosmani-planning-and-task-breakdown`. The planner owns
decomposition, task quality, and self-review. This gateway owns readiness,
single-plan output, task authority, automatic checkpoints, and the execution
boundary.

## When to use

- An explicit `+plan` selection arrives from `/internal-gateway-idea`.
- The user explicitly requests a plan from an approved design, reviewed spec,
  concrete direct requirements, or a legacy plan for re-authoring.
- Do not use it for early analysis, one-session implementation, or execution.

## Eligibility

Require an explicit plan request, a source, and known target and anti-scope.
That request authorizes the single-plan destination below without another
filename approval. Extra artifacts require an explicit user request.
A verified idea spec with
`plan_authoring_ready: true` satisfies readiness without another discovery
round. Recheck its reference against the active source: bind and recheck an
exposed content identity/version; otherwise compare observable accepted content
with the active unit and decision IDs, recording no invented identity or hash.
Changed, unavailable, or uncomparable content blocks until reverified.
`implementation_permission: false` never grants implementation or execution.

## Planner handoff

Create every new implementation plan at
`tmp/.plans/YYYY-MM-DD-HHMM-<topic>.md`, using the creation date/time and a
dash-case topic. Keep any explicitly requested alternative filename under
`tmp/.plans/`. Never migrate existing plans automatically. If a destination
contains different work, choose a distinct topic suffix without overwriting
it. Update the identified plan in place only on an explicit replanning request.

Pass one bounded context to `/addyosmani-planning-and-task-breakdown`: accepted
decisions, labeled evidence, verified source comparison, target and anti-scope,
repository deltas, and the exact single output path. Explicitly override the
planner's separate plan/todo outputs and implicit tracker selection. Produce
one Markdown file with overview, decisions, risks, detailed tasks, and progress.
Create tracker items or another task list only when the user explicitly asks;
do not duplicate task contracts across artifacts. A default tracker configured
by the repository is not a request to create tickets for this plan.

Every task must declare a stable ID, acceptance criteria, dependencies, exact
authorized writable paths, and concrete runnable verification. An estimated
`Files likely touched` list is not write authority. Preserve protected and
read-only paths unless the user explicitly authorized that exact change.
Applicable `/internal-tdd` posture remains authoritative. Check that validation
tools and commands exist; unresolved references block rather than being guessed.

Put the checklist and concise verification/blocker evidence in one `Progress`
section, keyed by stable task ID. Only that section may change during execution
without changing approval. The executor may update progress but may not hide
new criteria, dependencies, checks, or writable scope inside state notes.

Checkpoints are automatic checks, not confirmation prompts. Preserve a human
gate only when the user explicitly selected it. Plan one whole-plan final review
after task checks; no routine per-task full reviews or execution-method choice.
The review compares execution start and end state, not only committed changes.

Self-review the plan for coverage, authority, dependencies, concrete checks, and
proportion. Return its exact path, actual task IDs and scope, and any unresolved
decision. All stable contracts must be readable from the one plan. Do not create
default `tasks/` outputs, status siblings, or parallel runtime records. This
single-plan output does not promise compatibility with external `/build` tooling.

## Legacy and boundaries

A retained plan containing a legacy `## Execution Manifest` is read-only
conversion input. Leave it unchanged and write a new plan only after an
explicit re-authoring request; its manifest, permissions, and obsolete
workflow text have no authority. A missing producer or unresolved dependency
stays unresolved; never invent a path or claim readiness.

The writer performs no implementation, Git mutation, commit, branch, worktree,
runtime ledger or automatic execution. It preserves user work and does not
expand the authority envelope. Protected imported bundles remain read-only.
A plan result is not execution permission. The user's invocation of
`/internal-gateway-execute-plans` authorizes the identified plan, without a
second confirmation; an internal call or readiness flag never creates approval.
