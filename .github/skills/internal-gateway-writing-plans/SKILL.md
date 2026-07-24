---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs a short preflight before delegating retained writing to superpowers-writing-plans.
---

# Internal Gateway Writing Plans

## Referenced skills

- `superpowers-writing-plans`: required owner after the repository preflight.

Thin repository wrapper for retained writing. This skill records the local
handoff facts, delegates artifact decisions to `superpowers-writing-plans`, and
stops after the delegated outcome.

## When to use

- Use after the user approves retained spec or implementation-plan writing.

## When not to use

- Do not use for quick same-chat tasks, substantive ideation, execution, or
  imported `superpowers-*` edits.

## Contract

1. Capture the preflight: `Target`, `Anti-scope`, `Nearest owner`,
   `Validation path`, `Stop conditions`, and `Observable acceptance`.
2. Load `superpowers-writing-plans` and let it create a plan, ask a blocking
   clarification, redirect, or stop with a reason. Pass an explicit anti-scope
   and the relevant owners already identified in the preflight so the delegated
   plan avoids duplicate or speculative tasks at the source. Pass an explicit
   delivery rule: the delegated plan must not contain `git add`, `git commit`,
   or `git push` steps or instructions, and must not present committing
   changes as the default next step unless the user explicitly asks for
   commit help. If the
   delegated writing outcome persists a retained artifact, require timestamped local
   naming with four-digit 24-hour time: plans use
   `tmp/superpowers/plans/YYYY-MM-DD-HHMM-<feature-name>.md` and specs use
   `tmp/superpowers/specs/YYYY-MM-DD-HHMM-<topic>-design.md` such as
   `2026-07-03-1143-<name>`.
3. If a retained plan is created, verify execution-readiness and apply Plan
   Authoring Discipline: ordered tasks, concrete file targets, clear edit
   intent, validation commands or explicit gaps, stop conditions, and handoff
   readiness. Reject the draft if any task duplicates an existing owner, adds
   speculative scope, includes direct commit instructions without explicit
   user approval, or lacks validation commands or an explicit validation gap.
4. Stop after the writing outcome and wait for the user's next choice.

Preserve handoff quality with targeted rereads only when the delegation has a
real evidence gap.

## No-Commit Rule

- The skill must never run `git add`, `git commit`, `git push`, or any other
  git mutation while creating, persisting, or handing off plans or specs.
  Retained artifacts stay uncommitted under `tmp/superpowers/`; the user
  reviews and commits them personally.
- This rule is mandatory. The user may bypass it only with an explicit
  request for commit help in the current task; state the bypass in the
  outcome summary.
- Keep this rule distinct from the Contract delivery rule: this rule governs
  the skill's own git actions, while the delivery rule governs plan content.

## Plan Authoring Discipline

- Owner-first: before the delegated plan adds a task, confirm no existing
  owner, skill, or validator already covers that responsibility; prefer a
  reference over a duplicate.
- Single responsibility: each task must carry one clear deliverable tied to
  the approved target; split or merge tasks that don't.
- Fail-fast and redirect: if the delegated plan adds speculative scope,
  duplicates an existing owner, includes direct `git add`/`git commit`/`git push`
  instructions without explicit user approval, or lacks validation commands or
  an explicit validation gap, send it back for revision instead of accepting it.

DRY, YAGNI, and TDD stay owned by `superpowers-writing-plans`; this section
adds only the owner-awareness and redirect gate that the delegated skill does
not enforce.

## Validation

- Confirm the delegated plan carries ordered tasks, concrete file targets, clear edit intent, validation commands or explicit gaps, no duplicate-owner or speculative-scope drift, and no direct commit instructions unless the user explicitly asked for commit help.
- Confirm no git mutation ran while producing the writing outcome and that retained artifacts remain uncommitted, unless the user explicitly asked for commit help.
- `git diff --check`
