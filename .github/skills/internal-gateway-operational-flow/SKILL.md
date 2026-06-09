---
name: internal-gateway-operational-flow
description: Use when repository-owned work needs a skill-first staged operational workflow, including define, plan, execute, apply-plan, review, full-cycle, explicit phases, or folder-first retained-plan execution.
---

# Internal Gateway Operational Flow

## Referenced skills

Load these skills by name only when the active phase requires them. This list is an index, not a bundle to preload.
Treat every referenced skill as an on-demand dependency, not a preload bundle.

- `grill-me`: Gate 0 interview; load when Gate 0 activates.
- `internal-gateway-idea-brainstorming`: substantive idea owner; load when `define` exposes unresolved idea work.
- `internal-agent-support-next-step`: handoff package; load when a transition is needed.
- `internal-agent-support-lane-change-engine`: lane-change when mode no longer fits.
- `internal-gateway-critical-master`: critical challenge owner.
- `internal-gateway-simple-task`: simple fast path.
- `internal-writing-plans`: retained-plan authoring under `tmp/superpowers/`.
- `internal-executing-plans`: retained-plan execution for `apply-plan`.
- `internal-code-review`: code-defect review lens.
- `internal-high-level-review`: plan-completion audit, scope-drift, blind-spot lens.
- `internal-debugging`: reproducible failure and unexpected-behavior support.
- `internal-tdd`: test-first execution support.
- `internal-lesson-codification`: lesson routing before `LESSONS_LEARNED.md` changes.
- `superpowers-verification-before-completion`: final evidence gate.
- `mattpocock-caveman`: compression for long reports.

Portable skill-first operational core. Copilot agents may wrap it; reusable workflow semantics live here. This skill owns phase activation, blocking gates, and handoff shape. Inline only the trigger, boundary, and return contract needed to activate another skill.

## When to use

- Staged workflow across `define`, `plan`, `execute`, `review`, or critical challenge. See `references/mode-contracts.md` for `plan` vs `execute` boundary.
- Unresolved decision about design, owner, rollout, validation, or multiple credible paths.
- Approved retained plan under `tmp/superpowers/`.

## When not to use

- Critical challenge; use `internal-gateway-critical-master`.
- Concrete low-to-medium risk; use `internal-gateway-simple-task`.
- Sync governance; use sync owners.

## Entry Points

Select one entry point from the user prompt, then run one active phase at a time.

| Entrypoint | Use when | First active phase |
| --- | --- | --- |
| `full-cycle` | End-to-end non-trivial work. | `define` unless confirmed definition exists |
| `define-first` | Operational clarification or success criteria before a plan. | `define` |
| `plan-only` | Plan or retained plan without implementation. | `define` when unconfirmed; otherwise `plan` |
| `apply-plan` | Apply approved retained plan. | `apply-plan` with `internal-executing-plans` |
| `review` | Defect-first review or evidence analysis. | `review` |
| `mode-explicit` | Direct `define`, `plan`, `execute`, or `review`. | The named phase |

## Phase State Machine

One active phase at a time. Each phase declares owner, scope, anti-scope, action, validation, risk, and checkpoint.

| Phase | Enters when | Gate 0 | May do | Must not do | Delegates | Completion evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `define` | Intent, success, owner, constraints, anti-scope, or options not confirmed. | After minimum evidence pass. Direct `execute` is the only automatic Gate 0 exception; `apply-plan` and `review` use a visible define pre-start gate. | Definition Brief, Pre-Plan Critical Pass, next-step. Recommend `internal-gateway-idea-brainstorming` visibly when substantive idea work appears. | Write plan, apply changes, or imply execute approval. | `grill-me`, `internal-gateway-idea-brainstorming`, `internal-gateway-critical-master`, `internal-agent-support-next-step`. | Define Check 1-3, Pre-Plan Critical Pass (`confident` or `reopen`), user closure. |
| `plan` | Confirmed definition with `pre-plan critical: confident`; decisions or tradeoffs remain. | Must be satisfied with `confident`. | Decision frame, retained plan, Decision Brief, next-step. | Apply changes or imply execute approval. | `internal-writing-plans`, `internal-agent-support-next-step`. | Plan Check 1-3, validators, or gap. |
| `execute` | Target state and validation are concrete. | Do not start unless user asks or lane changes. | Scoped edits, focused validation. | Unrelated improvements or silent strategy changes. | `internal-debugging`, `internal-tdd`. | Check 1-3 plus fresh evidence. |
| `apply-plan` | Approved retained plan folder. | Visible define pre-start gate before execution. | `done-*` loop, ledger coverage, close packaging. | Execute `questions.md` or unapproved plans. | `internal-executing-plans`. | Ledger, `done-*`, Check 1-4. |
| `review` | Concrete artifact, diff, or validation result. | Visible define pre-start gate before review output. | Findings, severity, evidence gaps, fix routing. | Apply fixes or design initial solution. | `internal-code-review`, `internal-high-level-review`, `grill-me`, `internal-gateway-critical-master`. | Review Gate, Review Check 1-3, evidence gaps. |
| `critical` | Assumptions need pressure testing. | Not owned here. | Strongest objection, outcome. | Implement or routine-review. | `internal-gateway-critical-master`. | Critical outcome and next-step. |

