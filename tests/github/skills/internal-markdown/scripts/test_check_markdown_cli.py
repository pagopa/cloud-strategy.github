from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / ".github/skills/internal-markdown/scripts/check.sh"
VALID_FIXTURE = ".github/skills/internal-markdown/fixtures/valid/document.md"


@pytest.fixture
def fake_markdownlint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> dict[str, Path]:
    executable = tmp_path / "markdownlint-cli2"
    arguments = tmp_path / "arguments"
    input_text = tmp_path / "input"
    count = tmp_path / "count"
    executable.write_text(
        """#!/bin/bash
set -eu
printf '%s\\n' "$@" > "$FAKE_MARKDOWN_ARGUMENTS"
if [[ "${1:-}" == "--version" ]]; then
  printf '%s\\n' "${FAKE_MARKDOWN_VERSION:-markdownlint-cli2 v0.22.1}"
  exit 0
fi
count=0
if [[ -f "$FAKE_MARKDOWN_COUNT" ]]; then count=$(cat "$FAKE_MARKDOWN_COUNT"); fi
printf '%s\\n' "$((count + 1))" > "$FAKE_MARKDOWN_COUNT"
cat > "$FAKE_MARKDOWN_INPUT"
if [[ "${FAKE_MARKDOWN_EXIT:-0}" != "0" ]]; then
  printf '%s\\n' "${FAKE_MARKDOWN_OUTPUT:-fixture finding}"
  exit "$FAKE_MARKDOWN_EXIT"
fi
if grep -q "Broken references" "$FAKE_MARKDOWN_INPUT"; then
  printf '%s\\n' "broken reference finding"
  exit 1
fi
exit 0
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("FAKE_MARKDOWN_ARGUMENTS", str(arguments))
    monkeypatch.setenv("FAKE_MARKDOWN_INPUT", str(input_text))
    monkeypatch.setenv("FAKE_MARKDOWN_COUNT", str(count))
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    return {"arguments": arguments, "input": input_text, "count": count}


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


def test_missing_markdownlint_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "markdownlint-cli2 v0.22.1" in result.stderr
    assert "npm install -g markdownlint-cli2@0.22.1" in result.stderr


def test_version_mismatch_is_actionable(
    fake_markdownlint: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_MARKDOWN_VERSION", "markdownlint-cli2 v0.21.0")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "required markdownlint-cli2 v0.22.1" in result.stderr


@pytest.mark.parametrize(
    "banner",
    [
        "markdownlint-cli2 v0.22.1",
        "markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)",
    ],
)
def test_exact_markdownlint_version_banners_are_accepted(
    fake_markdownlint: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    banner: str,
) -> None:
    monkeypatch.setenv("FAKE_MARKDOWN_VERSION", banner)

    assert run_checker(VALID_FIXTURE).returncode == 0


@pytest.mark.parametrize(
    "banner",
    [
        "markdownlint-cli2 v0.22.10",
        "markdownlint-cli2 v0.22.1-rc1",
    ],
)
def test_markdownlint_near_match_versions_are_rejected(
    fake_markdownlint: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    banner: str,
) -> None:
    monkeypatch.setenv("FAKE_MARKDOWN_VERSION", banner)

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "required markdownlint-cli2 v0.22.1" in result.stderr


def test_checker_uses_bundle_config_and_stdin(
    fake_markdownlint: dict[str, Path], tmp_path: Path
) -> None:
    source = tmp_path / "consumer.md"
    source.write_text("# Consumer\n\nText.\n", encoding="utf-8")
    (tmp_path / ".markdownlint.json").write_text(
        '{"default": true}\n', encoding="utf-8"
    )

    result = run_checker(str(source))

    assert result.returncode == 0
    arguments = fake_markdownlint["arguments"].read_text(encoding="utf-8").splitlines()
    assert "--config" in arguments
    assert "scripts/markdownlint-cli2.jsonc" in " ".join(arguments)
    assert "-" in arguments
    assert str(source) not in arguments
    assert fake_markdownlint["input"].read_text(encoding="utf-8") == source.read_text(
        encoding="utf-8"
    )


def test_missing_input_is_a_usage_failure(fake_markdownlint: dict[str, Path]) -> None:
    result = run_checker()

    assert result.returncode == 2
    assert "input" in result.stderr.lower()


def test_missing_file_is_a_file_failure(fake_markdownlint: dict[str, Path]) -> None:
    result = run_checker("does-not-exist.md")

    assert result.returncode == 2
    assert "not found" in result.stderr.lower()


def test_tool_findings_are_normalized_to_one(
    fake_markdownlint: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_MARKDOWN_EXIT", "1")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 1
    assert "fixture finding" in result.stdout


def test_multi_file_findings_preserve_each_source_path(
    fake_markdownlint: dict[str, Path], tmp_path: Path
) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("# First\n", encoding="utf-8")
    second.write_text("# Second\n", encoding="utf-8")

    result = run_checker(
        str(first),
        str(second),
        FAKE_MARKDOWN_EXIT="1",
        FAKE_MARKDOWN_OUTPUT="stdin:5:1 MD052/reference-links-images Reference links and images should use a label that is defined",
    )

    assert result.returncode == 1
    assert f"{first}:5:1 MD052" in result.stdout
    assert f"{second}:5:1 MD052" in result.stdout


def test_unexpected_tool_exit_is_normalized_to_two(
    fake_markdownlint: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_MARKDOWN_EXIT", "7")

    result = run_checker(VALID_FIXTURE)

    assert result.returncode == 2
    assert "status 7" in result.stderr


def test_more_than_one_hundred_files_is_a_usage_failure(
    fake_markdownlint: dict[str, Path], tmp_path: Path
) -> None:
    files = []
    for index in range(101):
        path = tmp_path / f"document-{index}.md"
        path.write_text("# Document\n", encoding="utf-8")
        files.append(str(path))

    result = run_checker(*files)

    assert result.returncode == 2
    assert "at most 100 input files" in result.stderr
    assert not fake_markdownlint["count"].exists()


def test_self_test_runs_bundled_fixtures(fake_markdownlint: dict[str, Path]) -> None:
    result = run_checker("--self-test")

    assert result.returncode == 0
    assert "self-test" in result.stdout.lower()
