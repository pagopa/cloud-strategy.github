---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be answered, edited, diagnosed, or validated quickly without a retained plan, review mode, critical challenge, or staged workflow.
---

# Internal Gateway Simple Task

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `grill-me`: optional clarification support when missing context blocks the start or continuation of simple work.
- `internal-gateway-operational-flow`: staged workflow owner when simple work no longer fits.
- `internal-gateway-critical-master`: critical challenge owner when reasoning, assumptions, or failure modes dominate.
- `internal-debugging`: root-cause owner before claiming a bug, failure, or loop is fixed.
- `internal-tdd`: test-first owner before claiming red-green-refactor or regression coverage.
- `internal-performance-optimization`: measured performance owner before claiming a performance improvement.
- `internal-github-pr`: PR lifecycle owner before claiming readiness, validity, mergeability, or completion.
- `internal-code-review`: defect-first review owner before claiming no code findings or code merge readiness.
- `internal-systems-review`: systems review owner before claiming no systems findings or systems merge readiness.
- `superpowers-verification-before-completion`: final evidence gate before completion, readiness, or no-findings claims.

Use this skill as the skill-first fast path for concrete repository-owned work.
It keeps small and medium tasks light. It is not a hidden router, a retained-plan
engine, or a catalog of every operational skill in the repository.

## When to use

- The target outcome, file, artifact, question, command, or validation path is
  already concrete.
- The work can finish through one quick lane: `answer`, `edit`, `diagnose`,
  `validate`, or `escalate`.
- Support-skill selection can be inferred from the user request, target paths,
  scoped instructions, local evidence, or an explicit skill call.
- The work is low to medium risk and has a focused validation path.
- A heavier gateway de-escalates because the remaining work is a clear answer,
  local edit, diagnosis, or deterministic validation.

## When not to use

- Ownership, target shape, rollout, governance, validation, or cross-boundary
  tradeoffs still need to be settled. Stop and recommend
  `internal-gateway-operational-flow`.
- The request is `plan`, `execute`, `review`, `full-cycle`, `plan-only`,
  `apply-plan`, retained-plan execution, or merge-readiness review. Stop and
  recommend `internal-gateway-operational-flow`.
- The primary request is pressure testing, pre-mortem analysis, hidden
  assumptions, or failure modes. Stop and recommend
  `internal-gateway-critical-master`.
- The task is catalog sync governance or consumer propagation. Use the repo-only
  sync owner instead of this fast path.

## Simple Flow

1. Inspect local files first when repository evidence can answer the question.
2. If missing context blocks the start and local evidence cannot resolve it, use
   `grill-me` for the minimum necessary clarification.
3. Confirm the task still fits one quick lane.
4. Load only the support skill proved by the prompt, target path, scoped
   instruction, symptom, domain evidence, or validation surface.
5. Answer, edit, diagnose, or validate without creating a retained plan.
6. Run focused validation, or name the explicit validation gap.
7. If the task stops being simple, stop and issue an escalation alert.

## Quick Lanes

- `answer`: explain or decide from repository evidence without editing files.
- `edit`: make a clear local change and run the closest focused validation.
- `diagnose`: reproduce a failure, drift, or unexpected behavior before fixing
  it.
- `validate`: check an already concrete artifact, command, or result.
- `escalate`: stop when the task becomes staged, review-owned, retained-plan
  owned, or critical-challenge owned.

Read `references/simple-lanes.md` when the lane or output shape is still noisy
after the fast-path boundary is confirmed.

## Support Selection

Do not maintain a finite list of operational skills here. Select support by
evidence:

- explicit user-selected skill or domain
- matching scoped instructions for the target path
- file type, runtime, framework, or command surface
- reproduced failure loop or validation signal
- cloud, provider, platform, or governance evidence in the prompt or files

If the prompt mentions a domain that is not represented by a known support
skill, inspect repository evidence and use the closest valid owner. Do not infer
that an unlisted provider, tool, or runtime is unsupported.

Use `grill-me` only when missing user intent, target path, input data, local
context, or a blocker prevents starting or continuing the simple lane. Keep the
questions limited to the facts needed to proceed. If the missing information is
really an ownership, rollout, governance, tradeoff, or validation decision,
escalate instead of questioning inside simple mode.

## Claim Gates

These gates are exceptions to the anti-catalog posture. They are not a support
bundle to preload. Use them only before making the matching claim:

- Load `internal-debugging` before saying the original bug, failure, or loop is
  fixed.
- Load `internal-tdd` before saying red-green-refactor passed or a regression is
  covered.
- Load `internal-performance-optimization` before saying performance improved.
- Load `internal-github-pr` before saying a PR is ready, valid, mergeable, or
  complete.
- Load `internal-code-review` before saying there are no code findings or code
  merge-readiness blockers.
- Load `internal-systems-review` before saying there are no systems findings or
  systems merge-readiness blockers.
- Load `superpowers-verification-before-completion` before any completion,
  readiness, merge-ready, no-findings, fixed, covered, or improved claim.

If a claim gate makes the work review-owned, staged, retained-plan-owned, or
critical-owned, stop simple mode and escalate instead of making the claim.

Read `references/support-routing.md` only when several plausible support owners
compete. Use `scripts/suggest_support_skills.py` only as an advisory helper for
known paths or symptoms.

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

For simple work, return the lane used, support actually loaded, result, focused
validation or validation gap, and residual risk if any.

For escalation, return only the escalation alert fields.

## Validation

- The target state was concrete enough for a quick lane, or escalation was
  explicit.
- Support selection came from evidence, not a broad bundle or partial catalog.
- `grill-me`, when used, asked only for the minimum context needed to start or
  unblock simple work.
- Claim gates were loaded before any fixed, covered, improved, ready,
  merge-ready, complete, or no-findings claim.
- No retained plan or staged workflow was created inside this skill.
- Review-owned, critical-owned, and retained-plan-owned work stopped at the
  boundary and named the next owner.
- Focused validation was run before claiming completion, or the exact validation
  gap was reported.
