from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-excel/SKILL.md"
TOOL_SELECTION_PATH = (
    REPO_ROOT / ".github/skills/internal-excel/references/tool-selection.md"
)


def test_internal_excel_routes_workbook_presentation_to_anthropic_xlsx() -> None:
    skill_text = SKILL_PATH.read_text()
    tool_selection_text = TOOL_SELECTION_PATH.read_text()

    assert "anthropic-xlsx" in skill_text
    assert "anthropic-xlsx" in tool_selection_text
    assert "openai-spreadsheet" not in skill_text
    assert "openai-spreadsheet" not in tool_selection_text
