---
name: internal-github
description: Use only when a GitHub task cannot be routed confidently to a specific GitHub skill because the request is materially ambiguous, has multiple GitHub domains with no clear primary owner, or requires clarification before selecting the correct specialist. Do not use for clearly scoped governance, operations, PR lifecycle, Actions workflow authoring, composite-action authoring, or current Copilot platform behavior research.
---

# Internal GitHub

Fallback router for GitHub tasks that cannot be assigned confidently to one specialist. Do not activate only because the task concerns GitHub; activate only when material routing uncertainty blocks owner selection.

## Referenced skills

- `internal-github-governance`: rulesets, branch protection, repository and organization permissions, GitHub Apps permissions, Actions permissions, OIDC posture, secrets, environments, Copilot governance.
- `internal-github-operations`: Actions health, runner operations, audit logs, reporting, drift checks, preflight checks, post-rollout validation, operational evidence.
- `internal-github-actions`: GitHub Actions workflow authoring under `.github/workflows/`, reusable workflows, reuse-pattern selection.
- `internal-github-action-composite`: composite-action authoring under `.github/actions/`, input validation, shell safety, contract compatibility.
- `internal-github-pr`: PR creation, body, merge readiness, merge method, terminal-state verification, PR lifecycle evidence.
- `internal-copilot-docs-research`: current GitHub Copilot or MCP platform behavior research when freshness materially affects the answer.

## When to use

- Material ambiguity prevents selecting one primary GitHub specialist.
- Multiple GitHub domains are material and no primary owner can be identified safely.
- The user explicitly invokes `$internal-github`.
- The task asks which GitHub lane should own the work before requesting a domain solution.

## Routing threshold

Activate only when at least one holds:

- the request is materially ambiguous and clarification is required before a GitHub owner can be selected;
- multiple GitHub domains are material and no primary owner can be identified safely;
- the task asks which GitHub problem-solving lane should own the work.

Explicit `$internal-github` invocation remains valid.

## Handoffs

| To | Owns |
|---|---|
| `internal-github-governance` | rulesets, branch protection, repo and org permissions, GitHub Apps permissions, Actions permissions, OIDC, secrets, environments, Copilot governance |
| `internal-github-operations` | Actions health, runner operations, audit logs, reporting, drift, preflight, post-rollout validation, evidence |
| `internal-github-actions` | workflow authoring under `.github/workflows/`, reusable workflows, reuse-pattern selection |
| `internal-github-action-composite` | composite-action authoring under `.github/actions/`, input validation, shell safety, contract compatibility |
| `internal-github-pr` | PR creation, body, merge readiness, merge method, terminal-state verification, PR lifecycle evidence |
| `internal-copilot-docs-research` | current GitHub Copilot or MCP platform behavior when freshness materially affects the answer |

## Dispatch contract

1. State the routing uncertainty.
2. Identify the candidate GitHub owners.
3. Select the minimum specialist set.
4. Keep strategic comparison here only while it is needed to choose the owner.
5. Hand the resolved task to the primary specialist instead of retaining ownership.

## On-demand references

Load `references/routing-matrix.md` for the routing decision tree. Load `references/strategic-framing.md` when the fallback trigger fires and the choice of GitHub owner needs structured decision framing, optional lenses, or worked-shape comparison before handoff. Do not load either by default for a clearly scoped single-owner request.

## Optional lens activation

Do not load every lens by default.

Use only the minimum set of lenses needed for the request. If the user explicitly names one or more lenses, prioritize only those. If the user does not name lenses, infer the smallest useful set.

Available lenses include:

- security
- identity and access
- organization and repo model
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

## Use of current documentation

Use current GitHub documentation only when freshness materially affects the answer. When the question is about Copilot or MCP behavior specifically, route to `internal-copilot-docs-research` instead of answering from memory.

## Anti-scope

- Do not use this fallback for a clearly scoped ruleset, permission, OIDC, secret, environment, or Copilot governance request. Route directly to `internal-github-governance`.
- Do not use this fallback for Actions health, runner operations, audit log, drift, preflight, or post-rollout validation. Route directly to `internal-github-operations`.
- Do not use this fallback for workflow authoring, reusable workflow design, or reuse-pattern selection. Route directly to `internal-github-actions`.
- Do not use this fallback for composite-action authoring or contract changes under `.github/actions/`. Route directly to `internal-github-action-composite`.
- Do not use this fallback for PR creation, body, merge readiness, or lifecycle evidence. Route directly to `internal-github-pr`.
- Do not use this fallback when the only unresolved question is current Copilot or MCP platform behavior. Route directly to `internal-copilot-docs-research`.

## Anti-patterns

- Activating this fallback when one specialist clearly owns the next step.
- Forcing a full multi-lens analysis for a small question.
- Answering a governance, operations, or workflow question here instead of handing it to the specialist.
- Keeping ownership after the lane is resolved instead of handing off.
- Recommending implementation tooling when the user only asked for routing.
- Invoking current-doc research by default for stable, generic reasoning.

## Validation

- State why the request could not be assigned to one primary GitHub specialist.
- Confirm the selected specialist set is the minimum needed to resolve the uncertainty.
- Confirm the resolved task is handed to a primary specialist and not retained by this fallback.
- Confirm assumptions, tradeoffs, and the next owner are explicit.
- Confirm lenses, when used, are the minimum set and named explicitly when more than one is active.
