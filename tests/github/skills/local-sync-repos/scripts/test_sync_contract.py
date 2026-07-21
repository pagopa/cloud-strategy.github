import subprocess
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-sync-repos/scripts"

import sys
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_contract import (  # noqa: E402
    MANAGED_COPY_PATHS,
    SourceContractError,
    SyncPlan,
    build_plan,
    dirty_paths,
    plan_fingerprint,
)


MANAGED_COPY_PATHS_EXPECTED = (
    "AGENTS.md",
    ".python-version",
    ".pre-commit-config.yaml",
    ".editorconfig",
    ".github/copilot-instructions.md",
    ".github/workflows/_pre-commit.yml",
)


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test"],
        check=True,
        capture_output=True,
    )


def _populate_source(source: Path) -> None:
    (source / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
    (source / ".python-version").write_text("3.13\n", encoding="utf-8")
    (source / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    (source / ".editorconfig").write_text("root = true\n", encoding="utf-8")
    (source / ".github").mkdir(exist_ok=True)
    (source / ".github" / "copilot-instructions.md").write_text(
        "# copilot\n", encoding="utf-8"
    )
    (source / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (source / ".github" / "workflows" / "_pre-commit.yml").write_text(
        "name: pre-commit\n", encoding="utf-8"
    )
    instructions = source / ".github" / "instructions"
    instructions.mkdir(parents=True, exist_ok=True)
    (instructions / "internal-python.instructions.md").write_text(
        "# python\n", encoding="utf-8"
    )


@pytest.fixture()
def source_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "source"
    repo.mkdir()
    _git_init(repo)
    _populate_source(repo)
    subprocess.run(
        ["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "init", "--allow-empty"],
        check=True,
        capture_output=True,
    )
    return repo


@pytest.fixture()
def target_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "target"
    repo.mkdir()
    _git_init(repo)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "init", "--allow-empty"],
        check=True,
        capture_output=True,
    )
    return repo


def test_managed_copy_paths_constant_matches_approved_scope() -> None:
    assert MANAGED_COPY_PATHS == MANAGED_COPY_PATHS_EXPECTED


def test_build_plan_creates_only_approved_managed_paths(
    source_repo: Path, target_repo: Path
) -> None:
    plan = build_plan(source_repo, target_repo)
    mutations = {
        (item.action, item.path) for item in plan.operations if item.is_mutation
    }
    assert mutations == {
        *(("create", path) for path in MANAGED_COPY_PATHS_EXPECTED),
        ("create", ".github/instructions/internal-python.instructions.md"),
        ("create", "AGENTS.local.md"),
    }


def test_build_plan_updates_changed_managed_file(
    source_repo: Path, target_repo: Path
) -> None:
    (target_repo / ".editorconfig").write_text("target\n", encoding="utf-8")
    plan = build_plan(source_repo, target_repo)
    assert ("update", ".editorconfig") in {
        (item.action, item.path) for item in plan.operations
    }


def test_build_plan_preserves_local_instruction_and_deletes_other_target_only_instruction(
    source_repo: Path, target_repo: Path
) -> None:
    local_path = target_repo / ".github/instructions/local-team.instructions.md"
    stale_path = target_repo / ".github/instructions/stale.instructions.md"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text("local\n", encoding="utf-8")
    stale_path.write_text("stale\n", encoding="utf-8")
    plan = build_plan(source_repo, target_repo)
    assert (
        "preserve",
        ".github/instructions/local-team.instructions.md",
    ) in {(item.action, item.path) for item in plan.operations}
    assert (
        "delete",
        ".github/instructions/stale.instructions.md",
    ) in {(item.action, item.path) for item in plan.operations}


def test_existing_agents_local_is_preserved_byte_for_byte(
    source_repo: Path, target_repo: Path
) -> None:
    local_policy = target_repo / "AGENTS.local.md"
    local_policy.write_bytes(b"consumer-owned\n")
    plan = build_plan(source_repo, target_repo)
    assert ("preserve", "AGENTS.local.md") in {
        (item.action, item.path) for item in plan.operations
    }


def test_nested_source_instructions_are_discovered(
    source_repo: Path, target_repo: Path
) -> None:
    nested = source_repo / ".github" / "instructions" / "nested"
    nested.mkdir(parents=True, exist_ok=True)
    (nested / "deep.instructions.md").write_text("deep\n", encoding="utf-8")
    plan = build_plan(source_repo, target_repo)
    assert (
        "create",
        ".github/instructions/nested/deep.instructions.md",
    ) in {(item.action, item.path) for item in plan.operations}


def test_identical_files_produce_no_mutation(
    source_repo: Path, target_repo: Path
) -> None:
    for relative in MANAGED_COPY_PATHS_EXPECTED:
        target_file = target_repo / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes((source_repo / relative).read_bytes())
    instruction_src = source_repo / ".github" / "instructions" / "internal-python.instructions.md"
    instruction_tgt = target_repo / ".github" / "instructions" / "internal-python.instructions.md"
    instruction_tgt.parent.mkdir(parents=True, exist_ok=True)
    instruction_tgt.write_bytes(instruction_src.read_bytes())
    (target_repo / "AGENTS.local.md").write_text(
        (REPO_ROOT / ".github/skills/local-sync-repos/templates/AGENTS.local.md").read_text(),
        encoding="utf-8",
    )
    plan = build_plan(source_repo, target_repo)
    mutations = [op for op in plan.operations if op.is_mutation]
    assert mutations == []


def test_missing_source_path_raises_source_contract_error(
    target_repo: Path, tmp_path: Path
) -> None:
    empty_source = tmp_path / "empty-source"
    empty_source.mkdir()
    _git_init(empty_source)
    subprocess.run(
        ["git", "-C", str(empty_source), "commit", "-m", "init", "--allow-empty"],
        check=True,
        capture_output=True,
    )
    with pytest.raises(SourceContractError, match="missing required source path"):
        build_plan(empty_source, target_repo)


def test_fingerprint_is_deterministic(
    source_repo: Path, target_repo: Path
) -> None:
    first = build_plan(source_repo, target_repo)
    second = build_plan(source_repo, target_repo)
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_dirty_managed_overlap_is_reported(
    source_repo: Path, target_repo: Path
) -> None:
    (target_repo / ".editorconfig").write_text("dirty\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(target_repo), "add", "-A"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(target_repo), "commit", "-m", "seed", "--allow-empty"],
        check=True,
        capture_output=True,
    )
    (target_repo / ".editorconfig").write_text("dirty-again\n", encoding="utf-8")
    plan = build_plan(source_repo, target_repo)
    assert ".editorconfig" in plan.dirty_managed_overlap


def test_dirty_unrelated_path_is_non_blocking(
    source_repo: Path, target_repo: Path
) -> None:
    (target_repo / "unrelated.txt").write_text("dirty\n", encoding="utf-8")
    plan = build_plan(source_repo, target_repo)
    assert plan.dirty_managed_overlap == ()


def test_same_source_and_target_is_rejected(
    source_repo: Path,
) -> None:
    with pytest.raises(SourceContractError, match="same directory"):
        build_plan(source_repo, source_repo)
