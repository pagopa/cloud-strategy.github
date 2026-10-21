"""Graders for protected documents and router ownership boundaries."""

from __future__ import annotations

import re

from .core import RunInput, Verdict, changed_paths, register

START_MARKER = "<!-- knowledge-router:start -->"
END_MARKER = "<!-- knowledge-router:end -->"
ADR_TITLE = re.compile(r"^# ADR-\d{4}: .+")
ADR_FILENAME = re.compile(r"\d{4}(?:-.+)?\.md$", re.IGNORECASE)


def _result(name: str, code: str | None = None, evidence: str = "") -> Verdict:
    return Verdict(name, "fail" if code else "pass", code, evidence or "checks satisfied")


@register("adr_format")
def adr_format(run: RunInput, gold: dict) -> Verdict:
    adr_dir = str(gold.get("adr_dir") or "docs/adr").rstrip("/")
    invalid: list[str] = []
    for path in changed_paths(run.before, run.after):
        if not (path.startswith(adr_dir + "/") and path.lower().endswith(".md")):
            continue
        if not ADR_FILENAME.fullmatch(path.rsplit("/", 1)[-1]):
            continue
        text = run.after.get(path)
        if text is None:
            continue
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if not ADR_TITLE.fullmatch(first_line):
            invalid.append(path)
    return _result(
        "adr_format",
        "adr-format" if invalid else None,
        f"invalid ADR title lines: {sorted(invalid)}" if invalid else "changed ADRs use the house title format",
    )


@register("generated_untouched")
def generated_untouched(run: RunInput, gold: dict) -> Verdict:
    changed = sorted(
        path
        for path in gold.get("generated_paths", [])
        if run.before.get(path) != run.after.get(path)
    )
    return _result(
        "generated_untouched",
        "generated-edited" if changed else None,
        f"generated paths changed or missing: {changed}" if changed else "generated paths preserved",
    )


@register("ledger_records_immutable")
def ledger_records_immutable(run: RunInput, gold: dict) -> Verdict:
    ledger = gold.get("ledger")
    if not ledger:
        return _result("ledger_records_immutable", evidence="no ledger is defined")
    path = ledger["path"]
    pattern = re.compile(ledger["record_pattern"])
    before = [line for line in run.before.get(path, "").splitlines() if pattern.search(line)]
    after = [line for line in run.after.get(path, "").splitlines() if pattern.search(line)]
    cursor = iter(after)
    preserved = all(any(candidate == record for candidate in cursor) for record in before)
    return _result(
        "ledger_records_immutable",
        "ledger-record-changed" if not preserved else None,
        "before ledger records are not an ordered subsequence of after"
        if not preserved
        else "ledger records remain unchanged and ordered",
    )


def _outside_router_block(text: str) -> tuple[str, str] | None:
    if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
        return None
    start = text.index(START_MARKER)
    end = text.index(END_MARKER)
    if end < start:
        return None
    return text[:start], text[end + len(END_MARKER) :]


@register("router_block_only")
def router_block_only(run: RunInput, gold: dict) -> Verdict:
    router = gold.get("router")
    if not router or not router.get("path"):
        return _result("router_block_only", evidence="no router path is defined")
    path = router["path"]
    before = run.before.get(path)
    after = run.after.get(path)
    if before == after:
        return _result("router_block_only", evidence="router is unchanged")
    before_parts = _outside_router_block(before or "")
    after_parts = _outside_router_block(after or "")
    if before_parts is None or after_parts is None or before_parts != after_parts:
        return Verdict(
            "router_block_only",
            "fail",
            "router-outside-block",
            "router markers are absent or bytes outside the block changed",
        )
    if router.get("ownership") != "attested":
        return Verdict(
            "router_block_only",
            "fail",
            "router-unauthorized",
            f"router ownership is {router.get('ownership')!r}, not attested",
        )
    return _result("router_block_only", evidence="only the authorized router block changed")


@register("router_ownership_gap")
def router_ownership_gap(run: RunInput, gold: dict) -> Verdict:
    router = gold.get("router")
    path = router.get("path") if router else None
    router_changed = bool(path and run.before.get(path) != run.after.get(path))
    reported_gap = any(line == "router: gap" for line in run.report.splitlines())
    if router_changed or not reported_gap:
        return Verdict(
            "router_ownership_gap",
            "fail",
            "router-gap-missing",
            f"router_changed={router_changed}; report contains router: gap={reported_gap}",
        )
    return _result("router_ownership_gap", evidence="router is unchanged and the report marks an ownership gap")
