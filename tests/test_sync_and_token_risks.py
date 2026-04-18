from __future__ import annotations

import json
from pathlib import Path

from lib.syncing import apply_sync_plan, build_sync_plan, write_sync_plan
from lib.token_risks import detect_token_risks


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_sync_plan_preserves_local_assets_and_deletes_non_local_assets(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(
        source_root / ".github/agents/internal-fast.agent.md",
        "---\nname: internal-fast\ntools: [read]\n---\n",
    )
    write_file(
        source_root / ".github/agents/internal-sync-legacy.agent.md",
        "---\nname: internal-sync-legacy\ntools: [read]\n---\n",
    )

    write_file(target_root / "AGENTS.md", "# AGENTS\nold\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\nold\n")
    write_file(
        target_root / ".github/agents/internal-fast.agent.md",
        "---\nname: internal-fast\ntools: [read]\n---\nold\n",
    )
    write_file(
        target_root / ".github/agents/internal-sync-legacy.agent.md",
        "---\nname: internal-sync-legacy\ntools: [read]\n---\nlegacy\n",
    )
    write_file(
        target_root / ".github/agents/local-special.agent.md",
        "---\nname: local-special\ntools: [read]\n---\n",
    )
    write_file(
        target_root / ".github/local-copilot-overrides.md",
        "# Local Copilot Overrides\n\n- Override: Keep repo-local behavior explicit.\n",
    )
    write_file(
        target_root / ".github/agents/custom.agent.md",
        "---\nname: custom\ntools: [read]\n---\n",
    )

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("preserve", ".github/agents/local-special.agent.md") in actions
    assert ("preserve", ".github/local-copilot-overrides.md") in actions
    assert ("delete", ".github/agents/custom.agent.md") in actions
    assert ("update", ".github/agents/internal-fast.agent.md") in actions
    assert ("delete", ".github/agents/internal-sync-legacy.agent.md") in actions


def test_build_sync_plan_does_not_mirror_source_local_override_file(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/local-copilot-overrides.md",
        "# Local Copilot Overrides\n\n- No active overrides in this repository.\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")

    plan = build_sync_plan(source_root, target_root)

    assert all(
        operation.path != ".github/local-copilot-overrides.md"
        for operation in plan.operations
    )


def test_apply_sync_plan_clears_plan_file_and_writes_manifest(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / "VERSION", "1.2.3\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/agents/internal-fast.agent.md",
        "---\nname: internal-fast\ntools: [read]\n---\n\n# Source\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(
        target_root / ".github/agents/internal-fast.agent.md",
        "---\nname: internal-fast\ntools: [read]\n---\n\n# Target\n",
    )
    write_file(
        target_root / "tmp/internal-sync-copilot-configs.plan.md", "legacy plan\n"
    )
    write_file(
        target_root / ".github/internal-sync-copilot-configs.manifest.json", "{}\n"
    )
    write_file(
        target_root / ".github/local-copilot-overrides.md",
        "# Local Copilot Overrides\n\n- Override: Keep target-local exceptions.\n",
    )

    plan = build_sync_plan(source_root, target_root)
    plan_path = write_sync_plan(plan)

    manifest_path = apply_sync_plan(plan)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert not plan_path.exists()
    assert manifest_path.exists()
    assert manifest_path.name == "copilot-sync.manifest.json"
    assert not (target_root / "tmp/internal-sync-copilot-configs.plan.md").exists()
    assert not (
        target_root / ".github/internal-sync-copilot-configs.manifest.json"
    ).exists()
    assert (target_root / ".github/local-copilot-overrides.md").exists()
    assert "AGENTS.md" in manifest["managed_hashes"]
    assert manifest["managed_hashes"][".github/agents/internal-fast.agent.md"]
    assert manifest["source_version"] == "1.2.3"
    assert (target_root / "AGENTS.md").read_text(
        encoding="utf-8"
    ) == "# AGENTS\nsource\n"
    assert (target_root / ".gitignore").read_text(
        encoding="utf-8"
    ) == "/tmp/superpowers/\n"


def test_build_sync_plan_ensures_target_gitignore_entry_without_mirroring_source_gitignore(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / ".gitignore", "/tmp/\n")
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / ".gitignore", "node_modules/\n")

    plan = build_sync_plan(source_root, target_root)
    operations = {(operation.action, operation.path) for operation in plan.operations}

    assert ("ensure", ".gitignore") in operations
    assert plan.generated_gitignore == "node_modules/\n/tmp/superpowers/\n"


