from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.validate_code import validate_code

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_code_catalog_declares_static_leaves_and_python_shards() -> None:
    assert tuple(validate_code.STATIC_CHECKS) == (
        "actionlint",
        "shell-static-analysis",
        "python-dependencies",
        "python-static-analysis",
        "python-lint",
        "python-entrypoints",
    )
    assert tuple(validate_code.PYTHON_SHARDS) == (
        "repository",
        "skills-internal",
        "skills-terraform-import",
        "skills-local",
    )
    assert all(shard.paths for shard in validate_code.PYTHON_SHARDS.values())


def test_shard_paths_expand_globs_and_honor_exclusions(tmp_path: Path) -> None:
    for name in ("internal-a", "internal-terraform-import", "local-b"):
        (tmp_path / ".github/skills" / name).mkdir(parents=True)
    shard = validate_code.PythonShard(
        "sample",
        (".github/skills/internal-*",),
        excludes=(".github/skills/internal-terraform-import",),
    )

    assert validate_code._pytest_paths(tmp_path, shard) == (
        tmp_path / ".github/skills/internal-a",
    )


@pytest.mark.parametrize(
    ("cpu_count", "concurrent_shards", "expected"),
    [(14, 4, 3), (4, 1, 4), (2, 4, 1), (1, 1, 1)],
)
def test_pytest_workers_split_cpus_across_concurrent_shards(
    cpu_count: int, concurrent_shards: int, expected: int
) -> None:
    assert validate_code.pytest_workers(cpu_count, concurrent_shards) == expected


@pytest.mark.parametrize(("workers", "xdist_args"), [(3, ["-n", "3"]), (1, [])])
def test_python_shard_enables_xdist_only_for_multiple_workers(
    monkeypatch, tmp_path: Path, workers: int, xdist_args: list[str]
) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr(
        validate_code,
        "run_command",
        lambda _context, args: commands.append([str(arg) for arg in args]) or 0,
    )
    context = validate_code.RunContext(REPO_ROOT, tmp_path, True, True)

    assert (
        validate_code.run_python_shard(
            context, validate_code.PYTHON_SHARDS["repository"], workers
        )
        == 0
    )

    assert commands[0][3 : 4 + len(xdist_args)] == ["-q", *xdist_args]


def test_shard_integrity_rejects_unmapped_and_overlapping_nodes(
    monkeypatch, tmp_path: Path
) -> None:
    shards = {
        "first": validate_code.PythonShard("first", ("a",)),
        "second": validate_code.PythonShard("second", ("b",)),
    }
    for name in ("a", "b"):
        (tmp_path / name).mkdir()
    monkeypatch.setattr(validate_code, "PYTHON_SHARDS", shards)

    def collect(nodes_by_path):
        def _collect(_root, paths=None):
            key = "all" if paths is None else paths[0].name
            return nodes_by_path[key]

        return _collect

    monkeypatch.setattr(
        validate_code,
        "discover_pytest_node_ids",
        collect({"all": ("a::x", "b::y", "c::z"), "a": ("a::x",), "b": ("b::y",)}),
    )
    with pytest.raises(ValueError, match="Unmapped Python nodes: c::z"):
        validate_code.validate_python_shards(tmp_path)

    monkeypatch.setattr(
        validate_code,
        "discover_pytest_node_ids",
        collect({"all": ("a::x",), "a": ("a::x",), "b": ("a::x",)}),
    )
    with pytest.raises(ValueError, match="belongs to first and second"):
        validate_code.validate_python_shards(tmp_path)


def _capture_commands(monkeypatch) -> list[list[str]]:
    commands: list[list[str]] = []
    monkeypatch.setattr(
        validate_code,
        "run_command",
        lambda _context, args: commands.append([str(arg) for arg in args]) or 0,
    )
    return commands


def test_shell_leaf_never_skips_shellcheck_silently(
    monkeypatch, tmp_path: Path
) -> None:
    commands = _capture_commands(monkeypatch)
    monkeypatch.setattr(validate_code.shutil, "which", lambda _name: None)
    context = validate_code.RunContext(REPO_ROOT, tmp_path, False, True)

    validate_code._shell(context)

    assert any(command[0] == "shellcheck" for command in commands)


def test_entrypoint_smoke_does_not_bootstrap_the_tools_runner_venv(
    monkeypatch, tmp_path: Path
) -> None:
    commands = _capture_commands(monkeypatch)
    context = validate_code.RunContext(REPO_ROOT, tmp_path, False, True)

    assert validate_code._python_entrypoints(context) == 0

    assert commands
    assert not any(".github/tools/run.sh" in " ".join(c) for c in commands)


def test_unpublished_result_fails_the_run(monkeypatch, tmp_path: Path) -> None:
    def fail(_report, _path):
        raise OSError("disk full")

    monkeypatch.setattr(validate_code, "write_run_result", fail)

    assert (
        validate_code.main(
            [
                "python",
                "--group",
                "repository",
                "--dry-run",
                "--result-path",
                str(tmp_path / "result.json"),
                "--tmp-dir",
                str(tmp_path / "run"),
            ]
        )
        == 1
    )


def test_code_cli_rejects_terraform_stream(capsys) -> None:
    assert validate_code.main(["terraform", "--dry-run"]) == 2
    assert "invalid choice" in capsys.readouterr().err


