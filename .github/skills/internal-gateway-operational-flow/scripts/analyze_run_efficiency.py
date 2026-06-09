#!/usr/bin/env python3
"""Advisory run-efficiency analyzer for Copilot prompt-export JSON.

Emits aggregate metrics and warnings only. Never emits prompt text,
tool arguments, tool results, or paths from the input export.
"""

from __future__ import annotations

import argparse
import json
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Advisory thresholds; labeled as constants, not policy gates.
WARNING_HIGH_REQUESTS_PER_USER_PROMPT = 6
WARNING_LARGE_PROMPT_GROWTH_FACTOR = 3.0
WARNING_REPEATED_CRITICAL_GROUP = 2
WARNING_CONTEXT_INPUT_TOKENS = 12_000
WARNING_LOW_OUTPUT_TOKENS = 16


def _as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    return []


def _coerce_int(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _get_nested(data: object, *path: str) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _extract_first_int(data: object, paths: tuple[tuple[str, ...], ...]) -> int:
    for path in paths:
        value = _get_nested(data, *path)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value)
    return 0


def _extract_export_timestamp(data: dict[str, object], file_index: int) -> tuple[str, int]:
    for key in (
        "exportedAt",
        "exported_at",
        "generatedAt",
        "generated_at",
        "createdAt",
        "created_at",
        "timestamp",
    ):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value, file_index
    return "", file_index


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _hash_sensitive_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def detect_input_kind(data: object) -> str:
    if not isinstance(data, dict):
        raise ValueError("Top-level export must be a JSON object.")
    if isinstance(data.get("prompts"), list):
        return "prompt_export"
    if isinstance(data.get("resourceSpans"), list):
        return "otel_debug"
    if _extract_request_list(data) is not None:
        return "generic"
    raise ValueError(
        "Unsupported top-level shape: expected prompt exports, OpenTelemetry resourceSpans, "
        "or a recognized request list wrapper."
    )


def _extract_request_list(data: dict[str, object]) -> list[dict[str, object]] | None:
    requests = data.get("requests") or data.get("messages")
    if requests is None:
        for key in ("conversation", "history", "turns", "items"):
            if key in data and isinstance(data[key], list):
                requests = data[key]
                break
    return requests if isinstance(requests, list) else None


def _normalized_request_metrics(entry: dict[str, object]) -> dict[str, object]:
    usage = entry.get("usage") or entry.get("tokenUsage") or _get_nested(entry, "metadata", "usage") or {}
    if not isinstance(usage, dict):
        usage = {}

    prompt_tokens = _extract_first_int(
        usage,
        (
            ("promptTokens",),
            ("prompt_tokens",),
            ("input_tokens",),
        ),
    )
    cached = _extract_first_int(
        usage,
        (
            ("cachedPromptTokens",),
            ("cached_input_tokens",),
            ("prompt_tokens_details", "cached_tokens"),
        ),
    )
    uncached = _extract_first_int(
        usage,
        (
            ("uncachedPromptTokens",),
            ("uncached_input_tokens",),
            ("prompt_tokens_details", "uncached_tokens"),
        ),
    )
    if uncached == 0 and prompt_tokens:
        uncached = max(prompt_tokens - cached, 0)
    completion = _extract_first_int(
        usage,
        (
            ("completionTokens",),
            ("completion_tokens",),
            ("output_tokens",),
        ),
    )
    reasoning = _extract_first_int(
        usage,
        (
            ("reasoningTokens",),
            ("reasoning_tokens",),
            ("output_tokens_details", "reasoning_tokens"),
        ),
    )
    duration = _coerce_int(
        entry.get("duration")
        or entry.get("modelDuration")
        or entry.get("durationMs")
        or entry.get("duration_ms")
        or 0
    )

    return {
        "name": str(
            entry.get("name")
            or entry.get("requestName")
            or entry.get("role")
            or "unknown"
        ),
        "input_tokens": prompt_tokens,
        "cached_input_tokens": cached,
        "uncached_input_tokens": uncached,
        "completion_tokens": completion,
        "reasoning_tokens": reasoning,
        "duration_ms": duration,
        "output_tokens": completion + reasoning,
    }


