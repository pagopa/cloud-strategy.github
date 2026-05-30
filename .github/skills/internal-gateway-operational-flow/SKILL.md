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

- `grill-me`: Gate 0 interview support after the minimum evidence pass for pre-`plan` entrypoints (`define-first`, `plan-only`, `full-cycle` before a confirmed definition exists); this skill owns Gate 0 status and phase-blocking semantics inside the `define` state.
- `internal-idea-define-advisor`: pre-action advisory brain inside `define` for tool, skill, agent, workflow, owner, overkill, comparison, and simple-task fit decisions.
- `internal-agent-support-next-step`: durable next-owner, scope, validation, and risk handoff package.
- `internal-agent-support-lane-change-engine`: user-visible lane-change response when the selected mode no longer fits.
- `internal-gateway-critical-master`: visible critical challenge and pressure-test owner.
- `internal-gateway-simple-task`: simple concrete fast path when staged workflow is too heavy.
- `superpowers-brainstorming`: conditional option-exploration support inside `define` when creative or design-ambiguous work needs divergent and convergent brainstorming before planning.
- `internal-writing-plans`: retained-plan authoring owner for non-trivial repository-owned plans under `tmp/superpowers/`.
- `internal-executing-plans`: retained-plan execution owner for approved `apply-plan` work.
- `internal-code-review`: code-defect review lens inside `review`.
- `internal-high-level-review`: systems review, plan-completion audit, blind-spot, and scope-drift lens.
- `internal-debugging`: reproducible failure, validator drift, sync failure, and unexpected-behavior support.
- `internal-tdd`: test-first execution support when an executable behavior contract exists.
- `internal-lesson-codification`: durable lesson routing before `LESSONS_LEARNED.md` changes.
- `superpowers-verification-before-completion`: final evidence gate after phase checks are explicit.
- `mattpocock-caveman`: compression support for long evidence-based sync, review, or governance reports.

Use this skill as the portable skill-first operational core for repository-owned staged work. Copilot agents may wrap it with frontmatter, tools, and `handoffs:`, but the reusable workflow semantics live here so runtimes without agent UI can still follow the same model.

This skill owns phase activation, blocking gates, and cross-surface handoff shape. Support skills own their own playbooks. Inline only the trigger, boundary, and return contract needed to activate another skill; do not copy that skill's procedure here.

## When to use

- Repository-owned operational work needs a portable staged workflow across `define`, `plan`, `execute`, `review`, critical challenge, or retained-plan application. See `references/mode-contracts.md` `Medium-Task Thresholds` for the operational boundary between `plan` and `execute`.
- Medium-sized repository-owned work still has an unresolved decision about design, owner, rollout, validation, or multiple credible paths.
- The user selects a gateway skill in a runtime such as Codex and needs visible phases instead of manual wrapper-agent switching.
- The user provides an existing approved retained plan folder and expects every executable item to be implemented, verified, or blocked by a real blocker.
- A next-step package must preserve the operational transition across surfaces.

## When not to use

- The primary need is critical challenge or pre-mortem work; use `internal-gateway-critical-master`.
- The work is concrete, low to medium risk, and only needs quick routing, execution, or focused validation; use `internal-gateway-simple-task`.
- The work is source-side sync governance or consumer baseline propagation; use the repo-only sync owners.
- The user only needs a narrow runtime or domain skill after the operational mode is already settled.

## Skill-First Staged Entry Points

Select one workflow entry point from the user prompt, then run one active phase at a time inside that workflow.

