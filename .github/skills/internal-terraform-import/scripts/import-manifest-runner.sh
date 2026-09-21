#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
MANIFEST=""
MODE="script"
ROOT="${PWD}"
RUNNER_ADAPTER=""
RESOURCE_ADAPTER=""
EXPLICIT_RUNNER=""
HANDOFF=""
SCOPE_FILTER=""
NORMALIZED_MANIFEST=""
DRY_RUN=0
CONTINUE_ON_ERROR=0
LIVE=0
LIVE_ALLOWED=0
HCL_TMP_DIR=""
HANDOFF_JSON=""
HANDOFF_DECISION=""
HANDOFF_EXECUTION_MODE=""
HANDOFF_RUN_ID=""
HANDOFF_SCHEMA_VERSION=""
HANDOFF_RUNNER_PATH=""
LIVE_RECOVERY_PATH=""
LIVE_PLAN_ARTIFACT_PATH=""
LIVE_PLAN_ENVELOPE_PATH=""

usage() {
    printf 'Usage: %s --manifest FILE --mode script|hcl --root DIR --handoff FILE --runner-adapter FILE --resource-adapter FILE [options]\n' "$SCRIPT_NAME" >&2
    printf 'Options: --runner FILE --scope SCOPE --dry-run --continue-on-error --live\n' >&2
}

persist_failure_recovery() {
    local reason="$1" recovery_path recovery_dir recovery_json timestamp
    [[ "$LIVE_ALLOWED" -eq 1 && -n "$HANDOFF_RUN_ID" ]] || return 0
    command -v jq >/dev/null 2>&1 || return 1
    recovery_path="${LIVE_RECOVERY_PATH:-$ROOT/.terraform-import-adoption/$HANDOFF_RUN_ID.recovery.json}"
    recovery_dir="$(dirname "$recovery_path")"
    mkdir -p -- "$recovery_dir" || return 1
    timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || printf 'unknown')"
    recovery_json="$(jq -cn \
        --arg run_id "$HANDOFF_RUN_ID" \
        --arg status "failed" \
        --arg reason "$reason" \
        --arg timestamp "$timestamp" \
        --arg location "$recovery_path" \
        --arg plan_artifact "${LIVE_PLAN_ARTIFACT_PATH:-}" \
        --arg plan_envelope "${LIVE_PLAN_ENVELOPE_PATH:-}" \
        '{schema_version:1,kind:"internal-terraform-import-recovery",run_id:$run_id,status:$status,reason:$reason,timestamp:$timestamp,location:$location,plan_artifact:$plan_artifact,plan_envelope:$plan_envelope}' 2>/dev/null)" || return 1
    if [[ -e "$recovery_path" ]]; then
        [[ -f "$recovery_path" ]] || return 1
        jq -e \
            --arg run_id "$HANDOFF_RUN_ID" \
            --arg location "$recovery_path" \
            '(.schema_version == 1) and
             (.kind == "internal-terraform-import-recovery") and
             (.run_id == $run_id) and
             (.status == "failed") and
             (.location == $location) and
             (.reason | type == "string")' \
            "$recovery_path" >/dev/null 2>&1 || return 1
        return 0
    fi
    printf '%s\n' "$recovery_json" > "$recovery_path" || return 1
    chmod 600 "$recovery_path" || return 1
}

