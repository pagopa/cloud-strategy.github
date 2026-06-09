from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(
    ".github/skills/internal-gateway-operational-flow/scripts/analyze_run_efficiency.py"
)


def run_analyzer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_help_returns_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_missing_file_returns_nonzero() -> None:
    result = run_analyzer("/nonexistent/path/export.json")
    assert result.returncode == 1
    assert "not found" in result.stderr


def test_invalid_json_returns_nonzero() -> None:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not json")
        path = f.name
    result = run_analyzer(path)
    assert result.returncode == 1
    assert "invalid JSON" in result.stderr


def test_unsupported_shape_returns_nonzero() -> None:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"unknown": "value"}, f)
        path = f.name
    result = run_analyzer(path)
    assert result.returncode == 2
    assert "Unsupported top-level shape" in result.stderr


def test_basic_requests_shape_text_output() -> None:
    import tempfile
    export = {
        "requests": [
            {
                "name": "main-agent-turn-1",
                "usage": {
                    "promptTokens": 100,
                    "cachedPromptTokens": 50,
                    "completionTokens": 20,
                    "reasoningTokens": 5,
                },
                "duration": 1000,
            },
            {
                "name": "main-agent-turn-2",
                "usage": {
                    "promptTokens": 300,
                    "cachedPromptTokens": 100,
                    "completionTokens": 40,
                    "reasoningTokens": 10,
                },
                "duration": 2000,
            },
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "text")
    assert result.returncode == 0
    assert "Structural input cost" in result.stdout
    assert "Repository-controllable loop signals" in result.stdout
    assert "Total requests: 2" in result.stdout
    assert "Total input tokens: 400" in result.stdout
    assert "Cached input: 150" in result.stdout
    assert "Uncached input: 250" in result.stdout
    assert "Completion tokens: 60" in result.stdout
    assert "Reasoning tokens: 15" in result.stdout
    assert "Total duration (ms): 3,000" in result.stdout


def test_basic_requests_shape_json_output() -> None:
    import tempfile
    export = {
        "requests": [
            {
                "name": "main-agent-turn-1",
                "usage": {
                    "promptTokens": 100,
                },
                "duration": 1000,
            },
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["summary"]["total_requests"] == 1
    assert data["summary"]["total_input_tokens"] == 100
    assert data["advisory_note"] != ""
    assert "diagnostic" in data["advisory_note"].lower() or "advisory" in data["advisory_note"].lower()


def test_critical_group_warning() -> None:
    import tempfile
    export = {
        "requests": [
            {"name": "critical-master-1", "usage": {"promptTokens": 10}, "duration": 100},
            {"name": "critical-master-1", "usage": {"promptTokens": 10}, "duration": 100},
            {"name": "critical-master-1", "usage": {"promptTokens": 10}, "duration": 100},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert any("Repeated critical" in w for w in data["warnings"])


def test_high_requests_per_user_prompt_warning() -> None:
    import tempfile
    export = {
        "requests": [
            {"name": "main", "userPrompt": "plan the work", "usage": {"promptTokens": 10}, "duration": 100}
            for _ in range(8)
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert any("High requests per user prompt" in w for w in data["warnings"])


def test_large_prompt_growth_warning() -> None:
    import tempfile
    export = {
        "requests": [
            {"name": "main-agent-1", "usage": {"promptTokens": 1000}, "duration": 100},
            {"name": "main-agent-2", "usage": {"promptTokens": 5000}, "duration": 100},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert any("Large prompt growth" in w for w in data["warnings"])


def test_no_prompt_content_in_output() -> None:
    import tempfile
    export = {
        "requests": [
            {
                "name": "main",
                "userPrompt": "secret user prompt text",
                "usage": {"promptTokens": 10},
                "duration": 100,
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    # Ensure the raw prompt string does not appear in output.
    assert "secret user prompt text" not in result.stdout
    assert "secret user prompt text" not in result.stderr


def test_absent_optional_usage_fields() -> None:
    import tempfile
    export = {
        "requests": [
            {"name": "main", "usage": {"promptTokens": 100}},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["summary"]["completion_tokens"] == 0
    assert data["summary"]["reasoning_tokens"] == 0


def test_messages_wrapper_alternative() -> None:
    import tempfile
    export = {
        "messages": [
            {"name": "turn-1", "usage": {"promptTokens": 50}, "duration": 500},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["summary"]["total_requests"] == 1


def test_conversation_wrapper_alternative() -> None:
    import tempfile
    export = {
        "conversation": [
            {"name": "turn-1", "usage": {"promptTokens": 50}, "duration": 500},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["summary"]["total_requests"] == 1


def test_user_prompt_aggregates_grouped_by_prompt() -> None:
    import tempfile
    export = {
        "requests": [
            {"name": "main", "userPrompt": "do A", "usage": {"promptTokens": 10}, "duration": 100},
            {"name": "main", "userPrompt": "do A", "usage": {"promptTokens": 20}, "duration": 100},
            {"name": "main", "userPrompt": "do B", "usage": {"promptTokens": 30}, "duration": 100},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(export, f)
        path = f.name
    result = run_analyzer(path, "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    upa = data["user_prompt_aggregates"]
    assert len(upa) == 2
    # Sort by requests desc; first should be "do A" with 2 requests and 30 tokens
    assert upa[0]["requests"] == 2
    assert upa[0]["input_tokens"] == 30
    assert upa[1]["requests"] == 1
    assert upa[1]["input_tokens"] == 30


def test_prompt_export_shape_deduplicates_by_prompt_id_and_uses_chatml_success_logs(
    tmp_path: Path,
) -> None:
    older = tmp_path / "older-prompt-export.json"
    newer = tmp_path / "newer-prompt-export.json"
    older.write_text(
        json.dumps(
            {
                "exportedAt": "2026-06-09T10:00:00Z",
                "prompts": [
                    {
                        "promptId": "prompt-123",
                        "logCount": 1,
                        "logs": [
                            {
                                "kind": "ChatMLSuccess",
                                "request": {
                                    "metadata": {
                                        "usage": {
                                            "promptTokens": 100,
                                            "cachedPromptTokens": 25,
                                            "completionTokens": 10,
                                            "reasoningTokens": 2,
                                        }
                                    },
                                },
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    newer.write_text(
        json.dumps(
            {
                "exportedAt": "2026-06-09T11:00:00Z",
                "prompts": [
                    {
                        "promptId": "prompt-123",
                        "logCount": 3,
                        "logs": [
                            {
                                "kind": "ChatMLSuccess",
                                "request": {
                                    "metadata": {
                                        "usage": {
                                            "promptTokens": 200,
                                            "prompt_tokens_details": {"cached_tokens": 50},
                                            "completionTokens": 20,
                                            "reasoningTokens": 5,
                                        }
                                    },
                                },
                            },
                            {
                                "kind": "Other",
                                "promptText": "sentinel prompt text",
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_analyzer(str(older), str(newer), "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["summary"]["total_requests"] == 1
    assert data["summary"]["total_model_calls"] == 1
    assert data["summary"]["total_input_tokens"] == 200
    assert data["summary"]["cached_input_tokens"] == 50
    assert data["summary"]["uncached_input_tokens"] == 150
    assert data["summary"]["completion_tokens"] == 20
    assert data["summary"]["reasoning_tokens"] == 5
    assert data["summary"]["cache_rate"] == 0.25
    assert data["summary"]["input_output_ratio"] == 8.0
    assert len(data["sources"]) == 1
    assert data["sources"][0]["kind"] == "prompt_history"
    assert data["sources"][0]["first_input_tokens"] == 200
    assert data["sources"][0]["last_input_tokens"] == 200
    assert data["sources"][0]["context_growth_factor"] == 1.0
    assert "sentinel prompt text" not in result.stdout
    assert "sentinel prompt text" not in result.stderr


def test_otel_debug_log_shape_exposes_tool_and_loop_metrics(tmp_path: Path) -> None:
    log_path = tmp_path / "otel-session.json"
    log_path.write_text(
        json.dumps(
            {
                "resourceSpans": [
                    {
                        "resource": {
                            "attributes": [
                                {"key": "service.name", "value": {"stringValue": "demo"}},
                            ]
                        },
                        "scopeSpans": [
                            {
                                "spans": [
                                    {
                                        "name": "model-1",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "gen_ai.request.model": "gpt-4.1",
                                            "gen_ai.usage.input_tokens": 100,
                                            "gen_ai.usage.input_tokens_details.cached_tokens": 20,
                                            "gen_ai.usage.output_tokens": 10,
                                            "gen_ai.usage.output_tokens_details.reasoning_tokens": 2,
                                            "duration_ms": 10,
                                        },
                                    },
                                    {
                                        "name": "tool-search-a",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "tool.name": "search",
                                            "tool.kind": "lookup",
                                            "tool.command": "--redacted--",
                                            "duration_ms": 2,
                                        },
                                    },
                                    {
                                        "name": "tool-search-b",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "tool.name": "search",
                                            "tool.kind": "lookup",
                                            "tool.command": "--redacted--",
                                            "duration_ms": 2,
                                        },
                                    },
                                    {
                                        "name": "validation-1",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "tool.name": "pytest",
                                            "tool.category": "validation",
                                            "validation.command": "pytest -q unit",
                                            "duration_ms": 3,
                                        },
                                    },
                                    {
                                        "name": "validation-2",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "tool.name": "pytest",
                                            "tool.category": "validation",
                                            "validation.command": "pytest -q unit",
                                            "duration_ms": 3,
                                        },
                                    },
                                    {
                                        "name": "patch-step",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "tool.name": "apply_patch",
                                            "action.type": "patch",
                                            "duration_ms": 1,
                                        },
                                    },
                                    {
                                        "name": "model-2",
                                        "attributes": {
                                            "gen_ai.session.id": "session-42",
                                            "gen_ai.request.model": "gpt-4.1",
                                            "gen_ai.usage.input_tokens": 13_000,
                                            "gen_ai.usage.input_tokens_details.cached_tokens": 200,
                                            "gen_ai.usage.output_tokens": 1,
                                            "gen_ai.usage.output_tokens_details.reasoning_tokens": 1,
                                            "duration_ms": 20,
                                        },
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

    result = run_analyzer(str(log_path), "--format", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)

    assert data["summary"]["total_requests"] == 2
    assert data["summary"]["total_input_tokens"] == 13_100
    assert data["summary"]["cached_input_tokens"] == 220
    assert data["summary"]["uncached_input_tokens"] == 12_880
    assert data["summary"]["completion_tokens"] == 11
    assert data["summary"]["reasoning_tokens"] == 3
    assert data["summary"]["calls_above_context_threshold"] == 1
    assert data["summary"]["low_output_calls"] == 2
    assert data["summary"]["low_output_input_tokens"] == 13_100
    assert data["summary"]["tool_calls_by_tool"] == {"apply_patch": 1, "pytest": 2, "search": 2}
    assert data["summary"]["repeated_identical_tool_calls"] == 2
    assert data["summary"]["repeated_validation_commands"] == 1
    assert data["summary"]["pre_action_tool_calls"] == 4
    assert data["sources"][0]["first_input_tokens"] == 100
    assert data["sources"][0]["last_input_tokens"] == 13_000
    assert data["sources"][0]["context_growth_factor"] == 130.0
    assert data["sources"][0]["calls_above_context_threshold"] == 1
    assert data["sources"][0]["low_output_calls"] == 2


def test_multiple_input_paths_and_privacy_do_not_leak_sensitive_content(
    tmp_path: Path,
) -> None:
    prompt_export = tmp_path / "sensitive-prompt-export.json"
    otel_log = tmp_path / "sensitive-otel-log.json"
    prompt_export.write_text(
        json.dumps(
            {
                "exportedAt": "2026-06-09T12:00:00Z",
                "prompts": [
                    {
                        "promptId": "prompt-sensitive",
                        "logCount": 1,
                        "logs": [
                            {
                                "kind": "ChatMLSuccess",
                                "request": {
                                    "metadata": {
                                        "usage": {
                                            "promptTokens": 10,
                                            "completionTokens": 1,
                                        }
                                    },
                                    "userPrompt": "sentinel user prompt text",
                                    "toolArgs": {"secret": "sentinel tool argument"},
                                    "toolResult": "sentinel tool result",
                                    "sourcePath": "/tmp/sentinel/source/path",
                                },
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    otel_log.write_text(
        json.dumps(
            {
                "resourceSpans": [
                    {
                        "scopeSpans": [
                            {
                                "spans": [
                                    {
                                        "name": "model-privacy",
                                        "attributes": {
                                            "gen_ai.session.id": "privacy-session",
                                            "gen_ai.request.model": "gpt-4.1",
                                            "gen_ai.usage.input_tokens": 20,
                                            "gen_ai.usage.output_tokens": 2,
                                            "tool.command": "sentinel command text",
                                            "tool.arguments": "sentinel tool argument",
                                            "tool.result": "sentinel tool result",
                                            "source.path": "/tmp/sentinel/source/path",
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_analyzer(str(prompt_export), str(otel_log), "--format", "json")
    assert result.returncode == 0
    assert "sentinel user prompt text" not in result.stdout
    assert "sentinel tool argument" not in result.stdout
    assert "sentinel tool result" not in result.stdout
    assert "sentinel command text" not in result.stdout
    assert "sentinel user prompt text" not in result.stderr
    assert "sentinel tool argument" not in result.stderr
    assert "sentinel tool result" not in result.stderr
    assert "sentinel command text" not in result.stderr
    assert "sensitive-prompt-export.json" not in result.stdout
    assert "sensitive-otel-log.json" not in result.stdout
    assert "/tmp/sentinel/source/path" not in result.stdout
    assert "/tmp/sentinel/source/path" not in result.stderr
