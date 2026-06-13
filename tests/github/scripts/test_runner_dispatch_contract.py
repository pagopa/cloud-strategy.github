from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RUNNER = Path(".github/scripts/run.sh").resolve()


def run_runner(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(RUNNER), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_runner_rejects_unknown_tool_with_usage() -> None:
    result = run_runner("unknown_tool")

    assert result.returncode == 1
    assert "Unknown tool: unknown_tool" in result.stderr
    assert "Usage:" in result.stderr or "Usage:" in result.stdout


def test_runner_resolves_diagnostic_cli_aliases_through_venv() -> None:
    commands = (
        ("analyze_copilot_prompt_exports", "--help"),
        ("analyze_copilot_debug_logs", "--help"),
        ("benchmark_skill_tokens",),
    )

    for command in commands:
        result = run_runner(*command)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() or result.stderr.strip()


def test_runner_supports_python_suffix_alias_for_diagnostic_cli() -> None:
    result = run_runner("analyze_copilot_prompt_exports.py", "--help")

    assert result.returncode == 0, result.stderr
    assert "Summarize Copilot prompt export JSON files" in result.stdout
