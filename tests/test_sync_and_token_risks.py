from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from lib.syncing import apply_sync_plan, build_sync_plan, write_sync_plan
from lib.token_risks import (
    ROOT_ALWAYS_ON_PATHS,
    ROOT_ALWAYS_ON_TOKEN_TARGET,
    detect_token_risks,
    estimate_tokens,
)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def init_git_repo(root: Path) -> None:
    run_git(root, "init")
    run_git(root, "config", "user.name", "Test User")
    run_git(root, "config", "user.email", "test@example.com")


def commit_all(root: Path, message: str) -> None:
    run_git(root, "add", "-A")
    run_git(root, "commit", "-m", message)


def test_build_sync_plan_preserves_local_assets_and_deletes_non_local_assets(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(
        source_root / ".github/templates/copilot-instructions.override.md.template",
        "# Copilot Instructions Override\n\n- No active overrides in this repository.\n",
    )
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
        target_root / ".github/copilot-instructions.override.md",
        "# Copilot Instructions Override\n\n- Override: Keep repo-local behavior explicit.\n",
    )
    write_file(
        target_root / ".github/agents/custom.agent.md",
        "---\nname: custom\ntools: [read]\n---\n",
    )

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("preserve", ".github/agents/local-special.agent.md") in actions
    assert ("preserve", ".github/copilot-instructions.override.md") in actions
    assert ("delete", ".github/agents/custom.agent.md") in actions
    assert ("update", ".github/agents/internal-fast.agent.md") in actions
    assert ("delete", ".github/agents/internal-sync-legacy.agent.md") in actions


def test_build_sync_plan_creates_target_local_override_from_template_when_missing(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/templates/copilot-instructions.override.md.template",
        "# Copilot Instructions Override\n\n- No active overrides in this repository.\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")

    plan = build_sync_plan(source_root, target_root)

    assert ("create", ".github/copilot-instructions.override.md") in {
        (operation.action, operation.path) for operation in plan.operations
    }
    assert all(
        operation.path != ".github/templates/copilot-instructions.override.md.template"
        for operation in plan.operations
    )


