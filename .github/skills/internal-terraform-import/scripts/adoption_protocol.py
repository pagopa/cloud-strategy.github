"""Provider-neutral contracts for Terraform/OpenTofu adoption runs."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping, Sequence
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePath
from typing import Any


class ProtocolError(ValueError):
    """Raised when an adoption protocol record cannot be trusted."""


SAFE_PLAN_ACTIONS = {"import", "no-op", "moved"}
KNOWN_PLAN_ACTIONS = SAFE_PLAN_ACTIONS | {
    "create",
    "update",
    "delete",
    "replace",
    "unknown",
}
DISPOSITIONS = {
    "already_managed",
    "import_candidate",
    "absent_create",
    "moved_candidate",
    "collision",
    "ambiguous_live_identity",
    "state_identity_mismatch",
    "disputed_ownership",
    "undeclared_remote",
    "unsupported_capability",
    "excluded_by_scope",
}
ADOPTION_DISPOSITIONS = {"import_candidate", "moved_candidate"}
PLAN_CONTEXT_FIELDS = (
    "run_id",
    "consumer_root",
    "state_scope",
    "state_lineage",
    "state_serial",
    "configuration_digest",
    "dependency_lock_digest",
    "decision_id",
    "execution_mode",
    "import_mode",
    "authorized_scopes",
)
RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
PRIMARY_OWNER = "/internal-terraform"
EXECUTION_OWNER = "/internal-terraform-import"


def _require_object(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ProtocolError(f"{field} must be an object")
    return dict(value)


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolError(f"{field} must be a non-empty string")
    return value


def _require_run_id(value: object, field: str = "run_id") -> str:
    run_id = _require_string(value, field)
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ProtocolError(
            f"{field} must contain only letters, numbers, dots, underscores, and hyphens"
        )
    return run_id


def _require_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ProtocolError(f"{field} must be a list of non-empty strings")
    result = [_require_string(item, f"{field}[]") for item in value]
    if not result or len(result) != len(set(result)):
        raise ProtocolError(f"{field} must contain unique values")
    return result


def _require_tool_versions(value: object) -> dict[str, str]:
    versions = _require_object(value, "tool_versions")
    if not versions:
        raise ProtocolError("tool_versions must contain at least one tool")
    validated: dict[str, str] = {}
    for name, version in versions.items():
        validated[_require_string(name, "tool_versions[]")] = _require_string(
            version, f"tool_versions.{name}"
        )
    return validated


def _require_absolute_path(value: object, field: str) -> str:
    path = _require_string(value, field)
    if not PurePath(path).is_absolute():
        raise ProtocolError(f"{field} must be an absolute path")
    return path


def _is_path_within(path: str, root: str) -> bool:
    try:
        Path(path).resolve(strict=False).relative_to(Path(root).resolve(strict=False))
    except ValueError:
        return False
    return True


def _require_status(document: Mapping[str, object], field: str, allowed: set[str]) -> str:
    value = _require_string(document.get(field), field)
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ProtocolError(f"{field} must be one of: {choices}")
    return value


def _validate_authority_record(
    value: object,
    field: str,
    *,
    decision_id: str,
    consumer_root: str,
    scopes: list[str],
    mode: str,
) -> dict[str, Any]:
    authority = _require_object(value, field)
    _require_status(authority, "status", {"approved", "not-approved", "unknown", "pending"})
    _require_string(authority.get("actor"), f"{field}.actor")
    if authority.get("decision_id") != decision_id:
        raise ProtocolError(f"{field}.decision_id does not match decision_id")
    if authority.get("consumer_root") != consumer_root:
        raise ProtocolError(f"{field}.consumer_root does not match consumer_root")
    if set(_require_string_list(authority.get("scopes"), f"{field}.scopes")) != set(scopes):
        raise ProtocolError(f"{field}.scopes do not match scopes")
    if authority.get("mode") != mode:
        raise ProtocolError(f"{field}.mode does not match mode")
    return authority


def validate_handoff(
    document: Mapping[str, object],
    *,
    live: bool = False,
    expected_root: str | None = None,
    expected_mode: str | None = None,
    expected_scopes: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Validate and return an immutable-by-convention handoff projection."""

    handoff = _require_object(document, "handoff")
    schema_version = handoff.get("schema_version")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool):
        raise ProtocolError("handoff schema_version must be an integer")
    if schema_version not in {1, 2}:
        raise ProtocolError("handoff schema_version must be 1 or 2")
    if handoff.get("kind") != "internal-terraform-import-handoff":
        raise ProtocolError("handoff kind is invalid")

    decision = _require_string(handoff.get("decision"), "decision")
    if decision not in {"assess", "execute"}:
        raise ProtocolError("decision must be assess or execute")
    consumer_root = _require_absolute_path(handoff.get("consumer_root"), "consumer_root")
    mode = _require_string(handoff.get("mode"), "mode")
    if mode not in {"script", "hcl"}:
        raise ProtocolError("mode must be script or hcl")
    scopes = _require_string_list(handoff.get("scopes"), "scopes")
    _require_string(handoff.get("approval_reference"), "approval_reference")
    _validate_wrapper_projection(handoff, consumer_root, mode, scopes)

    if expected_root is not None and consumer_root != expected_root:
        raise ProtocolError("handoff consumer root does not match canonical run root")
    if expected_mode is not None and mode != expected_mode:
        raise ProtocolError("handoff mode does not match run mode")
    if expected_scopes is not None and set(scopes) != set(expected_scopes):
        raise ProtocolError("handoff scopes do not match the run")

    if live and schema_version != 2:
        raise ProtocolError("live execution requires handoff schema_version 2")

    if schema_version == 2:
        _validate_v2_fields(handoff, consumer_root, scopes, mode, live)
    elif decision != "assess":
        raise ProtocolError("protocol v1 supports assessment only")
    elif live:
        raise ProtocolError("live execution requires protocol v2 evidence")

    return deepcopy(handoff)


