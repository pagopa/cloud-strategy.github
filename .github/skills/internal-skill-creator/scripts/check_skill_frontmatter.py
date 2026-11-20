#!/usr/bin/env python3
"""Check SKILL.md frontmatter for YAML that strict host parsers reject."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # The stdlib scan still runs; only the strict parse is skipped.
    yaml = None

FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
TOP_LEVEL_KEY = re.compile(r"^([A-Za-z0-9_.-]+):([ \t].*|)$")
REQUIRED_KEYS = ("name", "description")
FORBIDDEN_FIRST_CHARS = frozenset("`@%,]}#&*!")
FORBIDDEN_PREFIXES = ("- ", "? ", ": ")
FIX_HINT = 'Wrap the whole value in double quotes, or use a ">-" folded block.'


def _finding(code: str, message: str, path: Path, line: int | None = None) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "code": code,
        "message": message,
        "severity": "blocking",
        "path": path.as_posix(),
    }
    if line is not None:
        finding["line"] = line
    return finding


def _plain_hazard(value: str, first_line: bool) -> str | None:
    stripped = value.strip()
    if first_line and (
        stripped[:1] in FORBIDDEN_FIRST_CHARS
        or stripped.startswith(FORBIDDEN_PREFIXES)
        or stripped in {"-", "?", ":"}
    ):
        return f"plain value starts with the YAML indicator {stripped[:1]!r}"
    if ": " in stripped or stripped.endswith(":"):
        return 'plain value contains ": ", which YAML reads as a nested mapping'
    if " #" in stripped or "\t#" in stripped:
        return 'plain value contains " #", which YAML truncates as a comment'
    return None


def check_file(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [_finding("frontmatter-missing", f"Cannot read file: {error}.", path)]
    match = FRONTMATTER.match(text)
    if not match:
        return [_finding("frontmatter-missing", "No leading --- frontmatter block.", path)]

    findings: list[dict[str, Any]] = []
    present: set[str] = set()
    current_key: str | None = None
    plain_open = False
    for offset, raw in enumerate(match.group(1).splitlines()):
        line_number = offset + 2
        if not raw.strip() or raw.startswith("#"):
            continue
        if raw[:1] in {" ", "\t"}:
            if current_key is not None:
                present.add(current_key)
            if plain_open:
                reason = _plain_hazard(raw, first_line=False)
                if reason:
                    findings.append(
                        _finding(
                            "frontmatter-unsafe-plain-scalar",
                            f"`{current_key}` {reason}. {FIX_HINT}",
                            path,
                            line_number,
                        )
                    )
            continue
        key_match = TOP_LEVEL_KEY.match(raw)
        if not key_match:
            current_key, plain_open = None, False
            continue
        current_key, value = key_match.group(1), key_match.group(2).strip()
        plain_open = False
        if not value:
            continue
        present.add(current_key)
        if value[0] in "\"'|>[{":
            continue
        plain_open = True
        reason = _plain_hazard(value, first_line=True)
        if reason:
            findings.append(
                _finding(
                    "frontmatter-unsafe-plain-scalar",
                    f"`{current_key}` {reason}. {FIX_HINT}",
                    path,
                    line_number,
                )
            )

    for key in REQUIRED_KEYS:
        if key not in present:
            findings.append(
                _finding("frontmatter-missing-key", f"Missing non-empty `{key}`.", path)
            )

    if not findings and yaml is not None:
        try:
            parsed = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            mark = getattr(error, "problem_mark", None)
            line = mark.line + 2 if mark is not None else None
            problem = getattr(error, "problem", None) or str(error)
            findings.append(
                _finding("frontmatter-yaml-error", f"Strict YAML parse failed: {problem}.", path, line)
            )
        else:
            if not isinstance(parsed, dict):
                findings.append(
                    _finding("frontmatter-yaml-error", "Frontmatter is not a YAML mapping.", path)
                )
            else:
                for key in REQUIRED_KEYS:
                    if not isinstance(parsed.get(key), str):
                        findings.append(
                            _finding("frontmatter-yaml-error", f"`{key}` does not parse as a string.", path)
                        )
    return findings


def _payload(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "failed" if findings else "ok",
        "finding_counts": {"blocking": len(findings), "total": len(findings)},
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_files", nargs="+", type=Path)
    parser.add_argument("--format", choices=("text", "compact"), default="text")
    args = parser.parse_args(argv)

    findings = [finding for path in args.skill_files for finding in check_file(path)]
    if args.format == "compact":
        print(json.dumps(_payload(findings), sort_keys=True))
    elif findings:
        for finding in findings:
            location = finding["path"] + (f":{finding['line']}" if "line" in finding else "")
            print(f"{location}: {finding['code']}: {finding['message']}")
    else:
        print("OK: SKILL.md frontmatter is strict-YAML safe.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
