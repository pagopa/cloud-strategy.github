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
    compose_handoff,
    evaluate_runtime_evidence,
    persist_handoff,
    resolve_evidence_allowlist,
)


def _brief(root: Path, mode: str = "write") -> dict:
    output = "out/result.md" if mode != "read" else None
    return {
        "schema_version": 1,
        "delegation_id": f"flow-{mode}",
        "mode": mode,
        "objective": "Produce one bounded observable result.",
        "value_gate": {"autonomous": True, "verifiable": True, "leverage": "Multiple bounded checks."},
        "evidence": [{"ref": "path:inputs", "purpose": "Authorized input root"}],
        "constraints": ["Use only authorized evidence."],
        "write_scope": [] if mode == "read" else ["out"],
        "expected_output": {"kind": "analysis" if mode == "read" else "artifact", "path": output, "format": "markdown"},
        "acceptance": [{"id": "A1", "observable": "Caller can verify the result."}],
        "validation": [{"id": "V1", "owner": "worker", "command": "true", "pass_signal": "exit-code-0"}],
        "budgets": {"attempts": 2, "context_refills": 1},
        "result_path": f"handoff/{mode}.result.json",
        "cache": {"prefix_version": "internal-subagent-contract/v1", "key_class": "worker-role"},
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
        "retry": {"recommended": False, "reason": "No retry needed.", "required_new_input": None},
    }


def _setup(tmp_path: Path, mode: str = "write") -> tuple[dict, dict, bytes]:
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/source.md").write_text("source", encoding="utf-8")
    brief = _brief(tmp_path, mode)
    raw = _raw_worker(brief)
    if mode != "read":
        (tmp_path / "out").mkdir()
        (tmp_path / brief["expected_output"]["path"]).write_text("artifact", encoding="utf-8")
    return brief, raw, json.dumps(raw, sort_keys=True).encode()


@pytest.mark.parametrize("mode", ["read", "write", "plan"])
def test_compose_handoff_preserves_worker_semantics_for_all_modes(tmp_path: Path, mode: str) -> None:
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
    assert result["budgets_used"] == {"attempts": 1, "context_refills": 0, "wall_seconds": 2}
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


def test_compose_handoff_rejects_artifact_hash_scope_and_semantic_mismatches(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path)
    out_of_scope = copy.deepcopy(raw)
    out_of_scope["artifacts"] = [{"path": "inputs/source.md", "kind": "markdown"}]
    with pytest.raises(AdapterError, match="scope"):
        compose_handoff(out_of_scope, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes)

    bad_hash = copy.deepcopy(raw)
    bad_hash["artifacts"][0]["sha256"] = "sha256:" + "0" * 64
    with pytest.raises(AdapterError, match="hash"):
        compose_handoff(bad_hash, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes)

    semantic_mutation = copy.deepcopy(raw)
    semantic_mutation["brief_sha256"] = "sha256:" + "0" * 64
    with pytest.raises(AdapterError, match="deterministic"):
        compose_handoff(semantic_mutation, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes)


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


def test_unobserved_validation_and_telemetry_are_not_presented_as_verified(tmp_path: Path) -> None:
    brief, raw, raw_bytes = _setup(tmp_path, "read")
    result, receipt = compose_handoff(raw, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes)

    assert result["budgets_used"]["wall_seconds"] is None
    assert receipt["attestations"]["validation_execution"]["state"] == "worker_claim"
    assert receipt["attestations"]["budget_accounting"]["state"] == "unavailable"


def test_runtime_evaluator_distinguishes_claims_observations_and_missing_telemetry() -> None:
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
    result, receipt = compose_handoff(raw, brief, repo_root=tmp_path, brief_bytes=b"brief", raw_worker_bytes=raw_bytes)
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

    result_path, receipt_path = persist_handoff(result, receipt, brief, repo_root=tmp_path)

    assert result_path == tmp_path / "handoff/write.result.json"
    assert receipt_path == tmp_path / "handoff/write.receipt.json"
    assert json.loads(result_path.read_text()) == result
    persisted_receipt = json.loads(receipt_path.read_text())
    assert persisted_receipt["attestations"]["result_persistence"]["state"] == "verified"