def test_build_sync_plan_creates_consumer_local_knowledge_docs_from_templates(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / "docs/03-local-ai-runtime-operating-model.md", "# Runtime\n")
    write_file(
        source_root / ".github/templates/01-architecture.md.template",
        "# Architecture scaffold\n",
    )
    write_file(
        source_root / ".github/templates/02-repository-context.md.template",
        "# Context scaffold\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}
    planned_paths = {operation.path for operation in plan.operations}

    assert ("create", "docs/01-local-architecture.md") in actions
    assert ("create", "docs/02-local-repository-context.md") in actions
    assert ("create", "docs/03-local-ai-runtime-operating-model.md") in actions
    assert ".github/templates/01-architecture.md.template" not in planned_paths
    assert ".github/templates/02-repository-context.md.template" not in planned_paths


def test_apply_sync_plan_creates_consumer_local_knowledge_docs_from_templates(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/templates/01-architecture.md.template",
        "# Architecture scaffold\n",
    )
    write_file(
        source_root / ".github/templates/02-repository-context.md.template",
        "# Context scaffold\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")

    plan = build_sync_plan(source_root, target_root)
    apply_sync_plan(plan)

    assert (target_root / "docs/01-local-architecture.md").read_text(
        encoding="utf-8"
    ) == "# Architecture scaffold\n"
    assert (target_root / "docs/02-local-repository-context.md").read_text(
        encoding="utf-8"
    ) == "# Context scaffold\n"


def test_build_sync_plan_preserves_existing_consumer_local_knowledge_docs(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/templates/01-architecture.md.template",
        "# Architecture scaffold\n",
    )
    write_file(
        source_root / ".github/templates/02-repository-context.md.template",
        "# Context scaffold\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "docs/01-local-architecture.md", "# Target architecture\n")
    write_file(target_root / "docs/02-local-repository-context.md", "# Target context\n")

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert ("preserve", "docs/01-local-architecture.md") in actions
    assert ("preserve", "docs/02-local-repository-context.md") in actions
    assert "docs/01-local-architecture.md" in plan.local_assets
    assert "docs/02-local-repository-context.md" in plan.local_assets


def test_build_sync_plan_renames_legacy_architecture_when_new_path_is_missing(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/templates/01-architecture.md.template",
        "# Architecture scaffold\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "docs/architecture.md", "# Legacy architecture\n")

    plan = build_sync_plan(source_root, target_root)

    assert ("rename", "docs/01-local-architecture.md") in {
        (operation.action, operation.path) for operation in plan.operations
    }

    apply_sync_plan(plan)

    assert not (target_root / "docs/architecture.md").exists()
    assert (target_root / "docs/01-local-architecture.md").read_text(
        encoding="utf-8"
    ) == "# Legacy architecture\n"


def test_apply_sync_plan_blocks_when_legacy_and_new_architecture_coexist(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/templates/01-architecture.md.template",
        "# Architecture scaffold\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "docs/architecture.md", "# Legacy architecture\n")
    write_file(target_root / "docs/01-local-architecture.md", "# New architecture\n")

    plan = build_sync_plan(source_root, target_root)

    assert ("manual", "docs/01-local-architecture.md") in {
        (operation.action, operation.path) for operation in plan.operations
    }
    with pytest.raises(RuntimeError, match="manual reconciliation"):
        apply_sync_plan(plan)


def test_build_sync_plan_deletes_legacy_runtime_fit_document(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / "docs/03-local-ai-runtime-operating-model.md", "# Runtime\n")
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "docs/runtime-fit.md", "# Runtime fit\n")

    plan = build_sync_plan(source_root, target_root)

    assert ("delete", "docs/runtime-fit.md") in {
        (operation.action, operation.path) for operation in plan.operations
    }


def test_build_sync_plan_includes_prompt_assets_in_managed_inventory(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/prompts/internal-agent-review-next-actions.prompt.md",
        "---\ndescription: Review next actions\n---\n",
    )
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")

    plan = build_sync_plan(source_root, target_root)
    actions = {(operation.action, operation.path) for operation in plan.operations}

    assert (
        "create",
        ".github/prompts/internal-agent-review-next-actions.prompt.md",
    ) in actions
    assert "## Prompts" in plan.generated_inventory
    assert (
        "- `.github/prompts/internal-agent-review-next-actions.prompt.md`"
        in plan.generated_inventory
    )


def test_apply_sync_plan_clears_plan_file_and_writes_manifest(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / "VERSION", "1.2.3\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(
        source_root / ".github/templates/copilot-instructions.override.md.template",
        "# Copilot Instructions Override\n\n- No active overrides in this repository.\n",
    )
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
    assert (target_root / ".github/copilot-instructions.override.md").exists()
    assert (target_root / ".github/copilot-instructions.override.md").read_text(
        encoding="utf-8"
    ) == (
        "# Copilot Instructions Override\n\n- No active overrides in this repository.\n"
    )
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


def test_sync_plan_json_reports_dirty_overlap_for_managed_mutations(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\nstale\n")
    write_file(target_root / ".gitignore", "/tmp/superpowers/\n")

    init_git_repo(target_root)
    commit_all(target_root, "Initial target state")

    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ndirty\n")
    write_file(target_root / "notes.txt", "target-only notes\n")

    plan = build_sync_plan(source_root, target_root)
    payload = plan.to_dict()

    assert payload["dirty_paths"] == [".github/copilot-instructions.md"]
    assert ".github/copilot-instructions.md" in payload["managed_mutation_paths"]
    assert payload["dirty_managed_overlap"] == [".github/copilot-instructions.md"]
    assert "notes.txt" not in payload["dirty_paths"]
    assert "notes.txt" not in payload["dirty_managed_overlap"]


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


def test_apply_sync_plan_preserves_multiple_lessons_rows_separated_by_blank_lines(
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
    target_lessons = (
        "# Lessons\n\n"
        "Target-managed retained learning ledger.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n"
        "| 2026-04-23 | Keep first lesson | pending | first.md |\n\n"
        "| 2026-04-21 | Keep second lesson | pending | second.md |\n"
    )

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / "LESSONS_LEARNED.md", source_lessons)
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "LESSONS_LEARNED.md", target_lessons)

    plan = build_sync_plan(source_root, target_root)

    assert ("update", "LESSONS_LEARNED.md") in {
        (operation.action, operation.path) for operation in plan.operations
    }

    apply_sync_plan(plan)

    assert (target_root / "LESSONS_LEARNED.md").read_text(encoding="utf-8") == (
        "# Lessons\n\n"
        "Source-managed retained learning ledger.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n"
        "| 2026-04-23 | Keep first lesson | pending | first.md |\n"
        "| 2026-04-21 | Keep second lesson | pending | second.md |\n"
    )


def test_apply_sync_plan_keeps_no_pending_marker_when_source_has_rows(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    source_lessons = (
        "# Lessons\n\n"
        "Source-managed retained learning ledger.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n"
        "| 2026-04-16 | Centralize shared Terraform lesson | pending | .github/instructions/internal-terraform.instructions.md |\n"
    )
    target_lessons = (
        "# Lessons\n\n"
        "Target-managed retained learning ledger.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n\n"
        "No pending lessons currently require codification.\n"
    )

    write_file(source_root / "AGENTS.md", "# AGENTS\nsource\n")
    write_file(source_root / ".github/copilot-instructions.md", "# Copilot\nsource\n")
    write_file(source_root / "LESSONS_LEARNED.md", source_lessons)
    write_file(target_root / "AGENTS.md", "# AGENTS\ntarget\n")
    write_file(target_root / ".github/copilot-instructions.md", "# Copilot\ntarget\n")
    write_file(target_root / "LESSONS_LEARNED.md", target_lessons)

    plan = build_sync_plan(source_root, target_root)

    assert ("update", "LESSONS_LEARNED.md") in {
        (operation.action, operation.path) for operation in plan.operations
    }

    apply_sync_plan(plan)

    assert (target_root / "LESSONS_LEARNED.md").read_text(encoding="utf-8") == (
        "# Lessons\n\n"
        "Source-managed retained learning ledger.\n\n"
        "## Pending Rules\n\n"
        "| Date | Lesson | Status | Intended canonical target |\n"
        "| --- | --- | --- | --- |\n\n"
        "No pending lessons currently require codification.\n"
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


def test_detect_token_risks_reports_root_always_on_budget(tmp_path: Path) -> None:
    write_file(tmp_path / "AGENTS.md", "# AGENTS\n\n" + ("Root policy line.\n" * 5000))
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot\n\n" + ("Projection policy line.\n" * 5000),
    )
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "root-always-on-budget" in finding_codes


def test_detect_token_risks_reports_agents_operational_procedure_markers(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path / "AGENTS.md",
        "# AGENTS\n\n"
        "## Retained Plans\n\n"
        "- Keep unresolved questions in `dubbi-e-domande.md`.\n"
        "- During execution, create matching `done-*` files.\n",
    )
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "agents-operational-procedure-marker" in finding_codes


def test_detect_token_risks_reports_copilot_review_window_missing_core_rules(
    tmp_path: Path,
) -> None:
    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        "# Copilot\n\n" + ("Repository background before critical rules.\n" * 150),
    )
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "copilot-review-window-missing-core-rules" in finding_codes


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
        "- Keep `.github/copilot-instructions.override.md` local to consumer repositories.\n",
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
        tmp_path / ".github/agents/local-sync-external-resources.agent.md",
        "---\nname: local-sync-external-resources\ntools: [read]\n---\n\n"
        "# Internal Sync External Resources\n\n"
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


def test_detect_token_risks_reports_paired_local_agent_skill_overlap(
    tmp_path: Path,
) -> None:
    shared_lines = "\n".join(
        [
            "- Keep the paired agent short.",
            "- The skill owns the reusable support workflow.",
            "- Keep references as the home for starter templates.",
            "- Re-check the paired bundle before finalizing.",
            "- Avoid cloning the same subtopic inventory in three places.",
            "- Leave routing and boundary language in the agent only.",
        ]
    )

    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    write_file(
        tmp_path / ".github/agents/local-sync-example.agent.md",
        "---\n"
        "name: local-sync-example\n"
        "tools: [read]\n"
        "---\n\n"
        "# Local Sync Example\n\n"
        "## Mandatory Engine Skills\n\n"
        "- `local-sync-example`\n\n"
        f"{shared_lines}\n",
    )
    write_file(
        tmp_path / ".github/skills/local-sync-example/SKILL.md",
        "---\n"
        "name: local-sync-example\n"
        "description: Local sync example\n"
        "---\n\n"
        "# Local Sync Example\n\n"
        f"{shared_lines}\n",
    )

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "paired-agent-skill-overlap" in finding_codes


def test_detect_token_risks_reports_unprofiled_imported_skill_description_budget(
    tmp_path: Path,
) -> None:
    long_description = (
        "Use when " + "optimizing cloud catalog trigger routing safely. " * 12
    )

    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    write_file(
        tmp_path / ".github/repo-profiles.yml",
        "version: 1\nprofiles:\n  minimal:\n    recommended_skills: []\n",
    )
    write_file(
        tmp_path / ".github/skills/awesome-long/SKILL.md",
        "---\n"
        "name: awesome-long\n"
        f"description: {long_description}\n"
        "---\n\n"
        "# Awesome Long\n",
    )

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "imported-skill-description-budget" in finding_codes


def test_detect_token_risks_reports_skill_description_trigger_collision(
    tmp_path: Path,
) -> None:
    description = "Use when reviewing repository-owned GitHub governance boundaries and validation evidence."

    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")
    write_file(tmp_path / ".github/copilot-instructions.md", "# Copilot\n")
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    write_file(
        tmp_path / ".github/skills/internal-one/SKILL.md",
        f"---\nname: internal-one\ndescription: {description}\n---\n\n# Internal One\n",
    )
    write_file(
        tmp_path / ".github/skills/internal-two/SKILL.md",
        f"---\nname: internal-two\ndescription: {description}\n---\n\n# Internal Two\n",
    )

    findings = detect_token_risks(tmp_path)
    finding_codes = {finding.code for finding in findings}

    assert "skill-description-trigger-collision" in finding_codes


def test_sync_contract_requires_target_local_validation_after_apply() -> None:
    sync_contract_text = Path(
        ".github/skills/local-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md"
    ).read_text(encoding="utf-8")

    assert (
        "run the closest target-local catalog or contract validation"
        in sync_contract_text
    )
    assert (
        "Treat any resulting fixes as consumer-local follow-up work"
        in sync_contract_text
    )


def test_sync_contract_requires_source_side_convergence_check_without_local_validator() -> (
    None
):
    sync_contract_text = Path(
        ".github/skills/local-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md"
    ).read_text(encoding="utf-8")

    assert (
        "When the target has no local catalog or contract validation script"
        in sync_contract_text
    )
    assert (
        "python3 ./.github/scripts/sync_copilot_catalog.py plan --target-repo <repo> --format json"
        in sync_contract_text
    )
    assert (
        "zero managed `create`, `update`, `ensure`, `rebuild`, or `delete` operations"
        in sync_contract_text
    )


def test_sync_contract_restricts_allow_dirty_target_to_overlap_checked_work() -> None:
    sync_contract_text = Path(
        ".github/skills/local-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md"
    ).read_text(encoding="utf-8")

    assert (
        "compare dirty paths against the planned managed mutations"
        in sync_contract_text
    )
    assert "do not use `--allow-dirty-target` as a blanket bypass" in sync_contract_text


def test_root_always_on_token_budget_contract_uses_validator_constants() -> None:
    agents_text = Path("AGENTS.md").read_text(encoding="utf-8")
    target_text = f"{ROOT_ALWAYS_ON_TOKEN_TARGET:,} estimated tokens"
    calculated_estimates = {
        file_path: estimate_tokens(Path(file_path))
        for file_path in ROOT_ALWAYS_ON_PATHS
    }

    assert "## Estimated Fixed-Load Token Budget" not in agents_text
    assert (
        "The critical always-on pair is `AGENTS.md` plus `.github/copilot-instructions.md`"
        in agents_text
    )
    assert target_text in agents_text
    assert "`make token-risks`" in agents_text
    assert set(calculated_estimates) == set(ROOT_ALWAYS_ON_PATHS)
