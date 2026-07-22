---
name: internal-github-governance
description: Use when the user needs GitHub guardrail or permission guidance — rulesets, branch protection, repository or organization permissions, GitHub Apps permissions, Actions permissions, OIDC posture, secret handling, environments, or Copilot governance — after the broad operating model is known. Do not use for enterprise, org, or repo-model decision framing; route those to internal-github.
---

# Internal GitHub Governance

## Referenced skills

- `internal-github`: route back when enterprise, org, repo, or operating-model direction is still unsettled and the owning specialist is not yet clear.
- `internal-github-operations`: route runner health, reporting, audit evidence, drift checks, or post-rollout validation.

Use this skill when the next need is to define or review GitHub permissions, guardrails, and policy decisions.

This skill owns governance logic after the broad operating model is known. It helps separate enterprise or org guardrails from repo or environment grants and keeps permission decisions auditable.

## When to use

- The user needs ruleset, branch protection, or repository permission guidance.
- The user needs GitHub Apps permission, Actions permission, or OIDC posture guidance.
- The user needs secret, environment, or Copilot governance guidance.
- The user needs a review of guardrail design, exceptions, or access governance.

## When not to use

- The main problem is enterprise, org, repo, or mono-repo versus multi-repo decision framing.
- The main problem is runner health, reporting, audit evidence, or post-rollout validation.
- The task is implementation-only.

## Main domains covered

- rulesets and branch protection
- CODEOWNERS review ownership and placeholder-owner readiness
- repository and organization permissions model
- GitHub Apps permissions
- GitHub Actions permissions
- OIDC posture
- secret and environment guardrails
- Copilot governance
- exception handling at governance level

## Core rules

- Keep org-level guardrails distinct from repo or environment grants.
- Keep `CODEOWNERS` entries explicit enough that reviewers can tell whether a rule is source-owned, template-owned, or consumer-owned.
- Allow `@your-org/platform-governance-team` only in template repositories; consumer repositories must replace that placeholder before review enforcement.
- Prefer GitHub Apps or OIDC-based federation over long-lived personal tokens or static cloud secrets unless there is a proven reason not to.
- Make scope explicit: enterprise, organization, repository set, or environment.
- Make exception handling explicit when a control is not universal.
- Keep Copilot governance separate from generic repository permissions when policy or licensing posture differs.

Load `references/guardrail-map.md` when the correct governance surface is ambiguous or when the user needs a deeper split between rulesets, permissions, Apps, Actions, OIDC, and environments.

## Use of current facts

Use current GitHub documentation when the answer depends on current ruleset capability, GitHub Apps permissions, Actions permission behavior, OIDC integration guidance, or Copilot governance limits.

## Output expectations

For narrow asks, return:

- recommended governance mechanism
- short reason
- main risk or validation note

For broader asks, return:

- governance objective
- scope
- candidate mechanisms
- recommended control stack
- exception or blast-radius note
- what should be validated before rollout

## Relationship to adjacent skills

- `internal-github`
  Use first when the user still needs option framing, repo-model tradeoffs, or operating-model decisions.
- `internal-github-operations`
  Use when the next need is preflight, audit evidence, drift checks, or validation after the governance design is chosen.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating permissions as if they automatically imply the right branch or environment guardrails | Authorization and workflow controls get conflated | Pair permissions with the rulesets, environments, or approvals that actually constrain risky actions |
| Answering a governance question without naming scope | Enterprise, organization, repository, and environment scopes behave differently | State the exact scope before recommending a mechanism |
| Mixing org-wide guardrails and repository-level exceptions into one vague recommendation | Reviewers cannot see what is standard versus exceptional | Separate the baseline control from the exception path and its owner |
| Proposing OIDC, Apps, or secret posture without naming trust boundaries | Automation trust becomes broad and hard to audit | Name what actor gets access, what boundary limits it, and what evidence must exist |
| Recommending rollout without staged validation when the blast radius is high | Ruleset, permission, or environment errors can block delivery quickly | Use scoped rollout, validation, and explicit rollback triggers before widening |
| Treating Copilot governance as identical to general repository permissions | Policy, licensing, and visibility needs may differ | Keep Copilot entitlement and governance posture explicit when they diverge from repo permissions |

## Validation

- Confirm the governance scope is explicit: enterprise, organization, repository set, or environment.
- Confirm the recommended mechanism is clear about whether it prevents, grants, or constrains automation.
- Confirm trust boundaries are explicit for Apps, Actions, OIDC, secrets, or Copilot policy choices.
- Confirm staged rollout validation is named before high-blast-radius ruleset, permission, or environment changes.
- Confirm the answer says when operational proof should move to `internal-github-operations`.
- Before enabling CODEOWNERS-backed review enforcement in a consumer repository, confirm no template placeholder owner remains.
