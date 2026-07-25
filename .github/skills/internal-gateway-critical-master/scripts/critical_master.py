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
        "route-to-execution-owner",
        "review-evidence",
        "continue-critical-with-new-evidence",
        "accept-with-risk",
    }
)

ALLOWED_CLAIM_CLASSES: frozenset[str] = frozenset(
    {"confirmed", "inference", "estimate"}
)

ALLOWED_EVIDENCE_QUALITY: frozenset[str] = frozenset(
    {"strong", "partial", "weak"}
)

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Summary",
    "Challenge Context",
    "Findings",
    "Synthesis",
    "Outcome",
)

REQUIRED_FINDING_FIELDS: tuple[str, ...] = (
    "Impact",
    "Evidence",
    "Mitigation",
)

OPTIONAL_FINDING_FIELDS: tuple[str, ...] = ("Reframe", "Question")

SUMMARY_MAX_WORDS = 75
SYNTHESIS_MAX_WORDS = 100
FINDING_OBJECTION_MAX_WORDS = 30
FINDING_FIELD_MAX_WORDS = 30
FINDING_REFRAME_MAX_WORDS = 25
FINDING_QUESTION_MAX_WORDS = 25
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


def parse_markdown_sections(text: str) -> list[tuple[str, str]]:
    """Parse a Markdown document into an ordered list of (title, body) tuples.

    Returns all H2 sections in document order, including duplicates,
    so callers can detect duplicates and ordering violations.
    """
    matches = list(_HEADING_PATTERN.finditer(text))
    sections: list[tuple[str, str]] = []

    h2_matches = [
        (idx, match) for idx, match in enumerate(matches) if len(match.group(1)) == 2
    ]

    for list_index, (match_index, match) in enumerate(h2_matches):
        title = match.group(2).strip()
        start = match.end()
        if list_index + 1 < len(h2_matches):
            _, next_match = h2_matches[list_index + 1]
            end = next_match.start()
        else:
            end = len(text)
        body = text[start:end]
        sections.append((title, body.rstrip()))
    return sections


def sections_to_dict(sections: list[tuple[str, str]]) -> dict[str, str]:
    """Convert an ordered section list to a dict, keeping the first occurrence."""
    result: dict[str, str] = {}
    for title, body in sections:
        if title not in result:
            result[title] = body
    return result


@dataclass(frozen=True)
class ChallengeContext:
    """Parsed Challenge Context section."""

    lenses: tuple[str, ...]
    premortem_status: str | None


@dataclass(frozen=True)
class ParsedFinding:
    """One finding extracted from a rendered Markdown output."""

    heading: str
    number: int
    objection: str
    body: str
    fields: dict[str, str]
    has_impact: bool
    has_evidence: bool
    has_mitigation: bool
    has_reframe: bool
    has_question: bool
    evidence_class: str | None
    evidence_quality: str | None
    raw_claim_class_token: str | None
    raw_lines: tuple[str, ...]


_FINDING_HEADING_PATTERN = re.compile(
    r"^#{3,6}\s+(\d+)\.\s+(.*?)\s*$", re.MULTILINE
)

_BULLET_PATTERN = re.compile(
    r"^-\s+\*\*(\w[\w\s-]*?):\*\*\s*(.*?)$", re.MULTILINE
)

_EVIDENCE_VALUE_PATTERN = re.compile(
    r"^`([^`]*)`\s*;\s*quality=`([^`]*)`\s*[—-]\s*(.*)$", re.DOTALL
)

_EVIDENCE_CLASS_ONLY_PATTERN = re.compile(
    r"^`([^`]*)`", re.DOTALL
)

_CLAIM_CLASS_BACKTICK_PATTERN = re.compile(r"`([^`]+)`")


def _parse_finding_fields(body: str) -> tuple[dict[str, str], dict[str, str | None]]:
    """Parse field bullets from a finding body.

    Returns (fields, raw_tokens) where raw_tokens contains the claim-class
    token extracted from the Evidence bullet for separate validation.
    """
    fields: dict[str, str] = {}
    raw_tokens: dict[str, str | None] = {}

    for match in _BULLET_PATTERN.finditer(body):
        label = match.group(1).strip()
        value = match.group(2).strip()

        if label in fields:
            fields[label] = "__DUPLICATE__"
            continue

        fields[label] = value

        if label == "Evidence":
            evidence_match = _EVIDENCE_VALUE_PATTERN.match(value)
            if evidence_match:
                raw_tokens["evidence_class"] = evidence_match.group(1)
                raw_tokens["evidence_quality"] = evidence_match.group(2)
                raw_tokens["raw_claim_class_token"] = evidence_match.group(1)
            else:
                class_only = _EVIDENCE_CLASS_ONLY_PATTERN.match(value)
                if class_only:
                    raw_tokens["evidence_class"] = class_only.group(1)
                raw_tokens["evidence_quality"] = None

                class_token_match = _CLAIM_CLASS_BACKTICK_PATTERN.search(value)
                if class_token_match:
                    raw_tokens["raw_claim_class_token"] = class_token_match.group(1)

    return fields, raw_tokens


