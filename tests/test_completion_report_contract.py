from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_repo_projection_makes_detail_sections_optional() -> None:
    copilot_text = read_text(".github/copilot-instructions.md")

    assert "- End completed operations with `✅ Outcome`." in copilot_text
    assert "Default to a concise `✅ Outcome`" in copilot_text
    assert "offer it as an optional follow-up" in copilot_text
    assert "allow a number-only reply" in copilot_text
    assert (
        "`1 = resources used`, `2 = files changed`, `3 = validations`, `4 = full detail`"
        in copilot_text
    )


def test_completion_report_docs_match_optional_detail_contract() -> None:
    readme_text = read_text(".github/README.md")
    internal_contract_text = read_text("INTERNAL_CONTRACT.md")
    sync_contract_text = read_text(
        ".github/skills/internal-agent-sync-global-copilot-configs-into-repo/references/sync-contract.md"
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
