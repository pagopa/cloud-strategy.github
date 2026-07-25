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
    ALLOWED_DEFENSE_VALUES,
    ALLOWED_EVIDENCE_QUALITY,
    ALLOWED_LIKELIHOODS,
    ALLOWED_OUTCOMES,
    FINDING_FIELD_MAX_WORDS,
    FINDING_OBJECTION_MAX_WORDS,
    FINDING_QUESTION_MAX_WORDS,
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
    extract_outcome_values,
    parse_challenge_context,
    parse_findings,
    parse_markdown_sections,
    parse_premortem,
    parse_synthesis_defense,
    sections_to_dict,
    validate_outcome_value,
)


LATERAL_LENS_VALUES = frozenset({"analogy", "reverse-assumption"})

ALL_KNOWN_FIELD_LABELS = frozenset(
    {"Impact", "Evidence", "Mitigation", "Reframe", "Question"}
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


def validate_output(text: str, *, max_words: int = TOTAL_MAX_WORDS) -> list[Finding]:
    """Run every output-contract check and return a list of Findings."""
    findings: list[Finding] = []
    ordered_sections = parse_markdown_sections(text)
    sections = sections_to_dict(ordered_sections)

    section_titles = [title for title, _ in ordered_sections]

    _check_section_duplicates(section_titles, findings)
    _check_section_presence(sections, findings)
    _check_section_order(section_titles, findings)
    _check_empty_sections(sections, findings)

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

    _check_challenge_context(text, findings)

    premortem_body = sections.get("Pre-mortem")
    ctx = parse_challenge_context(text)
    _check_premortem_section(ctx, premortem_body, findings)
    if premortem_body is not None:
        _check_premortem_content(premortem_body, findings)

    _check_synthesis_defense(synthesis_body, findings)

    parsed_findings = parse_findings(findings_body)
    _check_finding_numbers(parsed_findings, findings)
    _check_question_count(parsed_findings, findings)

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

    _check_outcome(outcome_body, findings)

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


def _section_slug(title: str) -> str:
    return title.lower().replace(" ", "-")


def _check_section_duplicates(
    section_titles: list[str], findings: list[Finding]
) -> None:
    seen: set[str] = set()
    for title in section_titles:
        if title in seen:
            findings.append(
                Finding(
                    severity="blocking",
                    code=f"duplicate-section-{_section_slug(title)}",
                    path=f"## {title}",
                    message=f"Section '## {title}' appears more than once.",
                    suggestion="Remove the duplicate section.",
                )
            )
        seen.add(title)


def _check_section_presence(
    sections: dict[str, str], findings: list[Finding]
) -> None:
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


def _check_section_order(
    section_titles: list[str], findings: list[Finding]
) -> None:
    relevant = [t for t in section_titles if t in REQUIRED_SECTIONS or t == "Pre-mortem"]
    required_order = list(REQUIRED_SECTIONS)
    required_positions = {name: idx for idx, name in enumerate(required_order)}

    filtered = [t for t in relevant if t in required_positions]
    expected_indices = [required_positions[t] for t in filtered]
    if expected_indices != sorted(expected_indices):
        findings.append(
            Finding(
                severity="blocking",
                code="section-order",
                path="(output)",
                message="Required sections are not in canonical order.",
                suggestion=(
                    "Use the order: Summary, Challenge Context, [Pre-mortem], "
                    "Findings, Synthesis, Outcome."
                ),
            )
        )


def _check_empty_sections(
    sections: dict[str, str], findings: list[Finding]
) -> None:
    for required in REQUIRED_SECTIONS:
        body = sections.get(required, "")
        if body is not None and not body.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code=f"empty-section-{_section_slug(required)}",
                    path=f"## {required}",
                    message=f"Section '## {required}' is empty.",
                    suggestion=f"Add content to the '## {required}' section.",
                )
            )


