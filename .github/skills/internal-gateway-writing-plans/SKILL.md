---
name: internal-gateway-writing-plans
description: Use when the user explicitly requests one retained implementation plan from an approved design, reviewed spec, concrete requirements, or a legacy plan to re-author. Route one-session work to /internal-gateway-simple-task.
---

# Internal Gateway Writing Plans

Write one practical plan through `/addyosmani-planning-and-task-breakdown`.
The planner owns task breakdown and quality. This gateway owns the output,
scope, checks, and boundary between planning and execution.

## When to use

- An explicit `+plan` selection arrives from `/internal-gateway-idea`.
- The user explicitly requests a plan from an approved design, reviewed spec,
  concrete direct requirements, or a legacy plan for re-authoring.
- Do not use it for early analysis, one-session implementation, or execution.

## Eligibility

Require a plan request, readable source, target, and anti-scope. A verified
idea spec with `plan_authoring_ready: true` needs no new discovery round.
Compare the source with accepted requirements, using its version when available.
Resolve missing content or material differences; state where the user's latest
explicit requirements supersede the source. Readiness and
`implementation_permission: false` grant no implementation authority.

## Planner handoff

The request authorizes one plan at `tmp/.plans/YYYY-MM-DD-HHMM-<topic>.md`,
using creation time and a dash-case topic. Keep requested alternative filenames
under `tmp/.plans/`. Preserve existing plans: use a distinct suffix on collision,
and update a plan in place only on explicit replanning. Do not migrate plans.

Pass the accepted requirements, relevant local evidence, target, anti-scope,
and exact output path to `/addyosmani-planning-and-task-breakdown`. Override
its separate plan/todo outputs and Git defaults: use the current branch and
HEAD for comparisons; require no branch, worktree, staging, commit, or stash.
Produce one Markdown file with overview, risks, detailed tasks, and `Progress`.
Create tracker items or another task list only on explicit request.

Each task declares ID, acceptance criteria, dependencies, exact writable paths,
and concrete verification. `Files likely touched` is not authority; protected
paths require explicit authorization. Apply `/internal-tdd` where relevant.
Check local files, dependencies, and validation commands without implementing
tasks or proving advance success. A supported setup step may be a prerequisite
task with its own scope and check.

Skill evaluations, including writer-to-executor trials, are optional unless
the user explicitly requires them. Do not require a runtime, judge, pilot, or
evaluation baseline merely to write a plan. Use available structural checks
and review for skill edits; label unperformed behavioral evaluation `not-run`.
If an explicit mandatory check has no usable path, name the missing capability
and resolve that requirement before promising the check. Do not invent a
runner, silently waive the check, or equate structural validation with behavior.

Keep checkboxes and concise check/blocker evidence in `Progress`, keyed by task
ID. Only progress may change without changing approval; it must not hide new
criteria, dependencies, checks, or writable scope. Checkpoints are automatic
unless the user selected a human gate. Include task checks and one final review
of execution changes, including uncommitted work.

Review coverage, scope, dependencies, and checks. Return the plan path, task IDs,
and material limitations. A plan describes intended work; it does not guarantee
successful execution. Keep all task contracts and progress in that one file.

## Legacy and boundaries

Legacy `## Execution Manifest` plans remain read-only conversion input. Write
a new plan only on explicit re-authoring; inherit no legacy authority. Name
missing sources or dependencies without inventing paths or claiming readiness.

Writing does not implement or execute the plan, mutate Git, or create runtime
state. Preserve user work and protected bundles. A user request to execute the
identified plan routes to `/internal-gateway-execute-plans` without another
confirmation; producing a plan or internally calling a skill grants no such
authority.
