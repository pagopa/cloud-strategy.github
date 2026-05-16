from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_retained_learning_contract_preserves_on_disk_lessons_rows() -> None:
    expected_contracts: dict[str, list[str]] = {
        "AGENTS.md": [
            "Root `LESSONS_LEARNED.md` is the repository learning ledger",
            "Keep `LESSONS_LEARNED.md` non-canonical",
            "codify stable lessons into the smallest canonical owner when ready",
            "Keep detailed retained-learning behavior in `.github/copilot-instructions.md`",
        ],
        ".github/copilot-instructions.md": [
            "Before editing repository-root `LESSONS_LEARNED.md`, read its current on-disk contents",
            "including uncommitted rows already present on disk",
            "append one concise, reusable row to the pending table in `LESSONS_LEARNED.md`",
            "do not regenerate, reorder, or rewrite unrelated rows",
            (
                "Preserve unrelated existing lessons in `LESSONS_LEARNED.md`, including local "
                "uncommitted ones already on disk"
            ),
            "update or remove only that lesson's row before completion",
        ],
        "LESSONS_LEARNED.md": [
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


def test_pending_lesson_rows_have_expected_shape_when_present() -> None:
    lines = read_text("LESSONS_LEARNED.md").splitlines()

    section_start = lines.index("## Pending Rules") + 1
    header_index = next(
        index
        for index in range(section_start, len(lines))
        if lines[index].startswith("|")
    )
    data_start = header_index + 2

    data_rows: list[list[str]] = []
    for line in lines[data_start:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if any(cells):
            data_rows.append(cells)

    for row in data_rows:
        assert len(row) == 4
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[0])
        assert all(cell for cell in row[1:])
