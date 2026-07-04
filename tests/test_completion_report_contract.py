from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_repo_projection_keeps_completion_report_compact() -> None:
    copilot_text = read_text(".github/copilot-instructions.md")

    assert "This file is only for GitHub.com Copilot code review." in copilot_text
    assert "It is not a general task-execution guide" in copilot_text
    assert "Review changed files for defects that matter before merge." in copilot_text
    assert "Report findings first, ordered by severity." in copilot_text
    assert (
        "Do not treat this file as instructions for coding agents, local CLIs, or"
        in copilot_text
    )
    assert "Report completed work with outcome, changed files" not in copilot_text
    assert "`✅ Outcome`" not in copilot_text
    assert "`1 = resources used`" not in copilot_text


def test_completion_report_docs_match_optional_detail_contract() -> None:
    readme_text = read_text(".github/README.md")
    internal_contract_text = read_text("INTERNAL_CONTRACT.md")
    sync_contract_text = read_text(
        ".github/skills/local-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md"
    )

    assert "offer it as an optional follow-up" in readme_text
    assert "number-only replies" in readme_text

    assert (
        "supporting sections such as `🤖 Agents`, `📘 Instructions`, `🧩 Skills`, and `📦 Other Resources` are optional detail by default"
        in internal_contract_text
    )
    assert "accepts number-only replies" in internal_contract_text

    assert "offer it as optional follow-up detail" in sync_contract_text
    assert "accepts number-only replies" in sync_contract_text


def test_completion_report_requires_mandatory_applicable_evidence_for_shipped() -> None:
    completion_reference = read_text(
        ".github/skills/internal-gateway-execute-plans/references/status-file.md"
    )

    assert (
        "Use this reference when `internal-gateway-execute-plans` finishes, pauses, or"
        in completion_reference
    )
    assert "## Resume Notes" in completion_reference
