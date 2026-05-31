---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be answered, edited, diagnosed, or validated quickly without a retained plan, review mode, critical challenge, or staged workflow.
---

# Internal Gateway Simple Task

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to. It is an owner index, not a preload bundle.

- `grill-me`: one focused clarification block for simple blockers.
- `internal-gateway-operational-flow`: staged owner when simple work no longer fits.
- `internal-gateway-critical-master`: critical owner when assumptions or failure modes dominate.
- `internal-lesson-codification`: lesson owner for a durable lesson candidate.
- `internal-debugging`: root-cause owner before fixed-claim language.
- `internal-tdd`: test-first owner before coverage or red-green-refactor claims.
- `internal-performance-optimization`: measured-performance owner before improvement claims.
- `internal-github-pr`: PR lifecycle owner before PR readiness or completion claims.
- `internal-code-review`: defect-first owner before no-code-finding or merge-readiness claims.
- `internal-high-level-review`: systems owner before no-systems-finding or systems-readiness claims.
- `superpowers-verification-before-completion`: final evidence gate before completion, readiness, or no-findings claims.

Use this skill as the skill-first fast path for concrete repository-owned work.
It is single-lane and single-phase by design. It keeps small and medium tasks light. It is not a hidden router, retained-plan engine, or operational-skill catalog.

## When to use

- The outcome, target, command, or validation path is already concrete.
- The work applies an already-decided contract and does not redesign ownership,
  routing, naming, rollout, or governance.
- One quick lane can finish: `answer`, `edit`, `diagnose`, `validate`, or
  `escalate`.
- Repeated low-risk edits may stay simple only when they apply the same already-decided pattern and share one validation path.
- Support selection follows the request, target path, command surface, local
  evidence, validation signal, or an explicit skill call.
- A heavier gateway de-escalates because only a clear answer, local edit,
  diagnosis, or deterministic validation remains.

## When not to use

- Ownership, target shape, rollout, governance, validation, or cross-boundary
  tradeoffs still need a decision. Stop and recommend
  `internal-gateway-operational-flow`.
- The request is `plan`, `execute`, `review`, `full-cycle`, `plan-only`,
  `apply-plan`, retained-plan execution, or merge-readiness review. Stop and
  recommend `internal-gateway-operational-flow`.
- The user asks to create, rewrite, or clarify context before a plan. Stop and
  recommend `internal-gateway-operational-flow` so its pre-plan `grill-me`
  gate can run.
- The primary request is pressure testing, pre-mortem analysis, hidden
  assumptions, or failure modes. Stop and recommend
  `internal-gateway-critical-master`.
- The task is catalog sync governance or consumer propagation. Use the repo-only
  sync owner instead of this fast path.

## Escalation Triggers

Leave simple mode when one of these becomes the real problem:

- The change redesigns ownership, routing, catalog boundaries,
  frontmatter contracts, sync behavior, or precedence.
- The work touches `AGENTS.md`, `.github/copilot-instructions.md`,
  `.github/INVENTORY.md`, validators, sync engines, retained-plan engines, or
  gateway contracts in a non-mechanical way.
- Token-risk, sync drift, or validator drift becomes the main issue instead of
  a final check.
- The edit expands into adjacent changes that need a design, rollback, rollout,
  or regression decision.
- Missing information could change scope, owner, target state, validation,
  rollout, or anti-scope before any plan output.
- A durable lesson candidate appears. Report it in chat or hand it to
  `internal-lesson-codification`; do not update `LESSONS_LEARNED.md` inside
  simple mode.

## Simple Flow

Use at most one focused block of clarification. `references/clarification-gate.md`
owns the exit check, single-clarification limit, and escalation triggers for
simple mode.

1. Inspect local files first when repository evidence can answer the question.
2. Run the exit check in `references/clarification-gate.md` before using
   `grill-me`.
3. If missing context still blocks the start and local evidence cannot resolve
   it, use `grill-me` only within that reference boundary.
4. Confirm the task still fits one quick lane.
5. Load only the support skill proved by the prompt, target path, command
  surface, symptom, domain evidence, or validation surface.
6. Answer, edit, diagnose, or validate without creating a retained plan.
7. Run focused validation, or name the explicit validation gap.
8. If the task stops being simple, stop and issue an escalation alert.

Keep the first read budget small: one target or owner file, one likely domain skill when applicable, and one nearby validator or test found with `rg`. Open tests only when exact assertions, fixtures, or failure output can change the lane.
Bundle-target maintenance does not stop at the first file. For a repository-owned skill or similar bundle owner, inspect relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`, or mark them as intentional non-action before closure.

## Quick Lanes

Use one quick lane: `answer`, `edit`, `diagnose`, `validate`, or `escalate`.
`references/simple-lanes.md` is the single source of truth for lane selection
and output shapes after the fast-path boundary is confirmed.

## Support Selection

Do not maintain a finite list of operational skills here. Select support by evidence:

- explicit user-selected skill or domain
- file type, path family, runtime, command surface, or schema signal
- file type, runtime, framework, or command surface
- reproduced failure loop or validation signal
- cloud, provider, platform, or governance evidence in the prompt or files

If the prompt mentions a domain that is not represented by a known support
skill, inspect repository evidence and use the closest valid owner. Do not infer
that an unlisted provider, tool, or runtime is unsupported.

Use `references/clarification-gate.md` for clarification boundaries. Use
`references/support-routing.md` only when several plausible support owners
compete. Use `scripts/suggest_support_skills.py` only as an advisory helper for
known paths or symptoms.

## grill-me boundary

`references/clarification-gate.md` is the canonical simple-mode boundary for
the exit check, `grill-me` limit, and escalation triggers.

## Claim Gates

`references/support-routing.md` is the single source of truth for claim-gate
owners and evidence gates in simple mode. Keep claim gates narrow and load them
only before the matching status claim.

## Escalation Alert

When this skill stops fitting, do not write a mini-plan. Return a short alert
with:

- boundary break
- recommended next owner
- scope to carry forward
- next action
- validation path
- main risk

## Output Shape

`references/simple-lanes.md` is the single source of truth for lane-specific
output shapes. For escalation, return only the escalation alert fields.

## Validation

- Work stayed single-lane and single-phase, or escalation was explicit.
- The target state was concrete enough for a quick lane.
- Support selection came from evidence, not a broad bundle or partial catalog.
- Bundle-target work reviewed the owning file plus relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`, or marked them as intentional non-action before closure.
- `grill-me`, when used, asked only for the minimum context needed and stayed
  within one focused block of clarification.
- Claim gates were loaded before any fixed, covered, improved, ready,
  merge-ready, complete, or no-findings claim.
- No retained plan or staged workflow was created inside this skill.
- Review-owned, critical-owned, and retained-plan-owned work stopped at the
  boundary and named the next owner.
- Multi-file edits stayed simple only when they applied the same decided pattern
  and shared one validation path.
- Durable lessons were handed to `internal-lesson-codification` or reported as a
  chat-only candidate when codification was out of scope.
- Focused validation ran before completion claims, or the exact validation gap
  was reported.
