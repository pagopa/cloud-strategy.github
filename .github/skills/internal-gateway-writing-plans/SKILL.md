---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs an approved implementation plan written from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

## Referenced skills

- `/superpowers-writing-plans`: required owner for producing the retained plan.
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

1. Capture the target, anti-scope, nearest owner, validation path, stop
   conditions, and observable acceptance. Build a control inventory before
   delegation: classify every task, acceptance criterion, and declared
   `manual_obligation` exactly once as `automatable-local`,
   `observable-runtime`, `external-capability`, `authority-or-scope`, or
   `genuine-human-judgment`. Keep the no-version-control-mutation rule in
   scope. Completion: all six facts, the no-mutation rule, and one owner for
   every obligation are recorded before delegation.
2. Load `/superpowers-writing-plans` and produce one reviewable retained plan
   under `tmp/superpowers/plans/` with ordered actionable tasks, concrete file
   targets, focused validation, a compact `## Control Inventory`, and an
   execution handoff. Each inventory row records a stable ID, preserved
   requirement, nearest owner, command or trigger, pass/fail signal, evidence,
   and safe fallback or authority boundary. Link local/runtime rows to
   `validations` and residual external/human rows to the existing contract
   fields; the inventory is traceability, not a second parser contract.
   Completion: one plan exists at the retained path and contains those
   artifact properties plus one versioned `## Execution Contract` fenced JSON
   object.
3. Perform human review for task actionability, approved scope, focused
   validation, control coverage, safety, and handoff quality. Every
   `automatable-local` or `observable-runtime` row must map to a required
   executable validation. An `external-capability` row must have an explicit
   probe and safe fallback, or a declared residual external obligation.
   `authority-or-scope` and `genuine-human-judgment` rows must remain explicit
   authority or human obligations; a user assertion cannot substitute for a
   technical gate. The contract must declare native authoritative validation
   commands and phases, equivalence policy, manual obligations, and authority
   boundaries. A local/runtime gate must fail when its requirement is violated;
   a warning or printout is not a gate. It must not predict runtime discovery
   results or recovery candidates. Completion: each review concern and control
   row is accepted or has a recorded revision.
4. Report the retained plan path, name `/internal-gateway-execute-plans` as
   the next owner, and wait for explicit execution approval. Completion: the
   path and next owner are reported and execution has not started without
   approval.

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
Before handoff, run the executor-owned `preflight` against the written plan and
revise it until there are zero blocking findings. Plans without the versioned
contract are not actionable. Do not leave an automatable obligation as
narrative-only evidence or downgrade it to a manual obligation to make
preflight or closeout pass.

## No-Commit Rule

- Never run `git add`, `git commit`, `git push`, or another Git mutation while
  writing or handing off a plan. Retained artifacts stay uncommitted for user
  review unless the user explicitly requests commit help.
- Do not put Git mutation steps or default commit advice in the produced plan.

## Validation

- Confirm the delegated plan has ordered tasks, concrete file targets, focused
  validation, clear scope and safety boundaries, and no duplicate owner.
- Confirm the handoff names `/internal-gateway-execute-plans` and waits for
  explicit approval.
- Run `git diff --check` and confirm no Git mutation occurred.
