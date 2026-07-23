import json
import subprocess
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


def _write_source_metadata_for_fixture(
    sources_root: Path, source_id: str, repository: str, ref: str, upstream: str
) -> None:
    source_dir = sources_root / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    import hashlib
    digest = hashlib.sha256(upstream.encode("utf-8")).hexdigest()
    tsv = (
        f"source_id\trepository\tref\tpaths_sha256\n"
        f"{source_id}\t{repository}\t{ref}\t{digest}\n"
    )
    (source_dir / ".external-resource-source.tsv").write_text(
        tsv, encoding="utf-8"
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
    _run_git(repo, ["commit", "-m", "snapshot", "--allow-empty"])


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


def test_audit_does_not_fetch_or_write(repo_root: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "audit",
            "--repo-root",
            str(repo_root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "audit"
    assert payload["repository_changed"] is False
    assert payload["managed_assets"] == 46


def test_apply_refuses_dirty_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    mini_manifest = tmp_path / "manifest.yaml"
    mini_manifest.write_text(
        """\
version: 1
sources:
  test-source:
    repository: https://example.com/repo.git
    ref: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )

    mini_overrides = tmp_path / "overrides.yaml"
    mini_overrides.write_text(
        """\
version: 1
overrides: []
""",
        encoding="utf-8",
    )

    target = repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\n", encoding="utf-8")
    _commit_all(repo)
    target.write_text("---\nname: locally-edited\n---\n", encoding="utf-8")

    workspace = tmp_path / "external-workspace"
    workspace.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "apply",
            "--repo-root",
            str(repo),
            "--workspace",
            str(workspace),
            "--manifest",
            str(mini_manifest),
            "--overrides",
            str(mini_overrides),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2


def test_apply_reports_repository_changed_when_candidate_diff_applies(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    manifest_src = tmp_path / "manifest.yaml"
    manifest_src.write_text(
        """\
version: 1
sources:
  test-source:
    repository: https://example.com/repo.git
    ref: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )

    overrides_src = tmp_path / "overrides.yaml"
    overrides_src.write_text(
        """\
version: 1
overrides: []
""",
        encoding="utf-8",
    )

    target = repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\nOld content.\n", encoding="utf-8")
    _commit_all(repo)

    workspace = tmp_path / "external-workspace"
    workspace.mkdir()
    source_dir = workspace / "sources" / "test-source" / "skills" / "example"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text(
        "---\nname: example\n---\nNew content.\n", encoding="utf-8"
    )
    _write_source_metadata_for_fixture(
        workspace / "sources",
        "test-source",
        "https://example.com/repo.git",
        "a" * 40,
        "skills/example",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "apply",
            "--repo-root",
            str(repo),
            "--workspace",
            str(workspace),
            "--manifest",
            str(manifest_src),
            "--overrides",
            str(overrides_src),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["repository_changed"] is True
    assert "New content." in target.read_text(encoding="utf-8")


def test_plan_uses_explicit_source_root(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    manifest_src = tmp_path / "manifest.yaml"
    manifest_src.write_text(
        """\
version: 1
sources:
  test-source:
    repository: https://example.com/repo.git
    ref: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )

    overrides_src = tmp_path / "overrides.yaml"
    overrides_src.write_text(
        """\
version: 1
overrides: []
""",
        encoding="utf-8",
    )

    target = repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\nOld content.\n", encoding="utf-8")
    _commit_all(repo)

    workspace = tmp_path / "external-workspace"
    workspace.mkdir()
    external_sources_root = tmp_path / "external-sources"
    external_sources = (
        external_sources_root / "test-source" / "skills" / "example"
    )
    external_sources.mkdir(parents=True)
    (external_sources / "SKILL.md").write_text(
        "---\nname: example\n---\nNew content.\n", encoding="utf-8"
    )
    _write_source_metadata_for_fixture(
        external_sources_root,
        "test-source",
        "https://example.com/repo.git",
        "a" * 40,
        "skills/example",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "plan",
            "--repo-root",
            str(repo),
            "--workspace",
            str(workspace),
            "--source-root",
            str(external_sources_root),
            "--manifest",
            str(manifest_src),
            "--overrides",
            str(overrides_src),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "plan"


def test_plan_then_apply_end_to_end(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    manifest_src = tmp_path / "manifest.yaml"
    manifest_src.write_text(
        """\
version: 1
sources:
  test-source:
    repository: https://example.com/repo.git
    ref: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )

    overrides_src = tmp_path / "overrides.yaml"
    overrides_src.write_text(
        """\
version: 1
overrides: []
""",
        encoding="utf-8",
    )

    target = repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\nOld content.\n", encoding="utf-8")
    _commit_all(repo)

    workspace = tmp_path / "external-workspace"
    workspace.mkdir()
    source_dir = workspace / "sources" / "test-source" / "skills" / "example"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text(
        "---\nname: example\n---\nNew content.\n", encoding="utf-8"
    )
    _write_source_metadata_for_fixture(
        workspace / "sources",
        "test-source",
        "https://example.com/repo.git",
        "a" * 40,
        "skills/example",
    )

    common_args = [
        sys.executable,
        str(SCRIPT_DIR / "sync_external_resources.py"),
        "--repo-root",
        str(repo),
        "--workspace",
        str(workspace),
        "--manifest",
        str(manifest_src),
        "--overrides",
        str(overrides_src),
        "--format",
        "json",
    ]

    plan_result = subprocess.run(
        [*common_args, "plan"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert plan_result.returncode == 0, plan_result.stderr
    plan_payload = json.loads(plan_result.stdout)
    assert plan_payload["repository_changed"] is False

    apply_result = subprocess.run(
        [*common_args, "apply"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert apply_result.returncode == 0, apply_result.stderr
    apply_payload = json.loads(apply_result.stdout)
    assert apply_payload["repository_changed"] is True
    assert "New content." in target.read_text(encoding="utf-8")


def test_audit_tsv_contains_summary_mode_row(repo_root: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "audit",
            "--repo-root",
            str(repo_root),
            "--format",
            "tsv",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "summary\tmode\tok\taudit" in result.stdout


def test_prepare_cold_then_warm_against_fixture(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])
    _commit_all(repo)

    remote = tmp_path / "remote.git"
    remote.mkdir()
    _run_git(remote, ["init", "--bare"])
    _run_git(remote, ["config", "uploadpack.allowReachableSHA1InWant", "true"])
    _run_git(remote, ["config", "uploadpack.allowFilter", "true"])

    work = tmp_path / "work"
    work.mkdir()
    _run_git(work, ["init"])
    _run_git(work, ["config", "user.email", "test@test.com"])
    _run_git(work, ["config", "user.name", "Test"])

    skill_dir = work / "skills" / "example"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: example\n---\nHello.\n", encoding="utf-8"
    )

    decoy = work / "decoy.bin"
    decoy.write_bytes(b"\x00" * 1024)

    _commit_all(work)
    sha_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=work,
        capture_output=True,
        text=True,
        check=True,
    )
    commit_sha = sha_result.stdout.strip()
    _run_git(work, ["remote", "add", "origin", str(remote)])
    _run_git(work, ["push", "origin", "HEAD:refs/heads/main"])

    manifest_src = tmp_path / "manifest.yaml"
    manifest_src.write_text(
        f"""\
version: 1
sources:
  test-source:
    repository: {remote}
    ref: {commit_sha}
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )
    overrides_src = tmp_path / "overrides.yaml"
    overrides_src.write_text("version: 1\noverrides: []\n", encoding="utf-8")

    workspace = tmp_path / "external-workspace"
    workspace.mkdir()

    common_args = [
        sys.executable,
        str(SCRIPT_DIR / "sync_external_resources.py"),
        "--repo-root",
        str(repo),
        "--workspace",
        str(workspace),
        "--manifest",
        str(manifest_src),
        "--overrides",
        str(overrides_src),
        "--format",
        "tsv",
    ]

    first = subprocess.run(
        [*common_args, "prepare"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    assert "source\ttest-source" in first.stdout
    assert "metric\ttest-source\tmaterialized_files" in first.stdout

    snapshot_skill = workspace / "sources" / "test-source" / "skills" / "example" / "SKILL.md"
    assert snapshot_skill.exists()
    assert not (workspace / "sources" / "test-source" / "decoy.bin").exists()

    second = subprocess.run(
        [*common_args, "prepare"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert second.returncode == 0, second.stderr
    assert "source\ttest-source\tcached" in second.stdout


def test_owner_docs_state_prepare_is_the_only_network_mode(
    repo_root: Path,
) -> None:
    skill_md = repo_root / ".github/skills/local-agent-sync-external-resources/SKILL.md"
    agent_md = repo_root / ".github/agents/local-sync-external-resources.agent.md"
    texts = []
    for path in (skill_md, agent_md):
        if path.exists():
            texts.append(path.read_text(encoding="utf-8"))
    combined = "\n".join(texts)

    if not combined:
        pytest.skip("Owner docs not yet written")

    for phrase in (
        "prepare",
        "offline",
        "pinned",
        "no package",
    ):
        assert phrase.lower() in combined.lower(), (
            f"Owner docs must mention {phrase!r}"
        )


def test_bundle_exposes_one_public_cli(repo_root: Path) -> None:
    scripts = repo_root / ".github/skills/local-agent-sync-external-resources/scripts"
    public_scripts = sorted(
        path.name for path in scripts.glob("*.py") if not path.name.endswith("_core.py")
    )

    assert public_scripts == ["sync_external_resources.py"]


def test_audit_reports_dirty_targets_but_stays_zero_exit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    manifest_src = tmp_path / "manifest.yaml"
    manifest_src.write_text(
        """\
version: 1
sources:
  test-source:
    repository: https://example.com/repo.git
    ref: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )

    overrides_src = tmp_path / "overrides.yaml"
    overrides_src.write_text("version: 1\noverrides: []\n", encoding="utf-8")

    target = repo / ".github/skills/example/SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("---\nname: example\n---\n", encoding="utf-8")
    _commit_all(repo)
    target.write_text("---\nname: locally-edited\n---\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "audit",
            "--repo-root",
            str(repo),
            "--manifest",
            str(manifest_src),
            "--overrides",
            str(overrides_src),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["blockers"] == [
        "dirty managed targets: .github/skills/example/SKILL.md"
    ]


def test_plan_missing_sources_names_explicit_source_root(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@test.com"])
    _run_git(repo, ["config", "user.name", "Test"])

    manifest_src = tmp_path / "manifest.yaml"
    manifest_src.write_text(
        """\
version: 1
sources:
  test-source:
    repository: https://example.com/repo.git
    ref: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    assets:
      - upstream: skills/example
        local: .github/skills/example
        canonical_name: example
watchlist: []
""",
        encoding="utf-8",
    )
    overrides_src = tmp_path / "overrides.yaml"
    overrides_src.write_text("version: 1\noverrides: []\n", encoding="utf-8")

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source_root = tmp_path / "prepared-sources"
    source_root.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "sync_external_resources.py"),
            "plan",
            "--repo-root",
            str(repo),
            "--workspace",
            str(workspace),
            "--source-root",
            str(source_root),
            "--manifest",
            str(manifest_src),
            "--overrides",
            str(overrides_src),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert str(source_root) in result.stderr + result.stdout


def test_agent_and_skill_do_not_route_to_unneeded_skills(repo_root: Path) -> None:
    paths = (
        repo_root / ".github/agents/local-sync-external-resources.agent.md",
        repo_root / ".github/skills/local-agent-sync-external-resources/SKILL.md",
    )
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in paths if path.exists()
    )

    if not text:
        pytest.skip("Agent or skill file not yet rewritten")

    for forbidden in (
        "openai-skill-creator",
        "internal-skill-creator",
        "internal-agent-creator",
        "internal-gateway-idea",
        "internal-copilot-docs-research",
        "internal-copilot-audit",
    ):
        assert forbidden not in text
