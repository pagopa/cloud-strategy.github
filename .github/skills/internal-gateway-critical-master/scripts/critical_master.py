"""Pure helpers for the internal-gateway-critical-master validator.

This module provides reusable building blocks for the sibling
``validate_critical_output.py`` script inside the skill bundle.
All functions in this module are pure: no I/O, no global state mutation,
no network access.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ALLOWED_OUTCOMES: frozenset[str] = frozenset(
    {
        "reformulate-plan",
        "de-escalate-to-simple",
        "execute-clear-next-step",
        "review-evidence",
        "continue-critical",
        "accept-with-risk",
    }
)

ALLOWED_CLAIM_CLASSES: frozenset[str] = frozenset(
    {"confirmed", "inference", "estimate"}
)

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Summary",
    "Findings",
    "Synthesis",
    "Outcome",
)

REQUIRED_FINDING_FIELDS: tuple[str, ...] = (
    "Impact",
    "Evidence",
    "Mitigation",
)

OPTIONAL_FINDING_FIELDS: tuple[str, ...] = ("Reframe",)

SUMMARY_MAX_WORDS = 75
SYNTHESIS_MAX_WORDS = 100
FINDING_OBJECTION_MAX_WORDS = 30
FINDING_FIELD_MAX_WORDS = 30
FINDING_REFRAME_MAX_WORDS = 25
TOTAL_MAX_WORDS = 600
MIN_FINDINGS = 1
MAX_FINDINGS = 3


@dataclass(frozen=True)
class Finding:
    """A single contract finding."""

    severity: str
    code: str
    path: str
    message: str
    suggestion: str = ""
    extras: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion,
        }
        if self.extras:
            payload["extras"] = dict(self.extras)
        return payload


def count_words(text: str) -> int:
    """Count whitespace-delimited words. Code fences contribute no words."""
    cleaned = _strip_code_fences(text)
    tokens = re.findall(r"\S+", cleaned)
    return len(tokens)


def _strip_code_fences(text: str) -> str:
    """Remove Markdown fenced code blocks so they do not count toward words."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.MULTILINE)


def parse_markdown_sections(text: str) -> dict[str, str]:
    """Parse a Markdown document into ``{section_title: body}``."""
    matches = list(_HEADING_PATTERN.finditer(text))
    sections: dict[str, str] = {}
    if not matches:
        return sections

    top_level_indices = [
        index for index, match in enumerate(matches) if len(match.group(1)) == 2
    ]
    for list_index, match_index in enumerate(top_level_indices):
        match = matches[match_index]
        title = match.group(2).strip()
        if title in sections:
            continue
        start = match.end()
        if list_index + 1 < len(top_level_indices):
            end = matches[top_level_indices[list_index + 1]].start()
        else:
            end = len(text)
        body = text[start:end]
        sections[title] = body.rstrip()
    return sections


@dataclass(frozen=True)
class ParsedFinding:
    """One finding extracted from a rendered Markdown output."""

    heading: str
    body: str
    has_impact: bool
    has_evidence: bool
    has_mitigation: bool
    has_reframe: bool
    evidence_class: str | None
    raw_lines: tuple[str, ...]


_FINDING_HEADING_PATTERN = re.compile(r"^(#{3,6})\s+(\d+)\.\s+(.*?)\s*$", re.MULTILINE)


def parse_findings(findings_body: str) -> list[ParsedFinding]:
    """Parse the ``## Findings`` section body into individual finding records."""
    matches = list(_FINDING_HEADING_PATTERN.finditer(findings_body))
    parsed: list[ParsedFinding] = []
    for index, match in enumerate(matches):
        heading = f"{match.group(2)}. {match.group(3)}"
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(findings_body)
        body = findings_body[start:end].rstrip()
        lower_body = body.lower()
        has_impact = "**impact:**" in lower_body
        has_evidence = "**evidence:**" in lower_body
        has_mitigation = "**mitigation:**" in lower_body
        has_reframe = "**reframe:**" in lower_body
        evidence_class = _extract_evidence_class(body)
        parsed.append(
            ParsedFinding(
                heading=heading,
                body=body,
                has_impact=has_impact,
                has_evidence=has_evidence,
                has_mitigation=has_mitigation,
                has_reframe=has_reframe,
                evidence_class=evidence_class,
                raw_lines=tuple(body.splitlines()),
            )
        )
    return parsed


_CLAIM_CLASS_PATTERN = re.compile(
    r"\*\*[Ee]vidence:\*\*\s*`?(confirmed|inference|estimate)`?",
    re.IGNORECASE,
)


def _extract_evidence_class(body: str) -> str | None:
    match = _CLAIM_CLASS_PATTERN.search(body)
    if not match:
        return None
    return match.group(1).lower()


_OUTCOME_PATTERN = re.compile(r"`([^`]+)`")


def extract_outcome_value(outcome_text: str) -> str | None:
    """Extract the single backtick-wrapped outcome from the Outcome section."""
    cleaned = outcome_text.strip()
    if not cleaned:
        return None
    match = _OUTCOME_PATTERN.search(cleaned)
    if not match:
        return None
    return match.group(1).strip()


def validate_outcome_value(value: str) -> bool:
    """Return True if ``value`` is an allowed outcome from SKILL.md."""
    return value in ALLOWED_OUTCOMES


def classify_claim_class(body: str) -> str | None:
    """Return the claim class extracted from an Evidence bullet, or None."""
    return _extract_evidence_class(body)


__all__ = [
    "ALLOWED_CLAIM_CLASSES",
    "ALLOWED_OUTCOMES",
    "Finding",
    "OPTIONAL_FINDING_FIELDS",
    "ParsedFinding",
    "REQUIRED_FINDING_FIELDS",
    "REQUIRED_SECTIONS",
    "SUMMARY_MAX_WORDS",
    "SYNTHESIS_MAX_WORDS",
    "TOTAL_MAX_WORDS",
    "classify_claim_class",
    "count_words",
    "extract_outcome_value",
    "parse_findings",
    "parse_markdown_sections",
    "validate_outcome_value",
]
