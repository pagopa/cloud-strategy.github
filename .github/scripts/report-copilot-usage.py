#!/usr/bin/env python3
"""Purpose: Aggregate repository-owned Copilot resource usage telemetry into JSON and Markdown reports.

Usage examples:
  python3 .github/scripts/report-copilot-usage.py --input telemetry.jsonl
  python3 .github/scripts/report-copilot-usage.py --input telemetry.json --markdown-out usage-report.md
  python3 .github/scripts/report-copilot-usage.py --input telemetry.jsonl --json-out usage-report.json --near-zero-threshold 1

Input schema:
  Accepts either a JSON array or JSONL where each event object contains:
    - timestamp: ISO-8601 timestamp
    - event_type: one of invoke, load, reference
    - resource_type: one of agent, skill, prompt, instruction
    - resource_name: canonical resource identifier

  Optional fields:
    - resource_path: relative repository path for the resource
    - actor_type: usually agent
    - actor_name: canonical actor identifier such as internal-infrastructure
    - session_id: session or conversation identifier
    - metadata: free-form object for future telemetry extensions
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys


REPO_ROOT = Path(".")
SUPPORTED_EVENT_TYPES = {"invoke", "load", "reference"}
SUPPORTED_RESOURCE_TYPES = {"agent", "skill", "prompt", "instruction"}
WINDOW_DAYS = (30, 90)


class CliError(RuntimeError):
    """Raised when CLI input is invalid."""


@dataclass(frozen=True)
class UsageEvent:
    timestamp: datetime
    event_type: str
    resource_type: str
    resource_name: str
    resource_path: str | None
    actor_type: str | None
    actor_name: str | None
    session_id: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        required=True,
        help="Telemetry input file in JSON array or JSONL format. May be passed multiple times.",
    )
    parser.add_argument(
        "--json-out",
        help="Write the machine-readable report to this path. Defaults to stdout when --markdown-out is set.",
    )
    parser.add_argument(
        "--markdown-out",
        help="Write the Markdown summary to this path. Defaults to stdout when --json-out is set.",
    )
    parser.add_argument(
        "--near-zero-threshold",
        type=int,
        default=1,
        help="Maximum event count to classify an asset as near-zero usage within each window.",
    )
    return parser.parse_args()


def parse_timestamp(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise CliError(f"Timestamp must include timezone information: {value}")
    return parsed.astimezone(timezone.utc)


def parse_event(raw_event: object, source_path: Path, line_number: int) -> UsageEvent:
    if not isinstance(raw_event, dict):
        raise CliError(f"Expected object event in {source_path}:{line_number}")

    required_fields = ("timestamp", "event_type", "resource_type", "resource_name")
    missing_fields = [field for field in required_fields if field not in raw_event]
    if missing_fields:
        joined = ", ".join(missing_fields)
        raise CliError(f"Missing required field(s) {joined} in {source_path}:{line_number}")

    event_type = str(raw_event["event_type"]).strip()
    resource_type = str(raw_event["resource_type"]).strip()
    if event_type not in SUPPORTED_EVENT_TYPES:
        raise CliError(f"Unsupported event_type `{event_type}` in {source_path}:{line_number}")
    if resource_type not in SUPPORTED_RESOURCE_TYPES:
        raise CliError(f"Unsupported resource_type `{resource_type}` in {source_path}:{line_number}")

    return UsageEvent(
        timestamp=parse_timestamp(str(raw_event["timestamp"])),
        event_type=event_type,
        resource_type=resource_type,
        resource_name=str(raw_event["resource_name"]).strip(),
        resource_path=_optional_str(raw_event.get("resource_path")),
        actor_type=_optional_str(raw_event.get("actor_type")),
        actor_name=_optional_str(raw_event.get("actor_name")),
        session_id=_optional_str(raw_event.get("session_id")),
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def load_events(input_paths: list[str]) -> list[UsageEvent]:
    events: list[UsageEvent] = []

    for input_path in input_paths:
        path = Path(input_path)
        if not path.exists():
            raise CliError(f"Input file not found: {path}")

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        if path.suffix == ".json":
            payload = json.loads(content)
            if not isinstance(payload, list):
                raise CliError(f"JSON input must be an array: {path}")
            for index, raw_event in enumerate(payload, start=1):
                events.append(parse_event(raw_event, path, index))
            continue

        for line_number, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            events.append(parse_event(json.loads(line), path, line_number))

    return sorted(events, key=lambda event: event.timestamp)


def discover_inventory() -> dict[str, dict[str, str]]:
    inventory: dict[str, dict[str, str]] = {
        "agent": {},
        "skill": {},
        "prompt": {},
        "instruction": {},
    }

    for path in sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")):
        inventory["agent"][path.name[: -len(".agent.md")]] = path.as_posix()
    for path in sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md")):
        inventory["skill"][path.parent.name] = path.as_posix()
    for path in sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")):
        inventory["prompt"][path.name[: -len(".prompt.md")]] = path.as_posix()
    for path in sorted((REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")):
        inventory["instruction"][path.name[: -len(".instructions.md")]] = path.as_posix()

    return inventory


def build_report(events: list[UsageEvent], near_zero_threshold: int) -> dict[str, object]:
    inventory = discover_inventory()
    generated_at = datetime.now(timezone.utc)

    counts_by_type = Counter(event.resource_type for event in events)
    event_counts_by_type = Counter(f"{event.resource_type}:{event.event_type}" for event in events)
    total_unique_sessions = len({event.session_id for event in events if event.session_id})

    resources: dict[str, Counter[str]] = {
        resource_type: Counter() for resource_type in SUPPORTED_RESOURCE_TYPES
    }
    actor_skill_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for event in events:
        resources[event.resource_type][event.resource_name] += 1
        if event.resource_type == "skill" and event.actor_type == "agent" and event.actor_name:
            actor_skill_counts[event.actor_name][event.resource_name] += 1

    windows: dict[str, dict[str, object]] = {}
    for days in WINDOW_DAYS:
        cutoff = generated_at - timedelta(days=days)
        window_events = [event for event in events if event.timestamp >= cutoff]
        windows[str(days)] = build_window_summary(
            inventory=inventory,
            events=window_events,
            near_zero_threshold=near_zero_threshold,
        )

    return {
        "generated_at": generated_at.isoformat(),
        "input_event_count": len(events),
        "input_session_count": total_unique_sessions,
        "resource_event_counts": dict(sorted(counts_by_type.items())),
        "resource_and_event_type_counts": dict(sorted(event_counts_by_type.items())),
        "all_time_top_resources": {
            resource_type: counter_to_ranked_list(counter)
            for resource_type, counter in sorted(resources.items())
        },
        "agent_to_skill_co_usage": {
            agent_name: counter_to_ranked_list(skill_counts)
            for agent_name, skill_counts in sorted(actor_skill_counts.items())
        },
        "windows": windows,
        "inventory_counts": {
            resource_type: len(resources_by_type)
            for resource_type, resources_by_type in sorted(inventory.items())
        },
        "input_schema": {
            "required_fields": ["timestamp", "event_type", "resource_type", "resource_name"],
            "optional_fields": [
                "resource_path",
                "actor_type",
                "actor_name",
                "session_id",
                "metadata",
            ],
            "supported_event_types": sorted(SUPPORTED_EVENT_TYPES),
            "supported_resource_types": sorted(SUPPORTED_RESOURCE_TYPES),
        },
    }


def build_window_summary(
    inventory: dict[str, dict[str, str]],
    events: list[UsageEvent],
    near_zero_threshold: int,
) -> dict[str, object]:
    counts_by_resource_type: dict[str, Counter[str]] = {
        resource_type: Counter() for resource_type in SUPPORTED_RESOURCE_TYPES
    }

    for event in events:
        counts_by_resource_type[event.resource_type][event.resource_name] += 1

    top_resources = {
        resource_type: counter_to_ranked_list(counter)
        for resource_type, counter in sorted(counts_by_resource_type.items())
    }

    zero_use_assets: dict[str, list[dict[str, str]]] = {}
    near_zero_assets: dict[str, list[dict[str, object]]] = {}
    for resource_type, known_resources in sorted(inventory.items()):
        counter = counts_by_resource_type[resource_type]
        zero_use_assets[resource_type] = [
            {"name": name, "path": path}
            for name, path in sorted(known_resources.items())
            if counter.get(name, 0) == 0
        ]
        near_zero_assets[resource_type] = [
            {"name": name, "path": path, "count": counter.get(name, 0)}
            for name, path in sorted(known_resources.items())
            if 0 < counter.get(name, 0) <= near_zero_threshold
        ]

    return {
        "event_count": len(events),
        "top_resources": top_resources,
        "zero_use_assets": zero_use_assets,
        "near_zero_assets": near_zero_assets,
    }


def counter_to_ranked_list(counter: Counter[str]) -> list[dict[str, object]]:
    return [
        {"name": name, "count": count}
        for name, count in counter.most_common()
    ]


def render_markdown(report: dict[str, object], near_zero_threshold: int) -> str:
    lines: list[str] = []
    lines.append("# Copilot Usage Report")
    lines.append("")
    lines.append(f"- Generated at: `{report['generated_at']}`")
    lines.append(f"- Input events: `{report['input_event_count']}`")
    lines.append(f"- Input sessions: `{report['input_session_count']}`")
    lines.append(f"- Near-zero threshold: `<= {near_zero_threshold}`")
    lines.append("")

    lines.append("## Inventory counts")
    for resource_type, count in report["inventory_counts"].items():
        lines.append(f"- {resource_type}: `{count}`")
    lines.append("")

    lines.append("## All-time top resources")
    all_time = report["all_time_top_resources"]
    for resource_type in sorted(all_time):
        lines.append(f"### {resource_type.title()}s")
        ranked = all_time[resource_type][:10]
        if not ranked:
            lines.append("- No events observed.")
        else:
            for item in ranked:
                lines.append(f"- `{item['name']}`: `{item['count']}`")
        lines.append("")

    lines.append("## Agent to skill co-usage")
    co_usage = report["agent_to_skill_co_usage"]
    if not co_usage:
        lines.append("- No agent -> skill events observed.")
        lines.append("")
    else:
        for agent_name, ranked in co_usage.items():
            lines.append(f"### {agent_name}")
            for item in ranked[:10]:
                lines.append(f"- `{item['name']}`: `{item['count']}`")
            lines.append("")

    for window_name, window_data in report["windows"].items():
        lines.append(f"## Last {window_name} days")
        lines.append(f"- Events: `{window_data['event_count']}`")
        lines.append("")

        lines.append("### Top resources")
        for resource_type, ranked in window_data["top_resources"].items():
            lines.append(f"- {resource_type}: " + format_top_resources(ranked))
        lines.append("")

        lines.append("### Zero-use assets")
        for resource_type, items in window_data["zero_use_assets"].items():
            lines.append(f"- {resource_type}: `{len(items)}`")
        lines.append("")

        lines.append("### Near-zero assets")
        for resource_type, items in window_data["near_zero_assets"].items():
            lines.append(f"- {resource_type}: `{len(items)}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def format_top_resources(ranked: list[dict[str, object]]) -> str:
    if not ranked:
        return "No events observed."
    top_items = [f"`{item['name']}` ({item['count']})" for item in ranked[:5]]
    return ", ".join(top_items)


def write_output(path: str | None, content: str) -> None:
    if path is None:
        sys.stdout.write(content)
        return
    Path(path).write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()

    try:
        events = load_events(args.inputs)
        report = build_report(events, near_zero_threshold=args.near_zero_threshold)
    except (CliError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    json_payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown_payload = render_markdown(report, near_zero_threshold=args.near_zero_threshold)

    if args.json_out:
        write_output(args.json_out, json_payload)
    if args.markdown_out:
        write_output(args.markdown_out, markdown_payload)

    if not args.json_out and not args.markdown_out:
        sys.stdout.write(markdown_payload)
        return 0

    if args.json_out and not args.markdown_out:
        sys.stdout.write(markdown_payload)
        return 0

    if args.markdown_out and not args.json_out:
        sys.stdout.write(json_payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
