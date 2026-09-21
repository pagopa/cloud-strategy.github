from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").is_file() and (parent / ".github").is_dir()
)
RUNNER = REPO_ROOT / ".github/skills/internal-terraform-import/scripts/import-manifest-runner.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _write_handoff(path: Path, root: Path, *, decision: str = "assess", **overrides: object) -> Path:
    selected_scopes = ["interop"]
    payload: dict[str, object] = {
        "schema_version": 1,
        "kind": "internal-terraform-import-handoff",
        "decision": decision,
        "consumer_root": str(root.resolve()),
        "mode": "hcl",
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
            "mode": "hcl",
            "scopes": selected_scopes,
        },
        "safety_evidence": {
            "identity_status": "pending",
            "ownership_disposition": "unknown",
            "recovery_status": "pending",
        },
        "validation": "protocol and adapter preflight",
    }
    if decision == "execute":
        payload.update(
            {
                "schema_version": 2,
                "run_id": "run-1",
                "decision_id": "decision-1",
                "runtime": "terraform",
                "runtime_version": "1.9.0",
                "execution_mode": "import",
                "import_mode": "hcl",
                "state_boundary": {"scope": "interop", "lineage": "lineage-1", "serial": 1},
                "runner": {
                    "path": str(root / "terraform.sh"),
                    "capabilities": [
                        "remote-lookup",
                        "canonical-identity",
                        "literal-import-id",
                        "state-read",
                        "hcl-import",
                        "configuration-address",
                        "saved-plan",
                        "plan-json",
                        "exact-plan-apply",
                        "post-apply-state-verify",
                        "post-apply-live-verify",
                    ],
                },
                "runner_path": str(root / "terraform.sh"),
                "runner_capabilities": [
                    "remote-lookup",
                    "canonical-identity",
                    "literal-import-id",
                    "state-read",
                    "hcl-import",
                    "configuration-address",
                    "saved-plan",
                    "plan-json",
                    "exact-plan-apply",
                    "post-apply-state-verify",
                    "post-apply-live-verify",
                ],
                "required_capabilities": [
                    "remote-lookup",
                    "canonical-identity",
                    "literal-import-id",
                    "state-read",
                    "hcl-import",
                    "configuration-address",
                    "saved-plan",
                    "plan-json",
                    "exact-plan-apply",
                    "post-apply-state-verify",
                    "post-apply-live-verify",
                ],
                "identity_status": "verified",
                "reconciliation_status": "complete",
                "ownership_disposition": "unmanaged",
                "mutation_authority": {
                    "status": "approved",
                    "actor": "change-approver",
                    "decision_id": "decision-1",
                    "consumer_root": str(root.resolve()),
                    "scopes": ["interop"],
                    "mode": "hcl",
                },
                "adoption_decision": "adopt",
                "runner_status": "verified",
                "recovery_status": "ready",
                "recovery_path": str(root / ".terraform-import-adoption" / "run-1.recovery.json"),
                "live_authorized": True,
                "live_authorization": {
                    "consumer_root": str(root.resolve()),
                    "state_scope": "interop",
                    "scopes": ["interop"],
                    "import_mode": "hcl",
                    "decision_id": "decision-1",
                },
                "canonical_identity_status": "verified",
                "desired_status": "verified",
                "live_status": "verified",
                "state_status": "verified",
                "identity_confirmation": {
                    "status": "confirmed",
                    "consumer_root": str(root.resolve()),
                    "state_scope": "interop",
                    "scopes": ["interop"],
                    "import_mode": "hcl",
                    "decision_id": "decision-1",
                },
                "environment_criticality": "non-production",
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
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def _make_hcl_consumer(
    tmp_path: Path, *, state_identity: str | None = None, plan_fails: bool = False
) -> tuple[Path, Path, Path, Path]:
    root = tmp_path / "consumer"
    root.mkdir()
    state_file = root / "state.tsv"
    calls_file = root / "calls.log"
    applied_marker = root / "applied"
    if state_identity:
        state_file.write_text(
            f'interop\taws_identitystore_group.groups["existing"]\t{state_identity}\n',
            encoding="utf-8",
        )
    else:
        state_file.write_text("", encoding="utf-8")
    _write_executable(
        root / "terraform.sh",
        "#!/usr/bin/env bash\n"
        "set -eu\n"
        f"printf '%s\\n' \"$*\" >> {calls_file!s}\n",
    )
    runner_adapter = tmp_path / "runner-adapter.sh"
    _write_executable(
        runner_adapter,
        "runner_preflight() { return 0; }\n"
        "runner_state_identity() {\n"
        "  if [[ \"$2\" == 'aws_identitystore_group.groups[\"existing\"]' ]]; then\n"
        "    printf '%s\\n' 'store-1/group-existing'; return 0\n"
        "  fi\n"
        f"  if [[ -f {applied_marker!s} ]]; then printf '%s\\n' 'store-1/group-new'; return 0; fi\n"
        "  return 3\n"
        "}\n"
        "runner_import() { return 0; }\n"
        + ("runner_plan() { return 9; }\n" if plan_fails else "runner_plan() { return 0; }\n")
        + "runner_plan_has_create() { return 1; }\n"
        + "runner_destination_exists() { return 0; }\n"
        + "runner_plan_json() { printf '%s\\n' '{\"resource_changes\":[]}'; }\n"
        + "runner_plan_saved() {\n"
        + "  printf '%s' 'saved-plan' > \"$4\"\n"
        + "  actions=\"$(jq -cs 'map(if .disposition == \"moved_candidate\" then {address:.move.to,action:\"moved\",from:.move.from,to:.move.to} else {address,action:\"import\"} end)' \"$5\")\"\n"
        + "  printf '{\"actions\":%s}\\n' \"$actions\"\n"
        + "}\n"
        + "runner_apply_saved() { touch "
        + str(applied_marker)
        + "; }\n"
        "runner_apply() { touch "
        + str(applied_marker)
        + "; }\n",
    )
    resource_adapter = tmp_path / "resource-adapter.sh"
    _write_executable(
        resource_adapter,
        "resolve_import_record() {\n"
        "  jq -c '{canonical_id: .lookup.canonical_id, import_id: .lookup.import_id, key: .lookup.key, to: .lookup.to, provider: .lookup.provider}' <<< \"$1\"\n"
        "}\n",
    )
    return root, runner_adapter, resource_adapter, calls_file


def _manifest(path: Path, records: list[dict[str, object]]) -> Path:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    return path


def _run_hcl(
    manifest: Path,
    *,
    root: Path,
    runner_adapter: Path,
    resource_adapter: Path,
    scope: str | None = "interop",
    decision: str = "assess",
    extra: tuple[str, ...] = (),
    handoff_overrides: dict[str, object] | None = None,
) -> subprocess.CompletedProcess[str]:
    handoff = root / "handoff.json"
    _write_handoff(handoff, root, decision=decision, **(handoff_overrides or {}))
    if decision == "execute":
        payload = json.loads(handoff.read_text(encoding="utf-8"))
        payload["runner_path"] = payload["runner"]["path"]
        payload["runner_capabilities"] = payload["runner"]["capabilities"]
        handoff.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    args = [
        str(RUNNER),
        "--manifest",
        str(manifest),
        "--mode=hcl",
        "--root",
        str(root),
        "--runner-adapter",
        str(runner_adapter),
        "--resource-adapter",
        str(resource_adapter),
        "--handoff",
        str(handoff),
    ]
    if scope is not None:
        args.extend(["--scope", scope])
    args.extend(extra)
    env = os.environ.copy()
    env["APPLIED_MARKER"] = str(root / "applied")
    return subprocess.run(args, cwd=REPO_ROOT, env=env, text=True, capture_output=True)


def _group_record(address: str, key: str, canonical: str, scope: str = "interop") -> dict[str, object]:
    return {
        "scope": scope,
        "address": address,
        "resource_kind": "identitystore_group",
        "lookup": {
            "canonical_id": canonical,
            "import_id": canonical,
            "key": key,
            "to": "aws_identitystore_group.groups[each.key]",
            "provider": "aws.identity_center",
        },
        "disposition": "import_candidate",
    }


def test_hcl_generates_one_scoped_adapter_owned_for_each_import(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, calls_file = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            _group_record('aws_identitystore_group.groups["new"]', "new", "store-1/group-new"),
            _group_record('aws_identitystore_group.groups["other"]', "other", "store-1/group-other", scope="other"),
        ],
    )
    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode == 0
    generated = (root / "imports.generated.tf").read_text(encoding="utf-8")
    assert '"store-1/group-new"' in generated
    assert "aws_identitystore_group.groups[each.key]" in generated
    assert "aws.identity_center" in generated
    assert 'groups["new"]' not in generated
    assert "store-1/group-other" not in generated
    assert not calls_file.exists()


def test_hcl_excludes_state_confirmed_addresses(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path, state_identity="store-1/group-existing")
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            _group_record('aws_identitystore_group.groups["existing"]', "existing", "store-1/group-existing"),
            _group_record('aws_identitystore_group.groups["new"]', "new", "store-1/group-new"),
        ],
    )
    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode == 0
    generated = (root / "imports.generated.tf").read_text(encoding="utf-8")
    assert "group-existing" not in generated
    assert "group-new" in generated


