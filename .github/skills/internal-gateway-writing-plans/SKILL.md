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
   conditions, and observable acceptance. Keep the no-version-control-mutation
   rule in scope. Completion: all six facts and the no-mutation rule are
   recorded before delegation.
2. Load `/superpowers-writing-plans` and produce one reviewable retained plan
   under `tmp/superpowers/plans/` with ordered actionable tasks, concrete file
   targets, focused validation, and an execution handoff. Completion: one plan
   exists at the retained path and contains those four artifact properties.
3. Perform human review for task actionability, approved scope, focused
   validation, safety, and handoff quality. Treat descriptive metadata as
   review guidance, not as a writer-owned machine acceptance state. Completion:
   each review concern is accepted or has a recorded revision.
4. Report the retained plan path, name `/internal-gateway-execute-plans` as
   the next owner, and wait for explicit execution approval. Completion: the
   path and next owner are reported and execution has not started without
   approval.

The executor owns the single mechanical plan validator. Do not add a
writer-local validator, draft-only lifecycle, or duplicate parser contract.

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