def _validate_wrapper_projection(
    handoff: Mapping[str, object],
    consumer_root: str,
    mode: str,
    scopes: list[str],
) -> None:
    primary_owner = _require_string(handoff.get("primary_owner"), "primary_owner")
    if primary_owner != PRIMARY_OWNER:
        raise ProtocolError(f"primary_owner must be {PRIMARY_OWNER}")
    execution_owner = _require_string(
        handoff.get("execution_owner"), "execution_owner"
    )
    if execution_owner != EXECUTION_OWNER:
        raise ProtocolError(f"execution_owner must be {EXECUTION_OWNER}")
    _require_string(handoff.get("reason"), "reason")

    context = _require_object(handoff.get("context"), "context")
    context_root = _require_absolute_path(
        context.get("consumer_root"), "context.consumer_root"
    )
    if context_root != consumer_root:
        raise ProtocolError("context.consumer_root does not match consumer_root")
    if context.get("mode") != mode:
        raise ProtocolError("context.mode does not match mode")
    context_scopes = _require_string_list(context.get("scopes"), "context.scopes")
    if set(context_scopes) != set(scopes):
        raise ProtocolError("context.scopes do not match scopes")

    safety_evidence = _require_object(
        handoff.get("safety_evidence"), "safety_evidence"
    )
    if not safety_evidence:
        raise ProtocolError("safety_evidence must not be empty")
    _require_string(handoff.get("validation"), "validation")


