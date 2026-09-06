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
FIXTURES = BUNDLE / "fixtures"
sys.path.insert(0, str(BUNDLE / "scripts"))

from runtime_evidence import compose_handoff  # noqa: E402
from subagent_contract import (  # noqa: E402
    ATTESTATION_NAMES,
    ATTESTATION_STATES,
    BRIEF_FIELDS,
    RECEIPT_FIELDS,
    canonical_json,
    compare_progress,
    compute_progress_signature,
    evidence_path_allowed,
    receipt_path_for,
    resolve_evidence_refs,
    retry_eligible,
    sha256_bytes,
    validate_brief,
    validate_prompt_order,
    validate_receipt,
    validate_result,
)


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _valid_brief() -> dict:
    return _load("valid-brief.json")


def _valid_result() -> dict:
    template = _load("valid-result.json")
    brief = _valid_brief()
    raw_worker = dict(template)
    raw_worker_bytes = canonical_json(raw_worker)
    materialized, _ = compose_handoff(
        raw_worker,
        brief,
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
        raw_worker_bytes=raw_worker_bytes,
    )
    return materialized


def _valid_receipt(brief: dict, raw_worker: bytes) -> dict:
    return {
        "schema_version": 1,
        "delegation_id": brief["delegation_id"],
        "brief_sha256": sha256_bytes((FIXTURES / "valid-brief.json").read_bytes()),
        "result_path": brief["result_path"],
        "raw_worker": {"sha256": sha256_bytes(raw_worker), "ref": None},
        "attestations": {
            name: {
                "state": "verified",
                "source": "adapter",
                "evidence_ref": f"evidence:{name}",
            }
            for name in ATTESTATION_NAMES
        },
        "caller_decision": {
            "decision": "accepted",
            "source": "caller",
            "evidence_ref": "evidence:caller-acceptance",
        },
        "value_verified": True,
        "final_artifact": {
            "path": ".github/skills/internal-subagent-contract/fixtures/valid-brief.json",
            "sha256": sha256_bytes((FIXTURES / "valid-brief.json").read_bytes()),
            "semantic_fingerprint": sha256_bytes(b"manifest"),
        },
    }


def test_valid_brief_fixture_has_exact_protocol_shape() -> None:
    brief = _valid_brief()
    assert set(brief) == BRIEF_FIELDS
    assert validate_brief(brief, repo_root=REPO_ROOT) == []


def test_brief_evidence_separates_inline_facts_from_resolved_paths() -> None:
    brief = _valid_brief()
    brief["evidence"] = [
        {"ref": "fact:caller-approved-policy", "purpose": "Materialized policy fact."},
        {
            "ref": "path:.github/skills/internal-subagent-contract/references/protocol.md",
            "purpose": "Protocol reference.",
        },
    ]

    resolved = resolve_evidence_refs(brief, repo_root=REPO_ROOT)

    assert resolved[0] == {
        "kind": "fact",
        "ref": "fact:caller-approved-policy",
        "value": "caller-approved-policy",
    }
    assert resolved[1]["kind"] == "path"
    assert evidence_path_allowed(BUNDLE / "references/protocol.md", resolved)
    assert not evidence_path_allowed(BUNDLE / "SKILL.md", resolved)
    assert validate_brief(brief, repo_root=REPO_ROOT) == []


def test_invalid_value_fixture_fails_closed() -> None:
    errors = validate_brief(_load("invalid-value.json"), repo_root=REPO_ROOT)
    assert any("value_gate" in error for error in errors)


@pytest.mark.parametrize("field", ["local_alternative", "off_critical_path"])
def test_plan_brief_requires_explicit_admission_evidence(field: str) -> None:
    brief = _valid_brief()
    brief["mode"] = "plan"
    brief["value_gate"].update(
        {
            "local_alternative": "The primary owner can author the same retained plan locally.",
            "off_critical_path": "The bounded worker package is not required to unblock the next handoff.",
        }
    )
    brief["value_gate"].pop(field)

    errors = validate_brief(brief, repo_root=REPO_ROOT)

    assert any(field in error for error in errors)


