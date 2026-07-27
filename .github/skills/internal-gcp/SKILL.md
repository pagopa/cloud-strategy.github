---
name: internal-gcp
description: Official entry point for any Google Cloud task. Routes every GCP request to the right specialist - organization structure, governance, or operations - or to internal-gcp-strategic for high-level decision framing. Use for any Google Cloud request, scoped or ambiguous.
---

# Internal GCP

Official entry point and lightweight router for Google Cloud work. This skill routes; it does not answer GCP domain questions itself.

## When to use

Use this skill as the entry point for any Google Cloud request, scoped or ambiguous. It always routes: to one specialist when the owner is clear, to `internal-gcp-strategic` for cross-domain ambiguity or high-level decision framing before implementation.

## Destinations

| To | Owns |
|---|---|
| `internal-gcp-organization-structure` | org, folder, project, billing-account, Shared VPC, platform topology |
| `internal-gcp-governance` | IAM, workload identity, service account, Org Policy, guardrails |
| `internal-gcp-operations` | monitoring, validation, backup, recovery, inventory, reporting, evidence |
| `internal-gcp-strategic` | high-level decision support, tradeoff framing, multi-lens analysis |

## How to route

1. Read the request. If it is clearly scoped to one specialist, name that owner. If it is ambiguous, spans multiple domains, or asks for decision framing before implementation, name `internal-gcp-strategic`. Ask one clarifying question only when ownership turns on the answer.
2. Hand off by reading the chosen skill's `SKILL.md` and adopting its instructions for the rest of the turn. Handoff by file read works regardless of the target's disable-model-invocation flag.
3. State the chosen owner and a one-line reason before handing off.

Load `references/routing-matrix.md` when the owner choice is not obvious.

## Rules

- Always route. Never answer a GCP domain question from this skill.
- Route directly when one specialist clearly owns the next step; use `internal-gcp-strategic` only for genuine cross-domain ambiguity or decision framing.
- Pick the minimum specialist set; one primary owner per lane.
- Every destination carries `disable-model-invocation: true`; reach it by this handoff or explicit manual invocation only.
- Do not retain ownership after the lane is resolved.

## Validation

- The chosen owner is named with a one-line reason.
- The handoff is performed by reading the owner's SKILL.md, not by answering here.
- The selected specialist set is the minimum needed.