def _validate_v2_fields(
    handoff: Mapping[str, object],
    consumer_root: str,
    scopes: list[str],
    mode: str,
    live: bool,
) -> None:
    _require_run_id(handoff.get("run_id"))
    decision_id = _require_string(handoff.get("decision_id"), "decision_id")
    runtime = _require_string(handoff.get("runtime"), "runtime")
    if runtime not in {"terraform", "tofu"}:
        raise ProtocolError("runtime must be terraform or tofu")
    _require_string(handoff.get("runtime_version"), "runtime_version")
    execution_mode = _require_string(handoff.get("execution_mode"), "execution_mode")
    if execution_mode not in {"inspect", "generate", "import", "converge"}:
        raise ProtocolError("execution_mode is invalid")
    if execution_mode in {"generate", "import", "converge"}:
        import_mode = _require_string(handoff.get("import_mode"), "import_mode")
        if import_mode not in {"script", "hcl"} or import_mode != mode:
            raise ProtocolError("import_mode must match the selected mode")
    for field in (
        "canonical_identity_status",
        "desired_status",
        "live_status",
        "state_status",
    ):
        _require_status(handoff, field, {"verified", "pending", "unknown", "not-applicable"})

    state_boundary = _require_object(handoff.get("state_boundary"), "state_boundary")
    state_scope = _require_string(state_boundary.get("scope"), "state_boundary.scope")
    if state_scope not in scopes:
        raise ProtocolError("state_boundary.scope must be included in scopes")
    _require_string(state_boundary.get("lineage"), "state_boundary.lineage")
    serial = state_boundary.get("serial")
    if not isinstance(serial, int) or isinstance(serial, bool) or serial < 0:
        raise ProtocolError("state_boundary.serial must be a non-negative integer")

    runner = _require_object(handoff.get("runner"), "runner")
    runner_path = _require_absolute_path(runner.get("path"), "runner.path")
    if not _is_path_within(runner_path, consumer_root):
        raise ProtocolError("runner.path must be inside consumer_root")
    declared_runner_path = _require_absolute_path(
        handoff.get("runner_path"), "runner_path"
    )
    if declared_runner_path != runner_path:
        raise ProtocolError("runner_path does not match runner.path")
    runner_capabilities = set(_require_string_list(runner.get("capabilities"), "runner.capabilities"))
    declared_runner_capabilities = set(
        _require_string_list(handoff.get("runner_capabilities"), "runner_capabilities")
    )
    if declared_runner_capabilities != runner_capabilities:
        raise ProtocolError("runner_capabilities do not match runner.capabilities")
    required_capabilities = _require_string_list(
        handoff.get("required_capabilities"), "required_capabilities"
    )
    missing = sorted(set(required_capabilities) - runner_capabilities)
    if missing:
        raise ProtocolError(
            "runner is missing required capabilities: " + ", ".join(missing)
        )

    _require_status(handoff, "identity_status", {"verified", "pending", "unknown"})
    _require_status(
        handoff, "reconciliation_status", {"complete", "pending", "unknown"}
    )
    _require_status(
        handoff,
        "ownership_disposition",
        {"unmanaged", "already_managed", "transferred", "disputed", "unknown"},
    )
    mutation_authority: dict[str, Any] | None = None
    if execution_mode in {"import", "converge"}:
        mutation_authority = _validate_authority_record(
            handoff.get("mutation_authority"),
            "mutation_authority",
            decision_id=decision_id,
            consumer_root=consumer_root,
            scopes=scopes,
            mode=mode,
        )
    _require_status(handoff, "runner_status", {"verified", "pending", "unknown"})
    _require_status(
        handoff,
        "convergence_decision",
        {"adoption-only", "converge-separately", "converge"},
    )
    adoption_decision = _require_string(handoff.get("adoption_decision"), "adoption_decision")
    if adoption_decision not in {"adopt", "defer", "blocked", "unknown"}:
        raise ProtocolError("adoption_decision is invalid")
    _require_status(handoff, "recovery_status", {"ready", "pending", "unknown"})
    recovery_path = _require_absolute_path(handoff.get("recovery_path"), "recovery_path")
    recovery_dir = (Path(consumer_root) / ".terraform-import-adoption").resolve(strict=False)
    if Path(recovery_path).resolve(strict=False).parent != recovery_dir:
        raise ProtocolError("recovery_path must be inside .terraform-import-adoption")
    if Path(recovery_path).name != f"{handoff['run_id']}.recovery.json":
        raise ProtocolError("recovery_path must match the handoff run_id")
    _require_string(handoff.get("environment_criticality"), "environment_criticality")
    _require_string_list(handoff.get("evidence_references"), "evidence_references")
    _require_string(handoff.get("configuration_digest"), "configuration_digest")
    _require_string(handoff.get("dependency_lock_digest"), "dependency_lock_digest")
    _require_tool_versions(handoff.get("tool_versions"))
    convergence_authority: dict[str, Any] | None = None
    if execution_mode == "generate":
        output_authority = _validate_authority_record(
            handoff.get("output_authorization"),
            "output_authorization",
            decision_id=decision_id,
            consumer_root=consumer_root,
            scopes=scopes,
            mode=mode,
        )
        if output_authority.get("status") != "approved":
            raise ProtocolError("generate execution requires approved output authorization")
    if execution_mode == "converge":
        convergence_authority = _validate_authority_record(
            handoff.get("convergence_authority"),
            "convergence_authority",
            decision_id=decision_id,
            consumer_root=consumer_root,
            scopes=scopes,
            mode=mode,
        )

    if mode == "hcl" and "hcl-import" not in required_capabilities:
        raise ProtocolError("HCL handoff must require hcl-import capability")
    if live:
        if execution_mode not in {"import", "converge"}:
            raise ProtocolError("live execution requires execution_mode=import or converge")
        if handoff.get("decision") != "execute":
            raise ProtocolError("live execution requires decision=execute")
        if handoff.get("live_authorized") is not True:
            raise ProtocolError("live execution requires live_authorized=true")
        live_authorization = _require_object(
            handoff.get("live_authorization"), "live_authorization"
        )
        if live_authorization.get("consumer_root") != consumer_root:
            raise ProtocolError("live_authorization.consumer_root does not match consumer_root")
        if live_authorization.get("state_scope") != state_scope:
            raise ProtocolError("live_authorization.state_scope does not match state boundary")
        if set(_require_string_list(live_authorization.get("scopes"), "live_authorization.scopes")) != set(scopes):
            raise ProtocolError("live_authorization.scopes do not match scopes")
        if live_authorization.get("import_mode") != mode:
            raise ProtocolError("live_authorization.import_mode does not match mode")
        if live_authorization.get("decision_id") != decision_id:
            raise ProtocolError("live_authorization.decision_id does not match decision_id")
        identity_confirmation = _require_object(
            handoff.get("identity_confirmation"), "identity_confirmation"
        )
        if identity_confirmation.get("status") != "confirmed":
            raise ProtocolError("live execution requires confirmed identity")
        if identity_confirmation.get("consumer_root") != consumer_root:
            raise ProtocolError("identity_confirmation.consumer_root does not match consumer_root")
        if identity_confirmation.get("state_scope") != state_scope:
            raise ProtocolError("identity_confirmation.state_scope does not match state boundary")
        if set(_require_string_list(identity_confirmation.get("scopes"), "identity_confirmation.scopes")) != set(scopes):
            raise ProtocolError("identity_confirmation.scopes do not match scopes")
        if identity_confirmation.get("import_mode") != mode:
            raise ProtocolError("identity_confirmation.import_mode does not match mode")
        if identity_confirmation.get("decision_id") != decision_id:
            raise ProtocolError("identity_confirmation.decision_id does not match decision_id")
        if handoff.get("canonical_identity_status") != "verified":
            raise ProtocolError("live execution requires verified canonical identity")
        if handoff.get("identity_status") != "verified":
            raise ProtocolError("live execution requires verified identity")
        if handoff.get("reconciliation_status") != "complete":
            raise ProtocolError("live execution requires complete reconciliation")
        if handoff.get("ownership_disposition") not in {"unmanaged", "transferred"}:
            raise ProtocolError("live execution requires an adoptable ownership disposition")
        if execution_mode == "import":
            if mutation_authority is None or mutation_authority.get("status") != "approved":
                raise ProtocolError("live execution requires approved mutation authority")
            if handoff.get("convergence_decision") != "adoption-only":
                raise ProtocolError("live execution requires adoption-only convergence")
        elif handoff.get("convergence_decision") != "converge":
            raise ProtocolError("live convergence requires convergence_decision=converge")
        elif convergence_authority is None or convergence_authority.get("status") != "approved":
            raise ProtocolError("live convergence requires approved convergence authority")
        if adoption_decision != "adopt":
            raise ProtocolError("live execution requires adoption_decision=adopt")
        if handoff.get("runner_status") != "verified":
            raise ProtocolError("live execution requires verified runner status")
        required_for_mode = {
            "script": {
                "script-import",
                "saved-plan",
                "plan-json",
                "exact-plan-apply",
            },
            "hcl": {"hcl-import", "saved-plan", "plan-json", "exact-plan-apply"},
        }[mode]
        if mode == "hcl":
            required_for_mode.add("configuration-address")
        required_for_mode.update({"post-apply-state-verify", "post-apply-live-verify"})
        missing_mode_capabilities = sorted(
            required_for_mode - set(required_capabilities)
        )
        if missing_mode_capabilities:
            raise ProtocolError(
                "live execution is missing required capabilities: "
                + ", ".join(missing_mode_capabilities)
            )
        if handoff.get("recovery_status") != "ready":
            raise ProtocolError("live execution requires recovery readiness")


