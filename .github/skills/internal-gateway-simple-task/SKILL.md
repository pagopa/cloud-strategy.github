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
- Support selection follows the request, target path, scoped instructions, local
  evidence, or an explicit skill call.
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

- The change redesigns ownership, routing, catalog boundaries, `applyTo`,
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

Use at most one focused block of clarification. If ownership, rollout,
governance, tradeoffs, or validation strategy remain ambiguous, escalate.

1. Inspect local files first when repository evidence can answer the question.
2. Run the exit check before using `grill-me`: if the prompt needs a plan,
   retained plan, plan rewrite, or clarify-first planning gate, stop simple
   mode and issue an escalation alert recommending
   `internal-gateway-operational-flow`.
3. If missing context blocks the start and local evidence cannot resolve it, use
   `grill-me` for the minimum necessary clarification.
4. Confirm the task still fits one quick lane.
5. Load only the support skill proved by the prompt, target path, scoped
   instruction, symptom, domain evidence, or validation surface.
6. Answer, edit, diagnose, or validate without creating a retained plan.
7. Run focused validation, or name the explicit validation gap.
8. If the task stops being simple, stop and issue an escalation alert.

Keep the first read budget small: one target or owner file, one matching scoped instruction when applicable, and one nearby validator or test found with `rg`. Open tests only when exact assertions, fixtures, or failure output can change the lane.

## Quick Lanes

| Lane | Use when |
| --- | --- |
| `answer` | Explain or decide from repository evidence without edits. |
| `edit` | Make a clear local change and run the closest focused validation. |
| `diagnose` | Reproduce a failure, drift, or unexpected behavior before fixing it. |
| `validate` | Check a concrete artifact, command, or result. |
| `escalate` | Stop when the task becomes staged, review-owned, retained-plan owned, or critical-challenge owned. |

Read `references/simple-lanes.md` when the lane or output shape is still noisy
after the fast-path boundary is confirmed.

## Support Selection

Do not maintain a finite list of operational skills here. Select support by evidence:

- explicit user-selected skill or domain
- matching scoped instructions for the target path
- file type, runtime, framework, or command surface
- reproduced failure loop or validation signal
- cloud, provider, platform, or governance evidence in the prompt or files

If the prompt mentions a domain that is not represented by a known support
skill, inspect repository evidence and use the closest valid owner. Do not infer
that an unlisted provider, tool, or runtime is unsupported.

Use the `grill-me boundary` below for clarification. Use `references/support-routing.md` only when several plausible support owners compete. Use `scripts/suggest_support_skills.py` only as an advisory helper for known paths or symptoms.

## grill-me boundary

This `grill-me boundary` is canonical for simple mode. Use `grill-me` only for
one focused block of clarification when missing user intent, target path, input data, local context, or a blocker prevents starting or continuing the active simple lane. Do not use simple-mode `grill-me` for pre-plan, ownership, rollout, governance, tradeoff, or validation-strategy decisions. Escalate to `internal-gateway-operational-flow` instead.

## Claim Gates

This section in `SKILL.md` is the source of truth for the claim-gate contract.
`references/support-routing.md` is a lazy-loaded operational mirror and must
stay aligned with these owners. These gates are exceptions to the anti-catalog
posture. They are not a support bundle to preload. Use them only before the matching claim:

- Load `internal-debugging` before saying the original bug, failure, or loop is
  fixed.
- Load `internal-tdd` before saying red-green-refactor passed or a regression is
  covered.
- Load `internal-performance-optimization` before saying performance improved.
- Load `internal-github-pr` before saying a PR is ready, valid, mergeable, or
  complete.
- Load `internal-code-review` before saying there are no code findings or code
  merge-readiness blockers.
- Load `internal-high-level-review` before saying there are no systems findings or
  systems merge-readiness blockers.
- Load `superpowers-verification-before-completion` before any completion,
  readiness, merge-ready, no-findings, fixed, covered, or improved claim.
- Treat `validator passes` as a completion or passing claim. Re-run the
  validator and read fresh output before saying it passed.
- If the touched work includes auth, config, secrets, tenant data, or other
  sensitive values, add a validation note confirming that nothing sensitive was
  hardcoded, or state the exact gap.

If a claim gate makes the work review-owned, staged, retained-plan-owned, or
critical-owned, stop simple mode and escalate instead of making the claim.

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

| Lane | Return |
| --- | --- |
| `answer` | Result, evidence inspected, and uncertainty. |
| `edit` | `lane`, `support-loaded`, `files-touched`, `validation`, and `residual-risk`. |
| `diagnose` | `lane`, `support-loaded`, reproduced failure, root cause, fix or blocker, and evidence. |
| `validate` | `lane`, `support-loaded`, check or command, result, and follow-up owner or gap. |

For escalation, return only the escalation alert fields.

## Validation

- Work stayed single-lane and single-phase, or escalation was explicit.
- The target state was concrete enough for a quick lane.
- Support selection came from evidence, not a broad bundle or partial catalog.
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