def _build_source_record(
    *,
    kind: str,
    source_index: int,
    calls: list[dict[str, object]],
    tool_events: list[dict[str, object]],
    requests_by_name: dict[str, int] | None = None,
) -> dict[str, object]:
    total_input_tokens = sum(call["input_tokens"] for call in calls)
    cached_input_tokens = sum(call["cached_input_tokens"] for call in calls)
    uncached_input_tokens = sum(call["uncached_input_tokens"] for call in calls)
    completion_tokens = sum(call["completion_tokens"] for call in calls)
    reasoning_tokens = sum(call["reasoning_tokens"] for call in calls)
    total_duration_ms = sum(call["duration_ms"] for call in calls)
    total_output_tokens = completion_tokens + reasoning_tokens
    first_input_tokens = calls[0]["input_tokens"] if calls else 0
    last_input_tokens = calls[-1]["input_tokens"] if calls else 0
    growth_factor = _ratio(last_input_tokens, first_input_tokens) if first_input_tokens else 0.0

    calls_above_context_threshold = [
        call for call in calls if call["input_tokens"] >= WARNING_CONTEXT_INPUT_TOKENS
    ]
    low_output_calls = [
        call
        for call in calls
        if (call["completion_tokens"] + call["reasoning_tokens"])
        <= WARNING_LOW_OUTPUT_TOKENS
    ]

    tool_name_counts = Counter(
        event["tool_name"] for event in tool_events if event.get("tool_name")
    )
    repeated_tool_signature_counts = Counter(
        event["signature"] for event in tool_events if event.get("signature")
    )
    repeated_identical_tool_calls = sum(
        count - 1 for count in repeated_tool_signature_counts.values() if count > 1
    )

    validation_signature_counts = Counter(
        event["validation_signature"]
        for event in tool_events
        if event.get("is_validation") and event.get("validation_signature")
    )
    repeated_validation_commands = sum(
        count - 1 for count in validation_signature_counts.values() if count > 1
    )

    tool_orders = [event["order"] for event in tool_events if isinstance(event.get("order"), int)]
    action_orders = [
        event["order"]
        for event in tool_events
        if event.get("is_action") and isinstance(event.get("order"), int)
    ]
    pre_action_tool_calls = 0
    if action_orders:
        first_action = min(action_orders)
        pre_action_tool_calls = sum(
            1
            for order in tool_orders
            if order < first_action
        )

    warnings: list[str] = []
    if calls_above_context_threshold:
        warnings.append(
            f"Context threshold exceeded in source {source_index}: "
            f"{len(calls_above_context_threshold)} call(s) above {WARNING_CONTEXT_INPUT_TOKENS:,} input tokens."
        )
    if low_output_calls:
        warnings.append(
            f"Low-output calls in source {source_index}: "
            f"{len(low_output_calls)} call(s) at or below {WARNING_LOW_OUTPUT_TOKENS} output tokens."
        )
    if repeated_identical_tool_calls:
        warnings.append(
            f"Repeated identical tool calls in source {source_index}: "
            f"{repeated_identical_tool_calls} repeated invocation(s)."
        )
    if repeated_validation_commands:
        warnings.append(
            f"Repeated validation commands in source {source_index}: "
            f"{repeated_validation_commands} repeated invocation(s)."
        )
    if pre_action_tool_calls:
        warnings.append(
            f"Pre-action tool calls in source {source_index}: "
            f"{pre_action_tool_calls} tool call(s) before patch or terminal evidence."
        )
    if calls and growth_factor >= WARNING_LARGE_PROMPT_GROWTH_FACTOR:
        warnings.append(
            f"Large prompt growth in source {source_index}: first {first_input_tokens} tokens, "
            f"last {last_input_tokens} tokens (factor {growth_factor:.1f}, "
            f"advisory threshold: {WARNING_LARGE_PROMPT_GROWTH_FACTOR}x)."
        )

    return {
        "index": source_index,
        "kind": kind,
        "calls": len(calls),
        "first_input_tokens": first_input_tokens,
        "last_input_tokens": last_input_tokens,
        "context_growth_factor": growth_factor,
        "total_input_tokens": total_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": uncached_input_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_output_tokens": total_output_tokens,
        "total_duration_ms": total_duration_ms,
        "cache_rate": _ratio(cached_input_tokens, total_input_tokens),
        "input_output_ratio": _ratio(total_input_tokens, total_output_tokens),
        "requests_by_name": dict(sorted((requests_by_name or {}).items(), key=lambda x: x[0])),
        "tool_calls_by_tool": dict(sorted(tool_name_counts.items(), key=lambda x: x[0])),
        "repeated_identical_tool_calls": repeated_identical_tool_calls,
        "repeated_validation_commands": repeated_validation_commands,
        "pre_action_tool_calls": pre_action_tool_calls,
        "calls_above_context_threshold": len(calls_above_context_threshold),
        "calls_above_context_threshold_input_tokens": sum(
            call["input_tokens"] for call in calls_above_context_threshold
        ),
        "low_output_calls": len(low_output_calls),
        "low_output_input_tokens": sum(call["input_tokens"] for call in low_output_calls),
        "warnings": warnings,
    }


