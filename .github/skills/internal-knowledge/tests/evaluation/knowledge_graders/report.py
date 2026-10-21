"""Schema and truth graders for the compact knowledge report."""

from __future__ import annotations

from .core import RunInput, Verdict, changed_paths, register

MARKER = "knowledge-report/v1"
MARKERS = frozenset({MARKER, "knowledge-report/v2"})
V2_FIELDS = frozenset({"removed", "transfers", "migration_state"})
FIELDS = frozenset(
    {
        "mode",
        "bucket",
        "signal",
        "router",
        "written",
        "unchanged",
        "failed",
        "omitted",
        "excluded",
        "gaps",
        "breaking_refs",
        "diagrams",
        "coverage",
    }
)
MODES = frozenset({"help", "audit", "align", "targeted", "sync", "setup"})
ROUTERS = frozenset({"written", "unchanged", "gap", "not-applicable"})
PATH_LIST_FIELDS = (
    "written",
    "unchanged",
    "failed",
    "omitted",
    "excluded",
    "breaking_refs",
    "diagrams",
    "removed",
)
REASON_FIELDS = frozenset({"omitted", "breaking_refs", "diagrams"})


def parse_report(text: str) -> dict[str, str]:
    """Parse v1 or v2 without admitting v2 extensions into the legacy schema."""
    if not isinstance(text, str):
        raise ValueError("report must be text")
    lines = text.splitlines()
    markers = [index for index, line in enumerate(lines) if line in MARKERS]
    if len(markers) != 1:
        raise ValueError("exactly one report marker is required")
    marker_index = markers[0]
    fields = (
        FIELDS | V2_FIELDS if lines[marker_index] == "knowledge-report/v2" else FIELDS
    )
    prose = lines[:marker_index]
    if not 2 <= len(prose) <= 3 or any(not line.strip() for line in prose):
        raise ValueError("report needs two to three prose lines before the marker")
    parsed: dict[str, str] = {}
    for line in lines[marker_index + 1 :]:
        if line == "":
            break
        if ": " not in line:
            raise ValueError(f"invalid report field line: {line!r}")
        key, value = line.split(": ", 1)
        if key not in fields or not value.strip():
            raise ValueError(f"unknown or empty report field: {key!r}")
        if key in parsed:
            raise ValueError(f"duplicate report field: {key}")
        parsed[key] = value
    if parsed.get("mode") not in MODES:
        raise ValueError("report mode is missing or invalid")
    if "router" in parsed and parsed["router"] not in ROUTERS:
        raise ValueError("report router value is invalid")
    if "migration_state" in parsed:
        if parsed["migration_state"] not in {"complete", "incomplete"}:
            raise ValueError("migration_state must be complete or incomplete")
        if parsed["migration_state"] == "incomplete" and "gaps" not in parsed:
            raise ValueError("incomplete migrations need an evidenced gap")
    if "transfers" in parsed:
        for item in parsed["transfers"].split("; "):
            source, separator, target = item.partition(" -> ")
            if (
                not separator
                or not source.strip()
                or not target.strip()
                or " -> " in target
            ):
                raise ValueError("transfers items need '<old path> -> <new path>'")
    for key in REASON_FIELDS & parsed.keys():
        for item in parsed[key].split("; "):
            path, separator, reason = item.partition(": ")
            if not separator or not path.strip() or not reason.strip():
                raise ValueError(f"{key} items need '<path>: <reason>'")
    return parsed


def _items(report: dict[str, str], key: str) -> set[str]:
    value = report.get(key, "")
    return {item.strip() for item in value.split(";") if item.strip()}


@register("report_schema")
def report_schema(run: RunInput, gold: dict) -> Verdict:
    try:
        parsed = parse_report(run.report)
    except ValueError as exc:
        return Verdict("report_schema", "fail", "report-schema", str(exc))
    expected_mode = gold.get("expected_mode")
    if expected_mode is not None and parsed.get("mode") != expected_mode:
        return Verdict(
            "report_schema",
            "fail",
            "wrong-mode",
            f"expected mode {expected_mode!r}, got {parsed.get('mode')!r}",
        )
    return Verdict("report_schema", "pass", None, "report matches its versioned schema")


@register("report_truthful")
def report_truthful(run: RunInput, gold: dict) -> Verdict:
    del gold
    try:
        parsed = parse_report(run.report)
    except ValueError as exc:
        return Verdict("report_truthful", "fail", "false-success-claim", str(exc))
    changed = changed_paths(run.before, run.after)
    written = _items(parsed, "written")
    removed = _items(parsed, "removed")
    unchanged = _items(parsed, "unchanged")
    failed = _items(parsed, "failed")
    v2 = "knowledge-report/v2" in run.report.splitlines()
    deleted = set(run.before) - set(run.after)
    expected_written = changed - deleted if v2 else changed
    invalid_transfers = []
    for transfer in _items(parsed, "transfers"):
        source, target = transfer.split(" -> ", 1)
        if source not in run.before or target not in run.after or source == target:
            invalid_transfers.append(transfer)
    if (
        written != expected_written
        or (v2 and removed != deleted)
        or (unchanged | failed) & changed
        or invalid_transfers
    ):
        return Verdict(
            "report_truthful",
            "fail",
            "false-success-claim",
            f"changed={sorted(changed)}; written={sorted(written)}; removed={sorted(removed)}; "
            f"unchanged={sorted(unchanged)}; failed={sorted(failed)}; invalid_transfers={invalid_transfers}",
        )
    return Verdict(
        "report_truthful",
        "pass",
        None,
        "reported writes and unchanged paths match the snapshots",
    )


@register("no_invented_paths")
def no_invented_paths(run: RunInput, gold: dict) -> Verdict:
    del gold
    try:
        parsed = parse_report(run.report)
    except ValueError as exc:
        return Verdict("no_invented_paths", "fail", "invented-path", str(exc))
    existing = run.before.keys() | run.after.keys()
    invented: set[str] = set()
    for key in PATH_LIST_FIELDS:
        for item in _items(parsed, key):
            path = item.split(":", 1)[0].strip() if key in REASON_FIELDS else item
            if path not in existing:
                invented.add(path)
    for transfer in _items(parsed, "transfers"):
        for path in transfer.split(" -> "):
            if path not in existing:
                invented.add(path)
    return Verdict(
        "no_invented_paths",
        "fail" if invented else "pass",
        "invented-path" if invented else None,
        f"reported paths absent from both snapshots: {sorted(invented)}",
    )