fail() {
    if ! persist_failure_recovery "$*"; then
        printf 'ERROR: unable to persist live recovery record\n' >&2
    fi
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

cleanup_normalized_manifest() {
    if [[ -n "$NORMALIZED_MANIFEST" && -f "$NORMALIZED_MANIFEST" ]]; then
        rm -f -- "$NORMALIZED_MANIFEST"
    fi
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

write_immutable_record() {
    local target="$1"
    local content="$2"
    if [[ -e "$target" ]]; then
        cmp -s <(printf '%s\n' "$content") "$target" || fail "immutable record changed: $target"
        return 0
    fi
    printf '%s\n' "$content" > "$target"
    chmod 600 "$target"
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
command -v cmp >/dev/null 2>&1 || fail "cmp is required"
command -v date >/dev/null 2>&1 || fail "date is required"
for required_command in basename dirname mktemp mkdir chmod rm sort sed head mv; do
    command -v "$required_command" >/dev/null 2>&1 || fail "$required_command is required"
done

ROOT="$(cd "$ROOT" && pwd -P)"
HANDOFF_JSON="$(jq -ce '
    if type != "object" then error("handoff must be an object")
    elif (.schema_version != 1 and .schema_version != 2) then error("handoff schema_version must be 1 or 2")
    elif .kind != "internal-terraform-import-handoff" then error("handoff kind is invalid")
    elif (.decision != "assess" and .decision != "execute") then error("handoff decision must be assess or execute")
    elif (.consumer_root|type) != "string" or (.mode|type) != "string" or (.scopes|type) != "array" then error("handoff root, mode, and scopes are required")
    elif (.scopes|length) == 0 or any(.scopes[]; (type != "string" or length == 0)) then error("handoff scopes must be non-empty strings")
    elif (.approval_reference|type) != "string" or (.approval_reference|length) == 0 then error("handoff approval_reference is required")
    else . end
' "$HANDOFF" 2>/dev/null)" || fail "handoff is malformed or incomplete"
HANDOFF_DECISION="$(jq -r '.decision' <<< "$HANDOFF_JSON")"
HANDOFF_SCHEMA_VERSION="$(jq -r '.schema_version' <<< "$HANDOFF_JSON")"
HANDOFF_ROOT="$(jq -r '.consumer_root' <<< "$HANDOFF_JSON")"
HANDOFF_MODE="$(jq -r '.mode' <<< "$HANDOFF_JSON")"
HANDOFF_EXECUTION_MODE="$(jq -r '.execution_mode // empty' <<< "$HANDOFF_JSON")"
HANDOFF_RUN_ID="$(jq -r '.run_id // empty' <<< "$HANDOFF_JSON")"
if [[ "$HANDOFF_SCHEMA_VERSION" == "1" && "$HANDOFF_DECISION" != "assess" ]]; then
    fail "protocol v1 supports assessment only"
fi
[[ "$HANDOFF_ROOT" == "$ROOT" ]] || fail "handoff consumer root does not match canonical run root"
[[ "$HANDOFF_MODE" == "$MODE" ]] || fail "handoff mode does not match run mode"
if [[ "$MODE" == "hcl" ]]; then
    jq -e --arg selected_scope "$SCOPE_FILTER" 'any(.scopes[]; . == $selected_scope)' <<< "$HANDOFF_JSON" >/dev/null 2>&1 || fail "selected HCL scope is not authorized by handoff: $SCOPE_FILTER"
fi
command -v python3 >/dev/null 2>&1 || fail "python3 is required for handoff validation"
protocol_validation_args=(validate-handoff --root "$ROOT" --mode "$MODE")
[[ "$LIVE" -eq 1 ]] && protocol_validation_args+=(--live)
if ! printf '%s\n' "$HANDOFF_JSON" | python3 "$SCRIPT_DIR/adoption_protocol.py" "${protocol_validation_args[@]}" >/dev/null; then
    fail "handoff failed protocol validation"
fi
[[ "$HANDOFF_EXECUTION_MODE" != "converge" ]] || fail "convergence execution is not supported by internal-terraform-import"

if [[ "$LIVE" -eq 1 ]]; then
    jq -e '.schema_version == 2' <<< "$HANDOFF_JSON" >/dev/null 2>&1 || fail "--live requires handoff schema_version 2"
    [[ "$HANDOFF_DECISION" == "execute" ]] || fail "--live requires handoff decision=execute"
    if ! jq -e '
        .identity_status == "verified" and
        .reconciliation_status == "complete" and
        (.ownership_disposition == "unmanaged" or .ownership_disposition == "transferred") and
        .mutation_authority.status == "approved" and
        .convergence_decision == "adoption-only" and
        .runner_status == "verified" and
        .recovery_status == "ready"
    ' <<< "$HANDOFF_JSON" >/dev/null 2>&1; then
        fail "--live requires complete execute safety evidence"
    fi
    LIVE_ALLOWED=1
    LIVE_RECOVERY_PATH="$ROOT/.terraform-import-adoption/$HANDOFF_RUN_ID.recovery.json"
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

NORMALIZED_MANIFEST="$(mktemp "${TMPDIR:-/tmp}/terraform-import-normalized.XXXXXX")" || fail "unable to create normalized manifest"
if [[ "$MODE" == "hcl" ]]; then
    if ! jq -cs --arg selected_scope "$SCOPE_FILTER" 'map(select(.scope == $selected_scope))' "$MANIFEST" | python3 "$SCRIPT_DIR/adoption_protocol.py" normalize-manifest --scope "$SCOPE_FILTER" | jq -c '.[]' > "$NORMALIZED_MANIFEST"; then
        fail "HCL manifest failed reconciliation disposition validation"
    fi
elif ! jq -cs '.' "$MANIFEST" | python3 "$SCRIPT_DIR/adoption_protocol.py" normalize-manifest | jq -c '.[]' > "$NORMALIZED_MANIFEST"; then
    fail "manifest failed reconciliation disposition validation"
fi
trap 'cleanup_normalized_manifest' EXIT
MANIFEST="$NORMALIZED_MANIFEST"

if [[ -n "$EXPLICIT_RUNNER" ]]; then
    TERRAFORM_RUNNER="$EXPLICIT_RUNNER"
else
    TERRAFORM_RUNNER="$ROOT/terraform.sh"
fi
[[ -x "$TERRAFORM_RUNNER" ]] || fail "consumer root has no executable terraform.sh runner: $TERRAFORM_RUNNER"
HANDOFF_RUNNER_PATH="$(jq -r '.runner.path // .runner_path // empty' <<< "$HANDOFF_JSON")"
if [[ -n "$EXPLICIT_RUNNER" || "$LIVE_ALLOWED" -eq 1 ]]; then
    [[ -n "$HANDOFF_RUNNER_PATH" && "$TERRAFORM_RUNNER" == "$HANDOFF_RUNNER_PATH" ]] || fail "selected runner path does not match handoff runner path"
fi

export ROOT TERRAFORM_RUNNER SCOPE_FILTER
# Adapters own the command mapping and are the only code allowed to invoke the
# consumer runner.
# shellcheck disable=SC1090
source "$RUNNER_ADAPTER" || fail "unable to load runner adapter"
# shellcheck disable=SC1090
source "$RESOURCE_ADAPTER" || fail "unable to load resource adapter"

for required_function in runner_preflight runner_state_identity runner_plan resolve_import_record; do
    declare -F "$required_function" >/dev/null 2>&1 || fail "adapter capability is missing: $required_function"
done

if ! runner_preflight "$ROOT"; then
    fail "runner adapter capability preflight failed"
fi

if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
    declare -F runner_plan_json >/dev/null 2>&1 || fail "adapter capability is missing: runner_plan_json"
    command -v python3 >/dev/null 2>&1 || fail "python3 is required for plan classification"
    PLAN_JSON=""
    if ! PLAN_JSON="$(runner_plan_json "$ROOT" "$SCOPE_FILTER" "$MANIFEST")"; then
        fail "runner plan JSON capability failed"
    fi
    PLAN_CLASSIFICATION=""
    if ! PLAN_CLASSIFICATION="$(printf '%s\n' "$PLAN_JSON" | python3 "$SCRIPT_DIR/adoption_protocol.py" classify-plan)"; then
        fail "runner returned invalid machine-readable plan"
    fi
    if ! jq -e '.allowed == true' <<< "$PLAN_CLASSIFICATION" >/dev/null 2>&1; then
        BLOCKED_ACTIONS="$(jq -r '[.blocked_actions[] | (.action + (if .address == "" then "" else " at " + .address end))] | join(", ")' <<< "$PLAN_CLASSIFICATION")"
        fail "adoption plan contains disallowed action(s): ${BLOCKED_ACTIONS:-unknown}"
    fi
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

build_runtime_evidence_record() {
    local evidence_path="$1" plan_artifact_path="$2" plan_envelope_path="$3"
    local plan_envelope_json="$4" post_plan_classification="$5" records_file="$6"
    local final_state_identities="$7" live_verifications="$8" reconciliation_file="$9"
    local desired_inventory reconciliation collision_results ambiguity_results state_inventory
    local tool_versions timestamp evidence_input

    if [[ -f "$evidence_path" ]]; then
        local existing_evidence
        existing_evidence="$(<"$evidence_path")"
        printf '%s\n' "$existing_evidence" | python3 "$SCRIPT_DIR/adoption_protocol.py" validate-runtime-evidence >/dev/null || return 1
        printf '%s\n' "$existing_evidence"
        return 0
    fi

    desired_inventory="$(jq -sc --arg selected_scope "$SCOPE_FILTER" 'if $selected_scope == "" then . else map(select(.scope == $selected_scope)) end' "$MANIFEST")"
    reconciliation="$(jq -sc '.' "$reconciliation_file")"
    collision_results="$(jq -c '[.[] | select(.observed_status == "collision" or .disposition == "collision")]' <<< "$reconciliation")"
    ambiguity_results="$(jq -c '[.[] | select(.observed_status == "ambiguous" or .disposition == "ambiguous_live_identity" or .disposition == "state_identity_mismatch")]' <<< "$reconciliation")"
    state_inventory="$(jq -c 'to_entries | map({address:.key,identity:.value})' <<< "$final_state_identities")"
    tool_versions="$(jq -c '.tool_versions' <<< "$HANDOFF_JSON")"
    timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    evidence_input="$(jq -cn \
        --arg run_id "$HANDOFF_RUN_ID" \
        --arg timestamp "$timestamp" \
        --arg plan_artifact_path "$plan_artifact_path" \
        --arg plan_envelope_path "$plan_envelope_path" \
        --argjson tool_versions "$tool_versions" \
        --argjson desired_inventory "$desired_inventory" \
        --argjson live_inventory "$live_verifications" \
        --argjson state_inventory "$state_inventory" \
        --argjson reconciliation "$reconciliation" \
        --argjson collision_results "$collision_results" \
        --argjson ambiguity_results "$ambiguity_results" \
        --argjson state_boundary "$(jq -c '.state_boundary' <<< "$HANDOFF_JSON")" \
        --argjson plan_binding "$(jq -c '.binding' <<< "$plan_envelope_json")" \
        --argjson plan_classification "$(jq -c '{actions,blocked_actions,allowed}' <<< "$plan_envelope_json")" \
        --argjson post_apply_classification "$post_plan_classification" \
        --argjson live_verifications "$live_verifications" \
        '{run_id:$run_id,timestamp:$timestamp,tool_versions:$tool_versions,desired_inventory:$desired_inventory,live_inventory:$live_inventory,state_inventory:$state_inventory,state_boundary:$state_boundary,reconciliation:$reconciliation,collision_results:$collision_results,ambiguity_results:$ambiguity_results,plan_artifact_path:$plan_artifact_path,plan_envelope_path:$plan_envelope_path,plan_binding:$plan_binding,plan_classification:$plan_classification,post_apply_classification:$post_apply_classification,live_verifications:$live_verifications}')"
    printf '%s\n' "$evidence_input" | python3 "$SCRIPT_DIR/adoption_protocol.py" build-runtime-evidence
}

persist_completion_records() {
    local evidence_path="$1" recovery_path="$2" receipt_path="$3"
    local authorization_json="$4" evidence_json="$5" plan_envelope_json="$6"
    local imports_json="$7" moves_json="$8" final_state_identities="$9"
    local live_verifications="${10}" post_plan_json="${11}" final_status="${12}"
    local recovery_json receipt_input receipt_json

    if [[ -f "$recovery_path" ]]; then
        recovery_json="$(<"$recovery_path")"
    else
        recovery_json="$(jq -cn \
            --arg location "$recovery_path" \
            --arg plan_artifact "$(jq -r '.plan_artifact_path' <<< "$evidence_json")" \
            --arg plan_envelope "$(jq -r '.plan_envelope_path' <<< "$evidence_json")" \
            '{location:$location,plan_artifact:$plan_artifact,plan_envelope:$plan_envelope}')"
        write_immutable_record "$recovery_path" "$recovery_json"
    fi
    write_immutable_record "$evidence_path" "$evidence_json"
    receipt_input="$(jq -cn \
        --arg run_id "$HANDOFF_RUN_ID" \
        --argjson authorization "$authorization_json" \
        --argjson evidence "$evidence_json" \
        --argjson plan_binding "$(jq -c '.binding' <<< "$plan_envelope_json")" \
        --argjson imports "$imports_json" \
        --argjson moves "$moves_json" \
        --argjson final_state_identities "$final_state_identities" \
        --argjson live_verifications "$live_verifications" \
        --argjson post_apply_plan "$post_plan_json" \
        --arg final_status "$final_status" \
        --argjson recovery_evidence "$recovery_json" \
        '{run_id:$run_id,authorization:$authorization,evidence:$evidence,plan_binding:$plan_binding,imports:$imports,moves:$moves,final_state_identities:$final_state_identities,live_verifications:$live_verifications,post_apply_plan:$post_apply_plan,final_status:$final_status,recovery_evidence:$recovery_evidence}')"
    if ! receipt_json="$(printf '%s\n' "$receipt_input" | python3 "$SCRIPT_DIR/adoption_protocol.py" build-receipt)"; then
        fail "completion receipt construction failed"
    fi
    write_immutable_record "$receipt_path" "$receipt_json"
}

validate_saved_adoption_operations() {
    local plan_envelope_json="$1" records_file="$2" expected_operations actual_operations
    expected_operations="$(jq -sc '
        map(if .disposition == "moved_candidate" then
            {action:"moved",address:.move.to,from:.move.from,to:.move.to}
        else
            {action:"import",address:.address,from:"",to:""}
        end)
        | sort_by(.action, .address, .from, .to)
    ' "$records_file")"
    actual_operations="$(jq -c '
        [.actions[]
        | select(.action == "import" or .action == "moved")
        | {action,address:(.address // ""),from:(.from // ""),to:(.to // "")}]
        | sort_by(.action, .address, .from, .to)
    ' <<< "$plan_envelope_json")"
    [[ "$expected_operations" == "$actual_operations" ]] || fail "saved adoption plan operations do not match requested operations: expected=$expected_operations actual=$actual_operations"
}

confirm_live_identities_before_apply() {
    local records_file="$1" item address expected_identity resolved resolution_status actual_identity
    while IFS= read -r item; do
        address="$(jq -r '.address' <<< "$item")"
        expected_identity="$(jq -r '.lookup.canonical_id // .canonical_id // .move.canonical_id // empty' <<< "$item")"
        if ! resolved="$(resolve_import_record "$item")"; then
            fail "pre-apply identity confirmation failed for $address"
        fi
        resolution_status="$(jq -r '.status // empty' <<< "$resolved" 2>/dev/null || true)"
        [[ -z "$resolution_status" ]] || fail "pre-apply identity confirmation returned $resolution_status for $address"
        actual_identity="$(jq -r '.canonical_id // empty' <<< "$resolved")"
        [[ -n "$expected_identity" && "$actual_identity" == "$expected_identity" ]] || fail "pre-apply identity confirmation mismatch for $address"
    done < "$records_file"
}

run_hcl_mode() {
    local generated_hcl temp_hcl record line scope address resource_kind record_mode
    local resolved resolution_status canonical_id import_id key destination provider state_id state_rc disposition
    local selected_count=0 kind local_name item key_json id_json first_to first_provider
    local terraform_expression_marker
    local move_from move_to move_canonical_id move_state_lineage destination_state_id live_resolution live_status
    local plan_artifact_dir plan_artifact_path plan_envelope_path plan_json plan_envelope
    local authorization_path evidence_path recovery_path receipt_path
    local authorization_json evidence_json recovery_json receipt_input receipt_json
    local imports_json moves_json final_state_identities live_verifications live_verifications_file
    HCL_TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/terraform-import-hcl.XXXXXX")"
    trap 'cleanup_normalized_manifest; if [[ -n "${HCL_TMP_DIR:-}" && -d "$HCL_TMP_DIR" ]]; then rm -rf -- "$HCL_TMP_DIR"; fi' EXIT
    if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
        LIVE_RECOVERY_PATH="$ROOT/.terraform-import-adoption/$HANDOFF_RUN_ID.recovery.json"
    fi
    generated_hcl="$ROOT/imports.generated.tf"
    temp_hcl="$HCL_TMP_DIR/imports.generated.tf"
    local records_file="$HCL_TMP_DIR/records.jsonl"
    local reconciliation_file="$HCL_TMP_DIR/reconciliation.jsonl"
    live_verifications_file="$HCL_TMP_DIR/live-verifications.jsonl"
    : > "$records_file"
    : > "$reconciliation_file"
    : > "$live_verifications_file"

    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "${line//[[:space:]]/}" ]] && continue
        if ! record="$(printf '%s\n' "$line" | jq -ce 'if type == "object" and (.scope|type) == "string" and (.address|type) == "string" and (.resource_kind|type) == "string" and (.lookup|type) == "object" then . else error("record must contain scope, address, resource_kind, and lookup") end' 2>/dev/null)"; then
            fail "malformed JSONL record in HCL mode"
        fi
        record_mode="$(jq -r '.mode // empty' <<< "$record")"
        [[ -z "$record_mode" || "$record_mode" == "hcl" ]] || fail "record mode conflicts with HCL mode"
        scope="$(jq -r '.scope' <<< "$record")"
        [[ "$scope" == "$SCOPE_FILTER" ]] || continue
        address="$(jq -r '.address' <<< "$record")"
        disposition="$(jq -r '.disposition // empty' <<< "$record")"
        if [[ "$disposition" == "absent_create" ]]; then
            emit_status "excluded_by_disposition" "$scope" "$address" "absent_create deferred to convergence"
            jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" '{scope:$scope,address:$address,disposition:$disposition,observed_status:"excluded_by_disposition"}' >> "$reconciliation_file"
            continue
        fi
        if [[ "$disposition" != "import_candidate" && "$disposition" != "moved_candidate" ]]; then
            if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
                fail "HCL record disposition is not adoption-eligible"
            fi
            emit_status "excluded_by_disposition" "$scope" "$address" "record is outside the assessment import path"
            jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" '{scope:$scope,address:$address,disposition:$disposition,observed_status:"excluded_by_disposition"}' >> "$reconciliation_file"
            continue
        fi
        selected_count=$((selected_count + 1))
        resource_kind="$(jq -r '.resource_kind' <<< "$record")"
        if [[ "$disposition" == "moved_candidate" ]]; then
            move_from="$(jq -r '.move.from' <<< "$record")"
            move_to="$(jq -r '.move.to' <<< "$record")"
            move_canonical_id="$(jq -r '.move.canonical_id' <<< "$record")"
            move_state_lineage="$(jq -r '.move.state_lineage' <<< "$record")"
            [[ "$move_to" == "$address" ]] || fail "move destination must match manifest address: $address"
            [[ "$move_canonical_id" == "$(jq -r '.lookup.canonical_id' <<< "$record")" ]] || fail "move canonical identity does not match lookup identity"
            if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
                jq -e 'any(.required_capabilities[]; . == "state-move")' <<< "$HANDOFF_JSON" >/dev/null 2>&1 || fail "moved HCL adoption requires state-move capability"
                [[ "$move_state_lineage" == "$(jq -r '.state_boundary.lineage' <<< "$HANDOFF_JSON")" ]] || fail "move state lineage does not match handoff boundary"
                state_id=""
                if ! state_id="$(runner_state_identity "$scope" "$move_from")"; then
                    fail "HCL move source state inspection failed for $move_from"
                fi
                [[ "$state_id" == "$move_canonical_id" ]] || fail "HCL move source identity mismatch for $move_from"
                destination_state_id=""
                if destination_state_id="$(runner_state_identity "$scope" "$move_to")"; then
                    fail "HCL move destination is already managed: $move_to"
                else
                    state_rc=$?
                fi
                [[ "$state_rc" -eq 3 && -z "$destination_state_id" ]] || fail "HCL move destination state inspection failed for $move_to"
            fi
            printf '%s\n' "$record" >> "$records_file"
            continue
        fi
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
        declare -F runner_destination_exists >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_destination_exists"
        runner_destination_exists "$scope" "$destination" "$key" || fail "HCL configuration destination is not verified for $address"
        [[ "$canonical_id" != *$'\n'* && "$import_id" != *$'\n'* && "$key" != *$'\n'* ]] || fail "HCL adapter metadata contains a newline"
        terraform_expression_marker="\${"
        [[ "$canonical_id" != *"$terraform_expression_marker"* && "$import_id" != *"$terraform_expression_marker"* ]] || fail "HCL import IDs must be verified literals"
        state_id=""
        if state_id="$(runner_state_identity "$scope" "$address")"; then
            [[ "$state_id" == "$canonical_id" ]] || fail "HCL canonical identity mismatch for $address: state=$state_id expected=$canonical_id"
            jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" --arg canonical_id "$canonical_id" --argjson observed_identity "$resolved" '{scope:$scope,address:$address,disposition:$disposition,canonical_id:$canonical_id,observed_status:"already_managed",observed_identity:$observed_identity}' >> "$reconciliation_file"
            jq -cn --arg scope "$scope" --arg address "$address" --arg canonical_id "$canonical_id" --argjson observed_identity "$resolved" '{scope:$scope,address:$address,status:"verified",canonical_id:$canonical_id,observed_identity:$observed_identity}' >> "$live_verifications_file"
            continue
        else
            state_rc=$?
        fi
        [[ "$state_rc" -eq 3 && -z "$state_id" ]] || fail "HCL state inspection failed for $address"
        jq -c --arg scope "$scope" --arg address "$address" --arg resource_kind "$resource_kind" --argjson resolved "$resolved" '. + {scope:$scope,address:$address,resource_kind:$resource_kind} + $resolved' <<< "$record" >> "$records_file"
    done < "$MANIFEST"

    if [[ "$selected_count" -eq 0 ]]; then
        summary
        [[ "$FAILURE_SEEN" -eq 0 ]] || return 1
        return 0
    fi
    : > "$temp_hcl"
    jq -r 'select(.disposition == "import_candidate") | .resource_kind' "$records_file" | sort -u | while IFS= read -r kind; do
        [[ -n "$kind" ]] || continue
        local_name="$(printf '%s' "$kind" | sed 's/[^A-Za-z0-9_]/_/g')_import_ids"
        first_to="$(jq -r --arg kind "$kind" 'select(.disposition == "import_candidate" and .resource_kind == $kind) | .to' "$records_file" | head -n 1)"
        first_provider="$(jq -r --arg kind "$kind" 'select(.disposition == "import_candidate" and .resource_kind == $kind) | .provider' "$records_file" | head -n 1)"
        if [[ -z "$first_to" || -z "$first_provider" ]]; then
            fail "HCL adapter metadata is incomplete for resource kind: $kind"
        fi
        while IFS= read -r item; do
            [[ "$(jq -r '.to' <<< "$item")" == "$first_to" ]] || fail "HCL destination metadata is not homogeneous for resource kind: $kind"
            [[ "$(jq -r '.provider' <<< "$item")" == "$first_provider" ]] || fail "HCL provider metadata is not homogeneous for resource kind: $kind"
        done < <(jq -c --arg kind "$kind" 'select(.disposition == "import_candidate" and .resource_kind == $kind)' "$records_file")
        {
            printf 'locals {\n'
            printf '  %s = {\n' "$local_name"
            while IFS= read -r item; do
                key_json="$(jq -r '.key | @json' <<< "$item")"
                id_json="$(jq -r '.import_id | @json' <<< "$item")"
                printf '    %s = %s\n' "$key_json" "$id_json"
            done < <(jq -c --arg kind "$kind" 'select(.disposition == "import_candidate" and .resource_kind == $kind)' "$records_file")
            printf '  }\n}\n\n'
            printf 'import {\n'
            printf '  for_each = local.%s\n' "$local_name"
            printf '  to       = %s\n' "$first_to"
            printf '  id       = each.value\n'
            printf '  provider = %s\n' "$first_provider"
            printf '}\n\n'
        } >> "$temp_hcl"
    done
    mv -- "$temp_hcl" "$generated_hcl"
    printf 'Generated: %s\n' "$generated_hcl"

    if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
        declare -F runner_plan_saved >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_plan_saved"
        declare -F runner_apply_saved >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_apply_saved"
        [[ -n "$HANDOFF_RUN_ID" ]] || fail "live HCL execution requires a handoff run_id"
        plan_artifact_dir="$ROOT/.terraform-import-adoption"
        mkdir -p -- "$plan_artifact_dir"
        plan_artifact_path="$plan_artifact_dir/$HANDOFF_RUN_ID.plan"
        plan_envelope_path="$plan_artifact_dir/$HANDOFF_RUN_ID.plan-envelope.json"
        LIVE_PLAN_ARTIFACT_PATH="$plan_artifact_path"
        LIVE_PLAN_ENVELOPE_PATH="$plan_envelope_path"
        if [[ -f "$plan_artifact_path" || -f "$plan_envelope_path" ]]; then
            [[ -f "$plan_artifact_path" && -f "$plan_envelope_path" ]] || fail "saved plan records are incomplete for handoff run_id: $HANDOFF_RUN_ID"
            plan_json="$(jq -c '.plan' "$plan_envelope_path")" || fail "saved plan envelope is malformed"
        else
            if ! plan_json="$(runner_plan_saved "$ROOT" "$SCOPE_FILTER" "$generated_hcl" "$plan_artifact_path" "$records_file")"; then
                fail "HCL saved-plan generation failed; generated file retained"
            fi
            [[ -s "$plan_artifact_path" ]] || fail "HCL saved-plan capability produced no artifact"
        fi
        if ! plan_envelope="$(printf '%s\n' "$plan_json" | python3 "$SCRIPT_DIR/adoption_protocol.py" build-plan-envelope --handoff "$HANDOFF" --artifact "$plan_artifact_path")"; then
            fail "HCL saved plan failed protocol binding or adoption classification"
        fi
        if [[ -f "$plan_envelope_path" ]]; then
            if ! cmp -s <(printf '%s\n' "$plan_envelope") "$plan_envelope_path"; then
                fail "saved plan envelope changed for handoff run_id: $HANDOFF_RUN_ID"
            fi
        else
            printf '%s\n' "$plan_envelope" > "$plan_envelope_path"
        fi
        validate_saved_adoption_operations "$plan_envelope" "$records_file"
        authorization_path="$plan_artifact_dir/$HANDOFF_RUN_ID.authorization.json"
        authorization_json="$HANDOFF_JSON"
        write_immutable_record "$authorization_path" "$authorization_json"
        while IFS= read -r item; do
            disposition="$(jq -r '.disposition' <<< "$item")"
            address="$(jq -r '.address' <<< "$item")"
            if [[ "$disposition" == "moved_candidate" ]]; then
                jq -e --arg from "$(jq -r '.move.from' <<< "$item")" --arg to "$(jq -r '.move.to' <<< "$item")" 'any(.actions[]; .action == "moved" and .from == $from and .to == $to)' <<< "$plan_envelope" >/dev/null 2>&1 || fail "saved HCL adoption plan does not prove the requested state move"
            else
                jq -e --arg address "$address" 'any(.actions[]; .action == "import" and .address == $address)' <<< "$plan_envelope" >/dev/null 2>&1 || fail "saved HCL adoption plan does not prove the requested import: $address"
            fi
        done < "$records_file"
        confirm_live_identities_before_apply "$records_file"
        if ! runner_apply_saved "$ROOT" "$SCOPE_FILTER" "$generated_hcl" "$plan_artifact_path" "$records_file"; then
            fail "HCL exact saved-plan apply failed; generated file retained"
        fi
        while IFS= read -r item; do
            address="$(jq -r '.address' <<< "$item")"
            disposition="$(jq -r '.disposition' <<< "$item")"
            canonical_id="$(jq -r '.canonical_id // .lookup.canonical_id' <<< "$item")"
            if [[ "$disposition" == "moved_candidate" ]]; then
                address="$(jq -r '.move.to' <<< "$item")"
            fi
            state_id=""
            if ! state_id="$(runner_state_identity "$SCOPE_FILTER" "$address")"; then
                fail "HCL post-apply state verification failed for $address"
            fi
            [[ "$state_id" == "$canonical_id" ]] || fail "HCL post-apply identity mismatch for $address"
            if ! live_resolution="$(resolve_import_record "$item")"; then
                fail "HCL post-apply live verification failed for $address"
            fi
            live_status="$(jq -r '.status // empty' <<< "$live_resolution" 2>/dev/null || true)"
            [[ -z "$live_status" ]] || fail "HCL post-apply live verification returned $live_status for $address"
            [[ "$(jq -r '.canonical_id // empty' <<< "$live_resolution")" == "$canonical_id" ]] || fail "HCL post-apply live identity mismatch for $address"
            jq -cn --arg scope "$SCOPE_FILTER" --arg address "$address" --arg canonical_id "$canonical_id" --argjson observed_identity "$live_resolution" '{scope:$scope,address:$address,status:"verified",canonical_id:$canonical_id,observed_identity:$observed_identity}' >> "$live_verifications_file"
            if [[ "$disposition" == "moved_candidate" ]]; then
                emit_status "moved" "$SCOPE_FILTER" "$address" "state-only move verified"
                jq -cn --arg scope "$SCOPE_FILTER" --arg address "$address" --arg disposition "$disposition" --arg canonical_id "$canonical_id" --arg from "$(jq -r '.move.from' <<< "$item")" --arg to "$address" --argjson observed_identity "$live_resolution" '{scope:$scope,address:$address,disposition:$disposition,canonical_id:$canonical_id,from:$from,to:$to,observed_status:"moved_verified",observed_identity:$observed_identity}' >> "$reconciliation_file"
            else
                emit_status "imported" "$SCOPE_FILTER" "$address" "exact saved-plan apply verified"
                IMPORTED=$((IMPORTED + 1))
                jq -cn --arg scope "$SCOPE_FILTER" --arg address "$address" --arg disposition "$disposition" --arg canonical_id "$canonical_id" --argjson observed_identity "$live_resolution" '{scope:$scope,address:$address,disposition:$disposition,canonical_id:$canonical_id,observed_status:"imported",observed_identity:$observed_identity}' >> "$reconciliation_file"
            fi
        done < "$records_file"
        if ! runner_plan "$ROOT" "$SCOPE_FILTER" "$generated_hcl"; then
            fail "HCL post-import plan failed; generated file retained"
        fi
            local post_plan_json post_plan_classification
        if ! post_plan_json="$(runner_plan_json "$ROOT" "$SCOPE_FILTER" "$generated_hcl")"; then
            fail "HCL post-import machine-readable plan failed; generated file retained"
        fi
        if ! post_plan_classification="$(printf '%s\n' "$post_plan_json" | python3 "$SCRIPT_DIR/adoption_protocol.py" classify-plan)"; then
            fail "HCL post-import plan is not machine-readable; generated file retained"
        fi
        if ! jq -e '.allowed == true' <<< "$post_plan_classification" >/dev/null 2>&1; then
            fail "HCL post-import plan contains disallowed actions; generated file retained"
        fi
        evidence_path="$plan_artifact_dir/$HANDOFF_RUN_ID.evidence.json"
        recovery_path="$plan_artifact_dir/$HANDOFF_RUN_ID.recovery.json"
        receipt_path="$plan_artifact_dir/$HANDOFF_RUN_ID.receipt.json"
        imports_json="$(jq -sc 'map(select(.disposition == "import_candidate") | {scope,address,identity:.canonical_id,import_id:.import_id})' "$records_file")"
        moves_json="$(jq -sc 'map(select(.disposition == "moved_candidate") | {scope,address,from:.move.from,to:.move.to,identity:.lookup.canonical_id})' "$records_file")"
        final_state_identities="$(jq -sc 'map({(.address): (.canonical_id // .lookup.canonical_id)}) | add // {}' "$records_file")"
        live_verifications="$(jq -sc '.' "$live_verifications_file")"
        evidence_json="$(build_runtime_evidence_record \
            "$evidence_path" "$plan_artifact_path" "$plan_envelope_path" \
            "$plan_envelope" "$post_plan_classification" "$records_file" \
            "$final_state_identities" "$live_verifications" "$reconciliation_file")" || fail "runtime evidence construction failed"
        persist_completion_records \
            "$evidence_path" "$recovery_path" "$receipt_path" \
            "$authorization_json" "$evidence_json" "$plan_envelope" \
            "$imports_json" "$moves_json" "$final_state_identities" \
            "$live_verifications" "$post_plan_json" "completed"
        rm -f -- "$generated_hcl"
        printf 'Verified: state identity and post-import plan; removed generated file\n'
    fi
}
    run_script_live_mode() {
        local records_file line record scope address disposition resolved resolution_status
        local state_id state_rc canonical_id selected_count=0
        local reconciliation_file live_verifications_file
        local plan_artifact_dir plan_artifact_path plan_envelope_path plan_json plan_envelope
        local authorization_path evidence_path recovery_path receipt_path
        local authorization_json evidence_json recovery_json receipt_input receipt_json
        local post_plan_json post_plan_classification imports_json moves_json
        local final_state_identities live_verifications final_status item move_from move_to
        local move_canonical_id move_state_lineage destination_state_id
        local live_resolution live_resolution_status

        HCL_TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/terraform-import-script.XXXXXX")"
        trap 'cleanup_normalized_manifest; if [[ -n "${HCL_TMP_DIR:-}" && -d "$HCL_TMP_DIR" ]]; then rm -rf -- "$HCL_TMP_DIR"; fi' EXIT
        LIVE_RECOVERY_PATH="$ROOT/.terraform-import-adoption/$HANDOFF_RUN_ID.recovery.json"
        records_file="$HCL_TMP_DIR/adoption.jsonl"
        reconciliation_file="$HCL_TMP_DIR/reconciliation.jsonl"
        live_verifications_file="$HCL_TMP_DIR/live-verifications.jsonl"
        : > "$records_file"
        : > "$reconciliation_file"
        : > "$live_verifications_file"

        while IFS= read -r line || [[ -n "$line" ]]; do
            [[ -z "${line//[[:space:]]/}" ]] && continue
            if ! record="$(printf '%s\n' "$line" | jq -ce 'if type == "object" and (.scope|type) == "string" and (.address|type) == "string" and (.resource_kind|type) == "string" and (.lookup|type) == "object" then . else error("record must contain scope, address, resource_kind, and lookup") end' 2>/dev/null)"; then
                fail "malformed JSONL record in script mode"
            fi
            scope="$(jq -r '.scope' <<< "$record")"
            [[ -z "$SCOPE_FILTER" || "$scope" == "$SCOPE_FILTER" ]] || continue
            address="$(jq -r '.address' <<< "$record")"
            disposition="$(jq -r '.disposition // empty' <<< "$record")"
            if [[ "$disposition" == "absent_create" ]]; then
                emit_status "excluded_by_disposition" "$scope" "$address" "absent_create deferred to convergence"
                jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" '{scope:$scope,address:$address,disposition:$disposition,observed_status:"excluded_by_disposition"}' >> "$reconciliation_file"
                continue
            fi
            if [[ "$disposition" != "import_candidate" && "$disposition" != "moved_candidate" ]]; then
                fail "record disposition is not adoption-eligible for $address"
            fi
            if [[ "$disposition" == "moved_candidate" ]]; then
                declare -F runner_move >/dev/null 2>&1 || fail "adapter capability is missing: runner_move"
                jq -e 'any(.required_capabilities[]; . == "state-move")' <<< "$HANDOFF_JSON" >/dev/null 2>&1 || fail "moved adoption requires state-move capability"
                move_from="$(jq -r '.move.from' <<< "$record")"
                move_to="$(jq -r '.move.to' <<< "$record")"
                move_canonical_id="$(jq -r '.move.canonical_id' <<< "$record")"
                move_state_lineage="$(jq -r '.move.state_lineage' <<< "$record")"
                [[ "$move_to" == "$address" ]] || fail "move destination must match manifest address: $address"
                [[ "$move_state_lineage" == "$(jq -r '.state_boundary.lineage' <<< "$HANDOFF_JSON")" ]] || fail "move state lineage does not match handoff boundary"
                [[ "$move_canonical_id" == "$(jq -r '.lookup.canonical_id' <<< "$record")" ]] || fail "move canonical identity does not match lookup identity"
                state_id=""
                if ! state_id="$(runner_state_identity "$scope" "$move_from")"; then
                    fail "move source state inspection failed for $move_from"
                fi
                [[ "$state_id" == "$move_canonical_id" ]] || fail "move source identity mismatch for $move_from"
                destination_state_id=""
                if destination_state_id="$(runner_state_identity "$scope" "$move_to")"; then
                    fail "move destination is already managed: $move_to"
                else
                    state_rc=$?
                fi
                [[ "$state_rc" -eq 3 && -z "$destination_state_id" ]] || fail "move destination state inspection failed for $move_to"
                printf '%s\n' "$record" >> "$records_file"
                selected_count=$((selected_count + 1))
                continue
            fi

            resolved=""
            if ! resolved="$(resolve_import_record "$record")"; then
                emit_status "terraform_error" "$scope" "$address" "resource adapter failed"
                TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
                record_failure
                [[ "$STOP_REQUESTED" -eq 1 ]] && break
                continue
            fi
            resolution_status="$(jq -r '.status // empty' <<< "$resolved" 2>/dev/null || true)"
            case "$resolution_status" in
                not_found)
                    emit_status "not_found" "$scope" "$address" "resource adapter found no identity"
                    NOT_FOUND=$((NOT_FOUND + 1))
                    record_failure
                    ;;
                ambiguous)
                    emit_status "ambiguous" "$scope" "$address" "resource identity is ambiguous"
                    AMBIGUOUS=$((AMBIGUOUS + 1))
                    record_failure
                    ;;
                aws_error)
                    emit_status "aws_error" "$scope" "$address" "resource adapter reported an AWS error"
                    AWS_ERROR=$((AWS_ERROR + 1))
                    record_failure
                    ;;
                terraform_error)
                    emit_status "terraform_error" "$scope" "$address" "resource adapter reported a Terraform error"
                    TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
                    record_failure
                    ;;
                *)
                    if ! jq -e 'type == "object" and (.canonical_id|type) == "string" and (.import_id|type) == "string" and (.canonical_id|length) > 0 and (.import_id|length) > 0' <<< "$resolved" >/dev/null 2>&1; then
                        fail "resource adapter returned incomplete identity for $address"
                    fi
                    canonical_id="$(jq -r '.canonical_id' <<< "$resolved")"
                    state_id=""
                    if state_id="$(runner_state_identity "$scope" "$address")"; then
                        if [[ "$state_id" == "$canonical_id" ]]; then
                            emit_status "skipped_already_managed" "$scope" "$address" "state identity matches"
                            SKIPPED_ALREADY_MANAGED=$((SKIPPED_ALREADY_MANAGED + 1))
                            jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" --arg canonical_id "$canonical_id" --argjson observed_identity "$resolved" '{scope:$scope,address:$address,disposition:$disposition,canonical_id:$canonical_id,observed_status:"already_managed",observed_identity:$observed_identity}' >> "$reconciliation_file"
                            jq -cn --arg scope "$scope" --arg address "$address" --arg canonical_id "$canonical_id" --argjson observed_identity "$resolved" '{scope:$scope,address:$address,status:"verified",canonical_id:$canonical_id,observed_identity:$observed_identity}' >> "$live_verifications_file"
                            continue
                        fi
                        emit_status "ambiguous" "$scope" "$address" "state identity mismatch"
                        AMBIGUOUS=$((AMBIGUOUS + 1))
                        record_failure
                        [[ "$STOP_REQUESTED" -eq 1 ]] && break
                        continue
                    else
                        state_rc=$?
                    fi
                    if [[ "$state_rc" -ne 3 || -n "$state_id" ]]; then
                        fail "state inspection failed for $address"
                    fi
                    record="$(jq -c --arg canonical_id "$canonical_id" --arg import_id "$(jq -r '.import_id' <<< "$resolved")" '.lookup.canonical_id = $canonical_id | .lookup.import_id = $import_id' <<< "$record")"
                    printf '%s\n' "$record" >> "$records_file"
                    selected_count=$((selected_count + 1))
                    ;;
            esac
            [[ "$STOP_REQUESTED" -eq 1 ]] && break
        done < "$MANIFEST"

        [[ "$STOP_REQUESTED" -eq 0 ]] || fail "live script reconciliation failed before mutation"
        if [[ "$selected_count" -eq 0 ]]; then
            summary
            [[ "$FAILURE_SEEN" -eq 0 ]] || return 1
            return 0
        fi

        declare -F runner_plan_saved >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_plan_saved"
        declare -F runner_apply_saved >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_apply_saved"
        [[ -n "$HANDOFF_RUN_ID" ]] || fail "live script execution requires a handoff run_id"
        plan_artifact_dir="$ROOT/.terraform-import-adoption"
        mkdir -p -- "$plan_artifact_dir"
        plan_artifact_path="$plan_artifact_dir/$HANDOFF_RUN_ID.plan"
        plan_envelope_path="$plan_artifact_dir/$HANDOFF_RUN_ID.plan-envelope.json"
        LIVE_PLAN_ARTIFACT_PATH="$plan_artifact_path"
        LIVE_PLAN_ENVELOPE_PATH="$plan_envelope_path"
        if [[ -f "$plan_artifact_path" || -f "$plan_envelope_path" ]]; then
            [[ -f "$plan_artifact_path" && -f "$plan_envelope_path" ]] || fail "saved plan records are incomplete for handoff run_id: $HANDOFF_RUN_ID"
            plan_json="$(jq -c '.plan' "$plan_envelope_path")" || fail "saved plan envelope is malformed"
        else
            if ! plan_json="$(runner_plan_saved "$ROOT" "$SCOPE_FILTER" "$records_file" "$plan_artifact_path")"; then
                fail "script saved-plan generation failed"
            fi
            [[ -s "$plan_artifact_path" ]] || fail "script saved-plan capability produced no artifact"
        fi
        if ! plan_envelope="$(printf '%s\n' "$plan_json" | python3 "$SCRIPT_DIR/adoption_protocol.py" build-plan-envelope --handoff "$HANDOFF" --artifact "$plan_artifact_path")"; then
            fail "script saved plan failed protocol binding or adoption classification"
        fi
        if [[ -f "$plan_envelope_path" ]]; then
            cmp -s <(printf '%s\n' "$plan_envelope") "$plan_envelope_path" || fail "saved plan envelope changed for handoff run_id: $HANDOFF_RUN_ID"
        else
            printf '%s\n' "$plan_envelope" > "$plan_envelope_path"
        fi
        validate_saved_adoption_operations "$plan_envelope" "$records_file"

        while IFS= read -r item; do
            disposition="$(jq -r '.disposition' <<< "$item")"
            address="$(jq -r '.address' <<< "$item")"
            if [[ "$disposition" == "moved_candidate" ]]; then
                move_from="$(jq -r '.move.from' <<< "$item")"
                move_to="$(jq -r '.move.to' <<< "$item")"
                move_canonical_id="$(jq -r '.move.canonical_id' <<< "$item")"
                [[ "$move_to" == "$address" ]] || fail "move destination must match manifest address: $address"
                [[ "$(jq -r '.move.state_lineage' <<< "$item")" == "$(jq -r '.state_boundary.lineage' <<< "$HANDOFF_JSON")" ]] || fail "move state lineage does not match handoff boundary"
                jq -e --arg from "$move_from" --arg to "$move_to" 'any(.actions[]; .action == "moved" and .from == $from and .to == $to)' <<< "$plan_envelope" >/dev/null 2>&1 || fail "saved adoption plan does not prove the requested state move"
                [[ "$move_canonical_id" == "$(jq -r '.lookup.canonical_id' <<< "$item")" ]] || fail "move canonical identity does not match lookup identity"
            else
                jq -e --arg address "$address" 'any(.actions[]; .action == "import" and .address == $address)' <<< "$plan_envelope" >/dev/null 2>&1 || fail "saved adoption plan does not prove the requested import: $address"
            fi
        done < "$records_file"

        authorization_path="$plan_artifact_dir/$HANDOFF_RUN_ID.authorization.json"
        authorization_json="$HANDOFF_JSON"
        write_immutable_record "$authorization_path" "$authorization_json"
        confirm_live_identities_before_apply "$records_file"
        if ! runner_apply_saved "$ROOT" "$SCOPE_FILTER" "$records_file" "$plan_artifact_path"; then
            fail "script exact saved-plan apply failed"
        fi

        while IFS= read -r item; do
            scope="$(jq -r '.scope' <<< "$item")"
            address="$(jq -r '.address' <<< "$item")"
            disposition="$(jq -r '.disposition' <<< "$item")"
            canonical_id="$(jq -r '.lookup.canonical_id' <<< "$item")"
            if [[ "$disposition" == "moved_candidate" ]]; then
                address="$(jq -r '.move.to' <<< "$item")"
            fi
            if ! state_id="$(runner_state_identity "$scope" "$address")"; then
                fail "post-apply state verification failed for $address"
            fi
            [[ "$state_id" == "$canonical_id" ]] || fail "post-apply identity mismatch for $address"
            if ! live_resolution="$(resolve_import_record "$item")"; then
                fail "post-apply live verification failed for $address"
            fi
            live_resolution_status="$(jq -r '.status // empty' <<< "$live_resolution" 2>/dev/null || true)"
            [[ -z "$live_resolution_status" ]] || fail "post-apply live verification returned $live_resolution_status for $address"
            [[ "$(jq -r '.canonical_id // empty' <<< "$live_resolution")" == "$canonical_id" ]] || fail "post-apply live identity mismatch for $address"
            jq -cn --arg scope "$scope" --arg address "$address" --arg canonical_id "$canonical_id" --argjson observed_identity "$live_resolution" '{scope:$scope,address:$address,status:"verified",canonical_id:$canonical_id,observed_identity:$observed_identity}' >> "$live_verifications_file"
            if [[ "$disposition" == "moved_candidate" ]]; then
                emit_status "moved" "$scope" "$address" "state-only move verified"
                jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" --arg canonical_id "$canonical_id" --arg from "$move_from" --arg to "$move_to" --argjson observed_identity "$live_resolution" '{scope:$scope,address:$address,disposition:$disposition,canonical_id:$canonical_id,from:$from,to:$to,observed_status:"moved_verified",observed_identity:$observed_identity}' >> "$reconciliation_file"
            else
                emit_status "imported" "$scope" "$address" "exact saved-plan apply verified"
                IMPORTED=$((IMPORTED + 1))
                jq -cn --arg scope "$scope" --arg address "$address" --arg disposition "$disposition" --arg canonical_id "$canonical_id" --argjson observed_identity "$live_resolution" '{scope:$scope,address:$address,disposition:$disposition,canonical_id:$canonical_id,observed_status:"imported",observed_identity:$observed_identity}' >> "$reconciliation_file"
            fi
        done < "$records_file"

        if ! runner_plan "$ROOT" "$SCOPE_FILTER" "$records_file"; then
            fail "script post-import plan failed"
        fi
        if ! post_plan_json="$(runner_plan_json "$ROOT" "$SCOPE_FILTER" "$records_file")"; then
            fail "script post-import machine-readable plan failed"
        fi
        if ! post_plan_classification="$(printf '%s\n' "$post_plan_json" | python3 "$SCRIPT_DIR/adoption_protocol.py" classify-plan)"; then
            fail "script post-import plan is not machine-readable"
        fi
        jq -e '.allowed == true' <<< "$post_plan_classification" >/dev/null 2>&1 || fail "script post-import plan contains disallowed actions"

        evidence_path="$plan_artifact_dir/$HANDOFF_RUN_ID.evidence.json"
        recovery_path="$plan_artifact_dir/$HANDOFF_RUN_ID.recovery.json"
        receipt_path="$plan_artifact_dir/$HANDOFF_RUN_ID.receipt.json"
        imports_json="$(jq -sc 'map(select(.disposition == "import_candidate") | {scope,address,identity:.lookup.canonical_id,import_id:.lookup.import_id})' "$records_file")"
        moves_json="$(jq -sc 'map(select(.disposition == "moved_candidate") | {scope,address,from:.move.from,to:.move.to,identity:.lookup.canonical_id})' "$records_file")"
        final_state_identities="$(jq -sc 'map({(.address): .lookup.canonical_id}) | add // {}' "$records_file")"
        live_verifications="$(jq -sc '.' "$live_verifications_file")"
        evidence_json="$(build_runtime_evidence_record \
            "$evidence_path" "$plan_artifact_path" "$plan_envelope_path" \
            "$plan_envelope" "$post_plan_classification" "$records_file" \
            "$final_state_identities" "$live_verifications" "$reconciliation_file")" || fail "runtime evidence construction failed"
        final_status="completed"
        [[ "$FAILURE_SEEN" -eq 0 ]] || final_status="failed"
        persist_completion_records \
            "$evidence_path" "$recovery_path" "$receipt_path" \
            "$authorization_json" "$evidence_json" "$plan_envelope" \
            "$imports_json" "$moves_json" "$final_state_identities" \
            "$live_verifications" "$post_plan_json" "$final_status"
        summary
        [[ "$FAILURE_SEEN" -eq 0 ]] || return 1
        return 0
    }


