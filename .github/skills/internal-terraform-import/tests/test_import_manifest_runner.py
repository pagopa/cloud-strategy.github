from __future__ import annotations

import json
import os
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
RUNNER = BUNDLE_ROOT / "scripts/import-manifest-runner.sh"
FIXTURE = BUNDLE_ROOT / "tests/fixtures/imports.valid.jsonl"

MakeConsumer = Callable[..., tuple[Path, Path, Path]]
RunRunner = Callable[..., subprocess.CompletedProcess[str]]
WriteExecutable = Callable[[Path, str], Path]
WriteManifest = Callable[[Path, list[dict[str, object]]], Path]


@pytest.fixture
def make_consumer(write_executable: WriteExecutable) -> MakeConsumer:
    def _make(tmp_path: Path, *, capability: bool = True) -> tuple[Path, Path, Path]:
        return _build_consumer(tmp_path, write_executable, capability=capability)

    return _make


@pytest.fixture
def run_runner(handoff_payload: Callable[..., dict[str, object]]) -> RunRunner:
    def _run(manifest: Path, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return _invoke_runner(manifest, handoff_payload=handoff_payload, **kwargs)  # type: ignore[arg-type]

    return _run


def _build_consumer(
    tmp_path: Path, write_executable: WriteExecutable, *, capability: bool = True
) -> tuple[Path, Path, Path]:
    root = tmp_path / "consumer"
    root.mkdir()
    state_file = root / "state.tsv"
    calls_file = root / "calls.log"
    state_file.write_text(
        'interop\taws_identitystore_group.groups["existing"]\tstore-1/group-existing\n',
        encoding="utf-8",
    )
    write_executable(
        root / "terraform.sh",
        f"#!/usr/bin/env bash\nset -eu\nprintf '%s\\n' \"$*\" >> {calls_file!s}\n",
    )
    runner_adapter = tmp_path / "runner-adapter.sh"
    write_executable(
        runner_adapter,
        "runner_preflight() {\n"
        + (
            '  [[ "${CAPABILITY_PROOF:-}" == yes ]]\n'
            if capability
            else "  return 21\n"
        )
        + "}\n"
        "runner_state_identity() {\n"
        "  local wanted_scope=$1 wanted_address=$2 line scope address canonical\n"
        "  while IFS=$'\\t' read -r scope address canonical; do\n"
        '    if [[ "$scope" == "$wanted_scope" && "$address" == "$wanted_address" ]]; then\n'
        "      printf '%s\\n' \"$canonical\"\n"
        "      return 0\n"
        "    fi\n"
        '  done < "$STATE_FILE"\n'
        "  return 3\n"
        "}\n"
        "runner_import() {\n"
        "  local scope=$1 address=$2 import_id=$3\n"
        '  "$TERRAFORM_RUNNER" import "$scope" "$address" "$import_id"\n'
        '  printf \'%s\\t%s\\t%s\\n\' "$scope" "$address" "$import_id" >> "$STATE_FILE"\n'
        "}\n"
        "runner_plan() { return 0; }\n"
        "runner_plan_has_create() { return 1; }\n"
        "runner_plan_json() {\n"
        '  if [[ -f "$1/applied" ]]; then printf \'%s\\n\' \'{"actions":[{"address":"aws_identitystore_group.groups[\\"missing\\"]","action":"no-op"}]}\'\n'
        '  else printf \'%s\\n\' \'{"actions":[{"address":"aws_identitystore_group.groups[\\"missing\\"]","action":"import"}]}\'\n'
        "  fi\n"
        "}\n"
        "runner_plan_saved() {\n"
        "  printf '%s' 'saved-plan' > \"$4\"\n"
        '  actions="$(jq -cs \'map(if .disposition == "moved_candidate" then {address:.move.to,action:"moved",from:.move.from,to:.move.to} else {address,action:"import"} end)\' "$3")"\n'
        '  printf \'{"actions":%s}\\n\' "$actions"\n'
        "}\n"
        "runner_apply_saved() {\n"
        "  local item scope address import_id\n"
        "  while IFS= read -r item; do\n"
        '    [[ "$(jq -r \'.disposition\' <<< "$item")" == import_candidate ]] || continue\n'
        '    scope="$(jq -r \'.scope\' <<< "$item")"\n'
        '    address="$(jq -r \'.address\' <<< "$item")"\n'
        '    import_id="$(jq -r \'.lookup.import_id\' <<< "$item")"\n'
        '    "$TERRAFORM_RUNNER" import "$scope" "$address" "$import_id"\n'
        '    printf \'%s\\t%s\\t%s\\n\' "$scope" "$address" "$import_id" >> "$STATE_FILE"\n'
        '  done < "$3"\n'
        '  touch "$1/applied"\n'
        "}\n",
    )
    resource_adapter = tmp_path / "resource-adapter.sh"
    write_executable(
        resource_adapter,
        "resolve_import_record() {\n"
        '  if [[ "$(jq -r \'.lookup.status // empty\' <<< "$1")" == failed ]]; then\n'
        "    printf '%s\\n' '{\"status\":\"aws_error\"}'\n"
        "    return 0\n"
        "  fi\n"
        "  jq -c '{canonical_id: .lookup.canonical_id, import_id: .lookup.import_id}' <<< \"$1\"\n"
        "}\n",
    )
    return root, runner_adapter, resource_adapter


def _invoke_runner(
    manifest: Path,
    *,
    handoff_payload: Callable[..., dict[str, object]],
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
        data = {"mode": mode, **(handoff_data or {})}
        if data.get("decision") == "execute":
            data.setdefault("state_move", True)
        handoff.write_text(
            json.dumps(handoff_payload(root, **data)) + "\n", encoding="utf-8"
        )
        args.extend(["--handoff", str(handoff)])
    args.extend(extra)
    return subprocess.run(
        args, cwd=BUNDLE_ROOT, env=env, text=True, capture_output=True
    )


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


def test_runner_skips_managed_and_resumes_without_duplicate_import(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    first = run_runner(
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

    resumed = run_runner(
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


def test_runner_assessment_rejects_duplicate_manifest_addresses(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    duplicate_manifest = tmp_path / "duplicate.jsonl"
    record = json.loads(FIXTURE.read_text(encoding="utf-8").splitlines()[0])
    write_manifest(duplicate_manifest, [record, record])

    result = run_runner(
        duplicate_manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "duplicate manifest address" in result.stderr
    assert not (root / "calls.log").exists()


def test_missing_handoff_stops_before_adapter_loading(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        include_handoff=False,
    )

    assert result.returncode != 0
    assert "--handoff is required" in result.stderr
    assert not (root / "calls.log").exists()


def test_assessment_rejects_live_execution(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--live",),
    )

    assert result.returncode != 0
    assert not (root / "calls.log").exists()


@pytest.mark.parametrize("extra", [(), ("--live",)], ids=["assess", "live"])
def test_protocol_v1_execute_handoff_is_rejected_before_assessment(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    extra: tuple[str, ...],
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute", "schema_version": 1},
        extra=extra,
    )

    assert result.returncode != 0
    assert "assessment" in result.stderr
    assert not (root / "calls.log").exists()


def test_live_script_mode_blocks_update_from_machine_readable_plan(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_json() {\n"
        + '  printf \'%s\\n\' \'{"resource_changes":[{"address":"aws_resource.example","change":{"actions":["update"]}}]}\'\n'
        + "}\n",
        encoding="utf-8",
    )
    result = run_runner(
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


def test_live_script_mode_applies_exact_saved_plan_and_writes_receipt(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_json() {\n"
        + '  if [[ -f "$1/applied" ]]; then printf \'%s\\n\' \'{"actions":[{"address":"aws_identitystore_group.groups[\\"missing\\"]","action":"no-op"}]}\'; else printf \'%s\\n\' \'{"actions":[{"address":"aws_identitystore_group.groups[\\"missing\\"]","action":"import"}]}\'; fi\n'
        + "}\n"
        + "runner_plan_saved() {\n"
        + "  printf '%s' 'script-saved-plan' > \"$4\"\n"
        + '  printf \'%s\\n\' \'{"actions":[{"address":"aws_identitystore_group.groups[\\"missing\\"]","action":"import"}]}\'\n'
        + "}\n"
        + "runner_apply_saved() {\n"
        + '  if [[ ! -f "$1/.terraform-import-adoption/run-1.authorization.json" ]]; then return 42; fi\n'
        + f"  printf 'apply-saved %s\\n' \"$4\" >> {root / 'calls.log'!s}\n"
        + "  printf '%s\\t%s\\t%s\\n' 'interop' 'aws_identitystore_group.groups[\"missing\"]' 'store-1/group-missing' >> \"$STATE_FILE\"\n"
        + '  touch "$1/applied"\n'
        + "}\n",
        encoding="utf-8",
    )
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"decision": "execute", "state_move": False},
        extra=("--live",),
    )

    assert result.returncode == 0
    assert any(
        line.startswith("apply-saved ")
        for line in (root / "calls.log").read_text(encoding="utf-8").splitlines()
    )
    records_dir = root / ".terraform-import-adoption"
    assert (records_dir / "run-1.authorization.json").is_file()
    assert (records_dir / "run-1.evidence.json").is_file()
    assert (records_dir / "run-1.receipt.json").is_file()
    evidence = json.loads(
        (records_dir / "run-1.evidence.json").read_text(encoding="utf-8")
    )
    assert set(evidence["inventory_digests"]) == {"desired", "live", "state"}
    assert evidence["state_boundary"]["serial"] == 1
    assert evidence["tool_versions"] == {"terraform": "1.9.0"}
    reconciliation = {item["address"]: item for item in evidence["reconciliation"]}
    assert (
        reconciliation['aws_identitystore_group.groups["existing"]']["observed_status"]
        == "already_managed"
    )
    assert (
        reconciliation['aws_identitystore_group.groups["missing"]'][
            "observed_identity"
        ]["canonical_id"]
        == "store-1/group-missing"
    )


def test_live_script_reconfirms_identity_before_exact_apply(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    counter = tmp_path / "resolver-count"
    resource_adapter.write_text(
        "#!/usr/bin/env bash\n"
        "resolve_import_record() {\n"
        f'  count=0; if [[ -f {counter!s} ]]; then count="$(cat {counter!s})"; fi; count=$((count + 1)); printf \'%s\' "$count" > {counter!s}\n'
        '  if [[ "$count" -gt 2 ]]; then printf \'%s\\n\' \'{"canonical_id":"store-1/changed","import_id":"store-1/changed"}\'; else jq -c \'{canonical_id: .lookup.canonical_id, import_id: .lookup.import_id}\' <<< "$1"; fi\n'
        "}\n",
        encoding="utf-8",
    )
    result = run_runner(
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


def test_live_script_mode_uses_adapter_resolved_import_id(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    resource_adapter.write_text(
        resource_adapter.read_text(encoding="utf-8")
        + 'resolve_import_record() { printf \'%s\\n\' \'{"canonical_id":"resolved/group","import_id":"resolved/group"}\'; }\n',
        encoding="utf-8",
    )
    manifest = tmp_path / "resolved-id.jsonl"
    write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": 'aws_identitystore_group.groups["missing"]',
                "resource_kind": "identitystore_group",
                "lookup": {},
                "disposition": "import_candidate",
            }
        ],
    )

    result = run_runner(
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


def test_live_script_mode_rejects_move_with_wrong_source_identity(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\tresource.old\tstore-1/not-moved\n", encoding="utf-8"
    )
    applied_marker = root / "move-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_move() { return 0; }\n"
        + 'runner_plan_saved() { printf \'%s\' \'moved-plan\' > "$4"; printf \'%s\\n\' \'{"actions":[{"address":"resource.new","action":"moved","from":"resource.old","to":"resource.new"}]}\'; }\n'
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "wrong-source.jsonl"
    write_manifest(manifest, [_moved_record()])

    result = run_runner(
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


def test_live_script_mode_rejects_move_destination_collision(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\tresource.old\tstore-1/group-moved\n"
        "interop\tresource.new\tstore-1/other\n",
        encoding="utf-8",
    )
    applied_marker = root / "move-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_move() { return 0; }\n"
        + 'runner_plan_saved() { printf \'%s\' \'moved-plan\' > "$4"; printf \'%s\\n\' \'{"actions":[{"address":"resource.new","action":"moved","from":"resource.old","to":"resource.new"}]}\'; }\n'
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "collision.jsonl"
    write_manifest(manifest, [_moved_record()])

    result = run_runner(
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


def test_live_script_mode_rejects_extra_saved_plan_operations(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    applied_marker = root / "extra-applied"
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + "runner_plan_saved() {\n"
        + "  printf '%s' 'saved-plan' > \"$4\"\n"
        + '  printf \'%s\\n\' \'{"actions":[{"address":"aws_identitystore_group.groups[\\"missing\\"]","action":"import"},{"address":"aws.extra","action":"import"}]}\'\n'
        + "}\n"
        + f"runner_apply_saved() {{ touch {applied_marker!s}; }}\n",
        encoding="utf-8",
    )

    result = run_runner(
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


def test_live_script_mode_excludes_absent_create_from_adoption(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    manifest = tmp_path / "absent-create.jsonl"
    write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": 'aws_identitystore_group.groups["future"]',
                "resource_kind": "identitystore_group",
                "lookup": {
                    "canonical_id": "store-1/group-future",
                    "import_id": "store-1/group-future",
                },
                "disposition": "absent_create",
            }
        ],
    )
    result = run_runner(
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


def test_live_script_mode_applies_only_proven_state_moves(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\tresource.old\tstore-1/group-moved\n", encoding="utf-8"
    )
    runner_adapter.write_text(
        runner_adapter.read_text(encoding="utf-8")
        + 'runner_plan_json() { printf \'%s\\n\' \'{"actions":[{"address":"resource.new","action":"moved","from":"resource.old","to":"resource.new"}]}\'; }\n'
        + "runner_move() { printf '%s\\n' 'interop\tresource.new\tstore-1/group-moved' > \"$STATE_FILE\"; }\n"
        + 'runner_plan_saved() { printf \'%s\' \'moved-plan\' > "$4"; printf \'%s\\n\' \'{"actions":[{"address":"resource.new","action":"moved","from":"resource.old","to":"resource.new"}]}\'; }\n'
        + "runner_apply_saved() { runner_move; }\n",
    )
    manifest = tmp_path / "moved.jsonl"
    write_manifest(
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

    result = run_runner(
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


def test_live_execution_requires_complete_protocol_v2_evidence(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
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


def test_incomplete_wrapper_projection_stops_before_adapter_calls(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)

    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={"execution_owner": None},
    )

    assert result.returncode != 0
    assert "execution_owner" in result.stderr
    assert not (root / "calls.log").exists()


def test_live_runner_override_must_match_handoff_path(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_executable: WriteExecutable,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    alternate_runner = root / "alternate-terraform.sh"
    write_executable(alternate_runner, "#!/usr/bin/env bash\nexit 0\n")

    result = run_runner(
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


def test_assessment_runner_override_requires_handoff_path(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_executable: WriteExecutable,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    alternate_runner = root / "alternate-terraform.sh"
    write_executable(alternate_runner, "#!/usr/bin/env bash\nexit 0\n")

    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--runner", str(alternate_runner)),
    )

    assert result.returncode != 0
    assert "runner path" in result.stderr
    assert not (root / "calls.log").exists()


def test_default_script_mode_never_calls_runner_import(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode == 0
    assert "Dry-run candidate" in result.stdout
    assert not (root / "calls.log").exists()


@pytest.mark.parametrize(
    ("missing_field", "expected_error"),
    [
        ("identity_status", "requires verified identity"),
        ("reconciliation_status", "requires complete reconciliation"),
        ("ownership_disposition", "requires an adoptable ownership disposition"),
        ("mutation_authority", "mutation_authority"),
        ("convergence_decision", "convergence_decision"),
        ("runner_status", "requires verified runner status"),
        ("recovery_status", "requires recovery readiness"),
    ],
)
def test_live_script_mode_requires_complete_execute_evidence(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    missing_field: str,
    expected_error: str,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data={
            "decision": "execute",
            missing_field: "pending" if missing_field.endswith("status") else "unknown",
        },
        extra=("--live",),
    )

    assert result.returncode != 0
    assert expected_error in result.stderr
    assert not (root / "calls.log").exists()


@pytest.mark.parametrize(
    ("handoff_data", "expected"),
    [
        ({"consumer_root": "/different/root"}, "root"),
        ({"mode": "hcl"}, "mode"),
        ({"scope": "other"}, "scope"),
    ],
)
def test_handoff_root_mode_and_scopes_must_match_the_run(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    handoff_data: dict[str, object],
    expected: str,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        handoff_data=handoff_data,
    )

    assert result.returncode != 0
    assert expected in result.stderr
    assert not (root / "calls.log").exists()


def test_dry_run_and_live_are_mutually_exclusive(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    result = run_runner(
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


def test_runner_rejects_malformed_jsonl(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    manifest = tmp_path / "malformed.jsonl"
    manifest.write_text('{"scope":"interop"}\nnot-json\n', encoding="utf-8")
    result = run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )
    assert result.returncode != 0
    assert "malformed JSONL" in result.stderr


def test_runner_rejects_renderer_escape_artifacts(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    manifest = tmp_path / "escaped.jsonl"
    manifest.write_text(
        '{"scope":"interop","address":"aws.foo[\\u003cname\\u003e]",'
        '"resource_kind":"identitystore_group","lookup":{"canonical_id":"id","import_id":"id"}}\n',
        encoding="utf-8",
    )
    result = run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )
    assert result.returncode != 0
    assert "escape artifact" in result.stderr


def test_runner_requires_executable_default_wrapper(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    (root / "terraform.sh").chmod(stat.S_IRUSR | stat.S_IWUSR)
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )
    assert result.returncode != 0
    assert "executable terraform.sh" in result.stderr


def test_runner_requires_adapter_capability_proof(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_executable: WriteExecutable,
) -> None:
    root, _, resource_adapter = make_consumer(tmp_path, capability=False)
    runner_adapter = tmp_path / "incomplete-adapter.sh"
    write_executable(runner_adapter, "runner_preflight() { return 21; }\n")
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )
    assert result.returncode != 0
    assert "capability" in result.stderr


def test_runner_fails_closed_on_state_identity_mismatch(
    tmp_path: Path, make_consumer: MakeConsumer, run_runner: RunRunner
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        'interop\taws_identitystore_group.groups["existing"]\tstore-1/wrong\n',
        encoding="utf-8",
    )
    result = run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )
    assert result.returncode != 0
    assert "ambiguous" in result.stdout
    assert "store-1/wrong" in result.stderr


def test_runner_continue_on_error_reports_nonzero_after_processing_remaining_records(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    manifest = tmp_path / "continue.jsonl"
    write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": 'aws_identitystore_group.groups["broken"]',
                "resource_kind": "identitystore_group",
                "lookup": {
                    "status": "failed",
                    "canonical_id": "store-1/group-broken",
                    "import_id": "store-1/group-broken",
                },
                "disposition": "import_candidate",
            },
            {
                "scope": "interop",
                "address": 'aws_identitystore_group.groups["new"]',
                "resource_kind": "identitystore_group",
                "lookup": {
                    "canonical_id": "store-1/group-new",
                    "import_id": "store-1/group-new",
                },
                "disposition": "import_candidate",
            },
        ],
    )
    result = run_runner(
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


def test_script_mode_rejects_record_selected_for_hcl(
    tmp_path: Path,
    make_consumer: MakeConsumer,
    run_runner: RunRunner,
    write_manifest: WriteManifest,
) -> None:
    root, runner_adapter, resource_adapter = make_consumer(tmp_path)
    manifest = write_manifest(
        tmp_path / "imports.jsonl",
        [
            {
                "scope": "interop",
                "address": "aws.foo",
                "resource_kind": "identitystore_group",
                "lookup": {"canonical_id": "id", "import_id": "id"},
                "disposition": "import_candidate",
                "mode": "hcl",
            }
        ],
    )

    result = run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "record mode conflicts with script mode" in result.stderr
