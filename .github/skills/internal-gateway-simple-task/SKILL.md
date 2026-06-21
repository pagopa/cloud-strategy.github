---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be answered, edited, diagnosed, validated, or planned quickly through one lane.
---

# Internal Gateway Simple Task

## Referenced skills

Load these skills by name only when the active lane proves the narrower owner.
Treat this list as an on-demand index, not a preload bundle.

- `grill-me`: mandatory pre-action interview for non-trivial simple work and one focused clarification block for simple blockers.
- `internal-gateway-idea-brainstorming`: planning owner when simple work no longer fits or needs substantive ideation.
- `internal-gateway-writing-plans`: retained-plan authoring owner when simple task switches to plan mode.
- `internal-gateway-review`: review owner when defect-first analysis becomes dominant.
- `internal-gateway-critical-master`: mandatory post-interview critical gate for non-trivial simple work and critical owner when assumptions or failure modes dominate.
- `superpowers-verification-before-completion`: final evidence gate.

Use this skill as the skill-first fast path for concrete repository-owned work.
It is single-lane and single-phase by design, but it can switch to **plan mode**
to produce a retained plan instead of executing when the user asks for a plan or
when same-chat execution would be less economical than a retained plan.

Before operational work, produce a lean Readiness Brief and name the gate
outcome. Stop for explicit user approval unless a narrower loaded skill defines
a deterministic auto-execute lane with its own zero-blocker, no-drift, and
post-run reporting gates.

`references/support-routing.md` remains the single source of truth for claim-gate owners in simple mode.
`references/simple-lanes.md` remains the single source of truth for lane definitions, support posture, and validation per lane.
`references/plan-mode.md` remains the single source of truth for plan-mode activation, profile selection, and procedure.

Use `scripts/resolve_simple_task.py` when the task facts are already known and
the bundle only needs a deterministic gate or claim-gate answer. Use
`scripts/suggest_support_skills.py` only when paths or symptoms are known and
support selection is still noisy.

## When to use

- The outcome, target, command, or validation path is already concrete.
- One quick lane can finish: `answer`, `edit`, `diagnose`, `validate`, or `plan`.
- The user explicitly asks for a plan, or cost signals show that a retained plan is cheaper than same-chat execution.

## When not to use

- Ownership, rollout, governance, or cross-boundary tradeoffs still need a decision; use `internal-gateway-idea-brainstorming`.
- The request is defect-first review; use `internal-gateway-review`.
- The request is approved retained-plan execution; use `internal-gateway-execute-plans`.
- The primary request is pressure testing; use `internal-gateway-critical-master`.

## Simple Gate Policy

Classify every simple task before operational work as `full-gate`,
`trivial-skip`, `escalate`, or `plan-mode`.

- Use `full-gate` by default unless the task is proven trivial and venial.
- Run `grill-me` first with one compact numbered block, then the critical gate.
- Before editing, executing, or finalizing, ask the user to respond first to
  the `grill-me` block and then to the critical outcome.
- Treat `full`, `idea`, and `complete` as depth keywords. A depth keyword
  forbids `trivial-skip`. Run `grill-me` first, then the critical gate.
- Use `trivial-skip` only for a local answer, tiny edit, focused read, or
  validator run with no material ambiguity or material risk and with obvious
  validation or a named validation gap.
- When using `trivial-skip`, emit a short Trivial-skip proof before operational
  work.
- Use `plan-mode` when the user explicitly asks for a plan or when cost signals
  show that same-chat execution is less economical than a retained plan.
- If planning, review, critical pressure, or multi-phase validation becomes the
  real job, `escalate`.

### Token Budget Gate

- Run a `Token Budget Gate` before choosing `trivial-skip` or `plan-mode` when
  the user asks for low-token execution or the task centers on large tabular
  files, log exports, repeated tool output, or broad file changes.
- For Copilot or debug log analysis, start with file size, model-call counts,
  prompt or token aggregates, tool-span counts, result-size summaries, and
  targeted slices; avoid full JSON dumps or prompt bodies unless they are the
  missing evidence.
