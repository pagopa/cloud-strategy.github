from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from adoption_protocol import (  # noqa: E402
    ProtocolError,
    build_completion_receipt,
    build_completion_receipt_from_records,
    build_plan_binding,
    build_runtime_evidence,
    classify_plan,
    normalize_manifest,
    validate_handoff,
    validate_plan_envelope,
    verify_plan_binding,
)


def _live_handoff() -> dict[str, object]:
    capabilities = [
        "remote-lookup",
        "canonical-identity",
        "literal-import-id",
        "state-read",
        "script-import",
        "saved-plan",
        "plan-json",
        "exact-plan-apply",
        "post-apply-state-verify",
        "post-apply-live-verify",
    ]
    return {
        "schema_version": 2,
        "kind": "internal-terraform-import-handoff",
        "run_id": "run-1",
        "decision": "execute",
        "decision_id": "decision-1",
        "consumer_root": "/workspace/root",
        "runtime": "terraform",
        "runtime_version": "1.9.0",
        "execution_mode": "import",
        "import_mode": "script",
        "mode": "script",
        "scopes": ["prod"],
        "canonical_identity_status": "verified",
        "desired_status": "verified",
        "live_status": "verified",
        "state_status": "verified",
        "state_boundary": {"scope": "prod", "lineage": "lineage-1", "serial": 7},
        "runner_path": "/workspace/root/terraform.sh",
        "runner_capabilities": capabilities,
        "runner": {"path": "/workspace/root/terraform.sh", "capabilities": capabilities},
        "required_capabilities": capabilities,
        "environment_criticality": "non-production",
        "identity_status": "verified",
        "reconciliation_status": "complete",
        "ownership_disposition": "unmanaged",
        "mutation_authority": {
            "status": "approved",
            "actor": "change-approver",
            "decision_id": "decision-1",
            "consumer_root": "/workspace/root",
            "scopes": ["prod"],
            "mode": "script",
        },
        "adoption_decision": "adopt",
        "convergence_decision": "adoption-only",
        "runner_status": "verified",
        "recovery_status": "ready",
        "recovery_path": "/workspace/root/.terraform-import-adoption/run-1.recovery.json",
        "live_authorized": True,
        "live_authorization": {
            "consumer_root": "/workspace/root",
            "state_scope": "prod",
            "scopes": ["prod"],
            "import_mode": "script",
            "decision_id": "decision-1",
        },
        "identity_confirmation": {
            "status": "confirmed",
            "consumer_root": "/workspace/root",
            "state_scope": "prod",
            "scopes": ["prod"],
            "import_mode": "script",
            "decision_id": "decision-1",
        },
        "approval_reference": "approval-1",
        "primary_owner": "/internal-terraform",
        "execution_owner": "/internal-terraform-import",
        "reason": "approved import adoption",
        "context": {
            "consumer_root": "/workspace/root",
            "mode": "script",
            "scopes": ["prod"],
        },
        "safety_evidence": {
            "identity_status": "verified",
            "ownership_disposition": "unmanaged",
            "recovery_status": "ready",
        },
        "validation": "protocol and adapter preflight",
        "evidence_references": ["evidence/run-1.json"],
        "configuration_digest": "sha256:config",
        "dependency_lock_digest": "sha256:lock",
        "tool_versions": {"terraform": "1.9.0"},
    }


def test_validate_handoff_accepts_complete_v2_live_authorization() -> None:
    handoff = _live_handoff()
    validated = validate_handoff(handoff, live=True)

    assert validated["run_id"] == "run-1"
    assert validated["required_capabilities"][-1] == "post-apply-live-verify"
    handoff["runner"]["capabilities"].append("mutated")  # type: ignore[index]
    assert "mutated" not in validated["runner"]["capabilities"]  # type: ignore[index]


def test_validate_handoff_rejects_live_authorization_without_post_apply_proof() -> None:
    handoff = _live_handoff()
    handoff["required_capabilities"] = ["script-import", "plan-json"]
    handoff["runner"]["capabilities"] = ["script-import", "plan-json"]  # type: ignore[index]
    handoff["runner_capabilities"] = ["script-import", "plan-json"]

    with pytest.raises(ProtocolError, match="post-apply"):
        validate_handoff(handoff, live=True)


@pytest.mark.parametrize(
    "field",
    [
        "decision_id",
        "runtime",
        "runtime_version",
        "execution_mode",
        "import_mode",
        "canonical_identity_status",
        "desired_status",
        "live_status",
        "state_status",
        "runner_path",
        "runner_capabilities",
        "environment_criticality",
        "recovery_path",
        "live_authorized",
        "live_authorization",
        "identity_confirmation",
    ],
)
def test_validate_handoff_rejects_missing_v2_authorization_field(field: str) -> None:
    handoff = _live_handoff()
    handoff.pop(field)

    with pytest.raises(ProtocolError, match=field):
        validate_handoff(handoff, live=True)


