from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

import sync_home_ai_resources


def sync_cli_module():
    return getattr(sync_home_ai_resources, "SKILL_CLI", sync_home_ai_resources)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def set_tree_mtime(root: Path, timestamp: float) -> None:
    for path in sorted(root.rglob("*")):
        os.utime(path, (timestamp, timestamp))
    os.utime(root, (timestamp, timestamp))


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
    assert payload["direction_counts"] == {"repo_to_home": 1, "home_to_repo": 0}
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
            "direction": "repo-to-home",
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
            targets="codex,opencode",
            retire_targets="opencode",
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
    assert payload["retired_targets"] == ["opencode"]


def test_sync_auto_applies_clean_repo_to_home_install(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="sync",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=True,
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
    assert payload["mode"] == "sync"
    assert payload["status"] == "done"
    assert payload["install"]["manifest_path"]
    assert payload["bisync"]["drifts"] == []
    assert (home_root / ".agents/skills/demo-skill/SKILL.md").is_file()


def test_sync_stops_for_bisync_drift_after_clean_install(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    write_file(home_root / ".agents/skills/home-only/SKILL.md", "# Home only\n")
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="sync",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=True,
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
    assert payload["mode"] == "sync"
    assert payload["status"] == "needs_review"
    assert payload["bisync"]["blocked_codes"] == ["bisync-only-home"]
    assert payload["bisync"]["drifts"][0]["skill"] == "home-only"


def test_sync_allows_safe_repo_only_bisync_after_clean_install(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    write_file(source_root / ".github/skills/repo-only-extra/SKILL.md", "# Repo only\n")
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="sync",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=True,
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
    assert payload["mode"] == "sync"
    assert payload["status"] == "done"
    assert payload["bisync"]["blocked_codes"] == ["bisync-only-repo"]
    assert payload["bisync"]["drifts"] == [
        {
            "direction": "repo-to-home",
            "home": str(home_root / ".agents/skills/repo-only-extra"),
            "repo": str(source_root / ".github/skills/repo-only-extra"),
            "skill": "repo-only-extra",
            "type": "only-repo",
        }
    ]


def test_sync_stops_on_home_newer_managed_drift_via_bisync_review(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    cli_module = sync_cli_module()
    initial_plan = cli_module.build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=cli_module.parse_targets("skills"),
        mode="apply",
    )
    cli_module.apply_home_sync_plan(
        initial_plan,
        create_missing_dirs=True,
    )

    source_skill = source_root / ".github/skills/demo-skill"
    home_skill = home_root / ".agents/skills/demo-skill"
    write_file(home_skill / "SKILL.md", "# Home edited\n")
    set_tree_mtime(source_skill, 100.0)
    set_tree_mtime(home_skill, 200.0)

    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="sync",
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

    assert exit_code == 1
    assert payload["mode"] == "sync"
    assert payload["status"] == "needs_review"
    assert payload["install"]["blocked_codes"] == []
    assert any(
        operation["action"] == "warning"
        and operation["code"] == "target-modified-managed"
        for operation in payload["install"]["operations"]
    )
    assert any(
        drift["direction"] == "home-to-repo" and drift["skill"] == "demo-skill"
        for drift in payload["bisync"]["drifts"]
    )
    assert (home_skill / "SKILL.md").read_text(encoding="utf-8") == "# Home edited\n"


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
            format="report",
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
    assert "python3 ./.github/scripts/sync_home_ai_resources.py" in content
    assert "--format report" in content
    assert (
        "The `bisync` lane provides explicit bidirectional synchronization" in content
    )
    assert "Do not infer the mode, do not skip blockers" in content
    assert "next_action` as user approval for `apply`" in content
    assert "## Reporting Contract" in content
    assert "summary-first" in content
    assert "Auto-run safe repo-to-home install" in content
    assert "repo wins" in content
    assert "local-*" in content
    assert "Do not run `bisync apply` automatically" in content
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
    assert "Text reports must use a summary-first layout" in contract_content
    assert "### Sync, Plan, Audit, And Bisync Plan Report" in contract_content
    assert "Auto-applied" in contract_content
    assert "The `sync` command is the only auto-execute mode." in contract_content
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


def test_sync_report_output_has_compact_chat_sections(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    write_file(home_root / ".agents/skills/home-only/SKILL.md", "# Home only\n")
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="sync",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            retire_targets="",
            create_missing_dirs=True,
            prune_managed=False,
            experimental_targets=False,
            format="report",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "Status: sync | status=needs_review" in output
    assert "targets=skills" in output
    assert "next_action=review_bisync" in output
    assert "## Summary" in output
    assert "## Auto-applied" in output
    assert "## Stopped on" in output
    assert "## Validation" in output
    assert "## Next" in output
    assert "# Install Lane" not in output
    assert "# Bisync Lane" not in output


def test_agent_and_skill_align_on_summary_first_reporting() -> None:
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

    assert "table-first report layout" not in agent_content
    assert "why each blocker matters" not in agent_content
    assert "summary-first" in skill_content


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
    assert expected not in agent_content
    assert "Run `sync` for the default `skills` target." in skill_content


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


def test_main_plan_report_output_has_stable_summary_sections(
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
            format="report",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "## Summary" in output
    assert "repo-to-home install" in output
    assert "targets=skills" in output
    assert "next_action=apply" in output
    assert "## Changes" in output
    assert "## Attention" in output
    assert "## Validation" in output
    assert "## Next" in output
    assert "## Current State" not in output


def test_bisync_plan_report_output_has_stable_summary_sections(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    source_root.mkdir()
    home_root.mkdir()
    write_file(source_root / ".github/skills/repo-only/SKILL.md", "# Repo only\n")
    write_file(home_root / ".agents/skills/home-only/SKILL.md", "# Home only\n")

    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="bisync",
            bisync_command="plan",
            source_root=str(source_root),
            home_root=str(home_root),
            format="report",
        ),
    )

    exit_code = sync_home_ai_resources.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "## Summary" in output
    assert "repo-home drift" in output
    assert "next_action=resolve_blockers" in output
    assert "## Changes" in output
    assert "## Attention" in output
    assert "## Validation" in output
    assert "## Remaining Work" in output
    assert "## Next" in output
    assert "## Current State" not in output


def test_install_report_bounds_large_change_tables() -> None:
    cli = sync_cli_module()
    operations = [
        {
            "action": "copy",
            "resource_id": f"skill-{index:02d}",
            "path": f"/tmp/home/.agents/skills/skill-{index:02d}",
            "reason": "Repository copy is newer than home copy.",
            "target": "skills",
        }
        for index in range(25)
    ]
    payload = {
        "mode": "plan",
        "selected_targets": ["skills"],
        "retired_targets": [],
        "source_resources_considered": 25,
        "operations": operations,
        "blocked_codes": [],
        "validation": "ready",
        "next_action": {
            "action": "apply",
            "allowed": True,
            "requires_explicit_approval": True,
            "command": "apply --targets skills",
            "reason": "Plan is ready.",
        },
        "next_step": "Run apply when ready.",
    }

    output = cli.render_install_report(payload)

    assert "skill-00" in output
    assert "skill-19" in output
    assert "skill-20" not in output
    assert (
        "5 additional change rows omitted; use --format json for full detail." in output
    )


def test_doctor_report_output_has_readiness_sections(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda _=None: argparse.Namespace(
            command="doctor",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="skills",
            create_missing_dirs=False,
            prune_managed=False,
            experimental_targets=False,
            format="report",
            fast=False,
            changed_only=False,
        ),
    )

    exit_code = sync_home_ai_resources.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Status: repo-to-home install | mode=doctor | targets=skills" in output
    assert "next_action=resolve_blockers" in output
    assert "## Readiness" in output
    assert "target-root:skills" in output
    assert "needs-directory-create" in output
    assert "## Next" in output


def test_report_tables_escape_pipe_and_newline_cells() -> None:
    cli = sync_cli_module()
    payload = {
        "mode": "plan",
        "selected_targets": ["skills"],
        "retired_targets": [],
        "source_resources_considered": 1,
        "operations": [
            {
                "action": "blocked",
                "resource_id": "broken|skill",
                "path": "/tmp/home/.agents/skills/broken|skill",
                "reason": "First line\nSecond | part",
                "code": "target-exists-unmanaged",
                "target": "skills",
            }
        ],
        "blocked_codes": ["target-exists-unmanaged"],
        "validation": "blocked",
        "next_action": {
            "action": "resolve_blockers",
            "allowed": False,
            "requires_explicit_approval": True,
            "command": "none",
            "reason": "Resolve blockers.",
        },
        "next_step": "Resolve blockers.",
    }

    output = cli.render_install_report(payload)

    assert "broken\\|skill" in output
    assert "First line Second \\| part" in output


def test_cli_defaults_to_report_output_for_user_facing_modes() -> None:
    cli = sync_cli_module()

    assert cli.parse_args(["plan"]).format == "report"
    assert cli.parse_args(["doctor"]).format == "report"
    assert cli.parse_args(["bisync", "plan"]).format == "report"


def test_invalid_target_report_has_clear_blocked_next_action(capsys) -> None:
    cli = sync_cli_module()
    args = cli.parse_args(["plan", "--targets", "nope"])

    exit_code = cli.run(args)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert (
        "Status: repo-to-home install | mode=plan | targets=none | status=blocked"
        in output
    )
    assert "next_action=resolve_blockers" in output
    assert "unknown-target" in output
