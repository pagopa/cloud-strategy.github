"""Compose deterministic handoff envelopes without changing worker semantics."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from subagent_contract import (
    ATTESTATION_NAMES,
    canonical_json,
    compute_progress_signature,
    receipt_path_for,
    sha256_bytes,
    sha256_path,
    validate_brief,
    validate_receipt,
    validate_result,
)


SEMANTIC_RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "delegation_id",
        "status",
        "value_delivered",
        "summary",
        "artifacts",
        "evidence",
        "non_blocking_findings",
        "remaining",
        "retry",
    }
)
DETERMINISTIC_RESULT_FIELDS = frozenset(
    {"brief_sha256", "progress_signature", "budgets_used"}
)


class AdapterError(ValueError):
    """Raised when an adapter cannot safely compose or persist a handoff."""


@dataclass(frozen=True)
class RuntimeObservation:
    attempts: int | None = None
    context_refills: int | None = None
    wall_seconds: int | None = None
    validation_observed: bool = False
    execution_confinement_verified: bool | None = None
    command: str | None = None
    outcome: str | None = None
    evidence_ref: str | None = None


def evaluate_runtime_evidence(
    observation: RuntimeObservation | None,
) -> dict[str, str]:
    """Classify worker claims, observed validation, and missing telemetry."""

    if observation is None or not observation.validation_observed:
        return {
            "state": "worker_claim",
            "source": "worker",
            "evidence_ref": "worker:declared-validation",
        }
    if (
        not observation.command
        or not observation.outcome
        or not observation.evidence_ref
        or observation.outcome not in {"pass", "fail"}
    ):
        return {
            "state": "unavailable",
            "source": "runtime",
            "evidence_ref": "runtime:telemetry-unavailable",
        }
    return {
        "state": "verified" if observation.outcome == "pass" else "failed",
        "source": "runtime",
        "command": observation.command,
        "outcome": observation.outcome,
        "evidence_ref": observation.evidence_ref,
    }


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _validate_raw_worker_bytes(raw_worker: Mapping[str, object], raw_worker_bytes: bytes) -> None:
    try:
        parsed = json.loads(raw_worker_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError(f"raw worker payload is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict) or parsed != dict(raw_worker):
        raise AdapterError("deterministic adapter detected semantic worker mutation")


def _scope_allows(path: str, scopes: list[str]) -> bool:
    candidate = path.rstrip("/")
    return any(
        candidate == scope.rstrip("/")
        or candidate.startswith(scope.rstrip("/") + "/")
        for scope in scopes
    )


def resolve_evidence_allowlist(
    brief: Mapping[str, object],
    *,
    repo_root: Path,
    max_files: int = 256,
) -> tuple[Path, ...]:
    """Resolve v1 evidence references into a bounded repository read allowlist.

    `fact:` is inline content, `path:` is an explicit path, and an unprefixed
    value is the v1 compatibility form for a repository-relative path.
    """

    root = repo_root.resolve()
    resolved: list[Path] = []
    evidence = brief.get("evidence")
    if not isinstance(evidence, list):
        raise AdapterError("evidence must be a list")
    for item in evidence:
        if not isinstance(item, Mapping) or not isinstance(item.get("ref"), str):
            raise AdapterError("evidence reference is invalid")
        reference = item["ref"]
        if reference.startswith("fact:"):
            if not reference.removeprefix("fact:").strip():
                raise AdapterError("inline evidence fact must be non-empty")
            continue
        value = reference.removeprefix("path:")
        if not value or any(marker in value for marker in ("*", "?", "[", "]")):
            raise AdapterError("evidence path must be explicit and must not contain a glob")
        declared = Path(value)
        if declared.is_absolute() or ".." in declared.parts:
            raise AdapterError("evidence path must remain repository-relative")
        candidate = root / declared
        if not candidate.exists():
            raise AdapterError(f"evidence path does not exist: {value}")
        candidates = [candidate] if not candidate.is_dir() else sorted(candidate.rglob("*"))
        for entry in candidates:
            real = entry.resolve()
            if not _inside(real, root):
                raise AdapterError("evidence symlink escapes the repository allowlist")
            if entry.is_file() or entry.is_symlink():
                resolved.append(real)
                if len(resolved) > max_files:
                    raise AdapterError("evidence allowlist exceeds the file limit")
    return tuple(sorted(set(resolved)))


def _artifact_envelopes(
    artifacts: object,
    *,
    repo_root: Path,
    write_scope: list[str],
) -> list[dict[str, object]]:
    if not isinstance(artifacts, list):
        raise AdapterError("worker artifacts must be a list")
    envelopes: list[dict[str, object]] = []
    for item in artifacts:
        if not isinstance(item, Mapping):
            raise AdapterError("worker artifact must be an object")
        if set(item) not in ({"path", "kind"}, {"path", "kind", "sha256"}):
            raise AdapterError("worker artifact uses an invalid shape")
        path = item.get("path")
        if not isinstance(path, str) or not _scope_allows(path, write_scope):
            raise AdapterError("worker artifact is outside write scope")
        artifact_path = repo_root / path
        if not _inside(artifact_path, repo_root) or not artifact_path.is_file():
            raise AdapterError("worker artifact is missing or outside repository scope")
        digest = sha256_path(artifact_path)
        if "sha256" in item and item["sha256"] != digest:
            raise AdapterError("worker artifact hash disagrees with deterministic bytes")
        envelopes.append({"path": path, "sha256": digest, "kind": item.get("kind")})
    return envelopes


def _attestation(state: str, source: str, evidence_ref: str) -> dict[str, str]:
    return {"state": state, "source": source, "evidence_ref": evidence_ref}


def compose_handoff(
    raw_worker: Mapping[str, object],
    brief: Mapping[str, object],
    *,
    repo_root: Path,
    brief_bytes: bytes,
    raw_worker_bytes: bytes,
    observation: RuntimeObservation | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    """Compose a WorkerResult v1 and separate caller-owned receipt."""

    brief_errors = validate_brief(brief, repo_root=repo_root)
    if brief_errors:
        raise AdapterError("invalid brief: " + "; ".join(brief_errors))
    unexpected = set(raw_worker) - SEMANTIC_RESULT_FIELDS
    missing = SEMANTIC_RESULT_FIELDS - set(raw_worker)
    if unexpected & DETERMINISTIC_RESULT_FIELDS:
        raise AdapterError("raw worker payload must not supply deterministic fields")
    if unexpected or missing:
        raise AdapterError("raw worker payload does not match the semantic result shape")

    result = copy.deepcopy(dict(raw_worker))
    write_scope = brief.get("write_scope")
    if not isinstance(write_scope, list) or not all(isinstance(item, str) for item in write_scope):
        raise AdapterError("brief write scope is invalid")
    result["artifacts"] = _artifact_envelopes(
        result["artifacts"], repo_root=repo_root, write_scope=write_scope
    )
    _validate_raw_worker_bytes(raw_worker, raw_worker_bytes)
    result["brief_sha256"] = sha256_bytes(brief_bytes)
    runtime = observation or RuntimeObservation()
    attempts = runtime.attempts if runtime.attempts is not None else 1
    refills = runtime.context_refills if runtime.context_refills is not None else 0
    budgets_used: dict[str, int | None] = {
        "attempts": attempts,
        "context_refills": refills,
        "wall_seconds": runtime.wall_seconds,
    }
    result["budgets_used"] = budgets_used
    result["progress_signature"] = compute_progress_signature(result)

    result_errors = validate_result(
        result,
        brief,
        repo_root=repo_root,
        brief_bytes=brief_bytes,
        result_path=brief.get("result_path"),
    )
    if result_errors:
        raise AdapterError("invalid composed result: " + "; ".join(result_errors))

    validation_evidence = evaluate_runtime_evidence(runtime)
    budget_state = (
        "verified"
        if runtime.attempts is not None
        and runtime.context_refills is not None
        and runtime.wall_seconds is not None
        else "unavailable"
    )
    confinement_state = (
        "verified"
        if runtime.execution_confinement_verified is True
        else "failed"
        if runtime.execution_confinement_verified is False
        else "unavailable"
    )
    states = {
        "brief_binding": "verified",
        "artifact_integrity": "verified",
        "declared_scope": "verified",
        "execution_confinement": confinement_state,
        "validation_execution": validation_evidence["state"],
        "budget_accounting": budget_state,
        "result_persistence": "unavailable",
        "caller_acceptance": "unavailable",
    }
    receipt = {
        "schema_version": 1,
        "delegation_id": brief["delegation_id"],
        "brief_sha256": sha256_bytes(brief_bytes),
        "result_path": brief["result_path"],
        "raw_worker": {"sha256": sha256_bytes(raw_worker_bytes), "ref": None},
        "attestations": {
            name: _attestation(
                states[name],
                validation_evidence["source"] if name == "validation_execution" else "adapter",
                validation_evidence["evidence_ref"] if name == "validation_execution" else f"adapter:{name}",
            )
            for name in ATTESTATION_NAMES
        },
        "caller_decision": {
            "decision": "not_decided",
            "source": "caller",
            "evidence_ref": "caller:pending",
        },
        "value_verified": False,
    }
    receipt_errors = validate_receipt(
        receipt,
        brief,
        result,
        repo_root=repo_root,
        brief_bytes=brief_bytes,
        raw_worker_bytes=raw_worker_bytes,
        result_path=brief.get("result_path"),
    )
    if receipt_errors:
        raise AdapterError("invalid verification receipt: " + "; ".join(receipt_errors))
    return result, receipt


def persist_handoff(
    result: Mapping[str, object],
    receipt: Mapping[str, object],
    brief: Mapping[str, object],
    *,
    repo_root: Path,
) -> tuple[Path, Path]:
    """Persist the adapter-owned result and receipt at deterministic siblings."""

    result_path = brief.get("result_path")
    if not isinstance(result_path, str) or receipt.get("result_path") != result_path:
        raise AdapterError("receipt result_path does not match brief result_path")
    write_scope = brief.get("write_scope", [])
    if isinstance(write_scope, list) and _scope_allows(result_path, write_scope):
        raise AdapterError("adapter-owned result_path must remain outside worker write scope")
    result_target = repo_root / result_path
    receipt_target = repo_root / receipt_path_for(result_path)
    if not _inside(result_target, repo_root) or not _inside(receipt_target, repo_root):
        raise AdapterError("result_path or receipt path escapes repository scope")
    result_target.parent.mkdir(parents=True, exist_ok=True)
    persisted_receipt = copy.deepcopy(dict(receipt))
    attestations = persisted_receipt.get("attestations")
    if isinstance(attestations, dict):
        attestations["result_persistence"] = _attestation(
            "verified", "adapter", result_path
        )
    result_target.write_bytes(canonical_json(result) + b"\n")
    receipt_target.write_bytes(canonical_json(persisted_receipt) + b"\n")
    return result_target, receipt_target
