import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/tools"))

from inventory.inventory import (  # noqa: E402
    build_inventory_markdown,
    collect_inventory_sections,
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
    assert (
        "### anthropics/skills — ref b29e7cf65e5c · 2026-07-24 · 2 skills" in rendered
    )
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


def test_manifest_support_file_is_not_listed_as_an_imported_skill(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / ".github/skills/vendor-planning"
    reference = skill_dir / "references/definition-of-done.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("# Definition of Done\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text("# Planning\n", encoding="utf-8")
    manifest = tmp_path / (
        ".github/skills/local-agent-sync-external-resources/"
        "references/managed-resources.yaml"
    )
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "version: 1\n"
        "sources:\n"
        "  vendor-skills:\n"
        "    repository: https://github.com/vendor/skills.git\n"
        "    ref: " + "a" * 40 + "\n"
        "    assets:\n"
        "      - local: .github/skills/vendor-planning\n"
        "      - local: .github/skills/vendor-planning/references/definition-of-done.md\n",
        encoding="utf-8",
    )

    rendered = build_inventory_markdown(tmp_path)
    sections = parse_inventory_markdown(rendered)

    assert sections["Imported Skill Provenance"] == {
        ".github/skills/vendor-planning/SKILL.md"
    }
    assert "1 skills" in rendered


def test_inventory_excludes_script_runtime_and_fixture_paths(tmp_path: Path) -> None:
    included_paths = {
        ".github/scripts/check.py",
    }
    excluded_paths = {
        ".github/tools/catalog/rules.py",
        ".github/scripts/.venv/lib/tool.py",
        ".github/scripts/.pytest_cache/cache.py",
        ".github/scripts/__pycache__/module.py",
        ".github/scripts/graphify-out/cache.py",
        ".github/scripts/tests/test_fixture.py",
        ".github/tools/common/__init__.py",
    }

    for relative_path in included_paths | excluded_paths:
        fixture_path = tmp_path / relative_path
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text("# fixture\n", encoding="utf-8")

    scripts = set(collect_inventory_sections(tmp_path)["Scripts"])

    assert included_paths <= scripts
    assert not scripts & excluded_paths
    assert not any(
        any(
            part in {".venv", ".pytest_cache", "__pycache__", "graphify-out", "tests"}
            for part in Path(script).parts
        )
        for script in scripts
    )