def test_hcl_assessment_defers_absent_create(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            {
                **_group_record("aws.future", "future", "store-1/group-future"),
                "disposition": "absent_create",
            },
            _group_record("aws.new", "new", "store-1/group-new"),
        ],
    )

    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)

    assert result.returncode == 0
    assert '"status":"excluded_by_disposition"' in result.stdout
    generated = (root / "imports.generated.tf").read_text(encoding="utf-8")
    assert "group-future" not in generated
    assert "group-new" in generated


@pytest.mark.parametrize(
    "disposition",
    [
        "absent_create",
        "collision",
        "disputed_ownership",
        "ambiguous_live_identity",
        "unsupported_capability",
    ],
)
def test_hcl_assessment_excludes_non_adoption_records_without_generation(
    tmp_path: Path, disposition: str
) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            {
                "scope": "interop",
                "address": "aws.collision",
                "resource_kind": "identitystore_group",
                "lookup": {},
                "disposition": disposition,
            }
        ],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode == 0
    assert '"status":"excluded_by_disposition"' in result.stdout
    assert not (root / "imports.generated.tf").exists()


def test_hcl_requires_one_selected_scope(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )
    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter, scope=None)
    assert result.returncode != 0
    assert "exactly one scope" in result.stderr


def test_hcl_rejects_selected_scope_not_authorized_by_handoff(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        scope="other",
    )

    assert result.returncode != 0
    assert "scope" in result.stderr


