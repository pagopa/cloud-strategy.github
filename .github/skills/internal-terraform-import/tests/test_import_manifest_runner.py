from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
RUNNER = BUNDLE_ROOT / "scripts/import-manifest-runner.sh"
FIXTURE = BUNDLE_ROOT / "tests/fixtures/imports.valid.jsonl"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _make_consumer(tmp_path: Path, *, capability: bool = True) -> tuple[Path, Path, Path]:
    root = tmp_path / "consumer"
    root.mkdir()
    state_file = root / "state.tsv"
    calls_file = root / "calls.log"
    state_file.write_text(
        "interop\taws_identitystore_group.groups[\"existing\"]\tstore-1/group-existing\n",
        encoding="utf-8",
    )
    _write_executable(
        root / "terraform.sh",
        "#!/usr/bin/env bash\n"
        "set -eu\n"
        f"printf '%s\\n' \"$*\" >> {calls_file!s}\n",
    )
    runner_adapter = tmp_path / "runner-adapter.sh"
    _write_executable(
        runner_adapter,
        "runner_preflight() {\n"
        + ("  [[ \"${CAPABILITY_PROOF:-}\" == yes ]]\n" if capability else "  return 21\n")
        + "}\n"
        "runner_state_identity() {\n"
        "  local wanted_scope=$1 wanted_address=$2 line scope address canonical\n"
        "  while IFS=$'\\t' read -r scope address canonical; do\n"
        "    if [[ \"$scope\" == \"$wanted_scope\" && \"$address\" == \"$wanted_address\" ]]; then\n"
        "      printf '%s\\n' \"$canonical\"\n"
        "      return 0\n"
        "    fi\n"
        "  done < \"$STATE_FILE\"\n"
        "  return 3\n"
        "}\n"
        "runner_import() {\n"
        "  local scope=$1 address=$2 import_id=$3\n"
        "  \"$TERRAFORM_RUNNER\" import \"$scope\" \"$address\" \"$import_id\"\n"
        "  printf '%s\\t%s\\t%s\\n' \"$scope\" \"$address\" \"$import_id\" >> \"$STATE_FILE\"\n"
        "}\n"
        "runner_plan() { return 0; }\n"
        "runner_plan_has_create() { return 1; }\n"
        "runner_plan_json() {\n"
        "  if [[ -f \"$1/applied\" ]]; then printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"missing\\\"]\",\"action\":\"no-op\"}]}'\n"
        "  else printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"missing\\\"]\",\"action\":\"import\"}]}'\n"
        "  fi\n"
        "}\n"
        "runner_plan_saved() {\n"
        "  printf '%s' 'saved-plan' > \"$4\"\n"
        "  actions=\"$(jq -cs 'map(if .disposition == \"moved_candidate\" then {address:.move.to,action:\"moved\",from:.move.from,to:.move.to} else {address,action:\"import\"} end)' \"$3\")\"\n"
        "  printf '{\"actions\":%s}\\n' \"$actions\"\n"
        "}\n"
        "runner_apply_saved() {\n"
        "  local item scope address import_id\n"
        "  while IFS= read -r item; do\n"
        "    [[ \"$(jq -r '.disposition' <<< \"$item\")\" == import_candidate ]] || continue\n"
        "    scope=\"$(jq -r '.scope' <<< \"$item\")\"\n"
        "    address=\"$(jq -r '.address' <<< \"$item\")\"\n"
        "    import_id=\"$(jq -r '.lookup.import_id' <<< \"$item\")\"\n"
        "    \"$TERRAFORM_RUNNER\" import \"$scope\" \"$address\" \"$import_id\"\n"
        "    printf '%s\\t%s\\t%s\\n' \"$scope\" \"$address\" \"$import_id\" >> \"$STATE_FILE\"\n"
        "  done < \"$3\"\n"
        "  touch \"$1/applied\"\n"
        "}\n",
    )
    resource_adapter = tmp_path / "resource-adapter.sh"
    _write_executable(
        resource_adapter,
        "resolve_import_record() {\n"
        "  if [[ \"$(jq -r '.lookup.status // empty' <<< \"$1\")\" == failed ]]; then\n"
        "    printf '%s\\n' '{\"status\":\"aws_error\"}'\n"
        "    return 0\n"
        "  fi\n"
        "  jq -c '{canonical_id: .lookup.canonical_id, import_id: .lookup.import_id}' <<< \"$1\"\n"
        "}\n",
    )
    return root, runner_adapter, resource_adapter


