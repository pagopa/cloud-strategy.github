import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_ROOT = REPO_ROOT / ".github/skills/local-copilot-log-analyzer/scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from analyze_copilot_debug_log.debug_logs import (  # noqa: E402
    build_report,
    load_input,
    render_markdown,
)

DIRECT_FIXTURE = Path(__file__).parent / "fixtures/direct-session.jsonl"


def test_build_report_accepts_direct_jsonl() -> None:
    report = build_report([DIRECT_FIXTURE])

    aggregate = report["aggregate"]
    assert aggregate["request_count"] == 2
    assert aggregate["input_tokens"] == 220
    assert aggregate["output_tokens"] == 30
    assert aggregate["cache_read_tokens"] == 180
    assert aggregate["non_cached_input_tokens"] == 40
    assert aggregate["aiu_total"] == 0.75
    assert report["sessions"][0]["first_context_tokens"] == 100
    assert report["sessions"][0]["last_context_tokens"] == 120
    assert report["sessions"][0]["max_context_tokens"] == 120
    assert report["sessions"][0]["tool_calls"] == 1
    assert report["sessions"][0]["tool_result_bytes"] == 2
    assert "must-not-leak" not in json.dumps(report)


def test_load_input_accepts_one_json_document(tmp_path: Path) -> None:
    path = tmp_path / "sessions.json"
    path.write_text('{"sessions": []}', encoding="utf-8")

    assert load_input(path) == {"sessions": []}


def test_load_input_accepts_empty_lines_around_one_json_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('\n{"type":"tool_call"}\n\n', encoding="utf-8")

    assert load_input(path) == {"type": "tool_call"}


def test_load_input_reports_malformed_jsonl_line_without_content(
    tmp_path: Path,
) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('{"type":"tool_call"}\nnot-json\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"events\.jsonl.*line 2") as error:
        load_input(path)

    assert "not-json" not in str(error.value)


def test_build_report_preserves_legacy_session_input(tmp_path: Path) -> None:
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps({"sessions": [{"id": "legacy", "requests": []}]}),
        encoding="utf-8",
    )

    report = build_report([path])

    assert report["sessions"][0]["session_id"] == "legacy"
    assert report["unsupported_input_count"] == 0


def test_markdown_reports_cache_uncached_and_aiu() -> None:
    report = build_report([DIRECT_FIXTURE])

    markdown = render_markdown(report)

    assert "| AIU |" in markdown
    assert "| 180 | 40 |" in markdown
    assert "| 0.75 |" in markdown
    assert "must-not-leak" not in markdown
    assert "| ok |" not in markdown