def test_validate_handoff_requires_separate_convergence_authority() -> None:
    handoff = _live_handoff()
    handoff["execution_mode"] = "converge"
    handoff.pop("convergence_authority", None)

    with pytest.raises(ProtocolError, match="convergence_authority"):
        validate_handoff(handoff)


@pytest.mark.parametrize("field", ["state_scope", "import_mode"])
def test_validate_handoff_rejects_unbound_identity_confirmation(field: str) -> None:
    handoff = _live_handoff()
    handoff["identity_confirmation"][field] = "wrong"  # type: ignore[index]

    with pytest.raises(ProtocolError, match="identity_confirmation"):
        validate_handoff(handoff, live=True)


def test_validate_handoff_allows_inspect_without_mutation_authority() -> None:
    handoff = _live_handoff()
    handoff["execution_mode"] = "inspect"
    handoff.pop("mutation_authority")

    assert validate_handoff(handoff)["execution_mode"] == "inspect"


def test_validate_handoff_rejects_path_traversal_run_id() -> None:
    handoff = _live_handoff()
    handoff["run_id"] = "../escape"

    with pytest.raises(ProtocolError, match="run_id"):
        validate_handoff(handoff, live=True)


def test_validate_handoff_rejects_protocol_v1_execute_decision() -> None:
    handoff = _live_handoff()
    handoff["schema_version"] = 1
    handoff["decision"] = "execute"

    with pytest.raises(ProtocolError, match="assessment"):
        validate_handoff(handoff)


def test_validate_handoff_requires_wrapper_projection() -> None:
    handoff = _live_handoff()
    handoff.pop("execution_owner")

    with pytest.raises(ProtocolError, match="execution_owner"):
        validate_handoff(handoff)


def test_classify_plan_blocks_every_mutating_action() -> None:
    plan = {
        "resource_changes": [
            {"address": "resource.imported", "change": {"actions": ["import"]}},
            {"address": "resource.same", "change": {"actions": ["no-op"]}},
            {"address": "resource.moved", "previous_address": "resource.old", "change": {"actions": ["no-op"]}},
            {"address": "resource.created", "change": {"actions": ["create"]}},
            {"address": "resource.updated", "change": {"actions": ["update"]}},
            {"address": "resource.deleted", "change": {"actions": ["delete"]}},
            {"address": "resource.replaced", "change": {"actions": ["delete", "create"]}},
            {"address": "resource.unknown", "change": {"actions": ["read"]}},
        ]
    }

    classification = classify_plan(plan)

    assert [item["action"] for item in classification["actions"]] == [
        "import",
        "no-op",
        "moved",
        "create",
        "update",
        "delete",
        "replace",
        "unknown",
    ]
    assert classification["allowed"] is False
    assert [item["action"] for item in classification["blocked_actions"]] == [
        "create",
        "update",
        "delete",
        "replace",
        "unknown",
    ]


def test_classify_normalized_plan_maps_unrecognized_actions_to_unknown() -> None:
    classification = classify_plan(
        {"actions": [{"address": "resource.example", "action": "read"}]}
    )

    assert classification["actions"] == [
        {"address": "resource.example", "action": "unknown"}
    ]


def test_classify_plan_blocks_unproven_normalized_move() -> None:
    classification = classify_plan(
        {"actions": [{"address": "resource.new", "action": "moved"}]}
    )

    assert classification["allowed"] is False
    assert classification["blocked_actions"][0]["action"] == "unknown"


def test_normalize_manifest_preserves_one_reconciliation_disposition() -> None:
    records = [
        {
            "scope": "prod",
            "address": "resource.group[\"platform\"]",
            "resource_kind": "generic_group",
            "lookup": {"canonical_id": "object-1", "import_id": "object-1"},
            "disposition": "import_candidate",
        },
        {
            "scope": "prod",
            "address": "resource.group[\"future\"]",
            "resource_kind": "generic_group",
            "lookup": {},
            "disposition": "absent_create",
        },
    ]

    normalized = normalize_manifest(records, expected_scopes=["prod"])

    assert [record["disposition"] for record in normalized] == [
        "import_candidate",
        "absent_create",
    ]
    assert normalized[0]["adoption_eligible"] is True
    assert normalized[1]["adoption_eligible"] is False


def test_normalize_manifest_allows_adapter_resolved_import_identity() -> None:
    normalized = normalize_manifest(
        [
            {
                "scope": "prod",
                "address": "resource.group[\"platform\"]",
                "resource_kind": "generic_group",
                "lookup": {},
                "disposition": "import_candidate",
            }
        ],
        expected_scopes=["prod"],
    )

    assert normalized[0]["adoption_eligible"] is True


