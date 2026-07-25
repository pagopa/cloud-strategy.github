---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs approved implementation plan writing from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

## Referenced skills

- `superpowers-writing-plans`: required owner after the repository preflight.

Thin repository wrapper for approved implementation-plan writing. This skill records the local handoff facts, delegates artifact decisions to `superpowers-writing-plans`, treats the delegated result as a draft until the local acceptance gate passes, and stops after reporting the accepted plan path.

## When to use

- Use after the user approves implementation-plan writing from an approved design or reviewed retained spec.

## When not to use

- Retained-spec writing stays in the brainstorming lane.
- Route same-chat work, ideation, plan review, execution, and imported `superpowers-*` maintenance to their existing owners.

## Contract

### Preflight Gate

Capture the preflight: `Target`, `Anti-scope`, `Nearest owner`,
`Validation path`, `Stop conditions`, and `Observable acceptance`.

Completion criterion: all six preflight facts are present and no fact is missing or explicitly recorded as a gap.

### Delegated Draft Gate

Load `superpowers-writing-plans` and let it create a plan, ask a blocking clarification, redirect, or stop with a reason. Pass an explicit anti-scope and the relevant owners already identified in the preflight so the delegated plan avoids duplicate or speculative tasks at the source. Pass an explicit delivery rule: the delegated plan must not contain `git add`, `git commit`, or `git push` steps or instructions, and must not present committing changes as the default next step unless the user explicitly asks for commit help. The delegated writing outcome persists as a draft-only artifact under `tmp/superpowers/plans/YYYY-MM-DD-HHMM-<feature-name>.md`.

Completion criterion: one delegated plan artifact exists under the timestamped plan path and is marked draft-only.

### Local Acceptance Gate

Delegated output remains draft-only until objective checks pass and human judgment checks pass. If either fails, revise the draft in place.

Objective checks: run `python3 scripts/validate_plan.py <retained-plan-path>`. A non-zero finding result keeps the artifact draft-only. Follow mechanical validation with human checks.

Human judgment checks: owner duplication, speculative scope, task responsibility, edit intent, validation quality, stop conditions, and handoff readiness.

Completion criterion: objective checks pass and human judgment checks pass.

### Writing Stop

After the local acceptance gate passes, name `internal-gateway-execute-plans` as the next owner. Stop after reporting the accepted plan path and wait for the user's next choice.

Completion criterion: accepted plan path is reported and `internal-gateway-execute-plans` is named as the next owner.

Preserve handoff quality with targeted rereads only when the delegation has a real evidence gap.

## No-Commit Rule

- The skill must never run `git add`, `git commit`, `git push`, or any other git mutation while creating, persisting, or handing off plans. Retained artifacts stay uncommitted under `tmp/superpowers/`; the user reviews and commits them personally.
- This rule is mandatory. The user may bypass it only with an explicit request for commit help in the current task; state the bypass in the outcome summary.
- The produced plan contains no Git mutation steps or default commit advice.

## Validation

- Confirm the delegated plan carries ordered tasks, concrete file targets, clear edit intent, validation commands or explicit gaps, no duplicate-owner or speculative-scope drift, and no direct commit instructions unless the user explicitly asked for commit help.
- Confirm no git mutation ran while producing the writing outcome and that retained artifacts remain uncommitted, unless the user explicitly asked for commit help.
- `git diff --check`
