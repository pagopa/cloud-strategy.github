#!/usr/bin/env python3
"""Validate a critical-master output Markdown against the output contract.

Usage examples:
  python3 scripts/validate_critical_output.py --file fixtures/critical_output_valid.md
  python3 scripts/validate_critical_output.py --file fixtures/critical_output_invalid_missing_section.md --format json
  python3 scripts/validate_critical_output.py --file fixtures/critical_output_advisory.md --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Protocol, TypeVar

from critical_master import (
    ALLOWED_CLAIM_CLASSES,
    ALLOWED_OUTCOMES,
    FINDING_FIELD_MAX_WORDS,
    FINDING_OBJECTION_MAX_WORDS,
    FINDING_REFRAME_MAX_WORDS,
    MAX_FINDINGS,
    MIN_FINDINGS,
    REQUIRED_FINDING_FIELDS,
    REQUIRED_SECTIONS,
    SUMMARY_MAX_WORDS,
    SYNTHESIS_MAX_WORDS,
    TOTAL_MAX_WORDS,
    Finding,
    count_words,
    extract_outcome_value,
    parse_findings,
    parse_markdown_sections,
    validate_outcome_value,
)


class FindingLike(Protocol):
    severity: str

    def to_dict(self) -> dict[str, object]: ...


FindingT = TypeVar("FindingT", bound=FindingLike)


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
        default=TOTAL_MAX_WORDS,
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


def log_info(message: str) -> None:
    print(f"INFO: {message}", flush=True)


def log_warn(message: str) -> None:
    print(f"WARN: {message}", flush=True)


def main() -> int:
    args = parse_args()
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    findings = run_finding_cli(
        detect_fn=lambda: validate_output(text, max_words=args.max_words),
        format_name=args.format,
        render_text=render_text,
        compact_builder=_compact_payload,
    )
    return 1 if should_fail(findings, strict=args.strict) else 0


def validate_output(text: str, *, max_words: int = TOTAL_MAX_WORDS) -> list[Finding]:
    """Run every output-contract check and return a list of Findings."""
    findings: list[Finding] = []
    sections = parse_markdown_sections(text)

    for required in REQUIRED_SECTIONS:
        if required not in sections:
            findings.append(
                Finding(
                    severity="blocking",
                    code=f"missing-section-{_section_slug(required)}",
                    path="(output)",
                    message=f"Required section '## {required}' is missing.",
                    suggestion=(
                        f"Add a '## {required}' section. "
                        "See references/output-contract.md for the template."
                    ),
                )
            )

    summary_body = sections.get("Summary", "")
    synthesis_body = sections.get("Synthesis", "")
    findings_body = sections.get("Findings", "")
    outcome_body = sections.get("Outcome", "")

    summary_words = count_words(summary_body)
    if summary_body and summary_words > SUMMARY_MAX_WORDS:
        findings.append(
            Finding(
                severity="non-blocking",
                code="summary-word-limit",
                path="## Summary",
                message=(
                    f"Summary has {summary_words} words; limit is {SUMMARY_MAX_WORDS}."
                ),
                suggestion="Compress the summary paragraph.",
                extras={"words": summary_words, "limit": SUMMARY_MAX_WORDS},
            )
        )

    synthesis_words = count_words(synthesis_body)
    if synthesis_body and synthesis_words > SYNTHESIS_MAX_WORDS:
        findings.append(
            Finding(
                severity="non-blocking",
                code="synthesis-word-limit",
                path="## Synthesis",
                message=(
                    f"Synthesis has {synthesis_words} words; limit is {SYNTHESIS_MAX_WORDS}."
                ),
                suggestion="Compress the synthesis paragraph.",
                extras={"words": synthesis_words, "limit": SYNTHESIS_MAX_WORDS},
            )
        )

    parsed_findings = parse_findings(findings_body)
    finding_count = len(parsed_findings)
    if finding_count < MIN_FINDINGS or finding_count > MAX_FINDINGS:
        findings.append(
            Finding(
                severity="blocking",
                code="finding-count-out-of-range",
                path="## Findings",
                message=(
                    f"Found {finding_count} findings; expected {MIN_FINDINGS}-{MAX_FINDINGS}."
                ),
                suggestion=(
                    "Adjust the count to fit the contract: one strong finding is "
                    "better than three weak ones."
                ),
                extras={"count": finding_count, "min": MIN_FINDINGS, "max": MAX_FINDINGS},
            )
        )

    for parsed in parsed_findings:
        _check_finding(parsed, findings)

    outcome_value = extract_outcome_value(outcome_body)
    if outcome_value is None:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-outcome-value",
                path="## Outcome",
                message="Outcome section is missing a backtick-wrapped value.",
                suggestion="Wrap the outcome value in single backticks, e.g. `accept-with-risk`.",
            )
        )
    elif not validate_outcome_value(outcome_value):
        findings.append(
            Finding(
                severity="blocking",
                code="invalid-outcome-value",
                path="## Outcome",
                message=(
                    f"Outcome value '{outcome_value}' is not in the allowed set."
                ),
                suggestion=(
                    f"Use one of: {', '.join(sorted(ALLOWED_OUTCOMES))}."
                ),
                extras={"allowed": sorted(ALLOWED_OUTCOMES)},
            )
        )

    total_words = count_words(text)
    if total_words > max_words:
        findings.append(
            Finding(
                severity="non-blocking",
                code="total-word-limit",
                path="(output)",
                message=(
                    f"Total output is {total_words} words; limit is {max_words}."
                ),
                suggestion="Compress the deliverable or split into multiple cycles.",
                extras={"words": total_words, "limit": max_words},
            )
        )

    return findings


def _check_finding(parsed, findings: list[Finding]) -> None:
    path = f"## Findings :: {parsed.heading}"
    for required in REQUIRED_FINDING_FIELDS:
        if not getattr(parsed, f"has_{required.lower()}"):
            findings.append(
                Finding(
                    severity="blocking",
                    code=f"missing-finding-field-{required.lower()}",
                    path=path,
                    message=f"Finding is missing **'{required}:'** field.",
                    suggestion=(
                        f"Add a '**{required}:**' bullet under the finding heading."
                    ),
                )
            )
    if parsed.evidence_class is None:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-claim-class",
                path=path,
                message=(
                    "Evidence field must declare a claim class "
                    f"({', '.join(sorted(ALLOWED_CLAIM_CLASSES))})."
                ),
                suggestion=(
                    "Append the class to the Evidence bullet, "
                    "e.g. '**Evidence:** `inference` — ...'."
                ),
            )
        )
    elif parsed.evidence_class not in ALLOWED_CLAIM_CLASSES:
        findings.append(
            Finding(
                severity="blocking",
                code="invalid-claim-class",
                path=path,
                message=(
                    f"Claim class '{parsed.evidence_class}' is not in the allowed set."
                ),
                suggestion=(
                    f"Use one of: {', '.join(sorted(ALLOWED_CLAIM_CLASSES))}."
                ),
            )
        )
    objection_words = _field_word_count(parsed.body, "Objection")
    if objection_words > FINDING_OBJECTION_MAX_WORDS:
        findings.append(
            Finding(
                severity="non-blocking",
                code="finding-objection-word-limit",
                path=path,
                message=(
                    f"Objection has {objection_words} words; "
                    f"limit is {FINDING_OBJECTION_MAX_WORDS}."
                ),
                suggestion="Shorten the objection heading.",
                extras={"words": objection_words, "limit": FINDING_OBJECTION_MAX_WORDS},
            )
        )
    for field_name in ("Impact", "Evidence", "Mitigation"):
        words = _field_word_count(parsed.body, field_name)
        if words > FINDING_FIELD_MAX_WORDS:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code=f"finding-field-word-limit-{field_name.lower()}",
                    path=path,
                    message=(
                        f"'{field_name}' has {words} words; "
                        f"limit is {FINDING_FIELD_MAX_WORDS}."
                    ),
                    suggestion=f"Shorten the '{field_name}' bullet.",
                    extras={
                        "words": words,
                        "limit": FINDING_FIELD_MAX_WORDS,
                    },
                )
            )
    if parsed.has_reframe:
        words = _field_word_count(parsed.body, "Reframe")
        if words > FINDING_REFRAME_MAX_WORDS:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="finding-reframe-word-limit",
                    path=path,
                    message=(
                        f"Reframe has {words} words; limit is {FINDING_REFRAME_MAX_WORDS}."
                    ),
                    suggestion="Shorten the optional reframe.",
                    extras={"words": words, "limit": FINDING_REFRAME_MAX_WORDS},
                )
            )


def _field_word_count(body: str, field_name: str) -> int:
    pattern = re.compile(rf"\*\*{field_name}:\*\*\s*(.*?)(?=\n\s*-\s*\*\*|\Z)", re.DOTALL)
    match = pattern.search(body)
    if not match:
        return 0
    return count_words(match.group(1))


def _section_slug(title: str) -> str:
    return title.lower().replace(" ", "-")


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
        log_warn(f"[{marker}] {finding.path} :: {finding.code} :: {finding.message}")
        print(f"   Suggestion: {finding.suggestion}")


if __name__ == "__main__":
    raise SystemExit(main())
