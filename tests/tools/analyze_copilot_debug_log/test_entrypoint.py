from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from tools.analyze_copilot_debug_log import cli, debug_logs, main, prompt_exports

SCRIPT = Path("tools/analyze_copilot_debug_log/run.sh").resolve()
REPO_ROOT = Path(__file__).resolve().parents[3]


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHON_BIN"] = sys.executable
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )


def test_prompt_exports_subcommand_summarizes_and_dedupes(tmp_path: Path) -> None:
    system_text = """
<skill>
<name>internal-gateway-execute-plans</name>
<path>/Users/example/.agents/skills/internal-gateway-execute-plans/SKILL.md</path>
---
name: internal-gateway-execute-plans
description: Execute approved retained plans with validation evidence.
---
</skill>
<skill>
<name>superpowers-executing-plans</name>
<path>/Users/example/.agents/skills/superpowers-executing-plans/SKILL.md</path>
---
name: superpowers-executing-plans
description: Execute written implementation plans step by step.
---
</skill>
PRIVATE SYSTEM BODY
"""
    prompt_export = {
        "exportedAt": "2026-06-10T08:33:51Z",
        "prompts": [
            {
                "promptId": "prompt-1",
                "title": "Prompt one",
                "logs": [
                    {
                        "name": "model_request",
                        "kind": "request",
                        "metadata": {
                            "copilotUsageAic": 1.25,
                            "usage": {
                                "prompt_tokens": 100,
                                "prompt_tokens_details": {"cached_tokens": 70},
                                "completion_tokens": 12,
                                "reasoning_tokens": 3,
                            },
                        },
                        "requestMessages": {
                            "messages": [
                                {
                                    "role": 0,
                                    "content": [{"type": 1, "text": system_text}],
                                },
                                {
                                    "role": 1,
                                    "content": [
                                        {
                                            "type": 1,
                                            "text": "PRIVATE USER BODY",
                                            "path": "docs/repeated.md",
                                        }
                                    ],
                                },
                            ]
                        },
                    },
                    {
                        "kind": "toolCall",
                        "tool": "tool_search",
                        "args": {"query": "graphify"},
                        "result": {"message": "BBBBB"},
                        "metadata": {
                            "usage": {
                                "prompt_tokens": 40,
                                "completion_tokens": 2,
                                "copilot_usage": {"total_nano_aiu": 12.5},
                            }
                        },
                        "requestMessages": {
                            "messages": [
                                {
                                    "role": 0,
                                    "content": [{"type": 1, "text": system_text}],
                                },
                                {
                                    "role": 1,
                                    "content": [
                                        {
                                            "type": 1,
                                            "text": "PRIVATE USER BODY",
                                            "path": "docs/repeated.md",
                                        }
                                    ],
                                },
                            ]
                        },
                    },
                    {
                        "kind": "toolCall",
                        "tool": {"name": "retry_tool_search"},
                        "arguments": {"query": "graphify"},
                        "output": {"message": "BBBBB"},
                        "metadata": {
                            "usage": {
                                "prompt_tokens": 40,
                                "completion_tokens": 2,
                                "copilot_usage": {"total_nano_aiu": 12.5},
                            }
                        },
                    },
                ],
            }
        ],
    }
    prompt_a = tmp_path / "prompt-a.json"
    prompt_b = tmp_path / "prompt-b.json"
    prompt_a.write_text(json.dumps(prompt_export), encoding="utf-8")
    prompt_b.write_text(
        json.dumps({**prompt_export, "exportedAt": "2026-06-10T09:00:00Z"}),
        encoding="utf-8",
    )

    result = run_tool("prompt-exports", str(prompt_a), str(prompt_b))
    payload = json.loads(result.stdout)

    assert payload["prompt_export_count"] == 2
    assert payload["deduped_prompt_export_count"] == 1
    assert payload["unsupported_input_count"] == 0
    assert payload["aggregate"]["prompt_count"] == 1
    assert payload["aggregate"]["request_count"] == 3
    assert payload["aggregate"]["prompt_tokens"] == 180
    assert payload["aggregate"]["cache_read_tokens"] == 70
    assert payload["aggregate"]["non_cached_input_tokens"] == 110
    assert payload["aggregate"]["completion_tokens"] == 16
    assert payload["aggregate"]["reasoning_tokens"] == 3
    assert payload["aggregate"]["aiu_total"] == 26.25
    assert payload["aggregate"]["max_prompt_tokens"] == 100
    assert payload["aggregate"]["cache_read_ratio"] == 0.3889
    assert payload["aggregate"]["tool_calls"] == 2
    assert payload["aggregate"]["tool_counts_by_name"] == {
        "retry_tool_search": 1,
        "tool_search": 1,
    }
    assert payload["aggregate"]["tool_payload_bytes"] > 0
    assert (
        payload["aggregate"]["top_tool_payloads"][0]["tool_name"] == "retry_tool_search"
    )
    assert (
        payload["aggregate"]["top_tool_payloads"][0]["payload_bytes"]
        >= payload["aggregate"]["top_tool_payloads"][1]["payload_bytes"]
    )
    assert payload["aggregate"]["retry_like_duplicate_count"] == 1
    assert payload["aggregate"]["retry_like_duplicate_records"][0]["occurrences"] == 2
    assert payload["prompts"][0]["context_growth_tokens"] == 0
    composition = payload["aggregate"]["composition"]
    assert composition["system_message_count"] == 2
    assert composition["repeated_system_message_hashes"][0]["occurrences"] == 2
    assert composition["skill_metadata_block_count"] == 4
    assert composition["gateway_superpowers_co_present_count"] == 2
    assert composition["duplicate_attachment_paths"] == [
        {"path": "docs/repeated.md", "occurrences": 2}
    ]
    assert composition["largest_skill_descriptions"][0]["skill_id"] in {
        "internal-gateway-execute-plans",
        "superpowers-executing-plans",
    }
    assert "PRIVATE SYSTEM BODY" not in result.stdout
    assert "PRIVATE USER BODY" not in result.stdout