def test_build_sync_plan_accepts_existing_tmp_superpowers_gitignore_entry(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / ".gitignore", "node_modules/\ntmp/superpowers/\n")

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("unchanged", ".gitignore") in actions
    assert plan.generated_gitignore == "node_modules/\ntmp/superpowers/\n"


def test_build_sync_plan_reads_source_and_target_manifest_versions(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / "VERSION", "2.4.0\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(
        target_root / ".github/copilot-sync.manifest.json",
        json.dumps({"source_version": "2.3.1"}) + "\n",
    )

    plan = build_sync_plan(source_root, target_root)

    assert plan.source_version == "2.4.0"
    assert plan.target_manifest_source_version == "2.3.1"


def test_apply_sync_plan_creates_target_lessons_from_source_template(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    source_lessons = (
        "# Lessons\n\n"
        "Source-managed retained learning ledger.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n\n"
        "No pending lessons currently.\n"
    )

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / "LESSONS_LEARNED.md", source_lessons)
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("create", "LESSONS_LEARNED.md") in actions

    apply_sync_plan(plan)

    assert (target_root / "LESSONS_LEARNED.md").read_text(
        encoding="utf-8"
    ) == source_lessons


def test_apply_sync_plan_realigns_lessons_structure_without_losing_target_rows(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    source_lessons = (
        "# Lessons\n\n"
        "Source-managed retained learning ledger.\n\n"
        "## Entry Rules\n\n"
        "- Use the source structure.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target | Notes |\n"
        "| --- | --- | --- | --- | --- |\n\n"
        "No pending lessons currently.\n"
    )
    target_lessons = (
        "# Lessons\n\n"
        "Target-only intro that should be replaced.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n"
        "| 2026-04-12 | Preserve local lesson | pending | AGENTS.md |\n"
    )

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / "LESSONS_LEARNED.md", source_lessons)
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "LESSONS_LEARNED.md", target_lessons)

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("update", "LESSONS_LEARNED.md") in actions

    apply_sync_plan(plan)

    assert (target_root / "LESSONS_LEARNED.md").read_text(encoding="utf-8") == (
        "# Lessons\n\n"
        "Source-managed retained learning ledger.\n\n"
        "## Entry Rules\n\n"
        "- Use the source structure.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target | Notes |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 2026-04-12 | Preserve local lesson | pending | AGENTS.md |  |\n"
    )


def test_build_sync_plan_includes_shared_repo_hygiene_files_only(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / ".editorconfig", "root = true\n")
    write_file(source_root / ".pre-commit-config.yaml", "repos: []\n")
    write_file(
        source_root / ".github/workflows/_pre-commit.yml",
        "name: pre-commit\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / ".editorconfig", "root = false\n")
    write_file(target_root / ".pre-commit-config.yaml", "repos:\n  - repo: old\n")
    write_file(
        target_root / ".github/workflows/_pre-commit.yml",
        "name: old-pre-commit\n",
    )
    write_file(target_root / ".github/workflows/local-only.yml", "name: local-only\n")

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}
    planned_paths = {operation.path for operation in plan.operations}

    assert ("update", ".editorconfig") in actions
    assert ("update", ".pre-commit-config.yaml") in actions
    assert ("update", ".github/workflows/_pre-commit.yml") in actions
    assert ".github/workflows/local-only.yml" not in planned_paths


