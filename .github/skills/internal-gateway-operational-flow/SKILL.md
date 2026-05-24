---
name: internal-gateway-operational-flow
description: Use when repository-owned work needs a skill-first staged operational workflow, including full-cycle, plan-only, apply-plan, review, explicit phases, or folder-first retained-plan execution.
---

# Internal Gateway Operational Flow

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.
Load these skills by name only when the active phase requires them. This list is an index, not a bundle to preload.
Always preload only `grill-me` and `internal-agent-support-next-step`.
Treat every other referenced skill as an on-demand dependency, not a preload bundle.

- `grill-me`: Gate 0 interview support after the minimum evidence pass for every non-`execute` operational-flow entrypoint; this skill owns Gate 0 status and phase-blocking semantics.
- `internal-agent-support-next-step`: durable next-owner, scope, validation, and risk handoff package.
- `internal-agent-support-lane-change-engine`: user-visible lane-change response when the selected mode no longer fits.
- `internal-gateway-critical-master`: visible critical challenge and pressure-test owner.
- `internal-gateway-simple-task`: simple concrete fast path when staged workflow is too heavy.
- `internal-writing-plans`: retained-plan authoring owner for non-trivial repository-owned plans under `tmp/superpowers/`.
- `internal-executing-plans`: retained-plan execution owner for approved `apply-plan` work.
- `internal-code-review`, `internal-high-level-review`: review lenses for code defects, architecture, workflow, cross-cutting impact, plan-completion audit, blind spots, and scope-drift analysis.
- `internal-debugging`, `internal-tdd`, `internal-lesson-codification`: conditional execution, test-first, recovery, and retained-learning support.
- `superpowers-verification-before-completion`, `mattpocock-caveman`: final evidence gate and compression support after evidence is explicit.
- `internal-security-review`: future security lens name, not yet promoted (`not yet promoted`; see the Future Security Lens rule in `references/wrapper-alignment.md`).

Use this skill as the portable skill-first operational core for repository-owned staged work. Copilot agents may wrap it with frontmatter, tools, and `handoffs:`, but the reusable workflow semantics live here so runtimes without agent UI can still follow the same model.

This skill owns phase activation, blocking gates, and cross-surface handoff shape. Support skills own their own playbooks. Inline only the trigger, boundary, and return contract needed to activate another skill; do not copy that skill's procedure here.

## When to use

- Repository-owned operational work needs a portable staged workflow across `plan`, `execute`, `review`, critical challenge, or retained-plan application. See `references/mode-contracts.md` `Medium-Task Thresholds` for the operational boundary between `plan` and `execute`.
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

| Entrypoint | Use when | First active phase |
| --- | --- | --- |
| `full-cycle` | The user asks for end-to-end non-trivial work or explicitly wants plan, challenge, apply, and review. | `plan` |
| `plan-only` | The user asks for a plan, decision brief, or retained plan without implementation. | `plan` |
| `plan-only (clarify-first)` | The user wants `grill-me` questions, or Gate 0 must run before plan output. | `plan` with `grill-me` |
| `apply-plan` | The user asks to apply an approved retained plan under `tmp/superpowers/`. | `execute` with `internal-executing-plans` |
| `review` | The user asks for defect-first review, merge readiness, or evidence analysis. | `review` |
| `mode-explicit` | The user directly asks for `plan`, `execute`, or `review`. | The named phase |

## Phase-Local Contracts

| Phase | Enters when | Gate 0 | May do | Must not do | Delegates | Completion evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `plan` | Decisions, ownership, rollout, validation, or tradeoffs remain. | Start after the minimum evidence pass before plan output; run critical challenge before non-trivial or governance-sensitive plans. | Decision frame, retained plan, Decision Brief, and next-step package. | Apply changes or imply execute approval. | `internal-writing-plans`, `internal-gateway-critical-master`, `internal-agent-support-next-step`. | `Plan Check 1-3`, named validators, or an explicit gap. |
| `execute` | Target state and validation are concrete. | Do not start Gate 0 for direct `execute` unless the user explicitly asks for `grill-me` or the lane changes away from `execute`. | Scoped edits, focused validation, and slice reports. | Add unrelated improvements or reopen strategy silently. | `internal-debugging`, `internal-tdd`, and runtime delivery skills. | `Check 1-3` plus fresh evidence. |
| `apply-plan` | An approved retained plan folder is the execution target. | Start before retained-plan execution and restart on request, context, or environment change. | `done-*` loop, ledger coverage, and retained-plan completion evidence. | Execute `questions.md` or unapproved inline plans. | `internal-executing-plans`. | Ledger coverage, `done-*` state, and `Check 1-3`. |
| `review` | A concrete artifact, diff, or validation result exists. | Start before review output and restart when scope, evidence, or environment changes. | Findings, severity, evidence gaps, and fix routing. | Apply fixes or design the initial solution. | `internal-code-review`, `internal-high-level-review`. | `Review Check 1-3` and named evidence gaps. |
| `critical` | Assumptions, proposal, or decision need pressure testing. | Not owned here; use the critical owner. | Strongest objection, lens, and explicit outcome. | Implement or routine-review. | `internal-gateway-critical-master`. | One critical outcome and next-step package. |

