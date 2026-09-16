#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
MANIFEST=""
MODE="script"
ROOT="${PWD}"
RUNNER_ADAPTER=""
RESOURCE_ADAPTER=""
EXPLICIT_RUNNER=""
HANDOFF=""
SCOPE_FILTER=""
DRY_RUN=0
CONTINUE_ON_ERROR=0
LIVE=0
LIVE_ALLOWED=0
HCL_TMP_DIR=""
HANDOFF_JSON=""
HANDOFF_DECISION=""

usage() {
    printf 'Usage: %s --manifest FILE --mode script|hcl --root DIR --handoff FILE --runner-adapter FILE --resource-adapter FILE [options]\n' "$SCRIPT_NAME" >&2
    printf 'Options: --runner FILE --scope SCOPE --dry-run --continue-on-error --live\n' >&2
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

emit_status() {
    local status="$1"
    local scope="$2"
    local address="$3"
    local reason="${4:-}"
    jq -cn \
        --arg status "$status" \
        --arg scope "$scope" \
        --arg address "$address" \
        --arg reason "$reason" \
        '{scope:$scope,address:$address,status:$status} + (if $reason == "" then {} else {reason:$reason} end)'
}

record_failure() {
    FAILURE_SEEN=1
    if [[ "$CONTINUE_ON_ERROR" -eq 0 ]]; then
        STOP_REQUESTED=1
    fi
}

require_option_value() {
    [[ "$#" -ge 2 && -n "$2" ]] || fail "missing value for $1"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --manifest|--mode|--root|--runner-adapter|--resource-adapter|--runner|--handoff|--scope)
            require_option_value "$@"
            case "$1" in
                --manifest) MANIFEST="$2" ;;
                --mode) MODE="$2" ;;
                --root) ROOT="$2" ;;
                --runner-adapter) RUNNER_ADAPTER="$2" ;;
                --resource-adapter) RESOURCE_ADAPTER="$2" ;;
                --runner) EXPLICIT_RUNNER="$2" ;;
                --handoff) HANDOFF="$2" ;;
                --scope) SCOPE_FILTER="$2" ;;
            esac
            shift 2
            ;;
        --manifest=*) MANIFEST="${1#*=}"; shift ;;
        --mode=*) MODE="${1#*=}"; shift ;;
        --root=*) ROOT="${1#*=}"; shift ;;
        --runner-adapter=*) RUNNER_ADAPTER="${1#*=}"; shift ;;
        --resource-adapter=*) RESOURCE_ADAPTER="${1#*=}"; shift ;;
        --runner=*) EXPLICIT_RUNNER="${1#*=}"; shift ;;
        --handoff=*) HANDOFF="${1#*=}"; shift ;;
        --scope=*) SCOPE_FILTER="${1#*=}"; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        --continue-on-error) CONTINUE_ON_ERROR=1; shift ;;
        --live) LIVE=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) usage; fail "unknown option: $1" ;;
    esac
done

[[ -n "$MANIFEST" ]] || fail "--manifest is required"
[[ -n "$RUNNER_ADAPTER" ]] || fail "--runner-adapter is required"
[[ -n "$RESOURCE_ADAPTER" ]] || fail "--resource-adapter is required"
[[ -n "$HANDOFF" ]] || fail "--handoff is required"
[[ "$MODE" == "script" || "$MODE" == "hcl" ]] || fail "mode must be script or hcl"
if [[ "$MODE" == "hcl" ]]; then
    [[ -n "$SCOPE_FILTER" ]] || fail "HCL mode requires exactly one scope"
fi
[[ "$DRY_RUN" -eq 0 || "$LIVE" -eq 0 ]] || fail "--dry-run and --live are mutually exclusive"
[[ -f "$MANIFEST" ]] || fail "manifest does not exist: $MANIFEST"
[[ -f "$RUNNER_ADAPTER" ]] || fail "runner adapter does not exist: $RUNNER_ADAPTER"
[[ -f "$RESOURCE_ADAPTER" ]] || fail "resource adapter does not exist: $RESOURCE_ADAPTER"
[[ -f "$HANDOFF" ]] || fail "handoff does not exist: $HANDOFF"
[[ -d "$ROOT" ]] || fail "consumer root does not exist: $ROOT"
command -v bash >/dev/null 2>&1 || fail "bash is required"
command -v jq >/dev/null 2>&1 || fail "jq is required"

