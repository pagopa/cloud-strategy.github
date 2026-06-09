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
