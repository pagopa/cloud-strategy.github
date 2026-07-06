import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPO_ROOT
    / ".github/skills/internal-gateway-critical-master/scripts/validate_critical_output.py"
)
FIXTURES = REPO_ROOT / ".github/skills/internal-gateway-critical-master/fixtures"


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
