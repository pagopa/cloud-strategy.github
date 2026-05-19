from __future__ import annotations

import argparse
import json
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
        "  display_name: \"Demo Skill\"\n"
        "  short_description: \"Portable demo skill bundle\"\n"
        "  default_prompt: \"Use $demo-skill for demo work.\"\n",
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-home-ai-resources/references/runtime-support-matrix.yaml",
        "version: 1\n"
        "rows:\n"
        "  - target: codex\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: $HOME/.agents/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Codex direct-copy skill support.\n"
        "  - target: antigravity\n"
        "    resource_family: skills\n"
        "    support_level: Unknown / To verify\n"
        "    home_path: ~/.gemini/antigravity/skills/<skill>/\n"
        "    direct_copy_possible: false\n"
        "    translation_required: false\n"
        "    include_in_v1: false\n"
        "    evidence: []\n"
        "    notes: Undocumented support.\n",
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-home-ai-resources/references/home-sync-catalog.yaml",
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
        "      - antigravity\n"
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
        lambda: argparse.Namespace(
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
    assert payload["missing_dirs"] == [str(home_root / ".agents/skills")]


def test_main_apply_blocks_docs_unverified_targets(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        sync_home_ai_resources,
        "parse_args",
        lambda: argparse.Namespace(
            command="apply",
            source_root=str(source_root),
            home_root=str(home_root),
            targets="antigravity",
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
