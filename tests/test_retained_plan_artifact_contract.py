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
    "Continuation:",
    "User action required:",
    "Files changed:",
    "Completed items:",
    "Intentional non-actions:",
    "Validators:",
    "Evidence envelope:",
    "Source-item ledger:",
    "Evidence gaps:",
    "Residual risks:",
    "Next-step package:",
    "Follow-up suggestions:",
)

OPEN_COMPLETION_STATUSES = (
    "PENDING",
    "PARTIAL",
    "NOT_DONE",
    "UNVERIFIABLE",
    "BLOCKED",
)

GATEWAY_STATUS_VALUES = ("DONE", "BLOCKED", "PARTIAL", "NEEDS_REVIEW")
GATEWAY_STATUS_HEADINGS = (
    "## Status",
    "## Reason",
    "## Completed",
    "## Remaining",
    "## Validation",
    "## Next",
    "## Resume Notes",
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


def resolve_gateway_status_file(
    plan_folder: Path,
) -> tuple[Path | None, str | None, list[str]]:
    violations: list[str] = []
    statuses = "|".join(GATEWAY_STATUS_VALUES)
    status_re = re.compile(rf"^{re.escape(plan_folder.name)}\.({statuses})\.md$")
    status_files: list[Path] = []

    for path in sorted(plan_folder.glob("*.md")):
        if status_re.match(path.name):
            status_files.append(path)
        elif re.match(rf"^{re.escape(plan_folder.name)}\.[A-Z0-9_-]+\.md$", path.name):
            violations.append(
                f"{path} must use one of these statuses: {', '.join(GATEWAY_STATUS_VALUES)}"
            )

    legacy_markers = sorted(plan_folder.glob("*-plan-state.md"))
    for marker in legacy_markers:
        violations.append(
            f"{marker} is a legacy gateway marker; use <plan-basename>.<STATUS>.md"
        )

    if len(status_files) > 1:
        violations.append(f"{plan_folder} has multiple gateway status files")
        return None, None, violations

    if not status_files:
        return None, None, violations

    marker = status_files[0]
    match = status_re.match(marker.name)
    if match is None:
        violations.append(f"{marker} must match <plan-basename>.<STATUS>.md")
        return None, None, violations

    return marker, match.group(1), violations


def completed_retained_plan_violations(root: Path) -> list[str]:
    violations: list[str] = []

    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        folder_done_files = done_files(folder)
        status_path, marker_state, marker_violations = resolve_gateway_status_file(folder)
        violations.extend(marker_violations)

        if not folder_done_files and status_path is None:
            continue

        if status_path is not None and not folder_done_files:
            status_text = status_path.read_text(encoding="utf-8")
            for heading in GATEWAY_STATUS_HEADINGS:
                if heading not in status_text:
                    violations.append(f"{status_path} is missing {heading}")

            status_match = re.search(
                r"^## Status\s*\n+\s*([A-Z0-9_-]+)\s*$",
                status_text,
                re.MULTILINE,
            )
            if status_match is None:
                violations.append(f"{status_path} must declare status under ## Status")
            elif status_match.group(1) != marker_state:
                violations.append(
                    f"{status_path} filename status does not match declared status"
                )
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
        for status in OPEN_COMPLETION_STATUSES:
            if f"| {status} |" in envelope_text:
                violations.append(
                    f"{envelope_path} contains open completion status {status}"
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


def write_lightweight_completed_plan_folder(root: Path) -> Path:
    plan_folder = root / "sample-plan"
    plan_folder.mkdir()
    (plan_folder / "01-change-summary.md").write_text(
        "# Summary\n",
        encoding="utf-8",
    )
    (plan_folder / "02-execution.md").write_text(
        "## Plan profile\ncompact\n\n"
        "## Source item coverage\n"
        "| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| PLAN-01 | Lightweight completion marker | DONE status file present | file | sample-plan.DONE.md | DONE | `none` |\n",
        encoding="utf-8",
    )
    (plan_folder / "sample-plan.DONE.md").write_text(
        "# sample-plan Status\n\n"
        "## Status\n\n"
        "DONE\n\n"
        "## Reason\n\n"
        "Complete.\n\n"
        "## Completed\n\n"
        "- All items.\n\n"
        "## Remaining\n\n"
        "- None.\n\n"
        "## Validation\n\n"
        "- `pytest` passed.\n\n"
        "## Next\n\n"
        "- No action required.\n\n"
        "## Resume Notes\n\n"
        "- Re-run validation after new edits.\n",
        encoding="utf-8",
    )
    return plan_folder


def write_blocked_plan_folder(root: Path) -> Path:
    plan_folder = root / "sample-plan"
    plan_folder.mkdir()
    (plan_folder / "sample-plan.BLOCKED.md").write_text(
        "# sample-plan Status\n\n"
        "## Status\n\n"
        "BLOCKED\n\n"
        "## Reason\n\n"
        "Blocked.\n\n"
        "## Completed\n\n"
        "- Partial work.\n\n"
        "## Remaining\n\n"
        "- Await approval.\n\n"
        "## Validation\n\n"
        "- Not run.\n\n"
        "## Next\n\n"
        "- Approve next owner.\n\n"
        "## Resume Notes\n\n"
        "- Resume after approval.\n",
        encoding="utf-8",
    )
    return plan_folder


def test_completed_retained_plan_validation_accepts_well_formed_folder(
    tmp_path: Path,
) -> None:
    write_completed_plan_folder(tmp_path)

    assert completed_retained_plan_violations(tmp_path) == []


def test_completed_retained_plan_validation_accepts_lightweight_folder(
    tmp_path: Path,
) -> None:
    write_lightweight_completed_plan_folder(tmp_path)

    assert completed_retained_plan_violations(tmp_path) == []


def test_completed_retained_plan_validation_accepts_active_blocked_marker(
    tmp_path: Path,
) -> None:
    write_blocked_plan_folder(tmp_path)

    assert completed_retained_plan_violations(tmp_path) == []


def test_completed_retained_plan_validation_rejects_active_numbered_files(
    tmp_path: Path,
) -> None:
    plan_folder = write_completed_plan_folder(tmp_path)
    (plan_folder / "01-still-active.md").write_text("# Active\n", encoding="utf-8")

    assert completed_retained_plan_violations(tmp_path) == [
        f"{plan_folder} still has active numbered plan files"
    ]


def test_completed_retained_plan_validation_rejects_open_statuses(
    tmp_path: Path,
) -> None:
    plan_folder = write_completed_plan_folder(tmp_path)
    (plan_folder / "evidence-envelope.md").write_text(
        "# Evidence Envelope\n\n"
        "| Source item | Status | Evidence path or command |\n"
        "| --- | --- | --- |\n"
        "| `done-01-sample.md` | PENDING | `pytest` |\n",
        encoding="utf-8",
    )

    assert completed_retained_plan_violations(tmp_path) == [
        f"{plan_folder / 'evidence-envelope.md'} contains open completion status PENDING"
    ]


def test_completed_retained_plan_validation_rejects_lightweight_non_shipped(
    tmp_path: Path,
) -> None:
    plan_folder = write_lightweight_completed_plan_folder(tmp_path)
    (plan_folder / "sample-plan.DONE.md").write_text(
        "# sample-plan Status\n\n"
        "## Status\n\n"
        "PARTIAL\n\n"
        "## Reason\n\n"
        "Incomplete.\n\n"
        "## Completed\n\n"
        "- Some items.\n\n"
        "## Remaining\n\n"
        "- More items.\n\n"
        "## Validation\n\n"
        "- Pending.\n\n"
        "## Next\n\n"
        "- Continue.\n\n"
        "## Resume Notes\n\n"
        "- Resume later.\n",
        encoding="utf-8",
    )

    assert completed_retained_plan_violations(tmp_path) == [
        f"{plan_folder / 'sample-plan.DONE.md'} filename status does not match declared status",
    ]


def test_completed_retained_plan_validation_rejects_waiting_marker_missing_fields(
    tmp_path: Path,
) -> None:
    plan_folder = tmp_path / "sample-plan"
    plan_folder.mkdir()
    (plan_folder / "sample-plan.BLOCKED.md").write_text(
        "# sample-plan Status\n\n"
        "## Status\n\n"
        "BLOCKED\n\n"
        "## Reason\n\n"
        "Blocked.\n\n"
        "## Completed\n\n"
        "- Partial work.\n\n"
        "## Remaining\n\n"
        "- Await approval.\n\n"
        "## Validation\n\n"
        "- Not run.\n\n"
        "## Next\n\n"
        "- Approve next owner.\n\n"
        encoding="utf-8",
    )

    assert completed_retained_plan_violations(tmp_path) == [
        f"{plan_folder / 'sample-plan.BLOCKED.md'} is missing ## Resume Notes",
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