def _generic_source_record(data: dict[str, object], source_index: int) -> dict[str, object]:
    requests = _extract_request_list(data)
    if requests is None:
        raise ValueError(
            "Unsupported top-level shape: expected 'requests', 'messages', or a recognized list wrapper."
        )

    calls: list[dict[str, object]] = []
    requests_by_name: dict[str, int] = defaultdict(int)
    user_prompt_requests: dict[str, int] = defaultdict(int)
    user_prompt_input_tokens: dict[str, int] = defaultdict(int)
    critical_counts: dict[str, int] = defaultdict(int)
    first_main_agent_tokens: list[int] = []

    for req in requests:
        if not isinstance(req, dict):
            continue

        metrics = _normalized_request_metrics(req)
        calls.append(metrics)
        requests_by_name[metrics["name"]] += 1

        if metrics["name"] and "critical" in str(metrics["name"]).lower():
            critical_counts[str(metrics["name"])] += 1

        user_prompt = req.get("userPrompt") or req.get("user_prompt") or req.get("prompt")
        if user_prompt:
            up_key = _hash_sensitive_text(str(user_prompt))
            user_prompt_requests[up_key] += 1
            user_prompt_input_tokens[up_key] += metrics["input_tokens"]

        if "main" in metrics["name"].lower() or "agent" in metrics["name"].lower():
            if metrics["input_tokens"]:
                first_main_agent_tokens.append(metrics["input_tokens"])

    source_record = _build_source_record(
        kind="generic",
        source_index=source_index,
        calls=calls,
        tool_events=[],
        requests_by_name=requests_by_name,
    )

    warnings = list(source_record["warnings"])
    for name, count in critical_counts.items():
        if count >= WARNING_REPEATED_CRITICAL_GROUP:
            warnings.append(
                f"Repeated critical subagent group '{name}': {count} requests "
                f"(advisory threshold: {WARNING_REPEATED_CRITICAL_GROUP})."
            )

    user_prompt_aggregates = []
    for idx, (prompt_key, count) in enumerate(
        sorted(user_prompt_requests.items(), key=lambda item: -item[1])
    ):
        user_prompt_aggregates.append(
            {
                "index": idx,
                "requests": count,
                "input_tokens": user_prompt_input_tokens.get(prompt_key, 0),
            }
        )
        if count >= WARNING_HIGH_REQUESTS_PER_USER_PROMPT:
            warnings.append(
                f"High requests per user prompt (index {idx}): {count} requests "
                f"(advisory threshold: {WARNING_HIGH_REQUESTS_PER_USER_PROMPT})."
            )

    if len(first_main_agent_tokens) >= 2:
        first = first_main_agent_tokens[0]
        last = first_main_agent_tokens[-1]
        if first > 0 and (last / first) >= WARNING_LARGE_PROMPT_GROWTH_FACTOR:
            warnings.append(
                f"Large prompt growth: first main-agent prompt {first} tokens, "
                f"last {last} tokens (factor {last/first:.1f}, "
                f"advisory threshold: {WARNING_LARGE_PROMPT_GROWTH_FACTOR}x)."
            )

    source_record["warnings"] = warnings
    return {
        "summary": {
            "total_requests": len(calls),
            "total_model_calls": len(calls),
            "requests_by_name": dict(sorted(requests_by_name.items(), key=lambda item: item[0])),
            "total_input_tokens": source_record["total_input_tokens"],
            "cached_input_tokens": source_record["cached_input_tokens"],
            "uncached_input_tokens": source_record["uncached_input_tokens"],
            "completion_tokens": source_record["completion_tokens"],
            "reasoning_tokens": source_record["reasoning_tokens"],
            "total_output_tokens": source_record["total_output_tokens"],
            "cache_rate": source_record["cache_rate"],
            "input_output_ratio": source_record["input_output_ratio"],
            "total_duration_ms": sum(call["duration_ms"] for call in calls),
            "source_count": 1,
            "calls_above_context_threshold": source_record["calls_above_context_threshold"],
            "calls_above_context_threshold_input_tokens": source_record[
                "calls_above_context_threshold_input_tokens"
            ],
            "low_output_calls": source_record["low_output_calls"],
            "low_output_input_tokens": source_record["low_output_input_tokens"],
            "tool_calls_by_tool": source_record["tool_calls_by_tool"],
            "repeated_identical_tool_calls": source_record["repeated_identical_tool_calls"],
            "repeated_validation_commands": source_record["repeated_validation_commands"],
            "pre_action_tool_calls": source_record["pre_action_tool_calls"],
        },
        "sources": [source_record],
        "user_prompt_aggregates": user_prompt_aggregates,
        "warnings": warnings,
        "advisory_note": (
            "Metrics are diagnostic/advisory only. "
            "No threshold permits skipping required evidence, gates, or validation."
        ),
    }


