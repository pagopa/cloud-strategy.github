import re
from pathlib import Path

import pytest
import yaml
from sync_external_resources_core import (
    _MATTPOCOCK_GRILL_ME_SCOPE_CONVERGENCE_END,
    _MATTPOCOCK_GRILL_ME_SCOPE_CONVERGENCE_START,
    load_managed_resources,
    load_overrides,
    render_source_summary_table,
    validate_override_patches,
)

_COMMIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MANIFEST_PATH = ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
_OVERRIDES_PATH = ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
_SUMMARY_START = "# managed-sources-summary:start"
_SUMMARY_END = "# managed-sources-summary:end"

_FULL_SHA40 = "a" * 40
_FULL_SHA40_ALT = "b" * 40

_MATTPOCOCK_UNPREFIXED = {"grill-me", "grilling"}
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
# Gateway handoff owners stay model-invocable in both runtimes.
_MATTPOCOCK_CODEX_MODEL_INVOKABLE = {
    "domain-modeling",
    "handoff",
    "implement",
    "research",
    "setup-matt-pocock-skills",
    "to-spec",
    "to-tickets",
}
_MATTPOCOCK_COPILOT_MODEL_INVOKABLE = {"implement", "to-spec"}
_RETIRED_SKILL_BUNDLES = (
    "internal-grill-me",
    "mattpocock-writing-great-skills",
    "anthropic-skill-creator",
)