- Keep compact reporting runner-agnostic: ask for bounded summaries, exit
  state, counts, anomalies, and evidence gaps, but do not require `jq`, `awk`,
  shell flags, or terminal-only recipes unless they are already the local
  workflow being analyzed.
- A cost checkpoint pauses before a new expensive tool burst, broad reread, or
  repeated execution loop. It does not interrupt ordinary conversation,
  grill-me questioning, or collaborative reasoning when no expensive tool
  action is being launched.
- If the user explicitly asks for full output, deeper slices, or continued
  execution, name the likely token or context impact before expanding and then
  either proceed with the smallest bounded next slice or ask for confirmation
  before the new expensive burst.
- Keep `trivial-skip` only for truly tiny local work with obvious validation
  and no material completeness risk.
- If context pressure could hide required validation, data integrity, or route
  ownership, prefer `plan-mode` and apply the `Plan Profile Selection Guard`
  before proposing `compact`.

## Simple Procedure

1. Inspect local files first.
2. Preserve compact working state: avoid full-context rereads unless new evidence invalidates the active lane assumptions.
3. Detect depth keywords: `full`, `idea`, or `complete`.
4. Classify the gate outcome as `full-gate`, `trivial-skip`, `escalate`, or
   `plan-mode`.
5. For `full-gate`, load `grill-me`, ask one compact numbered block, then load
   `internal-gateway-critical-master` after the user's response.
6. For `trivial-skip`, emit the Trivial-skip proof before operational work.
7. For `plan-mode`, run `grill-me` and `internal-gateway-critical-master` as for
   `full-gate`, then load `internal-gateway-writing-plans` and write the retained
   plan. Stop before execution.
8. Confirm the task still fits one quick lane and choose that lane from
   `references/simple-lanes.md`.
9. Select only directly applicable skill owners and required references from
   prompt, target path, runtime, ownership, and validation path.
10. Build a Readiness Brief before operational work: task, lane-owner, primary
    assumption or risk, focused validation path, gate outcome, and explicit
    confirmation prompt or named auto-execute exception.
11. Use `scripts/resolve_simple_task.py gate` when the facts are already known
    and the bundle only needs a deterministic gate and readiness summary.
12. Stop and wait for explicit user approval before executing the lane unless
    the selected narrower owner declares a deterministic auto-execute lane with
    its own zero-blocker, zero ambiguous drift, and no destructive or
    reverse-direction action.
13. Identify mandatory applicable requirements internally before execution; do
    not emit a default user checklist.
14. Execute the one concrete lane with the Agentic Execution Loop, or, in
    `plan-mode`, write the retained plan and stop before execution.
15. Run focused validation or name the explicit gap.
16. Run a pre-close compliance audit over mandatory applicable requirements
    only. Delegate fresh-evidence mechanics to
    `superpowers-verification-before-completion`.
17. Block completion claims when mandatory applicable requirements remain
    unverified.
18. If architecture ownership, owner conflicts, or validation strategy are
    ambiguous, escalate instead of assuming a universal rule.
19. If the task stops being simple, stop and issue an escalation alert.

Escalation trigger: if evidence collection, ownership checks, or validation needs spill into multi-phase execution, route to the narrow next owner instead of expanding the fast path.

## Agentic Execution Loop

When execution is already authorized, stay inside the active owner, target
scope, anti-scope, and validation path, then iterate:

1. Confirm the current goal and nearest evidence.
2. Apply the smallest in-scope action.
3. Run the focused validation or evidence check.
4. If validation fails for an in-scope, repairable reason, fix once and re-run.
5. Continue only while evidence improves and no stop condition fires.
6. Stop with `DONE`, a blocker, or an explicit evidence gap.

Stop on scope drift, destructive action, owner conflict, missing validation
path, human approval need, secret exposure risk, or repeated non-improving
failures.

## Plan Mode

Plan mode lets a concrete simple task produce a retained plan instead of
executing in the same chat. The task stays single-lane and single-phase; only
the output shape changes.

### Activation

