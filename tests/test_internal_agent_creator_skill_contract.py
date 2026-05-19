from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(".github/skills/internal-agent-creator")


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def run_json_script(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_internal_agent_creator_uses_single_core_skill_contract() -> None:
    skill_text = read_text(".github/skills/internal-agent-creator/SKILL.md")
    contract_text = read_text(
        ".github/skills/internal-agent-creator/references/agent-contract.md"
    )
    template_text = read_text(
        ".github/skills/internal-agent-creator/references/agent-template.md"
    )

    assert "## Referenced skills" in skill_text
    assert "## Core Skill" in skill_text
    assert "zero skill references or one explicit core skill" in skill_text
    assert (
        "one existing repo-owned skill for its required operating logic"
        in contract_text
    )
    assert "must list exactly one canonical skill identifier" in contract_text
    assert "## Core Skill" in template_text
    assert "## Optional Support Skills\n\n-" not in template_text
    assert "## Mandatory Engine Skills\n\n-" not in template_text


def test_internal_agent_creator_has_official_source_map_with_openai_guidance() -> None:
    source_map = read_text(
        ".github/skills/internal-agent-creator/references/official-source-map.md"
    )

    assert (
        "https://docs.github.com/en/copilot/reference/custom-agents-configuration"
        in source_map
    )
    assert "https://code.visualstudio.com/docs/copilot/agents/subagents" in source_map
    assert "https://agentskills.io/specification" not in source_map
    assert "skill-creation" not in source_map
    assert (
        "https://developers.openai.com/api/docs/guides/prompt-engineering#coding"
        in source_map
    )
    assert (
        "https://developers.openai.com/codex/learn/best-practices#improve-reliability-with-testing-and-review"
        in source_map
    )


def test_internal_agent_creator_scripts_report_agent_and_token_shape() -> None:
    audit = run_json_script(
        ".github/skills/internal-agent-creator/scripts/audit_agent_contract.py",
        "--root",
        ".",
        "--format",
        "json",
    )
    token_audit = run_json_script(
        ".github/skills/internal-agent-creator/scripts/measure_skill_bundle_tokens.py",
        "--skill-dir",
        ".github/skills/internal-agent-creator",
        "--format",
        "json",
    )

    assert audit["summary"]["agent_count"] >= 5
    assert audit["summary"]["legacy_agent_count"] == 0
    assert token_audit["totals"]["loaded_docs"] < 4500
    assert token_audit["totals"]["script_code"] > 0
    assert token_audit["summary"]["finding_count"] == 0
