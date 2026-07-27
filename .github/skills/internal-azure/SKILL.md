---
name: internal-azure
description: Official entry point for any Azure task. Routes every Azure request to the right specialist - organization structure, governance, operations, or Azure DevOps - or to internal-azure-strategic for high-level decision framing. Use for any Azure request, scoped or ambiguous.
---

# Internal Azure

Official entry point and lightweight router for Azure work. This skill routes; it does not answer Azure domain questions itself.

## When to use

Use this skill as the entry point for any Azure request, scoped or ambiguous. It always routes: to one specialist when the owner is clear, to `internal-azure-strategic` for cross-domain ambiguity or high-level decision framing before implementation.

## Destinations

| To | Owns |
|---|---|
| `internal-azure-organization-structure` | tenant, management-group, subscription, landing-zone, platform topology |
| `internal-azure-governance` | RBAC, managed identity, PIM, Policy, tagging, guardrails |
| `internal-azure-operations` | monitoring, validation, backup, Site Recovery, reporting, evidence |
| `internal-azure-devops` | Azure DevOps pipelines and project automation |
| `internal-azure-strategic` | high-level decision support, tradeoff framing, multi-lens analysis |
| `awesome-copilot-azure-pricing` | Azure-specific pricing depth when cost data is the primary problem |

## How to route

1. Read the request. If it is clearly scoped to one specialist, name that owner. If it is ambiguous, spans multiple domains, or asks for decision framing before implementation, name `internal-azure-strategic`. Ask one clarifying question only when ownership turns on the answer.
2. Hand off by reading the chosen skill's `SKILL.md` and adopting its instructions for the rest of the turn. Handoff by file read works regardless of the target's disable-model-invocation flag.
3. State the chosen owner and a one-line reason before handing off.

Load `references/routing-matrix.md` when the owner choice is not obvious.

## Rules

- Always route. Never answer an Azure domain question from this skill.
- Route directly when one specialist clearly owns the next step; use `internal-azure-strategic` only for genuine cross-domain ambiguity or decision framing.
- Pick the minimum specialist set; one primary owner per lane.
- Every destination except `awesome-copilot-azure-pricing` carries `disable-model-invocation: true`; reach it by this handoff or explicit manual invocation only.
- Do not retain ownership after the lane is resolved.

## Validation

- The chosen owner is named with a one-line reason.
- The handoff is performed by reading the owner's SKILL.md, not by answering here.
- The selected specialist set is the minimum needed.