def test_prompt_exports_reports_sequence_cost_diagnostics(tmp_path: Path) -> None:
    prompt_export = {
        "prompts": [
            {
                "promptId": "prompt-sequence",
                "logs": [
                    {
                        "id": "request-start",
                        "kind": "request",
                        "metadata": {
                            "model": "gpt-test",
                            "usage": {
                                "prompt_tokens": 100_000,
                                "prompt_tokens_details": {"cached_tokens": 95_000},
                                "completion_tokens": 100,
                            },
                        },
                    },
                    {
                        "id": "patch-big",
                        "kind": "toolCall",
                        "tool": "apply_patch",
                        "args": "A" * 12_000,
                        "response": "patched",
                    },
                    {
                        "id": "request-after-patch",
                        "kind": "request",
                        "metadata": {
                            "model": "gpt-test",
                            "usage": {
                                "prompt_tokens": 114_000,
                                "prompt_tokens_details": {"cached_tokens": 90_000},
                                "completion_tokens": 50,
                            },
                        },
                    },
                    {
                        "id": "tiny-tool",
                        "kind": "toolCall",
                        "tool": "manage_todo_list",
                        "args": {"todoList": []},
                        "response": "ok",
                    },
                    {
                        "id": "request-cache-drop",
                        "kind": "request",
                        "metadata": {
                            "model": "gpt-test",
                            "usage": {
                                "prompt_tokens": 114_500,
                                "prompt_tokens_details": {"cached_tokens": 70_000},
                                "completion_tokens": 25,
                            },
                        },
                    },
                ],
            }
        ]
    }
    prompt_path = tmp_path / "prompt-sequence.json"
    prompt_path.write_text(json.dumps(prompt_export), encoding="utf-8")

    result = run_tool("prompt-exports", str(prompt_path))
    payload = json.loads(result.stdout)

    prompt_summary = payload["prompts"][0]
    top_spike = prompt_summary["top_non_cached_spikes"][0]
    assert top_spike == {
        "prompt_id": "prompt-sequence",
        "request_id": "request-cache-drop",
        "model": "gpt-test",
        "prompt_tokens": 114_500,
        "cached_tokens": 70_000,
        "non_cached_input_tokens": 44_500,
        "previous_cached_tokens": 90_000,
        "cache_delta_tokens": -20_000,
        "prompt_delta_tokens": 500,
        "previous_tool_payload_bytes": 17,
        "previous_tool_names": ["manage_todo_list"],
    }
    assert prompt_summary["cache_drop_events"] == [top_spike]

    payload_candidate = prompt_summary["payload_to_noncache_candidates"][0]
    assert payload_candidate["request_id"] == "request-after-patch"
    assert payload_candidate["previous_tool_names"] == ["apply_patch"]
    assert payload_candidate["previous_tool_payload_bytes"] >= 12_000

    aggregate = payload["aggregate"]
    assert aggregate["top_non_cached_spikes"][0] == top_spike
    assert aggregate["cache_drop_events"][0] == top_spike
    assert aggregate["payload_to_noncache_candidates"][0] == payload_candidate

    markdown_result = run_tool(
        "prompt-exports", str(prompt_path), "--format", "markdown"
    )
    assert "## Sequence Diagnostics" in markdown_result.stdout
    assert "prompt-sequence/request-cache-drop" in markdown_result.stdout
    assert "previous tools manage_todo_list" in markdown_result.stdout


def test_debug_logs_subcommand_summarizes_otlp_and_dedupes_prompt_exports(
    tmp_path: Path,
) -> None:
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
        "copilotChat": {
            "sessionId": "lane-session-1",
            "sessionTitle": "Internal Gateway Execute Plans",
        },
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

    result = run_tool("debug-logs", str(otlp_path), str(prompt_a), str(prompt_b))
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
    lane_sessions = [
        session
        for session in payload["sessions"]
        if session.get("session_id") == "lane-session-1"
    ]
    assert lane_sessions
    assert lane_sessions[0]["title"] == "Internal Gateway Execute Plans"
    assert all(
        "cccccc" not in json.dumps(session).lower() for session in payload["sessions"]
    )


def test_debug_logs_subcommand_can_render_markdown(tmp_path: Path) -> None:
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

    result = run_tool("debug-logs", str(otlp_path), "--format", "markdown")

    assert "# Debug Log Summary" in result.stdout
    assert "Sync reporting" in result.stdout


def test_prompt_exports_subcommand_markdown_includes_aiu_total(tmp_path: Path) -> None:
    prompt_path = tmp_path / "prompt.json"
    prompt_path.write_text(
        json.dumps(
            {
                "prompts": [
                    {
                        "promptId": "prompt-aiu",
                        "logs": [
                            {
                                "metadata": {
                                    "usage": {
                                        "prompt_tokens": 50,
                                        "completion_tokens": 5,
                                        "copilot_usage": {"total_nano_aiu": 3.5},
                                    }
                                }
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_tool("prompt-exports", str(prompt_path), "--format", "markdown")

    assert "# Prompt Export Summary" in result.stdout
    assert "- AIU total: 3.5" in result.stdout


def test_tool_package_exports_main_and_parsers() -> None:
    assert callable(main)
    assert cli.parse_args(["prompt-exports", "input.json"]).command == "prompt-exports"
    assert (
        debug_logs.parse_args(["input.json", "--format", "markdown"]).format
        == "markdown"
    )
    assert (
        prompt_exports.parse_args(["input.json", "--format", "markdown"]).format
        == "markdown"
    )
