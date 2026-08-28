---
name: internal-github-operations
description: Use when /internal-github routes a GitHub operational request covering Actions health, runners, audit evidence, reporting, drift, preflight, rollout validation, or post-rollout proof.
---

# Internal GitHub Operations

Validate, observe, and operationalize an existing GitHub platform change.
Treat workflow behavior, runner health, audit evidence, and reporting as
separate signals that must be tied to the requested proof.

## When to use

Use when the requested deliverable is operational evidence, rollout proof,
runner or workflow health, audit evidence, reporting, or drift validation.

## Evidence workflow

1. State the operational objective, affected surface, and rollout unit.
2. Define preflight checks proportional to blast radius, including permission,
   environment, runner, workflow, audit, and reporting signals as relevant.
3. State what is confirmed, what is inferred, and what still needs a real
   test.
4. Validate the first safe rollout unit and record both success signals and
   unexpected permission, runner, or release regressions.
5. Define the rollback trigger and owner before widening rollout.
6. Collect post-rollout evidence for the workflow, runner, audit, and drift
   signals that prove the requested behavior.

## Operational rules

- Keep workflow success distinct from runner health and permission proof.
- Keep audit and reporting evidence tied to the decision that needs
  confirmation.
- Use current GitHub documentation when Actions behavior, runner support,
  audit capability, reporting export, or platform validation details can
  change the result.
- When querying GitHub security alert endpoints with `gh api`, force
  `--method GET` or encode filters in the query string. Form fields such as
  `-f state=open` without an explicit GET can produce misleading `404`
  responses.

Load `references/validation-and-evidence.md` when a deeper checklist is
needed.

## Completion criteria

- Confirmed and inferred evidence are separated.
- Rollout unit and rollback trigger are explicit for risky changes.
- Runner, workflow, audit, and permission signals match the affected surface.
- Post-rollout proof and any drift follow-up are stated.
- Continuity assumptions are included only when build, release, or repository
  criticality is in scope.
