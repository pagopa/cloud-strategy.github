from __future__ import annotations

import re
from pathlib import Path

RETAINED_PLAN_ROOT = Path("tmp/superpowers")

INVALID_PATCH_MARKERS = (
    "*** Begin Patch",
    "*** Update File:",
    "*** Add File:",
    "*** Delete File:",
    "*** End Patch",
)

COMPLETION_REPORT_FIELDS = (
    "Completion Report",
    "Active phase and owner:",
    "State:",
    "Files changed:",
    "Completed items:",
    "Intentional non-actions:",
    "Validators:",
    "Evidence envelope:",
    "Evidence gaps:",
    "Residual risks:",
    "Follow-up suggestions:",
)


def retained_plan_folders() -> list[Path]:
    if not RETAINED_PLAN_ROOT.exists():
        return []

    return sorted(path for path in RETAINED_PLAN_ROOT.iterdir() if path.is_dir())


def numbered_plan_files(plan_folder: Path) -> list[Path]:
    return sorted(
        path
        for path in plan_folder.glob("*.md")
        if re.fullmatch(r"\d{2}-.+\.md", path.name)
    )


def done_files(plan_folder: Path) -> list[Path]:
    return sorted(plan_folder.glob("done-*.md"))


def completed_retained_plan_violations(root: Path) -> list[str]:
    violations: list[str] = []

    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        folder_done_files = done_files(folder)
        if not folder_done_files:
            continue

        active_files = numbered_plan_files(folder)
        envelope_path = folder / "evidence-envelope.md"
        report_path = folder / "completion-report.md"

        if active_files:
            violations.append(f"{folder} still has active numbered plan files")
        if not envelope_path.is_file():
            violations.append(f"{folder} is missing evidence-envelope.md")
            continue
        if not report_path.is_file():
            violations.append(f"{folder} is missing completion-report.md")
            continue

        envelope_text = envelope_path.read_text(encoding="utf-8")
        report_text = report_path.read_text(encoding="utf-8")

        if "| Status |" not in envelope_text:
            violations.append(f"{envelope_path} is missing Status column")
        if "| Evidence path or command |" not in envelope_text:
            violations.append(
                f"{envelope_path} is missing Evidence path or command column"
            )

        for done_file in folder_done_files:
            if f"`{done_file.name}`" not in envelope_text:
                violations.append(
                    f"{envelope_path} does not reference {done_file.name}"
                )

        for field in COMPLETION_REPORT_FIELDS:
            if field not in report_text:
                violations.append(f"{report_path} is missing {field}")

    return violations


def patch_marker_violations(root: Path) -> list[str]:
    violations: list[str] = []

    for markdown_path in sorted(root.glob("**/*.md")):
        text = markdown_path.read_text(encoding="utf-8")
        for marker in INVALID_PATCH_MARKERS:
            if marker in text:
                violations.append(f"{markdown_path.as_posix()} contains {marker}")

    return violations


def write_completed_plan_folder(root: Path) -> Path:
    plan_folder = root / "sample-plan"
    plan_folder.mkdir()
    (plan_folder / "done-01-sample.md").write_text("# Done Sample\n", encoding="utf-8")
    (plan_folder / "evidence-envelope.md").write_text(
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01-sample.md` | DONE | `pytest` |\n",
        encoding="utf-8",
    )
    (plan_folder / "completion-report.md").write_text(
        "\n".join(COMPLETION_REPORT_FIELDS) + "\n",
        encoding="utf-8",
    )
    return plan_folder


def test_completed_retained_plan_validation_accepts_well_formed_folder(
    tmp_path: Path,
) -> None:
    write_completed_plan_folder(tmp_path)

    assert completed_retained_plan_violations(tmp_path) == []


def test_completed_retained_plan_validation_rejects_active_numbered_files(
    tmp_path: Path,
) -> None:
    plan_folder = write_completed_plan_folder(tmp_path)
    (plan_folder / "01-still-active.md").write_text("# Active\n", encoding="utf-8")

    assert completed_retained_plan_violations(tmp_path) == [
        f"{plan_folder} still has active numbered plan files"
    ]


def test_repository_completed_retained_plan_folders_preserve_completion_evidence() -> (
    None
):
    if not RETAINED_PLAN_ROOT.exists():
        return

    assert completed_retained_plan_violations(RETAINED_PLAN_ROOT) == []


def test_retained_plan_markdown_does_not_contain_patch_markers() -> None:
    if not RETAINED_PLAN_ROOT.exists():
        return

    assert patch_marker_violations(RETAINED_PLAN_ROOT) == []
