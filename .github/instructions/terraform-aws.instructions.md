---
description: AWS-specific Terraform standards for IAM, Organizations, SCPs, and resource conventions.
applyTo: "**/eng-aws-*/**/*.tf,**/*aws*.tf"
---

# Terraform AWS Instructions

## Provider conventions
- Pin `aws` provider version in `required_providers`.
- Use `assume_role` blocks for cross-account access instead of hardcoded credentials.
- Configure `default_tags` at the provider level for consistent tagging.
- Keep region explicit in provider configuration or variable.

## IAM patterns
- Separate IAM roles from IAM policies — roles define trust, policies define permissions.
- Use `aws_iam_policy_document` data source instead of inline JSON for readability and validation.
- Scope `Resource` to the narrowest ARN possible — never `"*"` without documented justification.
- Scope `Action` to exact API calls needed — never `"*"` without documented justification.
- Use `Condition` keys to restrict by source, tag, or organization when applicable.
- Prefer permission boundaries on human-assumable roles.
- Use `iam:PassRole` conditions to prevent privilege escalation.

## Organizations and SCPs
- Document alignment with active Service Control Policies — a resource may be valid Terraform but blocked by SCP.
- Keep SCP statements explicit: `Deny` with conditions, not implicit `Allow`.
- Use `aws:PrincipalOrgID` condition to restrict cross-account trust.
- Keep OU-level policy assignment explicit and auditable.

## Anti-patterns (AWS-specific)

### Critical
- `"Action": "*"` with `"Resource": "*"` — unrestricted admin.
- Hardcoded AWS account IDs — use `data.aws_caller_identity` or variables.
- Hardcoded access keys or secret keys.

### Major
- `"Resource": "*"` when the target resource ARN is known.
- Trust policy with `"Principal": "*"` or overly broad account trust.
- Missing `Condition` on `sts:AssumeRole` trust policies.
- S3 bucket without `block_public_access` configuration.
- Security group with `0.0.0.0/0` ingress on non-HTTP ports.
- Missing `aws_iam_account_password_policy` in account baseline.
- IAM user with inline policy instead of group/role-based access.

### Minor
- Missing `ManagedBy = "terraform"` tag.
- Redundant IAM policy statements that could be consolidated.
- Missing `source_policy_documents` for policy composition.

## Naming conventions
- Resource names: `snake_case` with cloud context (e.g., `aws_iam_role.lambda_execution`).
- Required tags: `Project`, `Environment`, `ManagedBy` (at minimum via `default_tags`).

## Validation
- `terraform fmt -recursive`
- `terraform validate`
- Review `terraform plan` for unintended IAM changes.
- Check that no SCP would block the planned changes.
