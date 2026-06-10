from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import sync_home_ai_resources


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def initialize_source_repo(root: Path) -> None:
    write_file(root / "AGENTS.md", "# AGENTS\n")
    write_file(
        root / ".github/skills/demo-skill/SKILL.md",
        "---\n"
        "name: demo-skill\n"
        "description: Use when a demo home-sync skill is needed.\n"
        "---\n\n"
        "# Demo Skill\n\n"
        "## When to use\n\n"
        "- Use when a demo home-sync skill is needed.\n",
    )
    write_file(
        root / ".github/skills/demo-skill/agents/openai.yaml",
        "interface:\n"
        '  display_name: "Demo Skill"\n'
        '  short_description: "Portable demo skill bundle"\n'
        '  default_prompt: "Use $demo-skill for demo work."\n',
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-install-ai-resources/references/runtime-support-matrix.yaml",
        "version: 1\n"
        "rows:\n"
        "  - target: skills\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: ~/.agents/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Shared skill support.\n"
        "  - target: codex\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: ~/.codex/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Codex direct-copy skill support.\n"
        "  - target: opencode\n"
        "    resource_family: skills\n"
        "    support_level: User-provided / To verify\n"
        "    home_path: ~/.config/opencode/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: false\n"
        "    evidence: []\n"
        "    notes: Undocumented support.\n",
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml",
        "version: 1\n"
        "defaults:\n"
        "  include_internal_skills: false\n"
        "  include_local_skills: false\n"
        "  include_unlisted_skills: false\n"
        "resources:\n"
        "  - resource_id: demo-skill\n"
        "    source_family: skills\n"
        "    source_path: .github/skills/demo-skill\n"
        "    include_targets:\n"
        "      - codex\n"
        "      - opencode\n"
        "    target_support: Documented\n"
        "    notes: Demo bundle.\n",
    )