def _write_handoff(
    path: Path,
    *,
    root: Path,
    mode: str = "script",
    decision: str = "assess",
    scopes: list[str] | None = None,
    **overrides: object,
) -> Path:
    selected_scopes = scopes or ["interop"]
    payload: dict[str, object] = {
        "schema_version": 1,
        "kind": "internal-terraform-import-handoff",
        "decision": decision,
        "consumer_root": str(root.resolve()),
        "mode": mode,
        "scopes": selected_scopes,
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
            "consumer_root": str(root.resolve()),
            "mode": mode,
            "scopes": selected_scopes,
        },
        "safety_evidence": {
            "identity_status": "pending",
            "ownership_disposition": "unknown",
            "recovery_status": "pending",
        },
        "validation": "protocol and adapter preflight",
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def _execute_handoff(path: Path, *, root: Path, mode: str = "script") -> Path:
    return _write_handoff(
        path,
        root=root,
        mode=mode,
        decision="execute",
        schema_version=2,
        run_id="run-1",
        state_boundary={"scope": "interop", "lineage": "lineage-1", "serial": 1},
        runner={
            "path": str(root / "terraform.sh"),
            "capabilities": [
                "remote-lookup",
                "canonical-identity",
                "literal-import-id",
                "state-read",
                "script-import",
                "state-move",
                "saved-plan",
                "plan-json",
                "exact-plan-apply",
                "post-apply-state-verify",
                "post-apply-live-verify",
            ],
        },
        required_capabilities=[
            "remote-lookup",
            "canonical-identity",
            "literal-import-id",
            "state-read",
            "script-import",
            "state-move",
            "saved-plan",
            "plan-json",
            "exact-plan-apply",
            "post-apply-state-verify",
            "post-apply-live-verify",
        ],
        identity_status="verified",
        reconciliation_status="complete",
        ownership_disposition="unmanaged",
        mutation_authority={
            "status": "approved",
            "actor": "change-approver",
            "decision_id": "decision-1",
            "consumer_root": str(root.resolve()),
            "scopes": ["interop"],
            "mode": mode,
        },
        adoption_decision="adopt",
        convergence_decision="adoption-only",
        runner_status="verified",
        recovery_status="ready",
        recovery_path=str(root / ".terraform-import-adoption" / "run-1.recovery.json"),
        live_authorized=True,
        live_authorization={
            "consumer_root": str(root.resolve()),
            "state_scope": "interop",
            "scopes": ["interop"],
            "import_mode": mode,
            "decision_id": "decision-1",
        },
        identity_confirmation={
            "status": "confirmed",
            "consumer_root": str(root.resolve()),
            "state_scope": "interop",
            "scopes": ["interop"],
            "import_mode": mode,
            "decision_id": "decision-1",
        },
        canonical_identity_status="verified",
        desired_status="verified",
        live_status="verified",
        state_status="verified",
        environment_criticality="non-production",
        evidence_references=["evidence/run-1.json"],
        configuration_digest="sha256:config",
        dependency_lock_digest="sha256:lock",
        tool_versions={"terraform": "1.9.0"},
        decision_id="decision-1",
        runtime="terraform",
        runtime_version="1.9.0",
        execution_mode="import",
        import_mode=mode,
        runner_path=str(root / "terraform.sh"),
        runner_capabilities=[
            "remote-lookup",
            "canonical-identity",
            "literal-import-id",
            "state-read",
            "script-import",
            "state-move",
            "saved-plan",
            "plan-json",
            "exact-plan-apply",
            "post-apply-state-verify",
            "post-apply-live-verify",
        ],
    )


