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
