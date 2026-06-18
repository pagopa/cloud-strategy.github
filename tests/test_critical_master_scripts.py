from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import validate_critical_output
from lib.critical_master import (
    ALLOWED_CLAIM_CLASSES,
    ALLOWED_OUTCOMES,
    classify_claim_class,
    count_words,
    extract_outcome_value,
    parse_findings,
    parse_markdown_sections,
    validate_outcome_value,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOOD_FIXTURE = FIXTURES_DIR / "critical_output_good.md"
BAD_FIXTURE = FIXTURES_DIR / "critical_output_bad.md"


def test_count_words_excludes_code_fences() -> None:
    body = "alpha beta\n```\nignore this code block\n```\ngamma delta"
    assert count_words(body) == 4


def test_count_words_handles_empty_string() -> None:
    assert count_words("") == 0


def test_parse_markdown_sections_returns_only_h2_headings() -> None:
    text = (
        "## Summary\nbody 1\n## Findings\n### 1. x\nbody 2\n## Outcome\nbody 3"
    )
    sections = parse_markdown_sections(text)
    assert list(sections.keys()) == ["Summary", "Findings", "Outcome"]
    assert "### 1. x" in sections["Findings"]


def test_validate_outcome_value_accepts_only_allowed_set() -> None:
    for value in ALLOWED_OUTCOMES:
        assert validate_outcome_value(value) is True
    assert validate_outcome_value("defer-forever") is False
    assert validate_outcome_value("ACCEPT-WITH-RISK") is False


def test_extract_outcome_value_picks_backtick_value() -> None:
    assert extract_outcome_value("`accept-with-risk`") == "accept-with-risk"
    assert extract_outcome_value("`continue-critical` is the result.") == "continue-critical"
    assert extract_outcome_value("no backticks here") is None


def test_classify_claim_class_reads_backticked_class() -> None:
    body = "- **Impact:** x\n- **Evidence:** `inference` — note\n- **Mitigation:** y"
    assert classify_claim_class(body) == "inference"
    assert ALLOWED_CLAIM_CLASSES == {"confirmed", "inference", "estimate"}


def test_parse_findings_extracts_claim_class_per_finding() -> None:
    body = (
        "### 1. first\n"
        "- **Impact:** x\n"
        "- **Evidence:** `confirmed` — repo evidence\n"
        "- **Mitigation:** y\n"
        "\n"
        "### 2. second\n"
        "- **Impact:** a\n"
        "- **Evidence:** `estimate` — guess\n"
        "- **Mitigation:** b\n"
    )
    parsed = parse_findings(body)
    assert len(parsed) == 2
    assert parsed[0].evidence_class == "confirmed"
    assert parsed[1].evidence_class == "estimate"


def test_validate_critical_output_main_passes_good_fixture(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        validate_critical_output,
        "parse_args",
        lambda: argparse.Namespace(
            file=str(GOOD_FIXTURE), format="text", max_words=600, strict=False
        ),
    )
    exit_code = validate_critical_output.main()
    assert exit_code == 0
    assert "passes the contract" in capsys.readouterr().out


def test_validate_critical_output_main_reports_blocking_for_bad_fixture(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        validate_critical_output,
        "parse_args",
        lambda: argparse.Namespace(
            file=str(BAD_FIXTURE), format="text", max_words=600, strict=False
        ),
    )
    exit_code = validate_critical_output.main()
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "missing-section-synthesis" in out
    assert "finding-count-out-of-range" in out
    assert "invalid-outcome-value" in out
    assert out.count("BLOCKING") >= 3


def test_validate_critical_output_main_strict_passes_on_good(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        validate_critical_output,
        "parse_args",
        lambda: argparse.Namespace(
            file=str(GOOD_FIXTURE), format="compact", max_words=600, strict=True
        ),
    )
    exit_code = validate_critical_output.main()
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
