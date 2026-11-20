"""Consumer regression checks for versioned migration reports."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "evaluation"))
from knowledge_graders.core import RunInput  # noqa: E402
from knowledge_graders.report import parse_report, report_truthful  # noqa: E402


def migration_run(fields: str, *, incomplete: bool = False) -> RunInput:
    return RunInput(
        profile="author",
        allowlist=("CONTEXT.md", "GLOSSARY.md"),
        before={"CONTEXT.md": "terms"},
        after={
            "GLOSSARY.md": "terms",
            **({"CONTEXT.md": "terms"} if incomplete else {}),
        },
        steps=(),
        trace=(),
        trace_complete=True,
        report="Migration result.\nObserved paths follow.\nknowledge-report/v2\nmode: targeted\n"
        + fields,
        second_after=None,
    )


def test_v2_migration_reports_separate_writes_and_removals() -> None:
    run = migration_run(
        "written: GLOSSARY.md\nremoved: CONTEXT.md\n"
        "transfers: CONTEXT.md -> GLOSSARY.md\nmigration_state: complete\n"
    )
    assert parse_report(run.report)["removed"] == "CONTEXT.md"
    assert report_truthful(run, {}).status == "pass"


@pytest.mark.parametrize(
    "fields",
    [
        "written: GLOSSARY.md\n",
        "written: CONTEXT.md; GLOSSARY.md\n",
        "written: GLOSSARY.md\nremoved: GLOSSARY.md\n",
        "written: GLOSSARY.md\nremoved: CONTEXT.md\ntransfers: ghost.md -> GLOSSARY.md\n",
        "written: GLOSSARY.md\nremoved: CONTEXT.md\ntransfers: CONTEXT.md -> ghost.md\n",
    ],
)
def test_v2_rejects_false_removal_or_transfer_claims(fields: str) -> None:
    assert report_truthful(migration_run(fields), {}).status == "fail"


def test_incomplete_migration_reports_only_operations_observed() -> None:
    run = migration_run(
        "written: GLOSSARY.md\nmigration_state: incomplete\n"
        "gaps: Old owner and references still need authorized reconciliation.\n",
        incomplete=True,
    )
    assert report_truthful(run, {}).status == "pass"
    false_removal = migration_run(
        "written: GLOSSARY.md\nremoved: CONTEXT.md\nmigration_state: complete\n",
        incomplete=True,
    )
    assert report_truthful(false_removal, {}).status == "fail"


@pytest.mark.parametrize(
    "extra",
    [
        "removed: CONTEXT.md\n",
        "migration_state: finished\n",
        "transfers: CONTEXT.md GLOSSARY.md\n",
        "migration_state: incomplete\n",
        "surprise: yes\n",
    ],
)
def test_versioned_parser_rejects_invalid_extensions(extra: str) -> None:
    marker = "v1" if extra.startswith("removed:") else "v2"
    with pytest.raises(ValueError):
        parse_report(
            f"Summary.\nObserved result.\nknowledge-report/{marker}\nmode: targeted\n{extra}"
        )


def test_legacy_report_remains_readable_and_truthful() -> None:
    run = migration_run("written: CONTEXT.md; GLOSSARY.md\n")
    legacy = RunInput(**{**run.__dict__, "report": run.report.replace("/v2", "/v1")})
    assert report_truthful(legacy, {}).status == "pass"


def test_align_report_is_readable_in_both_versions() -> None:
    for version in ("v1", "v2"):
        assert parse_report(
            f"Proposal only.\nNo writes.\nknowledge-report/{version}\nmode: align\n"
        ) == {"mode": "align"}