def parse_findings(findings_body: str) -> list[ParsedFinding]:
    """Parse the ``## Findings`` section body into individual finding records."""
    matches = list(_FINDING_HEADING_PATTERN.finditer(findings_body))
    parsed: list[ParsedFinding] = []
    for index, match in enumerate(matches):
        number = int(match.group(1))
        objection = match.group(2).strip()
        heading = f"{number}. {objection}"
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(findings_body)
        body = findings_body[start:end].rstrip()

        fields, raw_tokens = _parse_finding_fields(body)

        has_impact = "Impact" in fields and fields["Impact"] != "__DUPLICATE__"
        has_evidence = "Evidence" in fields and fields["Evidence"] != "__DUPLICATE__"
        has_mitigation = "Mitigation" in fields and fields["Mitigation"] != "__DUPLICATE__"
        has_reframe = "Reframe" in fields and fields["Reframe"] != "__DUPLICATE__"
        has_question = "Question" in fields and fields["Question"] != "__DUPLICATE__"

        evidence_class = raw_tokens.get("evidence_class")
        if evidence_class is not None:
            evidence_class = evidence_class.lower()
        evidence_quality = raw_tokens.get("evidence_quality")
        if evidence_quality is not None:
            evidence_quality = evidence_quality.lower()
        raw_claim_class_token = raw_tokens.get("raw_claim_class_token")

        parsed.append(
            ParsedFinding(
                heading=heading,
                number=number,
                objection=objection,
                body=body,
                fields=fields,
                has_impact=has_impact,
                has_evidence=has_evidence,
                has_mitigation=has_mitigation,
                has_reframe=has_reframe,
                has_question=has_question,
                evidence_class=evidence_class,
                evidence_quality=evidence_quality,
                raw_claim_class_token=raw_claim_class_token,
                raw_lines=tuple(body.splitlines()),
            )
        )
    return parsed


def parse_challenge_context(text: str) -> ChallengeContext:
    """Parse the Challenge Context section from a full document."""
    sections = parse_markdown_sections(text)
    section_dict = sections_to_dict(sections)
    body = section_dict.get("Challenge Context", "")

    lenses: list[str] = []
    premortem_status: str | None = None

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- **Lenses:**"):
            raw = stripped[len("- **Lenses:**"):].strip()
            lenses = [lens.strip() for lens in raw.split(",") if lens.strip()]
        elif stripped.startswith("- **Pre-mortem:**"):
            raw = stripped[len("- **Pre-mortem:**"):].strip()
            match = re.search(r"`([^`]*)`", raw)
            if match:
                premortem_status = match.group(1).strip()

    return ChallengeContext(
        lenses=tuple(lenses),
        premortem_status=premortem_status,
    )


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


def extract_outcome_values(outcome_text: str) -> tuple[str, ...]:
    """Extract all backtick-wrapped values from the Outcome section."""
    return tuple(match.group(1).strip() for match in _OUTCOME_PATTERN.finditer(outcome_text))


def validate_outcome_value(value: str) -> bool:
    """Return True if ``value`` is an allowed outcome from SKILL.md."""
    return value in ALLOWED_OUTCOMES


def classify_claim_class(body: str) -> str | None:
    """Return the claim class extracted from an Evidence bullet, or None."""
    match = re.search(
        r"\*\*Evidence:\*\*\s*`([^`]*)`",
        body,
    )
    if not match:
        return None
    return match.group(1).lower()


ALLOWED_LIKELIHOODS: frozenset[str] = frozenset({"high", "medium", "low"})

ALLOWED_DEFENSE_VALUES: frozenset[str] = frozenset(
    {"none", "resolves", "narrows", "accepts-risk", "unanswered"}
)


@dataclass(frozen=True)
class PremortemCause:
    """One cause in a pre-mortem analysis."""

    text: str
    claim_class: str | None
    likelihood: str | None
    mitigation: str


@dataclass(frozen=True)
class Premortem:
    """Parsed pre-mortem section."""

    failure: str
    causes: tuple[PremortemCause, ...]