def test_plan_brief_accepts_explicit_admission_evidence() -> None:
    brief = _valid_brief()
    brief["mode"] = "plan"
    brief["value_gate"].update(
        {
            "local_alternative": "The primary owner can author the same retained plan locally.",
            "off_critical_path": "The bounded worker package is not required to unblock the next handoff.",
        }
    )

    assert validate_brief(brief, repo_root=REPO_ROOT) == []


@pytest.mark.parametrize("field", ["local_alternative", "off_critical_path"])
def test_plan_brief_rejects_blank_admission_evidence(field: str) -> None:
    brief = _valid_brief()
    brief["mode"] = "plan"
    brief["value_gate"].update(
        {
            "local_alternative": "The primary owner can author the same retained plan locally.",
            "off_critical_path": "The bounded worker package is not required to unblock the next handoff.",
        }
    )
    brief["value_gate"][field] = "   "

    errors = validate_brief(brief, repo_root=REPO_ROOT)

    assert any(field in error for error in errors)


def test_brief_rejects_unknown_and_missing_fields() -> None:
    brief = _valid_brief()
    brief["unexpected"] = True
    brief.pop("objective")

    errors = validate_brief(brief, repo_root=REPO_ROOT)

    assert any("unknown" in error for error in errors)
    assert any("objective" in error for error in errors)


@pytest.mark.parametrize(
    "bad_scope", ["/tmp/out.md", "../outside.md", "tmp/../outside.md"]
)
def test_brief_write_scope_is_repository_relative(bad_scope: str) -> None:
    brief = _valid_brief()
    brief["write_scope"] = [bad_scope]

    errors = validate_brief(brief, repo_root=REPO_ROOT)

    assert any(
        "write_scope" in error or "repository-relative" in error for error in errors
    )


@pytest.mark.parametrize("mode", ["read", "write", "plan"])
def test_three_modes_are_structural_not_caller_identity(mode: str) -> None:
    brief = _valid_brief()
    brief["mode"] = mode
    if mode == "read":
        brief["write_scope"] = []
        brief["expected_output"]["path"] = None
    elif mode == "plan":
        brief["value_gate"].update(
            {
                "local_alternative": "The primary owner can author the same retained plan locally.",
                "off_critical_path": "The bounded worker package is not required to unblock the next handoff.",
            }
        )

    assert validate_brief(brief, repo_root=REPO_ROOT) == []


def test_valid_result_binds_delegation_brief_artifact_and_acceptance() -> None:
    brief_path = FIXTURES / "valid-brief.json"

    errors = validate_result(
        _valid_result(),
        _valid_brief(),
        repo_root=REPO_ROOT,
        brief_bytes=brief_path.read_bytes(),
    )

    assert errors == []


def test_valid_result_template_materializes_through_adapter_and_disk_round_trip(
    tmp_path: Path,
) -> None:
    template = _load("valid-result.json")
    assert not {"brief_sha256", "progress_signature", "budgets_used"} & set(template)

    brief = _valid_brief()
    raw_worker = {
        key: value
        for key, value in template.items()
        if key not in {"brief_sha256", "progress_signature", "budgets_used"}
    }
    raw_worker_bytes = canonical_json(raw_worker)
    materialized, _ = compose_handoff(
        raw_worker,
        brief,
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
        raw_worker_bytes=raw_worker_bytes,
    )

    result_path = tmp_path / "materialized-result.json"
    result_path.write_bytes(canonical_json(materialized) + b"\n")
    persisted = json.loads(result_path.read_text(encoding="utf-8"))

    assert (
        validate_result(
            persisted,
            brief,
            repo_root=REPO_ROOT,
            brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
        )
        == []
    )


