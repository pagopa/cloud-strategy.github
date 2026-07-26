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

REQUIRED_CARD_MARKERS = ("🎯", "⚠️", "✅")
OPTIONAL_CARD_MARKERS = ("💥", "❓")
CARD_MARKER_ORDER = ("🎯", "⚠️", "💥", "✅", "❓")
CARD_MIN_LINES = 3
CARD_MAX_LINES = 5
CARD_TOTAL_MAX_WORDS = 100
CARD_LINE_MAX_WORDS = 30


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


_CARD_LINE_PATTERN = re.compile(
    r"^(🎯|⚠️|💥|✅|❓)\s+\*\*([^*]+):\*\*\s+(.+?)\s*$"
)


@dataclass(frozen=True)
class CardLine:
    marker: str
    label: str
    content: str
    raw: str


@dataclass(frozen=True)
class CriticalCard:
    lines: tuple[CardLine, ...]

    @property
    def by_marker(self) -> dict[str, CardLine]:
        return {line.marker: line for line in self.lines}


def parse_critical_card(text: str) -> CriticalCard:
    lines: list[CardLine] = []
    for raw_line in text.splitlines():
        match = _CARD_LINE_PATTERN.match(raw_line.strip())
        if match:
            lines.append(
                CardLine(
                    marker=match.group(1),
                    label=match.group(2).strip(),
                    content=match.group(3).strip(),
                    raw=raw_line,
                )
            )
    return CriticalCard(lines=tuple(lines))


def validate_outcome_value(value: str) -> bool:
    """Return True if ``value`` is an allowed outcome from SKILL.md."""
    return value in ALLOWED_OUTCOMES


__all__ = [
    "ALLOWED_OUTCOMES",
    "CARD_LINE_MAX_WORDS",
    "CARD_MARKER_ORDER",
    "CARD_MAX_LINES",
    "CARD_MIN_LINES",
    "CARD_TOTAL_MAX_WORDS",
    "CardLine",
    "CriticalCard",
    "Finding",
    "OPTIONAL_CARD_MARKERS",
    "REQUIRED_CARD_MARKERS",
    "count_words",
    "parse_critical_card",
    "validate_outcome_value",
]