def test_apply_sync_plan_mirrors_shared_repo_hygiene_files(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / ".editorconfig", "root = true\n")
    write_file(source_root / ".pre-commit-config.yaml", "repos: []\n")
    write_file(
        source_root / ".github/workflows/_pre-commit.yml",
        "name: pre-commit\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / ".editorconfig", "root = false\n")
    write_file(target_root / ".pre-commit-config.yaml", "repos:\n  - repo: old\n")
    write_file(
        target_root / ".github/workflows/_pre-commit.yml",
        "name: old-pre-commit\n",
    )

    plan = build_sync_plan(source_root, target_root)
    apply_sync_plan(plan)

    assert (target_root / ".editorconfig").read_text(
        encoding="utf-8"
    ) == "root = true\n"
    assert (target_root / ".pre-commit-config.yaml").read_text(
        encoding="utf-8"
    ) == "repos: []\n"
    assert (target_root / ".github/workflows/_pre-commit.yml").read_text(
        encoding="utf-8"
    ) == "name: pre-commit\n"


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
    write_file(
        tmp_path / ".github/copilot-instructions.md", f"# Copilot\n\n{repeated_lines}\n"
    )
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "bridge-overlap" in finding_codes


def test_detect_token_risks_ignores_structural_bridge_references(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n"
        "- Use `.github/copilot-instructions.md` as the repo-wide projection.\n"
        "- Use `.github/INVENTORY.md` as the live catalog.\n"
        "- Use `.github/instructions/` for scoped guidance.\n"
        "- Use `.github/skills/` when a reusable workflow is relevant.\n"
        "- Use `.github/agents/` when a stable owner is relevant.\n"
        "- Keep `.github/local-copilot-overrides.md` local to consumer repositories.\n",
    )
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "inventory-dump-in-bridge" not in finding_codes


def test_detect_token_risks_reports_internal_root_policy_overlap(
    tmp_path: Path,
) -> None:
    root_policy_lines = "\n".join(
        [
            "- Keep policy separate from inventory.",
            "- Keep AGENTS.md strategic and stable.",
            "- Keep .github/copilot-instructions.md as the projection layer.",
            "- Keep .github/INVENTORY.md as the exact catalog.",
            "- Preserve explicit precedence rules.",
            "- Remove overlap instead of keeping compatibility copies.",
            "- Keep language exceptions explicit and local.",
            "- Keep repository-wide defaults in one canonical place.",
        ]
    )

    write_file(tmp_path / "AGENTS.md", f"# AGENTS\n\n{root_policy_lines}\n")
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot\n\n- Keep policy separate from inventory.\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    write_file(
        tmp_path / ".github/agents/internal-sync-control-center.agent.md",
        "---\nname: internal-sync-control-center\ntools: [read]\n---\n\n"
        "# Internal Sync Control Center\n\n"
        "Use `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md`.\n\n"
        f"{root_policy_lines}\n",
    )

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "internal-root-policy-overlap" in finding_codes


def test_detect_token_risks_reports_instruction_skill_policy_overlap(
    tmp_path: Path,
) -> None:
    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    write_file(
        tmp_path / ".github/instructions/internal-python.instructions.md",
        "---\n"
        "description: Python\n"
        "applyTo: '**/*.py'\n"
        "---\n\n"
        "# Python Instructions\n\n"
        "- Use emoji logs for key execution states.\n"
        "- Prefer early return and clear guard clauses.\n"
        "- Unit tests are required for testable logic.\n",
    )
    write_file(
        tmp_path / ".github/skills/internal-project-python/SKILL.md",
        "---\n"
        "name: internal-project-python\n"
        "description: Python project skill\n"
        "---\n\n"
        "# Python Project Skill\n\n"
        "- Use emoji logs for key execution states.\n"
        "- Prefer early return and clear guard clauses.\n"
        "- Unit tests are required for testable logic.\n",
    )

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "instruction-skill-policy-overlap" in finding_codes


def test_detect_token_risks_reports_paired_agent_skill_overlap(tmp_path: Path) -> None:
    shared_lines = "\n".join(
        [
            "- Keep the paired agent short.",
            "- The skill owns the reusable sync procedure.",
            "- Preserve target local assets during apply.",
            "- Exclude internal-sync resources from consumer mirroring.",
            "- Keep root-guidance files layered.",
            "- Write the tracking plan before mirrored changes.",
        ]
    )

    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    write_file(
        tmp_path / ".github/agents/internal-sync-example.agent.md",
        "---\n"
        "name: internal-sync-example\n"
        "tools: [read]\n"
        "---\n\n"
        "# Internal Sync Example\n\n"
        "## Mandatory Engine Skills\n\n"
        "- `internal-sync-example`\n\n"
        f"{shared_lines}\n",
    )
    write_file(
        tmp_path / ".github/skills/internal-sync-example/SKILL.md",
        "---\n"
        "name: internal-sync-example\n"
        "description: Sync example\n"
        "---\n\n"
        "# Internal Sync Example\n\n"
        f"{shared_lines}\n",
    )

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "paired-agent-skill-overlap" in finding_codes