def _check_challenge_context(text: str, findings: list[Finding]) -> None:
    ctx = parse_challenge_context(text)

    if len(ctx.lenses) != 3:
        findings.append(
            Finding(
                severity="blocking",
                code="lens-count",
                path="## Challenge Context",
                message=f"Expected exactly 3 lenses; found {len(ctx.lenses)}.",
                suggestion="Select exactly three lenses for the challenge.",
                extras={"count": len(ctx.lenses)},
            )
        )

    known_lenses = {
        "first-principles", "constraint-audit", "inversion", "counterfactual",
        "role-reversal", "time-shift", "scope-compression", "opportunity-cost",
        "analogy", "reverse-assumption",
    }
    for lens in ctx.lenses:
        if lens not in known_lenses:
            findings.append(
                Finding(
                    severity="blocking",
                    code="unknown-lens",
                    path="## Challenge Context",
                    message=f"Lens '{lens}' is not in the allowed set.",
                    suggestion=(
                        f"Use one of: {', '.join(sorted(known_lenses))}."
                    ),
                )
            )

    if len(ctx.lenses) >= 3 and ctx.lenses[2] not in LATERAL_LENS_VALUES:
        findings.append(
            Finding(
                severity="blocking",
                code="lateral-lens-required",
                path="## Challenge Context",
                message=(
                    f"Third lens '{ctx.lenses[2]}' must be one of: "
                    f"{', '.join(sorted(LATERAL_LENS_VALUES))}."
                ),
                suggestion="Set lens three to `analogy` or `reverse-assumption`.",
            )
        )

    if ctx.premortem_status is None:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-premortem-status",
                path="## Challenge Context",
                message="Challenge Context must declare Pre-mortem status.",
                suggestion="Add `- **Pre-mortem:** \\`triggered\\`` or `not-triggered`.",
            )
        )
    elif ctx.premortem_status not in ("triggered", "not-triggered"):
        findings.append(
            Finding(
                severity="blocking",
                code="invalid-premortem-status",
                path="## Challenge Context",
                message=(
                    f"Pre-mortem status '{ctx.premortem_status}' is not valid."
                ),
                suggestion="Use `triggered` or `not-triggered`.",
            )
        )


def _check_finding_numbers(
    parsed_findings: list, findings: list[Finding]
) -> None:
    if not parsed_findings:
        return
    expected = list(range(1, len(parsed_findings) + 1))
    actual = [p.number for p in parsed_findings]
    if actual != expected:
        findings.append(
            Finding(
                severity="blocking",
                code="finding-number-sequence",
                path="## Findings",
                message=(
                    f"Finding numbers {actual} are not sequential starting at 1."
                ),
                suggestion="Number findings sequentially: 1, 2, 3.",
                extras={"expected": expected, "actual": actual},
            )
        )


def _check_question_count(
    parsed_findings: list, findings: list[Finding]
) -> None:
    question_count = sum(1 for p in parsed_findings if p.has_question)
    if question_count > 1:
        findings.append(
            Finding(
                severity="blocking",
                code="multiple-root-questions",
                path="## Findings",
                message=(
                    f"Found {question_count} Question fields; at most 1 is allowed."
                ),
                suggestion="Keep at most one root question across all findings.",
                extras={"count": question_count},
            )
        )


