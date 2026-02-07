---
description: Create or modify a cloud governance policy (AWS SCP, Azure Policy, GCP Org Policy)
name: cs-cloud-policy
agent: agent
argument-hint: action=<create|modify> cloud=<aws|azure|gcp> policy_name=<name> purpose=<purpose> [effect=<deny|audit|modify|append|disabled>]
---

# Cloud Governance Policy Task

## Required inputs
- **Action**: ${input:action:create,modify}
- **Cloud**: ${input:cloud:aws,azure,gcp}
- **Policy name**: ${input:policy_name}
- **Purpose**: ${input:purpose}
- **Effect (optional)**: ${input:effect:deny,audit,modify,append,disabled}

## Instructions
1. Reuse existing policy patterns in the target repository.
2. Keep policy logic explicit (scope, conditions, effect).
3. Preserve naming and folder conventions.
4. Keep technical text in English.
5. If `action=modify`, preserve existing behavior unless explicitly changed.

## Validation
- Validate syntax for the target cloud policy format.
- Test in non-production first.
- Update docs in English when behavior changes.
