import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_external_resources import _build_candidate_patch  # noqa: E402
from sync_external_resources_core import (  # noqa: E402
    ImportedOverride,
    InvocationPolicy,
    ManagedAsset,
    ManagedResources,
    ManagedSource,
    TextReplacement,
    find_dirty_targets,
    load_managed_resources,
    load_overrides,
    materialize_candidate,
    normalize_candidate,
    replay_overrides,
    select_overrides,
    validate_external_workspace,
    validate_override_patches,
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


def _write_source_metadata(sources_root: Path, source: ManagedSource) -> None:
    source_dir = sources_root / source.source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    upstream_paths = sorted(asset.upstream for asset in source.assets)
    digest = hashlib.sha256(",".join(upstream_paths).encode("utf-8")).hexdigest()
    tsv = (
        f"source_id\trepository\tref\tpaths_sha256\n"
        f"{source.source_id}\t{source.repository}\t{source.ref}\t{digest}\n"
    )
    (source_dir / ".external-resource-source.tsv").write_text(tsv, encoding="utf-8")


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
        invocation_policy=InvocationPolicy(
            copilot_disable_model_invocation=True,
            codex_allow_implicit_invocation=False,
        ),
    )
    source = ManagedSource(
        source_id="obra-superpowers",
        repository="https://github.com/obra/superpowers.git",
        ref="abc123",
        advertised_ref=None,
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


def _mattpocock_resources() -> ManagedResources:
    assets = (
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/tdd",
            local=".github/skills/mattpocock-tdd",
            canonical_name="mattpocock-tdd",
        ),
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/grill-with-docs",
            local=".github/skills/mattpocock-grill-with-docs",
            canonical_name="mattpocock-grill-with-docs",
        ),
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/domain-modeling",
            local=".github/skills/mattpocock-domain-modeling",
            canonical_name="mattpocock-domain-modeling",
        ),
    )
    source = ManagedSource(
        source_id="mattpocock-skills",
        repository="https://github.com/mattpocock/skills.git",
        ref="abc123",
        advertised_ref=None,
        assets=assets,
        rewrite_skill_references=True,
        backtick_skill_references=("tdd",),
    )
    replacement = TextReplacement(
        source="mattpocock-skills",
        old="/grilling",
        new="/grill-me",
    )
    return ManagedResources(
        sources=(source,), replacements=(replacement,), watchlist=()
    )


def test_normalization_enforces_mattpocock_git_autonomy_source_wide(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    assets = (
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/first",
            local=".github/skills/mattpocock-first",
            canonical_name="mattpocock-first",
        ),
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/productivity/second",
            local=".github/skills/mattpocock-second",
            canonical_name="mattpocock-second",
        ),
    )
    for asset, body in zip(
        assets, ("First upstream body.\n", "Second upstream body.\n")
    ):
        skill = candidate / asset.local / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            f"---\nname: {asset.canonical_name}\n---\n{body}",
            encoding="utf-8",
        )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=assets,
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    assert first_changed == tuple(sorted(f"{asset.local}/SKILL.md" for asset in assets))
    assert second_changed == ()
    for asset in assets:
        content = (candidate / asset.local / "SKILL.md").read_text(encoding="utf-8")
        assert content.count("local-sync:mattpocock-git-autonomy:start") == 1
        assert content.count("local-sync:mattpocock-git-autonomy:end") == 1
        assert "may stage only changes owned by the current task" in content
        assert "Leave changes uncommitted and unpushed" in content
        assert "explicitly requests the specific commit or push action" in content