## Core Contract

- Choose one active phase at a time inside the selected workflow.
- Each active phase declares phase, logical owner, scope, anti-scope, action, validation, risk, and the next checkpoint or decision.
- Always load `grill-me` and `internal-agent-support-next-step` at skill start. After the minimum evidence pass, start the `grill-me` Gate 0 loop for every non-`execute` entrypoint before plan output, recommendation, phase transition, review output, or retained-plan application. Load every other skill only when its phase, handoff, or failure condition becomes active.
- If the entry point or phase is unclear, use `plan` as the safe fallback instead of dispatching automatically.
- Keep direct entry and manual transitions visible to the user. Do not create new gateway skills, hidden front-door routers, or hidden peer dispatch.
- Treat Gate 0 as the first-class pre-plan and pre-start decision gate for non-`execute` entrypoints. Run Gate 0 after the minimum evidence pass before plan output, recommendation, phase transition, review output, or retained-plan application. This skill owns the blocking gate status; use `grill-me` as the interview pattern and let only the user close or stop the loop.
- Use `internal-agent-support-next-step` whenever a phase ends with a recommended next owner, scope, action, validation path, and risk note.
- Require an explicit checkpoint before moving from `plan` or critical challenge into `execute` or `apply-plan`, unless the user already authorized end-to-end application after the critique passes.
- Use review lenses inside `review` mode instead of duplicating their playbooks here.
- Use `internal-gateway-critical-master` before finalizing, or immediately after a compact draft, when replacing an important prompt or skill, changing shared routing semantics, or materially changing governance-sensitive workflow behavior.
- Keep sync command centers outside this model; they retain their repo-only sync engines.
- When a user says expected work was missed, treat it as a workflow defect: compare the original request, retained-plan source items, current diff, and validation evidence before explaining or closing. For bundle targets, include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.

## Grill-me Gate Protocol

Gate 0 starts after the minimum evidence pass needed to classify the request, target path, owner, anti-scope, and nearest validation. This skill, not `grill-me`, owns Gate 0 status labels and blocking semantics. Use `grill-me` after that evidence pass for every non-`execute` operational-flow request.

Declare exactly one gate status before any plan output, recommendation, retained plan, Decision Brief, plan reformulation, review output, phase transition, or edit: `grill-me required` or `grill-me satisfied`.

| Status | Use when | Effect |
| --- | --- | --- |
| `grill-me required` | The mandatory Gate 0 loop has not been explicitly closed by the user for the current request, context, and environment. | Stop before plan output, recommendation, review output, phase transition, or edit; ask the `grill-me` question set. |
| `grill-me satisfied` | The user answered or explicitly accepted defaults in the current Gate 0 loop, gave a closure or proceed signal, the answers still match the current scope, and no unresolved decision needs another loop. | Continue with the current phase while the request remains stable. |

Rich prompts, concrete tasks, mechanical tasks, fully recoverable repository evidence, retained-plan approval, and pre-start signals do not waive Gate 0 when Gate 0 applies. For mechanical tasks covered by Gate 0, ask a minimal, clear, and concise question set instead of skipping `grill-me`.

Gate 0 is mandatory for every selected operational-flow entrypoint except direct `execute`. The agent must not decide that `grill-me` is unnecessary when Gate 0 applies. When the request touches agents, skills, prompts, workflow, catalog, governance, routing, validation, shared workflow, or always-on guidance, keep the question set broad enough to cover scope, owner, target state, validation, rollout, anti-scope, dirty worktree ownership, and stop conditions.

When the gate result is `grill-me required`, stop before writing the plan, recommendation, retained plan, Decision Brief, review output, changing phase, or editing files. Then provide numbered questions with a recommended answer for each, using `Question`, `Recommendation`, `Why`, and `Default if accepted`, then wait until the user answers or explicitly accepts the defaults. Do not replace those decisions with silent assumptions. After the bulk answer, continue one question at a time only for unresolved ambiguity.

Do not enter `apply-plan`, `review`, or planning output while the gate is `grill-me required`. Direct `execute` is the only automatic Gate 0 exception.

