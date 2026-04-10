---
name: internal-aws-governance
description: Use when the user needs AWS governance guidance for IAM operating models, role and trust design, permission boundaries, federation, SCPs, tag policies, exception handling, or other guardrails that define what principals can do after the AWS structure is chosen.
---

# Internal AWS Governance

Use this skill when the next need is to define or review AWS identity, access, and guardrail decisions.

This skill owns governance logic after the broad structure is known. It helps separate org-level guardrails from account-level access design and keeps permission decisions auditable.

## When to use

- The user needs IAM model guidance across accounts.
- The user needs SCP, trust, federation, or permission-boundary guidance.
- The user needs to separate preventive controls from granted permissions.
- The user needs a review of guardrail design, exception handling, or access governance.

## When not to use

- The main problem is account or OU layout.
- The main problem is strategic option framing before the governance surface is clear.
- The main problem is monitoring, reporting, backup, or post-rollout validation.
- The task is implementation-only.

## Main domains covered

- IAM operating model
- role and group strategy
- trust policy boundaries
- permission boundaries and session constraints
- federation and role assumption patterns
- SCP and tag-policy guardrails
- exception and break-glass handling at governance level
- security guardrails tied to identity and access decisions

## Core rules

- Keep org-level guardrails distinct from account-level grants.
- Treat SCPs as limits on maximum permission, not as grants.
- Prefer roles and federation over long-lived IAM users unless there is a proven reason not to.
- Make scope explicit: root, OU, account set, or single account.
- Make exception handling explicit when a control is not universal.

Load `references/guardrail-map.md` when the correct governance surface is ambiguous or when the user needs a deeper split between IAM, trust, SCP, and boundary controls.

## Use of current facts

Use `internal-aws-mcp-research` when the answer depends on current AWS IAM semantics, service support for delegated patterns, policy simulation, or current documentation.

## Output expectations

For narrow asks, return:

- recommended governance mechanism
- short reason
- main risk or simulation note

For broader asks, return:

- governance objective
- scope
- candidate mechanisms
- recommended control stack
- exception or blast-radius note
- what should be validated before rollout

## Relationship to adjacent skills

- `internal-aws-strategic`
  Use first when the user still needs option framing or lens selection.
- `internal-aws-organization-structure`
  Use when the governance question is actually about where a capability should live.
- `internal-aws-operations`
  Use when the next need is preflight, reporting, validation, or operational evidence after the governance design is chosen.

## Anti-patterns

- using SCPs as if they grant access
- answering a governance question without naming scope
- mixing org-wide guardrails and in-account authorization into one vague recommendation
- proposing break-glass access without boundaries or audit expectations
- recommending rollout without simulation or staged validation when the blast radius is high