def _run_runner(
    manifest: Path,
    *,
    root: Path,
    runner_adapter: Path,
    resource_adapter: Path,
    mode: str = "script",
    include_handoff: bool = True,
    handoff_data: dict[str, object] | None = None,
    extra: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({"CAPABILITY_PROOF": "yes", "STATE_FILE": str(root / "state.tsv")})
    args = [
        str(RUNNER),
        "--manifest",
        str(manifest),
        "--mode",
        mode,
        "--root",
        str(root),
        "--runner-adapter",
        str(runner_adapter),
        "--resource-adapter",
        str(resource_adapter),
    ]
    if include_handoff:
        handoff = root / "handoff.json"
        if handoff_data and handoff_data.get("decision") == "execute":
            _execute_handoff(handoff, root=root, mode=mode)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload.update(handoff_data)
            payload["runner_capabilities"] = payload["runner"]["capabilities"]
            handoff.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        else:
            payload = {"mode": mode}
            payload.update(handoff_data or {})
            _write_handoff(handoff, root=root, **payload)
        args.extend(["--handoff", str(handoff)])
    args.extend(extra)
    return subprocess.run(args, cwd=BUNDLE_ROOT, env=env, text=True, capture_output=True)


def _write_manifest(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _moved_record() -> dict[str, object]:
    return {
        "scope": "interop",
        "address": "resource.new",
        "resource_kind": "generic_group",
        "lookup": {
            "canonical_id": "store-1/group-moved",
            "import_id": "store-1/group-moved",
        },
        "disposition": "moved_candidate",
        "move": {
            "from": "resource.old",
            "to": "resource.new",
            "canonical_id": "store-1/group-moved",
            "state_lineage": "lineage-1",
            "collision_free": True,
            "remote_mutation": False,
        },
    }


def test_runner_skips_managed_and_resumes_without_duplicate_import(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    first = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert first.returncode == 0
    assert "Skipped already managed: 1" in first.stdout
    assert '"status":"skipped_already_managed"' in first.stdout
    assert '"status":"imported"' in first.stdout
    assert (root / "calls.log").read_text(encoding="utf-8").splitlines() == [
        'import interop aws_identitystore_group.groups["missing"] store-1/group-missing'
    ]

    resumed = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )
    assert resumed.returncode == 0
    assert "Skipped already managed: 2" in resumed.stdout
    assert (root / "calls.log").read_text(encoding="utf-8").splitlines() == [
        'import interop aws_identitystore_group.groups["missing"] store-1/group-missing'
    ]


def test_runner_assessment_rejects_duplicate_manifest_addresses(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    duplicate_manifest = tmp_path / "duplicate.jsonl"
    record = json.loads(FIXTURE.read_text(encoding="utf-8").splitlines()[0])
    _write_manifest(duplicate_manifest, [record, record])

    result = _run_runner(
        duplicate_manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "duplicate manifest address" in result.stderr
    assert not (root / "calls.log").exists()


def test_missing_handoff_stops_before_adapter_loading(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        include_handoff=False,
    )

    assert result.returncode != 0
    assert "--handoff is required" in result.stderr
    assert not (root / "calls.log").exists()


def test_assessment_rejects_live_execution(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--live",),
    )

    assert result.returncode != 0
    assert not (root / "calls.log").exists()


def test_live_execution_requires_protocol_v2(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute", "schema_version": 1},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "assessment" in result.stderr
    assert not (root / "calls.log").exists()


def test_live_script_mode_blocks_update_from_machine_readable_plan(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_json() {\n"
        + "  printf '%s\\n' '{\"resource_changes\":[{\"address\":\"aws_resource.example\",\"change\":{\"actions\":[\"update\"]}}]}'\n"
        + "}\n",
        encoding="utf-8",
    )
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "update" in result.stderr
    assert not (root / "calls.log").exists()


def test_live_script_mode_applies_exact_saved_plan_and_writes_receipt(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_json() {\n"
        + "  if [[ -f \"$1/applied\" ]]; then printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"missing\\\"]\",\"action\":\"no-op\"}]}'; else printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"missing\\\"]\",\"action\":\"import\"}]}'; fi\n"
        + "}\n"
        + "runner_plan_saved() {\n"
        + "  printf '%s' 'script-saved-plan' > \"$4\"\n"
        + "  printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"missing\\\"]\",\"action\":\"import\"}]}'\n"
        + "}\n"
        + "runner_apply_saved() {\n"
        + "  if [[ ! -f \"$1/.terraform-import-adoption/run-1.authorization.json\" ]]; then return 42; fi\n"
        + f"  printf 'apply-saved %s\\n' \"$4\" >> {root / 'calls.log'!s}\n"
        + "  printf '%s\\t%s\\t%s\\n' 'interop' 'aws_identitystore_group.groups[\"missing\"]' 'store-1/group-missing' >> \"$STATE_FILE\"\n"
        + "  touch \"$1/applied\"\n"
        + "}\n",
        encoding="utf-8",
    )
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
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={
            "decision": "execute",
            "runner": {"path": str(root / "terraform.sh"), "capabilities": capabilities},
            "required_capabilities": capabilities,
        },
        extra=("--live",),
    )

    assert result.returncode == 0
    assert any(line.startswith("apply-saved ") for line in (root / "calls.log").read_text(encoding="utf-8").splitlines())
    records_dir = root / ".terraform-import-adoption"
    assert (records_dir / "run-1.authorization.json").is_file()
    assert (records_dir / "run-1.evidence.json").is_file()
    assert (records_dir / "run-1.receipt.json").is_file()
    evidence = json.loads((records_dir / "run-1.evidence.json").read_text(encoding="utf-8"))
    assert set(evidence["inventory_digests"]) == {"desired", "live", "state"}
    assert evidence["state_boundary"]["serial"] == 1
    assert evidence["tool_versions"] == {"terraform": "1.9.0"}
    reconciliation = {
        item["address"]: item
        for item in evidence["reconciliation"]
    }
    assert reconciliation[
        'aws_identitystore_group.groups["existing"]'
    ]["observed_status"] == "already_managed"
    assert reconciliation[
        'aws_identitystore_group.groups["missing"]'
    ]["observed_identity"]["canonical_id"] == "store-1/group-missing"


def test_live_script_reconfirms_identity_before_exact_apply(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    counter = tmp_path / "resolver-count"
    resource_adapter.write_text(
        "#!/usr/bin/env bash\n"
        "resolve_import_record() {\n"
        f"  count=0; if [[ -f {counter!s} ]]; then count=\"$(cat {counter!s})\"; fi; count=$((count + 1)); printf '%s' \"$count\" > {counter!s}\n"
        "  if [[ \"$count\" -gt 2 ]]; then printf '%s\\n' '{\"canonical_id\":\"store-1/changed\",\"import_id\":\"store-1/changed\"}'; else jq -c '{canonical_id: .lookup.canonical_id, import_id: .lookup.import_id}' <<< \"$1\"; fi\n"
        "}\n",
        encoding="utf-8",
    )
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "identity confirmation" in result.stderr
    assert not (root / "applied").exists()


def test_live_script_mode_uses_adapter_resolved_import_id(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    resource_adapter.write_text(
        resource_adapter.read_text(encoding="utf-8")
        + "resolve_import_record() { printf '%s\\n' '{\"canonical_id\":\"resolved/group\",\"import_id\":\"resolved/group\"}'; }\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "resolved-id.jsonl"
    _write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": "aws_identitystore_group.groups[\"missing\"]",
                "resource_kind": "identitystore_group",
                "lookup": {},
                "disposition": "import_candidate",
            }
        ],
    )

    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode == 0
    assert (root / "calls.log").read_text(encoding="utf-8").splitlines() == [
        'import interop aws_identitystore_group.groups["missing"] resolved/group'
    ]


def test_live_script_mode_rejects_move_with_wrong_source_identity(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\tresource.old\tstore-1/not-moved\n", encoding="utf-8"
    )
    applied_marker = root / "move-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_move() { return 0; }\n"
        + "runner_plan_saved() { printf '%s' 'moved-plan' > \"$4\"; printf '%s\\n' '{\"actions\":[{\"address\":\"resource.new\",\"action\":\"moved\",\"from\":\"resource.old\",\"to\":\"resource.new\"}]}'; }\n"
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "wrong-source.jsonl"
    _write_manifest(manifest, [_moved_record()])

    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "source" in result.stderr
    assert not applied_marker.exists()


def test_live_script_mode_rejects_move_destination_collision(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\tresource.old\tstore-1/group-moved\n"
        "interop\tresource.new\tstore-1/other\n",
        encoding="utf-8",
    )
    applied_marker = root / "move-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_move() { return 0; }\n"
        + "runner_plan_saved() { printf '%s' 'moved-plan' > \"$4\"; printf '%s\\n' '{\"actions\":[{\"address\":\"resource.new\",\"action\":\"moved\",\"from\":\"resource.old\",\"to\":\"resource.new\"}]}'; }\n"
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "collision.jsonl"
    _write_manifest(manifest, [_moved_record()])

    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "already managed" in result.stderr
    assert not applied_marker.exists()


def test_live_script_mode_rejects_extra_saved_plan_operations(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    applied_marker = root / "extra-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_saved() {\n"
        + "  printf '%s' 'saved-plan' > \"$4\"\n"
        + "  printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"missing\\\"]\",\"action\":\"import\"},{\"address\":\"aws.extra\",\"action\":\"import\"}]}'\n"
        + "}\n"
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )

    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "extra" in result.stderr
    assert not applied_marker.exists()


def test_live_script_mode_excludes_absent_create_from_adoption(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "absent-create.jsonl"
    _write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": "aws_identitystore_group.groups[\"future\"]",
                "resource_kind": "identitystore_group",
                "lookup": {
                    "canonical_id": "store-1/group-future",
                    "import_id": "store-1/group-future",
                },
                "disposition": "absent_create",
            }
        ],
    )
    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode == 0
    assert '"status":"excluded_by_disposition"' in result.stdout
    assert not (root / "calls.log").exists()


def test_live_script_mode_applies_only_proven_state_moves(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\tresource.old\tstore-1/group-moved\n", encoding="utf-8"
    )
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_json() { printf '%s\\n' '{\"actions\":[{\"address\":\"resource.new\",\"action\":\"moved\",\"from\":\"resource.old\",\"to\":\"resource.new\"}]}'; }\n"
        + "runner_move() { printf '%s\\n' 'interop\tresource.new\tstore-1/group-moved' > \"$STATE_FILE\"; }\n"
        + "runner_plan_saved() { printf '%s' 'moved-plan' > \"$4\"; printf '%s\\n' '{\"actions\":[{\"address\":\"resource.new\",\"action\":\"moved\",\"from\":\"resource.old\",\"to\":\"resource.new\"}]}'; }\n"
        + "runner_apply_saved() { runner_move; }\n",
    )
    manifest = tmp_path / "moved.jsonl"
    _write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": "resource.new",
                "resource_kind": "generic_group",
                "lookup": {
                    "canonical_id": "store-1/group-moved",
                    "import_id": "store-1/group-moved",
                },
                "disposition": "moved_candidate",
                "move": {
                    "from": "resource.old",
                    "to": "resource.new",
                    "canonical_id": "store-1/group-moved",
                    "state_lineage": "lineage-1",
                    "collision_free": True,
                    "remote_mutation": False,
                },
            }
        ],
    )

    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live",),
    )

    assert result.returncode == 0
    assert '"status":"moved"' in result.stdout
    assert not (root / "calls.log").exists()


def test_live_execution_requires_complete_protocol_v2_evidence(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute", "run_id": ""},
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "run_id" in result.stderr
    assert not (root / "calls.log").exists()


def test_protocol_v1_execute_handoff_is_rejected_before_assessment(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)

    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"schema_version": 1, "decision": "execute"},
    )

    assert result.returncode != 0
    assert "assessment" in result.stderr
    assert not (root / "calls.log").exists()