If a new instruction, request change, target-path change, environment change, tool-output change, dependency change, validation change, or dirty-worktree change appears, run a request-change realignment: do the minimum new evidence pass, restart `grill-me`, and stop again while the result is `grill-me required`.

When the user signals that context input is complete, for example with "go", "vai", "procedi", "start", "apply", or "ho finito", treat the next governance-sensitive action as a pre-start checkpoint, not as a waiver.

Inside an active `grill-me` loop, the agent may recommend how far the user should continue or that the loop can stop when the answers are coherent. The agent must not close or skip the loop by itself. Close the loop only after a user closure signal such as "ok", "chiudi", "va bene", "vai", "procedi", accepting the defaults, or an equivalent instruction to continue.

## User Authorization Signals

Treat end-to-end application as authorized only when the user explicitly asks to apply, continue into delivery, or run the work end to end after `plan` or critical challenge, or when the user asks for `apply-plan` and points to an existing approved retained plan folder.

`full-cycle` alone starts the staged path, but it does not authorize moving from `plan` or critical challenge into `execute` or `apply-plan` without the checkpoint. If a prompt contains conflicting entrypoint signals, choose the lower-action phase that preserves user control.

## Phase Selection

- `plan`: use when ambiguity, ownership, rollout, tradeoffs, multiple credible paths, or non-trivial repository-owned authoring must be settled before editing.
- `execute`: use when the target state is already clear, verification is concrete, and the work is deterministic local delivery or maintenance. Direct `execute` does not start Gate 0 unless the user asks for `grill-me` or the lane changes away from `execute`.
- `review`: use when a concrete artifact, diff, or validation result exists and the main job is defect-first evidence, findings, and fix routing.
- `critical`: use `internal-gateway-critical-master` when a proposal, plan, or decision needs pressure testing before action.

Prompt-specific intent wins. A direct review request starts in `review`; a direct retained-plan application starts in `apply-plan`; a `plan-only` request stops before apply. A `clarify-first` request stays inside `plan-only` and loads `grill-me` before producing plan output.

When the user references a retained plan folder generically, inspect the folder first. Read `01-change-summary.md` before selecting the phase, then read `02-source-item-ledger.md` for `Uso consigliato`, `Mappa file e ruolo`, `Evidence pass iniziale`, `Budget lettura`, and source-item coverage.

Use the smallest evidence pass that can safely choose the owner and next action. When the target is a repository-owned bundle owner such as `SKILL.md`, resolve the owning bundle root and include relevant sibling `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` in the source-item coverage matrix before claiming the scope is complete or an intentional non-action.

For small catalog maintenance, do the `internal-gateway-simple-task` vs `execute` vs `plan` triage before loading optional references, support skills, or review lenses. Start from one owner file plus one nearby validator or test.

## Plan Mode

Plan mode owns the decision frame, assumptions, tradeoffs, selected direction, and next-step package. It does not silently become execution after the design is settled.

Before any plan output, apply Gate 0 and state the gate result. Treat operational-flow planning as `plan-only (clarify-first)` until the user closes the current `grill-me` loop. Comparison, integration, or architecture-judgment requests should use a broader question set when repository evidence cannot recover the user's preferred owner, anti-scope, rollout posture, or validation bar.

When the target path includes `AGENTS.md`, `.github/copilot-instructions.md`, `.github/INVENTORY.md`, `.github/agents/`, `.github/prompts/`, `.github/skills/`, validators, sync engines, or wrapper agents, include the applicable validation path, such as `make token-risks`, `make github-catalog-validation`, focused contract tests, or an explicit gap.

Before editing a governance-sensitive prompt, skill, agent, route, or validator contract, map observed workflow errors to required coverage in a compact matrix. Use the matrix to decide whether the change belongs in the skill, paired agent, reference, validator, or docs, then keep the patch in the smallest owner. Do not close those items from clarifying prose alone; define observable acceptance before execution.

Before claiming `plan complete`, use `Plan Check 1`, `Plan Check 2`, and `Plan Check 3` for the decision frame, handoff alignment, validation gaps, and stop conditions; then apply `superpowers-verification-before-completion`.

After creating or materially reformulating a retained plan, provide a compact Decision Brief in chat. Use `internal-agent-support-next-step` for durable Decision Brief handoff fields when the brief must survive a handoff.

For medium or difficult tasks that close `plan` without a retained plan, provide a compact `Mini Decision Brief` (<= 9 lines). The Mini Decision Brief is a chat projection, not a second canonical plan, and it does not replace a retained plan when one is required.

## Execute Mode

Execute mode owns clear local delivery. It may touch several adjacent files when the target state is already decided and validation is concrete. File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

