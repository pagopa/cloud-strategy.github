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
FIXTURE = REPO_ROOT / ".github/skills/internal-terraform-import/tests/fixtures/imports.valid.jsonl"


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
        "runner_plan_has_create() { return 1; }\n",
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
    payload: dict[str, object] = {
        "schema_version": 1,
        "kind": "internal-terraform-import-handoff",
        "decision": decision,
        "consumer_root": str(root.resolve()),
        "mode": mode,
        "scopes": scopes or ["interop"],
        "identity_status": "pending",
        "reconciliation_status": "pending",
        "ownership_disposition": "unknown",
        "mutation_authority": "not-approved",
        "convergence_decision": "adoption-only",
        "runner_status": "verified",
        "recovery_status": "pending",
        "approval_reference": "review-record-id",
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
        identity_status="verified",
        reconciliation_status="complete",
        ownership_disposition="unmanaged",
        mutation_authority="approved",
        convergence_decision="adoption-only",
        runner_status="verified",
        recovery_status="ready",
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
        handoff = manifest.parent / "handoff.json"
        if handoff_data and handoff_data.get("decision") == "execute":
            _execute_handoff(handoff, root=root, mode=mode)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload.update(handoff_data)
            handoff.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        else:
            payload = {"mode": mode}
            payload.update(handoff_data or {})
            _write_handoff(handoff, root=root, **payload)
        args.extend(["--handoff", str(handoff)])
    args.extend(extra)
    return subprocess.run(args, cwd=REPO_ROOT, env=env, text=True, capture_output=True)


def _write_manifest(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


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
        cwd=REPO_ROOT,
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
            {"scope": "interop", "address": "aws_identitystore_group.groups[\"broken\"]", "resource_kind": "identitystore_group", "lookup": {"status": "failed"}},
            {"scope": "interop", "address": "aws_identitystore_group.groups[\"new\"]", "resource_kind": "identitystore_group", "lookup": {"canonical_id": "store-1/group-new", "import_id": "store-1/group-new"}},
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
