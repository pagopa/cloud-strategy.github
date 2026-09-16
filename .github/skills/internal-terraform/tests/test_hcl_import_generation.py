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


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


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
    extra: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
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

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode == 0
    generated = (root / "imports.generated.tf").read_text(encoding="utf-8")
    assert '"store-1/group-new"' in generated
    assert "aws_identitystore_group.groups[each.key]" in generated
    assert "aws.identity_center" in generated
    assert 'groups["new"]' not in generated
    assert "store-1/group-other" not in generated
    assert not calls_file.exists()


def test_hcl_excludes_state_confirmed_addresses(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(
        tmp_path, state_identity="store-1/group-existing"
    )
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [
            _group_record('aws_identitystore_group.groups["existing"]', "existing", "store-1/group-existing"),
            _group_record('aws_identitystore_group.groups["new"]', "new", "store-1/group-new"),
        ],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode == 0
    generated = (root / "imports.generated.tf").read_text(encoding="utf-8")
    assert "group-existing" not in generated
    assert "group-new" in generated


def test_hcl_requires_one_selected_scope(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(tmp_path / "imports.jsonl", [_group_record("aws.foo", "new", "id")])

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        scope=None,
    )

    assert result.returncode != 0
    assert "exactly one scope" in result.stderr


def test_hcl_retains_generated_file_after_plan_failure(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path, plan_fails=True)
    manifest = _manifest(tmp_path / "imports.jsonl", [_group_record("aws.foo", "new", "id")])

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--live",),
    )

    assert result.returncode != 0
    assert (root / "imports.generated.tf").is_file()


def test_hcl_removes_file_only_after_live_verification_and_post_plan(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [_group_record('aws_identitystore_group.groups["new"]', "new", "store-1/group-new")],
    )

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
        extra=("--live",),
    )

    assert result.returncode == 0
    assert not (root / "imports.generated.tf").exists()


def test_script_mode_rejects_record_selected_for_hcl(tmp_path: Path) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    manifest = _manifest(
        tmp_path / "imports.jsonl",
        [{**_group_record("aws.foo", "new", "id"), "mode": "hcl"}],
    )

    result = subprocess.run(
        [
            str(RUNNER),
            "--manifest",
            str(manifest),
            "--mode=script",
            "--root",
            str(root),
            "--runner-adapter",
            str(runner_adapter),
            "--resource-adapter",
            str(resource_adapter),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "mode" in result.stderr


@pytest.mark.parametrize("bad_field", ["to", "provider"])
def test_hcl_requires_adapter_owned_destination_metadata(tmp_path: Path, bad_field: str) -> None:
    root, runner_adapter, resource_adapter, _ = _make_hcl_consumer(tmp_path)
    record = _group_record("aws.foo", "new", "id")
    record["lookup"][bad_field] = ""
    manifest = _manifest(tmp_path / "imports.jsonl", [record])

    result = _run_hcl(
        manifest,
        root=root,
        runner_adapter=runner_adapter,
        resource_adapter=resource_adapter,
    )

    assert result.returncode != 0
    assert "metadata" in result.stderr