def test_incomplete_wrapper_projection_stops_before_adapter_calls(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)

    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"execution_owner": None},
    )

    assert result.returncode != 0
    assert "execution_owner" in result.stderr
    assert not (root / "calls.log").exists()


def test_live_runner_override_must_match_handoff_path(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    alternate_runner = root / "alternate-terraform.sh"
    _write_executable(alternate_runner, "#!/usr/bin/env bash\nexit 0\n")

    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--live", "--runner", str(alternate_runner)),
    )

    assert result.returncode != 0
    assert "runner path" in result.stderr
    assert not (root / "calls.log").exists()


def test_assessment_runner_override_requires_handoff_path(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    alternate_runner = root / "alternate-terraform.sh"
    _write_executable(alternate_runner, "#!/usr/bin/env bash\nexit 0\n")

    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--runner", str(alternate_runner)),
    )

    assert result.returncode != 0
    assert "runner path" in result.stderr
    assert not (root / "calls.log").exists()


def test_default_script_mode_never_calls_runner_import(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode == 0
    assert "Dry-run candidate" in result.stdout
    assert not (root / "calls.log").exists()


@pytest.mark.parametrize(
    "missing_field",
    [
        "identity_status",
        "reconciliation_status",
        "ownership_disposition",
        "mutation_authority",
        "convergence_decision",
        "runner_status",
        "recovery_status",
    ],
)
def test_live_script_mode_requires_complete_execute_evidence(
    tmp_path: Path, missing_field: str
) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    handoff = tmp_path / "handoff.json"
    _execute_handoff(handoff, root=root)
    payload = json.loads(handoff.read_text(encoding="utf-8"))
    payload[missing_field] = "pending" if missing_field.endswith("status") else "unknown"
    handoff.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            str(RUNNER),
            "--manifest",
            str(FIXTURE),
            "--mode",
            "script",
            "--root",
            str(root),
            "--runner-adapter",
            str(runner_adapter),
            "--resource-adapter",
            str(resource_adapter),
            "--handoff",
            str(handoff),
            "--live",
        ],
        cwd=BUNDLE_ROOT,
        env={**os.environ, "CAPABILITY_PROOF": "yes", "STATE_FILE": str(root / "state.tsv")},
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert not (root / "calls.log").exists()