def _check_finding(parsed, findings: list[Finding]) -> None:
    path = f"## Findings :: {parsed.heading}"

    for required in REQUIRED_FINDING_FIELDS:
        has_field = getattr(parsed, f"has_{required.lower()}", False)
        if not has_field:
            findings.append(
                Finding(
                    severity="blocking",
                    code=f"missing-finding-field-{required.lower()}",
                    path=path,
                    message=f"Finding is missing **'{required}:**' field.",
                    suggestion=(
                        f"Add a '**{required}:**' bullet under the finding heading."
                    ),
                )
            )

    for label, value in parsed.fields.items():
        if value == "__DUPLICATE__":
            continue
        if label not in ALL_KNOWN_FIELD_LABELS:
            findings.append(
                Finding(
                    severity="blocking",
                    code="invalid-finding-field-label",
                    path=path,
                    message=f"Unknown field label '{label}'.",
                    suggestion=(
                        f"Use one of: {', '.join(sorted(ALL_KNOWN_FIELD_LABELS))}."
                    ),
                )
            )

    if parsed.raw_claim_class_token is not None:
        token_lower = parsed.raw_claim_class_token.lower()
        if token_lower not in ALLOWED_CLAIM_CLASSES:
            findings.append(
                Finding(
                    severity="blocking",
                    code="invalid-claim-class",
                    path=path,
                    message=(
                        f"Claim class '{parsed.raw_claim_class_token}' is not in the allowed set."
                    ),
                    suggestion=(
                        f"Use one of: {', '.join(sorted(ALLOWED_CLAIM_CLASSES))}."
                    ),
                )
            )
    elif parsed.has_evidence:
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
                    "e.g. '**Evidence:** `inference`; quality=`partial` — ...'."
                ),
            )
        )

    if parsed.has_evidence and parsed.evidence_quality is None:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-evidence-quality",
                path=path,
                message="Evidence field must declare evidence quality.",
                suggestion=(
                    "Add quality to the Evidence bullet, "
                    "e.g. '**Evidence:** `inference`; quality=`partial` — ...'."
                ),
            )
        )
    elif parsed.evidence_quality is not None and parsed.evidence_quality not in ALLOWED_EVIDENCE_QUALITY:
        findings.append(
            Finding(
                severity="blocking",
                code="invalid-evidence-quality",
                path=path,
                message=(
                    f"Evidence quality '{parsed.evidence_quality}' is not in the allowed set."
                ),
                suggestion=(
                    f"Use one of: {', '.join(sorted(ALLOWED_EVIDENCE_QUALITY))}."
                ),
            )
        )

    objection_words = count_words(parsed.objection)
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
        value = parsed.fields.get(field_name, "")
        if value and value != "__DUPLICATE__":
            words = count_words(value)
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
        words = count_words(parsed.fields.get("Reframe", ""))
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

    if parsed.has_question:
        words = count_words(parsed.fields.get("Question", ""))
        if words > FINDING_QUESTION_MAX_WORDS:
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="finding-question-word-limit",
                    path=path,
                    message=(
                        f"Question has {words} words; limit is {FINDING_QUESTION_MAX_WORDS}."
                    ),
                    suggestion="Shorten the optional root question.",
                    extras={"words": words, "limit": FINDING_QUESTION_MAX_WORDS},
                )
            )


def _check_outcome(outcome_body: str, findings: list[Finding]) -> None:
    values = extract_outcome_values(outcome_body)

    if not values:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-outcome-value",
                path="## Outcome",
                message="Outcome section is missing a backtick-wrapped value.",
                suggestion="Wrap the outcome value in single backticks, e.g. `accept-with-risk`.",
            )
        )
        return

    if len(values) > 1:
        findings.append(
            Finding(
                severity="blocking",
                code="multiple-outcome-values",
                path="## Outcome",
                message=f"Found {len(values)} outcome values; exactly one is allowed.",
                suggestion="Keep exactly one backtick-wrapped outcome value.",
                extras={"values": list(values)},
            )
        )
        return

    outcome_value = values[0]
    if not validate_outcome_value(outcome_value):
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


def _check_premortem_section(
    ctx,
    premortem_body: str | None,
    findings: list[Finding],
) -> None:
    if ctx.premortem_status == "triggered" and premortem_body is None:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-premortem-section",
                path="(output)",
                message="Pre-mortem status is `triggered` but no Pre-mortem section exists.",
                suggestion="Add a `## Pre-mortem` section or change status to `not-triggered`.",
            )
        )
    elif ctx.premortem_status == "not-triggered" and premortem_body is not None:
        findings.append(
            Finding(
                severity="blocking",
                code="premortem-not-triggered",
                path="## Pre-mortem",
                message="Pre-mortem section exists but status is `not-triggered`.",
                suggestion="Remove the Pre-mortem section or change status to `triggered`.",
            )
        )