def _attributes_to_dict(attributes: object) -> dict[str, object]:
    if isinstance(attributes, dict):
        return attributes
    if not isinstance(attributes, list):
        return {}

    result: dict[str, object] = {}
    for item in attributes:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if not isinstance(key, str):
            continue
        value = item.get("value")
        if isinstance(value, dict):
            for candidate_key in ("stringValue", "intValue", "doubleValue", "boolValue"):
                if candidate_key in value:
                    value = value[candidate_key]
                    break
            else:
                if "value" in value:
                    value = value["value"]
        result[key] = value
    return result


def _extract_otel_session_key(attrs: dict[str, object], file_index: int, span_index: int) -> str:
    for key in (
        "gen_ai.conversation.id",
        "gen_ai.session.id",
        "session.id",
        "conversation.id",
        "conversation_id",
        "trace.session_id",
    ):
        value = attrs.get(key)
        if isinstance(value, str) and value:
            return value
    return f"file:{file_index}"


def _extract_otel_call_metrics(span: dict[str, object], attrs: dict[str, object]) -> dict[str, object]:
    name = str(
        attrs.get("gen_ai.request.model")
        or attrs.get("gen_ai.response.model")
        or attrs.get("model")
        or span.get("name")
        or "unknown"
    )
    input_tokens = _coerce_int(
        attrs.get("gen_ai.usage.input_tokens")
        or attrs.get("input_tokens")
        or attrs.get("prompt_tokens")
    )
    cached_input_tokens = _coerce_int(
        attrs.get("gen_ai.usage.input_tokens_details.cached_tokens")
        or attrs.get("cached_input_tokens")
        or attrs.get("cached_tokens")
    )
    uncached_input_tokens = _coerce_int(
        attrs.get("gen_ai.usage.input_tokens_details.uncached_tokens")
        or attrs.get("uncached_input_tokens")
        or attrs.get("uncached_tokens")
    )
    if uncached_input_tokens == 0 and input_tokens:
        uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)
    completion_tokens = _coerce_int(
        attrs.get("gen_ai.usage.output_tokens")
        or attrs.get("completion_tokens")
        or attrs.get("output_tokens")
    )
    reasoning_tokens = _coerce_int(
        attrs.get("gen_ai.usage.output_tokens_details.reasoning_tokens")
        or attrs.get("reasoning_tokens")
    )
    duration_ms = _coerce_int(
        attrs.get("duration_ms")
        or attrs.get("durationMs")
        or attrs.get("duration")
    )
    return {
        "name": name,
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": uncached_input_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "duration_ms": duration_ms,
        "output_tokens": completion_tokens + reasoning_tokens,
    }


def _extract_tool_event(span: dict[str, object], attrs: dict[str, object], order: int) -> dict[str, object] | None:
    tool_name = attrs.get("tool.name") or attrs.get("gen_ai.tool.name") or attrs.get("tool_call.name")
    if not isinstance(tool_name, str) or not tool_name:
        return None

    validation_command = attrs.get("validation.command") or attrs.get("validation_command")
    command_key = validation_command if isinstance(validation_command, str) and validation_command else ""
    if not command_key:
        command_key = str(
            attrs.get("tool.command")
            or attrs.get("command")
            or attrs.get("tool.arguments")
            or attrs.get("tool.args")
            or ""
        )
    signature_source = "|".join(
        [
            tool_name,
            str(attrs.get("tool.kind") or ""),
            str(attrs.get("tool.category") or ""),
            str(attrs.get("phase") or ""),
        ]
    )
    signature = hashlib.sha256(signature_source.encode("utf-8")).hexdigest()
    validation_signature = hashlib.sha256(command_key.encode("utf-8")).hexdigest() if command_key else ""
    is_validation = bool(
        validation_command
        or attrs.get("validation_command")
        or attrs.get("tool.category") == "validation"
        or "validate" in tool_name.lower()
    )
    is_action = str(attrs.get("action.type") or attrs.get("phase") or "").lower() in {"patch", "terminal"}
    return {
        "tool_name": tool_name,
        "signature": signature,
        "validation_signature": validation_signature,
        "is_validation": is_validation,
        "is_action": is_action,
        "order": order,
    }