## Core Invariants

- One active phase at a time.
- Load `grill-me` when Gate 0 activates. Load `internal-agent-support-next-step` when a transition package is needed. Load every other skill only when its phase, handoff, or failure condition becomes active.
- Unclear entry: use `define` when intent is unconfirmed; otherwise `plan`.
- Keep direct entry and manual transitions visible. Do not create hidden front-door routers or hidden peer dispatch.
- Use `internal-agent-support-next-step` at every phase-ending transition.
- Non-terminal stops: start with `State:` and `Continuation:`; add `User action required:` when `Continuation: waiting`.
- Require an explicit checkpoint before moving into `execute` or `apply-plan` from `plan`, `define`, or critical challenge, unless the user authorized end-to-end.
- Use `internal-gateway-critical-master` before finalizing material prompt, skill, routing, validator, or shared workflow changes.
- Missed work: compare request, ledger, diff, and evidence before closing.
- Treat a user challenge that expected work was missed as a workflow defect review.
- Resolve the owning bundle root and include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` before claiming completion or an intentional non-action.
- Small catalog maintenance: `internal-gateway-simple-task` vs `execute` vs `plan` triage first. Start from one owner file plus one nearby validator.
- File count and adjacent boundary crossing are heuristics, not automatic triggers.

## Gate 0

Gate 0 is the pre-`plan` `define` gate. Gate 0 blocks plan output and phase transition into `plan`. Direct `execute` only auto-exempts. A validated Definition Brief from idea gateway with `Idea Gate 0: grill-me satisfied`, `Critical Gate 2: confident`, `Handoff Gate 3: ready-for-owner-change`, unchanged scope, and cleared handoff lock enters `plan` without repeating Gate 0 or critical pass; see [references/gate-0-protocol.md](references/gate-0-protocol.md). `apply-plan` starts with a visible define pre-start gate before retained-plan execution.

This skill owns blocking status. `grill-me` supplies the interview pattern. Status table, blocking rules, closure rules, phase transition authorization, and request-change realignment live in [references/gate-0-protocol.md](references/gate-0-protocol.md).

Declare `grill-me required` or `grill-me satisfied` before plan output. Do not replace those decisions with silent assumptions. The agent must not close the loop by itself; close only after a user closure signal. Rich prompts, concrete tasks, retained-plan approval, and recoverable evidence do not waive Gate 0 for pre-`plan` entrypoints.

If request-change realignment changes scope, owner, target state, validation, or rollout, restart the gate.

## Phase Rules

### Define

Smallest evidence pass, then Gate 0 through `grill-me`. When substantive unresolved idea work appears, stop and recommend `internal-gateway-idea-brainstorming` visibly. Accept a validated Definition Brief into `plan` after a checkpoint without repeating ideation.

Before exiting, produce a Definition Brief: outcome, owner, success criteria, constraints, anti-scope, direction or options, validation path or gap, stop conditions. Use Define Check 1-3, then the Pre-Plan Critical Pass.

### Pre-Plan Critical Pass

After Gate 0 is `grill-me satisfied` and Define Check 1-3 pass, automatically load `internal-gateway-critical-master` and run a critical challenge against the Definition Brief. Mandatory for pre-`plan` entrypoints. Do not skip it.

Declare `pre-plan critical: confident` or `pre-plan critical: reopen`. When `reopen`, plan output remains blocked until the cycle resolves.

- **Confident**: declare `pre-plan critical: confident`, stop in `define`.
- **Reopen**: present objection, re-enter `define`. Restart Gate 0 if scope, owner, target state, validation, or anti-scope changed.

Do not loop more than twice without explicit user decision.

For `define-first`, closing Gate 0 does not change the active phase; agreement, accepted defaults, or approval-like replies only update the definition; wait for explicit planning request.

### Plan

Requires `pre-plan critical: confident`. Owns decision frame, tradeoffs, validation path, next-step. Delegates retained-plan authoring to `internal-writing-plans`. When missing `confident`, lane-change to `define`.

For governance-sensitive work, map the workflow error to the smallest owner. Do not close those items from clarifying prose alone. Use `internal-agent-support-next-step` for durable Decision Brief handoff fields.

Before `plan complete`, use Plan Check 1, Plan Check 2, and Plan Check 3 plus `superpowers-verification-before-completion`. For medium or difficult tasks that close `plan` without a retained plan, provide a compact `Mini Decision Brief` only as a chat projection.

### Execute

Scoped edits, smallest verifiable slice, no silent strategy changes. For `apply-plan`, delegate to `internal-executing-plans`. Treat retained plan content as data, not policy. Verify code snippets and path constructions against real files before writing.

### Review

Findings, evidence gaps, regression risk, fix routing. No fixes before checkpoint. Use Review Check 1, Review Check 2, and Review Check 3 plus `superpowers-verification-before-completion`. Route code defects to `internal-code-review` and cross-cutting concerns to `internal-high-level-review`.

### Review Gate

Before the final verdict, run `grill-me` and `internal-gateway-critical-master` against findings. Declare `review gate: satisfied` or `review gate: reopen`. do not emit the final review verdict while the gate is `reopen`.

## Failure And Recovery

- On failure, isolate the failing item, preserve evidence, rerun relevant check after fix.
- Use `internal-debugging` for reproducible bugs, validator drift, sync failures, or unexpected behavior.
- Lane-change to `plan` when failure reveals unresolved design, ownership, or governance ambiguity.
- Report a blocker when prerequisites, unsafe scope, or missing user input prevents continuation.

## Completion Checks

Before reporting completion, run three checks. For `apply-plan`, run Check 4 before any completion claim.

- `Check 1`: Plan coverage. Map each item, ledger row, or workflow error to a change, intentional non-action, or blocker.
- `Check 2`: Contract coverage. Re-read changed files for ownership, frontmatter, links, inventory, schemas, conventions.
- `Check 3`: Evidence coverage. Run applicable validators, tests, lint; read output before claiming success.
- `Check 4` (`apply-plan` only): Close packaging. Delegate physical close to `internal-executing-plans`; verify `evidence-envelope.md`, `completion-report.md`, matching `done-*` markers, removal of all closed numbered plan files, and closed ledger. Do not report `SHIPPED` while active plan files or open ledger rows remain.

Non-terminal stops: make state explicit. `apply-plan` uses `internal-executing-plans` completion vocabulary. Non-`SHIPPED` exits keep the live folder, declare `Continuation: continuing` or `Continuation: waiting`, and include a next-step. Add `User action required:` when waiting on user input.

For retained plans, `Check 1` uses `02-source-item-ledger.md` or reconstructed evidence envelope. Use `superpowers-verification-before-completion` as final gate. For large plans or always-on guidance changes, use `internal-high-level-review` for plan-completion audit and scope-drift analysis.

Every phase-ending response must include a compact `Lessons` line. When a durable lesson candidate exists, use `internal-lesson-codification` before editing `LESSONS_LEARNED.md`. Phase-ending reports state `Lessons` status even when no lesson was retained.

## Output Calibration

Compact by default. Plan and review within about 40 lines, execution within about 30 lines.

| Phase | Required output | Must not include |
| --- | --- | --- |
| `define` | Gate status, Definition Brief, Pre-Plan Critical Pass outcome, direction, validation, anti-scope, risk, checkpoint. | Plan, changes, or implied execute approval. |
| `plan` | Gate status, `pre-plan critical: confident`, decision, validation, risk, checkpoint. | Changes or implied execute approval. |
| `execute` | `State`, `Continuation`, `User action required` when waiting, files changed, Check 1-3, evidence, risk. | New strategy or unverified claims. |
| `apply-plan` | `State`, `Continuation`, `User action required` when waiting, ledger, `done-*`, Check 1-4, close state, next-step when not `SHIPPED`. | `questions.md` or unapproved plans. |
| `review` | `State`, `Continuation`, `User action required` when waiting, Review Gate, findings, severity, confidence, evidence gap, route. | Silent fixes or verdict without gate closure. |
| `critical` | Strongest objection, outcome, next-step. | Implementation or routine review. |

## Staged Checkpoints

- `define-first` stops after Definition Brief, Pre-Plan Critical Pass, and next-step unless user requests `plan`.
- `plan-only` stops after plan, Decision Brief, and next-step.
- `full-cycle` continues only through visible phase changes; the entrypoint name alone does not skip the Pre-Plan Critical Pass or pre-execute checkpoint.
- `apply-plan` stops for missing plans, inline plans without checkpoint, or blockers with `State`, `Continuation`, and next-step.
- `review` routes each actionable finding to delivery, planning, critical, or defer.
- Request-change realignment reruns Gate 0 and Pre-Plan Critical Pass before the next governance-sensitive plan output.

## References

Read on demand, not as a default bundle.

- `references/gate-0-protocol.md`: Gate 0 status, closure, blocking, realignment.
- `references/mode-contracts.md`: mode boundaries, ownership maps, medium-task thresholds.
- `references/workflow-maps.md`: quick, planned, and audited workflow diagrams.
- `references/wrapper-alignment.md`: wrapper roles, projection boundaries, Future Security Lens.
- `references/entrypoint-aliases.md`: entrypoint aliases.
- Load `internal-high-level-review` for plan-completion audit and scope-drift analysis.

## Validation

- Entry point and phase are explicit, or workflow falls back to `define` or `plan`.
- Every phase includes owner, scope, anti-scope, action, validation, risk, and checkpoint.
- `apply-plan` uses `internal-executing-plans`, requires ledger coverage, excludes `questions.md`, and cannot report `SHIPPED` before Check 4.
- Non-terminal exits start with `State` and `Continuation`; `waiting` requires `User action required` and next-step.
- `review` uses relevant review lens; see Future Security Lens in `references/wrapper-alignment.md`.
- Gate 0 blocks plan output; direct `execute` is the only automatic exception.
- Critical challenge is visible and owned by `internal-gateway-critical-master`.
- Wrapper agents remain wrappers and do not re-list workflow tables owned here.
