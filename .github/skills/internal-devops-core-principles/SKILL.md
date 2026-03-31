---
name: internal-devops-core-principles
description: DevOps culture, CALMS, DORA metrics, deployment flow, blameless operations, automation-first delivery, and value-stream thinking. Use when the task concerns CI/CD strategy, release process quality, platform delivery, DevOps operating models, or software-delivery health.
---

# Internal DevOps Core Principles

Use this skill for delivery-system thinking, not for one-off YAML syntax questions.

## Core Lens

Apply CALMS in this order:

1. Culture: shared ownership, blameless learning, clear handoffs.
2. Automation: remove repetitive human gates.
3. Lean: reduce queue time, handoffs, and batch size.
4. Measurement: use DORA and operational metrics.
5. Sharing: document runbooks, incidents, and patterns.

## Delivery Rules

- Prefer small, frequent, reversible changes.
- Optimize for lead time and mean time to recovery, not ceremony.
- Use automated checks as the default quality gate.
- Keep infrastructure and environment changes reproducible.
- Design rollouts for rollback, not just for first success.

## DORA Focus

Always consider:

- Deployment frequency
- Lead time for changes
- Change failure rate
- Mean time to recovery

If a workflow harms one of these, call it out explicitly.

## What Good Looks Like

- Fast feedback in pull requests and CI.
- Clear ownership from commit to production.
- Observable systems with actionable alerts.
- Release pipelines that are testable and repeatable.
- Post-incident learning that changes the system.

## Anti-Patterns

- Large release trains as the default.
- Manual copy-paste deployments.
- Approval chains with no measurable risk reduction.
- Hidden tribal knowledge for on-call or release steps.
- Treating DevOps as a team name instead of an operating model.

## Output Expectations

When giving guidance:

- State which CALMS and DORA concerns apply.
- Identify the current bottleneck.
- Recommend the minimum process and automation changes that improve flow.
