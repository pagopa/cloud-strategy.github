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
- Do not use for quick same-chat tasks, substantive ideation, execution, or
  imported `superpowers-*` edits.

## Contract

1. Capture the preflight: `Target`, `Anti-scope`, `Nearest owner`,
   `Validation path`, `Stop conditions`, and `Observable acceptance`.
2. Load `superpowers-writing-plans` and let it create a plan, ask a blocking
   clarification, redirect, or stop with a reason. Pass an explicit anti-scope
   and the list of existing owners so the delegated plan avoids duplicate or
   speculative tasks at the source.
3. If a retained plan is created, verify execution-readiness and apply Plan
   Authoring Discipline: ordered tasks, concrete file targets, clear edit
   intent, validation commands or explicit gaps, stop conditions, and handoff
   readiness. Reject the draft if any task duplicates an existing owner, adds
   speculative scope, or lacks a validation path.
4. Stop after the writing outcome and wait for the user's next choice.

Preserve handoff quality with targeted rereads only when the delegation has a
real evidence gap.

## Plan Authoring Discipline

- Owner-first: before the delegated plan adds a task, confirm no existing
  owner, skill, or validator already covers that responsibility; prefer a
  reference over a duplicate.
- Single responsibility: each task must carry one clear deliverable tied to
  the approved target; split or merge tasks that don't.
- Fail-fast and redirect: if the delegated plan adds speculative scope,
  duplicates an existing owner, or lacks a validation path, send it back for
  revision instead of accepting it.

DRY, YAGNI, and TDD stay owned by `superpowers-writing-plans`; this section
adds only the owner-awareness and redirect gate that the delegated skill does
not enforce.