def _write_manifest(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "managed-resources.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_live_manifest_refs_are_full_lowercase_object_ids(repo_root: Path) -> None:
    manifest = load_managed_resources(repo_root / _MANIFEST_PATH)
    for source in manifest.sources:
        assert _COMMIT_OBJECT_ID_RE.match(source.ref), (
            f"source {source.source_id} ref {source.ref!r} "
            f"is not a full lowercase commit object ID"
        )


def _load_live_manifest(repo_root: Path):
    return load_managed_resources(repo_root / _MANIFEST_PATH)


def test_live_manifest_declares_commit_date_for_every_source(repo_root: Path) -> None:
    manifest = _load_live_manifest(repo_root)
    for source in manifest.sources:
        assert source.commit_date is not None, (
            f"source {source.source_id} must declare a pinned commit_date"
        )
        assert _ISO_DATE_RE.match(source.commit_date), (
            f"source {source.source_id} commit_date {source.commit_date!r} "
            f"is not an ISO date"
        )


def test_live_manifest_summary_table_matches_declared_sources(repo_root: Path) -> None:
    manifest_path = repo_root / _MANIFEST_PATH
    manifest = _load_live_manifest(repo_root)
    text = manifest_path.read_text(encoding="utf-8")
    start = text.index(_SUMMARY_START)
    end = text.index(_SUMMARY_END) + len(_SUMMARY_END)

    assert text[start:end].strip() == render_source_summary_table(manifest)


def test_manifest_accepts_optional_commit_date(tmp_path: Path) -> None:
    manifest = load_managed_resources(
        _write_manifest(
            tmp_path,
            f"""\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: {_FULL_SHA40}
    commit_date: "2026-07-24"
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        )
    )
    assert manifest.sources[0].commit_date == "2026-07-24"


def test_manifest_rejects_invalid_commit_date(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="commit_date"):
        load_managed_resources(
            _write_manifest(
                tmp_path,
                f"""\
version: 1
sources:
  source:
    repository: https://github.com/example/repo.git
    ref: {_FULL_SHA40}
    commit_date: "2026-13-45"
    assets:
      - upstream: skills/one
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
            )
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


def test_manifest_accepts_codex_only_invocation_policy(tmp_path: Path) -> None:
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
          codex:
            allow_implicit_invocation: false
watchlist: []
""",
        )
    )
    policy = manifest.sources[0].assets[0].invocation_policy
    assert policy is not None
    assert not policy.copilot_disable_model_invocation
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
    manifest = _load_live_manifest(repo_root)
    inventory = (repo_root / ".github/INVENTORY.md").read_text(encoding="utf-8")

    for asset in manifest.assets:
        assert (repo_root / asset.local).exists(), (
            f"{asset.canonical_name}: {asset.local} is missing on disk"
        )
        if (repo_root / asset.local / "SKILL.md").is_file():
            assert asset.local == f".github/skills/{asset.canonical_name}"
            assert f"{asset.local}/SKILL.md" in inventory

    matt_source = next(
        source for source in manifest.sources if source.source_id == "mattpocock-skills"
    )
    assert matt_source.rewrite_skill_references is True
    assert dict(matt_source.skill_reference_aliases) == {}
    for asset in matt_source.assets:
        upstream_name = Path(asset.upstream).name
        expected_name = (
            upstream_name
            if upstream_name in _MATTPOCOCK_UNPREFIXED
            else f"mattpocock-{upstream_name}"
        )
        assert asset.canonical_name == expected_name

    anthropic_source = next(
        source for source in manifest.sources if source.source_id == "anthropic-skills"
    )
    assert anthropic_source.ensure_python_shebangs is True


def test_live_mattpocock_invocation_policy(repo_root: Path) -> None:
    manifest = _load_live_manifest(repo_root)
    matt_source = next(
        source for source in manifest.sources if source.source_id == "mattpocock-skills"
    )
    upstream_names = {Path(asset.upstream).name for asset in matt_source.assets}
    assert _MATTPOCOCK_USER_INVOKED <= upstream_names
    assert _MATTPOCOCK_CODEX_MODEL_INVOKABLE <= upstream_names

    for asset in matt_source.assets:
        upstream_name = Path(asset.upstream).name
        policy = asset.invocation_policy
        expected_codex = (
            False
            if upstream_name in _MATTPOCOCK_USER_INVOKED
            and upstream_name not in _MATTPOCOCK_CODEX_MODEL_INVOKABLE
            else None
        )
        expected_copilot = (
            True
            if upstream_name in _MATTPOCOCK_USER_INVOKED
            and upstream_name not in _MATTPOCOCK_COPILOT_MODEL_INVOKABLE
            else None
        )
        assert (
            policy.codex_allow_implicit_invocation if policy else None
        ) == expected_codex, upstream_name
        assert (
            policy.copilot_disable_model_invocation if policy else None
        ) == expected_copilot, upstream_name


@pytest.mark.parametrize("name", _RETIRED_SKILL_BUNDLES)
def test_retired_skill_bundles_absent(repo_root: Path, name: str) -> None:
    local = f".github/skills/{name}"
    manifest = _load_live_manifest(repo_root)
    inventory = (repo_root / ".github/INVENTORY.md").read_text(encoding="utf-8")

    assert not (repo_root / local).exists()
    assert all(
        asset.local != local and not asset.local.startswith(local + "/")
        for asset in manifest.assets
    )
    assert name not in inventory


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


@pytest.mark.parametrize(
    "retired_target",
    (
        ".github/skills/mattpocock-handoff/SKILL.md",
        ".github/skills/mattpocock-writing-great-skills/SKILL.md",
        ".github/skills/mattpocock-writing-for-agents/SKILL.md",
        ".github/skills/addyosmani-idea-refine",
    ),
)
def test_retired_override_targets_absent(repo_root: Path, retired_target: str) -> None:
    overrides = load_overrides(repo_root / _OVERRIDES_PATH)

    assert not any(
        override.target_path == retired_target
        or override.target_path.startswith(retired_target + "/")
        for override in overrides
    )


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


def test_live_managed_skills_match_invocation_policy(repo_root: Path) -> None:
    resources = _load_live_manifest(repo_root)
    mismatches: list[str] = []
    for asset in resources.assets:
        bundle = repo_root / asset.local
        skill = bundle / "SKILL.md"
        if not skill.is_file():
            continue
        policy = asset.invocation_policy
        frontmatter = yaml.safe_load(
            skill.read_text(encoding="utf-8").split("---", 2)[1]
        )
        expected_copilot = policy.copilot_disable_model_invocation if policy else None
        if frontmatter.get("disable-model-invocation") != (
            True if expected_copilot else None
        ):
            mismatches.append(f"{asset.canonical_name}: SKILL.md invocation")

        metadata_path = bundle / "agents/openai.yaml"
        metadata = (
            yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
            if metadata_path.is_file()
            else {}
        )
        actual_codex = (metadata.get("policy") or {}).get("allow_implicit_invocation")
        expected_codex = policy.codex_allow_implicit_invocation if policy else None
        if actual_codex != expected_codex:
            mismatches.append(f"{asset.canonical_name}: agents/openai.yaml policy")

    assert mismatches == []


def test_live_grill_me_has_one_scope_convergence_block(repo_root: Path) -> None:
    content = (repo_root / ".github/skills/grill-me/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert content.count(_MATTPOCOCK_GRILL_ME_SCOPE_CONVERGENCE_START) == 1
    assert content.count(_MATTPOCOCK_GRILL_ME_SCOPE_CONVERGENCE_END) == 1
