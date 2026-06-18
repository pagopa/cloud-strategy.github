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

PLAN_STATE_MARKER_RE = re.compile(r"^([A-Z0-9_-]+)-plan-state\.md$")


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


def resolve_plan_state_marker(
    plan_folder: Path,
) -> tuple[Path | None, str | None, list[str]]:
    violations: list[str] = []
    named_markers = sorted(
        path for path in plan_folder.glob("*-plan-state.md") if path.is_file()
    )

    if len(named_markers) > 1:
        violations.append(f"{plan_folder} has multiple <STATE>-plan-state.md markers")
        return None, None, violations

    if named_markers:
        marker = named_markers[0]
        match = PLAN_STATE_MARKER_RE.match(marker.name)
        if match is None:
            violations.append(
                f"{marker} must match <STATE>-plan-state.md with uppercase state"
            )
            return None, None, violations
        marker_state = match.group(1).upper()
        return marker, marker_state, violations

    return None, None, violations


def completed_retained_plan_violations(root: Path) -> list[str]:
    violations: list[str] = []

    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        folder_done_files = done_files(folder)
        plan_state_path, marker_state, marker_violations = resolve_plan_state_marker(
            folder
        )
        violations.extend(marker_violations)

        if not folder_done_files and plan_state_path is None:
            continue

        if plan_state_path is not None and not folder_done_files:
            plan_state_text = plan_state_path.read_text(encoding="utf-8")
            state_match = re.search(r"^State:\s*(.+)$", plan_state_text, re.MULTILINE)
            continuation_match = re.search(
                r"^Continuation:\s*(.+)$", plan_state_text, re.MULTILINE
            )

            if state_match is None:
                violations.append(f"{plan_state_path} is missing State")
            elif state_match.group(1).strip() != "DONE":
                violations.append(f"{plan_state_path} must declare State: DONE")

            if marker_state and marker_state != "DONE":
                violations.append(
                    f"{plan_state_path} must encode DONE state in filename"
                )

            if (
                marker_state
                and state_match
                and state_match.group(1).strip().upper() != marker_state
            ):
                violations.append(
                    f"{plan_state_path} filename state does not match declared State"
                )

            if continuation_match is None:
                violations.append(f"{plan_state_path} is missing Continuation")
            elif continuation_match.group(1).strip() != "none":
                violations.append(f"{plan_state_path} must declare Continuation: none")
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
        "| PLAN-01 | Lightweight completion marker | DONE marker present | file | DONE-plan-state.md | DONE | `none` |\n",
        encoding="utf-8",
    )
    (plan_folder / "DONE-plan-state.md").write_text(
        "Plan State\nState: DONE\nContinuation: none\n",
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
    (plan_folder / "DONE-plan-state.md").write_text(
        "Plan State\nState: PARTIAL\nContinuation: continuing\n",
        encoding="utf-8",
    )

    assert completed_retained_plan_violations(tmp_path) == [
        f"{plan_folder / 'DONE-plan-state.md'} must declare State: DONE",
        f"{plan_folder / 'DONE-plan-state.md'} filename state does not match declared State",
        f"{plan_folder / 'DONE-plan-state.md'} must declare Continuation: none",
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
