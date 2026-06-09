from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_root_policy_files_keep_retained_plan_defaults_outside_always_on_detail() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")
    assert "tmp/superpowers/" in agents_text
    assert "internal-writing-plans" in agents_text
    assert "tmp/superpowers/" not in copilot_text


def test_writing_plans_declares_profile_consumer_contract() -> None:
    writing_text = read_text(".github/skills/internal-writing-plans/SKILL.md")
    assert "Recommended consumer" in writing_text
    assert "internal-gateway-simple-task" in writing_text
    assert "internal-executing-plans" in writing_text


def test_executing_plans_accepts_only_extended_consumers() -> None:
    executing_text = read_text(".github/skills/internal-executing-plans/SKILL.md")
    assert "approved `extended`" in executing_text
    assert "Reject any folder whose recommended consumer is not `internal-executing-plans`" in executing_text
