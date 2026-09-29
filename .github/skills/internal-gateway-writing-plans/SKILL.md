---
name: internal-gateway-writing-plans
description: Use when an approved design, reviewed spec, or direct requirement needs one retained implementation plan.
---

# Internal Gateway Writing Plans

This is the repository wrapper around `/addyosmani-planning-and-task-breakdown`.
The planner owns decomposition, checkpoints, template, task quality, and
planning self-review. This gateway owns source readiness, destination,
authority, repository deltas, and the explicit execution boundary.

## When to use

- An explicit `+plan` selection arrives from `/internal-gateway-idea`.
- The user explicitly requests a plan from an approved design, reviewed spec,
  concrete direct requirements, or a legacy plan for re-authoring.
- Do not use it for early analysis, one-session implementation, or execution.

## Eligibility

Require an explicit plan request, a source, known target and anti-scope, and
exact authority for every selected planner output. A verified idea spec with
`plan_authoring_ready: true` satisfies readiness without another discovery
round. Recheck its reference against the active source: bind and recheck an
exposed content identity/version; otherwise compare observable accepted content
with the active unit and decision IDs, recording no invented identity or hash.
Changed, unavailable, or uncomparable content blocks until reverified.
`implementation_permission: false` never grants implementation or execution.

## Planner handoff

Before authoring, preflight the planner's complete output set. Pass an explicit
approved destination override for every selected output: the retained plan and,
if selected, default `tasks/plan.md` and `tasks/todo.md` outputs. Planner
defaults are not authority; do not grant multiple artifacts automatically.
Pass one bounded context to `/addyosmani-planning-and-task-breakdown` with
accepted decisions, labeled evidence, verified source comparison, exact
target contracts (target(s), criteria, dependencies, verification, and human
checkpoints), anti-scope, repository deltas, and authorized paths/actions. Let
the planner own breakdown, template, checkpoints, task quality, and self-review.

Use the approved destination, often under `tmp/superpowers/plans/`; never
silently accept or write a default. The returned result must identify that
exact plan path and every actual task target, with each target's criteria,
dependencies, verification, and human checkpoints. Verify the returned outputs
against the approved set; unresolved target or output references block before
authoring. Do not duplicate task copies or infer tasks from the spec.
Applicable `/internal-tdd` posture remains authoritative.

## Legacy and boundaries

A retained plan containing a legacy `## Execution Manifest` is read-only
conversion input. Leave it unchanged and write a new plan only after an
explicit re-authoring request; its manifest, permissions, and obsolete
workflow text have no authority. A missing producer or unresolved dependency
stays unresolved; never invent a path or claim readiness.

The writer performs no implementation, Git mutation, commit, branch, worktree,
runtime ledger or status creation, or automatic execution. It preserves user
work and does not expand the supplied authority envelope. Protected imported
bundles remain read-only. A plan result is not execution permission. Route only
explicit approval to `/internal-gateway-execute-plans`.
