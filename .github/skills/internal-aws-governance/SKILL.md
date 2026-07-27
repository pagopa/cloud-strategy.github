---
name: internal-aws-governance
description: Use when /internal-aws selects the AWS governance lane for IAM operating models, trust policies, federation, permission boundaries, SCPs, tag policies, exception controls, or access guardrails.
---

# Internal AWS Governance

Own AWS IAM, trust, SCP, federation, permission-boundary, and access-guardrail
decisions. Separate org-level guardrails from account-level grants and keep
permission decisions auditable.

## When to use

- IAM operating-model guidance across accounts.
- SCP, trust, federation, or permission-boundary guidance.
- Separating preventive controls from granted permissions.
- Guardrail design, exception handling, or access-governance review.

## Core rules

- Keep org-level guardrails distinct from account-level grants.
- Treat SCPs as limits on maximum permission, not as grants.
- Prefer roles and federation over long-lived IAM users unless a proven reason exists.
- Make scope explicit: root, OU, account set, or single account.
- Make exception handling explicit when a control is not universal.
- On `AccessDenied` with "explicit deny in a service control policy", treat the SCP as the blocking control; target-account IAM grants cannot override an explicit SCP deny.

Load `references/guardrail-map.md` when the governance surface is ambiguous or a deeper split between IAM, trust, SCP, and boundary controls is needed.

## Domains

IAM operating model · role and group strategy · trust-policy boundaries · permission boundaries and session constraints · federation and role assumption · SCP and tag-policy guardrails · exception and break-glass handling · security guardrails tied to identity and access.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using SCPs as if they grant access | Preventive controls mistaken for execution permissions | Pair SCP guidance with the required IAM grant path |
| Answering without naming scope | Root, OU, and account controls behave differently | State the exact governance scope before recommending a mechanism |
| Mixing org-wide guardrails and in-account authorization into one vague recommendation | Reviewers cannot see which control prevents versus grants | Separate the org-level mechanism from the account-level design |
| Proposing break-glass access without boundaries or audit expectations | Emergency access becomes standing privilege with weak accountability | Define who can invoke it, how it is bounded, and what audit evidence must exist |
| Recommending rollout without simulation when blast radius is high | A wide deny or trust failure can interrupt platform operations | Use simulation, targeted rollout, and explicit rollback triggers before widening |
| Treating permission boundaries as a replacement for trust design | Delegation stays too broad even if identity policies are constrained | Use boundaries to limit delegated builders and trust policies to control who assumes the role |

## Completion contract

- Governance scope is explicit: root, OU, account set, or single account.
- Recommended mechanism is clear about whether it prevents, grants, or constrains.
- Trust boundaries and exception paths are explicit when access crosses account boundaries.
- Staged validation or simulation is named before high-blast-radius rollout.
- Expected effects and evidence requirements are explicit for every proposed control.
