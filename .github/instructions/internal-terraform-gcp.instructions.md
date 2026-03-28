---
description: GCP-specific Terraform standards for IAM bindings, Organization Policies, project hierarchy, and resource conventions.
applyTo: "**/eng-gcp-*/**/*.tf,**/*google*.tf"
---

# Terraform GCP Instructions

## Provider conventions
- Pin `google` and `google-beta` provider versions in `required_providers`.
- Use `project` and `region` from variables or data sources, never hardcoded.
- Prefer workload identity federation over service account keys for CI/CD authentication.
- Keep `credentials` out of provider blocks — use application default credentials or OIDC.

## IAM patterns
- Understand the critical difference between authoritative and additive IAM resources:
  - `google_*_iam_policy` — authoritative, replaces all bindings (dangerous, use only for full ownership).
  - `google_*_iam_binding` — authoritative per role (replaces all members for that role).
  - `google_*_iam_member` — additive (safest, adds one member to one role).
- **Default to `google_*_iam_member`** unless you explicitly own the full IAM state for that resource.
- Never use `roles/editor` or `roles/owner` — use the narrowest predefined role.
- Never bind `allUsers` or `allAuthenticatedUsers` without explicit documented justification.
- Use IAM conditions for time-based, resource-based, or attribute-based access control.
- Prefer Workload Identity over service account keys — keys are long-lived and high-risk.

## Organization Policies
- Use `google_org_policy_policy` for organization-level constraints.
- Document constraint behavior (`enforce: true`, `allow`/`deny` lists) and rollout scope.
- Key constraints to evaluate:
  - `iam.disableServiceAccountKeyCreation` — prevent key creation.
  - `compute.requireShieldedVm` — enforce secure boot.
  - `compute.restrictVpcPeering` — control network connectivity.
  - `iam.allowedPolicyMemberDomains` — restrict external access.
- Use folder-level overrides only with explicit justification.

## Anti-patterns (GCP-specific)

### Critical
- Hardcoded project IDs, service account keys, or OAuth tokens.
- Primitive roles (`roles/editor`, `roles/owner`) on any resource.
- `allUsers` or `allAuthenticatedUsers` IAM binding without justification.

### Major
- Authoritative IAM resource (`_iam_policy`, `_iam_binding`) when additive (`_iam_member`) is safer.
- Service account key creation instead of Workload Identity.
- Missing IAM conditions on sensitive role bindings.
- Firewall rule with `0.0.0.0/0` source range on non-HTTP ports.
- Cloud Storage bucket without uniform bucket-level access.
- Missing audit log configuration on production projects.
- `google_project_iam_binding` that removes existing bindings managed by other teams.

### Minor
- Missing `labels` on resources (equivalent to tags).
- Project naming not following convention (e.g., `<org>-<project>-<env>`).
- Redundant IAM bindings that could be consolidated.

## Project hierarchy
- Keep folder/project organization explicit in Terraform.
- Use `google_folder` and `google_project` with explicit `folder_id` or `org_id`.
- Document which resources are managed at organization, folder, or project level.

## Naming conventions
- Resource names: `snake_case` in Terraform, GCP naming convention in resource names.
- Required labels: `project`, `environment`, `managed-by` (at minimum).

## Validation
- `terraform fmt -recursive`
- `terraform validate`
- Review `terraform plan` for unintended IAM or Org Policy changes.
- Check that no Organization Policy would block the planned changes.