def classify_plan(plan: Mapping[str, object]) -> dict[str, Any]:
    """Normalize Terraform/OpenTofu plan actions for adoption enforcement."""

    document = _require_object(plan, "plan")
    if "resource_changes" in document:
        changes = document["resource_changes"]
        if not isinstance(changes, Sequence) or isinstance(changes, (str, bytes)):
            raise ProtocolError("plan.resource_changes must be a list")
        raw_actions = [_classify_resource_change(change) for change in changes]
    elif "actions" in document:
        raw_actions = _classify_normalized_actions(document["actions"])
    else:
        raw_actions = [{"address": "", "action": "unknown", "reason": "missing actions"}]

    blocked_actions = [item for item in raw_actions if item["action"] not in SAFE_PLAN_ACTIONS]
    return {
        "actions": raw_actions,
        "blocked_actions": blocked_actions,
        "allowed": not blocked_actions,
    }



def build_completion_receipt_from_records(document: Mapping[str, object]) -> dict[str, Any]:
    """Build a completion receipt from its separately persisted records."""

    payload = _require_object(document, "receipt input")
    authorization = _require_object(payload.get("authorization"), "authorization")
    evidence = _require_object(payload.get("evidence"), "evidence")
    run_id = _require_run_id(payload.get("run_id"))
    if _require_run_id(authorization.get("run_id"), "authorization.run_id") != run_id:
        raise ProtocolError("authorization run_id does not match receipt run_id")
    if _require_run_id(evidence.get("run_id"), "evidence.run_id") != run_id:
        raise ProtocolError("evidence run_id does not match receipt run_id")
    validate_runtime_evidence(evidence)
    plan_binding = _require_object(payload.get("plan_binding"), "plan_binding")
    evidence_binding = _require_object(
        evidence.get("plan_binding"), "evidence.plan_binding"
    )
    if plan_binding != evidence_binding:
        raise ProtocolError("plan binding does not match evidence plan binding")
    return build_completion_receipt(
        run_id=run_id,
        authorization_digest=_digest_document(authorization),
        evidence_digest=_digest_document(evidence),
        plan_binding=plan_binding,
        imports=payload.get("imports", []),
        moves=payload.get("moves", []),
        final_state_identities=_require_object(
            payload.get("final_state_identities"), "final_state_identities"
        ),
        live_verifications=payload.get("live_verifications", []),
        post_apply_plan=_require_object(payload.get("post_apply_plan"), "post_apply_plan"),
        final_status=_require_string(payload.get("final_status"), "final_status"),
        recovery_evidence=_require_object(
            payload.get("recovery_evidence"), "recovery_evidence"
        ),
    )


def build_runtime_evidence(document: Mapping[str, object]) -> dict[str, Any]:
    """Build the immutable runtime evidence record from run observations."""

    payload = _require_object(document, "runtime evidence input")
    run_id = _require_run_id(payload.get("run_id"))
    desired_inventory = _copy_record_list(
        payload.get("desired_inventory", []), "desired_inventory"
    )
    live_inventory = _copy_record_list(
        payload.get("live_inventory", []), "live_inventory"
    )
    state_inventory = _copy_record_list(
        payload.get("state_inventory", []), "state_inventory"
    )
    reconciliation = _copy_record_list(
        payload.get("reconciliation", []), "reconciliation"
    )
    collision_results = _copy_record_list(
        payload.get("collision_results", []), "collision_results"
    )
    ambiguity_results = _copy_record_list(
        payload.get("ambiguity_results", []), "ambiguity_results"
    )
    state_boundary = _require_object(payload.get("state_boundary"), "state_boundary")
    state_scope = _require_string(state_boundary.get("scope"), "state_boundary.scope")
    state_lineage = _require_string(
        state_boundary.get("lineage"), "state_boundary.lineage"
    )
    state_serial = state_boundary.get("serial")
    _validate_state_serial(state_serial)
    tool_versions = _require_tool_versions(payload.get("tool_versions"))
    timestamp = _require_string(payload.get("timestamp"), "timestamp")
    plan_binding = _require_object(payload.get("plan_binding"), "plan_binding")
    if plan_binding.get("run_id") != run_id:
        raise ProtocolError("plan binding run_id does not match runtime evidence run_id")
    _require_string(plan_binding.get("plan_digest"), "plan_binding.plan_digest")
    plan_classification = _require_plan_classification(
        payload.get("plan_classification"), "plan_classification"
    )
    post_apply_classification = _require_plan_classification(
        payload.get("post_apply_classification"), "post_apply_classification"
    )
    live_verifications = _copy_record_list(
        payload.get("live_verifications", []), "live_verifications"
    )
    plan_artifact_path = _require_absolute_path(
        payload.get("plan_artifact_path"), "plan_artifact_path"
    )
    plan_envelope_path = _require_absolute_path(
        payload.get("plan_envelope_path"), "plan_envelope_path"
    )
    evidence = {
        "schema_version": 1,
        "kind": "internal-terraform-import-runtime-evidence",
        "run_id": run_id,
        "timestamp": timestamp,
        "tool_versions": tool_versions,
        "inventory_digests": {
            "desired": _digest_document({"items": desired_inventory}),
            "live": _digest_document({"items": live_inventory}),
            "state": _digest_document({"items": state_inventory}),
        },
        "state_boundary": {
            "scope": state_scope,
            "lineage": state_lineage,
            "serial": state_serial,
        },
        "reconciliation": reconciliation,
        "collision_results": collision_results,
        "ambiguity_results": ambiguity_results,
        "plan_artifact_path": plan_artifact_path,
        "plan_envelope_path": plan_envelope_path,
        "plan_binding": deepcopy(plan_binding),
        "plan_classification": plan_classification,
        "post_apply_classification": post_apply_classification,
        "live_verifications": live_verifications,
    }
    return validate_runtime_evidence(evidence)