def test_hcl_requires_verified_configuration_destination(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_destination_exists() { return 1; }\n",
        encoding="utf-8",
    )
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "configuration destination" in result.stderr


def test_hcl_rejects_mixed_destination_metadata_for_one_resource_kind(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            _group_record("aws.foo", "new", "store-1/group-new"),
            {
                **_group_record("aws.other", "other", "store-1/group-other"),
                "lookup": {
                    "canonical_id": "store-1/group-other",
                    "import_id": "store-1/group-other",
                    "key": "other",
                    "to": "aws.other.groups[each.key]",
                    "provider": "aws.other",
                },
            },
        ],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "homogeneous" in result.stderr


def test_hcl_assessment_rejects_duplicate_manifest_addresses(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    record = _group_record("aws.foo", "new", "store-1/group-new")
    manifest = _manifest(tmp_path / "imports.jsonl", [record, record])

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "duplicate manifest address" in result.stderr


def test_hcl_retains_generated_file_after_plan_failure(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path, plan_fails=True)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )
    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter, decision="execute", extra=("--live",))
    assert result.returncode != 0
    assert (root / "imports.generated.tf").is_file()


def test_hcl_live_persists_recovery_record_on_failure(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path, plan_fails=True)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode != 0
    recovery_path = root / ".terraform-import-adoption" / "run-1.recovery.json"
    assert recovery_path.is_file()
    recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
    assert recovery["status"] == "failed"
    assert recovery["run_id"] == "run-1"


