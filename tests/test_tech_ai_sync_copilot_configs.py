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


def build_source_audit_fixture(path: Path) -> None:
    write_file(
        path / "AGENTS.md",
        "\n".join(
            [
                "# AGENTS.md - fixture",
                "",
                "## Preferred prompts",
                "- `prompts/tech-ai-python.prompt.md`",
                "",
                "## Repository Inventory (Auto-generated)",
                "",
                "### Prompts",
                "- `.github/prompts/tech-ai-python.prompt.md`",
                "",
            ]
        ),
    )
    write_file(
        path / ".github" / "prompts" / "tech-ai-python.prompt.md",
        "\n".join(
            [
                "---",
                "name: TechAIPython",
                "description: canonical",
                "agent: agent",
                "argument-hint: target=python",
                "---",
                "",
                "# Python",
                "",
            ]
        ),
    )
    write_file(
        path / ".github" / "prompts" / "cs-python.prompt.md",
        "\n".join(
            [
                "---",
                "name: cs-python",
                "description: legacy",
                "agent: agent",
                "argument-hint: target=python",
                "---",
                "",
                "# Legacy Python",
                "",
            ]
        ),
    )
    shared_steps = [
        "1. Inspect the target repository layout and current Copilot assets.",
        "2. Run the sync script in plan mode before any apply step.",
        "3. Report redundant aliases before rendering AGENTS inventory.",
    ]
    write_file(
        path / ".github" / "agents" / "tech-ai-sync-global-copilot-configs-into-repo.agent.md",
        "\n".join(
            [
                "---",
                "name: TechAISyncGlobalCopilotConfigsIntoRepo",
                "description: sync agent",
                'tools: ["search"]',
                "---",
                "",
                "# Agent",
                "",
                "## Workflow",
                *shared_steps,
                "",
            ]
        ),
    )
    write_file(
        path / ".github" / "skills" / "tech-ai-sync-global-copilot-configs-into-repo" / "SKILL.md",
        "\n".join(
            [
                "---",
                "name: TechAISyncGlobalCopilotConfigsIntoRepo",
                "description: sync skill",
                "---",
                "",
                "# Skill",
                "",
                "## Workflow",
                *shared_steps,
                "",
            ]
        ),
    )
    write_file(
        path / ".github" / "prompts" / "tech-ai-sync-global-copilot-configs-into-repo.prompt.md",
        "\n".join(
            [
                "---",
                "name: TechAISyncGlobalCopilotConfigsIntoRepo",
                "description: sync prompt",
                "agent: agent",
                "argument-hint: target_repo=<path>",
                "---",
                "",
                "# Prompt",
                "",
                "## Instructions",
                *shared_steps,
                "",
            ]
        ),
    )


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