@pytest.mark.parametrize(
    ("handoff_data", "expected"),
    [
        ({"consumer_root": "/different/root"}, "root"),
        ({"mode": "hcl"}, "mode"),
        ({"scopes": ["other"]}, "scope"),
    ],
)
def test_handoff_root_mode_and_scopes_must_match_the_run(
    tmp_path: Path, handoff_data: dict[str, object], expected: str
) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data=handoff_data,
    )

    assert result.returncode != 0
    assert expected in result.stderr
    assert not (root / "calls.log").exists()


def test_dry_run_and_live_are_mutually_exclusive(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--dry-run", "--live"),
    )

    assert result.returncode != 0
    assert "mutually exclusive" in result.stderr
    assert not (root / "calls.log").exists()


def test_runner_rejects_malformed_jsonl(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "malformed.jsonl"
    manifest.write_text('{"scope":"interop"}\nnot-json\n', encoding="utf-8")
    result = _run_runner(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode != 0
    assert "malformed JSONL" in result.stderr


def test_runner_rejects_renderer_escape_artifacts(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "escaped.jsonl"
    manifest.write_text(
        '{"scope":"interop","address":"aws.foo[\\u003cname\\u003e]",'
        '"resource_kind":"identitystore_group","lookup":{"canonical_id":"id","import_id":"id"}}\n',
        encoding="utf-8",
    )
    result = _run_runner(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode != 0
    assert "escape artifact" in result.stderr


def test_runner_requires_executable_default_wrapper(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "terraform.sh").chmod(stat.S_IRUSR | stat.S_IWUSR)
    result = _run_runner(FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode != 0
    assert "executable terraform.sh" in result.stderr


def test_runner_requires_adapter_capability_proof(tmp_path: Path) -> None:
    root, _, resource_adapter = _make_consumer(tmp_path, capability=False)
    runner_adapter = tmp_path / "incomplete-adapter.sh"
    _write_executable(runner_adapter, "runner_preflight() { return 21; }\n")
    result = _run_runner(FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode != 0
    assert "capability" in result.stderr


def test_runner_fails_closed_on_state_identity_mismatch(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\taws_identitystore_group.groups[\"existing\"]\tstore-1/wrong\n",
        encoding="utf-8",
    )
    result = _run_runner(FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode != 0
    assert "ambiguous" in result.stdout
    assert "store-1/wrong" in result.stderr


def test_runner_continue_on_error_reports_nonzero_after_processing_remaining_records(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "continue.jsonl"
    _write_manifest(
        manifest,
        [
            {"scope": "interop", "address": "aws_identitystore_group.groups[\"broken\"]", "resource_kind": "identitystore_group", "lookup": {"status": "failed", "canonical_id": "store-1/group-broken", "import_id": "store-1/group-broken"}, "disposition": "import_candidate"},
            {"scope": "interop", "address": "aws_identitystore_group.groups[\"new\"]", "resource_kind": "identitystore_group", "lookup": {"canonical_id": "store-1/group-new", "import_id": "store-1/group-new"}, "disposition": "import_candidate"},
        ],
    )
    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute"},
        extra=("--continue-on-error", "--live"),
    )
    assert result.returncode != 0
    assert '"status":"aws_error"' in result.stdout
    assert '"status":"imported"' in result.stdout
    assert "AWS errors: 1" in result.stdout


def test_hcl_mode_requires_an_explicit_scope(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        mode="hcl",
        handoff_data={"mode": "hcl"},
    )
    args = result.stderr
    assert result.returncode != 0
    assert "scope" in args