- **Mandatory explicit**: if the user asks for a plan with keywords such as
  `plan`, `piano`, `modalità plan`, `retained plan`, `scrivi il piano`,
  `non eseguire ancora`, or similar, switch to plan mode and honor the request.
- **Implicit cost signal**: if the user says nothing about a plan, but cost
  signals show that same-chat execution would be less economical than a retained
  plan, declare `plan-mode` and ask the user to confirm before writing the plan.
  See `references/plan-mode.md` for the exact cost-signal checklist.

### Profile

- Default to `compact` (`tmp/superpowers/mini-plan-*`) with
  `01-change-summary.md` and `02-execution.md` only when the task stays within
  one owner, one execution lane, one primary validation path, and low
  completeness risk.
- Apply the `Plan Profile Selection Guard` before proposing `compact`.
- Use `extended` when the task needs multi-slice execution, multiple
  independent validators, an articulated anti-scope, external pins,
  cross-skill token-discipline work, validator-impacting changes, or
  exports, generated reports, and datasets that need non-trivial
  reconciliation.

### Procedure

1. Classify the gate as `plan-mode`.
2. Run `grill-me` and `internal-gateway-critical-master` exactly as for
   `full-gate`.
3. Load `internal-gateway-writing-plans` and author the retained plan using its
   local contract.
4. Stop before execution. Report the plan folder and next owner
   (`internal-gateway-execute-plans`).

### Boundaries

- Do not use plan mode to avoid a hard ownership decision. If the target,
  anti-scope, or validation strategy is ambiguous, `escalate` instead.
- Do not use plan mode for vague ideas or substantive tradeoffs; use
  `internal-gateway-idea-brainstorming`.
- Do not execute the plan inside simple task. Execution belongs to
  `internal-gateway-execute-plans`.

## Deterministic Helpers

- `scripts/resolve_simple_task.py gate`: returns `full-gate`,
  `trivial-skip`, `escalate`, or `plan-mode` plus a lean Readiness Brief from
  normalized task facts.
- `scripts/resolve_simple_task.py claim`: maps status claims to the required
  owners and evidence gates before the final answer.
- `scripts/suggest_support_skills.py`: returns path and symptom-based support
  hints. It is advisory and does not override repository evidence.

## Validation

- Work stayed single-lane and single-phase, or escalation was explicit.
- `full-gate`, `trivial-skip`, `escalate`, or `plan-mode` was named before operational work.
- Non-trivial simple work used `grill-me` before `internal-gateway-critical-master`, and depth keywords prevented `trivial-skip`.
- `trivial-skip` included evidence that the task was trivial and venial.
- Readiness Brief stayed lean, named the lane-owner and validation path, and
  included an explicit approval checkpoint or named the narrower auto-execute exception.
- Focused validation ran before completion claims, or the exact validation gap was reported.
- The Agentic Execution Loop stayed inside the authorized owner, scope, and
  validation path.
- Auto-execute exceptions stopped on blockers, ambiguous drift, destructive actions, reverse-direction writes, or missing validation evidence.
- Completion claims were blocked when mandatory applicable requirements were still unverified.
- Output stayed concise unless a gap, exception, or escalation had to be reported.

## Common failure modes

- Treating loaded skills as automatically mandatory instead of checking applicability.
- Skipping `grill-me` and the critical gate without a Trivial-skip proof.
- Treating `full`, `idea`, or `complete` as advisory when the user meant to force the full gate.
- Switching to plan mode without declaring it or without user confirmation on implicit cost signals.
- Executing the plan inside simple task instead of handing off to `internal-gateway-execute-plans`.
- Expanding the Readiness Brief into a long checklist or proceeding without explicit user approval when no narrower auto-execute exception applies.
- Treating a generic `next_action.allowed=true` value as enough for auto-execution without checking the narrower skill's stop conditions.
- Continuing the Agentic Execution Loop after evidence stops improving or a
  stop condition fires.
- Declaring completion after code edits while mandatory applicable evidence is still missing.
- Promoting specialist requirements to universal policy without target/runtime ownership proof.
- Continuing without escalation when ownership conflicts or validation strategy remain undefined.
