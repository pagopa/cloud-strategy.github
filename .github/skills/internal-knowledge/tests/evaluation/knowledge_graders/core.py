"""Shared contracts and strict loaders for offline knowledge graders."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RUN_FIELDS = frozenset(
    {
        "profile",
        "allowlist",
        "before",
        "after",
        "steps",
        "trace",
        "trace_complete",
        "report",
        "second_after",
    }
)
TRACE_FIELDS = frozenset({"step", "tool", "kind", "path"})
PROFILES = frozenset({"audit", "author", "protected"})
TRACE_KINDS = frozenset({"read", "write", "shell", "denied"})
STATUSES = frozenset({"pass", "fail", "blocked", "not-run"})


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_strict_json(path: Path) -> dict[str, Any]:
    """Load a strict JSON object, rejecting duplicate keys at every depth."""
    try:
        value = json.loads(
            Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON top level must be an object: {path}")
    return value


def _text_map(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict) or any(
        not isinstance(key, str) or not isinstance(text, str)
        for key, text in value.items()
    ):
        raise ValueError(f"{field} must map string paths to text")
    return dict(value)


def _steps(value: Any) -> tuple[dict[str, str], ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("steps must be a list of path-to-text snapshots")
    return tuple(_text_map(step, "step") for step in value)


def _trace(value: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("trace must be a list of events")
    events: list[dict[str, Any]] = []
    for event in value:
        if not isinstance(event, dict) or set(event) != TRACE_FIELDS:
            raise ValueError("trace events need exactly step, tool, kind, and path")
        if (
            not isinstance(event["step"], int)
            or isinstance(event["step"], bool)
            or event["step"] < 0
            or not isinstance(event["tool"], str)
            or not isinstance(event["kind"], str)
            or event["kind"] not in TRACE_KINDS
            or not isinstance(event["path"], str)
        ):
            raise ValueError("trace event has an invalid field value")
        events.append(dict(event))
    return tuple(events)


@dataclass(frozen=True)
class RunInput:
    """One observed execution and its before, step, and after snapshots."""

    profile: str
    allowlist: tuple[str, ...]
    before: Mapping[str, str]
    after: Mapping[str, str]
    steps: tuple[Mapping[str, str], ...]
    trace: tuple[Mapping[str, Any], ...]
    trace_complete: bool
    report: str
    second_after: Mapping[str, str] | None


@dataclass(frozen=True)
class Verdict:
    """One grader result; only ``pass`` is green."""

    grader: str
    status: str
    code: str | None
    evidence: str

    def __post_init__(self) -> None:
        if not isinstance(self.status, str) or self.status not in STATUSES:
            raise ValueError(f"invalid verdict status: {self.status}")
        if self.status == "pass" and self.code is not None:
            raise ValueError("passing verdicts must have a null code")
        if not isinstance(self.grader, str) or not isinstance(self.evidence, str):
            raise ValueError("verdict grader and evidence must be strings")
        if self.code is not None and not isinstance(self.code, str):
            raise ValueError("verdict code must be a string or null")


def load_run_input(data: dict[str, Any]) -> RunInput:
    """Validate a run object and return its immutable top-level contract."""
    if not isinstance(data, dict) or set(data) != RUN_FIELDS:
        raise ValueError("run input has missing or unknown fields")
    profile = data["profile"]
    if not isinstance(profile, str) or profile not in PROFILES:
        raise ValueError(f"invalid run profile: {profile!r}")
    allowlist = data["allowlist"]
    if not isinstance(allowlist, (list, tuple)) or any(
        not isinstance(pattern, str) for pattern in allowlist
    ):
        raise ValueError("allowlist must be a list of glob strings")
    trace_complete = data["trace_complete"]
    if not isinstance(trace_complete, bool):
        raise ValueError("trace_complete must be boolean")
    report = data["report"]
    if not isinstance(report, str):
        raise ValueError("report must be text")
    second_after = data["second_after"]
    if second_after is not None:
        second_after = _text_map(second_after, "second_after")
    return RunInput(
        profile=profile,
        allowlist=tuple(allowlist),
        before=_text_map(data["before"], "before"),
        after=_text_map(data["after"], "after"),
        steps=_steps(data["steps"]),
        trace=_trace(data["trace"]),
        trace_complete=trace_complete,
        report=report,
        second_after=second_after,
    )


def changed_paths(before: Mapping[str, str], after: Mapping[str, str]) -> set[str]:
    """Return added, modified, and deleted paths between snapshots."""
    return {
        path
        for path in before.keys() | after.keys()
        if before.get(path) != after.get(path)
    }


Grader = Callable[[RunInput, dict[str, Any]], Verdict]
GRADERS: dict[str, Grader] = {}


def register(name: str) -> Callable[[Grader], Grader]:
    """Register a grader function under its stable pack identifier."""
    if not isinstance(name, str) or not name:
        raise ValueError("grader name must be non-empty")

    def decorate(grader: Grader) -> Grader:
        if name in GRADERS:
            raise ValueError(f"grader already registered: {name}")
        GRADERS[name] = grader
        return grader

    return decorate


def is_green(verdicts: Iterable[Verdict]) -> bool:
    """Return true only for a non-empty set of all-pass verdicts."""
    results = tuple(verdicts)
    return bool(results) and all(verdict.status == "pass" for verdict in results)
