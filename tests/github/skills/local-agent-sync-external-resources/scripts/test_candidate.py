import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources_core import (  # noqa: E402
    ImportedOverride,
    ManagedAsset,
    ManagedResources,
    ManagedSource,
    TextReplacement,
    find_dirty_targets,
    load_overrides,
    materialize_candidate,
    normalize_candidate,
    replay_overrides,
    select_overrides,
    validate_external_workspace,
    verify_override_hash,
)


def _run_git(cwd: Path, args: list[str]) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_all(repo: Path) -> None:
    _run_git(repo, ["add", "-A"])
    _run_git(
        repo,
        ["commit", "-m", "snapshot", "--allow-empty"],
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    _commit_all(repo)
    return repo


def _example_asset(local: str = ".github/skills/example") -> ManagedAsset:
    return ManagedAsset(
        source="test",
        upstream="skills/example",
        local=local,
        canonical_name="example",
    )


def _superpowers_resources() -> ManagedResources:
    asset = ManagedAsset(
        source="obra-superpowers",
        upstream="skills/brainstorming",
        local=".github/skills/superpowers-brainstorming",
        canonical_name="superpowers-brainstorming",
    )
    source = ManagedSource(
        source_id="obra-superpowers",
        repository="https://github.com/obra/superpowers.git",
        ref="abc123",
        assets=(asset,),
    )
    replacement = TextReplacement(
        source="obra-superpowers",
        old="docs/superpowers",
        new="tmp/superpowers",
    )
    return ManagedResources(
        sources=(source,),
        replacements=(replacement,),
        watchlist=(),
    )


def test_workspace_inside_repository_is_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workspace = repo / "tmp" / "refresh"
    workspace.mkdir(parents=True)

    with pytest.raises(ValueError, match="outside the repository"):
        validate_external_workspace(repo, workspace)


def test_workspace_outside_repository_is_accepted(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = tmp_path / "external-workspace"
    workspace.mkdir()

    validate_external_workspace(repo, workspace)


def test_dirty_managed_target_is_reported(git_repo: Path) -> None:
    target = git_repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\n", encoding="utf-8")
    _commit_all(git_repo)
    target.write_text("---\nname: locally-edited\n---\n", encoding="utf-8")

    assert find_dirty_targets(git_repo, (_example_asset(),)) == (
        ".github/skills/example/SKILL.md",
    )


def test_clean_managed_target_is_not_reported(git_repo: Path) -> None:
    target = git_repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\n", encoding="utf-8")
    _commit_all(git_repo)

    assert find_dirty_targets(git_repo, (_example_asset(),)) == ()


def test_normalization_updates_name_and_declared_text_only(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    skill = candidate / ".github/skills/superpowers-brainstorming/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: brainstorming\n---\nWrite to docs/superpowers.\n",
        encoding="utf-8",
    )

    changed = normalize_candidate(_superpowers_resources(), candidate)

    assert changed == (".github/skills/superpowers-brainstorming/SKILL.md",)
    content = skill.read_text(encoding="utf-8")
    assert "name: superpowers-brainstorming" in content
    assert "tmp/superpowers" in content


def test_materialize_candidate_copies_upstream_to_local(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    source_checkout = workspace / "sources" / "test-source" / "skills" / "example"
    source_checkout.mkdir(parents=True)
    (source_checkout / "SKILL.md").write_text(
        "---\nname: upstream-name\n---\n", encoding="utf-8"
    )

    asset = ManagedAsset(
        source="test-source",
        upstream="skills/example",
        local=".github/skills/example",
        canonical_name="example",
    )
    source = ManagedSource(
        source_id="test-source",
        repository="https://example.com/repo.git",
        ref="abc",
        assets=(asset,),
    )
    resources = ManagedResources(
        sources=(source,), replacements=(), watchlist=()
    )

    candidate = tmp_path / "candidate"
    materialize_candidate(resources, workspace, candidate)

    target = candidate / ".github/skills/example/SKILL.md"
    assert target.exists()
    assert "upstream-name" in target.read_text(encoding="utf-8")


@pytest.fixture
def candidate_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "candidate"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    _commit_all(repo)
    return repo


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _make_override(
    candidate_repo: Path,
    override_id: str = "test-override",
    target_rel: str = ".github/skills/test/SKILL.md",
    original_content: str = "---\nname: test\n---\nOriginal content.\n",
    patched_content: str = "---\nname: test\n---\nPatched content.\n",
) -> tuple[ImportedOverride, Path, Path]:
    target = candidate_repo / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(original_content, encoding="utf-8")
    _commit_all(candidate_repo)

    patch_dir = candidate_repo / "patches"
    patch_dir.mkdir(exist_ok=True)
    patch_path = patch_dir / f"{override_id}.patch"

    target.write_text(patched_content, encoding="utf-8")
    result = subprocess.run(
        ["git", "diff", "--", target_rel],
        cwd=candidate_repo,
        capture_output=True,
        text=True,
        check=True,
    )
    patch_path.write_text(result.stdout, encoding="utf-8")
    target.write_text(original_content, encoding="utf-8")

    override = ImportedOverride(
        override_id=override_id,
        target_path=target_rel,
        patch_path=patch_path.relative_to(candidate_repo).as_posix(),
        apply_strategy="git-apply",
        expected_content_hash=_sha256(patched_content),
    )
    return override, target, patch_path


def test_override_applies_cleanly(candidate_repo: Path) -> None:
    override, target, _ = _make_override(candidate_repo)

    results = replay_overrides(candidate_repo, (override,))

    assert len(results) == 1
    assert results[0].override_id == "test-override"
    assert results[0].status == "applied"
    assert "Patched content." in target.read_text(encoding="utf-8")


def test_conflicting_second_override_leaves_candidate_unchanged(
    candidate_repo: Path,
) -> None:
    first, target, _ = _make_override(
        candidate_repo,
        override_id="first",
        patched_content="---\nname: test\n---\nFirst patch.\n",
    )
    second = ImportedOverride(
        override_id="second",
        target_path=first.target_path,
        patch_path=first.patch_path,
        apply_strategy="git-apply",
        expected_content_hash="x" * 64,
    )
    before_content = target.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        replay_overrides(candidate_repo, (first, second))

    after_content = target.read_text(encoding="utf-8")
    assert before_content == after_content


def test_unknown_requested_override_id_is_rejected() -> None:
    overrides = (
        ImportedOverride(
            override_id="known",
            target_path=".github/skills/test/SKILL.md",
            patch_path="patches/test.patch",
            apply_strategy="git-apply",
            expected_content_hash="a" * 64,
        ),
    )

    with pytest.raises(ValueError, match="unknown override id: missing"):
        select_overrides(overrides, ("missing",))


def test_load_overrides_from_yaml(tmp_path: Path) -> None:
    registry = tmp_path / "overrides.yaml"
    registry.write_text(
        """\
version: 1
overrides:
  - id: test-override
    target_path: .github/skills/test/SKILL.md
    patch_path: patches/test.patch
    apply_strategy: git-apply
    expected_content_hash: abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
""",
        encoding="utf-8",
    )

    overrides = load_overrides(registry)

    assert len(overrides) == 1
    assert overrides[0].override_id == "test-override"
    assert overrides[0].expected_content_hash == "abcdef0123456789" * 4