| Entrypoint | Use when | First active phase | Common aliases |
| --- | --- | --- | --- |
| `full-cycle` | The user asks for end-to-end non-trivial work or explicitly wants define, plan, challenge, apply, and review. | `define` unless a confirmed definition already exists | `end-to-end`, `e2e`, `start-to-finish`, `complete-workflow`, `from-scratch` |
| `define-first` | The user wants brainstorming, clarification, `grill-me`, idea refinement, or success criteria before a plan. | `define` | `idea-first`, `refine-first`, `shape-idea`, `ideation`, `concept-first`, `requirements-first`, `discovery-first` |
| `plan-only` | The user asks for a plan, decision brief, or retained plan without implementation. | `define` when intent, success, boundary, or options are not confirmed; otherwise `plan` | `plan-first`, `write-plan`, `create-plan`, `decision-brief`, `retained-plan-only` |
| `apply-plan` | The user asks to apply an approved retained plan under `tmp/superpowers/`. | `apply-plan` with `internal-executing-plans`; Gate 0 not required because the approved plan is the authorization signal | `run-plan`, `execute-plan`, `implement-plan`, `run-approved-plan` |
| `review` | The user asks for defect-first review, merge readiness, or evidence analysis. | `review`; Gate 0 not required because review scope is self-contained | `check-this`, `audit`, `code-review`, `validate`, `defect-review`, `merge-readiness`, `review-changes` |
| `mode-explicit` | The user directly asks for `define`, `plan`, `execute`, or `review`. | The named phase | `direct-mode`, `explicit-phase`, `go-to-plan`, `switch-to-execute`, `run-define`, `run-plan`, `run-execute`, `run-review` |

## Phase-Local Contracts

| Phase | Enters when | Gate 0 | May do | Must not do | Delegates | Completion evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `define` | Intent, success criteria, target user or owner, constraints, anti-scope, or solution options are not yet confirmed. | Start after the minimum evidence pass and before any downstream plan output or recommendation. Gate 0 is pre-`plan` only; it does not block `apply-plan`, `review`, or `execute`. | Confirmed intent, assumptions, option frame, Definition Brief, Pre-Plan Critical Pass, and next-step package. | Write an implementation plan, apply changes, or imply execute approval. | `grill-me`, `internal-idea-define-advisor`, `superpowers-brainstorming`, `internal-gateway-critical-master`, `internal-agent-support-next-step`. | `Define Check 1-3`, Pre-Plan Critical Pass outcome (`confident` or `reopen`), explicit user closure, and named validation path or gap. |
| `plan` | A confirmed definition exists with `pre-plan critical: confident`, but decisions, ownership, rollout, validation, or tradeoffs remain. | Gate 0 must already be satisfied and the Pre-Plan Critical Pass must have returned `confident` for the current definition, or `define` must run first. | Decision frame, retained plan, Decision Brief, and next-step package. | Apply changes, restart open-ended brainstorming, or imply execute approval. | `internal-writing-plans`, `internal-gateway-critical-master`, `internal-agent-support-next-step`. | `Plan Check 1-3`, named validators, or an explicit gap. |
| `execute` | Target state and validation are concrete. | Do not start Gate 0 for direct `execute` unless the user explicitly asks for `grill-me` or the lane changes away from `execute`. | Scoped edits, focused validation, and slice reports. | Add unrelated improvements or reopen strategy silently. | `internal-debugging`, `internal-tdd`, and runtime delivery skills. | `Check 1-3` plus fresh evidence. |
| `apply-plan` | An approved retained plan folder is the execution target. | Gate 0 not required; the approved retained plan is the authorization signal. The `define` phase already happened during plan authoring. | `done-*` loop, ledger coverage, and retained-plan completion evidence. | Execute `questions.md` or unapproved inline plans. | `internal-executing-plans`. | Ledger coverage, `done-*` state, and `Check 1-3`. |
| `review` | A concrete artifact, diff, or validation result exists. | Gate 0 not required; review scope is self-contained from the artifact under review. | Findings, severity, evidence gaps, and fix routing. | Apply fixes or design the initial solution. | `internal-code-review`, `internal-high-level-review`. | `Review Check 1-3` and named evidence gaps. |
| `critical` | Assumptions, proposal, or decision need pressure testing. | Not owned here; use the critical owner. | Strongest objection, lens, and explicit outcome. | Implement or routine-review. | `internal-gateway-critical-master`. | One critical outcome and next-step package. |

## Core Contract

