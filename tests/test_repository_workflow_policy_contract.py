from __future__ import annotations

from pathlib import Path

import yaml


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_repo_bridge_owns_github_pr_merge_and_terminal_state_guardrails() -> None:
    agents_text = read_text("AGENTS.md")
    copilot_text = read_text(".github/copilot-instructions.md")
    internal_contract_text = read_text("INTERNAL_CONTRACT.md")

    assert "For self-authored PRs under required-review policy" in agents_text
    assert "qualifying non-author approval" in agents_text
    assert "prefer `gh pr merge --squash`" in agents_text
    assert (
        "Treat organization-wide `gh search prs` results as eventually consistent"
        in agents_text
    )
    assert "`gh pr view --json state,mergedAt`" in agents_text
    assert "Follow `AGENTS.md` for repository workflow reminders" in copilot_text

    assert (
        "repository-workflow-github-pr-merge-and-terminal-state-reminders-stay-owned"
        in internal_contract_text
    )
    assert "qualifying non-author approval" in internal_contract_text
    assert "the strategic bridge prefers `gh pr merge --squash`" in internal_contract_text
    assert "`gh pr view --json state,mergedAt`" in internal_contract_text


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


def test_recent_lessons_are_codified_in_scoped_owners() -> None:
    python_instruction_text = read_text(
        ".github/instructions/internal-python.instructions.md"
    )
    github_actions_instruction_text = read_text(
        ".github/instructions/internal-github-actions.instructions.md"
    )
    github_actions_skill_text = read_text(
        ".github/skills/internal-github-actions/SKILL.md"
    )

    assert (
        "modify `sys.path` before importing a standalone script"
        in python_instruction_text
    )
    assert "# noqa: E402" in python_instruction_text
    assert "remove truly unused imports or variables" in python_instruction_text

    assert (
        "Do not place runner-derived paths such as `runner.temp` in workflow-root `env`"
        in github_actions_instruction_text
    )
    assert (
        "Smoke-testing a repository wrapper around an external CLI"
        in github_actions_skill_text
    )
    assert "even on `--dry-run` paths" in github_actions_skill_text