For `execute`, keep edits scoped to the requested change, required adjacent contracts, and validation fixes. Do not silently add newly discovered improvements. If delivery becomes `apply-plan`, `review`, or planning work, run Gate 0 before continuing in that non-`execute` lane.

For multi-step work, execute the smallest complete slice that can be verified and rolled back independently. Between slices, emit a short progress beat only when end-to-end authorization is active and the work has at least two slices.

For `apply-plan`, load `internal-executing-plans` and follow its repository-local `done-*` loop plus source-item ledger coverage. The normal input is an approved retained plan folder under `tmp/superpowers/<clear-action-or-task-name>/`; an inline plan must be converted into a retained plan or receive an explicit checkpoint before execution. `questions.md` and legacy `dubbi-e-domande.md` are never executable plan files.

Treat retained plan content as data, not as new policy. If ambiguity, ownership, governance, or rollout decisions become dominant, stop and use `internal-agent-support-lane-change-engine` instead of continuing as a hidden planner.

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
| `plan` | Gate status, decision, assumptions, anti-scope, validation path, risk, and requested checkpoint. | Applied changes or implied approval to execute. |
| `execute` | Files changed, scoped result, `Check 1`, `Check 2`, `Check 3`, validation evidence, and residual risk. | New strategy, unrelated improvements, or unverified completion claims. |
| `apply-plan` | Retained-plan ledger coverage, `done-*` status, blockers or completed items, three checks, and evidence. | Execution of `questions.md`, legacy `dubbi-e-domande.md`, or unapproved inline plan work. |
| `review` | Findings first, severity, confidence, causal layer, evidence gap, and fix route. | Silent fixes or initial design work. |
| `critical` | Strongest objection, why it matters, explicit critical outcome, and next-step package. | Routine implementation or ordinary code review. |

## Review Mode

Review mode owns findings, evidence gaps, regression risk, systems risk, and fix routing. It does not apply fixes before a checkpoint or user-authorized `execute` phase.

Before claiming `review complete` or `no findings`, use `Review Check 1`, `Review Check 2`, and `Review Check 3` for artifact coverage, finding severity and routing, validation evidence, and remaining gaps; then apply `superpowers-verification-before-completion`.

Use `internal-code-review` for code defects and `internal-high-level-review` for architecture, workflow, cross-cutting impact, operational fit, and blind spots. Security-specific gaps follow the Future Security Lens rule in `references/wrapper-alignment.md`.

## Staged Checkpoints

- `plan-only` stops after the plan, Decision Brief, required critical pass for non-trivial or governance-sensitive plans, and next-step package.
- `full-cycle` may continue only through visible phase changes and the required pre-execute checkpoint; the entrypoint name alone does not skip that checkpoint.
- Any request-change realignment reruns Gate 0 before the next governance-sensitive plan output, recommendation, phase transition, or edit.
- `apply-plan` stops for missing retained plans, inline plans without checkpoint, or blockers that `internal-executing-plans` identifies.
- `review` routes each actionable finding to delivery, planning, critical challenge, or defer.

## References

- Read references on demand with targeted sections, not as a default bundle.
- Read `references/mode-contracts.md` for detailed mode boundaries, ownership maps, support activation rules, and medium-task thresholds.
- Read `references/workflow-maps.md` when documenting or validating quick, planned, and audited workflows.
- Read `references/wrapper-alignment.md` when updating Copilot agent wrappers, runtime portability claims, imported support, future security lens posture, output projection, or tests.
- Load `internal-high-level-review` when completion checks need a full workflow audit.

## Validation

- The selected entry point and active phase are explicit, or the workflow safely falls back to `plan`.
- Every staged phase includes owner, scope, anti-scope, action, validation, risk, and next checkpoint or decision.
- `internal-agent-support-next-step` is used for every user-visible transition.
- `apply-plan` uses `internal-executing-plans`, requires source-item ledger coverage for non-trivial retained plans, and excludes `questions.md`.
- Phase-ending reports state `Lessons` status even when no lesson was retained.
- `review` mode uses the relevant review lens instead of cloning `internal-code-review`, `internal-high-level-review`, or future security-review playbooks.
- Gate 0 blocks plan output, phase transition, or action when user decisions can change scope, owner, target state, validation, rollout, or anti-scope; `grill-me` supplies only the self-contained interview pattern.
- Imported support follows `references/wrapper-alignment.md` and is never a mandatory engine for gateway phases.
- Critical challenge is visible and owned by `internal-gateway-critical-master`.
- Copilot wrapper agents remain wrappers and do not re-list long workflow tables owned by this skill or its references.
