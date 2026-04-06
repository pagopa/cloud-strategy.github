from __future__ import annotations

import json
from pathlib import Path

from lib.syncing import apply_sync_plan, build_sync_plan, write_sync_plan
from lib.token_risks import detect_token_risks


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_sync_plan_preserves_local_assets_and_deletes_non_local_assets(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(
        source_root / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\ntools: [read]\n---\n",
    )
    write_file(
        source_root / ".github/skills/internal-sync/SKILL.md",
        "---\nname: internal-sync\ndescription: Sync\n---\n",
    )

    write_file(target_root / "AGENTS.md", "# AGENTS\nold\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\nold\n")
    write_file(
        target_root / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\ntools: [read]\n---\nold\n",
    )
    write_file(
        target_root / ".github/agents/local-special.agent.md",
        "---\nname: local-special\ntools: [read]\n---\n",
    )
    write_file(
        target_root / ".github/agents/custom.agent.md",
        "---\nname: custom\ntools: [read]\n---\n",
    )

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("preserve", ".github/agents/local-special.agent.md") in actions
    assert ("delete", ".github/agents/custom.agent.md") in actions
    assert ("update", ".github/agents/internal-sync.agent.md") in actions


def test_apply_sync_plan_keeps_plan_file_and_writes_manifest(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\ntools: [read]\n---\n\n# Source\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(
        target_root / ".github/agents/internal-sync.agent.md",
        "---\nname: internal-sync\ntools: [read]\n---\n\n# Target\n",
    )

    plan = build_sync_plan(source_root, target_root)
    plan_path = write_sync_plan(plan)

    manifest_path = apply_sync_plan(plan)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert plan_path.exists()
    assert manifest_path.exists()
    assert "AGENTS.md" in manifest["managed_hashes"]
    assert manifest["managed_hashes"][".github/agents/internal-sync.agent.md"]
    assert (target_root / "AGENTS.md").read_text(encoding="utf-8") == "# AGENTS\nsource\n"


def test_detect_token_risks_reports_bridge_overlap(tmp_path: Path) -> None:
    repeated_lines = "\n".join(
        [
            "- Keep policy separate from inventory.",
            "- Keep AGENTS.md strategic and stable.",
            "- Keep .github/copilot-instructions.md as the projection layer.",
            "- Keep .github/INVENTORY.md as the exact catalog.",
            "- Preserve explicit precedence rules.",
            "- Remove overlap instead of keeping compatibility copies.",
            "- Use GitHub Copilot terminology only.",
        ]
    )

    write_file(tmp_path / "AGENTS.md", f"# AGENTS\n\n{repeated_lines}\n")
    write_file(tmp_path / ".github/copilot-instructions.md", f"# Copilot\n\n{repeated_lines}\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "bridge-overlap" in finding_codes
