import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-subagent-contract"
sys.path.insert(0, str(BUNDLE / "scripts"))

from runtime_evidence import (  # noqa: E402
    AdapterError,
    RuntimeObservation,
    bounded_diagnostics,
    compose_handoff,
    evaluate_runtime_evidence,
    isolated_diagnostics,
    persist_handoff,
    resolve_evidence_allowlist,
    validate_path_identity,
)
from subagent_contract import (  # noqa: E402
    bind_final_artifact,
    compute_semantic_fingerprint,
    invalidate_attestation,
    primary_owner_decision,
    sha256_path,
    validate_payload_schema,
    validate_receipt,
)


def _brief(root: Path, mode: str = "write") -> dict:
    output = "out/result.md" if mode != "read" else None
    return {
        "schema_version": 1,
        "delegation_id": f"flow-{mode}",
        "mode": mode,
        "objective": "Produce one bounded observable result.",
        "value_gate": {
            "autonomous": True,
            "verifiable": True,
            "leverage": "Multiple bounded checks.",
        },
        "evidence": [{"ref": "path:inputs", "purpose": "Authorized input root"}],
        "constraints": ["Use only authorized evidence."],
        "write_scope": [] if mode == "read" else ["out"],
        "expected_output": {
            "kind": "analysis" if mode == "read" else "artifact",
            "path": output,
            "format": "markdown",
        },
        "acceptance": [{"id": "A1", "observable": "Caller can verify the result."}],
        "validation": [
            {
                "id": "V1",
                "owner": "worker",
                "command": "true",
                "pass_signal": "exit-code-0",
            }
        ],
        "budgets": {"attempts": 2, "context_refills": 1},
        "result_path": f"handoff/{mode}.result.json",
        "cache": {
            "prefix_version": "internal-subagent-contract/v1",
            "key_class": "worker-role",
        },
    }


def _raw_worker(brief: dict) -> dict:
    artifacts = []
    if brief["mode"] != "read":
        artifacts = [{"path": brief["expected_output"]["path"], "kind": "markdown"}]
    return {
        "schema_version": 1,
        "delegation_id": brief["delegation_id"],
        "status": "completed",
        "value_delivered": True,
        "summary": "Bounded work completed.",
        "artifacts": artifacts,
        "evidence": [{"acceptance_id": "A1", "ref": "V1", "outcome": "pass"}],
        "non_blocking_findings": [],
        "remaining": [],
        "retry": {
            "recommended": False,
            "reason": "No retry needed.",
            "required_new_input": None,
        },
    }


def _setup(tmp_path: Path, mode: str = "write") -> tuple[dict, dict, bytes]:
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/source.md").write_text("source", encoding="utf-8")
    brief = _brief(tmp_path, mode)
    raw = _raw_worker(brief)
    if mode != "read":
        (tmp_path / "out").mkdir()
        (tmp_path / brief["expected_output"]["path"]).write_text(
            "artifact", encoding="utf-8"
        )
    return brief, raw, json.dumps(raw, sort_keys=True).encode()


@pytest.mark.parametrize("mode", ["read", "write", "plan"])
def test_compose_handoff_preserves_worker_semantics_for_all_modes(
    tmp_path: Path, mode: str
) -> None:
    brief, raw, raw_bytes = _setup(tmp_path, mode)
    result, receipt = compose_handoff(
        raw,
        brief,
        repo_root=tmp_path,
        brief_bytes=json.dumps(brief).encode(),
        raw_worker_bytes=raw_bytes,
        observation=RuntimeObservation(
            attempts=1,
            context_refills=0,
            wall_seconds=2,
            validation_observed=True,
            command="python3 -m pytest -q",
            outcome="pass",
            evidence_ref="runtime:test-output",
        ),
    )

    assert result["summary"] == raw["summary"]
    assert result["budgets_used"] == {
        "attempts": 1,
        "context_refills": 0,
        "wall_seconds": 2,
    }
    assert receipt["attestations"]["validation_execution"]["state"] == "verified"
    assert receipt["caller_decision"]["decision"] == "not_decided"
    assert receipt["value_verified"] is False