def validate_runtime_evidence(document: Mapping[str, object]) -> dict[str, Any]:
    """Validate the persisted runtime evidence contract."""

    evidence = _require_object(document, "runtime evidence")
    if evidence.get("schema_version") != 1:
        raise ProtocolError("runtime evidence schema_version must be 1")
    if evidence.get("kind") != "internal-terraform-import-runtime-evidence":
        raise ProtocolError("runtime evidence kind is invalid")
    _require_run_id(evidence.get("run_id"))
    _require_string(evidence.get("timestamp"), "timestamp")
    _require_tool_versions(evidence.get("tool_versions"))
    inventory_digests = _require_object(
        evidence.get("inventory_digests"), "inventory_digests"
    )
    for inventory_name in ("desired", "live", "state"):
        digest = _require_string(
            inventory_digests.get(inventory_name),
            f"inventory_digests.{inventory_name}",
        )
        if not digest.startswith("sha256:"):
            raise ProtocolError(
                f"inventory_digests.{inventory_name} must be a sha256 digest"
            )
    state_boundary = _require_object(evidence.get("state_boundary"), "state_boundary")
    _require_string(state_boundary.get("scope"), "state_boundary.scope")
    _require_string(state_boundary.get("lineage"), "state_boundary.lineage")
    _validate_state_serial(state_boundary.get("serial"))
    plan_binding = _require_object(evidence.get("plan_binding"), "plan_binding")
    if plan_binding.get("run_id") != evidence.get("run_id"):
        raise ProtocolError("runtime evidence plan binding run_id does not match")
    consumer_root = _require_absolute_path(
        plan_binding.get("consumer_root"), "plan_binding.consumer_root"
    )
    _require_string(plan_binding.get("plan_digest"), "plan_binding.plan_digest")
    _require_plan_classification(
        evidence.get("plan_classification"), "plan_classification"
    )
    _require_plan_classification(
        evidence.get("post_apply_classification"), "post_apply_classification"
    )
    for field in (
        "reconciliation",
        "collision_results",
        "ambiguity_results",
        "live_verifications",
    ):
        _copy_record_list(evidence.get(field), field)
    plan_artifact_path = _require_absolute_path(
        evidence.get("plan_artifact_path"), "plan_artifact_path"
    )
    plan_envelope_path = _require_absolute_path(
        evidence.get("plan_envelope_path"), "plan_envelope_path"
    )
    adoption_dir = (Path(consumer_root) / ".terraform-import-adoption").resolve(
        strict=False
    )
    if Path(plan_artifact_path).resolve(strict=False).parent != adoption_dir:
        raise ProtocolError("plan_artifact_path must be inside adoption artifact directory")
    if Path(plan_artifact_path).resolve(strict=False).name != f"{evidence['run_id']}.plan":
        raise ProtocolError("plan_artifact_path must match runtime evidence run_id")
    if Path(plan_envelope_path).resolve(strict=False) != adoption_dir / f"{evidence['run_id']}.plan-envelope.json":
        raise ProtocolError("plan_envelope_path must match runtime evidence run_id")
    return deepcopy(evidence)

