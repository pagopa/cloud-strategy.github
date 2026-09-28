from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Mapping

import pytest

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = BUNDLE_ROOT / "references" / "run-protocol.md"
OBJECT_BLOCKS = (
    "cmd:object-probe",
    "cmd:checkpoint",
    "cmd:head-tree",
    "cmd:checkpoint-type",
    "cmd:changed-paths",
    "cmd:task-diff",
)


def extract_block(text: str, marker: str) -> str:
    match = re.search(
        rf"(?m)^<!-- {re.escape(marker)} -->\n```sh\n(.*?)\n```$",
        text,
        re.DOTALL,
    )
    assert match is not None, f"missing shell block marker: {marker}"
    return match.group(1)


def protocol_block(marker: str) -> str:
    assert PROTOCOL_PATH.is_file(), "run-protocol.md does not exist"
    return extract_block(PROTOCOL_PATH.read_text(encoding="utf-8"), marker)


def run_block(
    marker: str,
    cwd: Path,
    env: Mapping[str, str],
    suffix: str = "",
    paths: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", "-c", protocol_block(marker) + suffix, "protocol", *paths],
        cwd=cwd,
        env={**os.environ, **env},
        text=True,
        capture_output=True,
        check=False,
    )


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Plan Test"], cwd=path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "plan-test@example.invalid"],
        cwd=path,
        check=True,
    )
    (path / "README.md").write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=path, check=True)
    return path


def run_dir_for(repo: Path) -> Path:
    run_dir = repo / "tmp" / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def command(
    *args: str,
    cwd: Path,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={**os.environ, **(env or {})},
        text=True,
        capture_output=True,
        check=True,
    )


