from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_repo_projection_keeps_github_pr_merge_and_terminal_state_guardrails() -> None:
    copilot_text = read_text(".github/copilot-instructions.md")
    internal_contract_text = read_text("INTERNAL_CONTRACT.md")

    assert "For self-authored PRs under required-review policy" in copilot_text
    assert "qualifying non-author approval" in copilot_text
    assert "prefer `gh pr merge --squash`" in copilot_text
    assert (
        "Treat organization-wide `gh search prs` results as eventually consistent"
        in copilot_text
    )
    assert "`gh pr view --json state,mergedAt`" in copilot_text

    assert (
        "repository-workflow-github-pr-merge-and-terminal-state-reminders-stay-visible"
        in internal_contract_text
    )
    assert "qualifying non-author approval" in internal_contract_text
    assert "prefers `gh pr merge --squash`" in internal_contract_text
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
