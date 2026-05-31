---
name: internal-gateway-operational-flow
description: Use when repository-owned work needs a skill-first staged operational workflow, including define, plan, execute, apply-plan, review, full-cycle, explicit phases, or folder-first retained-plan execution.
---

# Internal Gateway Operational Flow

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.
Load these skills by name only when the active phase requires them. This list is an index, not a bundle to preload.
Always preload only `grill-me` and `internal-agent-support-next-step`.
Treat every other referenced skill as an on-demand dependency, not a preload bundle.

- `grill-me`: Gate 0 interview support after the minimum evidence pass for pre-`plan` entrypoints.
- `internal-idea-define-advisor`: pre-action advisory brain inside `define` for tool, skill, agent, workflow, owner, and overkill decisions.
- `internal-agent-support-next-step`: durable next-owner, scope, validation, and risk handoff package.
- `internal-agent-support-lane-change-engine`: user-visible lane-change response when the selected mode no longer fits.
- `internal-gateway-critical-master`: visible critical challenge and pressure-test owner.
- `internal-gateway-simple-task`: simple concrete fast path when staged workflow is too heavy.
- `superpowers-brainstorming`: option-exploration inside `define` for design-ambiguous work.
- `internal-writing-plans`: retained-plan authoring owner for plans under `tmp/superpowers/`.
- `internal-executing-plans`: retained-plan execution owner for `apply-plan` work.
- `internal-code-review`: code-defect review lens inside `review`.
- `internal-high-level-review`: systems review, plan-completion audit, blind-spot, and scope-drift lens.
- `internal-debugging`: reproducible failure, validator drift, sync failure, and unexpected-behavior support.
- `internal-tdd`: test-first execution support when an executable behavior contract exists.
- `internal-lesson-codification`: durable lesson routing before `LESSONS_LEARNED.md` changes.
- `superpowers-verification-before-completion`: final evidence gate after phase checks are explicit.
- `mattpocock-caveman`: compression support for long reports.

Use this skill as the portable skill-first operational core for repository-owned staged work. Copilot agents may wrap it with frontmatter, tools, and `handoffs:`, but the reusable workflow semantics live here so runtimes without agent UI can still follow the same model.

This skill owns phase activation, blocking gates, and cross-surface handoff shape. Support skills own their own playbooks. Inline only the trigger, boundary, and return contract needed to activate another skill; do not copy that skill's procedure here.

## When to use

- Repository-owned work needs a portable staged workflow across `define`, `plan`, `execute`, `review`, or critical challenge. See `references/mode-contracts.md` for the `plan` vs `execute` boundary.
- Medium-sized repository-owned work still has an unresolved decision about design, owner, rollout, validation, or multiple credible paths.
- The user provides an approved retained plan under `tmp/superpowers/`.
- A next-step package must preserve the operational transition across surfaces.

## When not to use

- Primary need is critical challenge; use `internal-gateway-critical-master`.
- Work is concrete, low-to-medium risk; use `internal-gateway-simple-task`.
- Source-side sync governance or consumer baseline propagation; use repo-only sync owners.
- Only a narrow runtime or domain skill is needed after the operational mode is settled.

## Entry Points

Select one workflow entry point from the user prompt, then run one active phase at a time inside that workflow.

| Entrypoint | Use when | First active phase |
| --- | --- | --- |
| `full-cycle` | The user asks for end-to-end non-trivial work or explicitly wants define, plan, challenge, apply, and review. | `define` unless a confirmed definition already exists |
| `define-first` | The user wants brainstorming, clarification, `grill-me`, idea refinement, or success criteria before a plan. | `define` |
| `plan-only` | The user asks for a plan, decision brief, or retained plan without implementation. | `define` when intent, success, boundary, or options are not confirmed; otherwise `plan` |
| `plan-only (clarify-first)` | Legacy input spelling for `define-first`; keep as compatibility, not as a separate phase. | `define` |
| `apply-plan` | The user asks to apply an approved retained plan under `tmp/superpowers/`. | `apply-plan` with `internal-executing-plans` |
| `review` | The user asks for defect-first review, merge readiness, or evidence analysis. | `review` |
| `mode-explicit` | The user directly asks for `define`, `plan`, `execute`, or `review`. | The named phase |

