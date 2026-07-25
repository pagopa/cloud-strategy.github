#!/usr/bin/env python3
"""Validate a critical-master output Markdown against the output contract.

Usage examples:
  python3 scripts/validate_critical_output.py --file fixtures/critical_output_valid.md
  python3 scripts/validate_critical_output.py --file fixtures/critical_output_valid.md --strict
  python3 scripts/validate_critical_output.py --file fixtures/critical_output_valid.md --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Protocol, TypeVar

from critical_master import (
    CARD_LINE_MAX_WORDS,
    CARD_MARKER_ORDER,
    CARD_MAX_LINES,
    CARD_MIN_LINES,
    CARD_TOTAL_MAX_WORDS,
    Finding,
    count_words,
    parse_critical_card,
)


class FindingLike(Protocol):
    severity: str

    def to_dict(self) -> dict[str, object]: ...


FindingT = TypeVar("FindingT", bound=FindingLike)

_H2_PATTERN = re.compile(r"^##\s+", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a critical-master output against references/output-contract.md."
    )
    parser.add_argument(
        "--file",
        help="Path to the Markdown output file. Defaults to stdin when omitted.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "compact"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=CARD_TOTAL_MAX_WORDS,
        help="Override the total output word limit.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when any non-blocking finding is reported.",
    )
    return parser.parse_args()


def run_finding_cli(
    *,
    detect_fn,
    format_name: str,
    render_text,
    compact_builder=None,
) -> list[FindingT]:
    findings = detect_fn()
    if format_name == "json":
        print(render_json([finding.to_dict() for finding in findings]))
    elif format_name == "compact":
        if compact_builder is None:
            raise ValueError("compact output requires a compact_builder")
        print(render_json(compact_builder(findings)))
    else:
        render_text(findings)
    return findings


def has_severity(findings: list[FindingLike], severity: str) -> bool:
    return any(finding.severity == severity for finding in findings)


def should_fail(
    findings: list[FindingLike],
    *,
    strict: bool = False,
    blocking_severity: str | None = "blocking",
) -> bool:
    if blocking_severity is not None and has_severity(findings, blocking_severity):
        return True
    return strict and bool(findings)


def render_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def main() -> int:
    args = parse_args()
    if args.file:
        path = Path(args.file)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"ERROR: cannot read '{path}': {exc}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()

    findings = run_finding_cli(
        detect_fn=lambda: validate_output(text, max_words=args.max_words),
        format_name=args.format,
        render_text=render_text,
        compact_builder=_compact_payload,
    )
    return 1 if should_fail(findings, strict=args.strict) else 0


def validate_output(
    text: str, *, max_words: int = CARD_TOTAL_MAX_WORDS
) -> list[Finding]:
    findings: list[Finding] = []

    if _H2_PATTERN.search(text):
        findings.append(
            Finding(
                severity="blocking",
                code="legacy-section-format",
                path="(output)",
                message="Legacy H2 sections are not allowed in the new card format.",
                suggestion="Use the emoji card layout from references/output-contract.md.",
            )
        )
        return findings

    lines = text.splitlines()
    card = parse_critical_card(text)
    non_empty_prose = [
        line for line in lines if line.strip() and line.strip() not in {
            cl.raw.strip() for cl in card.lines
        }
    ]
    if non_empty_prose:
        findings.append(
            Finding(
                severity="blocking",
                code="unexpected-content-line",
                path="(output)",
                message="Non-empty line does not match any card marker.",
                suggestion="Each content line must start with an emoji marker.",
            )
        )

    markers_present = [cl.marker for cl in card.lines]
    seen_markers: set[str] = set()
    for marker in markers_present:
        if marker in seen_markers:
            findings.append(
                Finding(
                    severity="blocking",
                    code="duplicate-marker",
                    path="(output)",
                    message=f"Marker '{marker}' appears more than once.",
                    suggestion="Each marker is allowed at most once.",
                )
            )
        seen_markers.add(marker)

    for required in ("🎯", "⚠️", "✅"):
        if required not in seen_markers:
            code_map = {"🎯": "missing-plan", "⚠️": "missing-critique", "✅": "missing-advice"}
            findings.append(
                Finding(
                    severity="blocking",
                    code=code_map[required],
                    path="(output)",
                    message=f"Required marker '{required}' is missing.",
                    suggestion="Add the missing emoji line to the card.",
                )
            )

    if "💥" in seen_markers and "✅" in seen_markers:
        risk_idx = markers_present.index("💥")
        advice_idx = markers_present.index("✅")
        if risk_idx > advice_idx:
            findings.append(
                Finding(
                    severity="blocking",
                    code="card-line-order",
                    path="(output)",
                    message="Risk marker 💥 must appear before advice ✅.",
                    suggestion="Move 💥 before ✅.",
                )
            )

    if "❓" in seen_markers and "✅" in seen_markers:
        question_idx = markers_present.index("❓")
        advice_idx = markers_present.index("✅")
        if question_idx < advice_idx:
            findings.append(
                Finding(
                    severity="blocking",
                    code="card-line-order",
                    path="(output)",
                    message="Question marker ❓ must appear after advice ✅.",
                    suggestion="Move ❓ after ✅.",
                )
            )

    expected_order = [m for m in CARD_MARKER_ORDER if m in seen_markers]
    actual_order = []
    for marker in markers_present:
        if marker not in actual_order:
            actual_order.append(marker)
    if expected_order != actual_order:
        already_reported_order = any(f.code == "card-line-order" for f in findings)
        if not already_reported_order:
            findings.append(
                Finding(
                    severity="blocking",
                    code="card-line-order",
                    path="(output)",
                    message="Card markers are not in canonical order.",
                    suggestion="Use order: 🎯, ⚠️, [💥], ✅, [❓].",
                )
            )

    line_count = len(card.lines)
    if line_count < CARD_MIN_LINES or line_count > CARD_MAX_LINES:
        findings.append(
            Finding(
                severity="blocking",
                code="card-line-count",
                path="(output)",
                message=f"Card has {line_count} lines; expected {CARD_MIN_LINES}-{CARD_MAX_LINES}.",
                suggestion="Use three to five content lines.",
                extras={"count": line_count, "min": CARD_MIN_LINES, "max": CARD_MAX_LINES},
            )
        )

    for cl in card.lines:
        if not cl.content.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="unexpected-content-line",
                    path=f"(marker {cl.marker})",
                    message="Card line has empty content after label.",
                    suggestion="Add content after the bold label.",
                )
            )
            continue
        line_words = count_words(cl.content)
        if line_words > CARD_LINE_MAX_WORDS:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="card-line-word-limit",
                    path=f"(marker {cl.marker})",
                    message=f"Line has {line_words} words; limit is {CARD_LINE_MAX_WORDS}.",
                    suggestion="Shorten the line.",
                    extras={"words": line_words, "limit": CARD_LINE_MAX_WORDS},
                )
            )

    total_words = count_words(text)
    if total_words > max_words:
        findings.append(
            Finding(
                severity="non-blocking",
                code="total-word-limit",
                path="(output)",
                message=f"Total output is {total_words} words; limit is {max_words}.",
                suggestion="Compress the card.",
                extras={"words": total_words, "limit": max_words},
            )
        )

    return findings


def _compact_payload(findings: list[Finding]) -> dict[str, object]:
    blocking = sum(1 for finding in findings if finding.severity == "blocking")
    return {
        "status": "failed" if blocking else "ok",
        "finding_counts": {
            "total": len(findings),
            "blocking": blocking,
        },
        "next_action": (
            "Resolve blocking findings before publishing the output."
            if blocking
            else "Output passes the contract; non-blocking findings are advisory."
        ),
    }


def render_text(findings: list[Finding]) -> None:
    if not findings:
        return
    for finding in findings:
        marker = "BLOCKING" if finding.severity == "blocking" else "advisory"
        print(f"[{marker}] {finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