ROOT="$(cd "$ROOT" && pwd -P)"
HANDOFF_JSON="$(jq -ce '
    if type != "object" then error("handoff must be an object")
    elif .schema_version != 1 then error("handoff schema_version must be 1")
    elif .kind != "internal-terraform-import-handoff" then error("handoff kind is invalid")
    elif (.decision != "assess" and .decision != "execute") then error("handoff decision must be assess or execute")
    elif (.consumer_root|type) != "string" or (.mode|type) != "string" or (.scopes|type) != "array" then error("handoff root, mode, and scopes are required")
    elif (.scopes|length) == 0 or any(.scopes[]; (type != "string" or length == 0)) then error("handoff scopes must be non-empty strings")
    elif (.approval_reference|type) != "string" or (.approval_reference|length) == 0 then error("handoff approval_reference is required")
    else . end
' "$HANDOFF" 2>/dev/null)" || fail "handoff is malformed or incomplete"
HANDOFF_DECISION="$(jq -r '.decision' <<< "$HANDOFF_JSON")"
HANDOFF_ROOT="$(jq -r '.consumer_root' <<< "$HANDOFF_JSON")"
HANDOFF_MODE="$(jq -r '.mode' <<< "$HANDOFF_JSON")"
[[ "$HANDOFF_ROOT" == "$ROOT" ]] || fail "handoff consumer root does not match canonical run root"
[[ "$HANDOFF_MODE" == "$MODE" ]] || fail "handoff mode does not match run mode"

if [[ "$LIVE" -eq 1 ]]; then
    [[ "$HANDOFF_DECISION" == "execute" ]] || fail "--live requires handoff decision=execute"
    if ! jq -e '
        .identity_status == "verified" and
        .reconciliation_status == "complete" and
        (.ownership_disposition == "unmanaged" or .ownership_disposition == "transferred") and
        .mutation_authority == "approved" and
        .convergence_decision == "adoption-only" and
        .runner_status == "verified" and
        .recovery_status == "ready"
    ' <<< "$HANDOFF_JSON" >/dev/null 2>&1; then
        fail "--live requires complete execute safety evidence"
    fi
    LIVE_ALLOWED=1
fi

validate_manifest_scopes() {
    local line record scope
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "${line//[[:space:]]/}" ]] && continue
        case "$line" in
            *'\u003c'*|*'\u003e'*|*'\u0026'*|*'\u0022'*) fail "rendered escape artifact in manifest" ;;
        esac
        if ! record="$(printf '%s\n' "$line" | jq -ce 'if type == "object" and (.scope|type) == "string" and (.address|type) == "string" and (.resource_kind|type) == "string" and (.lookup|type) == "object" then . else error("record must contain scope, address, resource_kind, and lookup") end' 2>/dev/null)"; then
            fail "malformed JSONL record"
        fi
        scope="$(jq -r '.scope' <<< "$record")"
        if [[ "$MODE" == "hcl" && "$scope" != "$SCOPE_FILTER" ]]; then
            continue
        fi
        jq -e --arg selected_scope "$scope" 'any(.scopes[]; . == $selected_scope)' <<< "$HANDOFF_JSON" >/dev/null 2>&1 || fail "handoff scope does not include manifest scope: $scope"
    done < "$MANIFEST"
}

validate_manifest_scopes

if [[ -n "$EXPLICIT_RUNNER" ]]; then
    TERRAFORM_RUNNER="$EXPLICIT_RUNNER"
else
    TERRAFORM_RUNNER="$ROOT/terraform.sh"
fi
[[ -x "$TERRAFORM_RUNNER" ]] || fail "consumer root has no executable terraform.sh runner: $TERRAFORM_RUNNER"

