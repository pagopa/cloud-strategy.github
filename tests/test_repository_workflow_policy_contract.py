from __future__ import annotations

import re
from pathlib import Path

import yaml


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def section_between(body: str, heading: str) -> str:
    section = body.split(heading, 1)[1]
    return section.split("\n## ", 1)[0]


def python_fenced_blocks(body: str) -> list[str]:
    return re.findall(r"```python\n(.*?)\n```", body, flags=re.DOTALL)


def test_github_pr_skill_owns_pr_merge_and_terminal_state_guardrails() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")
    github_pr_skill_text = read_text(".github/skills/internal-github-pr/SKILL.md")
    github_governance_skill_text = read_text(
        ".github/skills/internal-github-governance/SKILL.md"
    )
    inventory_text = read_text(".github/INVENTORY.md")
    internal_contract_text = read_text("INTERNAL_CONTRACT.md")

    assert "## Repository Workflow Reminders" not in agents_text
    assert "For self-authored PRs under required-review policy" in github_pr_skill_text
    assert "qualifying non-author approval" in github_pr_skill_text
    assert "Prefer `gh pr merge --squash`" in github_pr_skill_text
    assert (
        "Treat organization-wide `gh search prs` results as eventually consistent"
        in github_pr_skill_text
    )
    assert "`gh pr view --json state,mergedAt`" in github_pr_skill_text
    assert "Follow `AGENTS.md` for repository workflow reminders" not in copilot_text
    assert "@your-org/platform-governance-team" in github_governance_skill_text
    assert ".github/skills/internal-github-pr/SKILL.md" in inventory_text
    assert ".github/skills/internal-pr-editor/SKILL.md" not in inventory_text
    assert ".github/skills/internal-github-governance/SKILL.md" in inventory_text

    assert (
        "repository-workflow-github-pr-merge-and-terminal-state-reminders-stay-owned"
        in internal_contract_text
    )
    assert "qualifying non-author approval" in internal_contract_text
    assert (
        "the GitHub PR skill prefers `gh pr merge --squash`" in internal_contract_text
    )
    assert "`gh pr view --json state,mergedAt`" in internal_contract_text


def test_root_files_define_scoped_instruction_loading_for_manual_runtimes() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")

    assert "## First Move" in agents_text
    assert "## Precedence" in agents_text
    assert "Resolve conflicts with the smallest valid owner." in agents_text
    assert "fallback policy, not permission to override narrower contracts." in agents_text

    assert "## Scope And Placement" in agents_text
    assert "operational procedures, checklists, file-shape recipes" in agents_text
    assert ".github/instructions" not in agents_text
    assert "bridge" not in agents_text.lower()

    assert "`<shared-baseline>`" in agents_text
    assert "This block is the portable baseline" in agents_text
    assert "`<standards-repository-local-rules>`" in agents_text
    assert "This block applies only to this standards repository." in agents_text

    assert "It is not a general task-execution guide" in copilot_text
    assert "Do not ask the author to follow local runtime workflows" in copilot_text
    assert "that GitHub.com cannot" in copilot_text
    assert "execute." in copilot_text
    assert (
        "Do not treat this file as instructions for coding agents, local CLIs, or"
        in copilot_text
    )


def test_agents_keeps_only_intentional_root_level_workflows() -> None:
    agents_text = read_text("AGENTS.md")

    assert "tool-specific workflows here" in agents_text
    assert "Do not duplicate skill-owned paths" in agents_text
    assert "## graphify" in agents_text
    assert "When the user types `/graphify`" in agents_text
    assert 'graphify query "<question>"' in agents_text
    assert (
        "Only skip graphify if the task is about stale or incorrect graph output"
        in agents_text
    )


def test_agents_tactical_defaults_include_compact_context_discipline() -> None:
    agents_text = read_text("AGENTS.md")

    assert "## Tactical Defaults" in agents_text
    assert "Preserve compact working state across turns" in agents_text
    assert "Keep one active primary owner per execution lane" in agents_text
    assert "Use bounded evidence" in agents_text
    assert "Name the validation path early" in agents_text