def _build_prompt_source_record(prompt: dict[str, object], source_index: int) -> dict[str, object]:
    logs = prompt.get("logs")
    calls: list[dict[str, object]] = []
    for log in logs if isinstance(logs, list) else []:
        if not isinstance(log, dict):
            continue
        log_kind = log.get("kind") or log.get("type") or log.get("event") or log.get("name")
        if str(log_kind) != "ChatMLSuccess":
            continue
        request = log.get("request")
        if not isinstance(request, dict):
            request = log
        calls.append(_normalized_request_metrics(request))

    source_record = _build_source_record(
        kind="prompt_history",
        source_index=source_index,
        calls=calls,
        tool_events=[],
        requests_by_name={},
    )
    source_record["warnings"] = list(source_record["warnings"])
    return source_record


def _build_otel_source_records(data: dict[str, object], file_index: int) -> list[dict[str, object]]:
    resource_spans = data.get("resourceSpans")
    if not isinstance(resource_spans, list):
        return []

    sessions: dict[str, dict[str, object]] = {}
    session_order: dict[str, int] = {}

    for resource_index, resource_span in enumerate(resource_spans):
        if not isinstance(resource_span, dict):
            continue
        resource_attrs = _attributes_to_dict(resource_span.get("resource", {}).get("attributes") if isinstance(resource_span.get("resource"), dict) else {})
        scope_spans = resource_span.get("scopeSpans")
        if not isinstance(scope_spans, list):
            continue
        for scope_index, scope_span in enumerate(scope_spans):
            if not isinstance(scope_span, dict):
                continue
            spans = scope_span.get("spans")
            if not isinstance(spans, list):
                continue
            for span_index, span in enumerate(spans):
                if not isinstance(span, dict):
                    continue
                attrs = _attributes_to_dict(span.get("attributes"))
                combined_attrs = {**resource_attrs, **attrs}
                session_key = _extract_otel_session_key(combined_attrs, file_index, len(session_order))
                if session_key not in sessions:
                    sessions[session_key] = {
                        "calls": [],
                        "tool_events": [],
                        "requests_by_name": defaultdict(int),
                    }
                    session_order[session_key] = len(session_order)

                order = len(sessions[session_key]["calls"]) + len(sessions[session_key]["tool_events"])
                tool_event = _extract_tool_event(span, combined_attrs, order)
                if tool_event is not None:
                    sessions[session_key]["tool_events"].append(tool_event)
                if any(
                    key in combined_attrs
                    for key in (
                        "gen_ai.usage.input_tokens",
                        "input_tokens",
                        "prompt_tokens",
                        "gen_ai.usage.output_tokens",
                        "completion_tokens",
                    )
                ):
                    call = _extract_otel_call_metrics(span, combined_attrs)
                    sessions[session_key]["calls"].append(call)
                    sessions[session_key]["requests_by_name"][call["name"]] += 1

    records: list[dict[str, object]] = []
    for session_key, payload in sorted(session_order.items(), key=lambda item: item[1]):
        session = sessions[session_key]
        records.append(
            _build_source_record(
                kind="otel_session",
                source_index=payload,
                calls=session["calls"],
                tool_events=session["tool_events"],
                requests_by_name=session["requests_by_name"],
            )
        )
    return records