export ROOT TERRAFORM_RUNNER SCOPE_FILTER
# Adapters own the command mapping and are the only code allowed to invoke the
# consumer runner.
# shellcheck disable=SC1090
source "$RUNNER_ADAPTER" || fail "unable to load runner adapter"
# shellcheck disable=SC1090
source "$RESOURCE_ADAPTER" || fail "unable to load resource adapter"

for required_function in runner_preflight runner_state_identity runner_import runner_plan runner_plan_has_create resolve_import_record; do
    declare -F "$required_function" >/dev/null 2>&1 || fail "adapter capability is missing: $required_function"
done

if ! runner_preflight "$ROOT"; then
    fail "runner adapter capability preflight failed"
fi

IMPORTED=0
SKIPPED_ALREADY_MANAGED=0
NOT_FOUND=0
AMBIGUOUS=0
AWS_ERROR=0
TERRAFORM_ERROR=0
FAILURE_SEEN=0
STOP_REQUESTED=0

summary() {
    printf 'Imported: %d\n' "$IMPORTED"
    printf 'Skipped already managed: %d\n' "$SKIPPED_ALREADY_MANAGED"
    printf 'Not found: %d\n' "$NOT_FOUND"
    printf 'Ambiguous: %d\n' "$AMBIGUOUS"
    printf 'AWS errors: %d\n' "$AWS_ERROR"
    printf 'Terraform errors: %d\n' "$TERRAFORM_ERROR"
}

