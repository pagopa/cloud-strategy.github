import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_output_core import (  # noqa: E402
    OutputRecord,
    escape_tsv,
    render_tsv,
)


def test_escape_tsv_replaces_backslash_first() -> None:
    assert escape_tsv("a\\b") == "a\\\\b"


def test_escape_tsv_replaces_tab() -> None:
    assert escape_tsv("a\tb") == "a\\tb"


def test_escape_tsv_replaces_newline() -> None:
    assert escape_tsv("a\nb") == "a\\nb"


def test_escape_tsv_replaces_carriage_return() -> None:
    assert escape_tsv("a\rb") == "a\\rb"


def test_escape_tsv_order_backslash_before_others() -> None:
    assert escape_tsv("\\\t\n\r") == "\\\\\\t\\n\\r"


def test_render_tsv_header_is_fixed() -> None:
    records = [OutputRecord("summary", "mode", "ok", "audit")]
    output = render_tsv(records)
    first_line = output.split("\n", 1)[0]
    assert first_line == "record\tkey\tstatus\tvalue"


def test_render_tsv_sorts_lexically_by_record_key_status_value() -> None:
    records = [
        OutputRecord("z", "a", "ok", "v1"),
        OutputRecord("a", "z", "ok", "v2"),
        OutputRecord("a", "a", "ok", "v3"),
    ]
    output = render_tsv(records)
    lines = output.strip().split("\n")
    data_lines = lines[1:]
    assert data_lines == [
        "a\ta\tok\tv3",
        "a\tz\tok\tv2",
        "z\ta\tok\tv1",
    ]


def test_render_tsv_escapes_values() -> None:
    records = [OutputRecord("summary", "note", "ok", "has\ttab")]
    output = render_tsv(records)
    data_lines = output.strip().split("\n")[1:]
    assert len(data_lines) == 1
    assert "has\\ttab" in data_lines[0]
    assert "\t" not in data_lines[0].split("\t")[3]
