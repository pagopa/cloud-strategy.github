from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(".github/scripts/analyze_copilot_debug_logs.py").resolve()


def run_script(*paths: Path, format: str = "json") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *[str(path) for path in paths], "--format", format],
        capture_output=True,
        text=True,
        check=True,
    )


def test_analyzer_summarizes_otlp_and_dedupes_snapshot_exports(tmp_path: Path) -> None:
    otlp_path = tmp_path / "otlp.json"
    otlp_path.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "id": "sess-1",
                        "title": "Skill comparison",
                        "requests": [
                            {
                                "input_tokens": 120,
                                "output_tokens": 30,
                                "context_tokens": 120,
                                "tool_calls": [
                                    {"tool": "tool_search", "result_bytes": 400},
                                    {"tool": "graphify_query", "result_bytes": 50},
                                    {"tool": "read_file", "result_bytes": 800, "error": True},
                                ],
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    snapshot_a = tmp_path / "snapshot-a.json"
    snapshot_b = tmp_path / "snapshot-b.json"
    snapshot_payload = {
        "exported_at": "2026-06-10T08:33:51Z",
        "session_id": "snapshot-session",
        "title": "Snapshot export",
        "requests": [
            {
                "model": "gpt-5",
                "input_tokens": 200,
                "cached_input_tokens": 150,
                "output_tokens": 25,
                "aiu": 12.5,
                "tool_calls": [{"tool": "tool_search", "result_bytes": 25}],
            }
        ],
    }
    snapshot_a.write_text(json.dumps(snapshot_payload), encoding="utf-8")
    snapshot_b.write_text(
        json.dumps({**snapshot_payload, "exported_at": "2026-06-10T08:40:00Z"}),
        encoding="utf-8",
    )

    result = run_script(otlp_path, snapshot_a, snapshot_b)
    payload = json.loads(result.stdout)

    assert payload["snapshot_export_count"] == 2
    assert payload["deduped_snapshot_count"] == 1
    assert payload["aggregate"]["request_count"] == 2
    assert payload["aggregate"]["tool_result_bytes"] == 1275
    assert payload["aggregate"]["error_count"] == 1
    assert payload["aggregate"]["graphify_invocation_count"] == 1
    assert payload["aggregate"]["graphify_discovery_count"] == 2
    assert payload["aggregate"]["cache_read_tokens"] == 150
    assert payload["aggregate"]["non_cached_input_tokens"] == 170
    assert payload["aggregate"]["aiu_total"] == 12.5
    assert all("prompt" not in json.dumps(session).lower() for session in payload["sessions"])


def test_analyzer_can_render_markdown(tmp_path: Path) -> None:
    otlp_path = tmp_path / "otlp.json"
    otlp_path.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "id": "sess-2",
                        "title": "Sync reporting",
                        "requests": [{"input_tokens": 10, "output_tokens": 5, "tool_calls": []}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_script(otlp_path, format="markdown")

    assert "# Debug Log Summary" in result.stdout
    assert "Sync reporting" in result.stdout