def test_normalize_manifest_requires_proven_moves_and_rejects_identity_reuse() -> None:
    moved = {
        "scope": "prod",
        "address": "resource.group[\"new\"]",
        "resource_kind": "generic_group",
        "lookup": {"canonical_id": "object-1", "import_id": "object-1"},
        "disposition": "moved_candidate",
        "move": {
            "from": "resource.group[\"old\"]",
            "to": "resource.group[\"new\"]",
            "canonical_id": "object-1",
            "state_lineage": "lineage-1",
            "collision_free": True,
            "remote_mutation": False,
        },
    }

    normalized = normalize_manifest([moved], expected_scopes=["prod"])

    assert normalized[0]["adoption_eligible"] is True
    with pytest.raises(ProtocolError, match="canonical identity collision"):
        normalize_manifest(
            [
                moved,
                {
                    "scope": "prod",
                    "address": "resource.other",
                    "resource_kind": "generic_group",
                    "lookup": {"canonical_id": "object-1", "import_id": "object-1"},
                    "disposition": "import_candidate",
                },
            ],
            expected_scopes=["prod"],
        )


def test_plan_binding_rejects_state_drift_and_plan_byte_changes() -> None:
    context = {
        "run_id": "run-1",
        "consumer_root": "/workspace/root",
        "state_scope": "prod",
        "state_lineage": "lineage-1",
        "state_serial": 7,
        "configuration_digest": "sha256:config",
        "dependency_lock_digest": "sha256:lock",
    }
    binding = build_plan_binding(plan_artifact=b"saved-plan", **context)

    assert verify_plan_binding(binding, context, plan_artifact=b"saved-plan") is True
    with pytest.raises(ProtocolError, match="state_serial"):
        verify_plan_binding(
            binding,
            {**context, "state_serial": 8},
            plan_artifact=b"saved-plan",
        )
    with pytest.raises(ProtocolError, match="plan_digest"):
        verify_plan_binding(binding, context, plan_artifact=b"changed-plan")


def test_completion_receipt_links_authorization_evidence_and_recovery() -> None:
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        plan_artifact=b"saved-plan",
    )

    receipt = build_completion_receipt(
        run_id="run-1",
        authorization_digest="sha256:authorization",
        evidence_digest="sha256:evidence",
        plan_binding=binding,
        imports=[{"address": "resource.group[\"platform\"]", "identity": "object-1"}],
        moves=[],
        final_state_identities={"resource.group[\"platform\"]": "object-1"},
        live_verifications=[{"address": "resource.group[\"platform\"]", "status": "verified"}],
        post_apply_plan={"actions": [{"address": "resource.group[\"platform\"]", "action": "no-op"}]},
        final_status="completed",
        recovery_evidence={
            "location": "/workspace/root/.terraform-import-adoption/run-1.recovery.json"
        },
    )

    assert receipt["run_id"] == "run-1"
    assert receipt["authorization_digest"] == "sha256:authorization"
    assert receipt["applied_plan_digest"] == binding["plan_digest"]
    assert receipt["recovery_evidence"]["location"] == "/workspace/root/.terraform-import-adoption/run-1.recovery.json"


def test_completion_receipt_rejects_plan_binding_different_from_evidence() -> None:
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        plan_artifact=b"saved-plan",
    )
    evidence = build_runtime_evidence(
        {
            "run_id": "run-1",
            "timestamp": "2026-09-19T12:00:00Z",
            "tool_versions": {"terraform": "1.9.0"},
            "desired_inventory": [],
            "live_inventory": [],
            "state_inventory": [],
            "state_boundary": {"scope": "prod", "lineage": "lineage-1", "serial": 7},
            "reconciliation": [],
            "collision_results": [],
            "ambiguity_results": [],
            "plan_artifact_path": "/workspace/root/.terraform-import-adoption/run-1.plan",
            "plan_envelope_path": "/workspace/root/.terraform-import-adoption/run-1.plan-envelope.json",
            "plan_binding": binding,
            "plan_classification": {"actions": [], "blocked_actions": [], "allowed": True},
            "post_apply_classification": {"actions": [], "blocked_actions": [], "allowed": True},
            "live_verifications": [],
        }
    )
    mismatched_binding = {**binding, "plan_digest": "sha256:other"}

    with pytest.raises(ProtocolError, match="plan binding"):
        build_completion_receipt_from_records(
            {
                "run_id": "run-1",
                "authorization": {"run_id": "run-1"},
                "evidence": evidence,
                "plan_binding": mismatched_binding,
                "final_state_identities": {},
                "post_apply_plan": {"actions": []},
                "final_status": "completed",
                "recovery_evidence": {
                    "location": "/workspace/root/.terraform-import-adoption/run-1.recovery.json"
                },
            }
        )