def test_verification_receipt_binds_exact_pair_and_keeps_decision_separate() -> None:
    brief = copy.deepcopy(_valid_brief())
    brief["result_path"] = "tmp/.handoff/receipt-test.result.json"
    raw_worker = b'{"semantic":"worker output"}'
    receipt = _valid_receipt(brief, raw_worker)

    assert set(receipt) == RECEIPT_FIELDS
    assert (
        receipt_path_for(brief["result_path"])
        == "tmp/.handoff/receipt-test.receipt.json"
    )
    assert "value_verified" not in _valid_result()
    assert (
        validate_receipt(
            receipt,
            brief,
            _valid_result(),
            repo_root=REPO_ROOT,
            brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
            raw_worker_bytes=raw_worker,
            result_path=brief["result_path"],
        )
        == []
    )


@pytest.mark.parametrize("state", sorted(ATTESTATION_STATES))
def test_receipt_accepts_only_declared_attestation_states(state: str) -> None:
    brief = copy.deepcopy(_valid_brief())
    brief["result_path"] = "tmp/.handoff/receipt-state.result.json"
    raw_worker = b'{"semantic":"worker output"}'
    receipt = _valid_receipt(brief, raw_worker)
    for attestation in receipt["attestations"].values():
        attestation["state"] = state
    receipt["value_verified"] = state == "verified"
    if state != "verified":
        receipt["caller_decision"]["decision"] = "not_decided"

    assert (
        validate_receipt(
            receipt,
            brief,
            _valid_result(),
            repo_root=REPO_ROOT,
            brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
            raw_worker_bytes=raw_worker,
            result_path=brief["result_path"],
        )
        == []
    )


def test_receipt_rejects_unknown_attestation_state() -> None:
    brief = copy.deepcopy(_valid_brief())
    brief["result_path"] = "tmp/.handoff/receipt-state.result.json"
    raw_worker = b'{"semantic":"worker output"}'
    receipt = _valid_receipt(brief, raw_worker)
    receipt["attestations"]["validation_execution"]["state"] = "assumed"

    errors = validate_receipt(
        receipt,
        brief,
        _valid_result(),
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
        raw_worker_bytes=raw_worker,
        result_path=brief["result_path"],
    )

    assert any("state" in error for error in errors)


def test_result_rejects_delegation_and_brief_hash_mismatch() -> None:
    result = _valid_result()
    result["delegation_id"] = "different-delegation"
    result["brief_sha256"] = "sha256:" + "0" * 64

    errors = validate_result(
        result,
        _valid_brief(),
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
    )

    assert any("delegation_id" in error for error in errors)
    assert any("brief_sha256" in error for error in errors)


def test_result_requires_artifact_or_acceptance_bound_evidence_for_value() -> None:
    result = _valid_result()
    result["value_delivered"] = True
    result["artifacts"] = []
    result["evidence"] = [
        {"ref": "summary only", "outcome": "not_run", "acceptance_id": "A1"}
    ]

    errors = validate_result(
        result,
        _valid_brief(),
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
    )

    assert any("value_delivered" in error or "acceptance" in error for error in errors)


def test_result_rejects_artifact_hash_mismatch() -> None:
    result = _valid_result()
    result["artifacts"][0]["sha256"] = "sha256:" + "0" * 64

    errors = validate_result(
        result,
        _valid_brief(),
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
    )

    assert any("artifact" in error and "hash" in error for error in errors)


def test_budgets_reject_refill_and_attempt_overruns() -> None:
    brief = _valid_brief()
    brief["budgets"]["context_refills"] = 2
    brief["budgets"]["attempts"] = 3

    errors = validate_brief(brief, repo_root=REPO_ROOT)

    assert any("context_refills" in error for error in errors)
    assert any("attempts" in error for error in errors)


def test_progress_signature_is_jcs_stable_for_key_order_and_whitespace() -> None:
    result = _valid_result()
    reordered = json.loads(json.dumps(result, indent=2, sort_keys=True))

    assert canonical_json(result) != b""
    assert compute_progress_signature(result) == compute_progress_signature(reordered)


def test_repeated_progress_is_stalled() -> None:
    repeated = _load("repeated-progress.json")

    assert compare_progress(repeated["previous"], repeated["current"]) == "stalled"