def test_main_plan_emits_json_for_selected_targets(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="json",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "plan"
    assert payload["selected_targets"] == ["skills"]
    assert str(home_root / ".agents/skills") in payload["missing_dirs"]
    assert str(home_root / ".codex/agents") not in payload["missing_dirs"]


def test_main_plan_emits_compact_projection_for_selected_targets(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="compact",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "plan"
    assert "status" in payload
    assert payload["selected_targets_count"] == 1
    assert payload["retired_targets_count"] == 0
    assert payload["source_resources_considered"] >= 1
    assert "operations" not in payload
    assert "copied" not in payload
    assert "skipped" not in payload
    assert "blocked" not in payload
    assert "conflicts" not in payload
    assert "missing_dirs" not in payload
    assert "state_path" in payload
    assert "manifest_path" not in payload


def test_main_apply_blocks_docs_unverified_targets(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="apply",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="opencode",
            retire_targets="",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="json",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["mode"] == "apply"
    assert payload["blocked_codes"] == ["docs-unverified"]


def test_bisync_plan_json_output(monkeypatch, tmp_path: Path, capsys) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    source_root.mkdir()
    home_root.mkdir()
    write_file(source_root / ".gitkeep", "")
    (source_root / ".github" / "skills").mkdir(parents=True, exist_ok=True)
    (home_root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "add", "-A"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )

    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="bisync",
            bisync_command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            format="json",
        ),
    )

    sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert "drifts" in payload
    assert "next_action" in payload
    assert "blocked_codes" in payload
    assert "action" in payload["next_action"]


def test_bisync_plan_emits_compact_projection(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    source_root.mkdir()
    home_root.mkdir()
    write_file(source_root / ".github/skills/repo-only/SKILL.md", "# Repo only\n")
    write_file(home_root / ".agents/skills/home-only/SKILL.md", "# Home only\n")
    (source_root / ".github" / "skills").mkdir(parents=True, exist_ok=True)
    (home_root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "add", "-A"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=True,
    )

    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="bisync",
            bisync_command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            format="compact",
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["mode"] == "plan"
    assert "status" in payload
    assert payload["drift_total"] == 2
    assert payload["direction_counts"] == {"repo_to_home": 0, "home_to_repo": 0}
    assert payload["bucket_counts"] == {
        "only_repo": 1,
        "only_home": 1,
        "equal_mtime": 0,
    }
    assert payload["changed_resources"] == [
        {
            "blocked_codes": ["bisync-only-home"],
            "skill": "home-only",
            "type": "only-home",
        },
        {
            "blocked_codes": ["bisync-only-repo"],
            "skill": "repo-only",
            "type": "only-repo",
        },
    ]
    assert "drifts" not in payload
    assert "state_path" not in payload


def test_bisync_apply_returns_nonzero_on_blockers(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    source_root.mkdir()
    home_root.mkdir()
    (source_root / ".github" / "skills").mkdir(parents=True, exist_ok=True)
    (home_root / ".agents" / "skills").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="bisync",
            bisync_command="apply",
            source_root=str(source_root),
            home_root=str(home_root),
            format="json",
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["next_action"]["allowed"] is False


def test_plan_next_action_present(monkeypatch, tmp_path: Path, capsys) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="codex",
            retire_targets="",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="json",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "next_action" in payload
    assert "next_step" in payload
    assert "action" in payload["next_action"]
    assert "allowed" in payload["next_action"]
    assert "requires_explicit_approval" in payload["next_action"]


def test_main_plan_blocks_overlap_between_active_and_retired_targets(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="codex,claude",
            retire_targets="claude",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="json",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["blocked_codes"] == ["retire-target-overlap"]
    assert payload["retired_targets"] == ["claude"]


def test_skill_bundle_default_targets_focus_on_shared_skills(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="text",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Targets: skills" in output
    assert ".agents/skills" in output
    assert ".codex/agents" not in output


def test_skill_runbook_distinguishes_install_and_bisync_lanes() -> None:
    skill_path = (
        Path(__file__).resolve().parent
        / "../.github/skills/local-agent-sync-install-ai-resources/SKILL.md"
    ).resolve()
    content = skill_path.read_text(encoding="utf-8")

    assert "## Deterministic Operator Protocol" in content
    assert "Install sync is unidirectional: repo -> home only." in content
    assert "default `skills` target" in content
    assert (
        "The `bisync` lane provides explicit bidirectional synchronization" in content
    )
    assert "Do not infer the mode, do not skip blockers" in content
    assert "next_action` as user approval for `apply`" in content
    assert "## Reporting Contract" in content
    assert "table-first report" in content
    assert "planned-changes table" in content
    assert "actions-performed table" in content
    assert "remove it manually so sync can restore the source-of-truth version" not in (
        content.lower()
    )
    assert "routine recovery step" in content
    assert "non-thinking" not in content.lower()


def test_sync_contract_documents_verified_bisync_reconciliation() -> None:
    contract_path = (
        Path(__file__).resolve().parent
        / "../.github/skills/local-agent-sync-install-ai-resources/references/sync-contract.md"
    ).resolve()
    error_codes_path = (
        Path(__file__).resolve().parent
        / "../.github/skills/local-agent-sync-install-ai-resources/references/error-codes.md"
    ).resolve()
    contract_content = contract_path.read_text(encoding="utf-8")
    error_codes_content = error_codes_path.read_text(encoding="utf-8")

    assert "stale `target-modified-managed` blocker" in contract_content
    assert "bisync-manifest-reconcile-failed" in contract_content
    assert "Text reports must use a table-first layout" in contract_content
    assert "### Plan, Audit, And Bisync Plan Report" in contract_content
    assert (
        "| Resource or path | Lane | Planned action | Why this will change | Evidence or winner |"
        in contract_content
    )
    assert (
        "| Resource or path | Action performed | Why it was done | Result | Verification |"
        in contract_content
    )
    assert "bisync-manifest-reconcile-failed" in error_codes_content
    assert "combining the `Meaning` and `Rationale` columns" in error_codes_content
    assert "remove it manually so sync can restore the source-of-truth version" not in (
        error_codes_content.lower()
    )


def test_agent_and_skill_align_on_table_first_reporting() -> None:
    agent_path = (
        Path(__file__).resolve().parent
        / "../.github/agents/local-sync-install-ai-resources.agent.md"
    ).resolve()
    skill_path = (
        Path(__file__).resolve().parent
        / "../.github/skills/local-agent-sync-install-ai-resources/SKILL.md"
    ).resolve()
    agent_content = agent_path.read_text(encoding="utf-8")
    skill_content = skill_path.read_text(encoding="utf-8")

    assert "table-first report layout" in agent_content
    assert "why each blocker matters" in agent_content
    assert "table-first report" in skill_content


def test_agent_and_skill_align_on_default_sync_sequence() -> None:
    agent_path = (
        Path(__file__).resolve().parent
        / "../.github/agents/local-sync-install-ai-resources.agent.md"
    ).resolve()
    skill_path = (
        Path(__file__).resolve().parent
        / "../.github/skills/local-agent-sync-install-ai-resources/SKILL.md"
    ).resolve()
    agent_content = agent_path.read_text(encoding="utf-8")
    skill_content = skill_path.read_text(encoding="utf-8")

    expected = "run install `plan` first for the default `skills` target"
    assert expected in agent_content
    assert "Run install `plan` for the default `skills` target. Stop on blockers." in skill_content


def test_main_plan_compact_output_preserves_changed_resource_evidence(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="compact",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["changed_resources"]
    assert any(item["action"] == "mkdir" for item in payload["changed_resources"])