def test_build_plan_reports_unmanaged_target_assets_and_legacy_aliases_outside_selected_profile(tmp_path: Path) -> None:
    target_root = tmp_path / "unmanaged-assets"
    build_python_service_target(target_root)
    write_file(
        target_root / ".github" / "prompts" / "add-external-user.prompt.md",
        "\n".join(
            [
                "---",
                "agent: edit",
                "description: Add an external user to Azure AD",
                "---",
                "",
                "# Add External User",
                "",
                "## Instructions",
                "- Update the external user registry.",
                "",
                "## Validations",
                "- Keep JSON valid.",
                "",
            ]
        ),
    )
    write_file(
        target_root / ".github" / "prompts" / "cs-data-registry.prompt.md",
        "\n".join(
            [
                "---",
                "description: Add or modify entries in structured JSON/YAML registry files",
                "name: cs-data-registry",
                "agent: agent",
                "argument-hint: action=<create|modify|remove> file=<path> key=<identifier> change=<summary>",
                "---",
                "",
                "# Data Registry Task",
                "",
                "## Instructions",
                "1. Use `.github/skills/data-registry/SKILL.md`.",
                "",
                "## Minimal example",
                "- Input: `action=modify file=data.json key=user change=disable`",
                "",
                "## Validation",
                "- Validate JSON syntax.",
                "",
            ]
        ),
    )
    write_file(
        target_root / ".github" / "skills" / "data-registry" / "SKILL.md",
        "\n".join(
            [
                "---",
                "name: data-registry",
                "description: Safely update structured JSON/YAML registry files.",
                "---",
                "",
                "# Data Registry Skill",
                "",
                "## When to use",
                "- Update structured data safely.",
                "",
                "## Validation",
                "- Validate syntax and duplicate keys.",
                "",
            ]
        ),
    )
    write_file(
        target_root / ".github" / "skills" / "internal-registry" / "SKILL.md",
        "\n".join(
            [
                "---",
                "name: internal-registry",
                "description: Custom local registry helper.",
                "---",
                "",
                "# Local Registry Skill",
                "",
                "## When to use",
                "- Maintain a custom local registry.",
                "",
                "## Validation",
                "- Validate repository-local data.",
                "",
            ]
        ),
    )

    plan, planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    issue_by_path = {issue.target_relative_path: issue for issue in plan.target_asset_issues}
    agents_file = next(item for item in planned_files if item.target_relative_path == "AGENTS.md")

    assert ".github/prompts/add-external-user.prompt.md" in plan.analysis.target_only_assets["prompts"]
    assert ".github/skills/internal-registry/SKILL.md" in plan.analysis.target_only_assets["skills"]
    assert ".github/prompts/cs-data-registry.prompt.md" not in plan.analysis.target_only_assets["prompts"]
    assert ".github/skills/data-registry/SKILL.md" not in plan.analysis.target_only_assets["skills"]

    assert any(
        asset.canonical_target_path == ".github/prompts/tech-ai-data-registry.prompt.md"
        and asset.issue_type == "legacy_alias_only"
        for asset in plan.redundant_assets
    )
    assert any(
        asset.canonical_target_path == ".github/skills/tech-ai-data-registry/SKILL.md"
        and asset.issue_type == "legacy_alias_only"
        for asset in plan.redundant_assets
    )

    assert "validation" in issue_by_path[".github/prompts/add-external-user.prompt.md"].issue_types
    assert "internal_naming" in issue_by_path[".github/prompts/add-external-user.prompt.md"].issue_types
    assert "Missing frontmatter key `name`." in issue_by_path[".github/prompts/add-external-user.prompt.md"].details
    assert (
        "Repository-internal prompt filename must start with `internal-`."
        in issue_by_path[".github/prompts/add-external-user.prompt.md"].details
    )
    assert "legacy_alias" in issue_by_path[".github/prompts/cs-data-registry.prompt.md"].issue_types
    assert (
        issue_by_path[".github/prompts/cs-data-registry.prompt.md"].canonical_source_path
        == ".github/prompts/tech-ai-data-registry.prompt.md"
    )
    assert ".github/skills/internal-registry/SKILL.md" not in issue_by_path

    assert ".github/prompts/add-external-user.prompt.md" in agents_file.desired_content
    assert ".github/prompts/cs-data-registry.prompt.md" in agents_file.desired_content
    assert ".github/skills/data-registry/SKILL.md" in agents_file.desired_content
    assert ".github/skills/internal-registry/SKILL.md" in agents_file.desired_content


def test_build_plan_accepts_internal_prefixed_repo_owned_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "internal-assets"
    build_python_service_target(target_root)
    write_file(
        target_root / ".github" / "prompts" / "internal-add-external-user.prompt.md",
        "\n".join(
            [
                "---",
                "name: internal-add-external-user",
                "description: Add an external user to Entra ID.",
                "agent: agent",
                "argument-hint: user=<email>",
                "---",
                "",
                "# Local Add External User",
                "",
                "## Instructions",
                "1. Use `.github/skills/internal-entra-access/SKILL.md`.",
                "",
                "## Validation",
                "- Validate the repository-local registry update.",
                "",
                "## Minimal example",
                "- Input: `user=guest@example.com`",
                "",
            ]
        ),
    )
    write_file(
        target_root / ".github" / "skills" / "internal-entra-access" / "SKILL.md",
        "\n".join(
            [
                "---",
                "name: internal-entra-access",
                "description: Repository-internal Entra access workflow.",
                "---",
                "",
                "# Local Entra Access",
                "",
                "## When to use",
                "- Manage repository-local Entra access automation.",
                "",
                "## Validation",
                "- Validate repository-local access rules.",
                "",
            ]
        ),
    )

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    issue_paths = {issue.target_relative_path for issue in plan.target_asset_issues}
    assert ".github/prompts/internal-add-external-user.prompt.md" not in issue_paths
    assert ".github/skills/internal-entra-access/SKILL.md" not in issue_paths