def test_completion_receipt_rejects_recovery_path_outside_adoption_directory() -> None:
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        plan_artifact=b"saved-plan",
    )

    with pytest.raises(ProtocolError, match="recovery_evidence.location"):
        build_completion_receipt(
            run_id="run-1",
            authorization_digest="sha256:authorization",
            evidence_digest="sha256:evidence",
            plan_binding=binding,
            imports=[],
            moves=[],
            final_state_identities={},
            live_verifications=[],
            post_apply_plan={"actions": []},
            final_status="completed",
            recovery_evidence={"location": "/tmp/recovery.json"},
        )


def test_completion_receipt_rejects_records_from_another_run() -> None:
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        plan_artifact=b"saved-plan",
    )

    with pytest.raises(ProtocolError, match="run_id"):
        build_completion_receipt_from_records(
            {
                "run_id": "run-1",
                "authorization": {"run_id": "run-2"},
                "evidence": {"run_id": "run-1"},
                "plan_binding": binding,
                "final_state_identities": {},
                "post_apply_plan": {"actions": []},
                "final_status": "completed",
                "recovery_evidence": {"location": "evidence/run-1-recovery.json"},
            }
        )


def test_validate_plan_envelope_binds_saved_artifact_to_handoff() -> None:
    artifact = b"saved-plan"
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        decision_id="decision-1",
        execution_mode="import",
        import_mode="script",
        authorized_scopes=["prod"],
        plan_artifact=artifact,
    )
    envelope = {
        "plan": {"actions": [{"address": "resource.group", "action": "no-op"}]},
        "binding": binding,
        "plan_artifact_path": "/workspace/root/.terraform-import-adoption/run-1.plan",
    }

    validated = validate_plan_envelope(envelope, _live_handoff(), artifact)

    assert validated["allowed"] is True
    assert validated["binding"]["plan_digest"] == binding["plan_digest"]


def test_validate_plan_envelope_binds_decision_mode_and_scopes() -> None:
    artifact = b"saved-plan"
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        decision_id="decision-1",
        execution_mode="import",
        import_mode="script",
        authorized_scopes=["prod"],
        plan_artifact=artifact,
    )
    envelope = {
        "plan": {"actions": [{"address": "resource.group", "action": "no-op"}]},
        "binding": binding,
        "plan_artifact_path": "/workspace/root/.terraform-import-adoption/run-1.plan",
    }

    assert validate_plan_envelope(envelope, _live_handoff(), artifact)["allowed"] is True
    with pytest.raises(ProtocolError, match="decision_id"):
        validate_plan_envelope(
            {**envelope, "binding": {**binding, "decision_id": "other"}},
            _live_handoff(),
            artifact,
        )


def test_validate_plan_envelope_rejects_artifact_outside_adoption_directory() -> None:
    artifact = b"saved-plan"
    binding = build_plan_binding(
        run_id="run-1",
        consumer_root="/workspace/root",
        state_scope="prod",
        state_lineage="lineage-1",
        state_serial=7,
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        plan_artifact=artifact,
    )

    with pytest.raises(ProtocolError, match="adoption"):
        validate_plan_envelope(
            {
                "plan": {"actions": []},
                "binding": binding,
                "plan_artifact_path": "/workspace/root/../escape/run-1.plan",
            },
            _live_handoff(),
            artifact,
        )


def test_build_runtime_evidence_contains_inventory_and_execution_context() -> None:
    evidence = build_runtime_evidence(
        {
            "run_id": "run-1",
            "timestamp": "2026-09-19T12:00:00Z",
            "tool_versions": {"terraform": "1.9.0"},
            "desired_inventory": [{"address": "resource.group", "disposition": "import_candidate"}],
            "live_inventory": [{"address": "resource.group", "status": "verified"}],
            "state_inventory": [{"address": "resource.group", "identity": "object-1"}],
            "state_boundary": {"scope": "prod", "lineage": "lineage-1", "serial": 7},
            "reconciliation": [{"address": "resource.group", "disposition": "import_candidate"}],
            "collision_results": [],
            "ambiguity_results": [],
            "plan_artifact_path": "/workspace/root/.terraform-import-adoption/run-1.plan",
            "plan_envelope_path": "/workspace/root/.terraform-import-adoption/run-1.plan-envelope.json",
            "plan_binding": {
                "run_id": "run-1",
                "consumer_root": "/workspace/root",
                "plan_digest": "sha256:plan",
            },
            "plan_classification": {"actions": [], "blocked_actions": [], "allowed": True},
            "post_apply_classification": {"actions": [], "blocked_actions": [], "allowed": True},
            "live_verifications": [{"address": "resource.group", "status": "verified"}],
        }
    )

    assert set(evidence["inventory_digests"]) == {"desired", "live", "state"}
    assert evidence["state_boundary"]["serial"] == 7
    assert evidence["tool_versions"] == {"terraform": "1.9.0"}