def test_hcl_live_reports_recovery_persistence_failure(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path, plan_fails=True)
    recovery_path = root / ".terraform-import-adoption" / "run-1.recovery.json"
    recovery_path.mkdir(parents=True)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "unable to persist live recovery record" in result.stderr


def test_hcl_live_rejects_malformed_existing_recovery_record(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path, plan_fails=True)
    recovery_path = root / ".terraform-import-adoption" / "run-1.recovery.json"
    recovery_path.parent.mkdir(parents=True)
    recovery_path.write_text("{}\n", encoding="utf-8")
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "unable to persist live recovery record" in result.stderr


def test_hcl_removes_file_only_after_live_verification_and_post_plan(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(tmp_path / "imports.jsonl", [_group_record('aws_identitystore_group.groups["new"]', "new", "store-1/group-new")])
    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter, decision="execute", extra=("--live",))
    assert result.returncode == 0
    assert not (root / "imports.generated.tf").exists()


def test_hcl_live_applies_the_exact_saved_plan_artifact(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, calls_file = _make_hcl_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_saved() { printf '%s' 'saved-plan' > \"$4\"; printf '%s\\n' '{\"actions\":[{\"address\":\"aws.foo\",\"action\":\"import\"}]}'; }\n"
        + f"runner_apply_saved() {{ printf 'apply-saved %s\\n' \"$4\" >> {calls_file!s}; touch \"$1/applied\"; }}\n",
        encoding="utf-8",
    )
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode == 0
    assert any(line.startswith("apply-saved ") for line in calls_file.read_text(encoding="utf-8").splitlines())


def test_hcl_live_rejects_partial_saved_plan_records_without_overwrite(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    adoption_dir = root / ".terraform-import-adoption"
    adoption_dir.mkdir()
    artifact = adoption_dir / "run-1.plan"
    artifact.write_bytes(b"original-plan")
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "incomplete" in result.stderr
    assert artifact.read_bytes() == b"original-plan"


def test_hcl_live_persists_authorization_evidence_and_completion_receipt(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode == 0
    records_dir = root / ".terraform-import-adoption"
    authorization = json.loads((records_dir / "run-1.authorization.json").read_text(encoding="utf-8"))
    evidence = json.loads((records_dir / "run-1.evidence.json").read_text(encoding="utf-8"))
    receipt = json.loads((records_dir / "run-1.receipt.json").read_text(encoding="utf-8"))
    assert authorization["run_id"] == "run-1"
    assert evidence["run_id"] == "run-1"
    assert receipt["final_status"] == "completed"
    assert receipt["authorization_digest"].startswith("sha256:")
    assert receipt["evidence_digest"].startswith("sha256:")
    assert evidence["inventory_digests"]["desired"].startswith("sha256:")
    assert evidence["inventory_digests"]["live"].startswith("sha256:")
    assert evidence["inventory_digests"]["state"].startswith("sha256:")
    assert evidence["state_boundary"]["lineage"] == "lineage-1"
    assert evidence["tool_versions"] == {"terraform": "1.9.0"}
    assert evidence["reconciliation"]


@pytest.mark.parametrize(
    "record_name",
    ["authorization", "evidence", "recovery", "receipt", "plan-envelope"],
)
def test_hcl_live_rejects_mutated_immutable_record(tmp_path: Path, record_name: str) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    first_result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )
    assert first_result.returncode == 0
    (root / "applied").unlink()

    record_path = root / ".terraform-import-adoption" / f"run-1.{record_name}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["tampered"] = True
    record_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    second_result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert second_result.returncode != 0
    assert "immutable" in second_result.stderr or "changed" in second_result.stderr


def test_hcl_live_ignores_records_outside_selected_scope_before_normalization(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            _group_record("aws.foo", "new", "store-1/group-new"),
            {
                "scope": "other",
                "address": "aws.other",
                "resource_kind": "identitystore_group",
                "lookup": {},
                "disposition": "import_candidate",
            },
        ],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode == 0


def test_hcl_live_rejects_extra_saved_plan_operations(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    applied_marker = root / "extra-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_saved() {\n"
        + "  printf '%s' 'saved-plan' > \"$4\"\n"
        + "  printf '%s\\n' '{\"actions\":[{\"address\":\"aws_identitystore_group.groups[\\\"new\\\"]\",\"action\":\"import\"},{\"address\":\"aws.extra\",\"action\":\"import\"}]}'\n"
        + "}\n"
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record('aws_identitystore_group.groups["new"]', "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode != 0
    assert "extra" in result.stderr
    assert not applied_marker.exists()


def test_hcl_live_applies_only_a_proven_state_move(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    applied_marker = root / "applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_state_identity() {\n"
        + "  if [[ \"$2\" == resource.old ]]; then printf '%s\\n' 'store-1/group-moved'; return 0; fi\n"
        + f"  if [[ \"$2\" == resource.new && -f {applied_marker!s} ]]; then printf '%s\\n' 'store-1/group-moved'; return 0; fi\n"
        + "  return 3\n"
        + "}\n"
        + "runner_plan_json() {\n"
        + f"  if [[ -f {applied_marker!s} ]]; then printf '%s\\n' '{{\"actions\":[]}}'; else printf '%s\\n' '{{\"actions\":[{{\"address\":\"resource.new\",\"action\":\"moved\",\"from\":\"resource.old\",\"to\":\"resource.new\"}}]}}'; fi\n"
        + "}\n"
        + "runner_plan_saved() { printf '%s' 'moved-plan' > \"$4\"; printf '%s\\n' '{\"actions\":[{\"address\":\"resource.new\",\"action\":\"moved\",\"from\":\"resource.old\",\"to\":\"resource.new\"}]}'; }\n"
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )
    capabilities = [
        "remote-lookup",
        "canonical-identity",
        "literal-import-id",
        "state-read",
        "hcl-import",
        "configuration-address",
        "state-move",
        "saved-plan",
        "plan-json",
        "exact-plan-apply",
        "post-apply-state-verify",
        "post-apply-live-verify",
    ]
    manifest = _manifest(
        tmp_path / "moves.jsonl",
        [
            {
                "scope": "interop",
                "address": "resource.new",
                "resource_kind": "generic_group",
                "lookup": {
                    "canonical_id": "store-1/group-moved",
                    "import_id": "store-1/group-moved",
                    "key": "new",
                    "to": "resource.groups[each.key]",
                    "provider": "aws.identity_center",
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

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
        handoff_overrides={
            "runner": {"path": str(root / "terraform.sh"), "capabilities": capabilities},
            "required_capabilities": capabilities,
        },
    )

    assert result.returncode == 0
    assert '"status":"moved"' in result.stdout
    assert not (root / "imports.generated.tf").exists()


def test_hcl_live_persists_authorization_before_exact_apply(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_apply_saved() {\n"
        + "  if [[ ! -f \"$1/.terraform-import-adoption/run-1.authorization.json\" ]]; then return 42; fi\n"
        + "  touch \"$1/applied\"\n"
        + "}\n",
        encoding="utf-8",
    )
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record("aws.foo", "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        decision="execute",
        extra=("--live",),
    )

    assert result.returncode == 0


def test_script_mode_rejects_record_selected_for_hcl(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(tmp_path / "imports.jsonl", [{**_group_record("aws.foo", "new", "id"), "mode": "hcl"}])
    handoff = tmp_path / "script-handoff.json"
    _write_handoff(handoff, root, decision="assess")
    result = subprocess.run(
        [
            str(RUNNER), "--manifest", str(manifest), "--mode=script", "--root", str(root),
            "--runner-adapter", str(runner_adapter), "--resource-adapter", str(resource_adapter),
            "--handoff", str(handoff),
        ],
        cwd=REPO_ROOT, text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "mode" in result.stderr


@pytest.mark.parametrize("bad_field", ["to", "provider"])
def test_hcl_requires_adapter_owned_destination_metadata(tmp_path: Path, bad_field: str) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    record = _group_record("aws.foo", "new", "id")
    record["lookup"][bad_field] = ""
    manifest = _manifest(tmp_path / "imports.jsonl", [record])
    result = _run_hcl(manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter)
    assert result.returncode != 0
    assert "metadata" in result.stderr