if [[ "$MODE" == "hcl" ]]; then
    for required_function in runner_preflight runner_state_identity runner_plan runner_destination_exists resolve_import_record; do
        declare -F "$required_function" >/dev/null 2>&1 || fail "adapter capability is missing: $required_function"
    done
    if ! runner_preflight "$ROOT"; then
        fail "runner adapter capability preflight failed"
    fi
    run_hcl_mode
    exit 0
fi

if [[ "$LIVE_ALLOWED" -eq 1 ]]; then
    if run_script_live_mode; then
        exit 0
    else
        script_exit_code=$?
        exit "$script_exit_code"
    fi
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
    DISPOSITION="$(jq -r '.disposition // empty' <<< "$RECORD")"
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
    if [[ "$DISPOSITION" == "moved_candidate" ]]; then
        if [[ "$LIVE_ALLOWED" -eq 0 ]]; then
            emit_status "excluded_by_disposition" "$SCOPE" "$ADDRESS" "moved candidate requires live state migration"
            continue
        fi
        declare -F runner_move >/dev/null 2>&1 || fail "runner adapter capability is missing: runner_move"
        jq -e 'any(.required_capabilities[]; . == "state-move")' <<< "$HANDOFF_JSON" >/dev/null 2>&1 || fail "moved adoption requires state-move capability"
        MOVE_FROM="$(jq -r '.move.from' <<< "$RECORD")"
        MOVE_TO="$(jq -r '.move.to' <<< "$RECORD")"
        MOVE_CANONICAL_ID="$(jq -r '.move.canonical_id' <<< "$RECORD")"
        MOVE_LINEAGE="$(jq -r '.move.state_lineage' <<< "$RECORD")"
        STATE_LINEAGE="$(jq -r '.state_boundary.lineage' <<< "$HANDOFF_JSON")"
        [[ "$MOVE_TO" == "$ADDRESS" ]] || fail "move destination must match manifest address: $ADDRESS"
        [[ "$MOVE_LINEAGE" == "$STATE_LINEAGE" ]] || fail "move state lineage does not match handoff boundary"
        jq -e --arg from "$MOVE_FROM" --arg to "$MOVE_TO" 'any(.actions[]; .action == "moved" and .from == $from and .to == $to)' <<< "$PLAN_CLASSIFICATION" >/dev/null 2>&1 || fail "saved adoption plan does not prove the requested state move"
        if ! runner_move "$SCOPE" "$MOVE_FROM" "$MOVE_TO"; then
            emit_status "terraform_error" "$SCOPE" "$ADDRESS" "state move failed"
            TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
            record_failure
            [[ "$STOP_REQUESTED" -eq 1 ]] && break
            continue
        fi
        if ! MOVE_STATE_ID="$(runner_state_identity "$SCOPE" "$MOVE_TO")"; then
            fail "state move destination verification failed for $ADDRESS"
        fi
        [[ "$MOVE_STATE_ID" == "$MOVE_CANONICAL_ID" ]] || fail "state move identity mismatch for $ADDRESS"
        emit_status "moved" "$SCOPE" "$ADDRESS" "state-only move verified"
        continue
    fi
    if [[ "$LIVE_ALLOWED" -eq 1 && "$DISPOSITION" == "absent_create" ]]; then
        emit_status "excluded_by_disposition" "$SCOPE" "$ADDRESS" "absent_create deferred to convergence"
        continue
    fi
    if [[ "$LIVE_ALLOWED" -eq 0 && "$DISPOSITION" != "import_candidate" ]]; then
        emit_status "excluded_by_disposition" "$SCOPE" "$ADDRESS" "record is outside the assessment import path"
        continue
    fi
    [[ "$LIVE_ALLOWED" -eq 0 || "$DISPOSITION" == "import_candidate" ]] || {
        emit_status "terraform_error" "$SCOPE" "$ADDRESS" "record disposition is not adoption-eligible"
        TERRAFORM_ERROR=$((TERRAFORM_ERROR + 1))
        printf 'ERROR: record disposition is not adoption-eligible for %s\n' "$ADDRESS" >&2
        record_failure
        [[ "$STOP_REQUESTED" -eq 1 ]] && break
        continue
    }

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