@pytest.mark.parametrize(
    ("canonical_name", "file_name", "legacy", "expected"),
    [
        (
            "mattpocock-setup-matt-pocock-skills",
            "issue-tracker-local.md",
            ".scratch/<feature>/",
            "tmp/.issues/<feature>/",
        ),
        (
            "mattpocock-triage",
            "OUT-OF-SCOPE.md",
            ".out-of-scope/<concept>.md",
            "tmp/.out-of-scope/<concept>.md",
        ),
        (
            "mattpocock-handoff",
            "SKILL.md",
            "tmp/handoff/",
            "tmp/.handoff/",
        ),
        (
            "mattpocock-teach",
            "SKILL.md",
            "./tmp/teach/<lesson-name>/",
            "./tmp/.teach/<lesson-name>/",
        ),
        (
            "mattpocock-improve-codebase-architecture",
            "HTML-REPORT.md",
            "./tmp/codebase-improve/",
            "./tmp/.codebase-improve/",
        ),
    ],
)
def test_normalization_rewrites_mattpocock_legacy_workspace_paths(
    tmp_path: Path,
    canonical_name: str,
    file_name: str,
    legacy: str,
    expected: str,
) -> None:
    candidate = tmp_path / "candidate"
    local = f".github/skills/{canonical_name}"
    target = candidate / local / file_name
    target.parent.mkdir(parents=True)
    target.write_text(f"Legacy workspace path: {legacy}\n", encoding="utf-8")
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream=f"skills/{canonical_name}",
        local=local,
        canonical_name=canonical_name,
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    assert f"{local}/{file_name}" in first_changed
    assert second_changed == ()
    content = target.read_text(encoding="utf-8")
    assert expected in content