def test_lightweight_skill_references_stay_on_demand() -> None:
    checklist_text = read_text(
        ".github/skills/internal-skill-creator/references/writing-skills-checklist.md"
    )
    support_routing_text = read_text(
        ".github/skills/internal-gateway-simple-task/references/support-routing.md"
    )

    assert (
        "`## Referenced skills` as an audit index, not a preload bundle"
        in checklist_text
    )
    assert (
        "Add file extensions or path tokens in `description:` only when they materially disambiguate the owner"
        in checklist_text
    )
    assert (
        "Treat a support skill's `## Referenced skills` section as an owner index"
        in support_routing_text
    )
    assert "prefer the single narrowest owner proved by that" in support_routing_text

    lightweight_skill_paths = (
        ".github/skills/internal-bash/SKILL.md",
        ".github/skills/internal-go/SKILL.md",
        ".github/skills/internal-java/SKILL.md",
        ".github/skills/internal-nodejs/SKILL.md",
        ".github/skills/internal-python/SKILL.md",
        ".github/skills/internal-yaml/SKILL.md",
        ".github/skills/internal-kubernetes/SKILL.md",
        ".github/skills/internal-terraform/SKILL.md",
    )

    for relative_path in lightweight_skill_paths:
        referenced_section = section_between(
            read_text(relative_path), "## Referenced skills"
        )

        assert "on-demand" in referenced_section
        assert "Do not preload" in referenced_section
        assert "only when" in referenced_section


def test_lightweight_workflow_and_review_skills_keep_references_on_demand() -> None:
    skill_paths = (
        ".github/skills/internal-gateway-idea-brainstorming/SKILL.md",
        ".github/skills/internal-debugging/SKILL.md",
        ".github/skills/internal-high-level-review/SKILL.md",
        ".github/skills/internal-github-pr/SKILL.md",
        ".github/skills/internal-github-actions/SKILL.md",
        ".github/skills/internal-github-action-composite/SKILL.md",
        ".github/skills/internal-azure-devops/SKILL.md",
    )

    for relative_path in skill_paths:
        referenced_section = section_between(
            read_text(relative_path), "## Referenced skills"
        )

        assert "on-demand" in referenced_section
        assert "Do not preload" in referenced_section
        assert "only the owner proved" in referenced_section


def test_terraform_lock_matrix_policy_stays_visible() -> None:
    terraform_skill_text = read_text(".github/skills/internal-terraform/SKILL.md")
    precommit_text = read_text(".pre-commit-config.yaml")

    assert "canonical lock platform matrix" in terraform_skill_text
    assert (
        "`terraform_providers_lock` block in the repo `.pre-commit-config.yaml`"
        in terraform_skill_text
    )
    assert (
        "If `.terraform.lock.hcl` changes or checksum mismatches appear"
        in terraform_skill_text
    )

    assert (
        "Keep this hook commented to avoid slowing normal pre-commit runs."
        in precommit_text
    )
    assert (
        "Treat the platform list below as the canonical `.terraform.lock.hcl` matrix."
        in precommit_text
    )


def test_dependabot_tracks_source_repository_dependency_manifests() -> None:
    dependabot_config = yaml.safe_load(read_text(".github/dependabot.yml"))
    updates = {
        (entry["package-ecosystem"], entry["directory"]): entry
        for entry in dependabot_config["updates"]
    }

    assert ("github-actions", "/") in updates
    assert ("pip", "/.github/scripts") in updates
    assert ("pre-commit", "/") in updates
    assert Path(".github/scripts/requirements.txt").exists()
    assert Path(".pre-commit-config.yaml").exists()
    assert (
        "python-tooling-minor-patch" in updates[("pip", "/.github/scripts")]["groups"]
    )
    assert "pre-commit-minor-patch" in updates[("pre-commit", "/")]["groups"]


