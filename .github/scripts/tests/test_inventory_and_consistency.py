from __future__ import annotations

from pathlib import Path

from lib.catalog_checks import run_consistency_checks
from lib.inventory import build_inventory_markdown


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_inventory_markdown_lists_catalog_sections(tmp_path: Path) -> None:
    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(
        tmp_path / ".github/agents/internal-fast-executor.agent.md",
        "---\nname: internal-fast-executor\ntools: [read]\n---\n",
    )
    write_file(
        tmp_path / ".github/instructions/internal-python.instructions.md",
        "---\ndescription: Python\napplyTo: '**/*.py'\n---\n",
    )
    write_file(
        tmp_path / ".github/skills/internal-catalog/SKILL.md",
        "---\nname: internal-catalog\ndescription: Catalog helper\n---\n",
    )

    inventory = build_inventory_markdown(tmp_path)

    assert "## Instructions" in inventory
    assert "- `.github/instructions/internal-python.instructions.md`" in inventory
    assert "## Prompts" in inventory
    assert "No prompt files currently ship in the live catalog." in inventory
    assert "- `.github/skills/internal-catalog/SKILL.md`" in inventory
    assert "- `.github/agents/internal-fast-executor.agent.md`" in inventory


def test_run_consistency_checks_flags_inventory_drift_and_missing_tools(tmp_path: Path) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/INVENTORY.md",
        "# Copilot Inventory\n\n## Instructions\n\nNo instruction files currently ship in the live catalog.\n\n## Prompts\n\nNo prompt files currently ship in the live catalog.\n\n## Skills\n\nNo skill files currently ship in the live catalog.\n\n## Agents\n\nNo agent files currently ship in the live catalog.\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\n---\n\n# Internal Sync\n",
    )

    findings = run_consistency_checks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "inventory-missing-entry" in finding_codes
    assert "internal-agent-missing-tools" in finding_codes
