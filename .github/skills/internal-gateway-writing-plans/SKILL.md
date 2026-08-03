---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs an approved implementation plan written from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

## Referenced skills

- `/superpowers-writing-plans`: imported drafting mechanics only; this gateway
  owns eligibility, retained-plan requirements, review, and handoff.
- `/internal-gateway-execute-plans`: required next owner after human review and
  explicit execution approval.

## When to use

- Use after the user approves implementation-plan writing from an approved
  design or reviewed retained spec.

## When not to use

- Retained-spec writing stays in the brainstorming lane.
- Route same-chat work, plan review, plan execution, and imported
  `superpowers-*` maintenance to their existing owners.

## Contract

0. Establish writing eligibility before any drafting. `Critical Challenge Gate:
   accepted` authorizes plan writing only when it is supplied by
   `/internal-gateway-idea`. A direct invocation of this gateway requires
   explicit user approval in the current conversation. Neither path authorizes
   plan execution, status creation, or Git mutation.
1. Capture the target, anti-scope, nearest owner, validation path, stop
   conditions, and observable acceptance. Build a control inventory before
   delegation: classify every task, acceptance criterion, and declared
   `manual_obligation` exactly once as `automatable-local`,
   `observable-runtime`, `external-capability`, `authority-or-scope`, or
   `genuine-human-judgment`. Require an explicit `- No Git mutation.` bullet
   under `## Global Constraints` and a compact `## Control Inventory` in every
   current plan. Completion: all six facts, the no-mutation rule, and one owner
   for every obligation are recorded before delegation.
2. Produce one reviewable retained plan under `tmp/superpowers/plans/` with
   ordered actionable tasks, concrete file targets, focused validation, a
   compact `## Control Inventory`, and an execution handoff. Imported
   `/superpowers-writing-plans` mechanics may assist drafting but do not own
   approval eligibility or handoff. Each inventory row records a stable ID,
   preserved requirement, nearest owner, command or trigger, pass/fail signal,
   evidence, and safe fallback or authority boundary. Link local/runtime rows
   to `validations` and residual external/human rows to the existing contract
   fields; the inventory is traceability, not a second parser contract. When
   plan-writing or execution delegation is used, include the external
   `model-selection` acceptance evidence in `manual_obligations`. Treat
   `genuine-human-judgment` rows as explicit offline review follow-up; they are
   reported after a successful `DONE` closeout and do not block completion.
   Authority and approval rows remain pre-execution gates. Completion: one
   plan exists at the retained path and contains those artifact properties plus
   one versioned `## Execution Contract` fenced JSON object.
3. Perform human review for task actionability, approved scope, focused
   validation, control coverage, safety, and handoff quality. Every
   `automatable-local` or `observable-runtime` row must map to a required
   executable validation. An `external-capability` row must have an explicit
   probe and safe fallback, or a declared residual external obligation.
   `authority-or-scope` and `genuine-human-judgment` rows must remain explicit
   authority or human obligations; human judgment is verified offline after
   successful execution, while authority and approval remain pre-execution
   gates. A user assertion cannot substitute for a technical gate. The
   contract must declare native authoritative validation
   commands and phases, equivalence policy, manual obligations, and authority
   boundaries. A local/runtime gate must fail when its requirement is violated;
   a warning or printout is not a gate. It must not predict runtime discovery
   results or recovery candidates. Completion: each review concern and control
   row is accepted or has a recorded revision.
4. Report the retained plan path, name `/internal-gateway-execute-plans` as
   the only next owner, and wait for explicit execution approval. Do not invoke
   execution, create a status sibling, or offer an imported execution owner
   before that approval. Completion: the path and next owner are reported and
   execution has not started without approval.

## Command Portability

- Write every baseline, focused, and final validation command in directly
  executable native form. The command recorded in the plan is the
  authoritative command and evidence label.
- Do not make `rtk`, `graphify`, or another optional accelerator a prerequisite
  or command prefix unless the task's actual subject is that tool.
- Executor-side optimization may accelerate an invocation, but must not alter
  the recorded authoritative command or its validation meaning.

The executor owns the single mechanical plan validator. Do not add a
writer-local validator, draft-only lifecycle, or duplicate parser contract.
Before handoff, run the executor-owned `preflight` against the written current
plan and revise it until there are zero blocking findings. Explicitly
`legacy/imported` material is the only reconstruction path; it is not a current
plan exemption and requires refreshed approval and fingerprint. Plans without
the versioned contract are not actionable. Do not leave an automatable
obligation as narrative-only evidence or downgrade it to a manual obligation
to make preflight or closeout pass.

## Subagent model selection

Before any plan-writing or plan-execution delegation, probe whether
`gpt-5.6-luna` is available at `max` reasoning. If unavailable, select the
least expensive available model suitable for the specific task and record the
timestamp and context, probe and availability result, selected model,
reasoning level, suitability evidence, and cost/fallback rationale. The known
drafting fallback is `gpt-5.6-terra` at `high` reasoning, not a guarantee. Luna's
absence alone is not a blocker when fallback evidence is complete; lack of a
suitable approved fallback is.

## No-Commit Rule

- Never run `git add`, `git commit`, `git push`, or another Git mutation while
  writing or handing off a plan. This boundary also applies to any plan-writing
  or execution subagent. Retained artifacts stay uncommitted for user review
  unless the user explicitly requests commit help.
- Do not put Git mutation steps or default commit advice in the produced plan.

## Validation

- Confirm the delegated plan has ordered tasks, concrete file targets, focused
  validation, clear scope and safety boundaries, and no duplicate owner.
- Confirm the handoff names `/internal-gateway-execute-plans` and waits for
  explicit approval.
- Run `git diff --check` and confirm no Git mutation occurred.
