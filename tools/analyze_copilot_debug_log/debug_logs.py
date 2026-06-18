#!/usr/bin/env python3
"""Summarize Copilot debug exports without exposing prompt or response bodies by default."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import cast

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

MEMORY_PATH_SENTINEL = "/memories/repo/"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize Copilot debug logs and snapshot exports."
    )
    parser.add_argument(
        "inputs", nargs="+", help="JSON debug-log or snapshot-export files."
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser.parse_args(argv)


def stable_identity(value: object) -> str:
    normalized = strip_volatile(value)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def as_int(value: object) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def as_float(value: object) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def iter_dicts(value: object) -> list[dict[str, object]]:
    if isinstance(value, dict):
        return [value]
    if not isinstance(value, list):
        return []
    collected: list[dict[str, object]] = []
    for item in value:
        collected.extend(iter_dicts(item))
    return collected


def measure_payload_bytes(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, bytes):
        return len(value)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if isinstance(value, (int, float, bool)):
        return len(str(value).encode("utf-8"))
    normalized = strip_volatile(value)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return len(payload.encode("utf-8"))


def contains_text(value: object, needle: str) -> bool:
    if isinstance(value, str):
        return needle in value
    if isinstance(value, dict):
        return any(contains_text(item, needle) for item in value.values())
    if isinstance(value, list):
        return any(contains_text(item, needle) for item in value)
    return False


def normalized_kind(value: object) -> str:
    return str(value or "").replace("_", "").replace("-", "").lower()


def candidate_payload_bytes(mapping: dict[str, object], *keys: str) -> int:
    for key in keys:
        if key in mapping:
            return measure_payload_bytes(mapping.get(key))
    return 0


def read_otlp_value(value: object) -> object:
    if not isinstance(value, dict):
        return value
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in value:
            return value[key]
    array_value = value.get("arrayValue")
    if isinstance(array_value, dict):
        return [
            read_otlp_value(item.get("value"))
            for item in iter_dicts(array_value.get("values"))
        ]
    kvlist_value = value.get("kvlistValue")
    if isinstance(kvlist_value, dict):
        return {
            item.get("key"): read_otlp_value(item.get("value"))
            for item in iter_dicts(kvlist_value.get("values"))
            if isinstance(item.get("key"), str)
        }
    return value


def read_otlp_attributes(attributes: object) -> dict[str, object]:
    if not isinstance(attributes, list):
        return {}
    result: dict[str, object] = {}
    for attribute in attributes:
        if not isinstance(attribute, dict):
            continue
        key = attribute.get("key")
        if isinstance(key, str) and key:
            result[key] = read_otlp_value(attribute.get("value"))
    return result


def get_first_int(mapping: dict[str, object], *keys: str) -> int | None:
    for key in keys:
        if key in mapping:
            value = mapping.get(key)
            if isinstance(value, dict):
                nested_value = get_first_int(value, *keys)
                if nested_value is not None:
                    return nested_value
            elif isinstance(value, (int, float)):
                return int(value)
    return None


def get_first_float(mapping: dict[str, object], *keys: str) -> float | None:
    for key in keys:
        if key in mapping:
            value = mapping.get(key)
            if isinstance(value, dict):
                nested_value = get_first_float(value, *keys)
                if nested_value is not None:
                    return nested_value
            elif isinstance(value, (int, float)):
                return float(value)
    return None


def get_first_str(mapping: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def normalize_log_records(value: object) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in iter_dicts(value):
        records.append(item)
    return records


def extract_int(mapping: dict[str, object], *keys: str) -> int | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def extract_float(mapping: dict[str, object], *keys: str) -> float | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def otlp_status_code(span: dict[str, object]) -> int:
    status = span.get("status")
    if isinstance(status, dict):
        return as_int(status.get("code"))
    return 0


def summarize_otlp_span(span: dict[str, object]) -> dict[str, object]:
    attributes = read_otlp_attributes(span.get("attributes"))
    input_tokens = extract_int(attributes, "gen_ai.usage.input_tokens") or 0
    output_tokens = extract_int(attributes, "gen_ai.usage.output_tokens") or 0
    tool_name = str(attributes.get("gen_ai.tool.name") or "")
    tool_result_value = attributes.get("gen_ai.tool.call.result")
    is_tool_call = 1 if tool_name else 0
    is_model_request = 1 if not tool_name else 0
    tool_result_bytes = measure_payload_bytes(attributes.get("gen_ai.tool.call.result"))
    is_error = (
        1
        if otlp_status_code(span) == 2
        or attributes.get("copilot_chat.event_category") == "error"
        else 0
    )
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model_request_count": is_model_request,
        "tool_call_count": is_tool_call,
        "tool_calls": is_tool_call,
        "request_message_bytes": candidate_payload_bytes(
            attributes, "gen_ai.input.value", "gen_ai.input.messages", "gen_ai.prompt"
        ),
        "tool_result_bytes": tool_result_bytes,
        "tool_schema_bytes": candidate_payload_bytes(
            attributes, "gen_ai.tool.schemas", "gen_ai.tool.schema", "gen_ai.tools"
        ),
        "error_count": is_error,
        "invocation_error_count": is_error,
        "missing_memory_path_error_count": 1
        if contains_text(tool_result_value, MEMORY_PATH_SENTINEL)
        else 0,
        "graphify_invocation_count": 1 if "graphify" in tool_name else 0,
        "graphify_discovery_count": 1
        if "discover" in tool_name or "tool_search" in tool_name
        else 0,
    }


def summarize_otlp_export(
    resource_spans: list[dict[str, object]], *, source_name: str | None = None
) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for resource_span in resource_spans:
        resource = (
            resource_span.get("resource")
            if isinstance(resource_span.get("resource"), dict)
            else {}
        )
        resource_attrs = read_otlp_attributes(
            resource.get("attributes") if isinstance(resource, dict) else []
        )
        scope_spans = normalize_log_records(resource_span.get("scopeSpans"))
        spans: list[dict[str, object]] = []
        for scope_span in scope_spans:
            spans.extend(normalize_log_records(scope_span.get("spans")))

        request_spans: list[dict[str, object]] = []
        model_request_count = 0
        tool_call_count = 0
        request_message_bytes = 0
        tool_schema_bytes = 0
        tool_result_bytes = 0
        tool_calls = 0
        error_count = 0
        invocation_error_count = 0
        missing_memory_path_error_count = 0
        graphify_invocation_count = 0
        graphify_discovery_count = 0
        input_tokens_total = 0
        output_tokens_total = 0

        for span in spans:
            span_summary = summarize_otlp_span(span)
            if span_summary["input_tokens"] or span_summary["output_tokens"]:
                request_spans.append(span_summary)
                input_tokens_total += as_int(span_summary["input_tokens"])
                output_tokens_total += as_int(span_summary["output_tokens"])
            model_request_count += as_int(span_summary["model_request_count"])
            tool_call_count += as_int(span_summary["tool_call_count"])
            request_message_bytes += as_int(span_summary["request_message_bytes"])
            tool_schema_bytes += as_int(span_summary["tool_schema_bytes"])
            tool_calls += as_int(span_summary["tool_call_count"])
            tool_result_bytes += as_int(span_summary["tool_result_bytes"])
            error_count += as_int(span_summary["error_count"])
            invocation_error_count += as_int(span_summary["invocation_error_count"])
            missing_memory_path_error_count += as_int(
                span_summary["missing_memory_path_error_count"]
            )
            graphify_invocation_count += as_int(
                span_summary["graphify_invocation_count"]
            )
            graphify_discovery_count += as_int(span_summary["graphify_discovery_count"])

        context_series = [
            as_int(item["input_tokens"])
            for item in request_spans
            if item.get("input_tokens") is not None
        ]
        context_growth_tokens = (
            max(context_series[-1] - context_series[0], 0)
            if len(context_series) > 1
            else 0
        )
        session_id = (
            resource_attrs.get("copilotChat.sessionId")
            or resource_attrs.get("session.id")
            or resource_attrs.get("session_id")
            or source_name
            or "unknown-session"
        )
        title = (
            resource_attrs.get("copilotChat.sessionTitle")
            or resource_attrs.get("session.title")
            or resource_attrs.get("service.name")
            or session_id
        )
        summaries.append(
            {
                "session_id": str(session_id),
                "title": str(title),
                "model_request_count": model_request_count,
                "tool_call_count": tool_call_count,
                "request_count": model_request_count + tool_call_count,
                "input_tokens": input_tokens_total,
                "output_tokens": output_tokens_total,
                "cache_read_tokens": None,
                "estimated_cache_read_tokens": None,
                "non_cached_input_tokens": None,
                "estimated_non_cached_input_tokens": None,
                "aiu_total": None,
                "estimated_aiu_total": None,
                "request_message_bytes": request_message_bytes,
                "tool_calls": tool_calls,
                "tool_result_bytes": tool_result_bytes,
                "tool_result_volume_bytes": tool_result_bytes,
                "tool_schema_bytes": tool_schema_bytes,
                "error_count": error_count,
                "invocation_error_count": invocation_error_count,
                "missing_memory_path_error_count": missing_memory_path_error_count,
                "graphify_invocation_count": graphify_invocation_count,
                "graphify_discovery_count": graphify_discovery_count,
                "max_context_tokens": max(context_series) if context_series else 0,
                "runtime_context_tokens": max(context_series) if context_series else 0,
                "context_growth_tokens": context_growth_tokens,
                "first_context_tokens": context_series[0] if context_series else 0,
                "last_context_tokens": context_series[-1] if context_series else 0,
                "tool_schema_count": None,
                "limits": ["resourceSpans", "summary-only"],
            }
        )
    return summaries


def summarize_prompt_log(log: dict[str, object]) -> dict[str, object]:
    metadata_value = log.get("metadata")
    metadata = (
        cast(dict[str, object], metadata_value)
        if isinstance(metadata_value, dict)
        else {}
    )
    usage_value = metadata.get("usage")
    usage = (
        cast(dict[str, object], usage_value) if isinstance(usage_value, dict) else {}
    )
    prompt_tokens = as_int(
        usage.get("prompt_tokens") or metadata.get("maxPromptTokens")
    )
    prompt_token_details_value = usage.get("prompt_tokens_details")
    prompt_token_details = (
        cast(dict[str, object], prompt_token_details_value)
        if isinstance(prompt_token_details_value, dict)
        else {}
    )
    cached_tokens = as_int(prompt_token_details.get("cached_tokens"))
    completion_tokens = as_int(usage.get("completion_tokens"))
    copilot_usage_value = usage.get("copilot_usage")
    copilot_usage = (
        cast(dict[str, object], copilot_usage_value)
        if isinstance(copilot_usage_value, dict)
        else {}
    )
    total_nano_aiu = extract_float(copilot_usage, "total_nano_aiu") or 0.0
    response_value = log.get("response")
    response = (
        cast(dict[str, object], response_value)
        if isinstance(response_value, dict)
        else {}
    )
    response_message = response.get("message") if isinstance(response, dict) else None
    response_type = str(response.get("type") or "").lower()
    log_name = str(log.get("name") or "")
    is_tool_like = (
        "tool" in log_name.lower() or "tool" in str(log.get("kind") or "").lower()
    )
    is_error = 1 if response_type not in {"", "message", "success", "ok"} else 0
    return {
        "input_tokens": prompt_tokens,
        "output_tokens": completion_tokens,
        "cache_read_tokens": cached_tokens,
        "non_cached_input_tokens": max(prompt_tokens - cached_tokens, 0),
        "aiu_total": total_nano_aiu,
        "tool_calls": 1 if is_tool_like else 0,
        "tool_result_bytes": measure_payload_bytes(response_message)
        if is_tool_like
        else 0,
        "error_count": is_error,
        "invocation_error_count": is_error,
        "graphify_invocation_count": 1 if "graphify" in log_name.lower() else 0,
        "graphify_discovery_count": 1
        if "tool_search" in log_name.lower() or "discover" in log_name.lower()
        else 0,
        "max_context_tokens": prompt_tokens,
        "tool_schema_count": extract_int(
            metadata, "toolSchemaCount", "tool_schema_count"
        ),
    }


def summarize_prompt_export(
    prompt_export: dict[str, object],
) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    export_copilot_chat = (
        cast(dict[str, object], prompt_export.get("copilotChat"))
        if isinstance(prompt_export.get("copilotChat"), dict)
        else {}
    )
    prompts = normalize_log_records(prompt_export.get("prompts"))
    for index, prompt in enumerate(prompts, start=1):
        logs = normalize_log_records(prompt.get("logs"))
        prompt_copilot_chat = (
            cast(dict[str, object], prompt.get("copilotChat"))
            if isinstance(prompt.get("copilotChat"), dict)
            else {}
        )
        log_copilot_chat: dict[str, object] = {}
        for log in logs:
            if isinstance(log.get("copilotChat"), dict):
                log_copilot_chat = cast(dict[str, object], log.get("copilotChat"))
                break
            metadata = (
                cast(dict[str, object], log.get("metadata"))
                if isinstance(log.get("metadata"), dict)
                else {}
            )
            if isinstance(metadata.get("copilotChat"), dict):
                log_copilot_chat = cast(dict[str, object], metadata.get("copilotChat"))
                break

        copilot_session_id = (
            get_first_str(prompt_copilot_chat, "sessionId", "session_id", "id")
            or get_first_str(log_copilot_chat, "sessionId", "session_id", "id")
            or get_first_str(export_copilot_chat, "sessionId", "session_id", "id")
        )
        copilot_session_title = (
            get_first_str(prompt_copilot_chat, "sessionTitle", "session_title", "title")
            or get_first_str(log_copilot_chat, "sessionTitle", "session_title", "title")
            or get_first_str(
                export_copilot_chat, "sessionTitle", "session_title", "title"
            )
        )

        log_summaries = [summarize_prompt_log(log) for log in logs]
        context_series: list[int] = [
            as_int(summary["input_tokens"])
            for summary in log_summaries
            if summary["input_tokens"] is not None
        ]
        cache_read_total = sum(
            as_int(summary["cache_read_tokens"]) for summary in log_summaries
        )
        non_cached_total = sum(
            as_int(summary["non_cached_input_tokens"]) for summary in log_summaries
        )
        aiu_total = round(
            sum(as_float(summary["aiu_total"]) for summary in log_summaries), 6
        )
        tool_schema_counts: list[int] = [
            as_int(summary["tool_schema_count"])
            for summary in log_summaries
            if summary["tool_schema_count"] is not None
        ]
        prompt_id = (
            prompt.get("promptId") or prompt.get("prompt_id") or f"prompt-{index}"
        )
        session_id = copilot_session_id or str(prompt_id)
        title = copilot_session_title or str(
            prompt.get("title") or prompt.get("name") or session_id
        )
        summaries.append(
            {
                "session_id": session_id,
                "title": title,
                "request_count": len(log_summaries),
                "input_tokens": sum(
                    as_int(summary["input_tokens"]) for summary in log_summaries
                ),
                "output_tokens": sum(
                    as_int(summary["output_tokens"]) for summary in log_summaries
                ),
                "cache_read_tokens": cache_read_total,
                "non_cached_input_tokens": non_cached_total,
                "aiu_total": aiu_total,
                "tool_calls": sum(
                    as_int(summary["tool_calls"]) for summary in log_summaries
                ),
                "tool_result_bytes": sum(
                    as_int(summary["tool_result_bytes"]) for summary in log_summaries
                ),
                "tool_result_volume_bytes": sum(
                    as_int(summary["tool_result_bytes"]) for summary in log_summaries
                ),
                "error_count": sum(
                    as_int(summary["error_count"]) for summary in log_summaries
                ),
                "invocation_error_count": sum(
                    as_int(summary["invocation_error_count"])
                    for summary in log_summaries
                ),
                "graphify_invocation_count": sum(
                    as_int(summary["graphify_invocation_count"])
                    for summary in log_summaries
                ),
                "graphify_discovery_count": sum(
                    as_int(summary["graphify_discovery_count"])
                    for summary in log_summaries
                ),
                "max_context_tokens": max(context_series) if context_series else 0,
                "first_context_tokens": context_series[0] if context_series else 0,
                "last_context_tokens": context_series[-1] if context_series else 0,
                "tool_schema_count": sum(as_int(value) for value in tool_schema_counts)
                if tool_schema_counts
                else None,
                "limits": ["prompt-export", "summary-only"],
            }
        )
    return summaries


def summarize_legacy_sessions(data: dict[str, object]) -> list[dict[str, object]]:
    sessions = data.get("sessions")
    if not isinstance(sessions, list):
        return []
    summaries: list[dict[str, object]] = []
    for session in sessions:
        if not isinstance(session, dict):
            continue
        requests = session.get("requests")
        if not isinstance(requests, list):
            requests = []
        summary = {
            "session_id": session.get("id")
            or session.get("session_id")
            or "unknown-session",
            "title": session.get("title") or "untitled-session",
            "request_count": len(requests),
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": None,
            "non_cached_input_tokens": None,
            "aiu_total": None,
            "tool_calls": 0,
            "tool_result_bytes": 0,
            "tool_result_volume_bytes": 0,
            "error_count": 0,
            "invocation_error_count": 0,
            "graphify_invocation_count": 0,
            "graphify_discovery_count": 0,
            "max_context_tokens": 0,
            "first_context_tokens": 0,
            "last_context_tokens": 0,
            "tool_schema_count": None,
            "limits": ["cumulative-input-totals"],
        }
        for request in requests:
            if not isinstance(request, dict):
                continue
            summary["input_tokens"] += as_int(request.get("input_tokens"))
            summary["output_tokens"] += as_int(request.get("output_tokens"))
            summary["max_context_tokens"] = max(
                int(summary["max_context_tokens"]),
                as_int(
                    request.get("context_tokens") or request.get("max_context_tokens")
                ),
            )
            tool_calls = request.get("tool_calls")
            if not isinstance(tool_calls, list):
                tool_calls = []
            summary["tool_calls"] += len(tool_calls)
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                result_bytes, is_error, graphify_invocation, graphify_discovery = (
                    summarize_tool_call(tool_call)
                )
                summary["tool_result_bytes"] += result_bytes
                summary["tool_result_volume_bytes"] += result_bytes
                summary["error_count"] += is_error
                summary["invocation_error_count"] += is_error
                summary["graphify_invocation_count"] += graphify_invocation
                summary["graphify_discovery_count"] += graphify_discovery
        summaries.append(summary)
    return summaries


def summarize_input(path: Path) -> tuple[str, list[dict[str, object]], int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("resourceSpans"), list):
        return (
            "otlp",
            summarize_otlp_export(data["resourceSpans"], source_name=path.name),
            0,
        )
    if isinstance(data, dict) and isinstance(data.get("prompts"), list):
        return "prompt-export", summarize_prompt_export(data), 1
    if isinstance(data, dict) and isinstance(data.get("sessions"), list):
        return "otlp-legacy", summarize_legacy_sessions(data), 0
    return "unknown", [], 0


def summarize_tool_call(tool_call: dict[str, object]) -> tuple[int, int, int, int]:
    result_bytes = as_int(tool_call.get("result_bytes"))
    is_error = 1 if tool_call.get("error") else 0
    tool_name = str(tool_call.get("tool") or tool_call.get("name") or "")
    graphify_invocation = 1 if "graphify" in tool_name else 0
    graphify_discovery = (
        1 if "discover" in tool_name or "tool_search" in tool_name else 0
    )
    return result_bytes, is_error, graphify_invocation, graphify_discovery


def aggregate_summaries(summaries: list[dict[str, object]]) -> dict[str, object]:
    max_context_tokens = 0
    first_context_tokens = 0
    last_context_tokens = 0
    aiu_total = 0.0
    tool_schema_total: int | None = None
    for summary in summaries:
        max_context_tokens = max(
            max_context_tokens, as_int(summary.get("max_context_tokens"))
        )
        if not first_context_tokens and summary.get("first_context_tokens") is not None:
            first_context_tokens = as_int(summary.get("first_context_tokens"))
        if summary.get("last_context_tokens") is not None:
            last_context_tokens = as_int(summary.get("last_context_tokens"))
        if summary.get("aiu_total") is not None:
            aiu_total += as_float(summary.get("aiu_total"))
        if summary.get("tool_schema_count") is not None:
            tool_schema_total = (tool_schema_total or 0) + as_int(
                summary.get("tool_schema_count")
            )
    aggregate = {
        "session_count": len(summaries),
        "request_count": sum(
            as_int(summary.get("request_count")) for summary in summaries
        ),
        "input_tokens": sum(
            as_int(summary.get("input_tokens")) for summary in summaries
        ),
        "output_tokens": sum(
            as_int(summary.get("output_tokens")) for summary in summaries
        ),
        "max_context_tokens": max_context_tokens,
        "first_context_tokens": first_context_tokens,
        "last_context_tokens": last_context_tokens,
        "tool_calls": sum(as_int(summary.get("tool_calls")) for summary in summaries),
        "tool_result_bytes": sum(
            as_int(summary.get("tool_result_bytes")) for summary in summaries
        ),
        "error_count": sum(as_int(summary.get("error_count")) for summary in summaries),
        "invocation_error_count": sum(
            as_int(summary.get("invocation_error_count")) for summary in summaries
        ),
        "graphify_invocation_count": sum(
            as_int(summary.get("graphify_invocation_count")) for summary in summaries
        ),
        "graphify_discovery_count": sum(
            as_int(summary.get("graphify_discovery_count")) for summary in summaries
        ),
        "cache_read_tokens": sum(
            as_int(summary.get("cache_read_tokens"))
            for summary in summaries
            if summary.get("cache_read_tokens") is not None
        ),
        "non_cached_input_tokens": sum(
            as_int(summary.get("non_cached_input_tokens"))
            for summary in summaries
            if summary.get("non_cached_input_tokens") is not None
        ),
        "aiu_total": round(aiu_total, 6),
        "tool_schema_count": tool_schema_total,
    }
    return aggregate


def build_report(paths: list[Path]) -> dict[str, object]:
    session_summaries: list[dict[str, object]] = []
    unique_snapshots: dict[str, list[dict[str, object]]] = {}
    raw_snapshot_count = 0
    unsupported_inputs: list[str] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        kind, summaries, snapshot_like_count = summarize_input(path)
        if kind in {"otlp", "otlp-legacy"}:
            session_summaries.extend(summaries)
            continue
        if kind == "prompt-export":
            raw_snapshot_count += snapshot_like_count
            snapshot_id = stable_identity(data)
            if snapshot_id not in unique_snapshots and summaries:
                unique_snapshots[snapshot_id] = summaries
            continue
        unsupported_inputs.append(path.name)
    snapshot_summaries = [
        summary for summaries in unique_snapshots.values() for summary in summaries
    ]
    report_summaries = session_summaries + snapshot_summaries
    return {
        "sessions": report_summaries,
        "aggregate": aggregate_summaries(report_summaries),
        "snapshot_export_count": raw_snapshot_count,
        "deduped_snapshot_count": len(unique_snapshots),
        "unsupported_input_count": len(unsupported_inputs),
        "unsupported_inputs": unsupported_inputs,
        "recommendations": build_recommendations(report_summaries),
    }


def build_recommendations(
    summaries: list[dict[str, object]],
) -> list[dict[str, object]]:
    recommendations: list[dict[str, object]] = []
    for summary in summaries:
        if as_int(summary.get("tool_result_bytes")) > 1000:
            recommendations.append(
                {
                    "session_id": summary.get("session_id"),
                    "observation": "large-tool-results",
                    "confidence": "medium",
                }
            )
        if as_int(summary.get("invocation_error_count")):
            recommendations.append(
                {
                    "session_id": summary.get("session_id"),
                    "observation": "avoidable-invocation-errors",
                    "confidence": "high",
                }
            )
        if as_int(summary.get("first_context_tokens")) and as_int(
            summary.get("last_context_tokens")
        ) > as_int(summary.get("first_context_tokens")):
            recommendations.append(
                {
                    "session_id": summary.get("session_id"),
                    "observation": "context-growth",
                    "confidence": "medium",
                }
            )
        if as_int(summary.get("graphify_discovery_count")) and not as_int(
            summary.get("graphify_invocation_count")
        ):
            recommendations.append(
                {
                    "session_id": summary.get("session_id"),
                    "observation": "graphify-discovered-but-not-invoked",
                    "confidence": "medium",
                }
            )
        if summary.get("tool_schema_count") is None:
            recommendations.append(
                {
                    "session_id": summary.get("session_id"),
                    "observation": "tool-schema-unavailable",
                    "confidence": "low",
                }
            )
    return recommendations


def render_markdown(report: dict[str, object]) -> str:
    sessions = cast(
        list[dict[str, object]],
        report.get("sessions") if isinstance(report.get("sessions"), list) else [],
    )
    lines = [
        "# Debug Log Summary",
        "",
        "| Session | Requests | Input tokens | Output tokens | Cache read | Non-cached input | First ctx | Last ctx | Max ctx | Tool bytes | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in sessions:
        lines.append(
            f"| {summary['title']} | {summary['request_count']} | {summary['input_tokens']} | {summary['output_tokens']} | {summary.get('cache_read_tokens', 0)} | {summary.get('non_cached_input_tokens', 0)} | {summary.get('first_context_tokens', 0)} | {summary.get('last_context_tokens', 0)} | {summary.get('max_context_tokens', 0)} | {summary.get('tool_result_bytes', 0)} | {summary.get('error_count', 0)} |"
        )
    lines.append("")
    lines.append(
        f"Deduped snapshot exports: {report['deduped_snapshot_count']} of {report['snapshot_export_count']}."
    )
    if report.get("unsupported_input_count"):
        lines.append(f"Unsupported inputs: {report['unsupported_input_count']}.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = [Path(item) for item in args.inputs]
    report = build_report(paths)
    if args.format == "markdown":
        print(render_markdown(report), end="")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
