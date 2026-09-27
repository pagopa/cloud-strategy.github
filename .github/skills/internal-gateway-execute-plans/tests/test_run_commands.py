from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Mapping

import pytest


BUNDLE_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = BUNDLE_ROOT / "references" / "run-protocol.md"


def extract_block(text: str, marker: str) -> str:
    match = re.search(
        rf"(?m)^<!-- {re.escape(marker)} -->\n```sh\n(.*?)\n```$",
        text,
        re.DOTALL,
    )
    assert match is not None, f"missing shell block marker: {marker}"
    return match.group(1)


def run_block(
    marker: str,
    cwd: Path,
    env: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    assert PROTOCOL_PATH.is_file(), "run-protocol.md does not exist"
    text = PROTOCOL_PATH.read_text(encoding="utf-8")
    return subprocess.run(
        ["sh", "-c", extract_block(text, marker)],
        cwd=cwd,
        env={**os.environ, **env},
        text=True,
        capture_output=True,
        check=False,
    )


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Plan Test"], cwd=path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "plan-test@example.invalid"],
        cwd=path,
        check=True,
    )
    (path / "README.md").write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"], cwd=path, check=True
    )
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


def checkpoint(repo: Path, run_dir: Path) -> str:
    result = run_block("cmd:checkpoint", repo, {"RUN_DIR": str(run_dir)})
    return tree_for(result)


def loose_object_count(repo: Path) -> int:
    result = command("count-objects", "-v", cwd=repo)
    match = re.search(r"^count: (\d+)$", result.stdout, re.MULTILINE)
    assert match is not None, result.stdout
    return int(match.group(1))


def test_checkpoint_captures_worktree_without_touching_real_index(tmp_path: Path) -> None:
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
    paths = command("ls-tree", "-r", "--name-only", tree, cwd=repo).stdout.splitlines()

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
    paths = command("ls-tree", "-r", "--name-only", tree, cwd=repo).stdout.splitlines()

    assert not any(path.startswith(("tmp/", ".superpowers/")) for path in paths)


def test_checkpoint_fails_outside_repository(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    result = run_block("cmd:checkpoint", tmp_path, {"RUN_DIR": str(run_dir)})

    assert result.returncode != 0


def test_object_probe_writes_new_object(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    before = loose_object_count(repo)

    first = run_block("cmd:object-probe", repo, {"RUN_DIR": str(run_dir)})
    after_first = loose_object_count(repo)
    second = run_block("cmd:object-probe", repo, {"RUN_DIR": str(run_dir)})
    after_second = loose_object_count(repo)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert after_first == before + 1
    assert after_second == after_first + 1


def test_object_probe_fails_on_read_only_object_store(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root can write through read-only mode bits")

    repo = init_repo(tmp_path / "repo")
    run_dir = run_dir_for(repo)
    object_root = repo / ".git" / "objects"
    permissions = {
        path: path.stat().st_mode & 0o777
        for path in [object_root, *object_root.rglob("*")]
    }
    try:
        for path, mode in permissions.items():
            path.chmod(mode & ~0o222)
        result = run_block("cmd:object-probe", repo, {"RUN_DIR": str(run_dir)})
    finally:
        for path, mode in sorted(
            permissions.items(), key=lambda item: len(item[0].parts), reverse=True
        ):
            path.chmod(mode)

    assert result.returncode != 0


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
        {"CP_A": cp_a, "CP_B": cp_b},
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
        {"CP_A": cp_a, "CP_B": cp_b},
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
    )
    assert result.returncode == 0, result.stderr
    assert b"GIT binary patch" in diff_path.read_bytes()

    temporary_index = run_dir / "apply.index"
    command(
        "read-tree",
        cp_a,
        cwd=repo,
        env={"GIT_INDEX_FILE": str(temporary_index)},
    )
    applied = command(
        "apply",
        "--check",
        "--cached",
        str(diff_path),
        cwd=repo,
        env={"GIT_INDEX_FILE": str(temporary_index)},
    )

    assert applied.returncode == 0
