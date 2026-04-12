from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_retained_learning_contract_preserves_on_disk_lessons_rows() -> None:
    expected_contracts: dict[str, list[str]] = {
        "AGENTS.md": [
            "Keep `LESSONS.md` append-preserving by default",
            "preserve unrelated rows already on disk, including local uncommitted lessons",
            (
                "change a specific row only when that same lesson is being codified, "
                "disproven, narrowed, or deduplicated"
            ),
        ],
        ".github/copilot-instructions.md": [
            "Before editing repository-root `LESSONS.md`, read its current on-disk contents",
            "including uncommitted rows already present on disk",
            "append one concise, reusable row to the pending table in `LESSONS.md`",
            "do not regenerate, reorder, or rewrite unrelated rows",
            (
                "Preserve unrelated existing lessons in `LESSONS.md`, including local "
                "uncommitted ones already on disk"
            ),
            "update or remove only that lesson's row before completion",
        ],
        "LESSONS.md": [
            "Before editing this file, read its current on-disk contents",
            "including local uncommitted rows already present on disk",
            (
                "Add a new lesson by appending one new row to the pending table; do not "
                "regenerate, reorder, or rewrite unrelated rows."
            ),
            "Preserve unrelated existing lessons, including local uncommitted ones already on disk.",
            (
                "Only update or remove a specific lesson row when that same lesson is being "
                "codified, disproven, narrowed, or deduplicated."
            ),
        ],
    }

    for relative_path, expected_snippets in expected_contracts.items():
        text = read_text(relative_path)
        for snippet in expected_snippets:
            assert snippet in text, (
                f"{relative_path} is missing retained-learning guardrail text: {snippet}"
            )