def normalize_manifest(
    records: Sequence[Mapping[str, object]],
    *,
    expected_scopes: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Validate manifest records and assign their adoption eligibility."""

    if isinstance(records, (str, bytes)):
        raise ProtocolError("manifest must be a list of records")
    scopes = set(expected_scopes or [])
    normalized: list[dict[str, Any]] = []
    addresses: set[tuple[str, str]] = set()
    identities: set[tuple[str, str]] = set()
    for raw_record in records:
        record = _require_object(raw_record, "manifest record")
        scope = _require_string(record.get("scope"), "record.scope")
        address = _require_string(record.get("address"), "record.address")
        _require_string(record.get("resource_kind"), "record.resource_kind")
        lookup = _require_object(record.get("lookup"), "record.lookup")
        disposition = _require_string(record.get("disposition"), "record.disposition")
        if disposition not in DISPOSITIONS:
            raise ProtocolError(f"unknown disposition: {disposition}")
        if scopes and scope not in scopes:
            raise ProtocolError(f"record scope is outside the selected scope: {scope}")
        key = (scope, address)
        if key in addresses:
            raise ProtocolError(f"duplicate manifest address: {scope}:{address}")
        addresses.add(key)

        if disposition == "import_candidate":
            canonical_id = lookup.get("canonical_id")
            import_id = lookup.get("import_id")
            if canonical_id is not None:
                canonical_id = _require_string(canonical_id, "lookup.canonical_id")
            if import_id is not None:
                _require_string(import_id, "lookup.import_id")
            if canonical_id is not None:
                identity_key = (scope, canonical_id)
                if identity_key in identities:
                    raise ProtocolError(
                        f"canonical identity collision: {scope}:{canonical_id}"
                    )
                identities.add(identity_key)
        elif disposition == "moved_candidate":
            canonical_id = _require_string(
                lookup.get("canonical_id"), "lookup.canonical_id"
            )
            _require_string(lookup.get("import_id"), "lookup.import_id")
            identity_key = (scope, canonical_id)
            if identity_key in identities:
                raise ProtocolError(f"canonical identity collision: {scope}:{canonical_id}")
            identities.add(identity_key)
        if disposition == "moved_candidate":
            validate_move_proof(record.get("move"))

        normalized_record = deepcopy(record)
        normalized_record["lookup"] = lookup
        normalized_record["adoption_eligible"] = disposition in ADOPTION_DISPOSITIONS
        normalized.append(normalized_record)
    return normalized


def validate_move_proof(move: object) -> dict[str, Any]:
    """Validate the evidence that a state move preserves one remote object."""

    proof = _require_object(move, "move")
    source = _require_string(proof.get("from"), "move.from")
    destination = _require_string(proof.get("to"), "move.to")
    if source == destination:
        raise ProtocolError("move.from and move.to must differ")
    _require_string(proof.get("canonical_id"), "move.canonical_id")
    _require_string(proof.get("state_lineage"), "move.state_lineage")
    if proof.get("collision_free") is not True:
        raise ProtocolError("move requires collision_free=true")
    if proof.get("remote_mutation") is not False:
        raise ProtocolError("move requires remote_mutation=false")
    return deepcopy(proof)


def build_plan_binding(
    *,
    run_id: str,
    consumer_root: str,
    state_scope: str,
    state_lineage: str,
    state_serial: int,
    configuration_digest: str,
    dependency_lock_digest: str,
    decision_id: str | None = None,
    execution_mode: str | None = None,
    import_mode: str | None = None,
    authorized_scopes: Sequence[str] | None = None,
    plan_artifact: bytes,
) -> dict[str, Any]:
    """Bind a saved plan to the exact authorization and state context."""

    context: dict[str, Any] = {
        "run_id": _require_run_id(run_id),
        "consumer_root": _require_absolute_path(consumer_root, "consumer_root"),
        "state_scope": _require_string(state_scope, "state_scope"),
        "state_lineage": _require_string(state_lineage, "state_lineage"),
        "state_serial": state_serial,
        "configuration_digest": _require_string(
            configuration_digest, "configuration_digest"
        ),
        "dependency_lock_digest": _require_string(
            dependency_lock_digest, "dependency_lock_digest"
        ),
    }
    _validate_state_serial(state_serial)
    if decision_id is not None:
        context["decision_id"] = _require_string(decision_id, "decision_id")
    if execution_mode is not None:
        context["execution_mode"] = _require_string(execution_mode, "execution_mode")
    if import_mode is not None:
        context["import_mode"] = _require_string(import_mode, "import_mode")
    if authorized_scopes is not None:
        context["authorized_scopes"] = _require_string_list(
            authorized_scopes, "authorized_scopes"
        )
    artifact = _require_artifact(plan_artifact)
    context["plan_digest"] = _digest_bytes(artifact)
    return context


def verify_plan_binding(
    binding: Mapping[str, object],
    expected_context: Mapping[str, object],
    *,
    plan_artifact: bytes | None = None,
) -> bool:
    """Verify that a saved plan still matches its authorized execution context."""

    actual = _require_object(binding, "plan binding")
    expected = _require_object(expected_context, "expected plan context")
    for field in PLAN_CONTEXT_FIELDS:
        if actual.get(field) != expected.get(field):
            raise ProtocolError(f"plan binding mismatch: {field}")
    plan_digest = _require_string(actual.get("plan_digest"), "plan_digest")
    if plan_artifact is not None and _digest_bytes(_require_artifact(plan_artifact)) != plan_digest:
        raise ProtocolError("plan binding mismatch: plan_digest")
    expected_digest = expected.get("plan_digest")
    if expected_digest is not None and expected_digest != plan_digest:
        raise ProtocolError("plan binding mismatch: plan_digest")
    return True


def validate_plan_envelope(
    envelope: Mapping[str, object],
    handoff: Mapping[str, object],
    plan_artifact: bytes,
) -> dict[str, Any]:
    """Validate a saved plan envelope against a live v2 authorization."""

    document = _require_object(envelope, "plan envelope")
    validated_handoff = validate_handoff(handoff, live=True)
    plan = _require_object(document.get("plan"), "plan envelope.plan")
    binding = _require_object(document.get("binding"), "plan envelope.binding")
    artifact_path = _require_absolute_path(
        document.get("plan_artifact_path"), "plan_artifact_path"
    )
    consumer_root = validated_handoff["consumer_root"]
    adoption_dir = (Path(consumer_root) / ".terraform-import-adoption").resolve(
        strict=False
    )
    resolved_artifact_path = Path(artifact_path).resolve(strict=False)
    if resolved_artifact_path.parent != adoption_dir:
        raise ProtocolError(
            "plan_artifact_path must be directly inside .terraform-import-adoption"
        )
    if resolved_artifact_path.name != f"{validated_handoff['run_id']}.plan":
        raise ProtocolError("plan_artifact_path must match the handoff run_id")
    state_boundary = _require_object(
        validated_handoff.get("state_boundary"), "state_boundary"
    )
    expected_context = {
        "run_id": validated_handoff["run_id"],
        "consumer_root": consumer_root,
        "state_scope": state_boundary["scope"],
        "state_lineage": state_boundary["lineage"],
        "state_serial": state_boundary["serial"],
        "configuration_digest": validated_handoff.get("configuration_digest"),
        "dependency_lock_digest": validated_handoff.get("dependency_lock_digest"),
        "decision_id": validated_handoff["decision_id"],
        "execution_mode": validated_handoff["execution_mode"],
        "import_mode": validated_handoff.get("import_mode"),
        "authorized_scopes": validated_handoff["scopes"],
    }
    verify_plan_binding(binding, expected_context, plan_artifact=plan_artifact)
    classification = classify_plan(plan)
    if not classification["allowed"]:
        blocked = ", ".join(item["action"] for item in classification["blocked_actions"])
        raise ProtocolError(f"adoption plan contains disallowed action(s): {blocked}")
    return {
        "plan": deepcopy(plan),
        "binding": deepcopy(binding),
        "plan_artifact_path": str(resolved_artifact_path),
        **classification,
    }


def build_plan_envelope(
    plan: Mapping[str, object],
    handoff: Mapping[str, object],
    *,
    plan_artifact_path: str,
    plan_artifact: bytes,
) -> dict[str, Any]:
    """Build and validate the exact-plan envelope for a live HCL run."""

    validated_handoff = validate_handoff(handoff, live=True)
    state_boundary = _require_object(
        validated_handoff.get("state_boundary"), "state_boundary"
    )
    binding = build_plan_binding(
        run_id=validated_handoff["run_id"],
        consumer_root=validated_handoff["consumer_root"],
        state_scope=state_boundary["scope"],
        state_lineage=state_boundary["lineage"],
        state_serial=state_boundary["serial"],
        configuration_digest=validated_handoff["configuration_digest"],
        dependency_lock_digest=validated_handoff["dependency_lock_digest"],
        decision_id=validated_handoff["decision_id"],
        execution_mode=validated_handoff["execution_mode"],
        import_mode=validated_handoff.get("import_mode"),
        authorized_scopes=validated_handoff["scopes"],
        plan_artifact=plan_artifact,
    )
    envelope = {
        "plan": deepcopy(_require_object(plan, "plan")),
        "binding": binding,
        "plan_artifact_path": _require_absolute_path(
            plan_artifact_path, "plan_artifact_path"
        ),
    }
    return validate_plan_envelope(envelope, validated_handoff, plan_artifact)


def _validate_state_serial(value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ProtocolError("state_serial must be a non-negative integer")


def _require_artifact(value: object) -> bytes:
    if not isinstance(value, bytes):
        raise ProtocolError("plan_artifact must be bytes")
    return value


def _digest_bytes(value: bytes) -> str:
    return f"sha256:{sha256(value).hexdigest()}"


def _digest_document(value: Mapping[str, object]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _digest_bytes(encoded.encode("utf-8"))


def build_completion_receipt(
    *,
    run_id: str,
    authorization_digest: str,
    evidence_digest: str,
    plan_binding: Mapping[str, object],
    imports: Sequence[Mapping[str, object]],
    moves: Sequence[Mapping[str, object]],
    final_state_identities: Mapping[str, object],
    live_verifications: Sequence[Mapping[str, object]],
    post_apply_plan: Mapping[str, object],
    final_status: str,
    recovery_evidence: Mapping[str, object],
) -> dict[str, Any]:
    """Create the terminal record for an adoption run."""

    receipt_run_id = _require_run_id(run_id)
    authorization = _require_string(authorization_digest, "authorization_digest")
    evidence = _require_string(evidence_digest, "evidence_digest")
    binding = _require_object(plan_binding, "plan_binding")
    if binding.get("run_id") != receipt_run_id:
        raise ProtocolError("plan binding run_id does not match receipt run_id")
    applied_plan_digest = _require_string(binding.get("plan_digest"), "plan_digest")
    plan = _require_object(post_apply_plan, "post_apply_plan")
    classification = classify_plan(plan)
    if final_status == "completed" and not classification["allowed"]:
        raise ProtocolError("completed receipt requires an adoption-safe post-apply plan")
    if final_status not in {"completed", "failed", "recoverable"}:
        raise ProtocolError("final_status is invalid")
    recovery = _require_object(recovery_evidence, "recovery_evidence")
    recovery_location = _require_absolute_path(
        recovery.get("location"), "recovery_evidence.location"
    )
    consumer_root = _require_absolute_path(
        binding.get("consumer_root"), "plan_binding.consumer_root"
    )
    expected_recovery = (
        Path(consumer_root) / ".terraform-import-adoption" / f"{receipt_run_id}.recovery.json"
    ).resolve(strict=False)
    if Path(recovery_location).resolve(strict=False) != expected_recovery:
        raise ProtocolError(
            "recovery_evidence.location must be the run recovery artifact directly inside .terraform-import-adoption"
        )
    return {
        "schema_version": 1,
        "kind": "internal-terraform-import-completion-receipt",
        "run_id": receipt_run_id,
        "authorization_digest": authorization,
        "evidence_digest": evidence,
        "plan_binding": deepcopy(binding),
        "applied_plan_digest": applied_plan_digest,
        "imports": _copy_record_list(imports, "imports"),
        "moves": _copy_record_list(moves, "moves"),
        "final_state_identities": deepcopy(dict(final_state_identities)),
        "live_verifications": _copy_record_list(live_verifications, "live_verifications"),
        "post_apply_plan": deepcopy(plan),
        "post_apply_classification": classification,
        "final_status": final_status,
        "recovery_evidence": deepcopy(recovery),
    }


def _copy_record_list(
    records: Sequence[Mapping[str, object]], field: str
) -> list[dict[str, Any]]:
    if isinstance(records, (str, bytes)):
        raise ProtocolError(f"{field} must be a list of objects")
    copied: list[dict[str, Any]] = []
    for record in records:
        copied.append(_require_object(record, f"{field}[]"))
    return deepcopy(copied)


def _require_plan_classification(
    value: object, field: str
) -> dict[str, Any]:
    classification = _require_object(value, field)
    actions = _copy_record_list(classification.get("actions"), f"{field}.actions")
    blocked_actions = _copy_record_list(
        classification.get("blocked_actions"), f"{field}.blocked_actions"
    )
    if not isinstance(classification.get("allowed"), bool):
        raise ProtocolError(f"{field}.allowed must be a boolean")
    return {
        "actions": actions,
        "blocked_actions": blocked_actions,
        "allowed": classification["allowed"],
    }


def _main(argv: Sequence[str]) -> int:
    command = argv[1] if len(argv) > 1 else ""
    try:
        document = json.load(sys.stdin)
        if command == "classify-plan" and len(argv) == 2:
            output = classify_plan(document)
        elif command == "normalize-manifest" and len(argv) >= 2:
            output = normalize_manifest(document, expected_scopes=_command_options(argv, "--scope"))
        elif command == "validate-handoff":
            output = validate_handoff(
                document,
                live="--live" in argv[2:],
                expected_root=_command_option(argv, "--root"),
                expected_mode=_command_option(argv, "--mode"),
            )
        elif command == "build-plan-envelope":
            handoff_path = Path(
                _require_string(_command_option(argv, "--handoff"), "--handoff")
            )
            artifact_path = _require_string(_command_option(argv, "--artifact"), "--artifact")
            output = build_plan_envelope(
                document,
                json.loads(handoff_path.read_text(encoding="utf-8")),
                plan_artifact_path=artifact_path,
                plan_artifact=Path(artifact_path).read_bytes(),
            )
        elif command == "validate-plan-envelope":
            handoff_path = Path(_require_string(_command_option(argv, "--handoff"), "--handoff"))
            artifact_path = Path(_require_string(_command_option(argv, "--artifact"), "--artifact"))
            output = validate_plan_envelope(
                document,
                json.loads(handoff_path.read_text(encoding="utf-8")),
                artifact_path.read_bytes(),
            )
        elif command == "build-receipt" and len(argv) == 2:
            output = build_completion_receipt_from_records(document)
        elif command == "build-runtime-evidence" and len(argv) == 2:
            output = build_runtime_evidence(document)
        elif command == "validate-runtime-evidence" and len(argv) == 2:
            output = validate_runtime_evidence(document)
        else:
            print(
                "usage: adoption_protocol.py classify-plan | normalize-manifest | validate-handoff | build-plan-envelope | validate-plan-envelope | build-receipt | build-runtime-evidence | validate-runtime-evidence",
                file=sys.stderr,
            )
            return 2
    except (json.JSONDecodeError, OSError, ProtocolError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


def _command_option(argv: Sequence[str], name: str) -> str | None:
    try:
        index = argv.index(name)
    except ValueError:
        return None
    if index + 1 >= len(argv):
        raise ProtocolError(f"{name} requires a value")
    return argv[index + 1]


def _command_options(argv: Sequence[str], name: str) -> list[str] | None:
    values = [argv[index + 1] for index, value in enumerate(argv[:-1]) if value == name]
    return values or None


def _classify_resource_change(change: object) -> dict[str, Any]:
    resource = _require_object(change, "plan.resource_changes[]")
    address = resource.get("address", "")
    if not isinstance(address, str):
        address = ""
    previous_address = resource.get("previous_address")
    change_data = resource.get("change")
    if not isinstance(change_data, Mapping):
        return {"address": address, "action": "unknown", "reason": "missing change"}
    actions = change_data.get("actions")
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        return {"address": address, "action": "unknown", "reason": "missing action list"}
    action_names = [item for item in actions if isinstance(item, str)]
    if len(action_names) != len(actions):
        return {"address": address, "action": "unknown", "reason": "invalid action"}
    if action_names == ["import"]:
        action = "import"
    elif action_names == ["no-op"] and isinstance(previous_address, str) and previous_address:
        return {
            "address": address,
            "action": "moved",
            "from": previous_address,
            "to": address,
        }
    elif action_names == ["no-op"]:
        action = "no-op"
    elif action_names == ["create"]:
        action = "create"
    elif action_names == ["update"]:
        action = "update"
    elif action_names == ["delete"]:
        action = "delete"
    elif set(action_names) == {"create", "delete"} and len(action_names) == 2:
        action = "replace"
    else:
        action = "unknown"
    return {"address": address, "action": action}


def _classify_normalized_actions(actions: object) -> list[dict[str, Any]]:
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        raise ProtocolError("plan.actions must be a list")
    normalized: list[dict[str, Any]] = []
    for item in actions:
        record = _require_object(item, "plan.actions[]")
        action = record.get("action")
        address = record.get("address", "")
        if not isinstance(action, str) or not action:
            normalized.append({"address": address if isinstance(address, str) else "", "action": "unknown"})
            continue
        if action not in KNOWN_PLAN_ACTIONS:
            action = "unknown"
        if action == "moved" and not all(
            isinstance(record.get(field), str) and record[field]
            for field in ("from", "to")
        ):
            normalized.append(
                {
                    "address": address if isinstance(address, str) else "",
                    "action": "unknown",
                    "reason": "moved action requires from and to",
                }
            )
            continue
        normalized.append({key: value for key, value in {**record, "action": action}.items() if key in {"address", "action", "from", "to"}})
    return normalized


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