def test_compose_handoff_is_deterministic_for_repeated_inputs(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    brief_bytes = json.dumps(brief).encode()
    observation = RuntimeObservation(attempts=1, context_refills=0, wall_seconds=2)

    first = compose_handoff(
        raw,
        brief,
        repo_root=tmp_path,
        brief_bytes=brief_bytes,
        raw_worker_bytes=raw_bytes,
        observation=observation,
    )
    second = compose_handoff(
        raw,
        brief,
        repo_root=tmp_path,
        brief_bytes=brief_bytes,
        raw_worker_bytes=raw_bytes,
        observation=observation,
    )

    assert first == second


def test_evidence_allowlist_rejects_unlisted_or_escaping_inputs(tmp_path: Path) -> None:
    brief, _, _ = _setup(tmp_path)
    allowed = resolve_evidence_allowlist(brief, repo_root=tmp_path)
    assert allowed == ((tmp_path / "inputs/source.md").resolve(),)

    brief["evidence"] = [{"ref": "path:missing", "purpose": "Not present"}]
    with pytest.raises(AdapterError, match="evidence"):
        resolve_evidence_allowlist(brief, repo_root=tmp_path)

    outside = tmp_path.parent / "outside-evidence.txt"
    outside.write_text("outside", encoding="utf-8")
    (tmp_path / "inputs/escape").symlink_to(outside)
    brief["evidence"] = [{"ref": "path:inputs", "purpose": "Escaping link"}]
    with pytest.raises(AdapterError, match="symlink|allowlist|repository"):
        resolve_evidence_allowlist(brief, repo_root=tmp_path)


def test_compose_handoff_rejects_artifact_hash_scope_and_semantic_mismatches(
    tmp_path: Path,
) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    out_of_scope = copy.deepcopy(raw)
    out_of_scope["artifacts"] = [{"path": "inputs/source.md", "kind": "markdown"}]
    with pytest.raises(AdapterError, match="scope"):
        compose_handoff(
            out_of_scope,
            brief,
            repo_root=tmp_path,
            brief_bytes=b"brief",
            raw_worker_bytes=raw_bytes,
        )

    bad_hash = copy.deepcopy(raw)
    bad_hash["artifacts"][0]["sha256"] = "sha256:" + "0" * 64
    with pytest.raises(AdapterError, match="hash"):
        compose_handoff(
            bad_hash,
            brief,
            repo_root=tmp_path,
            brief_bytes=b"brief",
            raw_worker_bytes=raw_bytes,
        )

    semantic_mutation = copy.deepcopy(raw)
    semantic_mutation["brief_sha256"] = "sha256:" + "0" * 64
    with pytest.raises(AdapterError, match="deterministic"):
        compose_handoff(
            semantic_mutation,
            brief,
            repo_root=tmp_path,
            brief_bytes=b"brief",
            raw_worker_bytes=raw_bytes,
        )


def test_compose_handoff_rejects_raw_worker_semantic_mutation(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    semantic_mutation = copy.deepcopy(raw)
    semantic_mutation["summary"] = "silently rewritten"

    with pytest.raises(AdapterError, match="deterministic"):
        compose_handoff(
            semantic_mutation,
            brief,
            repo_root=tmp_path,
            brief_bytes=json.dumps(brief).encode(),
            raw_worker_bytes=raw_bytes,
        )


def test_unobserved_validation_and_telemetry_are_not_presented_as_verified(
    tmp_path: Path,
) -> None:
    brief, raw, raw_bytes = _setup(tmp_path, "read")
    result, receipt = compose_handoff(
        raw, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes
    )

    assert result["budgets_used"]["wall_seconds"] is None
    assert receipt["attestations"]["validation_execution"]["state"] == "worker_claim"
    assert receipt["attestations"]["budget_accounting"]["state"] == "unavailable"


def test_runtime_evaluator_distinguishes_claims_observations_and_missing_telemetry() -> (
    None
):
    claim = evaluate_runtime_evidence(RuntimeObservation())
    observed = evaluate_runtime_evidence(
        RuntimeObservation(
            validation_observed=True,
            command="python3 -m pytest -q",
            outcome="pass",
            evidence_ref="runtime:test-output",
        )
    )
    failed = evaluate_runtime_evidence(
        RuntimeObservation(
            validation_observed=True,
            command="python3 -m pytest -q",
            outcome="fail",
            evidence_ref="runtime:test-output",
        )
    )
    unavailable = evaluate_runtime_evidence(
        RuntimeObservation(validation_observed=True, command="python3 -m pytest -q")
    )

    assert claim["state"] == "worker_claim"
    assert observed == {
        "state": "verified",
        "source": "runtime",
        "command": "python3 -m pytest -q",
        "outcome": "pass",
        "evidence_ref": "runtime:test-output",
    }
    assert failed["state"] == "failed"
    assert unavailable["state"] == "unavailable"


def test_persistence_rejects_result_path_mismatch(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path, "read")
    result, receipt = compose_handoff(
        raw, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes
    )
    receipt["result_path"] = "handoff/other.result.json"

    with pytest.raises(AdapterError, match="result_path"):
        persist_handoff(result, receipt, brief, repo_root=tmp_path)


def test_persist_handoff_writes_caller_owned_result_and_receipt(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    result, receipt = compose_handoff(
        raw,
        brief,
        repo_root=tmp_path,
        brief_bytes=json.dumps(brief).encode(),
        raw_worker_bytes=raw_bytes,
    )

    result_path, receipt_path = persist_handoff(
        result, receipt, brief, repo_root=tmp_path
    )

    assert result_path == tmp_path / "handoff/write.result.json"
    assert receipt_path == tmp_path / "handoff/write.receipt.json"
    assert json.loads(result_path.read_text()) == result
    persisted_receipt = json.loads(receipt_path.read_text())
    assert (
        persisted_receipt["attestations"]["result_persistence"]["state"] == "verified"
    )


def test_bind_final_artifact_binds_final_bytes_and_semantic_fingerprint(
    tmp_path: Path,
) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    result, receipt = compose_handoff(
        raw,
        brief,
        repo_root=tmp_path,
        brief_bytes=json.dumps(brief).encode(),
        raw_worker_bytes=raw_bytes,
    )
    manifest = {"plan_id": "T2", "targets": ["out/result.md"]}

    binding = bind_final_artifact(
        result,
        receipt,
        brief["expected_output"]["path"],
        manifest,
        repo_root=tmp_path,
    )

    assert binding.receipt["final_artifact"]["path"] == "out/result.md"
    assert binding.receipt["final_artifact"]["sha256"] == sha256_path(
        tmp_path / "out/result.md"
    )
    assert (
        binding.receipt["final_artifact"]["semantic_fingerprint"]
        == compute_semantic_fingerprint(manifest)
    )


def test_stale_receipt_rejects_material_artifact_edit(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    result, receipt = compose_handoff(
        raw,
        brief,
        repo_root=tmp_path,
        brief_bytes=json.dumps(brief).encode(),
        raw_worker_bytes=raw_bytes,
    )
    binding = bind_final_artifact(
        result,
        receipt,
        brief["expected_output"]["path"],
        {"plan_id": "T2"},
        repo_root=tmp_path,
    )
    (tmp_path / "out/result.md").write_text("material edit", encoding="utf-8")

    errors = validate_receipt(
        binding.receipt,
        brief,
        binding.result,
        repo_root=tmp_path,
        brief_bytes=json.dumps(brief).encode(),
        raw_worker_bytes=raw_bytes,
        result_path=brief["result_path"],
        manifest={"plan_id": "T2"},
    )

    assert any("final artifact" in error for error in errors)


def test_material_edit_invalidation_marks_attestation_failed() -> None:
    receipt = {"attestations": {"artifact_integrity": {"state": "verified"}}, "value_verified": True}

    invalidated = invalidate_attestation(receipt, "material edit")

    assert invalidated["attestations"]["artifact_integrity"]["state"] == "failed"
    assert invalidated["value_verified"] is False


def test_primary_owner_path_emits_no_worker_chain() -> None:
    decision = primary_owner_decision(False)

    assert decision["owner"] == "primary"
    assert decision["delegated"] is False
    assert decision["worker_chain"] is None


def test_path_identity_checks_type_and_expected_symlink_target(tmp_path: Path) -> None:
    target = tmp_path / "target.md"
    target.write_text("target", encoding="utf-8")
    link = tmp_path / "link.md"
    link.symlink_to(target)

    assert validate_path_identity(target, "file") == []
    assert validate_path_identity(link, "symlink", target) == []
    assert validate_path_identity(link, "file")
    assert validate_path_identity(link, "symlink", tmp_path / "other.md")


def test_isolated_diagnostics_select_only_requested_source() -> None:
    diagnostics = {
        "executor": ["executor failure"],
        "provider": ["provider failure"],
    }

    assert isolated_diagnostics(diagnostics, "executor") == ["executor failure"]
    assert "provider failure" not in isolated_diagnostics(diagnostics, "executor")


def test_bounded_diagnostics_marks_omitted_output() -> None:
    bounded = bounded_diagnostics(["one", "two", "three"], 2)

    assert len(bounded) == 2
    assert bounded[0:1] == ["one"]
    assert "omitted" in bounded[-1]


def test_payload_schema_rejects_unknown_and_malformed_payloads() -> None:
    errors = validate_payload_schema(
        {"id": "brief", "extra": True},
        {"id": str, "items": list},
    )

    assert any("missing" in error for error in errors)
    assert any("unknown" in error for error in errors)
