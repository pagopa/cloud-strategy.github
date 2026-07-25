import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources_core import (  # noqa: E402
    load_managed_resources,
    load_overrides,
    validate_override_patches,
)


_COMMIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")

_FULL_SHA40 = "a" * 40
_FULL_SHA40_ALT = "b" * 40


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


def _write_manifest(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "managed-resources.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_live_manifest_refs_are_full_lowercase_object_ids(repo_root: Path) -> None:
    manifest = load_managed_resources(
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )
    for source in manifest.sources:
        assert _COMMIT_OBJECT_ID_RE.match(source.ref), (
            f"source {source.source_id} ref {source.ref!r} "
            f"is not a full lowercase commit object ID"
        )


def test_manifest_accepts_optional_advertised_ref(tmp_path: Path) -> None:
    manifest = load_managed_resources(
        _write_manifest(
            tmp_path,
            f"""\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: {_FULL_SHA40}
    advertised_ref: refs/heads/main
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        )
    )
    assert manifest.sources[0].advertised_ref == "refs/heads/main"


def test_manifest_rejects_short_ref(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="full lowercase commit object ID"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
                """\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: abc123
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
            )
        )


def test_manifest_rejects_branch_name_ref(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="full lowercase commit object ID"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
                """\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: main
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
            )
        )


def test_manifest_rejects_uppercase_sha_ref(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="full lowercase commit object ID"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
                f"""\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: {"A" * 40}
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
            )
        )


def test_live_manifest_preserves_declared_scope(repo_root: Path) -> None:
    manifest = load_managed_resources(
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )

    assert len(manifest.assets) == 54
    assert len(manifest.watchlist) == 13
    matt_source = next(
        source for source in manifest.sources if source.source_id == "mattpocock-skills"
    )
    assert matt_source.rewrite_skill_references is True
    assert dict(matt_source.skill_reference_aliases) == {}
    assert {
        item.upstream_id
        for item in manifest.watchlist
        if item.source_family == "mattpocock/skills"
    } >= {"prototype", "triage", "to-tickets", "qa"}
    assert {
        item.canonical_name for item in matt_source.assets
    } >= {
        "mattpocock-grill-with-docs",
        "mattpocock-domain-modeling",
        "mattpocock-implement",
        "mattpocock-tdd",
        "mattpocock-to-spec",
        "mattpocock-setup-matt-pocock-skills",
        "mattpocock-code-review",
        "mattpocock-wayfinder",
        "mattpocock-writing-great-skills",
    }
    assert "grill-me" not in {
        item.canonical_name for item in matt_source.assets
    }
    assert {
        (source.repository, asset.upstream, asset.local, asset.canonical_name)
        for source in manifest.sources
        for asset in source.assets
    } >= {
        (
            "https://github.com/atlassian/atlassian-mcp-server.git",
            "skills/search-company-knowledge",
            ".github/skills/search-company-knowledge",
            "search-company-knowledge",
        ),
        (
            "https://github.com/openai/skills.git",
            "skills/.curated/openai-docs",
            ".github/skills/openai-docs",
            "openai-docs",
        ),
        (
            "https://github.com/anthropics/skills.git",
            "skills/docx",
            ".github/skills/anthropic-docx",
            "anthropic-docx",
        ),
        (
            "https://github.com/anthropics/skills.git",
            "skills/pptx",
            ".github/skills/anthropic-pptx",
            "anthropic-pptx",
        ),
        (
            "https://github.com/anthropics/skills.git",
            "skills/xlsx",
            ".github/skills/anthropic-xlsx",
            "anthropic-xlsx",
        ),
    }
    imported_assets = {
        (source.repository, asset.upstream, asset.local, asset.canonical_name)
        for source in manifest.sources
        for asset in source.assets
    }
    assert (
        "https://github.com/anthropics/skills.git",
        "skills/skill-creator",
        ".github/skills/anthropic-skill-creator",
        "anthropic-skill-creator",
    ) not in imported_assets
    assert {
        item.local for item in manifest.assets if item.source == "obra-superpowers"
    } == {
        ".github/skills/superpowers-brainstorming",
        ".github/skills/superpowers-dispatching-parallel-agents",
        ".github/skills/superpowers-executing-plans",
        ".github/skills/superpowers-finishing-a-development-branch",
        ".github/skills/superpowers-receiving-code-review",
        ".github/skills/superpowers-requesting-code-review",
        ".github/skills/superpowers-subagent-driven-development",
        ".github/skills/superpowers-systematic-debugging",
        ".github/skills/superpowers-test-driven-development",
        ".github/skills/superpowers-using-git-worktrees",
        ".github/skills/superpowers-using-superpowers",
        ".github/skills/superpowers-verification-before-completion",
        ".github/skills/superpowers-writing-plans",
    }
    assert {
        item.local
        for item in manifest.assets
        if item.source == "addyosmani-agent-skills"
    } == {
        ".github/skills/addyosmani-code-review-and-quality",
        ".github/skills/addyosmani-code-simplification",
    }


def test_manifest_rejects_duplicate_local_paths(tmp_path: Path) -> None:
    path = tmp_path / "managed-resources.yaml"
    path.write_text(
        f"""\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: {_FULL_SHA40}
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
      - upstream: skills/two
        local: .github/skills/example
        canonical_name: example-two
watchlist: []
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate local path"):
        load_managed_resources(path)


def test_live_override_registry_patch_paths_exist(repo_root: Path) -> None:
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )
    bundle_root = repo_root / ".github/skills/local-agent-sync-external-resources"

    overrides = load_overrides(overrides_path)
    validate_override_patches(overrides, bundle_root)


def test_live_override_targets_sit_under_managed_assets(repo_root: Path) -> None:
    manifest = load_managed_resources(
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )

    managed_local_paths = {asset.local for asset in manifest.assets}
    overrides = load_overrides(overrides_path)

    for override in overrides:
        matched = any(
            override.target_path == local
            or override.target_path.startswith(local + "/")
            for local in managed_local_paths
        )
        assert matched, (
            f"Override {override.override_id} target {override.target_path} "
            f"does not sit under any managed local asset"
        )


def test_live_handoff_override_forces_repo_tmp_handoff(repo_root: Path) -> None:
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )
    bundle_root = repo_root / ".github/skills/local-agent-sync-external-resources"

    overrides = load_overrides(overrides_path)
    handoff = next(
        override
        for override in overrides
        if override.target_path == ".github/skills/mattpocock-handoff/SKILL.md"
    )

    assert handoff.override_id == "mattpocock-handoff-tmp-path"
    patch_text = (bundle_root / handoff.patch_path).read_text(encoding="utf-8")
    assert "tmp/handoff/" in patch_text


def test_mattpocock_skill_creator_review_keeps_invocation_override(
    repo_root: Path,
) -> None:
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/"
        "imported-asset-overrides.yaml"
    )
    bundle_root = (
        repo_root / ".github/skills/local-agent-sync-external-resources"
    )
    overrides = load_overrides(overrides_path)
    by_target = {override.target_path: override for override in overrides}

    expected = {
        ".github/skills/mattpocock-writing-great-skills/SKILL.md":
            "mattpocock-writing-great-skills-delegated-invocation",
    }
    for target, override_id in expected.items():
        override = by_target[target]
        assert override.override_id == override_id
        patch = (bundle_root / override.patch_path).read_text(
            encoding="utf-8"
        )
        assert "-disable-model-invocation: true" in patch
        assert "internal-skill-creator" in patch
    assert (
        ".github/skills/anthropic-skill-creator/SKILL.md"
        not in by_target
    )