def _build_result_from_sources(
    source_records: list[dict[str, object]],
    *,
    user_prompt_aggregates: list[dict[str, object]] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, object]:
    summary = {
        "total_requests": sum(record["calls"] for record in source_records),
        "total_model_calls": sum(record["calls"] for record in source_records),
        "requests_by_name": {},
        "total_input_tokens": sum(record["total_input_tokens"] for record in source_records),
        "cached_input_tokens": sum(record["cached_input_tokens"] for record in source_records),
        "uncached_input_tokens": sum(record["uncached_input_tokens"] for record in source_records),
        "completion_tokens": sum(record["completion_tokens"] for record in source_records),
        "reasoning_tokens": sum(record["reasoning_tokens"] for record in source_records),
        "total_output_tokens": sum(record["total_output_tokens"] for record in source_records),
        "cache_rate": 0.0,
        "input_output_ratio": 0.0,
        "total_duration_ms": sum(record["total_duration_ms"] for record in source_records),
        "source_count": len(source_records),
        "calls_above_context_threshold": sum(
            record["calls_above_context_threshold"] for record in source_records
        ),
        "calls_above_context_threshold_input_tokens": sum(
            record["calls_above_context_threshold_input_tokens"] for record in source_records
        ),
        "low_output_calls": sum(record["low_output_calls"] for record in source_records),
        "low_output_input_tokens": sum(record["low_output_input_tokens"] for record in source_records),
        "tool_calls_by_tool": {},
        "repeated_identical_tool_calls": sum(
            record["repeated_identical_tool_calls"] for record in source_records
        ),
        "repeated_validation_commands": sum(
            record["repeated_validation_commands"] for record in source_records
        ),
        "pre_action_tool_calls": sum(record["pre_action_tool_calls"] for record in source_records),
    }
    requests_by_name: Counter[str] = Counter()
    tool_calls_by_tool: Counter[str] = Counter()
    for record in source_records:
        requests_by_name.update(record["requests_by_name"])
        tool_calls_by_tool.update(record["tool_calls_by_tool"])
    summary["requests_by_name"] = dict(sorted(requests_by_name.items(), key=lambda item: item[0]))
    summary["tool_calls_by_tool"] = dict(sorted(tool_calls_by_tool.items(), key=lambda item: item[0]))
    summary["cache_rate"] = _ratio(summary["cached_input_tokens"], summary["total_input_tokens"])
    summary["input_output_ratio"] = _ratio(summary["total_input_tokens"], summary["total_output_tokens"])

    combined_warnings = list(warnings or [])
    for record in source_records:
        combined_warnings.extend(record["warnings"])
    deduped_warnings: list[str] = []
    seen_warnings: set[str] = set()
    for warning in combined_warnings:
        if warning in seen_warnings:
            continue
        seen_warnings.add(warning)
        deduped_warnings.append(warning)

    result = {
        "summary": summary,
        "sources": source_records,
        "user_prompt_aggregates": user_prompt_aggregates or [],
        "warnings": deduped_warnings,
        "advisory_note": (
            "Metrics are diagnostic/advisory only. "
            "No threshold permits skipping required evidence, gates, or validation."
        ),
    }
    return result


def _extract_prompt_candidates(
    data: dict[str, object],
    file_index: int,
) -> list[dict[str, object]]:
    prompts = data.get("prompts")
    if not isinstance(prompts, list):
        return []

    candidates: list[dict[str, object]] = []
    timestamp_key = _extract_export_timestamp(data, file_index)
    for prompt_index, prompt in enumerate(prompts):
        if not isinstance(prompt, dict):
            continue
        prompt_id = str(prompt.get("promptId") or prompt.get("prompt_id") or prompt_index)
        log_count = _coerce_int(prompt.get("logCount") or prompt.get("log_count") or 0)
        if log_count <= 0 and isinstance(prompt.get("logs"), list):
            log_count = len(prompt.get("logs"))
        candidates.append(
            {
                "prompt_id": prompt_id,
                "log_count": log_count,
                "timestamp_key": timestamp_key,
                "file_index": file_index,
                "prompt_index": prompt_index,
                "prompt": prompt,
            }
        )
    return candidates


