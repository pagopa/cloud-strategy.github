from __future__ import annotations

import json
import stat
from collections.abc import Callable
from pathlib import Path

import pytest

_BASE_CAPABILITIES = [
    "remote-lookup",
    "canonical-identity",
    "literal-import-id",
    "state-read",
]
_MODE_CAPABILITIES = {
    "script": ["script-import"],
    "hcl": ["hcl-import", "configuration-address"],
}
_APPLY_CAPABILITIES = [
    "saved-plan",
    "plan-json",
    "exact-plan-apply",
    "post-apply-state-verify",
    "post-apply-live-verify",
]


def _capabilities(mode: str, state_move: bool) -> list[str]:
    return [
        *_BASE_CAPABILITIES,
        *_MODE_CAPABILITIES[mode],
        *(["state-move"] if state_move else []),
        *_APPLY_CAPABILITIES,
    ]


def _handoff_payload(
    root: Path | str,
    mode: str = "script",
    decision: str = "assess",
    scope: str = "interop",
    *,
    serial: int = 1,
    state_move: bool = False,
    **overrides: object,
) -> dict[str, object]:
    root_path = Path(root)
    consumer_root = str(root_path.resolve())
    scopes = [scope]
    payload: dict[str, object] = {
        "schema_version": 1,
        "kind": "internal-terraform-import-handoff",
        "decision": decision,
        "consumer_root": consumer_root,
        "mode": mode,
        "scopes": scopes,
        "identity_status": "pending",
        "reconciliation_status": "pending",
        "ownership_disposition": "unknown",
        "mutation_authority": "not-approved",
        "convergence_decision": "adoption-only",
        "runner_status": "verified",
        "recovery_status": "pending",
        "approval_reference": "review-record-id",
        "primary_owner": "/internal-terraform",
        "execution_owner": "/internal-terraform-import",
        "reason": "approved import adoption",
        "context": {
            "consumer_root": consumer_root,
            "mode": mode,
            "scopes": list(scopes),
        },
        "safety_evidence": {
            "identity_status": "pending",
            "ownership_disposition": "unknown",
            "recovery_status": "pending",
        },
        "validation": "protocol and adapter preflight",
    }
    if decision == "execute":
        runner_path = str(root_path / "terraform.sh")
        capabilities = _capabilities(mode, state_move)
        binding = {
            "consumer_root": consumer_root,
            "state_scope": scope,
            "scopes": list(scopes),
            "import_mode": mode,
            "decision_id": "decision-1",
        }
        payload.update(
            {
                "schema_version": 2,
                "run_id": "run-1",
                "decision_id": "decision-1",
                "runtime": "terraform",
                "runtime_version": "1.9.0",
                "execution_mode": "import",
                "import_mode": mode,
                "canonical_identity_status": "verified",
                "desired_status": "verified",
                "live_status": "verified",
                "state_status": "verified",
                "state_boundary": {
                    "scope": scope,
                    "lineage": "lineage-1",
                    "serial": serial,
                },
                "runner_path": runner_path,
                "runner_capabilities": list(capabilities),
                "runner": {"path": runner_path, "capabilities": list(capabilities)},
                "required_capabilities": list(capabilities),
                "environment_criticality": "non-production",
                "identity_status": "verified",
                "reconciliation_status": "complete",
                "ownership_disposition": "unmanaged",
                "mutation_authority": {
                    "status": "approved",
                    "actor": "change-approver",
                    "decision_id": "decision-1",
                    "consumer_root": consumer_root,
                    "scopes": list(scopes),
                    "mode": mode,
                },
                "adoption_decision": "adopt",
                "recovery_status": "ready",
                "recovery_path": str(
                    root_path / ".terraform-import-adoption" / "run-1.recovery.json"
                ),
                "live_authorized": True,
                "live_authorization": dict(binding),
                "identity_confirmation": {"status": "confirmed", **binding},
                "safety_evidence": {
                    "identity_status": "verified",
                    "ownership_disposition": "unmanaged",
                    "recovery_status": "ready",
                },
                "evidence_references": ["evidence/run-1.json"],
                "configuration_digest": "sha256:config",
                "dependency_lock_digest": "sha256:lock",
                "tool_versions": {"terraform": "1.9.0"},
            }
        )
    payload.update(overrides)
    return payload


def _write_executable(target: Path, text: str) -> Path:
    target.write_text(text, encoding="utf-8")
    target.chmod(target.stat().st_mode | stat.S_IXUSR)
    return target


def _write_manifest(target: Path, records: list[dict[str, object]]) -> Path:
    target.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8"
    )
    return target


@pytest.fixture(scope="session")
def handoff_payload() -> Callable[..., dict[str, object]]:
    return _handoff_payload


@pytest.fixture(scope="session")
def write_executable() -> Callable[[Path, str], Path]:
    return _write_executable


@pytest.fixture(scope="session")
def write_manifest() -> Callable[[Path, list[dict[str, object]]], Path]:
    return _write_manifest
