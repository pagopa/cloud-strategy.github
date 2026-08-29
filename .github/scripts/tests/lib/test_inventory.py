import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.inventory import render_inventory_markdown  # noqa: E402


def test_document_support_heading_is_vendor_neutral() -> None:
    sections = {
        "Instructions": [],
        "Skills": [
            ".github/skills/anthropic-docx/SKILL.md",
            ".github/skills/anthropic-pdf/SKILL.md",
            ".github/skills/anthropic-pptx/SKILL.md",
            ".github/skills/anthropic-xlsx/SKILL.md",
        ],
        "Scripts": [],
        "Agents": [],
        "Prompts": [],
    }

    rendered = render_inventory_markdown(sections)

    assert "Support-only imported document skills" in rendered
    assert "anthropic-docx" in rendered
    assert "anthropic-pdf" in rendered
    assert "anthropic-pptx" in rendered
    assert "anthropic-xlsx" in rendered
    assert "openai-* office skills" not in rendered