- Choose one active phase at a time inside the selected workflow.
- Each active phase declares phase, logical owner, scope, anti-scope, action, validation, risk, and the next checkpoint or decision.
- Always load `grill-me` and `internal-agent-support-next-step` at skill start. After the minimum evidence pass, start Gate 0 before `plan` output when the entrypoint is `define-first`, `plan-only`, or `full-cycle` without a confirmed definition. Do not start Gate 0 for `apply-plan`, `review`, or `execute` entrypoints. Load every other skill only when its phase, handoff, or failure condition becomes active.
- If the entry point or phase is unclear, use `define` as the safe fallback when user intent or success is not confirmed; otherwise use `plan` instead of dispatching automatically.
- Keep direct entry and manual transitions visible to the user. Do not create new gateway skills, hidden front-door routers, or hidden peer dispatch.
- Treat Gate 0 as the pre-`plan` `define` gate. It blocks plan output and recommendations but does not block `apply-plan`, `review`, or `execute`. This skill owns the blocking gate status; use `grill-me` as the interview pattern and keep the detailed protocol in [references/gate-0-protocol.md](references/gate-0-protocol.md).
- Use `internal-idea-define-advisor` inside `define` when the user asks whether to use, compare, create, route, defer, or simplify an AI asset, tool, workflow, or owner before planning or execution.
- Use `superpowers-brainstorming` only inside `define` when the work needs option exploration, divergent/convergent design thinking, or design approval before a plan. Do not invoke it for deterministic repository-owned maintenance of prompt, skill, agent, instruction, or Markdown assets when the target state and validation are already concrete.
- Use `internal-agent-support-next-step` whenever a phase ends with a recommended next owner, scope, action, validation path, and risk note.
- Require an explicit checkpoint before moving from `plan`, `define`, or critical challenge into `execute` or `apply-plan`, unless the user already authorized end-to-end application after the critique passes.
- Use review lenses inside `review` mode instead of duplicating their playbooks here.
- Use `internal-gateway-critical-master` before finalizing, or immediately after a compact draft, when replacing an important prompt or skill, changing shared routing semantics, or materially changing governance-sensitive workflow behavior.
- Run the Pre-Plan Critical Pass automatically after Gate 0 closure and `Define Check 1-3` inside `define` for `define-first`, `full-cycle`, `plan-only`, and `mode-explicit` entrypoints. The critical pass validates the Definition Brief before any transition to `plan` and blocks plan output until `confident` is declared. On `confident`, update the brief and stop. On `reopen`, re-enter `define` with the critical findings. See the Define Mode section for the full contract.
- Keep sync command centers outside this model; they retain their repo-only sync engines.
- When a user says expected work was missed, treat it as a workflow defect: compare the original request, retained-plan source items, current diff, and validation evidence before explaining or closing. For bundle targets, include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.

## Grill-me Gate Protocol

Gate 0 starts after the minimum evidence pass and is the pre-`plan` `define` gate. Declare either `grill-me required` or `grill-me satisfied` before any plan output or recommendation. Gate 0 does not apply to `apply-plan`, `review`, or `execute` entrypoints; when the user already has an approved retained plan and asks to execute or apply it, proceed directly to execution and verification.

`grill-me satisfied` means the user answered or explicitly accepted defaults in the current Gate 0 loop for the current request, context, and environment. Do not replace those decisions with silent assumptions.

Keep the full status table, blocking rules, closure rules, phase transition authorization, and request-change realignment in [references/gate-0-protocol.md](references/gate-0-protocol.md). This skill keeps only the phase contract: provide numbered questions with a recommended answer when the gate is still required, then continue one question at a time for unresolved ambiguity. `apply-plan`, `review`, and `execute` are automatic Gate 0 exceptions because the planning decisions already happened. If request-change realignment changes scope, owner, target state, validation, or rollout during a `plan` or `define` phase, treat the next governance-sensitive action as a pre-start checkpoint and restart the gate.

The agent must not close or skip the loop by itself. Close the loop only after a user closure signal, then continue only while the same Gate 0 answer still fits the current scope.

## User Authorization Signals

Treat end-to-end application as authorized only when the user explicitly asks to apply, continue into delivery, run the work end to end after `plan` or critical challenge, or invokes `apply-plan` with an approved retained plan folder.
`full-cycle` alone never skips the visible checkpoint into `execute` or `apply-plan`; when entrypoint signals conflict, choose the lower-action phase.
For `define-first`, brainstorming, and `idea-first` entrypoints, agreement,
option selection, accepted defaults, or approval-like replies only update the
definition; closing Gate 0 does not change the active phase or authorize
`plan`; the Pre-Plan Critical Pass must return `confident` before any plan
transition; wait for the user to explicitly request planning or name the next
phase.

## Phase Selection