def _dedupe_prompt_candidates(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    best_by_prompt_id: dict[str, dict[str, object]] = {}
    for candidate in candidates:
        prompt_id = candidate["prompt_id"]
        current = best_by_prompt_id.get(prompt_id)
        candidate_key = (
            candidate["log_count"],
            candidate["timestamp_key"],
            candidate["file_index"],
            candidate["prompt_index"],
        )
        if current is None:
            best_by_prompt_id[prompt_id] = candidate
            continue
        current_key = (
            current["log_count"],
            current["timestamp_key"],
            current["file_index"],
            current["prompt_index"],
        )
        if candidate_key > current_key:
            best_by_prompt_id[prompt_id] = candidate
    return [
        best_by_prompt_id[prompt_id]
        for prompt_id in sorted(best_by_prompt_id.keys())
    ]


def analyze_generic_export(data: dict[str, object]) -> dict[str, object]:
    result = _generic_source_record(data, 0)
    source_record = result["sources"][0] if result.get("sources") else {}
    result["summary"].update(
        {
            "total_model_calls": result["summary"]["total_requests"],
            "total_output_tokens": result["summary"]["completion_tokens"]
            + result["summary"]["reasoning_tokens"],
            "cache_rate": source_record["cache_rate"],
            "input_output_ratio": source_record["input_output_ratio"],
            "source_count": 1,
            "calls_above_context_threshold": source_record["calls_above_context_threshold"],
            "calls_above_context_threshold_input_tokens": source_record[
                "calls_above_context_threshold_input_tokens"
            ],
            "low_output_calls": source_record["low_output_calls"],
            "low_output_input_tokens": source_record["low_output_input_tokens"],
            "tool_calls_by_tool": source_record["tool_calls_by_tool"],
            "repeated_identical_tool_calls": source_record["repeated_identical_tool_calls"],
            "repeated_validation_commands": source_record["repeated_validation_commands"],
            "pre_action_tool_calls": source_record["pre_action_tool_calls"],
        }
    )
    result["warnings"] = list(dict.fromkeys(result["warnings"] + source_record["warnings"]))
    return result


def analyze_prompt_export(data: dict[str, object]) -> dict[str, object]:
    prompts = data.get("prompts")
    if not isinstance(prompts, list):
        raise ValueError(
            "Unsupported top-level shape: expected prompt exports with a 'prompts' list."
        )

    source_records: list[dict[str, object]] = []
    user_prompt_aggregates: list[dict[str, object]] = []
    warnings: list[str] = []
    for source_index, prompt in enumerate(prompts):
        if not isinstance(prompt, dict):
            continue
        source_record = _build_prompt_source_record(prompt, source_index)
        source_records.append(source_record)
        warnings.extend(source_record["warnings"])
        user_prompt_aggregates.append(
            {
                "index": source_index,
                "requests": source_record["calls"],
                "input_tokens": source_record["total_input_tokens"],
            }
        )

    result = _build_result_from_sources(
        source_records,
        user_prompt_aggregates=user_prompt_aggregates,
        warnings=warnings,
    )
    result["summary"]["total_requests"] = result["summary"]["total_model_calls"]
    return result


def analyze_otel_export(data: dict[str, object]) -> dict[str, object]:
    source_records = _build_otel_source_records(data, 0)
    return _build_result_from_sources(source_records)


def analyze_exports(paths: list[Path]) -> dict[str, object]:
    generic_requests: list[dict[str, object]] = []
    prompt_candidates: list[dict[str, object]] = []
    otel_spans: list[dict[str, object]] = []

    for file_index, path in enumerate(paths):
        data = json.loads(path.read_text(encoding="utf-8"))
        kind = detect_input_kind(data)
        if kind == "generic":
            requests = _extract_request_list(data)
            if requests:
                generic_requests.extend([req for req in requests if isinstance(req, dict)])
        elif kind == "prompt_export":
            prompt_candidates.extend(_extract_prompt_candidates(data, file_index))
        elif kind == "otel_debug":
            spans = data.get("resourceSpans")
            if isinstance(spans, list):
                otel_spans.extend([span for span in spans if isinstance(span, dict)])

    results: list[dict[str, object]] = []
    if generic_requests:
        results.append(analyze_generic_export({"requests": generic_requests}))

    if prompt_candidates:
        deduped_prompts = [candidate["prompt"] for candidate in _dedupe_prompt_candidates(prompt_candidates)]
        results.append(analyze_prompt_export({"prompts": deduped_prompts}))

    if otel_spans:
        results.append(analyze_otel_export({"resourceSpans": otel_spans}))

    if not results:
        raise ValueError(
            "Unsupported top-level shape: expected prompt exports, OpenTelemetry resourceSpans, or a recognized request list wrapper."
        )

    if len(results) == 1:
        return results[0]

    merged_summary: dict[str, object] = {}
    merged_sources: list[dict[str, object]] = []
    merged_user_prompt_aggregates: list[dict[str, object]] = []
    merged_warnings: list[str] = []
    advisory_note = results[0]["advisory_note"]

    for result in results:
        summary = result["summary"]
        merged_sources.extend(result.get("sources", []))
        merged_user_prompt_aggregates.extend(result.get("user_prompt_aggregates", []))
        merged_warnings.extend(result.get("warnings", []))
        advisory_note = result.get("advisory_note", advisory_note)
        for key, value in summary.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                merged_summary[key] = merged_summary.get(key, 0) + value
            elif key == "requests_by_name":
                counter = Counter(merged_summary.get(key, {}))
                counter.update(value)
                merged_summary[key] = dict(sorted(counter.items(), key=lambda item: item[0]))
            elif key == "tool_calls_by_tool":
                counter = Counter(merged_summary.get(key, {}))
                counter.update(value)
                merged_summary[key] = dict(sorted(counter.items(), key=lambda item: item[0]))
            elif key not in merged_summary:
                merged_summary[key] = value

    merged_summary["cache_rate"] = _ratio(
        _coerce_int(merged_summary.get("cached_input_tokens")),
        _coerce_int(merged_summary.get("total_input_tokens")),
    )
    merged_summary["input_output_ratio"] = _ratio(
        _coerce_int(merged_summary.get("total_input_tokens")),
        _coerce_int(merged_summary.get("total_output_tokens")),
    )
    deduped_warnings: list[str] = []
    seen_warnings: set[str] = set()
    for warning in merged_warnings:
        if warning in seen_warnings:
            continue
        seen_warnings.add(warning)
        deduped_warnings.append(warning)

    return {
        "summary": merged_summary,
        "sources": merged_sources,
        "user_prompt_aggregates": merged_user_prompt_aggregates,
        "warnings": deduped_warnings,
        "advisory_note": advisory_note,
    }


def format_text(result: dict) -> str:
    lines: list[str] = []
    s = result["summary"]
    lines.append("Run Efficiency Analysis (Advisory)")
    lines.append("")
    lines.append("Structural input cost")
    lines.append(f"Total requests: {s['total_requests']}")
    lines.append(f"Total model calls: {s.get('total_model_calls', s['total_requests'])}")
    lines.append("Requests by name:")
    for name, count in sorted(s["requests_by_name"].items(), key=lambda x: -x[1]):
        lines.append(f"  {name}: {count}")
    lines.append(f"Total input tokens: {s['total_input_tokens']:,}")
    lines.append(f"  Cached input: {s['cached_input_tokens']:,}")
    lines.append(f"  Uncached input: {s['uncached_input_tokens']:,}")
    lines.append(f"Completion tokens: {s['completion_tokens']:,}")
    lines.append(f"Reasoning tokens: {s['reasoning_tokens']:,}")
    lines.append(f"Total output tokens: {s.get('total_output_tokens', 0):,}")
    lines.append(f"Cache rate: {s.get('cache_rate', 0.0):.2%}")
    lines.append(f"Input/output ratio: {s.get('input_output_ratio', 0.0):.2f}")
    lines.append(f"Total duration (ms): {s['total_duration_ms']:,}")
    lines.append(f"Calls above context threshold: {s.get('calls_above_context_threshold', 0)}")
    lines.append(
        f"Low-output calls: {s.get('low_output_calls', 0)} "
        f"({s.get('low_output_input_tokens', 0):,} input tokens)"
    )
    lines.append(f"Source count: {s.get('source_count', len(result.get('sources', [])))}")
    for source in result.get("sources", []):
        if not isinstance(source, dict):
            continue
        lines.append(
            f"  Source {source.get('index', '?')} [{source.get('kind', 'unknown')}]: "
            f"first {source.get('first_input_tokens', 0)}, "
            f"last {source.get('last_input_tokens', 0)}, "
            f"growth {source.get('context_growth_factor', 0.0):.2f}"
        )
    lines.append("")
    lines.append("Repository-controllable loop signals")
    lines.append("Tool calls by tool:")
    for tool_name, count in sorted(s.get("tool_calls_by_tool", {}).items(), key=lambda x: -x[1]):
        lines.append(f"  {tool_name}: {count}")
    lines.append(
        f"Repeated identical tool calls: {s.get('repeated_identical_tool_calls', 0)}"
    )
    lines.append(
        f"Repeated validation commands: {s.get('repeated_validation_commands', 0)}"
    )
    lines.append(f"Pre-action tool calls: {s.get('pre_action_tool_calls', 0)}")
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
        description="Advisory run-efficiency analyzer for Copilot prompt-export and OpenTelemetry JSON."
    )
    parser.add_argument(
        "export_paths",
        nargs="+",
        type=Path,
        help="One or more Copilot prompt-export or OpenTelemetry JSON files.",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format."
    )
    args = parser.parse_args(argv)

    try:
        missing_paths = [path for path in args.export_paths if not path.exists()]
        if missing_paths:
            print(f"Error: file not found: {missing_paths[0]}", file=sys.stderr)
            return 1
        result = analyze_exports(args.export_paths)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON: {exc}", file=sys.stderr)
        return 1
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
