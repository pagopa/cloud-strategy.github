from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / ".github/skills/internal-json/scripts/check.py"
FIXTURE_ROOT = REPO_ROOT / ".github/skills/internal-json/fixtures"
EXPECTED_CODES = {
    "JSON_BOM",
    "JSON_ENCODING",
    "JSON_SYNTAX",
    "JSON_DUPLICATE_KEY",
    "JSON_NON_FINITE",
    "JSON_UNSAFE_INTEGER",
    "JSON_NUMBER_RANGE",
    "JSON_UNPAIRED_SURROGATE",
}


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=REPO_ROOT,
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_nested_json_passes() -> None:
    result = run_checker(str(FIXTURE_ROOT / "valid/nested.json"))

    assert result.returncode == 0
    assert "checks passed within supported scope" in result.stdout


@pytest.mark.parametrize(
    ("fixture", "code"),
    [
        ("duplicate-root.json", "JSON_DUPLICATE_KEY"),
        ("duplicate-nested.json", "JSON_DUPLICATE_KEY"),
        ("non-finite.json", "JSON_NON_FINITE"),
        ("unsafe-integer.json", "JSON_UNSAFE_INTEGER"),
        ("overflow-number.json", "JSON_NUMBER_RANGE"),
    ],
)
def test_invalid_fixtures_report_stable_codes(fixture: str, code: str) -> None:
    result = run_checker(str(FIXTURE_ROOT / "invalid" / fixture))

    assert result.returncode == 1
    assert code in result.stdout


def test_duplicate_keys_are_reported_at_root_and_nested_levels() -> None:
    result = run_checker(
        str(FIXTURE_ROOT / "invalid/duplicate-root.json"),
        str(FIXTURE_ROOT / "invalid/duplicate-nested.json"),
    )

    assert result.returncode == 1
    assert result.stdout.count("JSON_DUPLICATE_KEY") >= 2


def test_structural_findings_keep_source_and_json_path(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text('{"first": 1, "first": 2}', encoding="utf-8")
    second.write_text('{"second": 1, "second": 2}', encoding="utf-8")

    result = run_checker("--format", "json", str(first), str(second))

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    duplicate_findings = [
        finding
        for finding in payload["findings"]
        if finding["code"] == "JSON_DUPLICATE_KEY"
    ]
    assert {finding["source"] for finding in duplicate_findings} == {
        str(first),
        str(second),
    }
    assert {finding["path"] for finding in duplicate_findings} == {"$"}


@pytest.mark.parametrize(
    "payload",
    [
        b"\xef\xbb\xbf{\"name\": \"value\"}",
        b"{\"name\": \xff}",
    ],
)
def test_bom_and_invalid_utf8_are_rejected(
    tmp_path: Path, payload: bytes
) -> None:
    path = tmp_path / "invalid.json"
    path.write_bytes(payload)

    result = run_checker(str(path))

    assert result.returncode == 1
    assert any(code in result.stdout for code in ("JSON_BOM", "JSON_ENCODING"))


@pytest.mark.parametrize(
    ("payload", "expected_line", "expected_column"),
    [
        (b'{\n"x":\xff}', 2, 5),
        ('{\n"é": '.encode("utf-8") + b"\xff}", 2, 6),
    ],
)
def test_invalid_utf8_reports_text_coordinates(
    tmp_path: Path,
    payload: bytes,
    expected_line: int,
    expected_column: int,
) -> None:
    path = tmp_path / "invalid-utf8.json"
    path.write_bytes(payload)

    result = run_checker("--format", "json", str(path))

    finding = json.loads(result.stdout)["findings"][0]
    assert result.returncode == 1
    assert finding["code"] == "JSON_ENCODING"
    assert (finding["line"], finding["column"]) == (
        expected_line,
        expected_column,
    )


@pytest.mark.parametrize(
    "content",
    [
        '{"name": "value",}',
        '{"name": /* comment */ "value"}',
        '{"items": [1, 2,}',
    ],
)
def test_non_standard_json_syntax_is_rejected(tmp_path: Path, content: str) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(content, encoding="utf-8")

    result = run_checker(str(path))

    assert result.returncode == 1
    assert "JSON_SYNTAX" in result.stdout


def test_unpaired_surrogates_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "surrogate.json"
    path.write_text('{"\\ud800": "\\udfff"}', encoding="utf-8")

    result = run_checker(str(path))

    assert result.returncode == 1
    assert "JSON_UNPAIRED_SURROGATE" in result.stdout


def test_valid_surrogate_pair_is_accepted(tmp_path: Path) -> None:
    path = tmp_path / "surrogate-pair.json"
    path.write_text('{"emoji": "\\ud83d\\ude00"}', encoding="utf-8")

    result = run_checker(str(path))

    assert result.returncode == 0


def test_json_output_is_stable_and_reports_checked_files() -> None:
    result = run_checker(
        "--format",
        "json",
        str(FIXTURE_ROOT / "valid/nested.json"),
        str(FIXTURE_ROOT / "invalid/duplicate-root.json"),
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert set(payload) == {"status", "files_checked", "findings_count", "findings"}
    assert payload["status"] == "findings"
    assert payload["files_checked"] == 2
    assert payload["findings_count"] == len(payload["findings"])
    assert payload["findings"][0]["code"] == "JSON_DUPLICATE_KEY"
    assert set(payload["findings"][0]) == {
        "code",
        "source",
        "path",
        "line",
        "column",
        "message",
    }


def test_findings_are_bounded_to_one_hundred(tmp_path: Path) -> None:
    pairs = ", ".join(f'"key": {index}' for index in range(151))
    path = tmp_path / "many-findings.json"
    path.write_text("{" + pairs + "}", encoding="utf-8")

    result = run_checker("--format", "json", str(path))

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["findings_count"] == 100


def test_arbitrarily_long_integer_is_a_bounded_finding(tmp_path: Path) -> None:
    path = tmp_path / "huge-integer.json"
    path.write_text("9" * 5000, encoding="utf-8")

    result = run_checker("--format", "json", str(path))

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert result.stderr == ""
    assert payload["findings_count"] == 1
    assert payload["findings"][0]["code"] == "JSON_UNSAFE_INTEGER"
    assert len(result.stdout) < 2000


def test_self_test_passes() -> None:
    result = run_checker("--self-test")

    assert result.returncode == 0
    assert "self-test passed" in result.stdout.lower()


def test_usage_and_file_errors_return_two() -> None:
    no_args = run_checker()
    missing = run_checker("does-not-exist.json")

    assert no_args.returncode == 2
    assert missing.returncode == 2
    assert "input" in no_args.stderr.lower()
    assert "not found" in missing.stderr.lower()
