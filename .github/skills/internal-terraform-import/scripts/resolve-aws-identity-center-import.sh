#!/usr/bin/env bash

set -Eeuo pipefail

fail_status() {
    local status="$1"
    local reason="$2"
    jq -cn --arg status "$status" --arg reason "$reason" '{status:$status,reason:$reason}'
    exit 1
}

command -v aws >/dev/null 2>&1 || fail_status "aws_error" "aws CLI is required"
command -v jq >/dev/null 2>&1 || fail_status "aws_error" "jq is required"

[[ -n "${AWS_PROFILE:-}" ]] || fail_status "aws_error" "AWS_PROFILE is required"
[[ -n "${EXPECTED_AWS_ACCOUNT_ID:-}" ]] || fail_status "aws_error" "EXPECTED_AWS_ACCOUNT_ID is required"
[[ -n "${IDENTITY_CENTER_REGION:-}" ]] || fail_status "aws_error" "IDENTITY_CENTER_REGION is required"

RECORD=""
if ! RECORD="$(jq -ce 'if type == "object" and (.scope|type) == "string" and (.address|type) == "string" and (.resource_kind|type) == "string" and (.lookup|type) == "object" then . else error("record must contain scope, address, resource_kind, and lookup") end' 2>/dev/null)"; then
    fail_status "terraform_error" "normalized import record is invalid"
fi

RESOURCE_KIND="$(jq -r '.resource_kind' <<< "$RECORD")"
case "$RESOURCE_KIND" in
    identitystore_group|identitystore_group_membership) ;;
    *) fail_status "terraform_error" "unsupported resource_kind: $RESOURCE_KIND" ;;
esac

CALLER_IDENTITY=""
if ! CALLER_IDENTITY="$(aws --profile "$AWS_PROFILE" --region "$IDENTITY_CENTER_REGION" sts get-caller-identity --output json 2>/dev/null)"; then
    fail_status "aws_error" "sts get-caller-identity failed"
fi
CALLER_ACCOUNT="$(jq -r '.Account // empty' <<< "$CALLER_IDENTITY" 2>/dev/null || true)"
[[ -n "$CALLER_ACCOUNT" ]] || fail_status "aws_error" "caller identity response is incomplete"
[[ "$CALLER_ACCOUNT" == "$EXPECTED_AWS_ACCOUNT_ID" ]] || fail_status "aws_error" "unexpected AWS account: $CALLER_ACCOUNT"

INSTANCES=""
if ! INSTANCES="$(aws --profile "$AWS_PROFILE" --region "$IDENTITY_CENTER_REGION" sso-admin list-instances --output json 2>/dev/null)"; then
    fail_status "aws_error" "sso-admin list-instances failed"
fi
INSTANCE_COUNT="$(jq -r 'if (.Instances|type) == "array" then (.Instances|length) else -1 end' <<< "$INSTANCES" 2>/dev/null || true)"
[[ "$INSTANCE_COUNT" == "1" ]] || {
    if [[ "$INSTANCE_COUNT" == "0" ]]; then
        fail_status "not_found" "no Identity Center instance was returned"
    fi
    fail_status "ambiguous" "expected exactly one Identity Center instance"
}
IDENTITY_STORE_ID="$(jq -r '.Instances[0].IdentityStoreId // empty' <<< "$INSTANCES" 2>/dev/null || true)"
[[ -n "$IDENTITY_STORE_ID" ]] || fail_status "aws_error" "IdentityStoreId is missing"

DISPLAY_NAME="$(jq -r '.lookup.display_name // .lookup.displayName // empty' <<< "$RECORD")"
GROUP_ALTERNATE_IDENTIFIER=""
if [[ -n "$DISPLAY_NAME" ]]; then
    GROUP_ALTERNATE_IDENTIFIER="$(jq -cn --arg value "$DISPLAY_NAME" '{UniqueAttribute:{AttributePath:"DisplayName",AttributeValue:$value}}')"
fi

GROUP_ID=""
if [[ "$RESOURCE_KIND" == "identitystore_group" || "$RESOURCE_KIND" == "identitystore_group_membership" ]]; then
    [[ -n "$GROUP_ALTERNATE_IDENTIFIER" ]] || fail_status "not_found" "group display name is required"
    GROUP_RESPONSE=""
    if ! GROUP_RESPONSE="$(aws --profile "$AWS_PROFILE" --region "$IDENTITY_CENTER_REGION" identitystore get-group-id --identity-store-id "$IDENTITY_STORE_ID" --alternate-identifier "$GROUP_ALTERNATE_IDENTIFIER" --output json 2>/dev/null)"; then
        fail_status "aws_error" "identitystore get-group-id failed"
    fi
    GROUP_ID="$(jq -r '.GroupId // empty' <<< "$GROUP_RESPONSE" 2>/dev/null || true)"
    [[ -n "$GROUP_ID" ]] || fail_status "aws_error" "group lookup response is incomplete"