def test_code_cli_dry_run_selects_one_group_without_running_children(
    tmp_path: Path, capsys
) -> None:
    assert (
        validate_code.main(
            [
                "python",
                "--group",
                "repository",
                "--dry-run",
                "--tmp-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "repository" in output
    assert "skills-local" not in output
    assert "simulated" in output.lower() or "dry-run" in output.lower()


def test_code_cli_rejects_unknown_group(tmp_path: Path, capsys) -> None:
    assert (
        validate_code.main(
            ["python", "--group", "unknown", "--dry-run", "--tmp-dir", str(tmp_path)]
        )
        == 2
    )
    assert "skills-internal" in capsys.readouterr().err


def test_code_cli_rejects_selector_for_wrong_stream(tmp_path: Path, capsys) -> None:
    assert (
        validate_code.main(
            ["static", "--group", "repository", "--tmp-dir", str(tmp_path)]
        )
        == 2
    )
    assert "--group is only valid for python" in capsys.readouterr().err


def test_code_cli_writes_explicit_ci_result_and_artifact_contract(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "result.json"
    artifact_dir = tmp_path / "artifacts"

    assert (
        validate_code.main(
            [
                "python",
                "--group",
                "repository",
                "--dry-run",
                "--format",
                "ci",
                "--result-path",
                str(result_path),
                "--artifact-dir",
                str(artifact_dir),
                "--tmp-dir",
                str(tmp_path / "run"),
            ]
        )
        == 0
    )

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "validation-run/v1"
    assert payload["planned_units"] == ["python:repository"]
    assert payload["artifacts"]


def test_static_leaf_dry_run_plans_only_that_leaf(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"

    assert (
        validate_code.main(
            [
                "static",
                "--leaf",
                "python-lint",
                "--dry-run",
                "--format",
                "json",
                "--result-path",
                str(result_path),
                "--tmp-dir",
                str(tmp_path / "run"),
            ]
        )
        == 0
    )

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["planned_units"] == ["static:python-lint"]


def test_explicit_python_group_does_not_repeat_global_shard_integrity_collection(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        validate_code,
        "validate_python_shards",
        lambda _root: calls.append("integrity") or {},
    )
    monkeypatch.setattr(validate_code, "run_python_shard", lambda *_args: 0)

    assert (
        validate_code.main(
            ["python", "--group", "repository", "--tmp-dir", str(tmp_path)]
        )
        == 0
    )

    assert calls == []


def test_integrity_only_runs_canonical_shard_collection_once(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        validate_code,
        "validate_python_shards",
        lambda _root: calls.append("integrity") or {},
    )

    assert (
        validate_code.main(["python", "--integrity-only", "--tmp-dir", str(tmp_path)])
        == 0
    )

    assert calls == ["integrity"]


def test_integrity_only_requires_python_stream_without_selectors(capsys) -> None:
    assert validate_code.main(["static", "--integrity-only"]) == 2
    assert (
        validate_code.main(["python", "--integrity-only", "--group", "repository"]) == 2
    )
    err = capsys.readouterr().err
    assert "requires the python stream" in err
    assert "cannot be combined" in err


def test_code_cli_emits_preflight_before_shard_collection(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    observations: list[str] = []

    def collect(_root):
        observations.append(capsys.readouterr().err)
        return {}

    monkeypatch.setattr(validate_code, "validate_python_shards", collect)

    assert (
        validate_code.main(["python", "--integrity-only", "--tmp-dir", str(tmp_path)])
        == 0
    )

    assert observations and "preflight" in observations[0]


def test_code_cli_compact_mode_keeps_one_scoped_unit_and_terminal_projection(
    tmp_path: Path, capsys
) -> None:
    assert (
        validate_code.main(
            [
                "python",
                "--group",
                "repository",
                "--compact",
                "--format",
                "terminal",
                "--dry-run",
                "--tmp-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "[01/01]" in output
    assert "repository" in output


def test_compact_terminal_mode_skips_live_progress_stream(
    tmp_path: Path, capsys
) -> None:
    assert (
        validate_code.main(
            ["static", "--compact", "--dry-run", "--tmp-dir", str(tmp_path)]
        )
        == 0
    )

    assert capsys.readouterr().err == ""


def test_code_cli_compact_does_not_change_json_contract(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    assert (
        validate_code.main(
            [
                "python",
                "--group",
                "repository",
                "--compact",
                "--format",
                "json",
                "--dry-run",
                "--result-path",
                str(result_path),
                "--tmp-dir",
                str(tmp_path / "run"),
            ]
        )
        == 0
    )
    assert json.loads(result_path.read_text(encoding="utf-8"))["planned_units"] == [
        "python:repository"
    ]


def test_failing_unit_returns_nonzero(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(validate_code, "run_python_shard", lambda *_args: 1)

    assert (
        validate_code.main(
            ["python", "--group", "repository", "--tmp-dir", str(tmp_path)]
        )
        == 1
    )


def test_wrapper_lists_catalog_from_any_working_directory(tmp_path: Path) -> None:
    completed = subprocess.run(
        ["bash", str(REPO_ROOT / "validate-code.sh"), "--list"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "STATIC" in completed.stdout
    assert "skills-terraform-import" in completed.stdout


def test_wrapper_resolves_relative_python_bin_from_caller_directory(
    tmp_path: Path,
) -> None:
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin/py").symlink_to(sys.executable)
    completed = subprocess.run(
        ["bash", str(REPO_ROOT / "validate-code.sh"), "--list"],
        cwd=tmp_path,
        env={**os.environ, "PYTHON_BIN": "bin/py"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_wrapper_records_only_the_operator_request(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    completed = subprocess.run(
        [
            "bash",
            str(REPO_ROOT / "validate-code.sh"),
            "static",
            "--leaf",
            "python-lint",
            "--dry-run",
            "--format",
            "json",
            "--result-path",
            str(result_path),
            "--tmp-dir",
            str(tmp_path / "run"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    request = json.loads(result_path.read_text(encoding="utf-8"))["request"]
    assert request.startswith("static --leaf python-lint")
    assert "--root" not in request
