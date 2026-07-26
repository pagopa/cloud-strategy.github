from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / ".github/skills/internal-makefile/scripts/check.sh"
VALID_FIXTURE = ".github/skills/internal-makefile/fixtures/valid/Makefile"


@pytest.fixture
def fake_checkmake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    executable = tmp_path / "checkmake"
    arguments = tmp_path / "arguments"
    executable.write_text(
        """#!/bin/bash
set -eu
printf '%s\\n' "$@" > "$FAKE_CHECKMAKE_ARGUMENTS"
if [[ "${1:-}" == "--version" ]]; then
  printf '%s\\n' "${FAKE_CHECKMAKE_VERSION:-checkmake version 0.3.2}"
  exit 0
fi
if [[ "${FAKE_CHECKMAKE_EXIT:-0}" != "0" ]]; then
  printf '%s\\n' "fixture finding"
  exit "$FAKE_CHECKMAKE_EXIT"
fi
if [[ " $* " == *missing-phony.mk* ]]; then
  printf '%s\\n' "fixture finding: phonydeclared"
  exit 1
fi
exit 0
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("FAKE_CHECKMAKE_ARGUMENTS", str(arguments))
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


def test_missing_checkmake_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "checkmake version 0.3.2" in result.stderr
    assert "go install github.com/checkmake/checkmake/cmd/checkmake@v0.3.2" in result.stderr


def test_version_mismatch_is_actionable(
    fake_checkmake: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_CHECKMAKE_VERSION", "checkmake version 0.3.1")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "required checkmake version 0.3.2" in result.stderr


def test_homebrew_version_banner_with_required_version_is_accepted(
    fake_checkmake: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(
        "FAKE_CHECKMAKE_VERSION",
        "checkmake 0.3.2 built at 2026-01-12T19:04:29Z by Homebrew",
    )

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 0


@pytest.mark.parametrize(
    "banner",
    [
        "checkmake version 0.3.2-rc1",
        "checkmake version 0.3.20",
        "checkmake 0.3.2-rc1 built locally",
    ],
)
def test_checkmake_near_match_versions_are_rejected(
    fake_checkmake: Path,
    monkeypatch: pytest.MonkeyPatch,
    banner: str,
) -> None:
    monkeypatch.setenv("FAKE_CHECKMAKE_VERSION", banner)

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "required checkmake version 0.3.2" in result.stderr


def test_checker_uses_bundle_config_and_all_explicit_files(
    fake_checkmake: Path, tmp_path: Path
) -> None:
    second = tmp_path / "other.mk"
    second.write_text(".PHONY: other\nother:\n\t@true\n", encoding="utf-8")

    result = run_checker(VALID_FIXTURE, str(second))

    assert result.returncode == 0
    arguments = fake_checkmake.read_text(encoding="utf-8").splitlines()
    assert "--config" in arguments
    assert "scripts/checkmake.ini" in " ".join(arguments)
    assert "--output" in arguments
    assert "text" in arguments
    assert VALID_FIXTURE in arguments
    assert str(second) in arguments


def test_missing_input_is_a_usage_failure(fake_checkmake: Path) -> None:
    result = run_checker()

    assert result.returncode == 2
    assert "input" in result.stderr.lower()


def test_missing_file_is_a_file_failure(fake_checkmake: Path) -> None:
    result = run_checker("does-not-exist.mk")

    assert result.returncode == 2
    assert "not found" in result.stderr.lower()


def test_tool_findings_are_normalized_to_one(
    fake_checkmake: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = run_checker(
        ".github/skills/internal-makefile/fixtures/invalid/missing-phony.mk"
    )

    assert result.returncode == 1
    assert "fixture finding" in result.stdout


def test_unexpected_tool_exit_is_normalized_to_two(
    fake_checkmake: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_CHECKMAKE_EXIT", "7")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "status 7" in result.stderr


def test_checker_never_invokes_make_or_eval() -> None:
    source = CHECKER.read_text(encoding="utf-8").lower()

    assert "eval" not in source
    assert " make " not in source


def test_self_test_runs_bundled_fixtures(fake_checkmake: Path) -> None:
    result = run_checker("--self-test")

    assert result.returncode == 0
    assert "self-test" in result.stdout.lower()
