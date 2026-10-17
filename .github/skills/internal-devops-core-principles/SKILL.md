---
name: internal-devops-core-principles
description: Use when the task is about delivery-system strategy, release safety, operational readiness, or incident learning across the software-delivery lifecycle, not one-off workflow syntax or provider commands.
---

# Internal DevOps Core Principles

## When to use

- The task is about delivery-system strategy, release safety, operational
  readiness, or incident learning across the software-delivery lifecycle.
- The main need is DevOps tradeoff framing rather than one-off workflow syntax
  or provider-specific commands.
- A repository or platform decision must be evaluated through CALMS, DORA,
  rollout safety, or operational controls.

## Core lens

Apply CALMS in this order:

1. Culture: shared ownership, blameless learning, clear handoffs.
2. Automation: remove repetitive human gates.
3. Lean: reduce queue time, handoffs, and batch size.
4. Measurement: use DORA and operational metrics.
5. Sharing: document runbooks, incidents, and patterns.

## Delivery rules

- Prefer small, frequent, reversible changes.
- Optimize for lead time and mean time to recovery, not ceremony.
- Use automated checks as the default quality gate.
- Keep code, infrastructure, environments, builds, tests, releases, and
  deployments reproducible.
- Design rollouts for rollback, not just for first success.
- Prefer progressive delivery, feature flags, or other blast-radius controls
  over all-at-once production changes.
- Treat observability and incident readiness as delivery requirements, not as
  post-deploy chores.
- Use approvals only when they reduce measurable risk that automation cannot
  already cover.

## DORA focus

Always consider deployment frequency, lead time for changes, change failure
rate, and mean time to recovery. If a workflow harms one of these, call it out
explicitly.

## Anti-patterns

- Large release trains as the default.
- Manual copy-paste deployments.
- Green pipelines with no deployment verification or rollback rehearsal.
- Monitoring that creates noisy alerts with no operator action tied to them.
- Hidden release knowledge, on-call knowledge, or recovery steps.
- Approval chains with no measurable risk reduction.
- Treating DevOps as a team name instead of an operating model.

## Output expectations

When giving guidance:

- State which Infinity Loop phases plus CALMS and DORA concerns apply.
- Name the current bottleneck with its evidence.
- Identify missing controls in testing, release safety, deployment safety,
  operations, or observability when they matter, with supporting evidence.
- Recommend the minimum process and automation changes that improve flow,
  with the expected improvement stated.

## References

- [`references/practice-checklists.md`](references/practice-checklists.md):
  Infinity Loop scope, minimum operational controls, and what good looks like.
  Load the checklist matching the current lifecycle stage or control question.
