from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / ".github/skills/internal-yaml/scripts/check.sh"
FIXTURES_DIR = ".github/skills/internal-yaml/fixtures"
VALID_FIXTURE = f"{FIXTURES_DIR}/valid/pre-commit-like.yaml"
REQUIRED_VERSION = "yamllint 1.38.0"


def _fixture_names(kind: str) -> list[str]:
    return sorted(path.name for path in (REPO_ROOT / FIXTURES_DIR / kind).glob("*.yaml"))


def _has_pinned_yamllint() -> bool:
    try:
        result = subprocess.run(
            ["yamllint", "--version"], text=True, capture_output=True, check=False
        )
    except OSError:
        return False
    return result.stdout.strip() == REQUIRED_VERSION


requires_pinned_yamllint = pytest.mark.skipif(
    not _has_pinned_yamllint(), reason=f"requires {REQUIRED_VERSION} on PATH"
)


@pytest.fixture
def fake_yamllint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    executable = tmp_path / "yamllint"
    arguments = tmp_path / "arguments"
    executable.write_text(
        """#!/usr/bin/env bash
set -eu
printf '%s\\n' "$@" > "$FAKE_YAMLLINT_ARGUMENTS"
if [[ "${1:-}" == "--version" ]]; then
  printf '%s\\n' "${FAKE_YAMLLINT_VERSION:-yamllint 1.38.0}"
  exit 0
fi
if [[ "${FAKE_YAMLLINT_EXIT:-0}" != "0" ]]; then
  printf '%s\\n' "fixture finding" >&2
  exit "$FAKE_YAMLLINT_EXIT"
fi
if [[ " $* " == *fixtures/invalid/* ]]; then
  exit 1
fi
exit 0
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("FAKE_YAMLLINT_ARGUMENTS", str(arguments))
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    return arguments


def run_checker(*args: str, **extra_env: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(extra_env)
    return subprocess.run(
        [str(CHECKER), *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_missing_yamllint_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "yamllint 1.38.0" in result.stderr
    assert "pipx install yamllint==1.38.0" in result.stderr


def test_version_mismatch_is_actionable(
    fake_yamllint: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_YAMLLINT_VERSION", "yamllint 1.37.0")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "required yamllint 1.38.0" in result.stderr


def test_checker_uses_only_its_explicit_config(fake_yamllint: Path) -> None:
    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 0
    arguments = fake_yamllint.read_text(encoding="utf-8").splitlines()
    assert "--config-file" in arguments
    assert "scripts/yamllint.yaml" in " ".join(arguments)
    assert "--strict" in arguments


def test_missing_input_is_a_usage_failure(fake_yamllint: Path) -> None:
    result = run_checker()

    assert result.returncode == 2
    assert "input" in result.stderr.lower()


def test_missing_file_is_a_file_failure(fake_yamllint: Path) -> None:
    result = run_checker("does-not-exist.yaml")

    assert result.returncode == 2
    assert "not found" in result.stderr.lower()


def test_tool_findings_are_normalized_to_one(
    fake_yamllint: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_YAMLLINT_EXIT", "1")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 1
    assert "fixture finding" in result.stdout + result.stderr


def test_unexpected_tool_exit_is_normalized_to_two(
    fake_yamllint: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_YAMLLINT_EXIT", "7")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "status 7" in result.stderr


def test_self_test_runs_bundled_fixtures(fake_yamllint: Path) -> None:
    result = run_checker("--self-test")

    assert result.returncode == 0
    assert "self-test" in result.stdout.lower()


@requires_pinned_yamllint
@pytest.mark.parametrize("fixture", _fixture_names("invalid"))
def test_invalid_fixture_is_reported_as_a_format_finding(fixture: str) -> None:
    result = run_checker(f"{FIXTURES_DIR}/invalid/{fixture}")

    assert result.returncode == 1, result.stdout + result.stderr


@requires_pinned_yamllint
@pytest.mark.parametrize("fixture", _fixture_names("valid"))
def test_valid_fixture_passes_the_configured_rules(fixture: str) -> None:
    result = run_checker(f"{FIXTURES_DIR}/valid/{fixture}")

    assert result.returncode == 0, result.stdout + result.stderr