fi

if [[ "$RESOURCE_KIND" == "identitystore_group" ]]; then
    HCL_KEY="$(jq -r '.lookup.key // .lookup.display_name // .lookup.displayName // empty' <<< "$RECORD")"
    HCL_TO="$(jq -r '.lookup.to // empty' <<< "$RECORD")"
    HCL_PROVIDER="$(jq -r '.lookup.provider_alias // .lookup.provider // empty' <<< "$RECORD")"
    jq -cn \
        --arg canonical_id "$IDENTITY_STORE_ID/$GROUP_ID" \
        --arg import_id "$IDENTITY_STORE_ID/$GROUP_ID" \
        --arg identity_store_id "$IDENTITY_STORE_ID" \
        --arg resource_kind "$RESOURCE_KIND" \
        --arg key "$HCL_KEY" \
        --arg to "$HCL_TO" \
        --arg provider "$HCL_PROVIDER" \
        '{canonical_id:$canonical_id,import_id:$import_id,identity_store_id:$identity_store_id,resource_kind:$resource_kind} + (if $key != "" and $to != "" and $provider != "" then {key:$key,to:$to,provider:$provider} else {} end)'
    exit 0
fi

USER_NAME="$(jq -r '.lookup.user_name // .lookup.userName // empty' <<< "$RECORD")"
[[ -n "$USER_NAME" ]] || fail_status "not_found" "user name is required for membership lookup"
USER_ALTERNATE_IDENTIFIER="$(jq -cn --arg value "$USER_NAME" '{UniqueAttribute:{AttributePath:"UserName",AttributeValue:$value}}')"
USER_RESPONSE=""
if ! USER_RESPONSE="$(aws --profile "$AWS_PROFILE" --region "$IDENTITY_CENTER_REGION" identitystore get-user-id --identity-store-id "$IDENTITY_STORE_ID" --alternate-identifier "$USER_ALTERNATE_IDENTIFIER" --output json 2>/dev/null)"; then
    fail_status "aws_error" "identitystore get-user-id failed"
fi
USER_ID="$(jq -r '.UserId // empty' <<< "$USER_RESPONSE" 2>/dev/null || true)"
[[ -n "$USER_ID" ]] || fail_status "aws_error" "user lookup response is incomplete"

MEMBERSHIP_RESPONSE=""
if ! MEMBERSHIP_RESPONSE="$(aws --profile "$AWS_PROFILE" --region "$IDENTITY_CENTER_REGION" identitystore get-group-membership-id --identity-store-id "$IDENTITY_STORE_ID" --group-id "$GROUP_ID" --member-id "UserId=$USER_ID" --output json 2>/dev/null)"; then
    fail_status "aws_error" "identitystore get-group-membership-id failed"
fi
MEMBERSHIP_ID="$(jq -r '.MembershipId // empty' <<< "$MEMBERSHIP_RESPONSE" 2>/dev/null || true)"
[[ -n "$MEMBERSHIP_ID" ]] || fail_status "aws_error" "membership lookup response is incomplete"
HCL_KEY="$(jq -r '.lookup.key // .lookup.display_name // .lookup.displayName // empty' <<< "$RECORD")"
HCL_TO="$(jq -r '.lookup.to // empty' <<< "$RECORD")"
HCL_PROVIDER="$(jq -r '.lookup.provider_alias // .lookup.provider // empty' <<< "$RECORD")"
jq -cn \
    --arg canonical_id "$IDENTITY_STORE_ID/$MEMBERSHIP_ID" \
    --arg import_id "$IDENTITY_STORE_ID/$MEMBERSHIP_ID" \
    --arg identity_store_id "$IDENTITY_STORE_ID" \
    --arg resource_kind "$RESOURCE_KIND" \
    --arg key "$HCL_KEY" \
    --arg to "$HCL_TO" \
    --arg provider "$HCL_PROVIDER" \
    '{canonical_id:$canonical_id,import_id:$import_id,identity_store_id:$identity_store_id,resource_kind:$resource_kind} + (if $key != "" and $to != "" and $provider != "" then {key:$key,to:$to,provider:$provider} else {} end)'