def test_apply_plan_writes_manifest_and_managed_files(tmp_path: Path) -> None:
    target_root = tmp_path / "fresh-target"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    plan, planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert not any(action.status == "conflict" for action in plan.actions if action.target_relative_path != "AGENTS.md")

    MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    manifest_path = target_root / ".github" / "tech-ai-sync-copilot-configs.manifest.json"
    agents_path = target_root / "AGENTS.md"
    assert manifest_path.is_file()
    assert agents_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "AGENTS.md" in manifest["managed_files"]
    assert ".github/copilot-instructions.md" in manifest["managed_files"]
    assert manifest["source_version"] == (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert len(manifest["source_commit"]) == 40


def test_rendered_agents_markdown_keeps_github_copilot_wording(tmp_path: Path) -> None:
    target_root = tmp_path / "wording-target"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')

    plan, planned_files = MODULE.build_plan(REPO_ROOT, target_root)
    agents_file = next(item for item in planned_files if item.target_relative_path == "AGENTS.md")
    expected_prompt_path = plan.selection.prompts[0]
    expected_skill_path = plan.selection.skills[0]

    assert "GitHub Copilot" in agents_file.desired_content
    assert "Codex" not in agents_file.desired_content
    assert "## Available Skills" not in agents_file.desired_content
    assert "## Available Prompts" not in agents_file.desired_content
    assert agents_file.desired_content.count(expected_prompt_path) == 1
    assert agents_file.desired_content.count(expected_skill_path) == 1


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
    assert "pytest" not in plan.selection.validation_commands
    assert ".github/prompts/tech-ai-python.prompt.md" in plan.selection.prompts


def test_build_plan_adds_pytest_only_when_repo_contains_pytest_tests(tmp_path: Path) -> None:
    target_root = tmp_path / "python-service-with-tests"
    build_python_service_target(target_root)
    write_file(target_root / "tests" / "test_app.py", 'def test_placeholder() -> None:\n    assert True\n')

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert "pytest" in plan.selection.validation_commands


def test_build_plan_prefers_tech_ai_script_prompts_to_reduce_prompt_duplication(tmp_path: Path) -> None:
    target_root = tmp_path / "automation"
    build_script_automation_target(target_root)

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert ".github/prompts/tech-ai-bash-script.prompt.md" in plan.selection.prompts
    assert ".github/prompts/tech-ai-python-script.prompt.md" in plan.selection.prompts
    assert ".github/prompts/tech-ai-add-unit-tests.prompt.md" in plan.selection.prompts
    assert ".github/prompts/script-bash.prompt.md" not in plan.selection.prompts
    assert ".github/prompts/script-python.prompt.md" not in plan.selection.prompts


def test_build_plan_flags_legacy_prompt_aliases_before_creating_canonical_duplicates(tmp_path: Path) -> None:
    target_root = tmp_path / "legacy-prompt-aliases"
    build_python_service_target(target_root)
    write_file(
        target_root / ".github" / "prompts" / "cs-python.prompt.md",
        "---\nname: cs-python\ndescription: legacy\nagent: agent\nargument-hint: test=true\n---\n",
    )

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    prompt_action = next(
        action for action in plan.actions if action.target_relative_path == ".github/prompts/tech-ai-python.prompt.md"
    )
    agents_action = next(action for action in plan.actions if action.target_relative_path == "AGENTS.md")

    assert prompt_action.status == "conflict"
    assert "redundant configuration" in prompt_action.reason
    assert agents_action.status == "conflict"
    assert ".github/prompts/cs-python.prompt.md" not in plan.analysis.target_only_assets["prompts"]
    assert any(
        asset.canonical_target_path == ".github/prompts/tech-ai-python.prompt.md"
        and asset.issue_type == "sync_would_duplicate"
        for asset in plan.redundant_assets
    )


def test_build_plan_flags_existing_canonical_and_legacy_agent_aliases_as_redundant(tmp_path: Path) -> None:
    target_root = tmp_path / "duplicate-agents"
    build_python_service_target(target_root)
    write_file(
        target_root / ".github" / "agents" / "tech-ai-planner.agent.md",
        (REPO_ROOT / ".github" / "agents" / "tech-ai-planner.agent.md").read_text(encoding="utf-8"),
    )
    write_file(
        target_root / ".github" / "agents" / "planner.agent.md",
        "---\nname: planner\ndescription: legacy\ntools: []\n---\n# Planner\n\n## Objective\nlegacy\n\n## Restrictions\nlegacy\n",
    )

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    action = next(
        action for action in plan.actions if action.target_relative_path == ".github/agents/tech-ai-planner.agent.md"
    )

    assert action.status == "conflict"
    assert ".github/agents/planner.agent.md" in action.reason
    assert any(
        asset.canonical_target_path == ".github/agents/tech-ai-planner.agent.md"
        and asset.issue_type == "existing_redundancy"
        for asset in plan.redundant_assets
    )


def test_audit_source_configuration_detects_legacy_aliases_role_overlaps_and_agents_repeats(tmp_path: Path) -> None:
    source_root = tmp_path / "source-audit"
    build_source_audit_fixture(source_root)

    audit = MODULE.audit_source_configuration(source_root)

    assert any(alias.canonical_path == ".github/prompts/tech-ai-python.prompt.md" for alias in audit.legacy_aliases)
    assert any(overlap.family == "sync-copilot-configs" for overlap in audit.role_overlaps)
    assert any(repeat.reference == ".github/prompts/tech-ai-python.prompt.md" for repeat in audit.agents_md_repeats)


def test_audit_source_configuration_does_not_flag_canonical_only_assets(tmp_path: Path) -> None:
    source_root = tmp_path / "canonical-only"
    write_file(source_root / "AGENTS.md", "# AGENTS.md - fixture\n")
    write_file(
        source_root / ".github" / "prompts" / "tech-ai-python.prompt.md",
        "---\nname: TechAIPython\ndescription: canonical\nagent: agent\nargument-hint: target=python\n---\n",
    )

    audit = MODULE.audit_source_configuration(source_root)

    assert not audit.legacy_aliases
    assert not audit.role_overlaps
    assert not audit.agents_md_repeats


def test_build_plan_excludes_repo_only_global_customization_agents_from_consumer_selection(tmp_path: Path) -> None:
    target_root = tmp_path / "python-service"
    build_python_service_target(target_root)

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert ".github/agents/tech-ai-standards-repo-config-builder.agent.md" not in plan.selection.agents
    assert ".github/agents/tech-ai-standards-repo-config-auditor.agent.md" not in plan.selection.agents


def test_internal_builder_triads_are_source_only_and_excluded_from_consumer_sync() -> None:
    assert (
        ".github/agents/tech-ai-repo-copilot-extender.agent.md"
        in MODULE.SOURCE_ONLY_AGENT_PATHS
    )
    assert (
        ".github/prompts/tech-ai-repo-copilot-extender.prompt.md"
        in MODULE.SOURCE_ONLY_PROMPT_PATHS
    )
    assert (
        ".github/skills/tech-ai-repo-copilot-extender/SKILL.md"
        in MODULE.SOURCE_ONLY_SKILL_PATHS
    )


def test_build_plan_reports_unsupported_go_and_docker_stacks(tmp_path: Path) -> None:
    target_root = tmp_path / "polyglot"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(target_root / "Dockerfile", "FROM alpine:3.21\n")
    write_file(target_root / "main.go", "package main\n\nfunc main() {}\n")

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.unsupported_stacks == ["docker", "go"]
    recommendations = "\n".join(plan.recommendations["missing instructions/prompts/skills"])
    assert "unsupported target stacks: docker, go" in recommendations


def test_build_plan_detects_composite_actions_under_workflows_tree(tmp_path: Path) -> None:
    target_root = tmp_path / "workflow-composite"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(
        target_root / ".github" / "workflows" / "shared" / "action.yml",
        "\n".join(
            [
                "name: shared",
                "runs:",
                "  using: composite",
                "  steps:",
                "    - shell: bash",
                '      run: echo "ok"',
                "",
            ]
        ),
    )

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert "composite-action" in plan.analysis.stacks
    assert ".github/instructions/github-action-composite.instructions.md" in plan.selection.instructions
    assert ".github/prompts/tech-ai-github-composite-action.prompt.md" in plan.selection.prompts


def test_build_plan_adds_data_registry_assets_for_json_heavy_repositories(tmp_path: Path) -> None:
    target_root = tmp_path / "json-heavy"
    write_file(target_root / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    for index in range(5):
        write_file(target_root / "data" / f"registry-{index}.json", '{"enabled": true}\n')

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    assert ".github/prompts/tech-ai-data-registry.prompt.md" in plan.selection.prompts
    assert ".github/skills/tech-ai-data-registry/SKILL.md" in plan.selection.skills


def test_rendered_agents_markdown_uses_explicit_github_paths_and_table_routing(tmp_path: Path) -> None:
    target_root = tmp_path / "rendered-agents"
    build_python_service_target(target_root)

    _plan, planned_files = MODULE.build_plan(REPO_ROOT, target_root)
    agents_file = next(item for item in planned_files if item.target_relative_path == "AGENTS.md")

    assert "Apply repository non-negotiables from `.github/copilot-instructions.md`." in agents_file.desired_content
    assert "| Pattern | Instruction |" in agents_file.desired_content
    assert "Apply all non-negotiables from `.github/copilot-instructions.md` plus:" in agents_file.desired_content
    assert "- `TechAIAddUnitTests`" in agents_file.desired_content
    assert "- `TechAICICDWorkflow`" in agents_file.desired_content
    assert ": Add or improve unit tests for Python code" not in agents_file.desired_content


def test_build_plan_reports_missing_validation_workflow_and_source_only_residues(tmp_path: Path) -> None:
    target_root = tmp_path / "consumer-residue"
    build_python_service_target(target_root)
    write_file(target_root / ".github" / "README.md", "# source-only\n")
    write_file(target_root / ".github" / "agents" / "README.md", "# source-only\n")
    write_file(target_root / ".github" / "templates" / "AGENTS.template.md", "# source-only\n")
    write_file(target_root / ".github" / "scripts" / "bootstrap-copilot-config.sh", "#!/usr/bin/env bash\n")

    plan, _planned_files = MODULE.build_plan(REPO_ROOT, target_root)

    guidance = "\n".join(plan.recommendations["missing consumer-facing validation or onboarding guidance"])
    assert "github-validate-copilot-customizations.yml" in guidance
    assert ".github/README.md" in guidance
    assert ".github/agents/README.md" in guidance
    assert ".github/templates/**" in guidance
    assert ".github/scripts/bootstrap-copilot-config.sh" in guidance


def test_build_plan_fails_for_corrupted_manifest(tmp_path: Path) -> None:
    target_root = tmp_path / "broken-manifest"
    build_python_service_target(target_root)
    write_file(target_root / MODULE.MANIFEST_RELATIVE_PATH, "{not-json}\n")

    with pytest.raises(MODULE.CliError, match="Invalid JSON manifest"):
        MODULE.build_plan(REPO_ROOT, target_root)


def test_main_writes_json_report_with_selection_and_actions(tmp_path: Path) -> None:
    target_root = tmp_path / "json-report"
    build_python_service_target(target_root)
    write_file(
        target_root / ".github" / "prompts" / "add-external-user.prompt.md",
        "---\nagent: edit\ndescription: invalid custom prompt\n---\n# Add External User\n\n## Instructions\n- Update registry.\n",
    )

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
    assert payload["tool"] == "TechAISyncGlobalCopilotConfigsIntoRepo"
    assert payload["analysis"]["profile"] == "backend-python"
    assert ".github/prompts/tech-ai-python.prompt.md" in payload["selection"]["prompts"]
    assert "redundant_assets" in payload["analysis"]
    assert "unmanaged_target_asset_issues" in payload["analysis"]
    assert any(
        issue["target_relative_path"] == ".github/prompts/add-external-user.prompt.md"
        and "validation" in issue["issue_types"]
        for issue in payload["analysis"]["unmanaged_target_asset_issues"]
    )
    assert any(
        "github-validate-copilot-customizations.yml" in item
        for item in payload["recommendations"]["missing consumer-facing validation or onboarding guidance"]
    )
    assert sorted(payload["source_audit"].keys()) == [
        "agents_md_repeats",
        "canonical_assets",
        "legacy_aliases",
        "recommendations",
        "role_overlaps",
    ]
    assert any(action["status"] == "create" for action in payload["actions"])


def test_current_source_repo_audit_has_no_sync_role_overlap_or_agents_inventory_repeats() -> None:
    audit = MODULE.audit_source_configuration(REPO_ROOT)

    assert not audit.legacy_aliases
    assert not any(overlap.family == "sync-copilot-configs" for overlap in audit.role_overlaps)
    assert not audit.agents_md_repeats
