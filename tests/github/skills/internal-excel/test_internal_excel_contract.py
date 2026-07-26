from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-excel/SKILL.md"
TOOL_SELECTION_PATH = (
    REPO_ROOT / ".github/skills/internal-excel/references/tool-selection.md"
)
OPENAI_PATH = REPO_ROOT / ".github/skills/internal-excel/agents/openai.yaml"

EXPECTED_DESCRIPTION = (
    "Use when any task reads, creates, edits, validates, converts, or mentions "
    "an Excel workbook or an XLSX, XLSM, CSV, or TSV file. Load this skill "
    "first and keep it active even when formatting, charts, rendered review, "
    "or recalculation also require anthropic-xlsx."
)


def test_internal_excel_is_the_universal_spreadsheet_entry_point() -> None:
    _, raw_frontmatter, _ = SKILL_PATH.read_text(encoding="utf-8").split(
        "---", maxsplit=2
    )

    assert yaml.safe_load(raw_frontmatter)["description"] == EXPECTED_DESCRIPTION


def test_internal_excel_adds_anthropic_xlsx_without_being_replaced() -> None:
    skill_text = SKILL_PATH.read_text()
    tool_selection_text = TOOL_SELECTION_PATH.read_text()
    openai_text = OPENAI_PATH.read_text()

    assert "anthropic-xlsx" in skill_text
    assert "anthropic-xlsx" in tool_selection_text
    assert "add `anthropic-xlsx`" in skill_text
    assert "add `anthropic-xlsx`" in tool_selection_text
    assert "primary entry point" in openai_text
    assert "Route out of this skill." not in tool_selection_text
    assert "Hand off only when" not in skill_text
    assert "openai-spreadsheet" not in skill_text
    assert "openai-spreadsheet" not in tool_selection_text
