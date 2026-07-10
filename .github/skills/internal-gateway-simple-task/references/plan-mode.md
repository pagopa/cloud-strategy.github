# Simple Task Plan Recommendation

Use this reference when same-run execution should stop and a retained plan should be recommended instead.

## Core Rule

This bundle does not write retained plans. It detects when same-run execution is no longer economical or safe, explains why, and stops so the user can choose whether to create a plan.

## Triggers

Recommend a plan when one or more of these signals is present:

- the user explicitly asks for a plan
- the task needs more than roughly 5-7 concrete executable steps
- the task touches more than roughly 3 unrelated files or path families
- the task has multiple independent validators
- the task depends on external approvals, credentials, or third-party state
- the task risks context pressure before validation can complete
- the work centers on large exports, tables, logs, or broad mechanical change

## Procedure

1. Classify the cost or complexity signal.
2. Explain why same-run execution is unsafe or uneconomical.
3. Ask the user whether to create a retained plan.
4. Stop without writing one.

## Token Budget Gate

When the main signal is context pressure, keep evidence compact before stopping:

- prefer bounded summaries over raw dumps
- avoid broad scans and repeated output bursts
- name the likely context impact before any expensive expansion

## Stop Output

When recommending a plan, report:

- `why stopped`
- `cost or complexity signal`
- `user decision needed`
- `evidence required before execution can continue`

## Boundaries

- Do not use plan recommendation to hide ambiguity about the target state.
- Do not continue same-run execution after deciding that a plan is needed.
- Do not write the retained plan from this bundle.
