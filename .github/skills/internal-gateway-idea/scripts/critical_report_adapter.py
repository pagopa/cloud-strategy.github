#!/usr/bin/env python3
"""Adapt a readable critical report to the idea gateway's review boundary.

The critical skill is intentionally independent from this adapter. This module
belongs to the idea gateway because only that gateway knows how a review is
bound to a source, design path, and revision.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import PurePosixPath
from typing import Iterable


PACKET_SCHEMA = "internal-gateway-critical/full-analysis-v1"
ALLOWED_SOURCES = frozenset({"standard", "independent"})
ALLOWED_OUTCOMES = frozenset(
    {
        "accepted",
        "revise-design",
        "reopen-analysis",
        "needs-clarification",
        "invalid-target",
        "request-separate-review",
    }
)
FINDING_HEADER = re.compile(
    r"^###\s+(?:Evidence|Evidenza)\s+(\d+)\s*(?:[-—:]\s*(.*))?$",
    re.IGNORECASE,
)
FIELD = re.compile(r"^\s*\*\*([^*]+):\*\*\s*(.*)$")
SECTION = re.compile(r"^##\s+(.+?)\s*$")


class CriticalReportError(ValueError):
    """Raised when a consumer cannot safely adapt a critical report."""


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", without_marks).strip("-")


FIELD_ALIASES = {
    "critique": "critique",
    "critica": "critique",
    "evidence": "evidence",
    "evidenza": "evidence",
    "suggestion": "suggestion",
    "suggerimento": "suggestion",
    "recommendation": "suggestion",
    "raccomandazione": "suggestion",
    "why": "why",
    "perche": "why",
    "reason": "why",
    "motivo": "why",
    "impact": "impact",
    "impatto": "impact",
    "blocking": "blocking",
    "bloccante": "blocking",
}


def _canonical_field(label: str) -> str | None:
    return FIELD_ALIASES.get(_normalize(label))


def _clean_lines(lines: Iterable[str]) -> str:
    return " ".join(line.strip() for line in lines if line.strip()).strip()


def _parse_fields(lines: Iterable[str]) -> dict[str, str]:
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = FIELD.match(line)
        if match:
            current = _canonical_field(match.group(1))
            if current is not None:
                fields.setdefault(current, []).append(match.group(2).strip())
            continue
        if current is not None and line.strip():
            fields[current].append(line.strip())
    return {key: _clean_lines(value) for key, value in fields.items()}


def _section_body(lines: list[str], names: set[str]) -> list[str]:
    start: int | None = None
    for index, line in enumerate(lines):
        match = SECTION.match(line)
        if match and _normalize(match.group(1)) in names:
            start = index + 1
            break
    if start is None:
        return []
    end = len(lines)
    for index in range(start, len(lines)):
        if SECTION.match(lines[index]):
            end = index
            break
    return lines[start:end]


def _list_items(lines: Iterable[str]) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    item_start = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(.*)$")
    for line in lines:
        match = item_start.match(line)
        if match:
            if current:
                items.append(_clean_lines(current))
            current = [match.group(1)]
        elif current and line.strip():
            current.append(line)
    if current:
        items.append(_clean_lines(current))
    return [item for item in items if item]


def _parse_boolean(value: str | None, *, label: str) -> bool:
    if value is None or not value.strip():
        return False
    normalized = _normalize(value)
    if normalized in {"true", "yes", "si", "s", "1"}:
        return True
    if normalized in {"false", "no", "n", "0"}:
        return False
    raise CriticalReportError(f"{label} must be true or false")


def _valid_repository_path(value: object) -> bool:
    if not isinstance(value, str) or not value or value.startswith("/"):
        return False
    if "\\" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and ".." not in parts


def _validate_binding(*, source: str, target_path: str, target_revision: int) -> None:
    if source not in ALLOWED_SOURCES:
        raise CriticalReportError("source must be standard or independent")
    if not _valid_repository_path(target_path):
        raise CriticalReportError("target_path must be a repository-relative POSIX path")
    if type(target_revision) is not int or target_revision <= 0:
        raise CriticalReportError("target_revision must be a positive integer")


def _finding_blocks(lines: list[str]) -> list[tuple[int, str, list[str]]]:
    matches = [
        (index, match)
        for index, line in enumerate(lines)
        if (match := FINDING_HEADER.match(line))
    ]
    blocks: list[tuple[int, str, list[str]]] = []
    for position, (start, match) in enumerate(matches):
        end = matches[position + 1][0] if position + 1 < len(matches) else len(lines)
        for index in range(start + 1, end):
            if SECTION.match(lines[index]):
                end = index
                break
        title = (match.group(2) or f"Evidence {match.group(1)}").strip()
        blocks.append((int(match.group(1)), title, lines[start + 1 : end]))
    return blocks


def _parse_findings(lines: list[str]) -> list[dict[str, object]]:
    blocks = _finding_blocks(lines)
    numbers = [number for number, _, _ in blocks]
    if numbers != list(range(1, len(numbers) + 1)):
        raise CriticalReportError("evidence headings must be numbered consecutively")

    findings: list[dict[str, object]] = []
    for number, title, block in blocks:
        fields = _parse_fields(block)
        missing = [
            field
            for field in ("critique", "evidence", "suggestion", "why", "blocking")
            if not fields.get(field)
        ]
        if missing:
            raise CriticalReportError(
                f"Evidence {number} is missing: {', '.join(missing)}"
            )
        findings.append(
            {
                "id": f"C-{number:03d}",
                "critique": fields["critique"],
                "recommendation": fields["suggestion"],
                "reason": fields["why"],
                "blocking": _parse_boolean(
                    fields.get("blocking"), label=f"Evidence {number} blocking"
                ),
                "evidence": [fields["evidence"]],
                "_title": title,
                "_impact": fields.get("impact", ""),
            }
        )
    return findings


def _parse_outcome(report: str, *, findings: list[dict[str, object]]) -> str:
    match = re.search(
        r"^\s*\*\*(?:Outcome|Esito):\*\*\s*(.+?)\s*$",
        report,
        re.IGNORECASE | re.MULTILINE,
    )
    if match:
        normalized = _normalize(match.group(1))
        aliases = {
            "accepted": "accepted",
            "accept": "accepted",
            "approved": "accepted",
            "accettato": "accepted",
            "accetta": "accepted",
            "revise": "revise-design",
            "revise-design": "revise-design",
            "revise-design-needed": "revise-design",
            "rivedere": "revise-design",
            "reopen": "reopen-analysis",
            "reopen-analysis": "reopen-analysis",
            "riaprire": "reopen-analysis",
            "clarify": "needs-clarification",
            "needs-clarification": "needs-clarification",
            "chiarire": "needs-clarification",
            "invalid": "invalid-target",
            "invalid-target": "invalid-target",
            "request-separate-review": "request-separate-review",
        }
        if normalized in aliases:
            return aliases[normalized]
        raise CriticalReportError(f"unsupported outcome: {match.group(1).strip()}")

    blockers = any(bool(finding["blocking"]) for finding in findings)
    if blockers:
        return "reopen-analysis"
    return "revise-design" if findings else "accepted"


def _no_context_report(report: str) -> bool:
    normalized = _normalize(report)
    return (
        "no-analysable-context" in normalized
        or "no-analyzable-context" in normalized
        or "nessun-contesto-analizzabile" in normalized
    )


def _clean_findings(findings: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            key: value
            for key, value in finding.items()
            if not key.startswith("_")
        }
        for finding in findings
    ]


def adapt_critical_report(
    report: str,
    *,
    source: str,
    target_path: str,
    target_revision: int,
) -> dict[str, object]:
    """Bind a readable report to the consumer's current review context."""

    _validate_binding(
        source=source,
        target_path=target_path,
        target_revision=target_revision,
    )
    if not isinstance(report, str) or not report.strip():
        raise CriticalReportError("critical report is empty")

    if _no_context_report(report):
        raise CriticalReportError(
            "No analysable context was available for critical analysis."
        )

    lines = report.splitlines()
    findings = _parse_findings(lines)
    outcome = _parse_outcome(report, findings=findings)
    residual_risks = _list_items(
        _section_body(lines, {"residual-risks", "rischi-residui"})
    )
    diagnostics = _list_items(_section_body(lines, {"diagnostics", "diagnostica"}))
    open_questions = _list_items(
        _section_body(lines, {"open-questions", "domande-aperte"})
    )

    blockers = [finding for finding in findings if finding["blocking"]]
    if outcome == "accepted" and blockers:
        raise CriticalReportError("accepted cannot contain a blocking evidence")
    if outcome == "invalid-target":
        raise CriticalReportError("invalid-target reports cannot be ingested")
    if outcome == "revise-design" and not findings:
        raise CriticalReportError("revise-design requires at least one evidence")
    if outcome == "reopen-analysis" and not blockers:
        raise CriticalReportError("reopen-analysis requires a blocking evidence")
    if outcome == "needs-clarification" and (not blockers or not open_questions):
        raise CriticalReportError(
            "needs-clarification requires a blocking evidence and an open question"
        )
    if outcome == "request-separate-review":
        if source != "independent":
            raise CriticalReportError(
                "request-separate-review requires independent source"
            )
        if not diagnostics:
            raise CriticalReportError("request-separate-review requires diagnostics")

    if outcome == "needs-clarification":
        clarification = " ".join(open_questions)
        for finding in findings:
            if finding["blocking"] and "unresolved" not in str(finding["reason"]).casefold():
                finding["reason"] = f"{finding['reason']} Unresolved user decision: {clarification}"

    return {
        "schema": PACKET_SCHEMA,
        "source": source,
        "target_path": target_path,
        "target_revision": target_revision,
        "outcome": outcome,
        "findings": _clean_findings(findings),
        "residual_risks": residual_risks,
        "diagnostics": diagnostics,
    }


