---
name: internal-aws-operations
description: Use when /internal-aws selects the AWS operations lane for monitoring, logging, rollout validation, backup and restore proof, DR evidence, reporting, or audit evidence.
---

# Internal AWS Operations

Own the operational proof for AWS changes: monitoring, evidence, preflight,
rollout validation, recovery proof, reporting, and audit evidence.

## When to use

- Operational readiness guidance after a design choice.
- Monitoring, logging, backup, restore, or DR validation guidance.
- Preflight or post-rollout validation patterns.
- Reporting, export, or audit-evidence guidance.

## Domains

Monitoring and observability · CloudTrail, Config, and audit evidence · backup and restore · DR validation and recovery evidence · preflight checks · post-rollout validation · export and reporting · operational proof that a governance or structure change behaved.

## Core rules

- Keep validation proportional to blast radius.
- Treat backup posture and restore evidence as different things.
- Prefer preflight and staged validation before wide rollout when access or platform automation could break.
- Tie monitoring, evidence, and reporting to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` for a deeper preflight, rollout-validation, or DR-evidence checklist.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Treating monitoring as proof that restore works | Healthy telemetry does not prove recovery viability | Keep backup posture, restore proof, and DR validation as separate evidence lines |
| Skipping preflight for high-blast-radius rollout | Access, logging, or automation regressions discovered too late | Define preflight checks, rollback trigger, and owner before rollout starts |
| Reporting control intent without operational evidence | The platform looks compliant on paper but not in practice | Record what was observed in CloudTrail, Config, logs, or recovery tests |
| Mixing validation advice with new governance design | The answer stops being a reliable operations owner | Keep new guardrail design out of the validation answer and validate the chosen design here |
| Giving a DR answer without making criticality assumption visible | Recovery effort may be overbuilt or underbuilt | State assumed RTO, RPO, or criticality before recommending the evidence path |
| Treating one successful rollout wave as proof for all scopes | Wider OUs, regions, or accounts can still fail differently | Widen only after the first safe unit is validated and recorded |

## Completion contract

- Confirmed evidence is distinguished from inferred evidence.
- Preflight checks, rollback trigger, and rollout unit are explicit for risky changes.
- Backup proof and restore proof are separate validation paths when state exists.
- Main operational signals are named for the affected surface, not as a generic checklist.
- DR or continuity notes appear only when business criticality or recovery posture is in scope.
