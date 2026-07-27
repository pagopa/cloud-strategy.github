---
name: internal-aws
description: Official entry point for any AWS task. Routes every AWS request to the right specialist - organization structure, governance, operations, Lambda, or AWS documentation research - or to internal-aws-strategic for high-level decision framing. Use for any AWS request, scoped or ambiguous.
---

# Internal AWS

Official entry point and lightweight router for AWS work. This skill routes; it does not answer AWS domain questions itself.

## When to use

Use this skill as the entry point for any AWS request, scoped or ambiguous. It always routes: to one specialist when the owner is clear, to `internal-aws-strategic` for cross-domain ambiguity or high-level decision framing before implementation.

## Destinations

| To | Owns |
|---|---|
| `internal-aws-organization-structure` | account, OU, delegated admin, StackSets, platform network topology |
| `internal-aws-governance` | IAM, trust, SCP, federation, guardrails |
| `internal-aws-operations` | monitoring, validation, backup, recovery, reporting, evidence |
| `internal-aws-lambda` | Lambda runtime, handler, trigger, packaging, retry |
| `internal-aws-mcp-research` | current AWS documentation and safe IAM inspection |
| `internal-aws-strategic` | high-level decision support, tradeoff framing, multi-lens analysis |
| `antigravity-aws-cost-optimizer` | AWS-specific cost analysis when cost data is the primary problem |

## How to route

1. Read the request. If it is clearly scoped to one specialist, name that owner. If it is ambiguous, spans multiple domains, or asks for decision framing before implementation, name `internal-aws-strategic`. Ask one clarifying question only when ownership turns on the answer.
2. Hand off by reading the chosen skill's `SKILL.md` and adopting its instructions for the rest of the turn. Handoff by file read works regardless of the target's disable-model-invocation flag.
3. State the chosen owner and a one-line reason before handing off.

Load `references/routing-matrix.md` when the owner choice is not obvious.

## Rules

- Always route. Never answer an AWS domain question from this skill.
- Route directly when one specialist clearly owns the next step; use `internal-aws-strategic` only for genuine cross-domain ambiguity or decision framing.
- Pick the minimum specialist set; one primary owner per lane.
- Every destination except `antigravity-aws-cost-optimizer` carries `disable-model-invocation: true`; reach it by this handoff or explicit manual invocation only.
- Do not retain ownership after the lane is resolved.

## Validation

- The chosen owner is named with a one-line reason.
- The handoff is performed by reading the owner's SKILL.md, not by answering here.
- The selected specialist set is the minimum needed.