def _read_report(file_path: str | None) -> str:
    if file_path is None:
        return sys.stdin.read()
    with open(file_path, encoding="utf-8") as stream:
        return stream.read()


def _render(packet: dict[str, object], format_name: str) -> None:
    outcome = str(packet["outcome"])
    findings = packet["findings"]
    diagnostics = packet["diagnostics"]
    if format_name == "compact":
        print(
            json.dumps(
                {
                    "status": "failed" if outcome == "invalid-target" else "ok",
                    "outcome": outcome,
                    "finding_count": len(findings),  # type: ignore[arg-type]
                    "diagnostic_count": len(diagnostics),  # type: ignore[arg-type]
                },
                ensure_ascii=False,
            )
        )
        return
    if format_name == "text":
        if outcome == "invalid-target":
            for diagnostic in diagnostics:  # type: ignore[union-attr]
                print(f"[INVALID] {diagnostic}")
        else:
            print(f"[VALID] outcome={outcome} findings={len(findings)}")  # type: ignore[arg-type]
        return
    print(json.dumps(packet, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Adapt a readable critical report for the idea gateway."
    )
    parser.add_argument("--file", help="Report file; stdin is used when omitted.")
    parser.add_argument("--source", choices=sorted(ALLOWED_SOURCES), default="standard")
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--revision", required=True, type=int)
    parser.add_argument("--format", choices=("text", "json", "compact"), default="json")
    args = parser.parse_args(argv)
    try:
        packet = adapt_critical_report(
            _read_report(args.file),
            source=args.source,
            target_path=args.target_path,
            target_revision=args.revision,
        )
    except (OSError, CriticalReportError) as error:
        print(f"critical report adaptation failed: {error}", file=sys.stderr)
        return 1
    _render(packet, args.format)
    return 1 if packet["outcome"] == "invalid-target" else 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["CriticalReportError", "adapt_critical_report"]
