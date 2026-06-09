#!/usr/bin/env python3
"""Advisory run-efficiency analyzer for Copilot prompt-export JSON.

Emits aggregate metrics and warnings only. Never emits prompt text,
tool arguments, tool results, or paths from the input export.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Advisory thresholds; labeled as constants, not policy gates.
WARNING_HIGH_REQUESTS_PER_USER_PROMPT = 6
WARNING_LARGE_PROMPT_GROWTH_FACTOR = 3.0
WARNING_REPEATED_CRITICAL_GROUP = 2


def analyze(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Top-level export must be a JSON object.")

    # Try to handle the known Copilot export shape.
    requests = data.get("requests") or data.get("messages")
    if requests is None:
        # Some exports wrap under a 'conversation' or 'history' key.
        for key in ("conversation", "history", "turns", "items"):
            if key in data and isinstance(data[key], list):
                requests = data[key]
                break

    if not isinstance(requests, list):
        raise ValueError(
            "Unsupported top-level shape: expected 'requests', 'messages', "
            "or a recognized list wrapper."
        )

    total_requests = len(requests)
    total_input_tokens = 0
    cached_input_tokens = 0
    uncached_input_tokens = 0
    completion_tokens = 0
    reasoning_tokens = 0
    total_duration_ms = 0

    requests_by_name: dict[str, int] = defaultdict(int)
    user_prompt_requests: dict[str, int] = defaultdict(int)
    user_prompt_input_tokens: dict[str, int] = defaultdict(int)

    critical_groups: list[str] = []

    for req in requests:
        if not isinstance(req, dict):
            continue

        name = req.get("name") or req.get("requestName") or req.get("role") or "unknown"
        requests_by_name[name] += 1

        # Detect critical subagent groups by name heuristic
        if name and "critical" in str(name).lower():
            critical_groups.append(str(name))

        # User prompt grouping
        user_prompt = req.get("userPrompt") or req.get("user_prompt") or req.get("prompt")
        if user_prompt:
            up_str = str(user_prompt)[:120]  # Truncate for key safety
            user_prompt_requests[up_str] += 1
            # Do not store the actual prompt text anywhere in output.

        usage = req.get("usage") or req.get("tokenUsage") or {}
        if not isinstance(usage, dict):
            usage = {}

        prompt_tokens = usage.get("promptTokens") or usage.get("prompt_tokens") or usage.get("input_tokens") or 0
        cached = usage.get("cachedPromptTokens") or usage.get("cached_input_tokens") or 0
        uncached = usage.get("uncachedPromptTokens") or usage.get("uncached_input_tokens")
        if uncached is None and prompt_tokens and cached is not None:
            uncached = prompt_tokens - cached
        completion = usage.get("completionTokens") or usage.get("completion_tokens") or 0
        reasoning = usage.get("reasoningTokens") or usage.get("reasoning_tokens") or 0
        duration = req.get("duration") or req.get("modelDuration") or req.get("durationMs") or 0

        total_input_tokens += prompt_tokens or 0
        if cached:
            cached_input_tokens += cached
        if uncached:
            uncached_input_tokens += uncached
        completion_tokens += completion or 0
        reasoning_tokens += reasoning or 0
        total_duration_ms += duration or 0

        if user_prompt and prompt_tokens:
            up_str = str(user_prompt)[:120]
            user_prompt_input_tokens[up_str] += prompt_tokens or 0

    # Build per-user-prompt aggregates (keyed by index, not content)
    user_prompt_aggregates = []
    for idx, (up_key, count) in enumerate(sorted(user_prompt_requests.items(), key=lambda x: -x[1])):
        user_prompt_aggregates.append({
            "index": idx,
            "requests": count,
            "input_tokens": user_prompt_input_tokens.get(up_key, 0),
        })

    warnings: list[str] = []

    # Repeated critical group warning
    critical_counts: dict[str, int] = defaultdict(int)
    for cg in critical_groups:
        critical_counts[cg] += 1
    for cg, count in critical_counts.items():
        if count >= WARNING_REPEATED_CRITICAL_GROUP:
            warnings.append(
                f"Repeated critical subagent group '{cg}': {count} requests "
                f"(advisory threshold: {WARNING_REPEATED_CRITICAL_GROUP})"
            )

    # High requests per user prompt
    for upa in user_prompt_aggregates:
        if upa["requests"] >= WARNING_HIGH_REQUESTS_PER_USER_PROMPT:
            warnings.append(
                f"High requests per user prompt (index {upa['index']}): "
                f"{upa['requests']} requests "
                f"(advisory threshold: {WARNING_HIGH_REQUESTS_PER_USER_PROMPT})"
            )

    # Large prompt growth: compare first and last main-agent-like request sizes
    main_agent_input_tokens = []
    for req in requests:
        if not isinstance(req, dict):
            continue
        name = req.get("name") or req.get("requestName") or ""
        if "main" in str(name).lower() or "agent" in str(name).lower():
            usage = req.get("usage") or req.get("tokenUsage") or {}
            if isinstance(usage, dict):
                pt = usage.get("promptTokens") or usage.get("prompt_tokens") or usage.get("input_tokens") or 0
                if pt:
                    main_agent_input_tokens.append(pt)
    if len(main_agent_input_tokens) >= 2:
        first = main_agent_input_tokens[0]
        last = main_agent_input_tokens[-1]
        if first > 0 and last / first >= WARNING_LARGE_PROMPT_GROWTH_FACTOR:
            warnings.append(
                f"Large prompt growth: first main-agent prompt {first} tokens, "
                f"last {last} tokens (factor {last/first:.1f}, "
                f"advisory threshold: {WARNING_LARGE_PROMPT_GROWTH_FACTOR}x)"
            )

    result = {
        "summary": {
            "total_requests": total_requests,
            "requests_by_name": dict(requests_by_name),
            "total_input_tokens": total_input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "total_duration_ms": total_duration_ms,
        },
        "user_prompt_aggregates": user_prompt_aggregates,
        "warnings": warnings,
        "advisory_note": (
            "Metrics are diagnostic/advisory only. "
            "No threshold permits skipping required evidence, gates, or validation."
        ),
    }

    return result


def format_text(result: dict) -> str:
    lines: list[str] = []
    s = result["summary"]
    lines.append("Run Efficiency Analysis (Advisory)")
    lines.append("=" * 40)
    lines.append(f"Total requests: {s['total_requests']}")
    lines.append(f"Requests by name:")
    for name, count in sorted(s["requests_by_name"].items(), key=lambda x: -x[1]):
        lines.append(f"  {name}: {count}")
    lines.append(f"Total input tokens: {s['total_input_tokens']:,}")
    lines.append(f"  Cached input: {s['cached_input_tokens']:,}")
    lines.append(f"  Uncached input: {s['uncached_input_tokens']:,}")
    lines.append(f"Completion tokens: {s['completion_tokens']:,}")
    lines.append(f"Reasoning tokens: {s['reasoning_tokens']:,}")
    lines.append(f"Total duration (ms): {s['total_duration_ms']:,}")
    lines.append("")
    lines.append("User prompt aggregates:")
    for upa in result["user_prompt_aggregates"]:
        lines.append(f"  Prompt index {upa['index']}: {upa['requests']} requests, {upa['input_tokens']:,} input tokens")
    lines.append("")
    if result["warnings"]:
        lines.append("Warnings:")
        for w in result["warnings"]:
            lines.append(f"  - {w}")
    else:
        lines.append("Warnings: none")
    lines.append("")
    lines.append(f"Note: {result['advisory_note']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Advisory run-efficiency analyzer for Copilot prompt-export JSON."
    )
    parser.add_argument("export_path", type=Path, help="Path to Copilot prompt-export JSON.")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format."
    )
    args = parser.parse_args(argv)

    if not args.export_path.exists():
        print(f"Error: file not found: {args.export_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(args.export_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON: {exc}", file=sys.stderr)
        return 1

    try:
        result = analyze(data)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
