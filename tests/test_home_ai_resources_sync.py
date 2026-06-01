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
            targets="codex",
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
    assert payload["selected_targets"] == ["codex"]
    assert str(home_root / ".agents/skills") in payload["missing_dirs"]
    assert str(home_root / ".codex/agents") in payload["missing_dirs"]


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

    exit_code = sync_home_ai_resources.main()
    payload = json.loads(capsys.readouterr().out)

    assert "drifts" in payload
    assert "next_action" in payload
    assert "blocked_codes" in payload
    assert "action" in payload["next_action"]


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


def test_skill_runbook_distinguishes_install_and_bisync_lanes() -> None:
    skill_path = (
        Path(__file__).resolve().parent
        / "../.github/skills/local-agent-sync-install-ai-resources/SKILL.md"
    ).resolve()
    content = skill_path.read_text(encoding="utf-8")

    assert "## Deterministic Operator Protocol" in content
    assert "Install sync is unidirectional: repo -> home only." in content
    assert (
        "The `bisync` lane provides explicit bidirectional synchronization" in content
    )
    assert "Do not infer the mode, do not skip blockers" in content
    assert "next_action` as user approval for `apply`" in content
    assert "non-thinking" not in content.lower()