def tree_for(result: subprocess.CompletedProcess[str]) -> str:
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def store_env(repo: Path, run_dir: Path) -> dict[str, str]:
    return {
        "GIT_OBJECT_DIRECTORY": str(run_dir / "objects"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(repo / ".git" / "objects"),
    }


def checkpoint(repo: Path, run_dir: Path, cwd: Path | None = None) -> str:
    result = run_block("cmd:checkpoint", cwd or repo, {"RUN_DIR": str(run_dir)})
    return tree_for(result)


def tree_paths(repo: Path, run_dir: Path, tree: str) -> list[str]:
    return command(
        "ls-tree", "-r", "--name-only", tree, cwd=repo, env=store_env(repo, run_dir)
    ).stdout.splitlines()


def file_count(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file())


def set_writable(root: Path, writable: bool) -> dict[Path, int]:
    modes = {path: path.stat().st_mode & 0o777 for path in [root, *root.rglob("*")]}
    for path, mode in modes.items():
        path.chmod(mode | 0o200 if writable else mode & ~0o222)
    return modes


def restore_modes(modes: dict[Path, int]) -> None:
    for path, mode in sorted(
        modes.items(), key=lambda item: len(item[0].parts), reverse=True
    ):
        path.chmod(mode)


def test_checkpoint_captures_worktree_without_touching_real_index(
    tmp_path: Path,
) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    (repo / "README.md").write_text("unstaged edit\n", encoding="utf-8")
    (repo / "staged.txt").write_text("staged\n", encoding="utf-8")
    command("add", "staged.txt", cwd=repo)
    (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")
    index_path = repo / ".git" / "index"
    index_before = index_path.read_bytes()

    result = run_block("cmd:checkpoint", repo, {"RUN_DIR": str(run_dir)})
    tree = tree_for(result)
    paths = tree_paths(repo, run_dir, tree)

    assert set(paths) == {"README.md", "staged.txt", "untracked.txt"}
    assert index_path.read_bytes() == index_before


def test_checkpoint_excludes_scratch_even_when_tracked(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "tmp").mkdir()
    (repo / ".superpowers").mkdir()
    (repo / "tmp" / "a.txt").write_text("before\n", encoding="utf-8")
    (repo / ".superpowers" / "b.txt").write_text("before\n", encoding="utf-8")
    command("add", "tmp/a.txt", ".superpowers/b.txt", cwd=repo)
    command("commit", "-q", "-m", "add scratch", cwd=repo)
    (repo / "tmp" / "a.txt").write_text("after\n", encoding="utf-8")
    (repo / ".superpowers" / "b.txt").write_text("after\n", encoding="utf-8")
    run_dir = run_dir_for(repo)

    tree = checkpoint(repo, run_dir)
    paths = tree_paths(repo, run_dir, tree)

    assert not any(path.startswith(("tmp/", ".superpowers/")) for path in paths)


def test_checkpoint_fails_outside_repository(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    result = run_block("cmd:checkpoint", tmp_path, {"RUN_DIR": str(run_dir)})

    assert result.returncode != 0


def test_object_probe_writes_new_object_to_run_dir_only(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    git_files = file_count(repo / ".git" / "objects")

    first = run_block("cmd:object-probe", repo, {"RUN_DIR": str(run_dir)})
    after_first = file_count(run_dir / "objects")
    second = run_block("cmd:object-probe", repo, {"RUN_DIR": str(run_dir)})
    after_second = file_count(run_dir / "objects")

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert after_first == 1
    assert after_second == 2
    assert file_count(repo / ".git" / "objects") == git_files


def test_protocol_runs_with_read_only_git_dir(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root can write through read-only mode bits")

    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    cp_a = checkpoint(repo, run_dir)
    (repo / "README.md").write_text("edited under read-only git\n", encoding="utf-8")
    env = {"RUN_DIR": str(run_dir), "CP_A": cp_a, "DIFF_NAME": "ro.diff"}
    modes = set_writable(repo / ".git", writable=False)
    try:
        probe = run_block("cmd:object-probe", repo, env)
        cp_b = checkpoint(repo, run_dir)
        env["CP_B"] = env["CP"] = cp_b
        head = run_block("cmd:head-tree", repo, env)
        kind = run_block("cmd:checkpoint-type", repo, env)
        changed = run_block("cmd:changed-paths", repo, env)
        diff = run_block("cmd:task-diff", repo, env, paths=("README.md",))
    finally:
        restore_modes(modes)

    assert probe.returncode == 0, probe.stderr
    assert head.returncode == 0, head.stderr
    assert kind.stdout == "tree\n", kind.stderr
    assert changed.stdout.split("\0") == ["M", "README.md", ""], changed.stderr
    assert diff.returncode == 0, diff.stderr
    assert b"edited under read-only git" in (run_dir / "ro.diff").read_bytes()


def test_object_probe_fails_when_run_dir_is_read_only(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root can write through read-only mode bits")

    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    modes = set_writable(run_dir, writable=False)
    try:
        result = run_block("cmd:object-probe", repo, {"RUN_DIR": str(run_dir)})
    finally:
        restore_modes(modes)

    assert result.returncode != 0


def test_checkpoint_from_subdirectory_captures_whole_repository(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "src").mkdir()
    (repo / "src" / "a.txt").write_text("a\n", encoding="utf-8")
    (repo / "README.md").write_text("edited outside cwd\n", encoding="utf-8")
    run_dir = run_dir_for(repo)
    (run_dir / "scratch.txt").write_text("scratch\n", encoding="utf-8")

    tree = checkpoint(repo, run_dir, cwd=repo / "src")
    changed = command(
        "diff", "--name-only", "HEAD", tree, cwd=repo, env=store_env(repo, run_dir)
    ).stdout.splitlines()

    assert changed == ["README.md", "src/a.txt"]


def test_relative_run_dir_resolves_from_repository_root(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "src").mkdir()
    run_dir = run_dir_for(repo)

    result = run_block("cmd:object-probe", repo / "src", {"RUN_DIR": "tmp/run"})

    assert result.returncode == 0, result.stderr
    assert file_count(run_dir / "objects") == 1
    assert not (repo / "src" / "tmp").exists()


@pytest.mark.parametrize("marker", OBJECT_BLOCKS)
def test_object_blocks_share_the_store_prelude(marker: str) -> None:
    prelude = protocol_block("cmd:object-probe").splitlines()[:11]

    assert protocol_block(marker).splitlines()[:11] == prelude
    assert protocol_block(marker).splitlines()[-1] == ")"


@pytest.mark.parametrize("marker", OBJECT_BLOCKS)
def test_object_blocks_do_not_leak_into_caller_shell(
    tmp_path: Path, marker: str
) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "src").mkdir()
    run_dir = run_dir_for(repo)
    cp = checkpoint(repo, run_dir)
    env = {
        "RUN_DIR": str(run_dir),
        "CP": cp,
        "CP_A": cp,
        "CP_B": cp,
        "DIFF_NAME": "leak.diff",
    }
    suffix = (
        "\nprintf '%s|%s|%s\\n' \"${GIT_OBJECT_DIRECTORY-unset}\" "
        '"${GIT_ALTERNATE_OBJECT_DIRECTORIES-unset}" "$PWD"'
    )

    result = run_block(marker, repo / "src", env, suffix=suffix, paths=("README.md",))

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[-1] == f"unset|unset|{repo / 'src'}"


def test_object_blocks_ignore_a_leaked_redirect(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    leaked = {
        "RUN_DIR": str(run_dir),
        "GIT_OBJECT_DIRECTORY": str(tmp_path / "missing" / "objects"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(tmp_path / "missing" / "alt"),
    }

    result = run_block("cmd:checkpoint", repo, leaked)

    assert result.returncode == 0, result.stderr


def test_checkpoint_does_not_hash_unignored_scratch(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    scratch = run_dir / "unique-scratch.txt"
    scratch.write_text("never hash this scratch payload\n", encoding="utf-8")
    blob = command("hash-object", str(scratch), cwd=repo).stdout.strip()

    checkpoint(repo, run_dir)
    probe = subprocess.run(
        ["git", "cat-file", "-e", blob],
        cwd=repo,
        env={**os.environ, **store_env(repo, run_dir)},
        capture_output=True,
        check=False,
    )

    assert probe.returncode != 0


def test_default_branch_resolves_origin_head(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    command("update-ref", "refs/remotes/origin/trunk", "HEAD", cwd=repo)
    command(
        "symbolic-ref",
        "refs/remotes/origin/HEAD",
        "refs/remotes/origin/trunk",
        cwd=repo,
    )
    run_dir = run_dir_for(repo)

    result = run_block("cmd:default-branch", repo, {"RUN_DIR": str(run_dir)})

    assert result.returncode == 0
    assert result.stdout == "trunk\n"


def test_default_branch_unresolved_without_origin_head(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)

    result = run_block("cmd:default-branch", repo, {"RUN_DIR": str(run_dir)})

    assert result.returncode == 0
    assert result.stdout == "unresolved\n"


def test_current_branch_reports_detached(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    command("checkout", "-q", "--detach", cwd=repo)
    run_dir = run_dir_for(repo)

    result = run_block("cmd:current-branch", repo, {"RUN_DIR": str(run_dir)})

    assert result.returncode == 0
    assert result.stdout == "detached\n"


def test_head_tree_matches_checkpoint_after_full_commit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "tmp").mkdir()
    (repo / "tmp" / "x").write_text("tracked scratch\n", encoding="utf-8")
    run_dir = run_dir_for(repo)
    checkpoint_tree = checkpoint(repo, run_dir)

    command("add", "-A", cwd=repo)
    command("commit", "-q", "-m", "track scratch", cwd=repo)
    head_result = run_block("cmd:head-tree", repo, {"RUN_DIR": str(run_dir)})

    assert tree_for(head_result) == checkpoint_tree


def test_head_tree_differs_after_partial_commit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "first.txt").write_text("first before\n", encoding="utf-8")
    (repo / "second.txt").write_text("second before\n", encoding="utf-8")
    command("add", "first.txt", "second.txt", cwd=repo)
    command("commit", "-q", "-m", "add files", cwd=repo)
    (repo / "first.txt").write_text("first after\n", encoding="utf-8")
    (repo / "second.txt").write_text("second after\n", encoding="utf-8")
    run_dir = run_dir_for(repo)
    checkpoint_tree = checkpoint(repo, run_dir)

    (repo / "first.txt").write_text("first committed\n", encoding="utf-8")
    command("add", "first.txt", cwd=repo)
    command("commit", "-q", "-m", "partial worktree commit", cwd=repo)
    head_result = run_block("cmd:head-tree", repo, {"RUN_DIR": str(run_dir)})

    assert tree_for(head_result) != checkpoint_tree


def test_changed_paths_reports_both_rename_endpoints(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "src" / "a.py").write_text("value = 1\n", encoding="utf-8")
    command("add", "src/a.py", cwd=repo)
    command("commit", "-q", "-m", "add source", cwd=repo)
    run_dir = run_dir_for(repo)
    cp_a = checkpoint(repo, run_dir)

    command("mv", "src/a.py", "tests/a.py", cwd=repo)
    cp_b = checkpoint(repo, run_dir)
    result = run_block(
        "cmd:changed-paths",
        repo,
        {"RUN_DIR": str(run_dir), "CP_A": cp_a, "CP_B": cp_b},
    )

    assert result.returncode == 0, result.stderr
    records = result.stdout.split("\0")
    assert records[:3] == ["R100", "src/a.py", "tests/a.py"]


def test_changed_paths_survives_newline_in_filename(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    cp_a = checkpoint(repo, run_dir)
    filename = "odd\nname.txt"
    (repo / filename).write_text("added\n", encoding="utf-8")
    cp_b = checkpoint(repo, run_dir)

    result = run_block(
        "cmd:changed-paths",
        repo,
        {"RUN_DIR": str(run_dir), "CP_A": cp_a, "CP_B": cp_b},
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.split("\0") == ["A", filename, ""]


def test_task_diff_preserves_binary_content(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    (repo / "payload.bin").write_bytes(b"old binary\x00")
    command("add", "payload.bin", cwd=repo)
    command("commit", "-q", "-m", "add binary", cwd=repo)
    run_dir = run_dir_for(repo)
    cp_a = checkpoint(repo, run_dir)
    (repo / "payload.bin").write_bytes(bytes(range(256)))
    cp_b = checkpoint(repo, run_dir)
    diff_path = run_dir / "binary.diff"

    result = run_block(
        "cmd:task-diff",
        repo,
        {
            "RUN_DIR": str(run_dir),
            "CP_A": cp_a,
            "CP_B": cp_b,
            "DIFF_NAME": diff_path.name,
        },
        paths=("payload.bin",),
    )
    assert result.returncode == 0, result.stderr
    assert b"GIT binary patch" in diff_path.read_bytes()

    temporary_index = run_dir / "apply.index"
    apply_env = {"GIT_INDEX_FILE": str(temporary_index), **store_env(repo, run_dir)}
    command("read-tree", cp_a, cwd=repo, env=apply_env)
    applied = command(
        "apply",
        "--check",
        "--cached",
        str(diff_path),
        cwd=repo,
        env=apply_env,
    )

    assert applied.returncode == 0


@pytest.mark.parametrize(
    "filename", ["README.md", "odd\nname.txt", "literal*.txt", ":(exclude)note"]
)
def test_task_diff_selects_only_literal_paths(tmp_path: Path, filename: str) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    cp_a = checkpoint(repo, run_dir)
    (repo / filename).write_text("task output\n", encoding="utf-8")
    (repo / "foreign.txt").write_text("foreign output\n", encoding="utf-8")
    (repo / "literal-other.txt").write_text(
        "foreign wildcard match\n", encoding="utf-8"
    )
    cp_b = checkpoint(repo, run_dir)

    result = run_block(
        "cmd:task-diff",
        repo,
        {
            "RUN_DIR": str(run_dir),
            "CP_A": cp_a,
            "CP_B": cp_b,
            "DIFF_NAME": "scoped.diff",
        },
        paths=(filename,),
    )

    assert result.returncode == 0, result.stderr
    diff = (run_dir / "scoped.diff").read_text(encoding="utf-8")
    assert "+task output" in diff
    assert "foreign output" not in diff
    assert "foreign wildcard match" not in diff


def test_task_diff_without_paths_fails_closed(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    cp_a = checkpoint(repo, run_dir)
    (repo / "foreign.txt").write_text("foreign output\n", encoding="utf-8")
    cp_b = checkpoint(repo, run_dir)

    result = run_block(
        "cmd:task-diff",
        repo,
        {
            "RUN_DIR": str(run_dir),
            "CP_A": cp_a,
            "CP_B": cp_b,
            "DIFF_NAME": "empty.diff",
        },
    )

    assert result.returncode != 0
    assert not (run_dir / "empty.diff").exists()


def test_head_changes_reports_foreign_commit_with_dirty_task(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    base = command("rev-parse", "HEAD", cwd=repo).stdout.strip()
    (repo / "README.md").write_text("uncommitted task\n", encoding="utf-8")
    (repo / "foreign.txt").write_text("other work\n", encoding="utf-8")
    command("add", "foreign.txt", cwd=repo)
    command("commit", "-q", "-m", "foreign", cwd=repo)
    index_before = (repo / ".git" / "index").read_bytes()

    result = run_block("cmd:head-changes", repo, {"HEAD_BASE": base})

    assert result.returncode == 0, result.stderr
    assert result.stdout.split("\0") == ["A", "foreign.txt", ""]
    assert (repo / "README.md").read_text() == "uncommitted task\n"
    assert (repo / ".git" / "index").read_bytes() == index_before


def test_head_changes_retains_reverted_path_and_rename_endpoints(
    tmp_path: Path,
) -> None:
    repo = init_repo(tmp_path / "repo")
    base = command("rev-parse", "HEAD", cwd=repo).stdout.strip()
    (repo / "README.md").write_text("pertinent commit\n", encoding="utf-8")
    command("add", "README.md", cwd=repo)
    command("commit", "-q", "-m", "pertinent", cwd=repo)
    command("revert", "--no-edit", "HEAD", cwd=repo)
    command("mv", "README.md", "foreign.md", cwd=repo)
    command("commit", "-q", "-m", "rename", cwd=repo)

    result = run_block("cmd:head-changes", repo, {"HEAD_BASE": base})

    assert result.returncode == 0, result.stderr
    records = result.stdout.split("\0")
    assert records.count("M") == 2
    assert records[:3] == ["R100", "README.md", "foreign.md"]


def test_head_changes_rejects_rewritten_history(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    base = command("rev-parse", "HEAD", cwd=repo).stdout.strip()
    command("commit", "--amend", "-q", "-m", "rewritten", cwd=repo)

    result = run_block("cmd:head-changes", repo, {"HEAD_BASE": base})

    assert result.returncode != 0
