import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/tools"))

from inventory.inventory import (  # noqa: E402
    parse_inventory_markdown,
    render_inventory_markdown,
)


def _base_sections() -> dict[str, list[str]]:
    return {
        "Instructions": [],
        "Skills": [
            ".github/skills/anthropic-docx/SKILL.md",
            ".github/skills/anthropic-pdf/SKILL.md",
            ".github/skills/anthropic-pptx/SKILL.md",
            ".github/skills/anthropic-xlsx/SKILL.md",
        ],
        "Imported Skill Provenance": [
            ".github/skills/anthropic-docx/SKILL.md",
            ".github/skills/anthropic-pdf/SKILL.md",
            ".github/skills/anthropic-pptx/SKILL.md",
            ".github/skills/anthropic-xlsx/SKILL.md",
        ],
        "Scripts": [],
        "Agents": [],
        "Prompts": [],
    }


def test_document_support_heading_is_vendor_neutral() -> None:
    rendered = render_inventory_markdown(_base_sections())

    assert "Support-only imported document skills" in rendered
    assert "anthropic-docx" in rendered
    assert "anthropic-pdf" in rendered
    assert "anthropic-pptx" in rendered
    assert "anthropic-xlsx" in rendered
    assert "openai-* office skills" not in rendered


def test_render_inventory_groups_imported_skills_by_source() -> None:
    groups = [
        {
            "repository": "anthropics/skills",
            "ref": "b29e7cf65e5c",
            "tag": None,
            "commit_date": "2026-07-24",
            "paths": [
                ".github/skills/anthropic-docx/SKILL.md",
                ".github/skills/anthropic-pdf/SKILL.md",
            ],
        },
    ]

    rendered = render_inventory_markdown(_base_sections(), groups)

    assert "## Imported Skill Provenance" in rendered
    assert "### anthropics/skills — ref b29e7cf65e5c · 2026-07-24 · 2 skills" in rendered
    assert "- `.github/skills/anthropic-docx/SKILL.md`" in rendered
    assert "- `.github/skills/anthropic-pdf/SKILL.md`" in rendered


def test_render_inventory_reports_tag_when_declared() -> None:
    groups = [
        {
            "repository": "mattpocock/skills",
            "ref": "6acc160e4e0c",
            "tag": "v1.2.3",
            "commit_date": "2026-08-06",
            "paths": [".github/skills/mattpocock-tdd/SKILL.md"],
        },
    ]

    rendered = render_inventory_markdown(_base_sections(), groups)

    assert (
        "### mattpocock/skills — ref 6acc160e4e0c · tag v1.2.3 · 2026-08-06 · 1 skills"
        in rendered
    )


def test_parse_inventory_collects_provenance_entries() -> None:
    text = (
        "# Copilot Inventory\n"
        "\n"
        "## Imported Skill Provenance\n"
        "\n"
        "### anthropics/skills — ref b29e7cf65e5c · 2026-07-24 · 2 skills\n"
        "\n"
        "- `.github/skills/anthropic-docx/SKILL.md`\n"
        "- `.github/skills/anthropic-pdf/SKILL.md`\n"
        "\n"
    )

    sections = parse_inventory_markdown(text)

    assert sections["Imported Skill Provenance"] == {
        ".github/skills/anthropic-docx/SKILL.md",
        ".github/skills/anthropic-pdf/SKILL.md",
    }


def test_render_inventory_empty_provenance_uses_placeholder() -> None:
    rendered = render_inventory_markdown(_base_sections(), [])

    assert (
        "No imported skill provenance is available; declare sources in the "
        "external resource manifest." in rendered
    )
