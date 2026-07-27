---
name: internal-github-governance
description: Use when /internal-github routes a GitHub governance decision covering rulesets, permissions, Apps, Actions permissions, OIDC trust, secrets, environments, CODEOWNERS, or Copilot policy.
user-invocable: false
---

# Internal GitHub Governance

Define or review GitHub permissions, guardrails, and policy decisions. Keep
enterprise or organization guardrails distinct from repository or environment
grants, and keep every control auditable.

## When to use

Use when the requested deliverable is a GitHub governance control, permission
boundary, trust design, exception path, or policy decision.

## Governance workflow

1. State the governance objective and exact scope: enterprise, organization,
   repository set, repository, or environment.
2. Select the preventive control, permission mechanism, or policy surface that
   matches the objective.
3. Name the trust boundary for Apps, Actions, OIDC, secrets, environments, or
   Copilot policy. State what actor receives access and what limits it.
4. Define the exception path, including owner, reason, duration, review date,
   and rollback where the control is not universal.
5. Verify current GitHub facts when ruleset capability, Apps permissions,
   Actions behavior, OIDC integration, or Copilot limits affect the answer.
6. Define rollout validation proportional to blast radius before enabling the
   control broadly.

## Control rules

- Keep `CODEOWNERS` entries explicit about source, template, or consumer
  ownership.
- Allow `@your-org/platform-governance-team` only in template repositories;
  consumer repositories must replace it before review enforcement.
- Prefer GitHub Apps or OIDC federation over long-lived personal tokens or
  static cloud secrets unless a proven constraint requires otherwise.
- Keep Copilot entitlement and governance explicit when they differ from
  repository permissions.

Load `references/guardrail-map.md` when the correct governance surface or
trust boundary needs comparison.

## Completion criteria

- Scope and governance objective are explicit.
- The selected control mechanism and its preventive effect are clear.
- The trust boundary and actor permissions are named.
- The exception path is actionable and auditable.
- Current-fact dependencies are identified.
- Rollout validation need and rollback trigger are stated for risky changes.
