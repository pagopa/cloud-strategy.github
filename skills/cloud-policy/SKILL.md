---
name: cloud-policy
description: Create or modify governance policies for AWS SCP, Azure Policy, and GCP Org Policy.
---

# Cloud Policy Skill

## When to use
- Creating or modifying cloud governance policy definitions.
- Updating scope, conditions, or effects of existing policies.

## Mandatory rules
- Keep scope explicit (organization/folder/subscription/project).
- Keep conditions readable and auditable.
- Prefer deny-by-default for high-risk controls.
- Keep descriptions and metadata in English.

## Minimal patterns
- AWS: explicit `Action`/`NotAction`, `Resource`, `Condition`.
- Azure: `if` / `then.effect` in policy rule JSON.
- GCP: `google_org_policy_policy` with clear target scope.

## Validation
- Validate syntax in target format.
- Test in non-production before rollout.
- Document behavioral impact.
