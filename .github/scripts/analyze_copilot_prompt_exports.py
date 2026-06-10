#!/usr/bin/env python3
"""Summarize Copilot prompt export JSON files without exposing raw bodies."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


VOLATILE_KEYS = frozenset(
    {
        "exported_at",
        "exportedAt",
        "generated_at",
        "generatedAt",
        "created_at",
        "createdAt",
        "file_path",
    }
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Copilot prompt export JSON files.")
    parser.add_argument("inputs", nargs="+", help="One or more Copilot prompt export JSON files.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser.parse_args(argv)


def strip_volatile(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: strip_volatile(item)
            for key, item in sorted(value.items())
            if key not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [strip_volatile(item) for item in value]
    return value


def stable_identity(value: object) -> str:
    normalized = strip_volatile(value)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def as_int(value: object) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def as_float(value: object) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def read_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def read_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def first_int(mapping: dict[str, object], *keys: str) -> int | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def first_str(mapping: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def measure_payload_bytes(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, bytes):
        return len(value)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if isinstance(value, (int, float, bool)):  # pragma: no cover - simple primitive fast path
        return len(str(value).encode("utf-8"))
    normalized = strip_volatile(value)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return len(payload.encode("utf-8"))


def normalized_kind(value: object) -> str:
    return str(value or "").replace("_", "").replace("-", "").lower()


def summarize_prompt_log(log: dict[str, object]) -> dict[str, object]:
    metadata = read_dict(log.get("metadata"))
    usage = read_dict(metadata.get("usage") or log.get("usage") or log.get("tokenUsage"))

    prompt_tokens = first_int(usage, "prompt_tokens", "promptTokens", "input_tokens", "inputTokens")
    if prompt_tokens is None:
        prompt_tokens = first_int(metadata, "maxPromptTokens", "max_prompt_tokens") or 0

    prompt_token_details = read_dict(usage.get("prompt_tokens_details") or usage.get("promptTokensDetails"))
    cached_tokens = first_int(prompt_token_details, "cached_tokens", "cachedTokens")
    if cached_tokens is None:
        cached_tokens = first_int(usage, "cachedPromptTokens", "cached_input_tokens", "cachedTokens") or 0

    completion_tokens = first_int(usage, "completion_tokens", "completionTokens", "output_tokens", "outputTokens") or 0

    reasoning_tokens = first_int(usage, "reasoning_tokens", "reasoningTokens")
    if reasoning_tokens is None:
        completion_details = read_dict(usage.get("completion_tokens_details") or usage.get("completionTokensDetails"))
        reasoning_tokens = first_int(completion_details, "reasoning_tokens", "reasoningTokens") or 0

    tool_name = first_str(log, "tool_name", "toolName", "name")
    kind = normalized_kind(log.get("kind") or log.get("type"))
    tool_kind = normalized_kind(tool_name)
    is_tool = bool(tool_name) and ("tool" in tool_kind or "tool" in kind)
    payload_bytes = 0
    if is_tool:
        payload_bytes = measure_payload_bytes(log.get("args") or log.get("arguments") or log.get("input"))
        payload_bytes += measure_payload_bytes(log.get("response") or log.get("result") or log.get("output"))

    return {
        "prompt_tokens": prompt_tokens,
        "cached_tokens": cached_tokens,
        "non_cached_input_tokens": max(prompt_tokens - cached_tokens, 0),
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "tool_name": tool_name,
        "tool_call": is_tool,
        "tool_payload_bytes": payload_bytes,
        "retry_hint": "retry" in tool_kind or "retry" in kind,
        "usage_signature": stable_identity(
            {
                "prompt_tokens": prompt_tokens,
                "cached_tokens": cached_tokens,
                "completion_tokens": completion_tokens,
                "reasoning_tokens": reasoning_tokens,
                "tool_payload_bytes": payload_bytes,
            }
        ),
    }


def summarize_prompt_export(prompt_export: dict[str, object], *, source_name: str) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    prompts = read_list(prompt_export.get("prompts"))

    for index, prompt in enumerate(prompts, start=1):
        if not isinstance(prompt, dict):
            continue

        logs = [item for item in read_list(prompt.get("logs")) if isinstance(item, dict)]
        log_summaries = [summarize_prompt_log(log) for log in logs]
        prompt_series = [as_int(summary["prompt_tokens"]) for summary in log_summaries if summary["prompt_tokens"] or summary["cached_tokens"] or summary["completion_tokens"] or summary["reasoning_tokens"] or summary["tool_payload_bytes"]]

        tool_counts_by_name: dict[str, int] = defaultdict(int)
        tool_payload_bytes_by_name: dict[str, int] = defaultdict(int)
        retry_groups: dict[str, dict[str, object]] = {}

        prompt_tokens_total = 0
        cache_read_tokens = 0
        non_cached_input_tokens = 0
        completion_tokens_total = 0
        reasoning_tokens_total = 0
        tool_payload_bytes_total = 0
        tool_calls = 0

        for summary in log_summaries:
            prompt_tokens_total += as_int(summary["prompt_tokens"])
            cache_read_tokens += as_int(summary["cached_tokens"])
            non_cached_input_tokens += as_int(summary["non_cached_input_tokens"])
            completion_tokens_total += as_int(summary["completion_tokens"])
            reasoning_tokens_total += as_int(summary["reasoning_tokens"])
            tool_payload_bytes_total += as_int(summary["tool_payload_bytes"])

            tool_name = str(summary["tool_name"])
            if summary["tool_call"] and tool_name:
                tool_calls += 1
                tool_counts_by_name[tool_name] += 1
                tool_payload_bytes_by_name[tool_name] += as_int(summary["tool_payload_bytes"])

            signature = str(summary["usage_signature"])
            retry_group = retry_groups.setdefault(
                signature,
                {
                    "prompt_name": first_str(prompt, "promptId", "prompt_id", "id", "title") or f"prompt-{index}",
                    "log_name": tool_name,
                    "occurrences": 0,
                    "prompt_tokens": as_int(summary["prompt_tokens"]),
                    "cached_tokens": as_int(summary["cached_tokens"]),
                    "completion_tokens": as_int(summary["completion_tokens"]),
                    "reasoning_tokens": as_int(summary["reasoning_tokens"]),
                    "retry_hint": False,
                },
            )
            retry_group["occurrences"] = as_int(retry_group["occurrences"]) + 1
            retry_group["retry_hint"] = bool(retry_group["retry_hint"]) or bool(summary["retry_hint"])
            if not retry_group["log_name"] and tool_name:
                retry_group["log_name"] = tool_name

        top_tool_payloads = [
            {
                "tool_name": tool_name,
                "payload_bytes": payload_bytes,
                "call_count": tool_counts_by_name[tool_name],
            }
            for tool_name, payload_bytes in sorted(
                tool_payload_bytes_by_name.items(),
                key=lambda item: (-item[1], -tool_counts_by_name[item[0]], item[0]),
            )
        ]

        retry_like_duplicate_records = [
            record
            for record in sorted(
                retry_groups.values(),
                key=lambda item: (-as_int(item["occurrences"]), str(item["prompt_name"]), str(item["log_name"])),
            )
            if as_int(record["occurrences"]) > 1 and bool(record["retry_hint"])
        ]

        summaries.append(
            {
                "source_name": source_name,
                "prompt_id": first_str(prompt, "promptId", "prompt_id", "id", "title") or f"prompt-{index}",
                "title": first_str(prompt, "title", "name") or f"prompt-{index}",
                "request_count": len(logs),
                "prompt_tokens": prompt_tokens_total,
                "cache_read_tokens": cache_read_tokens,
                "non_cached_input_tokens": non_cached_input_tokens,
                "completion_tokens": completion_tokens_total,
                "reasoning_tokens": reasoning_tokens_total,
                "max_prompt_tokens": max(prompt_series) if prompt_series else 0,
                "first_context_tokens": prompt_series[0] if prompt_series else 0,
                "last_context_tokens": prompt_series[-1] if prompt_series else 0,
                "context_growth_tokens": max((prompt_series[-1] - prompt_series[0]) if len(prompt_series) > 1 else 0, 0),
                "tool_calls": tool_calls,
                "tool_payload_bytes": tool_payload_bytes_total,
                "tool_counts_by_name": dict(sorted(tool_counts_by_name.items())),
                "top_tool_payloads": top_tool_payloads,
                "retry_like_duplicate_records": retry_like_duplicate_records,
            }
        )

    return summaries


def summarize_input(path: Path) -> tuple[str, list[dict[str, object]], int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("prompts"), list):
        return "prompt-export", summarize_prompt_export(data, source_name=path.name), 1
    return "unknown", [], 0


def aggregate_summaries(summaries: list[dict[str, object]]) -> dict[str, object]:
    tool_counts_by_name: dict[str, int] = defaultdict(int)
    tool_payload_bytes_by_name: dict[str, int] = defaultdict(int)
    retry_like_duplicate_records: list[dict[str, object]] = []
    max_prompt_tokens = 0
    first_context_tokens = 0
    last_context_tokens = 0
    context_growth_tokens = 0

    for summary in summaries:
        max_prompt_tokens = max(max_prompt_tokens, as_int(summary.get("max_prompt_tokens")))
        if not first_context_tokens and summary.get("first_context_tokens") is not None:
            first_context_tokens = as_int(summary.get("first_context_tokens"))
        if summary.get("last_context_tokens") is not None:
            last_context_tokens = as_int(summary.get("last_context_tokens"))
        context_growth_tokens += as_int(summary.get("context_growth_tokens"))

        for tool_name, count in read_dict(summary.get("tool_counts_by_name")).items():
            tool_counts_by_name[str(tool_name)] += as_int(count)
        for item in read_list(summary.get("top_tool_payloads")):
            if isinstance(item, dict):
                tool_payload_bytes_by_name[str(item.get("tool_name") or "")] += as_int(item.get("payload_bytes"))
        for record in read_list(summary.get("retry_like_duplicate_records")):
            if isinstance(record, dict):
                retry_like_duplicate_records.append(record)

    top_tool_payloads = [
        {
            "tool_name": tool_name,
            "payload_bytes": payload_bytes,
            "call_count": tool_counts_by_name[tool_name],
        }
        for tool_name, payload_bytes in sorted(
            tool_payload_bytes_by_name.items(),
            key=lambda item: (-item[1], -tool_counts_by_name[item[0]], item[0]),
        )
    ]

    return {
        "prompt_count": len(summaries),
        "request_count": sum(as_int(summary.get("request_count")) for summary in summaries),
        "prompt_tokens": sum(as_int(summary.get("prompt_tokens")) for summary in summaries),
        "cache_read_tokens": sum(as_int(summary.get("cache_read_tokens")) for summary in summaries),
        "non_cached_input_tokens": sum(as_int(summary.get("non_cached_input_tokens")) for summary in summaries),
        "completion_tokens": sum(as_int(summary.get("completion_tokens")) for summary in summaries),
        "reasoning_tokens": sum(as_int(summary.get("reasoning_tokens")) for summary in summaries),
        "max_prompt_tokens": max_prompt_tokens,
        "first_context_tokens": first_context_tokens,
        "last_context_tokens": last_context_tokens,
        "context_growth_tokens": context_growth_tokens,
        "tool_calls": sum(as_int(summary.get("tool_calls")) for summary in summaries),
        "tool_payload_bytes": sum(as_int(summary.get("tool_payload_bytes")) for summary in summaries),
        "tool_counts_by_name": dict(sorted(tool_counts_by_name.items())),
        "top_tool_payloads": top_tool_payloads,
        "retry_like_duplicate_count": len(retry_like_duplicate_records),
        "retry_like_duplicate_records": retry_like_duplicate_records,
    }


def build_report(paths: list[Path]) -> dict[str, object]:
    prompt_summaries: list[dict[str, object]] = []
    unique_exports: dict[str, list[dict[str, object]]] = {}
    prompt_export_count = 0
    unsupported_inputs: list[str] = []

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        kind, summaries, snapshot_like_count = summarize_input(path)
        if kind == "prompt-export":
            prompt_export_count += snapshot_like_count
            export_id = stable_identity(data)
            if export_id not in unique_exports and summaries:
                unique_exports[export_id] = summaries
            continue
        unsupported_inputs.append(path.name)

    for summaries in unique_exports.values():
        prompt_summaries.extend(summaries)

    return {
        "prompt_export_count": prompt_export_count,
        "deduped_prompt_export_count": len(unique_exports),
        "unsupported_input_count": len(unsupported_inputs),
        "unsupported_inputs": unsupported_inputs,
        "prompts": prompt_summaries,
        "aggregate": aggregate_summaries(prompt_summaries),
    }


def format_markdown(report: dict[str, object]) -> str:
    aggregate = read_dict(report.get("aggregate"))
    lines = ["# Prompt Export Summary", ""]
    lines.append(
        f"- Prompt exports: {report.get('deduped_prompt_export_count', 0)} deduped from {report.get('prompt_export_count', 0)} inputs"
    )
    lines.append(f"- Unsupported inputs: {report.get('unsupported_input_count', 0)}")
    lines.append(f"- Requests: {aggregate.get('request_count', 0)}")
    lines.append(f"- Prompt tokens: {aggregate.get('prompt_tokens', 0)}")
    lines.append(f"- Cache read tokens: {aggregate.get('cache_read_tokens', 0)}")
    lines.append(f"- Non-cached input tokens: {aggregate.get('non_cached_input_tokens', 0)}")
    lines.append(f"- Completion tokens: {aggregate.get('completion_tokens', 0)}")
    lines.append(f"- Reasoning tokens: {aggregate.get('reasoning_tokens', 0)}")
    lines.append(f"- Max prompt tokens: {aggregate.get('max_prompt_tokens', 0)}")
    lines.append(f"- Retry-like duplicate records: {aggregate.get('retry_like_duplicate_count', 0)}")
    lines.append("")
    lines.append("## Top Tool Payloads")
    top_tool_payloads = read_list(aggregate.get("top_tool_payloads"))
    if not top_tool_payloads:
        lines.append("- None")
    else:
        for item in top_tool_payloads[:10]:
            if isinstance(item, dict):
                lines.append(
                    f"- {item.get('tool_name', '')}: {item.get('payload_bytes', 0)} bytes across {item.get('call_count', 0)} calls"
                )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = [Path(item) for item in args.inputs]
    try:
        report = build_report(paths)
    except FileNotFoundError as exc:
        print(f"Error: file not found: {exc.filename}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {exc.doc!r}: {exc.msg}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
