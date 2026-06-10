#!/usr/bin/env python3
"""Summarize Copilot debug exports without exposing prompt or response bodies by default."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


VOLATILE_KEYS = frozenset({"exported_at", "generated_at", "created_at", "file_path"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Copilot debug logs and snapshot exports.")
    parser.add_argument("inputs", nargs="+", help="JSON debug-log or snapshot-export files.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser.parse_args()


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


def summarize_tool_call(tool_call: dict[str, object]) -> tuple[int, int, int, int]:
    result_bytes = as_int(tool_call.get("result_bytes"))
    is_error = 1 if tool_call.get("error") else 0
    tool_name = str(tool_call.get("tool") or tool_call.get("name") or "")
    graphify_invocation = 1 if "graphify" in tool_name else 0
    graphify_discovery = 1 if "discover" in tool_name or "tool_search" in tool_name else 0
    return result_bytes, is_error, graphify_invocation, graphify_discovery


def summarize_otlp_session(session: dict[str, object]) -> dict[str, object]:
    requests = session.get("requests")
    if not isinstance(requests, list):
        requests = []
    summary = {
        "session_id": session.get("id") or session.get("session_id") or "unknown-session",
        "title": session.get("title") or "untitled-session",
        "request_count": len(requests),
        "input_tokens": 0,
        "output_tokens": 0,
        "max_context_tokens": 0,
        "tool_calls": 0,
        "tool_result_bytes": 0,
        "error_count": 0,
        "graphify_invocation_count": 0,
        "graphify_discovery_count": 0,
        "cache_read_tokens": None,
        "non_cached_input_tokens": None,
        "aiu_total": None,
        "limits": ["cumulative-input-totals"],
    }
    for request in requests:
        if not isinstance(request, dict):
            continue
        summary["input_tokens"] += as_int(request.get("input_tokens"))
        summary["output_tokens"] += as_int(request.get("output_tokens"))
        summary["max_context_tokens"] = max(
            int(summary["max_context_tokens"]),
            as_int(request.get("context_tokens") or request.get("max_context_tokens")),
        )
        tool_calls = request.get("tool_calls")
        if not isinstance(tool_calls, list):
            tool_calls = []
        summary["tool_calls"] += len(tool_calls)
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
            result_bytes, is_error, graphify_invocation, graphify_discovery = summarize_tool_call(tool_call)
            summary["tool_result_bytes"] += result_bytes
            summary["error_count"] += is_error
            summary["graphify_invocation_count"] += graphify_invocation
            summary["graphify_discovery_count"] += graphify_discovery
    return summary


def summarize_snapshot_export(snapshot: dict[str, object]) -> dict[str, object]:
    requests = snapshot.get("requests")
    if not isinstance(requests, list):
        requests = []
    summary = {
        "session_id": snapshot.get("session_id") or "snapshot-export",
        "title": snapshot.get("title") or "snapshot-export",
        "request_count": len(requests),
        "model": snapshot.get("model"),
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "non_cached_input_tokens": 0,
        "aiu_total": 0.0,
        "tool_calls": 0,
        "tool_result_bytes": 0,
        "error_count": 0,
        "graphify_invocation_count": 0,
        "graphify_discovery_count": 0,
        "max_context_tokens": 0,
        "limits": [],
    }
    for request in requests:
        if not isinstance(request, dict):
            continue
        summary["model"] = summary["model"] or request.get("model")
        summary["input_tokens"] += as_int(request.get("input_tokens"))
        summary["output_tokens"] += as_int(request.get("output_tokens"))
        summary["cache_read_tokens"] += as_int(
            request.get("cached_input_tokens") or request.get("cache_read_input_tokens")
        )
        summary["non_cached_input_tokens"] += as_int(
            request.get("non_cached_input_tokens")
            or (
                as_int(request.get("input_tokens"))
                - as_int(request.get("cached_input_tokens") or request.get("cache_read_input_tokens"))
            )
        )
        summary["aiu_total"] += float(request.get("aiu") or 0.0)
        summary["max_context_tokens"] = max(
            int(summary["max_context_tokens"]),
            as_int(request.get("context_tokens") or request.get("max_context_tokens")),
        )
        tool_calls = request.get("tool_calls")
        if not isinstance(tool_calls, list):
            tool_calls = []
        summary["tool_calls"] += len(tool_calls)
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
            result_bytes, is_error, graphify_invocation, graphify_discovery = summarize_tool_call(tool_call)
            summary["tool_result_bytes"] += result_bytes
            summary["error_count"] += is_error
            summary["graphify_invocation_count"] += graphify_invocation
            summary["graphify_discovery_count"] += graphify_discovery
    return summary


def summarize_input(path: Path) -> tuple[str, list[dict[str, object]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("sessions"), list):
        return "otlp", [summarize_otlp_session(session) for session in data["sessions"] if isinstance(session, dict)]
    if isinstance(data, dict) and isinstance(data.get("requests"), list):
        return "snapshot", [summarize_snapshot_export(data)]
    return "unknown", []


def aggregate_summaries(summaries: list[dict[str, object]]) -> dict[str, object]:
    aggregate = {
        "session_count": len(summaries),
        "request_count": sum(as_int(summary.get("request_count")) for summary in summaries),
        "input_tokens": sum(as_int(summary.get("input_tokens")) for summary in summaries),
        "output_tokens": sum(as_int(summary.get("output_tokens")) for summary in summaries),
        "tool_calls": sum(as_int(summary.get("tool_calls")) for summary in summaries),
        "tool_result_bytes": sum(as_int(summary.get("tool_result_bytes")) for summary in summaries),
        "error_count": sum(as_int(summary.get("error_count")) for summary in summaries),
        "graphify_invocation_count": sum(as_int(summary.get("graphify_invocation_count")) for summary in summaries),
        "graphify_discovery_count": sum(as_int(summary.get("graphify_discovery_count")) for summary in summaries),
        "cache_read_tokens": sum(as_int(summary.get("cache_read_tokens")) for summary in summaries if summary.get("cache_read_tokens") is not None),
        "non_cached_input_tokens": sum(
            as_int(summary.get("non_cached_input_tokens"))
            if summary.get("non_cached_input_tokens") is not None
            else as_int(summary.get("input_tokens"))
            for summary in summaries
        ),
        "aiu_total": round(sum(float(summary.get("aiu_total") or 0.0) for summary in summaries if summary.get("aiu_total") is not None), 6),
    }
    return aggregate


def build_report(paths: list[Path]) -> dict[str, object]:
    session_summaries: list[dict[str, object]] = []
    unique_snapshots: dict[str, dict[str, object]] = {}
    raw_snapshot_count = 0
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        kind, summaries = summarize_input(path)
        if kind == "otlp":
            session_summaries.extend(summaries)
            continue
        if kind == "snapshot":
            raw_snapshot_count += 1
            snapshot_id = stable_identity(data)
            if snapshot_id not in unique_snapshots and summaries:
                unique_snapshots[snapshot_id] = summaries[0]
    snapshot_summaries = list(unique_snapshots.values())
    report_summaries = session_summaries + snapshot_summaries
    return {
        "sessions": report_summaries,
        "aggregate": aggregate_summaries(report_summaries),
        "snapshot_export_count": raw_snapshot_count,
        "deduped_snapshot_count": len(snapshot_summaries),
        "recommendations": build_recommendations(report_summaries),
    }


def build_recommendations(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
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
        if as_int(summary.get("graphify_discovery_count")) and not as_int(summary.get("graphify_invocation_count")):
            recommendations.append(
                {
                    "session_id": summary.get("session_id"),
                    "observation": "graphify-discovered-but-not-invoked",
                    "confidence": "medium",
                }
            )
    return recommendations


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Debug Log Summary",
        "",
        "| Session | Requests | Input tokens | Output tokens | Tool calls |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for summary in report["sessions"]:
        lines.append(
            f"| {summary['title']} | {summary['request_count']} | {summary['input_tokens']} | {summary['output_tokens']} | {summary['tool_calls']} |"
        )
    lines.append("")
    lines.append(f"Deduped snapshot exports: {report['deduped_snapshot_count']} of {report['snapshot_export_count']}.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    paths = [Path(item) for item in args.inputs]
    report = build_report(paths)
    if args.format == "markdown":
        print(render_markdown(report), end="")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