def _check_premortem_content(body: str, findings: list[Finding]) -> None:
    premortem = parse_premortem(body)
    if not premortem.failure:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-premortem-failure",
                path="## Pre-mortem",
                message="Pre-mortem must state one concrete failure.",
                suggestion="Add a `**Failure:**` bullet to the Pre-mortem section.",
            )
        )

    cause_count = len(premortem.causes)
    if cause_count < 2 or cause_count > 3:
        findings.append(
            Finding(
                severity="blocking",
                code="premortem-cause-count",
                path="## Pre-mortem",
                message=f"Found {cause_count} causes; expected 2-3.",
                suggestion="List 2-3 root causes for the pre-mortem failure.",
                extras={"count": cause_count},
            )
        )

    for index, cause in enumerate(premortem.causes):
        cause_path = f"## Pre-mortem :: Cause {index + 1}"

        if cause.claim_class is not None and cause.claim_class not in ALLOWED_CLAIM_CLASSES:
            findings.append(
                Finding(
                    severity="blocking",
                    code="invalid-premortem-claim-class",
                    path=cause_path,
                    message=f"Cause claim class '{cause.claim_class}' is not allowed.",
                    suggestion=(
                        f"Use one of: {', '.join(sorted(ALLOWED_CLAIM_CLASSES))}."
                    ),
                )
            )

        if cause.likelihood is not None and cause.likelihood not in ALLOWED_LIKELIHOODS:
            findings.append(
                Finding(
                    severity="blocking",
                    code="invalid-premortem-likelihood",
                    path=cause_path,
                    message=f"Cause likelihood '{cause.likelihood}' is not allowed.",
                    suggestion=(
                        f"Use one of: {', '.join(sorted(ALLOWED_LIKELIHOODS))}."
                    ),
                )
            )

        if cause.likelihood in ("high", "medium") and not cause.mitigation:
            findings.append(
                Finding(
                    severity="blocking",
                    code="missing-cause-mitigation",
                    path=cause_path,
                    message=(
                        f"Cause with likelihood `{cause.likelihood}` requires a mitigation."
                    ),
                    suggestion="Add a non-empty mitigation for this cause.",
                )
            )


def _check_synthesis_defense(body: str, findings: list[Finding]) -> None:
    if not body or not body.strip():
        return

    defense = parse_synthesis_defense(body)

    if defense.classification is None:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-defense-classification",
                path="## Synthesis",
                message="Synthesis must declare a Defense classification.",
                suggestion=(
                    "Add `- **Defense:** \\`none\\`` or one of: "
                    f"{', '.join(sorted(ALLOWED_DEFENSE_VALUES))}."
                ),
            )
        )
        return

    if defense.classification not in ALLOWED_DEFENSE_VALUES:
        findings.append(
            Finding(
                severity="blocking",
                code="invalid-defense-classification",
                path="## Synthesis",
                message=f"Defense classification '{defense.classification}' is not allowed.",
                suggestion=(
                    f"Use one of: {', '.join(sorted(ALLOWED_DEFENSE_VALUES))}."
                ),
            )
        )
        return

    if defense.classification != "none":
        if not defense.strongest_defense:
            findings.append(
                Finding(
                    severity="blocking",
                    code="missing-strongest-defense",
                    path="## Synthesis",
                    message="Defense is not `none`; `Strongest defense` is required.",
                    suggestion="Add `- **Strongest defense:**` to the synthesis.",
                )
            )
        if not defense.remaining_vulnerability:
            findings.append(
                Finding(
                    severity="blocking",
                    code="missing-remaining-vulnerability",
                    path="## Synthesis",
                    message="Defense is not `none`; `Remaining vulnerability` is required.",
                    suggestion="Add `- **Remaining vulnerability:**` to the synthesis.",
                )
            )


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