def test_normalization_updates_wayfinder_contracts_without_changing_lifecycle(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/mattpocock-wayfinder"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    upstream_lifecycle = """\
## Invocation

### Chart the map

1. Name the destination.
2. Map the frontier.
3. Create the map and its ticket batch.

### Work through the map

1. Load the map.
2. Claim one ticket before any work.
3. Resolve that ticket only.
4. Record the resolution and update the map.
"""
    skill.write_text(
        upstream_lifecycle
        + "\nCapture findings on a throwaway `research/<name>` branch.\n\n"
        + "<!-- local-sync:wayfinder-critical-validation:start -->\n"
        + "Run the gate before every artifact.\n"
        + "<!-- local-sync:wayfinder-critical-validation:end -->\n\n"
        + "<!-- local-sync:wayfinder-grilling:start -->\n"
        + "Ask one question at a time.\n"
        + "<!-- local-sync:wayfinder-grilling:end -->\n",
        encoding="utf-8",
    )
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream="skills/engineering/wayfinder",
        local=local,
        canonical_name="mattpocock-wayfinder",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    wayfinder_content = skill.read_text(encoding="utf-8")
    normalized_text = " ".join(wayfinder_content.split())
    assert f"{local}/SKILL.md" in first_changed
    assert second_changed == ()
    assert wayfinder_content.startswith(upstream_lifecycle)
    assert "local-sync:wayfinder-workspace:start" in wayfinder_content
    assert "local-sync:wayfinder-workspace:end" in wayfinder_content
    assert (
        wayfinder_content.count("local-sync:wayfinder-critical-validation:start") == 1
    )
    assert wayfinder_content.count("local-sync:wayfinder-critical-validation:end") == 1
    assert "`/internal-gateway-critical-master`" in wayfinder_content
    assert "Counter-validate every material critique" in wayfinder_content
    assert "one analysis unit" in wayfinder_content
    assert "entire batch of content-producing writes" in normalized_text
    assert "ticket claim remains the first coordination action" in normalized_text
    assert "Do not rerun the critic against unchanged evidence" in normalized_text
    assert "Run the gate before every artifact." not in wayfinder_content
    assert wayfinder_content.count("local-sync:wayfinder-grilling:start") == 1
    assert wayfinder_content.count("local-sync:wayfinder-grilling:end") == 1
    assert "one numbered bulk block" in wayfinder_content
    for field in ("Question", "Recommendation", "Why", "Default if accepted"):
        assert f"`{field}`" in wayfinder_content
    assert "`tmp/.wayfinder/<analysis-slug>/`" in wayfinder_content
    assert "`tmp/.wayfinder/<analysis-slug>/map.md`" in wayfinder_content
    assert "`tmp/.wayfinder/<analysis-slug>/issues/`" in wayfinder_content
    assert "tracker-owned `tmp/.issues/`" not in wayfinder_content
    assert "throwaway `research/<name>` branch" not in wayfinder_content


def test_normalization_enforces_mattpocock_research_workspace_contract(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/mattpocock-research"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "Investigate the question and report the findings.\n", encoding="utf-8"
    )
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream="skills/engineering/research",
        local=local,
        canonical_name="mattpocock-research",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    research_content = skill.read_text(encoding="utf-8")
    assert f"{local}/SKILL.md" in first_changed
    assert second_changed == ()
    assert "local-sync:research-workspace:start" in research_content
    assert "local-sync:research-workspace:end" in research_content
    assert "`tmp/.research/YYYY-MM-DD-<slug>.md`" in research_content


def test_normalization_enforces_mattpocock_research_luna_delegation_contract(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/mattpocock-research"
    skill = candidate / local / "SKILL.md"
    metadata = candidate / local / "agents/openai.yaml"
    skill.parent.mkdir(parents=True)
    metadata.parent.mkdir(parents=True)
    skill.write_text(
        "Investigate the question and report the findings.\n", encoding="utf-8"
    )
    metadata.write_text(
        'interface:\n  display_name: "Research"\n'
        '  short_description: "Research from high-trust sources"\n',
        encoding="utf-8",
    )
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream="skills/engineering/research",
        local=local,
        canonical_name="mattpocock-research",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    research_content = skill.read_text(encoding="utf-8")
    metadata_content = metadata.read_text(encoding="utf-8")
    assert f"{local}/SKILL.md" in first_changed
    assert f"{local}/agents/openai.yaml" in first_changed
    assert second_changed == ()
    assert "local-sync:research-delegation:start" in research_content
    assert "local-sync:research-delegation:end" in research_content
    assert "`internal-luna-executor`" in research_content
    assert "self-contained brief" in research_content
    assert "report a blocker instead of switching to another agent" in research_content
    assert "local-sync:research-description:start" in metadata_content
    assert (
        'short_description: "Research from high-trust sources via Luna"'
        in metadata_content
    )
    assert yaml.safe_load(metadata_content)["interface"]["short_description"] == (
        "Research from high-trust sources via Luna"
    )


def test_normalization_enforces_mattpocock_handoff_workspace_contract(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/mattpocock-handoff"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "Write a handoff under tmp/handoff/. Do not duplicate content already "
        "captured in PRDs, plans, ADRs, issues, commits, diffs.\n",
        encoding="utf-8",
    )
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream="skills/productivity/handoff",
        local=local,
        canonical_name="mattpocock-handoff",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    handoff_content = skill.read_text(encoding="utf-8")
    assert f"{local}/SKILL.md" in first_changed
    assert second_changed == ()
    assert "local-sync:handoff-workspace:start" in handoff_content
    assert "local-sync:handoff-workspace:end" in handoff_content
    assert "`tmp/.handoff/`" in handoff_content
    assert (
        "Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead."
        in handoff_content
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
        "---\nname: brainstorming\n---\n"
        "Write to docs/superpowers.\n"
        "Use `superpowers:test-driven-development` first.\n"
        "Then use superpowers:verification-before-completion.\n",
        encoding="utf-8",
    )

    changed = normalize_candidate(_superpowers_resources(), candidate)

    assert changed == tuple(
        sorted(
            (
                ".github/skills/superpowers-brainstorming/SKILL.md",
                ".github/skills/superpowers-brainstorming/agents/openai.yaml",
            )
        )
    )
    content = skill.read_text(encoding="utf-8")
    assert "name: superpowers-brainstorming" in content
    assert "tmp/superpowers" in content
    assert "`superpowers-test-driven-development`" in content
    assert "superpowers-verification-before-completion" in content


def test_normalization_creates_human_only_brainstorming_metadata_idempotently(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    skill = candidate / ".github/skills/superpowers-brainstorming/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: brainstorming\n---\nAsk questions.\n",
        encoding="utf-8",
    )

    first_changed = normalize_candidate(_superpowers_resources(), candidate)
    second_changed = normalize_candidate(_superpowers_resources(), candidate)

    metadata = yaml.safe_load(
        (
            candidate / ".github/skills/superpowers-brainstorming/agents/openai.yaml"
        ).read_text(encoding="utf-8")
    )
    assert first_changed == tuple(
        sorted(
            (
                ".github/skills/superpowers-brainstorming/SKILL.md",
                ".github/skills/superpowers-brainstorming/agents/openai.yaml",
            )
        )
    )
    assert second_changed == ()
    assert metadata["interface"]["display_name"] == "Brainstorming"
    assert metadata["policy"]["allow_implicit_invocation"] is False
    frontmatter = yaml.safe_load(skill.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["disable-model-invocation"] is True


@pytest.mark.parametrize(
    "canonical_name",
    ("superpowers-brainstorming", "grill-me"),
)
def test_normalization_enforces_guided_bulk_questions_for_interview_skills(
    tmp_path: Path,
    canonical_name: str,
) -> None:
    candidate = tmp_path / "candidate"
    local = f".github/skills/{canonical_name}"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        f"---\nname: {canonical_name}\n---\nAsk clarifying questions one at a time.\n",
        encoding="utf-8",
    )
    asset = ManagedAsset(
        source="upstream",
        upstream=f"skills/{canonical_name}",
        local=local,
        canonical_name=canonical_name,
        invocation_policy=(
            InvocationPolicy(
                copilot_disable_model_invocation=True,
                codex_allow_implicit_invocation=False,
            )
            if canonical_name == "superpowers-brainstorming"
            else None
        ),
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="upstream",
                repository="https://example.com/upstream.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    content = skill.read_text(encoding="utf-8")
    expected_changed = [f"{local}/SKILL.md"]
    if canonical_name == "superpowers-brainstorming":
        expected_changed.append(f"{local}/agents/openai.yaml")
    assert first_changed == tuple(sorted(expected_changed))
    assert second_changed == ()
    assert content.count("Local guided-question contract") == 1
    assert "numbered bulk question blocks" in content
    assert "`Question`, `Recommendation`, `Why`, and `Default if accepted`" in content
    assert "Keep each question, recommendation, and reason brief" in content
    assert "overrides any earlier instruction to ask one question at a time" in content


def _policy_driven_resources(canonical_name: str, local: str) -> ManagedResources:
    asset = ManagedAsset(
        source="upstream",
        upstream=f"skills/{canonical_name}",
        local=local,
        canonical_name=canonical_name,
        invocation_policy=InvocationPolicy(
            copilot_disable_model_invocation=True,
            codex_allow_implicit_invocation=False,
        ),
    )
    return ManagedResources(
        sources=(
            ManagedSource(
                source_id="upstream",
                repository="https://example.com/upstream.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )


def test_normalization_applies_declared_invocation_policy_to_any_asset(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/example-human-only"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: example-human-only\n---\nAsk questions.\n",
        encoding="utf-8",
    )

    first_changed = normalize_candidate(
        _policy_driven_resources("example-human-only", local), candidate
    )
    second_changed = normalize_candidate(
        _policy_driven_resources("example-human-only", local), candidate
    )

    assert first_changed == tuple(
        sorted((f"{local}/SKILL.md", f"{local}/agents/openai.yaml"))
    )
    assert second_changed == ()
    frontmatter = yaml.safe_load(skill.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["disable-model-invocation"] is True
    metadata = yaml.safe_load(
        (candidate / local / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    assert metadata["policy"]["allow_implicit_invocation"] is False
    assert metadata["interface"]["display_name"] == "Example Human Only"


def test_normalization_without_invocation_policy_creates_no_codex_metadata(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/example"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: example\ndisable-model-invocation: true\n---\nBody.\n",
        encoding="utf-8",
    )

    changed = normalize_candidate(
        ManagedResources(
            sources=(
                ManagedSource(
                    source_id="upstream",
                    repository="https://example.com/upstream.git",
                    ref="a" * 40,
                    advertised_ref=None,
                    assets=(
                        ManagedAsset(
                            source="upstream",
                            upstream="skills/example",
                            local=local,
                            canonical_name="example",
                        ),
                    ),
                ),
            ),
            replacements=(),
            watchlist=(),
        ),
        candidate,
    )

    assert changed == (f"{local}/SKILL.md",)
    assert not (candidate / local / "agents/openai.yaml").exists()
    assert "disable-model-invocation" not in skill.read_text(encoding="utf-8")


def test_normalization_enforces_teach_workspace_without_upstream_text_coupling(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/mattpocock-teach"
    skill = candidate / local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: teach\n---\n"
        "# Changed upstream teaching guidance\n\n"
        "Upstream may reorganize every surrounding section.\n",
        encoding="utf-8",
    )
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream="skills/productivity/teach",
        local=local,
        canonical_name="mattpocock-teach",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    content = skill.read_text(encoding="utf-8")
    assert first_changed == (f"{local}/SKILL.md",)
    assert second_changed == ()
    assert content.count("local-sync:teach-workspace:start") == 1
    assert content.count("local-sync:teach-workspace:end") == 1
    assert "`./tmp/.teach/<lesson-name>/`" in content
    assert "Upstream may reorganize every surrounding section." in content


def test_normalization_enforces_codebase_improvement_workspace_for_all_artifacts(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    local = ".github/skills/mattpocock-improve-codebase-architecture"
    skill_dir = candidate / local
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: improve-codebase-architecture\n---\n"
        "# Changed upstream workflow\n\nCreate architecture artifacts as needed.\n",
        encoding="utf-8",
    )
    (skill_dir / "HTML-REPORT.md").write_text(
        "# Changed upstream report guidance\n\nWrite the report wherever appropriate.\n",
        encoding="utf-8",
    )
    asset = ManagedAsset(
        source="mattpocock-skills",
        upstream="skills/engineering/improve-codebase-architecture",
        local=local,
        canonical_name="mattpocock-improve-codebase-architecture",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    expected_changed = (
        f"{local}/HTML-REPORT.md",
        f"{local}/SKILL.md",
    )
    assert first_changed == expected_changed
    assert second_changed == ()
    for file_name in ("SKILL.md", "HTML-REPORT.md"):
        content = (skill_dir / file_name).read_text(encoding="utf-8")
        assert content.count("local-sync:codebase-improve-workspace:start") == 1
        assert content.count("local-sync:codebase-improve-workspace:end") == 1
        assert "`./tmp/.codebase-improve/`" in content
        assert "every generated artifact" in content

    skill_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    report_content = (skill_dir / "HTML-REPORT.md").read_text(encoding="utf-8")

    for content in (skill_content, report_content):
        assert "local-sync:codebase-improve-pre-render" not in content
        assert "Local pre-render analysis checkpoint" not in content


def test_normalization_rewrites_declared_mattpocock_skill_references(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    skill = candidate / ".github/skills/mattpocock-tdd/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: tdd\n---\n"
        "Use /domain-modeling, /tdd, /grill-with-docs, and /grilling.\n"
        "See `tdd` and /unmanaged when needed.\n",
        encoding="utf-8",
    )

    changed = normalize_candidate(_mattpocock_resources(), candidate)

    assert changed == (".github/skills/mattpocock-tdd/SKILL.md",)
    content = skill.read_text(encoding="utf-8")
    assert "name: mattpocock-tdd" in content
    assert "/mattpocock-tdd" in content
    assert "`mattpocock-tdd`" in content
    assert "/mattpocock-grill-with-docs" in content
    assert "/grill-me" in content
    assert "/mattpocock-domain-modeling" in content
    assert "/grilling" not in content
    assert "/domain-modeling" not in content
    assert "/unmanaged" in content


def test_normalization_removes_unsupported_invocation_field_from_all_mattpocock_skills(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    assets = (
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/wayfinder",
            local=".github/skills/mattpocock-wayfinder",
            canonical_name="mattpocock-wayfinder",
        ),
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/domain-modeling",
            local=".github/skills/mattpocock-domain-modeling",
            canonical_name="mattpocock-domain-modeling",
        ),
    )
    for asset in assets:
        skill = candidate / asset.local / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            "---\n"
            f"name: {Path(asset.upstream).name}\n"
            "description: Test skill.\n"
            "disable-model-invocation: true\n"
            "---\n"
            "Use /domain-modeling when needed.\n",
            encoding="utf-8",
        )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="mattpocock-skills",
                repository="https://example.com/mattpocock/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=assets,
                rewrite_skill_references=True,
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    first_changed = normalize_candidate(resources, candidate)
    second_changed = normalize_candidate(resources, candidate)

    assert first_changed == tuple(sorted(f"{asset.local}/SKILL.md" for asset in assets))
    assert second_changed == ()
    for asset in assets:
        content = (candidate / asset.local / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = yaml.safe_load(content.split("---", 2)[1])
        assert set(frontmatter) == {"name", "description"}
        assert "/mattpocock-domain-modeling" in content


def test_normalization_removes_unsupported_invocation_field_from_all_managed_skills(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    asset = ManagedAsset(
        source="external-skills",
        upstream="skills/example",
        local=".github/skills/external-example",
        canonical_name="external-example",
    )
    skill = candidate / asset.local / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\n"
        "name: example\n"
        "description: Test skill.\n"
        "disable-model-invocation: true\n"
        "---\n"
        "Use the skill.\n",
        encoding="utf-8",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="external-skills",
                repository="https://example.com/external/skills.git",
                ref="a" * 40,
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    changed = normalize_candidate(resources, candidate)

    assert changed == (".github/skills/external-example/SKILL.md",)
    content = skill.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])
    assert set(frontmatter) == {"name", "description"}
    assert frontmatter["name"] == "external-example"


def test_materialize_candidate_copies_upstream_to_local(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    sources_root = workspace / "sources"
    source_checkout = sources_root / "test-source" / "skills" / "example"
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
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset,),
    )
    _write_source_metadata(sources_root, source)
    resources = ManagedResources(sources=(source,), replacements=(), watchlist=())

    candidate = tmp_path / "candidate"
    materialize_candidate(resources, workspace, candidate)

    target = candidate / ".github/skills/example/SKILL.md"
    assert target.exists()
    assert "upstream-name" in target.read_text(encoding="utf-8")


def test_materialize_candidate_rejects_mismatched_prepared_ref(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    sources_root = workspace / "sources"
    source_checkout = sources_root / "test-source" / "skills" / "example"
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
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset,),
    )
    _write_source_metadata(sources_root, source)
    metadata_path = sources_root / "test-source" / ".external-resource-source.tsv"
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8").replace("a" * 40, "b" * 40),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="ref"):
        materialize_candidate(
            ManagedResources(sources=(source,), replacements=(), watchlist=()),
            workspace,
            tmp_path / "candidate",
        )
    assert not (tmp_path / "candidate" / ".github/skills/example/SKILL.md").exists()


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


def test_override_hash_normalizes_text_whitespace(tmp_path: Path) -> None:
    target_rel = ".github/skills/test/SKILL.md"
    target = tmp_path / target_rel
    target.parent.mkdir(parents=True)
    target.write_bytes(b"---\r\nname: test  \r\n---\r\nBody.  \r\n\r\n")
    override = ImportedOverride(
        override_id="test-override",
        target_path=target_rel,
        patch_path="patches/test.patch",
        apply_strategy="git-apply",
        expected_content_hash=_sha256("---\nname: test\n---\nBody.\n"),
    )

    verify_override_hash(tmp_path, override)


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


def test_build_candidate_patch_detects_repo_vs_candidate_diff(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    target = repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\nOld content.\n", encoding="utf-8")
    _commit_all(repo)

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    cand_target = candidate / ".github/skills/example/SKILL.md"
    cand_target.parent.mkdir(parents=True)
    cand_target.write_text("---\nname: example\n---\nNew content.\n", encoding="utf-8")

    asset = ManagedAsset(
        source="test-source",
        upstream="skills/example",
        local=".github/skills/example",
        canonical_name="example",
    )
    resources = ManagedResources(
        sources=(
            ManagedSource(
                source_id="test-source",
                repository="https://example.com/repo.git",
                ref="abc",
                advertised_ref=None,
                assets=(asset,),
            ),
        ),
        replacements=(),
        watchlist=(),
    )

    patch = _build_candidate_patch(repo, candidate, resources)
    assert patch.strip(), "patch must be non-empty when candidate differs from repo"
    assert "New content." in patch


def test_materialize_candidate_uses_explicit_source_root(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    external_sources = tmp_path / "external-sources"
    source_checkout = external_sources / "test-source" / "skills" / "example"
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
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset,),
    )
    _write_source_metadata(external_sources, source)
    resources = ManagedResources(sources=(source,), replacements=(), watchlist=())

    candidate = tmp_path / "candidate"
    materialize_candidate(
        resources, workspace, candidate, sources_root=external_sources
    )

    target = candidate / ".github/skills/example/SKILL.md"
    assert target.exists()
    assert "upstream-name" in target.read_text(encoding="utf-8")


def test_materialize_candidate_reports_all_missing_upstreams(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    sources_root = tmp_path / "sources"
    sources_root.mkdir()

    asset_a = ManagedAsset(
        source="src-a",
        upstream="skills/a",
        local=".github/skills/a",
        canonical_name="a",
    )
    asset_b = ManagedAsset(
        source="src-b",
        upstream="skills/b",
        local=".github/skills/b",
        canonical_name="b",
    )
    source_a = ManagedSource(
        source_id="src-a",
        repository="https://example.com/a.git",
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset_a,),
    )
    source_b = ManagedSource(
        source_id="src-b",
        repository="https://example.com/b.git",
        ref="b" * 40,
        advertised_ref=None,
        assets=(asset_b,),
    )
    _write_source_metadata(sources_root, source_a)
    _write_source_metadata(sources_root, source_b)
    resources = ManagedResources(
        sources=(source_a, source_b),
        replacements=(),
        watchlist=(),
    )

    candidate = tmp_path / "candidate"
    with pytest.raises(ValueError, match="Missing upstream paths") as exc_info:
        materialize_candidate(
            resources, workspace, candidate, sources_root=sources_root
        )
    message = str(exc_info.value)
    assert "src-a" in message
    assert "src-b" in message


def test_materialize_candidate_reports_expected_source_root(tmp_path: Path) -> None:
    resources = load_managed_resources(
        REPO_ROOT
        / ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
    )
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    candidate = tmp_path / "candidate"

    with pytest.raises(ValueError) as excinfo:
        materialize_candidate(resources, workspace, candidate)

    message = str(excinfo.value)
    assert "Missing prepared source metadata:" in message
    assert "Run prepare before plan/apply." in message


def test_load_overrides_rejects_missing_patch_file(tmp_path: Path) -> None:
    registry = tmp_path / "overrides.yaml"
    registry.write_text(
        """\
version: 1
overrides:
  - id: test-override
    target_path: .github/skills/test/SKILL.md
    patch_path: patches/nonexistent.patch
    apply_strategy: git-apply
    expected_content_hash: abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
""",
        encoding="utf-8",
    )

    overrides = load_overrides(registry)
    bundle_root = tmp_path
    with pytest.raises(ValueError, match="Override patch missing"):
        validate_override_patches(overrides, bundle_root)


def test_override_3way_replay_uses_real_git_repo(
    candidate_repo: Path,
) -> None:
    target = candidate_repo / ".github/skills/test/SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\nname: test\n---\nOriginal.\n", encoding="utf-8")
    _commit_all(candidate_repo)

    patch_dir = candidate_repo / "patches"
    patch_dir.mkdir(exist_ok=True)
    patch_path = patch_dir / "test-3way.patch"

    target.write_text("---\nname: test\n---\nPatched.\n", encoding="utf-8")
    result = subprocess.run(
        ["git", "diff", "--", ".github/skills/test/SKILL.md"],
        cwd=candidate_repo,
        capture_output=True,
        text=True,
        check=True,
    )
    patch_path.write_text(result.stdout, encoding="utf-8")
    target.write_text("---\nname: test\n---\nOriginal.\n", encoding="utf-8")

    override = ImportedOverride(
        override_id="test-3way",
        target_path=".github/skills/test/SKILL.md",
        patch_path=patch_path.relative_to(candidate_repo).as_posix(),
        apply_strategy="git-apply-3way",
        expected_content_hash=_sha256("---\nname: test\n---\nPatched.\n"),
    )

    results = replay_overrides(candidate_repo, (override,), patches_root=candidate_repo)

    assert len(results) == 1
    assert results[0].status == "applied"
    assert "Patched." in target.read_text(encoding="utf-8")


def test_grill_with_docs_normalizes_to_mattpocock_wrapper_delegating_to_grill_me(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    sources_root = workspace / "sources"
    grill_dir = (
        sources_root
        / "mattpocock-skills"
        / "skills"
        / "engineering"
        / "grill-with-docs"
    )
    grill_dir.mkdir(parents=True)
    (grill_dir / "SKILL.md").write_text(
        "---\nname: grill-with-docs\n---\n"
        "Run a `/grilling` session, using the `/domain-modeling` skill.\n",
        encoding="utf-8",
    )
    domain_dir = (
        sources_root
        / "mattpocock-skills"
        / "skills"
        / "engineering"
        / "domain-modeling"
    )
    domain_dir.mkdir(parents=True)
    (domain_dir / "SKILL.md").write_text(
        "---\nname: domain-modeling\n---\nDomain modeling.\n",
        encoding="utf-8",
    )

    assets = (
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/grill-with-docs",
            local=".github/skills/mattpocock-grill-with-docs",
            canonical_name="mattpocock-grill-with-docs",
        ),
        ManagedAsset(
            source="mattpocock-skills",
            upstream="skills/engineering/domain-modeling",
            local=".github/skills/mattpocock-domain-modeling",
            canonical_name="mattpocock-domain-modeling",
        ),
    )
    source = ManagedSource(
        source_id="mattpocock-skills",
        repository="https://github.com/mattpocock/skills.git",
        ref="abc123",
        advertised_ref=None,
        assets=assets,
        rewrite_skill_references=True,
    )
    replacement = TextReplacement(
        source="mattpocock-skills",
        old="/grilling",
        new="/grill-me",
    )
    resources = ManagedResources(
        sources=(source,), replacements=(replacement,), watchlist=()
    )
    _write_source_metadata(sources_root, source)

    candidate = tmp_path / "candidate"
    materialize_candidate(resources, workspace, candidate)
    normalize_candidate(resources, candidate)

    wrapper = candidate / ".github/skills/mattpocock-grill-with-docs/SKILL.md"
    assert wrapper.exists()
    content = wrapper.read_text(encoding="utf-8")
    assert "name: mattpocock-grill-with-docs" in content
    assert "/grill-me" in content
    assert "/mattpocock-domain-modeling" in content
    assert "/grilling" not in content
    assert "/mattpocock-grill-with-docs session" not in content


def test_undeclared_backtick_reference_is_left_unchanged(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    skill = candidate / ".github/skills/mattpocock-domain-modeling/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: domain-modeling\n---\n"
        "Use `domain-modeling` for vocabulary and `tdd` for the loop.\n"
        "See /domain-modeling for the command form.\n",
        encoding="utf-8",
    )

    normalize_candidate(_mattpocock_resources(), candidate)

    content = skill.read_text(encoding="utf-8")
    assert "`domain-modeling`" in content
    assert "`mattpocock-domain-modeling`" not in content
    assert "`mattpocock-tdd`" in content
    assert "/mattpocock-domain-modeling" in content


def test_normalize_candidate_adds_shebang_only_to_opted_in_executable_python(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    asset_dir = candidate / ".github/skills/anthropic-docx"
    scripts_dir = asset_dir / "scripts"
    scripts_dir.mkdir(parents=True)

    missing_shebang = scripts_dir / "missing.py"
    missing_shebang.write_text('"""Tool."""\n', encoding="utf-8")
    missing_shebang.chmod(0o755)

    existing_shebang = scripts_dir / "existing.py"
    existing_shebang.write_text(
        "#!/usr/bin/python3\nprint('ok')\n",
        encoding="utf-8",
    )
    existing_shebang.chmod(0o755)

    non_executable = scripts_dir / "library.py"
    non_executable.write_text('"""Library."""\n', encoding="utf-8")
    non_executable.chmod(0o644)

    shell_script = scripts_dir / "tool.sh"
    shell_script.write_text("set -eu\n", encoding="utf-8")
    shell_script.chmod(0o755)

    asset = ManagedAsset(
        source="anthropic-skills",
        upstream="skills/docx",
        local=".github/skills/anthropic-docx",
        canonical_name="anthropic-docx",
    )
    source = ManagedSource(
        source_id="anthropic-skills",
        repository="https://github.com/anthropics/skills.git",
        ref="a" * 40,
        advertised_ref=None,
        assets=(asset,),
        ensure_python_shebangs=True,
    )
    resources = ManagedResources(
        sources=(source,),
        replacements=(),
        watchlist=(),
    )

    changed = normalize_candidate(resources, candidate)

    assert missing_shebang.read_text(encoding="utf-8") == (
        '#!/usr/bin/env python3\n"""Tool."""\n'
    )
    assert existing_shebang.read_text(encoding="utf-8").startswith(
        "#!/usr/bin/python3\n"
    )
    assert non_executable.read_text(encoding="utf-8") == '"""Library."""\n'
    assert shell_script.read_text(encoding="utf-8") == "set -eu\n"
    assert changed == (".github/skills/anthropic-docx/scripts/missing.py",)


def _example_asset() -> ManagedAsset:
    return ManagedAsset(
        source="test-source",
        upstream="skills/example",
        local=".github/skills/example",
        canonical_name="example",
    )


def test_renamed_managed_file_is_reported_once_with_new_path(git_repo: Path) -> None:
    target = git_repo / ".github/skills/example"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("---\nname: example\n---\n", encoding="utf-8")
    _commit_all(git_repo)

    _run_git(
        git_repo,
        ["mv", ".github/skills/example/SKILL.md", ".github/skills/example/RENAMED.md"],
    )

    dirty = find_dirty_targets(git_repo, (_example_asset(),))

    assert dirty == (".github/skills/example/RENAMED.md",)
