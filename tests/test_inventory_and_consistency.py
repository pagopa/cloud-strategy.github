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
    assert "- `.github/skills/internal-catalog/SKILL.md`" in inventory
    assert "- `.github/agents/internal-fast-executor.agent.md`" in inventory


def test_run_consistency_checks_flags_inventory_drift_and_missing_tools(
    tmp_path: Path,
) -> None:
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
        "# Copilot Inventory\n\n## Instructions\n\nNo instruction files currently ship in the live catalog.\n\n## Skills\n\nNo skill files currently ship in the live catalog.\n\n## Agents\n\nNo agent files currently ship in the live catalog.\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\n---\n\n# Internal Sync\n",
    )

    findings = run_consistency_checks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "inventory-missing-entry" in finding_codes
    assert "internal-agent-missing-tools" in finding_codes


def test_run_consistency_checks_flags_empty_and_invalid_tools_contracts(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md`.\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-empty.agent.md",
        "---\nname: internal-empty\ntools: []\n---\n\n# Empty\n",
    )
    write_file(
        tmp_path / ".github/agents/internal-invalid.agent.md",
        "---\nname: internal-invalid\ntools:\n  - read\n  - 1\n---\n\n# Invalid\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/agents/internal-empty.agent.md",
        "internal-agent-missing-tools",
    ) in findings_by_path
    assert (
        ".github/agents/internal-invalid.agent.md",
        "internal-agent-invalid-tools",
    ) in findings_by_path


def test_run_consistency_checks_flags_invalid_imported_asset_override_registry(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md`.\n",
    )
    write_file(
        tmp_path / ".github/skills/obra-demo/SKILL.md",
        "---\nname: obra-demo\ndescription: Imported workflow.\n---\n",
    )
    write_file(
        tmp_path
        / ".github/skills/internal-agent-sync-control-center/references/imported-asset-overrides.yaml",
        "overrides:\n"
        "  - id: bad-entry\n"
        "    target_path: .github/skills/obra-demo/SKILL.md\n"
        "    lifecycle_mode: support-only\n"
        "    apply_strategy: ad-hoc\n"
        "    approval: pending\n"
        "    patch_path: patches/missing.patch\n"
        "    expected_content_hash: short\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "imported-asset-override-approval-missing" in finding_codes
    assert "imported-asset-override-invalid-lifecycle" in finding_codes
    assert "imported-asset-override-invalid-apply-strategy" in finding_codes
    assert "imported-asset-override-patch-missing" in finding_codes
    assert "imported-asset-override-invalid-hash" in finding_codes