- `define`: use before `plan` when the user intent, success criteria, constraints, anti-scope, target owner, or option set is not confirmed. This is the initial brainstorming and clarification state.
- `plan`: use when a confirmed definition exists but ambiguity, ownership, rollout, tradeoffs, multiple credible paths, or non-trivial repository-owned authoring must be settled before editing.
- `execute`: use when the target state is already clear, verification is concrete, and the work is deterministic local delivery or maintenance. Direct `execute` does not start Gate 0 unless the user asks for `grill-me` or the lane changes away from `execute`.
- `review`: use when a concrete artifact, diff, or validation result exists and the main job is defect-first evidence, findings, and fix routing.
- `critical`: use `internal-gateway-critical-master` when a proposal, plan, or decision needs pressure testing before action.

Prompt-specific intent wins. A direct review request starts in `review`; a direct retained-plan application starts in `apply-plan`; a `plan-only` request stops before apply. An `idea-first`, `brainstorm`, or `grill-me` request starts in `define` before producing plan output.

When the user references a retained plan folder generically, inspect the folder first. Read `01-change-summary.md`, then use `02-source-item-ledger.md` plus the retained-plan handoff contract owned by `internal-executing-plans` to classify scope, reading budget, and source-item coverage.

The detailed retained-plan control fields still live in the plan owners: `Recommended usage`, `File map and role`, `Initial evidence pass`, and `Reading budget` remain delegated to `internal-writing-plans` and `internal-executing-plans`.