## Phase State Machine

One active phase at a time. Each phase declares owner, scope, anti-scope, action, validation, risk, and the next checkpoint.

| Phase | Enters when | Gate 0 | May do | Must not do | Delegates | Completion evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `define` | Intent, success criteria, target user or owner, constraints, anti-scope, or solution options are not yet confirmed. | Start after the minimum evidence pass and before any downstream plan output or recommendation. Direct `execute` is the only automatic Gate 0 exception; `apply-plan` and `review` use a visible define pre-start gate. | Confirmed intent, assumptions, option frame, Definition Brief, Pre-Plan Critical Pass, and next-step package. | Write an implementation plan, apply changes, or imply execute approval. | `grill-me`, `internal-idea-define-advisor`, `superpowers-brainstorming`, `internal-gateway-critical-master`, `internal-agent-support-next-step`. | `Define Check 1-3`, Pre-Plan Critical Pass outcome (`confident` or `reopen`), explicit user closure, and named validation path or gap. |
| `plan` | A confirmed definition exists with `pre-plan critical: confident`, but decisions, ownership, rollout, validation, or tradeoffs remain. | Gate 0 must already be satisfied and the Pre-Plan Critical Pass must have returned `confident` for the current definition, or `define` must run first. | Decision frame, retained plan, Decision Brief, and next-step package. | Apply changes, restart open-ended brainstorming, or imply execute approval. | `internal-writing-plans`, `internal-agent-support-next-step`. | `Plan Check 1-3`, named validators, or an explicit gap. |
| `execute` | Target state and validation are concrete. | Do not start Gate 0 for direct `execute` unless the user explicitly asks for `grill-me` or the lane changes away from `execute`. | Scoped edits, focused validation, and slice reports. | Add unrelated improvements or reopen strategy silently. | `internal-debugging`, `internal-tdd`, and runtime delivery skills. | `Check 1-3` plus fresh evidence. |
| `apply-plan` | An approved retained plan folder is the execution target. | Gate 0 applies. Run the visible define pre-start gate before retained-plan execution, then continue without restarting it mid-loop unless the lane changes away from `apply-plan`. | `done-*` loop, ledger coverage, retained-plan close packaging, and completion evidence. | Execute `questions.md` or unapproved inline plans. | `internal-executing-plans`. | Ledger coverage, `done-*` state, `Check 1-3`, and retained-plan `Check 4`. |
| `review` | A concrete artifact, diff, or validation result exists. | Gate 0 applies as a pre-start define gate before review output. | Findings, severity, evidence gaps, and fix routing. | Apply fixes or design the initial solution. | `internal-code-review`, `internal-high-level-review`, `grill-me`, `internal-gateway-critical-master`. | Review Gate (`grill-me satisfied` and `pre-verdict critical: confident`), `Review Check 1-3`, and named evidence gaps. |
| `critical` | Assumptions, proposal, or decision need pressure testing. | Not owned here; use the critical owner. | Strongest objection, lens, and explicit outcome. | Implement or routine-review. | `internal-gateway-critical-master`. | One critical outcome and next-step package. |

## Core Invariants

- One active phase at a time inside the selected workflow.
- Always preload `grill-me` and `internal-agent-support-next-step`. Load every other skill only when its phase, handoff, or failure condition becomes active.
- Unclear entry point: use `define` when intent is unconfirmed; otherwise use `plan`.
- Keep direct entry and manual transitions visible. Do not create new gateway skills, hidden front-door routers, or hidden peer dispatch.
- Use `internal-agent-support-next-step` at every phase-ending transition.
- If `execute`, `apply-plan`, or `review` stops without a terminal success
  claim, start the response with `State:` and `Continuation:`. Use
  `internal-agent-support-next-step`, and add `User action required:` when
  `Continuation` is `waiting`.
