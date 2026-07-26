#!/usr/bin/env python3
"""Strict, read-only JSON format checker using only the Python standard library."""
from __future__ import annotations

import argparse
import codecs
import decimal
import json
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_FINDINGS = 100
MAX_SAFE_INTEGER = 2**53 - 1
MAX_BINARY64 = decimal.Decimal(str(sys.float_info.max))


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    line: int | None
    column: int | None
    message: str


@dataclass(frozen=True)
class JsonNumber:
    raw: str
    integer: bool


@dataclass(frozen=True)
class JsonObject:
    pairs: list[tuple[str, object]]


def _append_finding(
    findings: list[Finding],
    code: str,
    path: str,
    message: str,
    line: int | None = None,
    column: int | None = None,
) -> None:
    if len(findings) < MAX_FINDINGS:
        findings.append(Finding(code, path, line, column, message))


def _member_path(path: str, key: str) -> str:
    return f"{path}[{json.dumps(key, ensure_ascii=True)}]"


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _check_number(number: JsonNumber, path: str, findings: list[Finding]) -> None:
    try:
        if number.integer:
            if abs(int(number.raw)) > MAX_SAFE_INTEGER:
                _append_finding(
                    findings,
                    "JSON_UNSAFE_INTEGER",
                    path,
                    f"integer magnitude exceeds {MAX_SAFE_INTEGER}",
                )
            return

        value = decimal.Decimal(number.raw)
    except decimal.InvalidOperation:
        _append_finding(
            findings,
            "JSON_SYNTAX",
            path,
            "number could not be interpreted",
        )
        return

    if value.is_finite() and abs(value) > MAX_BINARY64:
        _append_finding(
            findings,
            "JSON_NUMBER_RANGE",
            path,
            "finite number exceeds IEEE-754 binary64 range",
        )


def _inspect_value(value: object, path: str, findings: list[Finding]) -> None:
    if len(findings) >= MAX_FINDINGS:
        return
    if isinstance(value, JsonObject):
        seen: set[str] = set()
        for key, child in value.pairs:
            child_path = _member_path(path, key)
            if key in seen:
                _append_finding(
                    findings,
                    "JSON_DUPLICATE_KEY",
                    path,
                    f"object name {key!r} is repeated",
                )
            seen.add(key)
            if _contains_surrogate(key):
                _append_finding(
                    findings,
                    "JSON_UNPAIRED_SURROGATE",
                    child_path,
                    "string contains an unpaired UTF-16 surrogate",
                )
            _inspect_value(child, child_path, findings)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _inspect_value(child, f"{path}[{index}]", findings)
        return
    if isinstance(value, str) and _contains_surrogate(value):
        _append_finding(
            findings,
            "JSON_UNPAIRED_SURROGATE",
            path,
            "string contains an unpaired UTF-16 surrogate",
        )
    elif isinstance(value, JsonNumber):
        _check_number(value, path, findings)


def _line_column(text: str, position: int) -> tuple[int, int]:
    line = text.count("\n", 0, position) + 1
    previous_newline = text.rfind("\n", 0, position)
    return line, position - previous_newline


def check_bytes(data: bytes, path: str) -> list[Finding]:
    findings: list[Finding] = []
    if data.startswith(codecs.BOM_UTF8):
        _append_finding(
            findings,
            "JSON_BOM",
            path,
            "UTF-8 BOM is not allowed",
            1,
            1,
        )
        return findings

    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        _append_finding(
            findings,
            "JSON_ENCODING",
            path,
            "input is not valid UTF-8",
            error.start + 1,
            error.start + 1,
        )
        return findings

    def parse_constant(raw: str) -> JsonNumber:
        _append_finding(
            findings,
            "JSON_NON_FINITE",
            "$",
            f"non-standard constant {raw} is not allowed",
        )
        return JsonNumber(raw, integer=False)

    try:
        value = json.loads(
            text,
            object_pairs_hook=JsonObject,
            parse_int=lambda raw: JsonNumber(raw, integer=True),
            parse_float=lambda raw: JsonNumber(raw, integer=False),
            parse_constant=parse_constant,
        )
    except json.JSONDecodeError as error:
        _append_finding(
            findings,
            "JSON_SYNTAX",
            path,
            error.msg,
            error.lineno,
            error.colno,
        )
        return findings

    _inspect_value(value, "$", findings)
    return findings


def check_file(path: Path) -> list[Finding]:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise OSError(f"unable to read input file {path}: {error}") from error
    return check_bytes(data, str(path))


def _render_text(findings: list[Finding]) -> str:
    if not findings:
        return "checks passed within supported scope\n"
    lines = []
    for finding in findings:
        location = finding.path
        if finding.line is not None and finding.column is not None:
            location += f":{finding.line}:{finding.column}"
        lines.append(f"{location} {finding.code}: {finding.message}")
    return "\n".join(lines) + "\n"


def _render_json(findings: list[Finding], files_checked: int) -> str:
    return json.dumps(
        {
            "status": "passed" if not findings else "findings",
            "files_checked": files_checked,
            "findings_count": len(findings),
            "findings": [
                {
                    "code": finding.code,
                    "path": finding.path,
                    "line": finding.line,
                    "column": finding.column,
                    "message": finding.message,
                }
                for finding in findings
            ],
        },
        ensure_ascii=True,
        sort_keys=False,
    ) + "\n"


def _run_self_test(script_path: Path) -> int:
    fixture_root = script_path.parent.parent / "fixtures"
    valid = fixture_root / "valid/nested.json"
    invalid = [
        fixture_root / "invalid/duplicate-root.json",
        fixture_root / "invalid/duplicate-nested.json",
        fixture_root / "invalid/non-finite.json",
        fixture_root / "invalid/unsafe-integer.json",
        fixture_root / "invalid/overflow-number.json",
    ]
    try:
        if check_file(valid):
            print("error: JSON self-test valid fixture produced findings", file=sys.stderr)
            return 2
        for path in invalid:
            if not check_file(path):
                print(f"error: JSON self-test invalid fixture passed: {path}", file=sys.stderr)
                return 2
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print("JSON self-test passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check strict JSON format constraints for explicit files"
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)

    if args.self_test:
        if args.files:
            parser.error("--self-test does not accept input files")
        return _run_self_test(Path(__file__).resolve())
    if not args.files:
        parser.error("at least one input file is required")

    findings: list[Finding] = []
    files_checked = 0
    try:
        for name in args.files:
            path = Path(name)
            if not path.is_file():
                print(f"error: input file not found: {name}", file=sys.stderr)
                return 2
            files_checked += 1
            for finding in check_file(path):
                if len(findings) < MAX_FINDINGS:
                    findings.append(finding)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # pragma: no cover - defensive CLI boundary
        print(f"error: internal checker failure: {error}", file=sys.stderr)
        return 2

    if args.format == "json":
        sys.stdout.write(_render_json(findings, files_checked))
    else:
        sys.stdout.write(_render_text(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
