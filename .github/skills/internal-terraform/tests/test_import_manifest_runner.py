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
RUNNER = REPO_ROOT / ".github/skills/internal-terraform/scripts/import-manifest-runner.sh"
FIXTURE = (
    REPO_ROOT / ".github/skills/internal-terraform/tests/fixtures/imports.valid.jsonl"
)


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


def _run_runner(
    manifest: Path,
    *,
    root: Path,
    runner_adapter: Path,
    resource_adapter: Path,
    mode: str = "script",
    extra: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "CAPABILITY_PROOF": "yes",
            "STATE_FILE": str(root / "state.tsv"),
        }
    )
    return subprocess.run(
        [
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
            *extra,
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def _write_manifest(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def test_runner_skips_managed_and_resumes_without_duplicate_import(
    tmp_path: Path,
) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    first = _run_runner(
        FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )

    assert first.returncode == 0
    assert "Skipped already managed: 1" in first.stdout
    assert '"status":"skipped_already_managed"' in first.stdout
    assert '"status":"imported"' in first.stdout
    assert (root / "calls.log").read_text(encoding="utf-8").splitlines() == [
        'import interop aws_identitystore_group.groups["missing"] store-1/group-missing'
    ]

    resumed = _run_runner(
        FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )
    assert resumed.returncode == 0
    assert "Skipped already managed: 2" in resumed.stdout
    assert (root / "calls.log").read_text(encoding="utf-8").splitlines() == [
        'import interop aws_identitystore_group.groups["missing"] store-1/group-missing'
    ]


def test_runner_rejects_malformed_jsonl(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "malformed.jsonl"
    manifest.write_text('{"scope":"interop"}\nnot-json\n', encoding="utf-8")

    result = _run_runner(
        manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )

    assert result.returncode != 0
    assert "malformed JSONL" in result.stderr


def test_runner_rejects_renderer_escape_artifacts(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "escaped.jsonl"
    manifest.write_text(
        '{"scope":"interop","address":"aws.foo[\\\\u003cname\\\\u003e]",'
        '"resource_kind":"identitystore_group","lookup":{"canonical_id":"id","import_id":"id"}}\n',
        encoding="utf-8",
    )

    result = _run_runner(
        manifest, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )

    assert result.returncode != 0
    assert "escape artifact" in result.stderr


def test_runner_requires_executable_default_wrapper(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "terraform.sh").chmod(stat.S_IRUSR | stat.S_IWUSR)

    result = _run_runner(
        FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )

    assert result.returncode != 0
    assert "executable terraform.sh" in result.stderr


def test_runner_requires_adapter_capability_proof(tmp_path: Path) -> None:
    root, _, resource_adapter = _make_consumer(tmp_path, capability=False)
    runner_adapter = tmp_path / "incomplete-adapter.sh"
    _write_executable(runner_adapter, "runner_preflight() { return 21; }\n")

    result = _run_runner(
        FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )

    assert result.returncode != 0
    assert "capability" in result.stderr


def test_runner_fails_closed_on_state_identity_mismatch(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    (root / "state.tsv").write_text(
        "interop\taws_identitystore_group.groups[\"existing\"]\tstore-1/wrong\n",
        encoding="utf-8",
    )

    result = _run_runner(
        FIXTURE, root=root, runner_adapter=runner_adapter, resource_adapter=resource_adapter
    )

    assert result.returncode != 0
    assert "ambiguous" in result.stdout
    assert "store-1/wrong" in result.stderr


def test_runner_dry_run_does_not_import(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)

    result = _run_runner(
        FIXTURE,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--dry-run",),
    )

    assert result.returncode == 0
    assert "Dry-run candidate" in result.stdout
    assert not (root / "calls.log").exists()


def test_runner_continue_on_error_reports_nonzero_after_processing_remaining_records(
    tmp_path: Path,
) -> None:
    root, runner_adapter, resource_adapter = _make_consumer(tmp_path)
    manifest = tmp_path / "continue.jsonl"
    _write_manifest(
        manifest,
        [
            {
                "scope": "interop",
                "address": "aws_identitystore_group.groups[\"broken\"]",
                "resource_kind": "identitystore_group",
                "lookup": {"status": "failed"},
            },
            {
                "scope": "interop",
                "address": "aws_identitystore_group.groups[\"new\"]",
                "resource_kind": "identitystore_group",
                "lookup": {"canonical_id": "store-1/group-new", "import_id": "store-1/group-new"},
            },
        ],
    )

    result = _run_runner(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--continue-on-error",),
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
    )

    assert result.returncode != 0
    assert "scope" in result.stderr
