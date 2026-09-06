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

_MATTPOCOCK_REF = "6acc160e4e0cd062dbbbd7a1b26ae92855edf07e"
_MATTPOCOCK_ENGINEERING_SKILLS = {
    "ask-matt",
    "code-review",
    "codebase-design",
    "diagnosing-bugs",
    "domain-modeling",
    "grill-with-docs",
    "implement",
    "improve-codebase-architecture",
    "prototype",
    "research",
    "resolving-merge-conflicts",
    "setup-matt-pocock-skills",
    "tdd",
    "to-spec",
    "to-tickets",
    "triage",
    "wayfinder",
    "wizard",
}
_MATTPOCOCK_PRODUCTIVITY_SKILLS = {
    "grill-me",
    "grilling",
    "handoff",
    "teach",
    "to-questionnaire",
    "wait-what",
    "writing-for-agents",
}
_MATTPOCOCK_USER_INVOKED = {
    "ask-matt",
    "grill-with-docs",
    "grilling",
    "handoff",
    "implement",
    "improve-codebase-architecture",
    "teach",
    "to-questionnaire",
    "to-spec",
    "to-tickets",
    "triage",
    "wait-what",
    "wayfinder",
}


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


def test_manifest_accepts_optional_asset_invocation_policy(tmp_path: Path) -> None:
    manifest = load_managed_resources(
        _write_manifest(
            tmp_path,
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
        invocation_policy:
          copilot:
            disable_model_invocation: true
          codex:
            allow_implicit_invocation: false
watchlist: []
""",
        )
    )
    policy = manifest.sources[0].assets[0].invocation_policy
    assert policy is not None
    assert policy.copilot_disable_model_invocation is True
    assert policy.codex_allow_implicit_invocation is False


def test_manifest_asset_invocation_policy_defaults_to_none(tmp_path: Path) -> None:
    manifest = load_managed_resources(
        _write_manifest(
            tmp_path,
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
watchlist: []
""",
        )
    )
    assert manifest.sources[0].assets[0].invocation_policy is None


def test_manifest_rejects_invocation_policy_with_unknown_runtime(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="invocation_policy"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
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
        invocation_policy:
          unknown-runtime:
            flag: true
watchlist: []
""",
            )
        )


def test_manifest_rejects_invocation_policy_with_unknown_field(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invocation_policy"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
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
        invocation_policy:
          copilot:
            not_a_field: true
watchlist: []
""",
            )
        )


def test_manifest_rejects_non_boolean_invocation_policy_field(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invocation_policy"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
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
        invocation_policy:
          copilot:
            disable_model_invocation: "yes"
watchlist: []
""",
            )
        )


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

    assert len(manifest.assets) == 67
    assert len(manifest.watchlist) == 11
    matt_source = next(
        source for source in manifest.sources if source.source_id == "mattpocock-skills"
    )
    assert matt_source.ref == _MATTPOCOCK_REF
    assert matt_source.rewrite_skill_references is True
    assert dict(matt_source.skill_reference_aliases) == {}
    expected_upstreams = {
        *(f"skills/engineering/{name}" for name in _MATTPOCOCK_ENGINEERING_SKILLS),
        *(f"skills/productivity/{name}" for name in _MATTPOCOCK_PRODUCTIVITY_SKILLS),
    }
    assert {asset.upstream for asset in matt_source.assets} == expected_upstreams
    assert len(matt_source.assets) == 25
    expected_canonical_names = {
        name if name in {"grill-me", "grilling"} else f"mattpocock-{name}"
        for name in _MATTPOCOCK_ENGINEERING_SKILLS | _MATTPOCOCK_PRODUCTIVITY_SKILLS
    }
    assert {asset.canonical_name for asset in matt_source.assets} == (
        expected_canonical_names
    )
    assert {
        Path(asset.upstream).name
        for asset in matt_source.assets
        if asset.invocation_policy is not None
    } == _MATTPOCOCK_USER_INVOKED
    for asset in matt_source.assets:
        upstream_name = Path(asset.upstream).name
        if upstream_name in _MATTPOCOCK_USER_INVOKED:
            assert asset.invocation_policy is not None
            assert asset.invocation_policy.copilot_disable_model_invocation is True
            assert asset.invocation_policy.codex_allow_implicit_invocation is False
        else:
            assert asset.invocation_policy is None
    anthropic_source = next(
        source for source in manifest.sources if source.source_id == "anthropic-skills"
    )
    assert anthropic_source.ensure_python_shebangs is True
    assert {
        item.upstream_id
        for item in manifest.watchlist
        if item.source_family == "mattpocock/skills"
    } >= {"prototype", "qa"}
    assert "to-tickets" not in {
        item.upstream_id
        for item in manifest.watchlist
        if item.source_family == "mattpocock/skills"
    }
    assert "triage" not in {
        item.upstream_id
        for item in manifest.watchlist
        if item.source_family == "mattpocock/skills"
    }
    assert "mattpocock-writing-great-skills" not in expected_canonical_names
    assert not (repo_root / ".github/skills/mattpocock-writing-great-skills").exists()
    inventory = (repo_root / ".github/INVENTORY.md").read_text(encoding="utf-8")
    for canonical_name in expected_canonical_names:
        assert f".github/skills/{canonical_name}/SKILL.md" in inventory
    assert ".github/skills/internal-grill-me/SKILL.md" not in inventory
    assert "mattpocock-writing-great-skills" not in inventory
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


def test_live_handoff_override_is_owned_by_candidate_normalization(
    repo_root: Path,
) -> None:
    overrides_path = (
        repo_root
        / ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
    )
    overrides = load_overrides(overrides_path)
    assert all(
        override.target_path != ".github/skills/mattpocock-handoff/SKILL.md"
        for override in overrides
    )


def test_mattpocock_writing_for_agents_needs_no_replay_override(
    repo_root: Path,
) -> None:
    overrides_path = (
        repo_root / ".github/skills/local-agent-sync-external-resources/references/"
        "imported-asset-overrides.yaml"
    )
    overrides = load_overrides(overrides_path)
    override_targets = {override.target_path for override in overrides}

    assert ".github/skills/mattpocock-writing-great-skills/SKILL.md" not in (
        override_targets
    )
    assert ".github/skills/mattpocock-writing-for-agents/SKILL.md" not in (
        override_targets
    )


def test_active_internal_skill_consumers_use_current_mattpocock_entrypoints(
    repo_root: Path,
) -> None:
    active_consumers = (
        repo_root / ".github/skills/internal-skill-creator/SKILL.md",
        repo_root / ".github/skills/internal-skill-creator/agents/openai.yaml",
    )

    combined = "\n".join(
        consumer.read_text(encoding="utf-8") for consumer in active_consumers
    )
    assert "mattpocock-writing-great-skills" not in combined
    assert "mattpocock-writing-for-agents" in combined
    assert "/internal-grill-me" not in combined


def test_manifest_rejects_undeclared_backtick_skill_reference(tmp_path: Path) -> None:
    manifest = tmp_path / "managed-resources.yaml"
    manifest.write_text(
        "version: 1\n"
        "sources:\n"
        "  example-source:\n"
        "    repository: https://example.com/repo.git\n"
        f"    ref: {'a' * 40}\n"
        "    rewrite_skill_references: true\n"
        "    backtick_skill_references:\n"
        "      - not-an-asset\n"
        "    assets:\n"
        "      - upstream: skills/example\n"
        "        local: .github/skills/example\n"
        "        canonical_name: example\n"
        "watchlist: []\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="not-an-asset"):
        load_managed_resources(manifest)