def test_cosmetic_or_minor_findings_never_reopen_retry() -> None:
    result = _valid_result()
    result["non_blocking_findings"] = ["Minor: punctuation in the summary"]
    result["retry"]["recommended"] = True

    errors = validate_result(
        result,
        _valid_brief(),
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
    )

    assert any("non-blocking" in error or "Minor" in error for error in errors)


def test_one_context_refill_and_one_corrective_retry_are_upper_bounds() -> None:
    brief = _valid_brief()
    result = _valid_result()
    result["budgets_used"]["context_refills"] = 1
    assert (
        validate_result(
            result,
            brief,
            repo_root=REPO_ROOT,
            brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
        )
        == []
    )

    overrun = copy.deepcopy(result)
    overrun["budgets_used"]["context_refills"] = 2
    errors = validate_result(
        overrun,
        brief,
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
    )
    assert any("context_refills" in error for error in errors)


def test_retry_requires_new_brief_input_and_changed_progress() -> None:
    previous_brief = _valid_brief()
    next_brief = copy.deepcopy(previous_brief)
    next_brief["evidence"].append(
        {"ref": "new-validator-output", "purpose": "corrective evidence"}
    )
    previous_result = _valid_result()
    previous_result["status"] = "partial"
    previous_result["value_delivered"] = False
    previous_result["retry"]["recommended"] = True
    previous_result["retry"]["reason"] = "One acceptance check remains."
    previous_result["progress_signature"] = compute_progress_signature(previous_result)
    next_result = copy.deepcopy(previous_result)
    next_result["remaining"] = ["one bounded acceptance item remains"]
    next_result["progress_signature"] = compute_progress_signature(next_result)

    assert retry_eligible(previous_brief, next_brief, previous_result, next_result)


def test_blocked_authority_result_is_terminal_for_retry() -> None:
    result = _valid_result()
    result["status"] = "blocked"
    result["value_delivered"] = False
    result["retry"] = {
        "recommended": False,
        "reason": "Authority is required",
        "required_new_input": "approved write scope",
    }
    result["progress_signature"] = compute_progress_signature(result)

    errors = validate_result(
        result,
        _valid_brief(),
        repo_root=REPO_ROOT,
        brief_bytes=(FIXTURES / "valid-brief.json").read_bytes(),
    )

    assert errors == []
    assert not retry_eligible(_valid_brief(), _valid_brief(), result, result)


def test_prompt_prefix_order_is_stable_and_dynamic_sections_are_last() -> None:
    assert (
        validate_prompt_order(
            ["role", "protocol", "schemas", "mode", "breakpoint", "brief", "retry"]
        )
        == []
    )
    errors = validate_prompt_order(["role", "brief", "protocol", "retry"])
    assert errors


def test_cache_prefix_keeps_stable_protocol_before_dynamic_brief_and_retry() -> None:
    brief = _valid_brief()
    assert brief["cache"]["prefix_version"] == "internal-subagent-contract/v1"
    assert (
        validate_prompt_order(
            ["role", "protocol", "schemas", "mode", "breakpoint", "brief", "retry"]
        )
        == []
    )


def test_protected_compatibility_is_caller_scope_not_provider_identity() -> None:
    brief = _valid_brief()
    brief["mode"] = "read"
    brief["write_scope"] = []
    brief["expected_output"] = {"kind": "analysis", "path": None, "format": "text"}
    brief["evidence"] = [
        {
            "ref": ".github/skills/mattpocock-research/SKILL.md",
            "purpose": "compatibility input",
        }
    ]

    assert validate_brief(brief, repo_root=REPO_ROOT) == []


def test_near_miss_mode_and_owner_prompts_are_rejected_structurally() -> None:
    brief = _valid_brief()
    brief["mode"] = "researcher"
    brief["validation"][0]["owner"] = "router"

    errors = validate_brief(brief, repo_root=REPO_ROOT)

    assert any("mode" in error for error in errors)
    assert any("owner" in error for error in errors)
