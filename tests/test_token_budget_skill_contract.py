from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_token_budget_guardrails_are_distributed_by_owner() -> None:
    simple_text = read_text(".github/skills/internal-gateway-simple-task/SKILL.md")
    plan_mode_text = read_text(
        ".github/skills/internal-gateway-simple-task/references/plan-mode.md"
    )
    idea_text = read_text(".github/skills/internal-gateway-idea-brainstorming/SKILL.md")
    execute_text = read_text(".github/skills/internal-gateway-execute-plans/SKILL.md")
    review_text = read_text(".github/skills/internal-gateway-review/SKILL.md")
    verification_text = read_text(
        ".github/skills/superpowers-verification-before-completion/SKILL.md"
    )
    spreadsheet_text = read_text(".github/skills/openai-spreadsheet/SKILL.md")

    assert "Token Budget Gate" in simple_text
    assert "Copilot or debug log analysis" in simple_text
    assert "Token Budget Gate" in plan_mode_text
    assert "aggregate-first" in idea_text
    assert "Compact Evidence Reporting" in execute_text
    assert "Compact Evidence Reporting" in review_text
    assert "Compact Evidence Reporting" in verification_text
    assert "Structured Data Evidence Budget" in spreadsheet_text


def test_structured_data_guardrails_preserve_full_file_correctness() -> None:
    spreadsheet_text = read_text(".github/skills/openai-spreadsheet/SKILL.md")
    lowered = spreadsheet_text.lower()

    assert ".xlsx" in spreadsheet_text
    assert ".csv" in spreadsheet_text
    assert ".tsv" in spreadsheet_text
    assert "row counts" in lowered
    assert "column counts" in lowered
    assert "full-file" in lowered
    assert "sampling does not replace full-file validation" in lowered
    assert "source links" in lowered
    assert "duplicate ids" in lowered
