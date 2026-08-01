---
name: internal-aws-organization-structure
description: Use when /internal-aws selects the AWS organization-structure lane for Organizations, accounts, OUs, delegated administrators, StackSets topology, or platform-level network placement.
---

# Internal AWS Organization Structure

Own AWS layout decisions: account, OU, delegated administrator, StackSets
topology, and platform-level network placement. Translate the platform goal
into a structural result with explicit ownership and rollout scope.

## When to use

- Shaping or reviewing AWS Organizations layout.
- Account, OU, or payer-management separation guidance.
- Delegated administrator placement decisions.
- StackSets topology or rollout-scope guidance.
- Network placement or multi-region layout at platform level.

## Domains

AWS Organizations hierarchy · OU design and safe rollout scope · management vs payer responsibilities · account segmentation and purpose · shared services, security, and log-archive account layout · delegated administrator placement · StackSets topology and blast radius · platform-level network topology · multi-account and multi-region structural decisions.

## Working model

- Keep the management account minimal unless AWS explicitly requires otherwise.
- Distinguish financial ownership from operational ownership.
- Prefer delegated administration when it materially reduces blast radius.
- Separate structure (where capabilities live) from governance (what controls apply).
- Name the smallest safe rollout unit for structural change: account, OU, or region set.

Load `references/control-surface-map.md` for the control-surface split and default review checklist when the structure choice is ambiguous.

## Output expectations

Narrow asks: recommended structure choice · short reason · main blast-radius or rollout note.
Broader asks: structural objective · candidate layouts · recommended placement model · smallest safe rollout unit · main risks.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Treating the management account as the default operating account | Increases blast radius and weakens separation of duties | Keep management account minimal and prefer delegated administrator accounts |
| Mixing payer responsibility with day-to-day operational ownership | Finance and platform controls drift together and are harder to change | State financial owner and operational owner separately |
| Proposing OU or account layouts without a rollout scope | Structural changes become hard to stage or roll back | Name the smallest safe rollout unit: account, OU, or region set |
| Hiding global-resource or cross-region blast radius in StackSets discussions | Failures spread further than the rollout plan suggests | Make regional scope, global resources, and rollback boundaries explicit |
| Using structure answers to sneak in IAM or SCP design | Lane boundary blurs and review gets weaker | Keep placement here and keep guardrail logic out of the structure answer |
| Recommending shared services placement without naming ownership | Central accounts become dumping grounds | State which platform capability lives centrally and which workload teams own execution accounts |

## Completion contract

- Placement model is explicit: management account, delegated administrator, shared-services account, or member account.
- Smallest safe rollout unit is named and matches the proposed structural change.
- Blast radius is explicit for OU moves, delegated admin changes, StackSets rollout, or regional topology shifts.
- Financial ownership and operational ownership are separated when both appear.
- Structural assumptions and rollback boundaries are visible.
