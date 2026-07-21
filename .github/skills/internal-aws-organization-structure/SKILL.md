---
name: internal-aws-organization-structure
description: Use when the user needs AWS control-plane or multi-account structure guidance for Organizations, OUs, account models, delegated administrator placement, StackSets topology, network topology at platform level, or other organization-shaping decisions that affect how AWS is laid out before implementation.
---

# Internal AWS Organization Structure

Owns AWS layout decisions: account, OU, delegated admin, StackSets topology, and platform-level network layout. Translates a platform goal into account, OU, delegated admin, network, and rollout structure. Does not own generic strategy, detailed IAM, or monitoring implementation.

## When to use

- Shaping or reviewing AWS Organizations layout.
- Account, OU, or payer-management separation guidance.
- Delegated administrator placement decisions.
- StackSets topology or rollout-scope guidance.
- Network placement or multi-region layout at platform level.

## When not to use

- Mainly IAM, SCP, federation, or guardrail logic → `internal-aws-governance`.
- Mainly monitoring, backup, reporting, or post-rollout validation → `internal-aws-operations`.
- Generic strategic comparison with no concrete structure question → `internal-aws`.
- Already implementation-focused → `internal-aws-lambda`.

## Domains

AWS Organizations hierarchy · OU design and safe rollout scope · management vs payer responsibilities · account segmentation and purpose · shared services, security, and log-archive account layout · delegated administrator placement · StackSets topology and blast radius · platform-level network topology · multi-account and multi-region structural decisions.

## Working model

- Keep the management account minimal unless AWS explicitly requires otherwise.
- Distinguish financial ownership from operational ownership.
- Prefer delegated administration when it materially reduces blast radius.
- Separate structure (where capabilities live) from governance (what controls apply).
- Name the smallest safe rollout unit for structural change: account, OU, or region set.

Load `references/control-surface-map.md` for the control-surface split and default review checklist when the structure choice is ambiguous.

## Handoffs

| To | When |
|---|---|
| `internal-aws-mcp-research` | answer depends on current AWS service support, delegated admin capabilities, StackSets behavior, or region-sensitive constraints |
| `internal-aws-governance` | structure is accepted and next need is IAM, SCP, trust, federation, or guardrail definition |
| `internal-aws-operations` | structure is accepted and next need is validation, monitoring, backup, or operational evidence |

## Output expectations

Narrow asks: recommended structure choice · short reason · main blast-radius or rollout note.
Broader asks: structural objective · candidate layouts · recommended placement model · smallest safe rollout unit · main risks · next handoff.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Treating the management account as the default operating account | Increases blast radius and weakens separation of duties | Keep management account minimal and prefer delegated administrator accounts |
| Mixing payer responsibility with day-to-day operational ownership | Finance and platform controls drift together and are harder to change | State financial owner and operational owner separately |
| Proposing OU or account layouts without a rollout scope | Structural changes become hard to stage or roll back | Name the smallest safe rollout unit: account, OU, or region set |
| Hiding global-resource or cross-region blast radius in StackSets discussions | Failures spread further than the rollout plan suggests | Make regional scope, global resources, and rollback boundaries explicit |
| Using structure answers to sneak in IAM or SCP design | Lane boundary blurs and review gets weaker | Keep placement here and hand guardrail logic to `internal-aws-governance` |
| Recommending shared services placement without naming ownership | Central accounts become dumping grounds | State which platform capability lives centrally and which workload teams own execution accounts |

## Validation

- Placement model is explicit: management account, delegated administrator, shared-services account, or member account.
- Smallest safe rollout unit is named and matches the proposed structural change.
- Blast radius is explicit for OU moves, delegated admin changes, StackSets rollout, or regional topology shifts.
- Financial ownership and operational ownership are separated when both appear.
- Next handoff is clear when the user now needs guardrails or operational validation.
