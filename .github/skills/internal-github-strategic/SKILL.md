---
name: internal-github-strategic
description: Use when the user needs high-level GitHub platform decision support, option framing, or tradeoff analysis before implementation. This skill helps evaluate GitHub operating-model choices, clarify assumptions, and recommend a direction using only the lenses that matter for the current request while using current GitHub documentation only when freshness materially affects the answer.
---

# Internal GitHub Strategic

Use this skill when the main need is to reason about a GitHub platform decision before implementation.

This is a strategic support skill. It helps frame the decision, compare realistic options, expose tradeoffs, and recommend a direction. It does not implement the change and it does not choose Terraform, Python, or Bash on behalf of the user.

This skill absorbs light structure concerns such as enterprise, organization, and repository model choices. Do not force a separate structure lane unless a future boundary clearly emerges.

## When to use

- The user needs GitHub decision support before execution.
- Multiple GitHub approaches are credible and tradeoffs matter.
- The user wants a recommendation grounded in current GitHub guidance.
- The user wants high-level support for enterprise, org, repo, Apps, Actions, runner, Copilot, or spend decisions.

## When not to use

- The task is already a clear implementation change.
- The user only needs detailed ruleset, permission, OIDC, secret, or runner-operation implementation.
- The task is purely post-rollout validation or evidence gathering.
- The request is narrow and operational with no real decision to frame.

## Main domains covered

- enterprise, organization, and repository model decision framing
- mono-repo versus multi-repo tradeoffs when relevant
- GitHub Apps strategy
- GitHub Actions strategy
- runner strategy at decision level
- Copilot direction and governance implications at decision level
- licensing, spend, and cost-value implications at decision level
- operational and governance implications at decision level

## Optional lens activation

Do not load every lens by default.

Use only the minimum set of lenses needed for the request. If the user explicitly names one or more lenses, prioritize only those. If the user does not name lenses, infer the smallest useful set.

Available lenses include:

- security
- identity and access
- governance
- operations
- runner model
- Copilot
- BC/DR
- FinOps
- compliance
- rollout and rollback
- blast radius
- maintainability

Rules:

- Start narrow.
- Expand only when the request is broad, risky, or ambiguous.
- If another lens would materially improve the recommendation, suggest it briefly instead of forcing it.
- Keep the active lenses explicit when more than one is in play.

Load `references/lens-playbook.md` when the user wants a deeper framing aid or when the choice of lenses is not obvious.

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about delivery continuity, runner resilience, backup, recovery, or failover expectations
- the decision has clear continuity implications for build, release, or repository operations
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use current GitHub documentation only when freshness materially affects the answer, especially for GitHub Apps permissions, Actions behavior, runner support, OIDC guidance, rulesets, or Copilot product boundaries.

Do not invoke current-doc research by default for stable, generic reasoning.

## Mandatory behavior

- Identify the decision first, not the implementation tool.
- Make assumptions explicit.
- Compare realistic options, not strawmen.
- Keep tradeoffs concrete.
- Surface material risk, blast radius, and reversibility when relevant.
- Include cost-value considerations when they matter to the decision.
- Stay proportional to the size of the question.

## Adaptive output modes

Choose the lightest output that fits the request.

### Quick answer

Use for narrow asks.

Include:

- direct recommendation
- short rationale
- optional risk or follow-up note

### Decision note

Use for normal strategic support.

Include:

- decision statement
- key options or tradeoff
- recommended direction
- main risk or validation note

### Deep analysis

Use only for broad, ambiguous, high-risk, or explicitly detailed requests.

Include:

- context and assumptions
- options considered
- active lenses used
- recommendation and why it wins
- main risks and blast radius
- validation or follow-up path

## Relationship to adjacent skills

- `internal-github-governance`
  Use when the next need is rulesets, permissions, OIDC, secret posture, environments, or Copilot guardrail definition.
- `internal-github-operations`
  Use when the next need is Actions health, runner validation, audit evidence, reporting, drift checks, or post-rollout checks.
- `internal-cicd-workflow`, `internal-script-python`, `internal-script-bash`
  Use when the decision is settled and implementation begins.

## Anti-patterns

- forcing a full multi-lens analysis for a small question
- treating BC/DR as mandatory for every answer
- recommending a direction without current-source verification when freshness matters
- confusing decision support with implementation guidance
- expanding into tool selection when the user did not ask for it
- forcing GitHub into a cloud-provider structure pattern when the boundary is weaker
