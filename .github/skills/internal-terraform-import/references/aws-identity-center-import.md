# AWS Identity Center Import Adapter

Use this reference only after `/internal-terraform` hands off an approved
import and the generic import orchestrator selects the AWS Identity Center
adapter. The consumer runner must supply an explicit `AWS_PROFILE`, expected
AWS account ID, Identity Center API region, scope, and ownership evidence.
These values are independent of Terraform backend region, provider alias, and
state scope; none may be inferred.

## Identity and lookup contract

Before any lookup, verify the explicit profile and region are present and run:

```text
aws sts get-caller-identity
```

Require the returned account to equal the expected account. Then enumerate
instances with the current service namespace:

```text
aws sso-admin list-instances
```

Require exactly one selected Identity Center instance and identity store. The
AWS CLI service is `sso-admin`; `ssoadmin` is not a valid substitute for this
adapter contract.

For a group, call `identitystore get-group-id` with JSON document input using
`displayName`, and emit the canonical import identity
`identity_store_id/group_id`. For a user, call `identitystore get-user-id`
with JSON document input using `userName`. For a membership, call
`identitystore get-group-membership-id` with `MemberId` set to
`UserId=<user_id>`, and emit `identity_store_id/membership_id`.

Do not use deprecated list-based group or user filters,
`list-group-memberships`, or response fallbacks such as `.Memberships` and
`.GroupMemberships`. Stop without an ID on no result, multiple results, an
incomplete response, an AWS error, an unexpected account, or an unsupported
`resource_kind`.

## Evidence separation

The AWS profile and account identify the caller; the Identity Center API region
and identity store identify the lookup service; the Terraform backend region
and state scope identify remote state; and the provider alias identifies the
Terraform provider configuration. Scope, ownership, and mutation authority are
separate evidence fields. A resolver result is usable only when one canonical
expected identity is proven across these boundaries.
