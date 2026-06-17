from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.analyze_copilot_debug_log import prompt_exports

SCRIPT = Path(".github/scripts/analyze_copilot_prompt_exports.py").resolve()


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


def test_analyzer_summarizes_prompt_exports_and_dedupes_duplicates(
    tmp_path: Path,
) -> None:
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
                            "usage": {
                                "prompt_tokens": 100,
                                "prompt_tokens_details": {"cached_tokens": 70},
                                "completion_tokens": 12,
                                "reasoning_tokens": 3,
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
                        "tool": "tool_search",
                        "args": {"query": "graphify"},
                        "result": {"message": "BBBBB"},
                        "metadata": {
                            "usage": {
                                "prompt_tokens": 40,
                                "completion_tokens": 2,
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

    result = run_script(prompt_a, prompt_b)
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


def test_analyzer_defaults_missing_usage_and_reports_unsupported_schema(
    tmp_path: Path,
) -> None:
    prompt_path = tmp_path / "prompt.json"
    prompt_path.write_text(
        json.dumps(
            {
                "prompts": [
                    {
                        "id": "prompt-2",
                        "logs": [
                            {
                                "name": "empty_log",
                                "kind": "info",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    unknown_path = tmp_path / "unknown.json"
    unknown_path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")

    result = run_script(prompt_path, unknown_path)
    payload = json.loads(result.stdout)

    assert payload["unsupported_input_count"] == 1
    assert payload["unsupported_inputs"] == ["unknown.json"]
    assert payload["aggregate"]["request_count"] == 1
    assert payload["aggregate"]["prompt_tokens"] == 0
    assert payload["aggregate"]["cache_read_tokens"] == 0
    assert payload["aggregate"]["non_cached_input_tokens"] == 0
    assert payload["aggregate"]["completion_tokens"] == 0
    assert payload["aggregate"]["reasoning_tokens"] == 0
    assert payload["aggregate"]["top_tool_payloads"] == []


def test_analyzer_can_render_markdown(tmp_path: Path) -> None:
    prompt_path = tmp_path / "prompt.json"
    prompt_path.write_text(
        json.dumps(
            {
                "prompts": [
                    {
                        "promptId": "prompt-3",
                        "title": "Markdown prompt",
                        "logs": [
                            {
                                "name": "model_request",
                                "kind": "request",
                                "metadata": {
                                    "usage": {
                                        "prompt_tokens": 20,
                                        "completion_tokens": 4,
                                    }
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_script(prompt_path, format="markdown")

    assert "# Prompt Export Summary" in result.stdout
    assert "Markdown prompt" not in result.stdout
    assert "Cache read ratio:" in result.stdout
    assert "## Prompt Composition" in result.stdout


def test_prompt_export_tool_package_is_importable() -> None:
    assert prompt_exports.parse_args(["input.json", "--format", "markdown"]).format == "markdown"
