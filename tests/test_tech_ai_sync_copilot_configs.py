from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "tech-ai-sync-copilot-configs.py"


def load_module():
    module_name = "tech_ai_sync_copilot_configs"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_eng_like_target(path: Path) -> None:
    write_file(path / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(path / "AGENTS.md", "# Manual AGENTS\n")
    write_file(path / "scripts" / "check.sh", "#!/usr/bin/env bash\nset -euo pipefail\n")
    write_file(path / "src" / "01_custom_roles" / "main.tf", 'resource "null_resource" "roles" {}\n')
    write_file(path / "src" / "02_policy_tags" / "main.tf", 'resource "null_resource" "policy" {}\n')
    write_file(path / "src" / "03_policy_set" / "main.tf", 'resource "null_resource" "set" {}\n')
    write_file(path / "src" / "04_policy_assignments" / "main.tf", 'resource "null_resource" "assign" {}\n')
    write_file(path / "src" / "scripts" / "policy_remediation.sh", "#!/usr/bin/env bash\nset -euo pipefail\n")


def build_python_service_target(path: Path) -> None:
    write_file(path / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(path / "src" / "app.py", 'def main() -> None:\n    print("hello")\n')


def build_script_automation_target(path: Path) -> None:
    write_file(path / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(path / "scripts" / "sync.sh", "#!/usr/bin/env bash\nset -euo pipefail\n")
    write_file(path / "src" / "scripts" / "report.py", 'def main() -> None:\n    print("report")\n')


def test_build_plan_detects_infrastructure_heavy_and_root_agents_conflict(tmp_path: Path) -> None:
    target_root = tmp_path / "eng-like"
    build_eng_like_target(target_root)

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.profile_name == "infrastructure-heavy"
    assert plan.analysis.agents_relative_path == "AGENTS.md"
    assert "src/01_custom_roles" in plan.analysis.priority_paths
    assert "src/02_policy_*" in plan.analysis.priority_paths
    assert any(
        action.target_relative_path == "AGENTS.md" and action.status == "conflict"
        for action in plan.actions
    )


def test_build_plan_normalizes_legacy_github_agents_to_root_path(tmp_path: Path) -> None:
    target_root = tmp_path / "legacy-agents"
    write_file(target_root / ".github" / "AGENTS.md", "# Legacy AGENTS\n")
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.agents_relative_path == "AGENTS.md"
    assert plan.analysis.agents_is_root is True


def test_build_plan_adopts_matching_source_files_and_reports_target_only_prompts(tmp_path: Path) -> None:
    target_root = tmp_path / "consumer"
    write_file(
        target_root / ".github" / "copilot-instructions.md",
        (REPO_ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8"),
    )
    write_file(
        target_root / ".github" / "prompts" / "create-policy.prompt.md",
        "---\nname: create-policy\ndescription: custom\nagent: agent\nargument-hint: test=true\n---\n",
    )
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    action = next(
        action for action in plan.actions if action.target_relative_path == ".github/copilot-instructions.md"
    )
    assert action.status == "adopt"
    missing_assets = "\n".join(plan.recommendations["missing instructions/prompts/skills"])
    assert "create-policy.prompt.md" in missing_assets


def test_apply_plan_writes_manifest_and_managed_files(tmp_path: Path) -> None:
    target_root = tmp_path / "fresh-target"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    plan, planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert not any(action.status == "conflict" for action in plan.actions if action.target_relative_path != "AGENTS.md")

    MODULE.apply_plan(target_root, plan, planned_files)

    manifest_path = target_root / ".github" / "tech-ai-sync-copilot-configs.manifest.json"
    agents_path = target_root / "AGENTS.md"
    assert manifest_path.is_file()
    assert agents_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "AGENTS.md" in manifest["managed_files"]
    assert ".github/copilot-instructions.md" in manifest["managed_files"]


def test_rendered_agents_markdown_keeps_github_copilot_wording(tmp_path: Path) -> None:
    target_root = tmp_path / "wording-target"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    _plan, planned_files = MODULE.build_plan(REPO_ROOT, target_root)
    agents_file = next(item for item in planned_files if item.target_relative_path == "AGENTS.md")

    assert "GitHub Copilot" in agents_file.desired_content
    assert "Codex" not in agents_file.desired_content


def test_main_supports_targets_without_existing_github_directory(tmp_path: Path, capsys) -> None:
    target_root = tmp_path / "no-github-yet"
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    report_file = tmp_path / "report.json"
    result = MODULE.main(
        [
            "--target",
            str(target_root),
            "--mode",
            "plan",
            "--report-format",
            "json",
            "--report-file",
            str(report_file),
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert report_file.is_file()
    assert '"profile": "infrastructure-heavy"' in captured.out


def test_build_plan_detects_backend_python_profile_and_python_validation_commands(tmp_path: Path) -> None:
    target_root = tmp_path / "python-service"
    build_python_service_target(target_root)

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.profile_name == "backend-python"
    assert "python -m compileall <changed_python_paths>" in plan.selection.validation_commands
    assert "pytest" in plan.selection.validation_commands
    assert ".github/prompts/tech-ai-python.prompt.md" in plan.selection.prompts


def test_build_plan_prefers_tech_ai_script_prompts_to_reduce_prompt_duplication(tmp_path: Path) -> None:
    target_root = tmp_path / "automation"
    build_script_automation_target(target_root)

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert ".github/prompts/tech-ai-bash-script.prompt.md" in plan.selection.prompts
    assert ".github/prompts/tech-ai-python-script.prompt.md" in plan.selection.prompts
    assert ".github/prompts/tech-ai-add-unit-tests.prompt.md" in plan.selection.prompts
    assert ".github/prompts/script-bash.prompt.md" not in plan.selection.prompts
    assert ".github/prompts/script-python.prompt.md" not in plan.selection.prompts


def test_build_plan_reports_unsupported_go_and_docker_stacks(tmp_path: Path) -> None:
    target_root = tmp_path / "polyglot"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "Dockerfile", "FROM alpine:3.21\n")
    write_file(target_root / "main.go", "package main\n\nfunc main() {}\n")

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.unsupported_stacks == ["docker", "go"]
    recommendations = "\n".join(plan.recommendations["missing instructions/prompts/skills"])
    assert "unsupported target stacks: docker, go" in recommendations


def test_build_plan_fails_for_corrupted_manifest(tmp_path: Path) -> None:
    target_root = tmp_path / "broken-manifest"
    build_python_service_target(target_root)
    write_file(target_root / MODULE.MANIFEST_RELATIVE_PATH, "{not-json}\n")

    with pytest.raises(MODULE.CliError, match="Invalid JSON manifest"):
        MODULE.build_plan(REPO_ROOT, target_root)


def test_main_writes_json_report_with_selection_and_actions(tmp_path: Path) -> None:
    target_root = tmp_path / "json-report"
    build_python_service_target(target_root)

    report_file = tmp_path / "tech-ai-sync-report.json"
    result = MODULE.main(
        [
            "--target",
            str(target_root),
            "--mode",
            "plan",
            "--report-format",
            "json",
            "--report-file",
            str(report_file),
        ]
    )

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert result == 0
    assert payload["tool"] == "TechAISyncCopilotConfigs"
    assert payload["analysis"]["profile"] == "backend-python"
    assert ".github/prompts/tech-ai-python.prompt.md" in payload["selection"]["prompts"]
    assert any(action["status"] == "create" for action in payload["actions"])
