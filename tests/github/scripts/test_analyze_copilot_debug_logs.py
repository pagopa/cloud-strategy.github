from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.analyze_copilot_debug_log import debug_logs

SCRIPT = Path(".github/scripts/analyze_copilot_debug_logs.py").resolve()


def run_script(*paths: Path, format: str = "json") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            *[str(path) for path in paths],
            "--format",
            format,
        ],
        capture_output=True,
        text=True,
        check=True,
    )


def test_analyzer_summarizes_otlp_and_dedupes_prompt_exports(tmp_path: Path) -> None:
    otlp_path = tmp_path / "otlp.json"
    otlp_path.write_text(
        json.dumps(
            {
                "resourceSpans": [
                    {
                        "resource": {
                            "attributes": [
                                {
                                    "key": "service.name",
                                    "value": {"stringValue": "copilot-chat"},
                                },
                                {
                                    "key": "session.id",
                                    "value": {"stringValue": "sess-1"},
                                },
                            ]
                        },
                        "scopeSpans": [
                            {
                                "spans": [
                                    {
                                        "name": "chat:gpt-5.4-mini",
                                        "status": {"code": 0},
                                        "attributes": [
                                            {
                                                "key": "gen_ai.usage.input_tokens",
                                                "value": {"intValue": 40},
                                            },
                                            {
                                                "key": "gen_ai.usage.output_tokens",
                                                "value": {"intValue": 8},
                                            },
                                        ],
                                    },
                                    {
                                        "name": "tool_search",
                                        "status": {"code": 0},
                                        "attributes": [
                                            {
                                                "key": "gen_ai.usage.input_tokens",
                                                "value": {"intValue": 10},
                                            },
                                            {
                                                "key": "gen_ai.usage.output_tokens",
                                                "value": {"intValue": 1},
                                            },
                                            {
                                                "key": "gen_ai.tool.name",
                                                "value": {"stringValue": "tool_search"},
                                            },
                                            {
                                                "key": "gen_ai.tool.call.result",
                                                "value": {"stringValue": "AAAA"},
                                            },
                                        ],
                                    },
                                    {
                                        "name": "graphify_query",
                                        "status": {"code": 2},
                                        "attributes": [
                                            {
                                                "key": "gen_ai.usage.input_tokens",
                                                "value": {"intValue": 10},
                                            },
                                            {
                                                "key": "gen_ai.usage.output_tokens",
                                                "value": {"intValue": 3},
                                            },
                                            {
                                                "key": "gen_ai.tool.name",
                                                "value": {
                                                    "stringValue": "graphify_query"
                                                },
                                            },
                                            {
                                                "key": "gen_ai.tool.call.result",
                                                "value": {"stringValue": "BBBBB"},
                                            },
                                        ],
                                    },
                                ]
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    prompt_a = tmp_path / "prompt-a.json"
    prompt_b = tmp_path / "prompt-b.json"
    prompt_payload = {
        "exportedAt": "2026-06-10T08:33:51Z",
        "prompts": [
            {
                "promptId": "prompt-1",
                "logs": [
                    {
                        "name": "tool_search",
                        "kind": "info",
                        "metadata": {
                            "maxPromptTokens": 200,
                            "usage": {
                                "prompt_tokens": 200,
                                "prompt_tokens_details": {"cached_tokens": 150},
                                "completion_tokens": 25,
                                "copilot_usage": {"total_nano_aiu": 12.5},
                            },
                        },
                        "response": {"type": "message", "message": "CCCCCC"},
                    }
                ],
            }
        ],
    }
    prompt_a.write_text(json.dumps(prompt_payload), encoding="utf-8")
    prompt_b.write_text(
        json.dumps({**prompt_payload, "exportedAt": "2026-06-10T08:40:00Z"}),
        encoding="utf-8",
    )

    result = run_script(otlp_path, prompt_a, prompt_b)
    payload = json.loads(result.stdout)

    assert payload["snapshot_export_count"] == 2
    assert payload["deduped_snapshot_count"] == 1
    assert payload["unsupported_input_count"] == 0
    assert payload["aggregate"]["request_count"] == 4
    assert payload["aggregate"]["tool_result_bytes"] == 15
    assert payload["aggregate"]["error_count"] == 1
    assert payload["aggregate"]["graphify_invocation_count"] == 1
    assert payload["aggregate"]["graphify_discovery_count"] == 2
    assert payload["aggregate"]["cache_read_tokens"] == 150
    assert payload["aggregate"]["non_cached_input_tokens"] == 50
    assert payload["aggregate"]["aiu_total"] == 12.5
    assert all(
        "cccccc" not in json.dumps(session).lower() for session in payload["sessions"]
    )


def test_analyzer_reports_unsupported_schema(tmp_path: Path) -> None:
    unknown_path = tmp_path / "unknown.json"
    unknown_path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

    result = run_script(unknown_path)
    payload = json.loads(result.stdout)

    assert payload["unsupported_input_count"] == 1
    assert payload["unsupported_inputs"] == ["unknown.json"]
    assert payload["aggregate"]["request_count"] == 0


def test_analyzer_can_render_markdown(tmp_path: Path) -> None:
    otlp_path = tmp_path / "otlp.json"
    otlp_path.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "id": "sess-2",
                        "title": "Sync reporting",
                        "requests": [
                            {"input_tokens": 10, "output_tokens": 5, "tool_calls": []}
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_script(otlp_path, format="markdown")

    assert "# Debug Log Summary" in result.stdout
    assert "Sync reporting" in result.stdout


def test_debug_log_tool_package_is_importable() -> None:
    assert debug_logs.parse_args(["input.json", "--format", "markdown"]).format == "markdown"