run_hcl_mode() {
    local generated_hcl temp_hcl record line scope address resource_kind record_mode
    local resolved resolution_status canonical_id import_id key destination provider state_id state_rc
    local selected_count=0 kind local_name item key_json id_json first_to first_provider
    HCL_TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/terraform-import-hcl.XXXXXX")"
    trap 'if [[ -n "${HCL_TMP_DIR:-}" && -d "$HCL_TMP_DIR" ]]; then rm -rf -- "$HCL_TMP_DIR"; fi' EXIT
    generated_hcl="$ROOT/imports.generated.tf"
    temp_hcl="$HCL_TMP_DIR/imports.generated.tf"
    local records_file="$HCL_TMP_DIR/records.jsonl"
    : > "$records_file"

    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "${line//[[:space:]]/}" ]] && continue
        if ! record="$(printf '%s\n' "$line" | jq -ce 'if type == "object" and (.scope|type) == "string" and (.address|type) == "string" and (.resource_kind|type) == "string" and (.lookup|type) == "object" then . else error("record must contain scope, address, resource_kind, and lookup") end' 2>/dev/null)"; then
            fail "malformed JSONL record in HCL mode"
        fi
        record_mode="$(jq -r '.mode // empty' <<< "$record")"
        [[ -z "$record_mode" || "$record_mode" == "hcl" ]] || fail "record mode conflicts with HCL mode"
        scope="$(jq -r '.scope' <<< "$record")"
        [[ "$scope" == "$SCOPE_FILTER" ]] || continue
        selected_count=$((selected_count + 1))
        address="$(jq -r '.address' <<< "$record")"
        resource_kind="$(jq -r '.resource_kind' <<< "$record")"
        resolved=""
        if ! resolved="$(resolve_import_record "$record")"; then
            fail "resource adapter failed for HCL address: $address"
        fi
        resolution_status="$(jq -r '.status // empty' <<< "$resolved" 2>/dev/null || true)"
        [[ -z "$resolution_status" ]] || fail "HCL resource resolution failed for $address: $resolution_status"
        if ! jq -e 'type == "object" and (.canonical_id|type) == "string" and (.import_id|type) == "string" and (.key|type) == "string" and (.to|type) == "string" and (.provider|type) == "string" and (.canonical_id|length) > 0 and (.import_id|length) > 0 and (.key|length) > 0 and (.to|length) > 0 and (.provider|length) > 0' <<< "$resolved" >/dev/null 2>&1; then
            fail "HCL adapter metadata is incomplete for $address"
        fi
        canonical_id="$(jq -r '.canonical_id' <<< "$resolved")"
        import_id="$(jq -r '.import_id' <<< "$resolved")"
        key="$(jq -r '.key' <<< "$resolved")"
        destination="$(jq -r '.to' <<< "$resolved")"
        provider="$(jq -r '.provider' <<< "$resolved")"
        [[ "$destination" =~ ^[A-Za-z0-9_.-]+\[each\.key\]$ ]] || fail "HCL adapter destination metadata is not a known shape for $address"
        [[ "$provider" =~ ^[A-Za-z0-9_.-]+$ ]] || fail "HCL adapter provider metadata is not a known alias for $address"
        [[ "$canonical_id" != *$'\n'* && "$import_id" != *$'\n'* && "$key" != *$'\n'* ]] || fail "HCL adapter metadata contains a newline"
        [[ "$canonical_id" != *'${'* && "$import_id" != *'${'* ]] || fail "HCL import IDs must be verified literals"
        state_id=""
        if state_id="$(runner_state_identity "$scope" "$address")"; then
            [[ "$state_id" == "$canonical_id" ]] || fail "HCL canonical identity mismatch for $address: state=$state_id expected=$canonical_id"
            continue
        else
            state_rc=$?
        fi
        [[ "$state_rc" -eq 3 && -z "$state_id" ]] || fail "HCL state inspection failed for $address"
        jq -c --arg scope "$scope" --arg address "$address" --arg resource_kind "$resource_kind" '. + {scope:$scope,address:$address,resource_kind:$resource_kind}' <<< "$resolved" >> "$records_file"
    done < "$MANIFEST"

    [[ "$selected_count" -gt 0 ]] || fail "HCL mode selected no records for exactly one scope: $SCOPE_FILTER"
    : > "$temp_hcl"
    jq -r '.resource_kind' "$records_file" | sort -u | while IFS= read -r kind; do
        [[ -n "$kind" ]] || continue
        local_name="$(printf '%s' "$kind" | sed 's/[^A-Za-z0-9_]/_/g')_import_ids"
        first_to="$(jq -r --arg kind "$kind" 'select(.resource_kind == $kind) | .to' "$records_file" | head -n 1)"
        first_provider="$(jq -r --arg kind "$kind" 'select(.resource_kind == $kind) | .provider' "$records_file" | head -n 1)"
        if [[ -z "$first_to" || -z "$first_provider" ]]; then
            fail "HCL adapter metadata is incomplete for resource kind: $kind"
        fi
        printf 'locals {\n' >> "$temp_hcl"
        printf '  %s = {\n' "$local_name" >> "$temp_hcl"
        while IFS= read -r item; do
            key_json="$(jq -r '.key | @json' <<< "$item")"
            id_json="$(jq -r '.import_id | @json' <<< "$item")"
            printf '    %s = %s\n' "$key_json" "$id_json" >> "$temp_hcl"
        done < <(jq -c --arg kind "$kind" 'select(.resource_kind == $kind)' "$records_file")
        printf '  }\n}\n\n' >> "$temp_hcl"
        printf 'import {\n' >> "$temp_hcl"
        printf '  for_each = local.%s\n' "$local_name" >> "$temp_hcl"
        printf '  to       = %s\n' "$first_to" >> "$temp_hcl"
        printf '  id       = each.value\n' >> "$temp_hcl"
        printf '  provider = %s\n' "$first_provider" >> "$temp_hcl"
        printf '}\n\n' >> "$temp_hcl"
    done
    mv -- "$temp_hcl" "$generated_hcl"
    printf 'Generated: %s\n' "$generated_hcl"

    if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
        declare -F runner_apply >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_apply"
        if ! runner_plan "$ROOT" "$SCOPE_FILTER" "$generated_hcl"; then
            fail "HCL pre-import plan failed; generated file retained"
        fi
        if ! runner_apply "$ROOT" "$SCOPE_FILTER" "$generated_hcl"; then
            fail "HCL apply failed; generated file retained"
        fi
        while IFS= read -r item; do
            address="$(jq -r '.address' <<< "$item")"
            canonical_id="$(jq -r '.canonical_id' <<< "$item")"
            state_id=""
            if ! state_id="$(runner_state_identity "$SCOPE_FILTER" "$address")"; then
                fail "HCL post-apply state verification failed for $address"
            fi
            [[ "$state_id" == "$canonical_id" ]] || fail "HCL post-apply identity mismatch for $address"
        done < "$records_file"
        if ! runner_plan "$ROOT" "$SCOPE_FILTER" "$generated_hcl"; then
            fail "HCL post-import plan failed; generated file retained"
        fi
        if runner_plan_has_create "$ROOT" "$SCOPE_FILTER" "$generated_hcl"; then
            fail "HCL post-import plan contains unexpected creates; generated file retained"
        fi
        rm -f -- "$generated_hcl"
        printf 'Verified: state identity and post-import plan; removed generated file\n'
    fi
}