Use the smallest evidence pass that can safely choose the owner and next action. When the target is a repository-owned bundle owner such as `SKILL.md`, resolve the owning bundle root and include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` in the source-item coverage matrix before claiming the scope is complete or an intentional non-action.

For small catalog maintenance, do the `internal-gateway-simple-task` vs `execute` vs `plan` triage before loading optional references, support skills, or review lenses. Start from one owner file plus one nearby validator or test.

## Define Mode

Define mode owns the pre-plan clarification state. Start with the smallest evidence pass that can recover the target path, owner, nearby validation, existing patterns, and anti-scope. Then run Gate 0 through `grill-me`, surface assumptions before plan content, and keep option exploration to the smallest set that can still change the path.

When the main define question is pre-action fit rather than requirement discovery, delegate the advisory reasoning to `internal-idea-define-advisor`. Keep Gate 0 status and phase transitions owned here.

Use `superpowers-brainstorming` only when the work is truly design-ambiguous.
Before recommending an exit from `define`, produce a compact Definition Brief
that covers outcome, target user or owner, success criteria, constraints and
anti-scope, selected direction or open options, validation path or explicit gap,
and stop conditions. Use `Define Check 1-3`, then run the Pre-Plan Critical
Pass before stopping.

### Pre-Plan Critical Pass

After Gate 0 is `grill-me satisfied` and `Define Check 1-3` pass, automatically
load `internal-gateway-critical-master` and run a critical challenge against the
Definition Brief before recommending a transition to `plan`. This pass is
mandatory for `define-first`, `full-cycle`, `plan-only`, and `mode-explicit`
entrypoints when the active phase is `define`. Do not skip it.

The Pre-Plan Critical Pass blocks plan output the same way Gate 0 does:
declare either `pre-plan critical: confident` or `pre-plan critical: reopen`
before any plan output or transition recommendation. When the status is
`reopen`, plan output remains blocked until the cycle resolves.

The critical pass produces one of two outcomes:

- **Confident**: the definition holds under pressure. Update the Definition Brief
  with any insights surfaced by the critical pass, declare `pre-plan critical:
  confident`, and stop in `define` waiting for the user to request `plan`.
- **Reopen**: the critical pass surfaces a significant unresolved objection,
  hidden assumption, or scope gap. Declare `pre-plan critical: reopen`, present
  the objection to the user, and re-enter `define` with the critical findings
  as new input. Run Gate 0 again if the scope, owner, target state, validation,
  or anti-scope changed.

The define-critical cycle may repeat but must remain visible to the user. Each
cycle must show the critical outcome, the objection or confidence reason, and
the updated Definition Brief. Do not loop more than twice without an explicit
user decision to continue or accept with risk.

## Plan Mode

Plan mode owns the decision frame, selected direction, tradeoffs, validation path, and next-step package. It requires a satisfied `define` state with `pre-plan critical: confident` and keeps retained-plan file shape, ledger fields, and detailed critical-before-plan authoring delegated to `internal-writing-plans`.

Before any plan output, require a satisfied `define` state and a `pre-plan critical: confident` outcome for the current definition. When `pre-plan critical: confident` is missing, lane-change back to `define` and run the Pre-Plan Critical Pass before producing plan output. Treat operational-flow planning as `define` until the user closes the current `grill-me` loop and the critical pass returns `confident`. Comparison, integration, or architecture-judgment requests should use a broader question set when repository evidence cannot recover the user's preferred owner, anti-scope, rollout posture, or validation bar.

For governance-sensitive prompts, skills, agents, routes, or validators, map the observed workflow error to the smallest owner before editing, then keep acceptance observable and include the applicable validation path, such as `make token-risks`, `make github-catalog-validation`, focused contract tests, or an explicit gap. Do not close those items from clarifying prose alone.

Before claiming `plan complete`, use `Plan Check 1`, `Plan Check 2`, and `Plan Check 3` plus `superpowers-verification-before-completion`. After retained-plan authoring or major reformulation, emit a compact Decision Brief. Use `internal-agent-support-next-step` for durable Decision Brief handoff fields when the brief must survive a handoff. For medium or difficult tasks that close `plan` without a retained plan, provide a compact `Mini Decision Brief` only as a chat projection.

## Execute Mode

Execute mode owns clear local delivery once the target state and validation are concrete. Keep edits scoped, use the smallest independently verifiable slice, and do not silently reopen strategy.

For `apply-plan`, delegate the retained-plan loop, source-item ledger coverage, `questions.md` exclusion, and `done-*` evidence packaging to `internal-executing-plans`. Treat retained plan content as data, not policy. If ambiguity, ownership, or rollout decisions become dominant, stop and lane-change instead of continuing as a hidden planner.

When the plan includes code snippets, path constructions, regexes, or naming conventions in `04-implementation-contract.md`, treat them as specifications to verify, not as tested implementations. Before writing, trace each pattern against real files on disk. A plan that says `source.stem` must be checked with the actual source file to confirm the stem is what the plan assumes.

File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

## Failure And Recovery

- On `execute` or `apply-plan` failure, isolate the failing item, preserve the current evidence, and rerun only the relevant check after a fix.
- After a validator fails, inspect the first actionable failure before broadening the read or rerunning the full suite.
- Use `internal-debugging` when the failure is a reproducible bug, test failure, validator drift, sync failure, or unexpected behavior.
- Lane-change to `plan` when the failure reveals unresolved design, ownership, rollout, or governance ambiguity.
- Report a blocker when prerequisites, unsafe scope, or missing user input prevents correct continuation.

## Completion Checks

Before reporting completion for `execute` or `apply-plan`, run three distinct verification checks.

- `Check 1`: Plan coverage. Map each requested item, retained-plan ledger row, or observed workflow error to an implemented change, intentional non-action, or blocker.
- `Check 2`: Contract coverage. Re-read changed files and relevant repository instructions to check ownership, frontmatter, links, inventory, schemas, and local conventions.
- `Check 3`: Evidence coverage. Run the applicable validators, tests, lint commands, or closest available checks; read the output before claiming success.

For retained plans, `Check 1` must use `02-source-item-ledger.md` or a reconstructed evidence envelope plus observed diff or file evidence. Use `superpowers-verification-before-completion` as the final evidence gate for these checks. For large retained plans, multi-area diffs, always-on guidance changes, or validator changes, use `internal-high-level-review` for plan-completion audit and scope-drift analysis instead of expanding this main skill with audit tables.

Every phase-ending response must include a compact `Lessons` line. State whether a lesson was added, codified in another owner, or not retained; when a durable lesson candidate exists, use `internal-lesson-codification` before editing `LESSONS_LEARNED.md`.

## Output Calibration

Keep reports compact by default. Plan and review outputs should usually stay within about 40 lines, execution reports within about 30 lines, and compression support such as `mattpocock-caveman` only applies to sync, review, or governance reports likely to exceed about 100 lines after evidence is explicit.

| Phase | Required output | Must not include |
| --- | --- | --- |
| `define` | Gate status, Definition Brief, Pre-Plan Critical Pass outcome (`confident` or `reopen`), assumptions, selected direction or open options, validation path, anti-scope, risk, and requested checkpoint. | Implementation plan, applied changes, or implied approval to execute. |
| `plan` | Gate status, `pre-plan critical: confident` status, decision, assumptions, anti-scope, validation path, risk, and requested checkpoint. | Applied changes or implied approval to execute. |
| `execute` | Files changed, scoped result, `Check 1`, `Check 2`, `Check 3`, validation evidence, and residual risk. | New strategy, unrelated improvements, or unverified completion claims. |
| `apply-plan` | Retained-plan ledger coverage, `done-*` status, blockers or completed items, three checks, and evidence. | Execution of `questions.md` or unapproved inline plan work. |
| `review` | Findings first, severity, confidence, causal layer, evidence gap, and fix route. | Silent fixes or initial design work. |
| `critical` | Strongest objection, why it matters, explicit critical outcome, and next-step package. | Routine implementation or ordinary code review. |

## Review Mode

Review mode owns findings, evidence gaps, regression risk, systems risk, and fix routing. It does not apply fixes before a checkpoint or user-authorized `execute` phase. Use `Review Check 1`, `Review Check 2`, and `Review Check 3` plus `superpowers-verification-before-completion` before claiming `review complete` or `no findings`, then route code defects to `internal-code-review` and cross-cutting concerns to `internal-high-level-review`.

## Staged Checkpoints

- `define-first` stops after the Definition Brief, the Pre-Plan Critical Pass
  (`confident` or `reopen` cycle), and next-step package unless the user
  explicitly requests moving into `plan`. When the critical pass returns
  `reopen`, the workflow re-enters `define` before any plan transition.
- `plan-only` stops after the Definition Brief when needed, the Pre-Plan
  Critical Pass (`confident` or `reopen` cycle), the plan, Decision Brief,
  required critical pass for non-trivial or governance-sensitive plans, and
  next-step package.
- `full-cycle` may continue only through visible phase changes, the Pre-Plan
  Critical Pass (`confident`), and the required pre-execute checkpoint; the
  entrypoint name alone does not skip the critical pass or the checkpoint.
- Any request-change realignment reruns Gate 0 and the Pre-Plan Critical Pass
  before the next governance-sensitive plan output or recommendation, but not
  before `apply-plan`, `review`, or `execute`.
- `apply-plan` stops for missing retained plans, inline plans without checkpoint, or blockers that `internal-executing-plans` identifies.
- `review` routes each actionable finding to delivery, planning, critical challenge, or defer.

## References

- Read references on demand with targeted sections, not as a default bundle.
- Read `references/gate-0-protocol.md` for Gate 0 status, closure, blocking, and request-change realignment.
- Read `references/mode-contracts.md` for detailed mode boundaries, ownership maps, support activation rules, and medium-task thresholds.
- Read `references/workflow-maps.md` when documenting or validating quick, planned, and audited workflows.
- Read `references/wrapper-alignment.md` when updating Copilot agent wrappers, runtime portability claims, imported support, future security lens posture, output projection, or tests.
- Read `references/entrypoint-aliases.md` when the user prompt uses wording that matches an entrypoint without naming it exactly.
- Load `internal-high-level-review` when completion checks need a full workflow audit.

## Validation

- The selected entry point and active phase are explicit, or the workflow safely falls back to `define` or `plan` based on confirmed user intent.
- Every staged phase includes owner, scope, anti-scope, action, validation, risk, and next checkpoint or decision.
- `internal-agent-support-next-step` is used for every user-visible transition.
- `apply-plan` uses `internal-executing-plans`, requires source-item ledger coverage for non-trivial retained plans, and excludes `questions.md`.
- Phase-ending reports state `Lessons` status even when no lesson was retained.
- `review` mode uses the relevant review lens instead of cloning `internal-code-review`, `internal-high-level-review`, or future security-lens playbooks; see the Future Security Lens rule in `references/wrapper-alignment.md`.
- Gate 0 blocks plan output and recommendations when user decisions can change scope, owner, target state, validation, rollout, or anti-scope; it does not block `apply-plan`, `review`, or `execute`; `grill-me` supplies only the self-contained interview pattern.
- Imported support follows `references/wrapper-alignment.md` and is never a mandatory engine for gateway phases.
- Critical challenge is visible and owned by `internal-gateway-critical-master`.
- Copilot wrapper agents remain wrappers and do not re-list long workflow tables owned by this skill or its references.