@dataclass(frozen=True)
class DefenseSynthesis:
    """Parsed defense synthesis metadata."""

    classification: str | None
    strongest_objection: str
    unresolved_uncertainty: str
    strongest_defense: str = ""
    remaining_vulnerability: str = ""


_PREMORTEM_FAILURE_PATTERN = re.compile(
    r"^-\s+\*\*Failure:\*\*\s*(.*?)$", re.MULTILINE
)

_PREMORTEM_CAUSE_PATTERN = re.compile(
    r"^-\s+\*\*Cause\s+(\d+):\*\*\s*(.*?)$", re.MULTILINE
)

_CAUSE_DETAIL_PATTERN = re.compile(
    r"^(.*?)\s*\|\s*class=`([^`]*)`\s*\|\s*likelihood=`([^`]*)`\s*\|\s*mitigation=(.*)$",
    re.DOTALL,
)

_SYNTHESIS_FIELD_PATTERN = re.compile(
    r"^-\s+\*\*(.+?):\*\*\s*(.*?)$", re.MULTILINE
)


def parse_premortem(body: str) -> Premortem | None:
    """Parse a Pre-mortem section body into a Premortem record."""
    failure_match = _PREMORTEM_FAILURE_PATTERN.search(body)
    failure = failure_match.group(1).strip() if failure_match else ""

    causes: list[PremortemCause] = []
    for cause_match in _PREMORTEM_CAUSE_PATTERN.finditer(body):
        cause_text = cause_match.group(2).strip()
        detail = _CAUSE_DETAIL_PATTERN.match(cause_text)
        if detail:
            causes.append(
                PremortemCause(
                    text=detail.group(1).strip(),
                    claim_class=detail.group(2).strip().lower(),
                    likelihood=detail.group(3).strip().lower(),
                    mitigation=detail.group(4).strip(),
                )
            )
        else:
            causes.append(
                PremortemCause(
                    text=cause_text,
                    claim_class=None,
                    likelihood=None,
                    mitigation="",
                )
            )

    return Premortem(failure=failure, causes=tuple(causes))


def parse_synthesis_defense(body: str) -> DefenseSynthesis:
    """Parse the Synthesis section body to extract defense metadata."""
    fields: dict[str, str] = {}
    for match in _SYNTHESIS_FIELD_PATTERN.finditer(body):
        label = match.group(1).strip()
        value = match.group(2).strip()
        match_backtick = re.search(r"`([^`]*)`", value)
        if match_backtick:
            fields[label] = match_backtick.group(1).strip()
        else:
            fields[label] = value

    classification = fields.get("Defense")
    strongest_objection = fields.get("Strongest objection", "")
    unresolved_uncertainty = fields.get("Unresolved uncertainty", "")
    strongest_defense = fields.get("Strongest defense", "")
    remaining_vulnerability = fields.get("Remaining vulnerability", "")

    return DefenseSynthesis(
        classification=classification,
        strongest_objection=strongest_objection,
        unresolved_uncertainty=unresolved_uncertainty,
        strongest_defense=strongest_defense,
        remaining_vulnerability=remaining_vulnerability,
    )


__all__ = [
    "ALLOWED_CLAIM_CLASSES",
    "ALLOWED_DEFENSE_VALUES",
    "ALLOWED_EVIDENCE_QUALITY",
    "ALLOWED_LIKELIHOODS",
    "ALLOWED_OUTCOMES",
    "ChallengeContext",
    "DefenseSynthesis",
    "Finding",
    "FINDING_FIELD_MAX_WORDS",
    "FINDING_OBJECTION_MAX_WORDS",
    "FINDING_QUESTION_MAX_WORDS",
    "FINDING_REFRAME_MAX_WORDS",
    "MAX_FINDINGS",
    "MIN_FINDINGS",
    "OPTIONAL_FINDING_FIELDS",
    "ParsedFinding",
    "Premortem",
    "PremortemCause",
    "REQUIRED_FINDING_FIELDS",
    "REQUIRED_SECTIONS",
    "SUMMARY_MAX_WORDS",
    "SYNTHESIS_MAX_WORDS",
    "TOTAL_MAX_WORDS",
    "classify_claim_class",
    "count_words",
    "extract_outcome_value",
    "extract_outcome_values",
    "parse_challenge_context",
    "parse_findings",
    "parse_markdown_sections",
    "parse_premortem",
    "parse_synthesis_defense",
    "sections_to_dict",
    "validate_outcome_value",
]