if [[ "$MODE" == "hcl" ]]; then
    for required_function in runner_preflight runner_state_identity runner_plan runner_plan_has_create resolve_import_record; do
        declare -F "$required_function" >/dev/null 2>&1 || fail "adapter capability is missing: $required_function"
    done
    if ! runner_preflight "$ROOT"; then
        fail "runner adapter capability preflight failed"
    fi
    run_hcl_mode
    exit 0
fi

while IFS= read -r MANIFEST_LINE || [[ -n "$MANIFEST_LINE" ]]; do
    [[ -z "${MANIFEST_LINE//[[:space:]]/}" ]] && continue

    RECORD=""
    if ! RECORD="$(printf '%s\n' "$MANIFEST_LINE" | jq -ce 'if type == "object" and (.scope|type) == "string" and (.address|type) == "string" and (.resource_kind|type) == "string" and (.lookup|type) == "object" then . else error("record must contain scope, address, resource_kind, and lookup") end' 2>/dev/null)"; then
        emit_status "terraform_error" "" "" "malformed JSONL record"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: malformed JSONL record\n' >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    fi

    SCOPE="$(jq -r '.scope' <<< "$RECORD")"
    ADDRESS="$(jq -r '.address' <<< "$RECORD")"
    RESOURCE_KIND="$(jq -r '.resource_kind' <<< "$RECORD")"
    RECORD_MODE="$(jq -r '.mode // empty' <<< "$RECORD")"
    if [[ -n "$RECORD_MODE" && "$RECORD_MODE" != "script" ]]; then
        emit_status "terraform_error" "$SCOPE" "$ADDRESS" "record mode conflicts with script mode"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: record mode conflicts with script mode for %s\n' "$ADDRESS" >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    fi
    [[ -n "$SCOPE" && -n "$ADDRESS" && -n "$RESOURCE_KIND" ]] || {
        emit_status "terraform_error" "$SCOPE" "$ADDRESS" "empty record field"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: empty scope, address, or resource_kind\n' >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    }
    if [[ "$ADDRESS" == *'\u003c'* || "$ADDRESS" == *'\u003e'* || "$ADDRESS" == *'\u0026'* || "$ADDRESS" == *'\u0022'* ]]; then
        emit_status "terraform_error" "$SCOPE" "$ADDRESS" "rendered escape artifact"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: rendered escape artifact in address: %s\n' "$ADDRESS" >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    fi
    if [[ "$ADDRESS" == *$'\n'* || "$SCOPE" == *$'\n'* ]]; then
        emit_status "terraform_error" "$SCOPE" "$ADDRESS" "newline in record identity"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: newline in record identity\n' >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    fi
    if [[ -n "$SCOPE_FILTER" && "$SCOPE" != "$SCOPE_FILTER" ]]; then
        continue
    fi

    RESOLVED=""
    if ! RESOLVED="$(resolve_import_record "$RECORD")"; then
        emit_status "terraform_error" "$SCOPE" "$ADDRESS" "resource adapter failed"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: resource adapter failed for %s\n' "$ADDRESS" >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    fi
    RESOLUTION_STATUS="$(jq -r '.status // empty' <<< "$RESOLVED" 2>/dev/null || true)"
    case "$RESOLUTION_STATUS" in
        not_found)
            emit_status "not_found" "$SCOPE" "$ADDRESS" "resource adapter found no identity"
            NOT_FOUND=$((NOT_FOUND + 1))
            record_failure
            ;;
        ambiguous)
            emit_status "ambiguous" "$SCOPE" "$ADDRESS" "resource identity is ambiguous"
            AMBIGUOUS=$((AMBIGUOUS + 1))
            record_failure
            ;;
        aws_error)
            emit_status "aws_error" "$SCOPE" "$ADDRESS" "resource adapter reported an AWS error"
            AWS_ERROR=$((AWS_ERROR + 1))
            record_failure
            ;;
        terraform_error)
            emit_status "terraform_error" "$SCOPE" "$ADDRESS" "resource adapter reported a Terraform error"
            TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
            record_failure
            ;;
        *)
            if ! jq -e 'type == "object" and (.canonical_id|type) == "string" and (.import_id|type) == "string" and (.canonical_id|length) > 0 and (.import_id|length) > 0' <<< "$RESOLVED" >/dev/null 2>&1; then
                emit_status "terraform_error" "$SCOPE" "$ADDRESS" "resource adapter returned incomplete identity"
                TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
                printf 'ERROR: incomplete resource identity for %s\n' "$ADDRESS" >&2
                record_failure
                [[ "$STOP_REQUESTED" -eq 1 ]] && break
                continue
            fi
            CANONICAL_ID="$(jq -r '.canonical_id' <<< "$RESOLVED")"
            IMPORT_ID="$(jq -r '.import_id' <<< "$RESOLVED")"
            STATE_ID=""
            STATE_RC=0
            if STATE_ID="$(runner_state_identity "$SCOPE" "$ADDRESS")"; then
                if [[ "$STATE_ID" == "$CANONICAL_ID" ]]; then
                    emit_status "skipped_already_managed" "$SCOPE" "$ADDRESS" "state identity matches"
                    SKIPPED_ALREADY_MANAGED=$((SKIPPED_ALREADY_MANAGED + 1))
                    continue
                fi
                emit_status "ambiguous" "$SCOPE" "$ADDRESS" "state identity mismatch"
                AMBIGUOUS=$((AMBIGUOUS + 1))
                printf 'ERROR: canonical identity mismatch for %s: state=%s expected=%s\n' "$ADDRESS" "$STATE_ID" "$CANONICAL_ID" >&2
                record_failure
                [[ "$STOP_REQUESTED" -eq 1 ]] && break
                continue
            else
                STATE_RC=$?
            fi
            if [[ "$STATE_RC" -ne 3 || -n "$STATE_ID" ]]; then
                emit_status "terraform_error" "$SCOPE" "$ADDRESS" "state inspection failed"
                TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
                printf 'ERROR: state inspection failed for %s (exit %d)\n' "$ADDRESS" "$STATE_RC" >&2
                record_failure
                [[ "$STOP_REQUESTED" -eq 1 ]] && break
                continue
            fi
            if [[ "$LIVE_ALLOWED" -eq 0 ]]; then
                emit_status "not_found" "$SCOPE" "$ADDRESS" "Dry-run candidate; no import performed"
                NOT_FOUND=$((NOT_FOUND + 1))
                continue
            fi
            if ! runner_import "$SCOPE" "$ADDRESS" "$IMPORT_ID"; then
                emit_status "terraform_error" "$SCOPE" "$ADDRESS" "runner import failed"
                TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
                printf 'ERROR: runner import failed for %s\n' "$ADDRESS" >&2
                record_failure
                [[ "$STOP_REQUESTED" -eq 1 ]] && break
                continue
            fi
            emit_status "imported" "$SCOPE" "$ADDRESS" "runner import succeeded"
            IMPORTED=$((IMPORTED + 1))
            ;;
    esac
    [[ "$STOP_REQUESTED" -eq 1 ]] && break
done < "$MANIFEST"

summary
if [[ "$FAILURE_SEEN" -ne 0 ]]; then
    exit 1
fi