- Require an explicit checkpoint before moving into `execute` or `apply-plan` from `plan`, `define`, or critical challenge, unless the user already authorized end-to-end application.
- Use `internal-gateway-critical-master` before finalizing material prompt, skill, routing, validator, or shared workflow changes.
- When expected work was missed: compare the original request, ledger, diff, and validation evidence before closing. For bundle targets, include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.
- Treat a user challenge that expected work was missed as a workflow defect review before any reassurance or closeout.
- resolve the owning bundle root and include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` in the source-item coverage matrix before claiming the scope is complete or an intentional non-action.

- For small catalog maintenance, do the `internal-gateway-simple-task` vs `execute` vs `plan` triage first. Start from one owner file plus one nearby validator or test.

- File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

## Gate 0

Gate 0 is the pre-`plan` `define` gate. It blocks plan output and recommendations. Direct `execute` is the only automatic exception. `apply-plan` starts with a visible define pre-start gate before retained-plan execution.

This skill owns the blocking status. `grill-me` supplies the interview pattern. Full status table, blocking rules, closure rules, phase transition authorization, and request-change realignment live in [references/gate-0-protocol.md](references/gate-0-protocol.md).

Declare `grill-me required` or `grill-me satisfied` before any plan output. `grill-me satisfied` means the user answered or explicitly accepted defaults in the current Gate 0 loop for the current request, context, and environment. Do not replace those decisions with silent assumptions. The agent must not close the loop by itself; close only after a user closure signal. Rich prompts, concrete tasks, retained-plan approval, and recoverable evidence do not waive Gate 0 for pre-`plan` entrypoints or for the visible `apply-plan` pre-start gate.

If request-change realignment changes scope, owner, target state, validation, or rollout, restart the gate.

## Phase Rules

### Define

Start with the smallest evidence pass to recover the target path, owner, nearby validation, existing patterns, and anti-scope. Run Gate 0 through `grill-me`, surface assumptions before plan content.

Use `superpowers-brainstorming` only when design-ambiguous. When the main question is pre-action fit, delegate to `internal-idea-define-advisor`.

Before exiting `define`, produce a Definition Brief covering outcome, owner, success criteria, constraints, anti-scope, selected direction or open options, validation path or gap, and stop conditions. Use `Define Check 1-3`, then run the Pre-Plan Critical Pass.

### Pre-Plan Critical Pass

After Gate 0 is `grill-me satisfied` and `Define Check 1-3` pass, automatically load `internal-gateway-critical-master` and run a critical challenge against the Definition Brief. This pass is mandatory for pre-`plan` entrypoints. Do not skip it.

Declare `pre-plan critical: confident` or `pre-plan critical: reopen`. When `reopen`, plan output remains blocked until the cycle resolves.

- **Confident**: the definition holds under pressure. Declare `pre-plan critical: confident` and stop in `define` waiting for the user to request the next phase.
- **Reopen**: the critical pass surfaces a significant unresolved objection. Declare `pre-plan critical: reopen`, present the objection, and re-enter `define` with the critical findings as new input. Restart Gate 0 if scope, owner, target state, validation, or anti-scope changed.

Do not loop more than twice without explicit user decision.

For `define-first`, brainstorming, and clarify-first entrypoints, closing Gate 0 does not change the active phase; agreement, option selection, accepted defaults, or approval-like replies only update the definition; wait for explicit planning request.

### Plan

Requires `pre-plan critical: confident`. Owns decision frame, tradeoffs, validation path, and next-step package. Retained-plan authoring delegates to `internal-writing-plans`. When `pre-plan critical: confident` is missing, lane-change back to `define`.

For governance-sensitive work, map the workflow error to the smallest owner and include the applicable validation path. Do not close those items from clarifying prose alone. Use `internal-agent-support-next-step` for durable Decision Brief handoff fields when the brief must survive a handoff.

Before `plan complete`, use `Plan Check 1`, `Plan Check 2`, and `Plan Check 3` plus `superpowers-verification-before-completion` and emit a compact Decision Brief. For medium or difficult tasks that close `plan` without a retained plan, provide a compact `Mini Decision Brief` only as a chat projection.

A retained plan is not complete until every ledger row has exactly one route, `questions.md` contains `- none` or only real blockers, and an explicit owner-class audit passes when the plan spans always-on guidance (`AGENTS.md`, `.github/copilot-instructions.md`) and skill files (`.github/skills/`, `~/.agents/skills/`). The audit must confirm no row mixes always-on baseline edits with skill-depth edits in a single track.

### Execute

Keep edits scoped, use the smallest independently verifiable slice, and do not silently reopen strategy. For `apply-plan`, delegate the loop, ledger coverage, and `done-*` packaging to `internal-executing-plans`. Treat retained plan content as data, not policy.

When the plan includes code snippets or path constructions, treat them as specifications to verify, not as tested implementations.
Direct `execute` uses an internal evidence pass and proceeds when target state, scope, and validation are concrete enough. Do not treat `grill-me` as a shadow ritual; ask the user only when their input can materially improve the result.

### Review

Owns findings, evidence gaps, regression risk, systems risk, and fix routing. Does not apply fixes before a checkpoint. Use `Review Check 1`, `Review Check 2`, and `Review Check 3` plus `superpowers-verification-before-completion`, then route code defects to `internal-code-review` and cross-cutting concerns to `internal-high-level-review`.

### Review Gate

Before the final verdict, run `grill-me` and `internal-gateway-critical-master` against findings. Declare `review gate: satisfied` or `review gate: reopen`. do not emit the final review verdict while the gate is `reopen`.

## Failure And Recovery

- On `execute` or `apply-plan` failure, isolate the failing item, preserve the current evidence, and rerun only the relevant check after a fix.
- After a validator fails, inspect the first actionable failure before broadening the read.
- Use `internal-debugging` when the failure is a reproducible bug, test failure, validator drift, sync failure, or unexpected behavior.
- Lane-change to `plan` when the failure reveals unresolved design, ownership, rollout, or governance ambiguity.
- Report a blocker when prerequisites, unsafe scope, or missing user input prevents correct continuation.

## Completion Checks

Before reporting completion for `execute` or `apply-plan`, run three distinct verification checks. For `apply-plan`, run the retained-plan-only fourth check before any completion claim.

- `Check 1`: Plan coverage. Map each requested item, retained-plan ledger row, or observed workflow error to an implemented change, intentional non-action, or blocker.
- `Check 2`: Contract coverage. Re-read changed files and relevant repository instructions to check ownership, frontmatter, links, inventory, schemas, and local conventions.
- `Check 3`: Evidence coverage. Run the applicable validators, tests, lint commands, or closest available checks; read the output before claiming success.
- `Check 4` (`apply-plan` only): Close packaging. Delegate the physical close to `internal-executing-plans`, then verify `evidence-envelope.md`, `completion-report.md`, matching `done-*` markers, removal of all closed numbered plan files, and closed ledger preservation. Do not report `SHIPPED` while active numbered plan files or open ledger rows remain.

For any non-terminal `execute`, `apply-plan`, or `review` stop, make the stop
state explicit instead of implying completion. `apply-plan` uses the completion
state vocabulary owned by `internal-executing-plans` and its completion-report
reference. Non-`SHIPPED` retained-plan exits must keep
the live folder in place, declare `Continuation: continuing` or
`Continuation: waiting`, and include a visible next-step package. When the stop
depends on user input, approval, or an external prerequisite, add `User action
required:` with the exact missing action.

For retained plans, `Check 1` must use `02-source-item-ledger.md` or a reconstructed evidence envelope plus observed diff or file evidence. Use `superpowers-verification-before-completion` as the final evidence gate. For large retained plans, multi-area diffs, always-on guidance changes, or validator changes, use `internal-high-level-review` for plan-completion audit and scope-drift analysis.

Every phase-ending response must include a compact `Lessons` line. State whether a lesson was added, codified in another owner, or not retained; when a durable lesson candidate exists, use `internal-lesson-codification` before editing `LESSONS_LEARNED.md`.

## Output Calibration

Keep reports compact by default. Plan and review outputs should usually stay within about 40 lines, execution reports within about 30 lines.

| Phase | Required output | Must not include |
| --- | --- | --- |
| `define` | Gate status, Definition Brief, Pre-Plan Critical Pass outcome, assumptions, selected direction or open options, validation path, anti-scope, risk, and requested checkpoint. | Implementation plan, applied changes, or implied approval to execute. |
| `plan` | Gate status, `pre-plan critical: confident` status, decision, assumptions, anti-scope, validation path, risk, and requested checkpoint. | Applied changes or implied approval to execute. |
| `execute` | `State`, `Continuation`, `User action required` when waiting, files changed, scoped result, `Check 1`, `Check 2`, `Check 3`, validation evidence, and residual risk. | New strategy, unrelated improvements, or unverified completion claims. |
| `apply-plan` | `State`, `Continuation`, `User action required` when waiting, retained-plan ledger coverage, `done-*` status, blockers or completed items, `Check 1-4`, close-package state, evidence, and next-step package when not `SHIPPED`. | Execution of `questions.md` or unapproved inline plan work. |
| `review` | `State`, `Continuation`, `User action required` when waiting, Review Gate status, findings first, severity, confidence, causal layer, evidence gap, and fix route. | Silent fixes, initial design work, or final verdict without review gate closure. |
| `critical` | Strongest objection, why it matters, explicit critical outcome, and next-step package. | Routine implementation or ordinary code review. |

## Staged Checkpoints

- `define-first` stops after the Definition Brief, the Pre-Plan Critical Pass, and next-step package unless the user explicitly requests `plan`.
- `plan-only` stops after the plan, Decision Brief, and next-step package.
- `full-cycle` continues only through visible phase changes; the entrypoint name alone does not skip the Pre-Plan Critical Pass or the pre-execute checkpoint.
- `apply-plan` stops for missing retained plans, inline plans without checkpoint, or blockers, and those non-`SHIPPED` stops must include explicit `State`, `Continuation`, and next-step package fields.
- `review` routes each actionable finding to delivery, planning, critical challenge, or defer.
- Any request-change realignment reruns Gate 0 and the Pre-Plan Critical Pass before the next governance-sensitive plan output.

## References

- Read references on demand with targeted sections, not as a default bundle.
- Read `references/gate-0-protocol.md` for Gate 0 status, closure, blocking, and request-change realignment.
- Read `references/mode-contracts.md` for detailed mode boundaries, ownership maps, support activation rules, and medium-task thresholds.
- Read `references/workflow-maps.md` when documenting or validating quick, planned, and audited workflows.
- Read `references/wrapper-alignment.md` when updating Copilot agent wrappers, runtime portability claims, imported support, future security lens posture, output projection, or tests.
- Read `references/entrypoint-aliases.md` when the user prompt uses wording that matches an entrypoint without naming it exactly.
- Load `internal-high-level-review` when completion checks need a full workflow audit.

## Validation

- Entry point and active phase are explicit, or the workflow falls back to `define` or `plan`.
- Every phase includes owner, scope, anti-scope, action, validation, risk, and next checkpoint.
- `internal-agent-support-next-step` is used for every user-visible transition.
- `apply-plan` uses `internal-executing-plans`, requires source-item ledger coverage, excludes `questions.md`, and cannot report `SHIPPED` before retained-plan `Check 4` closes physical artifacts.
- Non-terminal `execute`, `apply-plan`, and `review` exits start with explicit
  `State` and `Continuation`; `Continuation: waiting` also requires `User action
  required` plus a visible next-step package.
- Phase-ending reports state `Lessons` status even when no lesson was retained.
- `review` uses the relevant review lens; see Future Security Lens rule in `references/wrapper-alignment.md`.
- Gate 0 blocks plan output when user decisions can change scope, owner, target state, validation, rollout, or anti-scope; direct `execute` is the only automatic exception, and `apply-plan` uses a visible pre-start gate.
- Imported support follows `references/wrapper-alignment.md` and is never a mandatory gateway engine.
- Critical challenge is visible and owned by `internal-gateway-critical-master`.
- Copilot wrapper agents remain wrappers and do not re-list workflow tables owned here.

(End of file - total 182 lines)
