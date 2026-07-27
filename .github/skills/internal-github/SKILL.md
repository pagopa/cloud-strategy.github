---
name: internal-github
description: Official entry point for any GitHub task. Routes every GitHub request to the right specialist - governance, operations, Actions workflows, composite actions, PR lifecycle, or Copilot platform research - or to internal-github-strategic for high-level decision framing. Use for any GitHub request, scoped or ambiguous.
---

# Internal GitHub

Official entry point and lightweight router for GitHub work. This skill routes; it does not answer GitHub domain questions itself.

## When to use

Use this skill as the entry point for any GitHub request, scoped or ambiguous. It always routes: to one specialist when the owner is clear, to `internal-github-strategic` for cross-domain ambiguity or high-level platform or operating-model decision framing.

## Destinations

| To | Owns |
|---|---|
| `internal-github-governance` | rulesets, branch protection, repo and org permissions, GitHub Apps permissions, Actions permissions, OIDC, secrets, environments, Copilot governance |
| `internal-github-operations` | Actions health, runner operations, audit logs, reporting, drift, preflight, post-rollout validation, evidence |
| `internal-github-actions` | workflow authoring under `.github/workflows/`, reusable workflows, reuse-pattern selection |
| `internal-github-action-composite` | composite-action authoring under `.github/actions/`, input validation, shell safety, contract compatibility |
| `internal-github-pr` | PR creation, body, merge readiness, merge method, terminal-state verification, PR lifecycle evidence |
| `internal-copilot-docs-research` | current GitHub Copilot or MCP platform behavior when freshness materially affects the answer |
| `internal-github-strategic` | high-level platform and operating-model decision support, tradeoff framing, multi-lens analysis |

## How to route

1. Read the request. If it is clearly scoped to one specialist, name that owner. If it is ambiguous, spans multiple domains, or asks for platform or operating-model decision framing, name `internal-github-strategic`. Ask one clarifying question only when ownership turns on the answer.
2. Hand off by reading the chosen skill's `SKILL.md` and adopting its instructions for the rest of the turn. Handoff by file read works regardless of the target's disable-model-invocation flag.
3. State the chosen owner and a one-line reason before handing off.

Load `references/routing-matrix.md` when the owner choice is not obvious.

## Rules

- Always route. Never answer a GitHub domain question from this skill.
- Route directly when one specialist clearly owns the next step; use `internal-github-strategic` only for genuine cross-domain ambiguity or decision framing.
- Pick the minimum specialist set; one primary owner per lane.
- Every destination except `internal-copilot-docs-research` carries `disable-model-invocation: true`; reach it by this handoff or explicit manual invocation only.
- Do not retain ownership after the lane is resolved.

## Validation

- The chosen owner is named with a one-line reason.
- The handoff is performed by reading the owner's SKILL.md, not by answering here.
- The selected specialist set is the minimum needed.