def test_recent_lessons_are_codified_in_skill_owners() -> None:
    python_skill_text = read_text(".github/skills/internal-python/SKILL.md")
    github_actions_skill_text = read_text(
        ".github/skills/internal-github-actions/SKILL.md"
    )

    assert "modify `sys.path` before importing a standalone script" in python_skill_text
    assert "# noqa: E402" in python_skill_text
    assert "remove truly unused imports or variables" in python_skill_text

    assert (
        "Using `runner.temp` or other runner-scoped contexts in workflow-root `env`"
        in github_actions_skill_text
    )
    assert (
        "Smoke-testing a repository wrapper around an external CLI"
        in github_actions_skill_text
    )
    assert "even on `--dry-run` paths" in github_actions_skill_text


def test_technology_skill_modularity_contract_is_owned_and_searchable() -> None:
    python_skill_text = read_text(".github/skills/internal-python/SKILL.md").lower()
    python_script_skill_text = read_text(
        ".github/skills/internal-python-script/SKILL.md"
    ).lower()
    python_project_skill_text = read_text(
        ".github/skills/internal-python-project/SKILL.md"
    ).lower()
    bash_skill_text = read_text(".github/skills/internal-bash/SKILL.md").lower()
    bash_script_skill_text = read_text(
        ".github/skills/internal-bash-script/SKILL.md"
    ).lower()
    node_skill_text = read_text(".github/skills/internal-nodejs/SKILL.md").lower()
    node_project_skill_text = read_text(
        ".github/skills/internal-nodejs-project/SKILL.md"
    ).lower()
    java_skill_text = read_text(".github/skills/internal-java/SKILL.md").lower()
    java_project_skill_text = read_text(
        ".github/skills/internal-java-project/SKILL.md"
    ).lower()

    base_skill_texts = (
        python_skill_text,
        bash_skill_text,
        node_skill_text,
        java_skill_text,
    )

    for body in base_skill_texts:
        assert "300" in body
        assert "400" in body
        assert "split-or-justify" in body
        assert "dry" in body

    assert "entrypoint" in python_script_skill_text
    assert "utils/" in python_script_skill_text
    assert "single-file" in python_script_skill_text
    assert "toolkit" in python_script_skill_text
    assert "project" in python_script_skill_text
    assert "generated" in python_script_skill_text
    assert "fixture" in python_script_skill_text
    assert "## referenced skills" in python_script_skill_text
    assert "internal-tdd" in python_script_skill_text
    assert "references/reporting.md" in python_script_skill_text
    assert "executionreporter" in python_script_skill_text
    assert "rich" in python_script_skill_text
    assert "test-first" in python_script_skill_text
    assert "pip install --require-hashes" in python_script_skill_text

    assert "entrypoint" in bash_script_skill_text
    assert "sourced helper" in bash_script_skill_text

    assert "thin" in node_project_skill_text
    assert "async boundaries" in node_project_skill_text

    assert "thin" in java_project_skill_text
    assert "god class" in java_project_skill_text
    assert "dto" in java_project_skill_text

    assert "domain/service/adapter" in python_project_skill_text
    assert "## referenced skills" in python_project_skill_text
    assert "internal-tdd" in python_project_skill_text
    assert "structured" in python_project_skill_text
    assert "rich" in python_project_skill_text
    assert "cli adapter" in python_project_skill_text
    assert "no emoji" in python_project_skill_text
    assert "references/logging-and-reporting.md" in python_project_skill_text
    assert "typed results" in python_project_skill_text
    assert "machine-readable" in python_project_skill_text


def test_python_skill_template_snippets_are_copyable_python() -> None:
    template_paths = (
        ".github/skills/internal-python-project/references/logging-and-reporting.md",
        ".github/skills/internal-python-script/references/layout-and-templates.md",
        ".github/skills/internal-python-script/references/reporting.md",
    )

    for relative_path in template_paths:
        blocks = python_fenced_blocks(read_text(relative_path))
        assert blocks, f"{relative_path} should contain Python fenced snippets"

        for index, block in enumerate(blocks, start=1):
            compile(block, f"{relative_path}:python-block-{index}", "exec")
