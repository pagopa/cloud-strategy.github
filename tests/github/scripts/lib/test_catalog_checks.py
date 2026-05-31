from __future__ import annotations

from pathlib import Path

from lib.catalog_checks import run_consistency_checks
from lib.inventory import build_inventory_markdown

LEGACY_INSTRUCTION_DIR = ".github/" + "instructions"
LEGACY_APPLY_TO_KEY = "apply" + "To"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bridge_files(root: Path) -> None:
    write_file(
        root / "AGENTS.md",
        "# AGENTS\n\n- Use `.github/copilot-instructions.md`.\n- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        root / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )


def test_run_consistency_checks_flags_active_residual_instruction_reference(
    tmp_path: Path,
) -> None:
    write_bridge_files(tmp_path)
    write_file(
        tmp_path / ".github/skills/internal-demo/SKILL.md",
        "---\n"
        "name: internal-demo\n"
        "description: Use when demo validation needs a fixture.\n"
        "---\n\n"
        "# Internal Demo\n\n"
        "## When to use\n\n"
        "Use this skill for tests.\n\n"
        f"See `{LEGACY_INSTRUCTION_DIR}/internal-python.instructions.md`.\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/skills/internal-demo/SKILL.md",
        "residual-instruction-reference",
    ) in findings_by_path


def test_run_consistency_checks_ignores_legacy_instruction_sources_until_removed(
    tmp_path: Path,
) -> None:
    write_bridge_files(tmp_path)
    write_file(
        tmp_path / LEGACY_INSTRUCTION_DIR / "internal-python.instructions.md",
        "---\n"
        "description: Python\n"
        f"{LEGACY_APPLY_TO_KEY}: '**/*.py'\n"
        "---\n\n"
        "# Python Instructions\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "residual-instruction-reference" not in finding_codes


def test_run_consistency_checks_ignores_historical_deprecation_entries(
    tmp_path: Path,
) -> None:
    write_bridge_files(tmp_path)
    write_file(
        tmp_path / ".github/DEPRECATION.md",
        f"# Deprecation\n\n- `{LEGACY_INSTRUCTION_DIR}/`: removed under migration exception.\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", build_inventory_markdown(tmp_path))

    findings = run_consistency_checks(tmp_path)
    findings_by_path = {(finding.path, finding.code) for finding in findings}

    assert (
        ".github/DEPRECATION.md",
        "residual-instruction-reference",
    ) not in findings_by_path
