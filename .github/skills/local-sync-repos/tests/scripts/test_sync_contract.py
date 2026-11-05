import subprocess
from pathlib import Path

import pytest
from sync_contract import SourceContractError, build_plan


def test_build_plan_creates_only_approved_managed_paths(
    source_repo: Path, target_repo: Path, managed_copy_paths: tuple[str, ...]
) -> None:
    plan = build_plan(source_repo, target_repo)
    mutations = {
        (item.action, item.path) for item in plan.operations if item.is_mutation
    }
    assert mutations == {
        *(("create", path) for path in managed_copy_paths),
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
    source_repo: Path,
    target_repo: Path,
    managed_copy_paths: tuple[str, ...],
    agents_local_template: Path,
) -> None:
    for relative in managed_copy_paths:
        target_file = target_repo / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes((source_repo / relative).read_bytes())
    instruction_src = (
        source_repo / ".github" / "instructions" / "internal-python.instructions.md"
    )
    instruction_tgt = (
        target_repo / ".github" / "instructions" / "internal-python.instructions.md"
    )
    instruction_tgt.parent.mkdir(parents=True, exist_ok=True)
    instruction_tgt.write_bytes(instruction_src.read_bytes())
    (target_repo / "AGENTS.local.md").write_bytes(agents_local_template.read_bytes())
    plan = build_plan(source_repo, target_repo)
    mutations = [op for op in plan.operations if op.is_mutation]
    assert mutations == []


def test_missing_source_path_raises_source_contract_error(
    target_repo: Path, tmp_path: Path, git_repo
) -> None:
    empty_source = git_repo(tmp_path / "empty-source")
    with pytest.raises(SourceContractError, match="missing required source path"):
        build_plan(empty_source, target_repo)


def test_fingerprint_is_stable_and_changes_with_plan(
    source_repo: Path, target_repo: Path
) -> None:
    initial = build_plan(source_repo, target_repo).fingerprint
    repeated = build_plan(source_repo, target_repo).fingerprint

    (target_repo / ".editorconfig").write_text("changed\n", encoding="utf-8")
    changed = build_plan(source_repo, target_repo).fingerprint

    assert repeated == initial
    assert changed != initial
    assert len(initial) == 64


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
