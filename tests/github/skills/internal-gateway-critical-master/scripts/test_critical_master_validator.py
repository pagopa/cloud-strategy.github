import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
VALIDATOR = (
    REPO_ROOT
    / ".github/skills/internal-gateway-critical-master/scripts/validate_critical_output.py"
)
FIXTURES = REPO_ROOT / ".github/skills/internal-gateway-critical-master/fixtures"
VALIDATOR_SPEC = spec_from_file_location("validate_critical_output", VALIDATOR)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
VALIDATOR_MODULE = module_from_spec(VALIDATOR_SPEC)
sys.path.insert(0, str(VALIDATOR.parent))
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_fixture_passes() -> None:
    result = run_validator("--file", str(FIXTURES / "critical_output_valid.md"))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_invalid_fixture_fails() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_invalid_missing_section.md"),
    )
    assert result.returncode != 0
    assert "Required section" in result.stdout


def test_strict_mode_fails_on_advisory_finding() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_advisory.md"),
        "--strict",
    )
    assert result.returncode != 0
    assert "summary-word-limit" in result.stdout or "total-word-limit" in result.stdout


def test_question_word_limit_is_advisory() -> None:
    text = """
## Summary

We are challenging whether local validation can replace CI validation.

## Findings

### 1. The audit trail weakens

- **Impact:** Central CI logs become incomplete.
- **Evidence:** `inference` - no replacement logging is described.
- **Mitigation:** Define a durable audit record before replacing CI.
- **Question:** Which durable centrally searchable independently retained signed audit record replaces the CI validation log for reviewers, compliance checks, later investigations, audit replay, governance reporting, incident review, and rollout approval?

## Synthesis

The strongest risk is compliance visibility.

## Outcome

`accept-with-risk`
"""

    findings = VALIDATOR_MODULE.validate_output(text)

    assert any(finding.code == "finding-question-word-limit" for finding in findings)


def test_objection_word_limit_is_advisory() -> None:
    long_objection = " ".join(
        [
            "This",
            "objection",
            "heading",
            "intentionally",
            "exceeds",
            "the",
            "thirty",
            "word",
            "limit",
            "by",
            "repeating",
            "core",
            "concerns",
            "about",
            "the",
            "proposal",
            "without",
            "adding",
            "any",
            "new",
            "signal",
            "for",
            "the",
            "reader",
            "and",
            "must",
            "be",
            "shortened",
            "now",
            "again",
            "finally",
        ]
    )
    text = f"""
## Summary

We are testing the objection word-limit enforcement.

## Findings

### 1. {long_objection}

- **Impact:** Scope ambiguity risks rejection.
- **Evidence:** `inference` — no attachment to contract.
- **Mitigation:** Tighten scope before approval.

## Outcome

`accept-with-risk`

## Synthesis

The challenge surfaces one open question.
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    assert any(finding.code == "finding-objection-word-limit" for finding in findings)


def test_adversarial_fixture_produces_expected_codes() -> None:
    text = (FIXTURES / "critical_output_invalid_adversarial.md").read_text(encoding="utf-8")
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    expected_codes = {
        "empty-section-summary",
        "empty-section-synthesis",
        "finding-number-sequence",
        "invalid-finding-field-label",
        "multiple-root-questions",
        "multiple-outcome-values",
    }
    assert expected_codes <= codes


def test_duplicate_required_section_detected() -> None:
    text = """
## Summary

One paragraph summary.

## Summary

Duplicate summary section.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `inference`; quality=`partial` — evidence.
- **Mitigation:** Fix it.

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "duplicate-section-summary" in codes or "section-order" in codes


def test_section_order_violation_detected() -> None:
    text = """
## Summary

One paragraph summary.

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `inference`; quality=`partial` — evidence.
- **Mitigation:** Fix it.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "section-order" in codes


def test_unknown_claim_class_detected() -> None:
    text = """
## Summary

One paragraph summary.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `speculation`; quality=`partial` — evidence.
- **Mitigation:** Fix it.

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "invalid-claim-class" in codes


def test_missing_evidence_quality_detected() -> None:
    text = """
## Summary

One paragraph summary.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `inference` — evidence without quality marker.
- **Mitigation:** Fix it.

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "missing-evidence-quality" in codes


def test_valid_premortem_fixture_passes_strict() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_valid_premortem.md"),
        "--strict",
    )
    assert result.returncode == 0


def test_valid_defended_fixture_passes_strict() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_valid_defended.md"),
        "--strict",
    )
    assert result.returncode == 0


def test_invalid_premortem_missing_mitigation_for_high_cause() -> None:
    text = (FIXTURES / "critical_output_invalid_premortem.md").read_text(encoding="utf-8")
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "missing-cause-mitigation" in codes


def test_invalid_defense_missing_remaining_vulnerability() -> None:
    text = (FIXTURES / "critical_output_invalid_defense.md").read_text(encoding="utf-8")
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "missing-remaining-vulnerability" in codes


def test_premortem_section_rejected_when_not_triggered() -> None:
    text = """
## Summary

One paragraph summary.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Pre-mortem

- **Failure:** Something goes wrong.
- **Cause 1:** Root cause | class=`inference` | likelihood=`high` | mitigation=do something.

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `inference`; quality=`partial` — evidence.
- **Mitigation:** Fix it.

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "premortem-not-triggered" in codes


def test_premortem_section_required_when_triggered() -> None:
    text = """
## Summary

One paragraph summary.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `triggered`

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `inference`; quality=`partial` — evidence.
- **Mitigation:** Fix it.

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "missing-premortem-section" in codes


def test_defense_none_does_not_require_strongest_defense() -> None:
    text = """
## Summary

One paragraph summary.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Findings

### 1. The objection

- **Impact:** Something matters.
- **Evidence:** `inference`; quality=`partial` — evidence.
- **Mitigation:** Fix it.

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Something.
- **Unresolved uncertainty:** Something.

## Outcome

`accept-with-risk`
"""
    findings = VALIDATOR_MODULE.validate_output(text)
    codes = {f.code for f in findings}
    assert "missing-strongest-defense" not in codes
    assert "missing-remaining-vulnerability" not in codes


def test_cli_format_text_renders_findings() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_invalid_adversarial.md"),
        "--format", "text",
    )
    assert result.returncode != 0
    assert "[BLOCKING]" in result.stdout or "[advisory]" in result.stdout


def test_cli_format_json_returns_finding_list() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_invalid_adversarial.md"),
        "--format", "json",
    )
    import json as json_mod
    data = json_mod.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "code" in data[0]


def test_cli_format_compact_returns_status_and_counts() -> None:
    result = run_validator(
        "--file",
        str(FIXTURES / "critical_output_invalid_adversarial.md"),
        "--format", "compact",
    )
    import json as json_mod
    data = json_mod.loads(result.stdout)
    assert "status" in data
    assert "finding_counts" in data
    assert "next_action" in data


def test_cli_unreadable_file_exits_nonzero_with_stderr() -> None:
    result = run_validator(
        "--file", "/nonexistent/path/missing_file.md",
    )
    assert result.returncode != 0
    assert result.stderr.strip() != ""


def test_cli_make_target_includes_strict() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "--strict" in makefile
    assert "critical-validate" in makefile


