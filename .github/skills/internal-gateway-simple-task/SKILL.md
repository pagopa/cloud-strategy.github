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

When execution stays in the same chat, this skill owns end-to-end direct
completion control. It must keep the original request, emerged requirements,
mandatory applicable requirements, validation path, and evidence status aligned
until everything in scope is closed or a blocker is explicit.

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
Do not preload adjacent skill bodies speculatively. Load only the active lane
owner, mandatory gate owners, and the smallest support owner proven by the
evidence.

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
- For concrete low-to-medium-risk non-trivial work, the required `full-gate`
  posture is `compact full-gate`: one compact `grill-me` block, one critical
  outcome, one lean Readiness Brief, then explicit user approval.
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
- Before that gate, do not launch broad scans, repo-wide discovery, full log
  reads, wide dependency walks, or wide workbook and export inspection when the
  task touches workbooks, exports, logs, dependency trees, or tabular data.
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
   prompt, target path, runtime, ownership, and validation path. Do not
   preload full adjacent skills without evidence.
10. Build a Readiness Brief before operational work: task, lane-owner, primary
    assumption or risk, focused validation path, gate outcome, and explicit
    confirmation prompt or named auto-execute exception.
11. Use `scripts/resolve_simple_task.py gate` when the facts are already known
    and the bundle only needs a deterministic gate and readiness summary.
12. Stop and wait for explicit user approval before executing the lane unless
    the selected narrower owner declares a deterministic auto-execute lane with
    its own zero-blocker, zero ambiguous drift, and no destructive or
    reverse-direction action.
13. After approval, move directly into the edit or validation loop. Keep
    intermediary prose to blockers, risk changes, and evidence.
14. Identify mandatory applicable requirements and direct source items
    internally before execution; do not emit a default user checklist.
15. Maintain `Direct Execution Control` for non-plan execution.
16. Execute the one concrete lane with the Agentic Execution Loop, or, in
    `plan-mode`, write the retained plan and stop before execution.
17. Run focused validation or name the explicit gap.
18. Run a pre-close compliance audit over mandatory applicable requirements
    only. Delegate fresh-evidence mechanics to
    `superpowers-verification-before-completion`.
19. Run `Direct Completion Control` before any `DONE`, readiness, fixed, or
    complete claim.
20. Block completion claims when mandatory applicable requirements remain
    unverified.
21. If architecture ownership, owner conflicts, or validation strategy are
    ambiguous, escalate instead of assuming a universal rule.
22. If the task stops being simple, stop and issue an escalation alert.

Escalation trigger: if evidence collection, ownership checks, or validation needs spill into multi-phase execution, route to the narrow next owner instead of expanding the fast path.

## Agentic Execution Loop

When execution is already authorized, stay inside the active owner, target
scope, anti-scope, and validation path, then iterate:

1. Confirm the current goal, nearest evidence, and the open direct-control item.
2. Apply the smallest in-scope action.
3. Run the focused validation or evidence check.
4. If validation fails for an in-scope, repairable reason, fix once and re-run.
5. Continue only while evidence improves and no stop condition fires.
6. Stop with `DONE` only when direct-control coverage is closed, or stop with a
  blocker or an explicit evidence gap.

Stop on scope drift, destructive action, owner conflict, missing validation
path, human approval need, secret exposure risk, or repeated non-improving
failures.

## Direct Execution Control

Use this mode when the task executes directly in the same chat instead of
creating a retained plan. Keep the control state compact and internal unless a
gap, blocker, or user-facing status update needs to expose it.

Track these fields for non-trivial direct execution:

- original intent, separated from emerged requirements
- target, anti-scope, owner, lane-change owner, and validation path
- direct source items with observable acceptance, evidence class, status, and
  route through the active lane or explicit non-action
- mandatory applicable requirements from selected skills and local evidence
- stop conditions, blockers, and validation gaps

During execution, update direct-control status after every edit, command,
validator, or explicit non-action. If new in-scope work is discovered, add it
before continuing. If new work changes owner, scope, or validation strategy,
stop and escalate instead of silently shrinking the task.

### Direct Completion Control

Before any `DONE`, fixed, complete, ready, validator-passes, or no-gap claim:

1. Compare the original intent, emerged requirements, direct source items,
  current diff or file state, validation output, and explicit non-actions.
2. Confirm every in-scope source item is closed with observable evidence or a
  named explicit non-action.
3. Confirm mandatory applicable requirements are verified with fresh evidence,
  or the exact evidence gap is named.
4. Confirm no stop condition remains open and no sensitive value was hardcoded
  when the touched surface could expose secrets or tenant data.
5. Continue the Agentic Execution Loop when safe work remains; otherwise stop
  with a blocker or explicit evidence gap.

One successful validator, one patched file, or one satisfied subtask is not
enough for completion unless direct-control coverage shows that all in-scope
items are closed.

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
- After approval, execution moved quickly from the chosen edit or validation
  lane to focused verification without extra prose bursts.
- Focused validation ran before completion claims, or the exact validation gap was reported.
- Direct non-plan execution used `Direct Execution Control` for non-trivial
  work and `Direct Completion Control` before completion claims.
- The Agentic Execution Loop stayed inside the authorized owner, scope, and
  validation path.
- Auto-execute exceptions stopped on blockers, ambiguous drift, destructive actions, reverse-direction writes, or missing validation evidence.
- Completion claims were blocked when mandatory applicable requirements were still unverified.
- Completion claims were blocked when any in-scope direct source item remained
  open, unverified, or silently dropped.
- Output stayed concise unless a gap, exception, or escalation had to be reported.

## Common failure modes

- Treating loaded skills as automatically mandatory instead of checking applicability.
- Skipping `grill-me` and the critical gate without a Trivial-skip proof.
- Treating `full`, `idea`, or `complete` as advisory when the user meant to force the full gate.
- Switching to plan mode without declaring it or without user confirmation on implicit cost signals.
- Executing the plan inside simple task instead of handing off to `internal-gateway-execute-plans`.
- Expanding the Readiness Brief into a long checklist or proceeding without explicit user approval when no narrower auto-execute exception applies.
- Running broad scans before the token budget gate on workbook, export, log, dependency, or tabular tasks.
- Treating a generic `next_action.allowed=true` value as enough for auto-execution without checking the narrower skill's stop conditions.
- Continuing the Agentic Execution Loop after evidence stops improving or a
  stop condition fires.
- Declaring completion after code edits while mandatory applicable evidence is still missing.
- Declaring completion after one successful check while direct source items or
  emerged requirements remain open.
- Dropping emerged in-scope requirements because they were not in the initial
  prompt instead of tracking, closing, or explicitly rejecting them as out of
  scope.
- Promoting specialist requirements to universal policy without target/runtime ownership proof.
- Continuing without escalation when ownership conflicts or validation strategy remain undefined.
