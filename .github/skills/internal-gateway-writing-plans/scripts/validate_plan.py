#!/usr/bin/env python3
"""Deterministic objective validation for retained implementation Plans."""

from __future__ import annotations

import re
import sys
from pathlib import Path


FILENAME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-[a-z0-9-]+\.md$")
TASK_HEADING_PATTERN = re.compile(r"^###\s+Task\s+(\d+):")
FILES_BLOCK_PATTERN = re.compile(
    r"\*\*Files:\*\*\s*\n((?:\s*-\s+.+\n?)+)", re.MULTILINE
)
FILE_TARGET_PATTERN = re.compile(r"\.github/|tests/|AGENTS\.md|Makefile")
VALIDATION_PATTERN = re.compile(r"rtk\s+\S+|python3\s+\S+|pytest|make\s+\S+")
GIT_MUTATION_PHRASES = (
    "git add",
    "git commit",
    "git push",
    "git merge",
)


def _check_filename(path: Path) -> str | None:
    if not FILENAME_PATTERN.match(path.name):
        return "filename"
    return None


def _check_preflight(text: str) -> str | None:
    required = ("Target", "Anti-scope", "Validation path", "Stop conditions", "Observable acceptance")
    for marker in required:
        if marker not in text:
            return "preflight"
    return None


def _extract_tasks(text: str) -> list[tuple[int, str]]:
    tasks: list[tuple[int, str]] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        match = TASK_HEADING_PATTERN.match(line)
        if match:
            task_num = int(match.group(1))
            task_body = "\n".join(lines[idx:])
            next_match = TASK_HEADING_PATTERN.search(task_body[len(line) + 1:])
            if next_match:
                task_body = "\n".join(lines[idx:idx + 1 + next_match.start()])
            tasks.append((task_num, task_body))
    return tasks


def _check_ordered_tasks(tasks: list[tuple[int, str]]) -> str | None:
    if not tasks:
        return "ordered_tasks"
    nums = [t[0] for t in tasks]
    if nums != sorted(nums) or len(nums) != len(set(nums)):
        return "ordered_tasks"
    return None


def _check_file_targets(tasks: list[tuple[int, str]]) -> str | None:
    for _, body in tasks:
        files_match = FILES_BLOCK_PATTERN.search(body)
        if not files_match:
            return "file_targets"
        files_block = files_match.group(1)
        if not FILE_TARGET_PATTERN.search(files_block):
            return "file_targets"
    return None


def _check_validation(tasks: list[tuple[int, str]]) -> str | None:
    for _, body in tasks:
        if not VALIDATION_PATTERN.search(body) and "validation gap" not in body.lower():
            return "validation"
    return None


def _check_git_mutation(text: str) -> str | None:
    lower = text.lower()
    for phrase in GIT_MUTATION_PHRASES:
        if phrase in lower:
            return "git_mutation"
    return None


def _check_execution_owner(text: str) -> str | None:
    if "internal-gateway-execute-plans" not in text:
        return "execution_owner"
    if "superpowers-executing-plans" in text and "internal-gateway-execute-plans" not in text:
        return "execution_owner"
    return None


def validate_plan(path: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    text = path.read_text(encoding="utf-8")

    filename_code = _check_filename(path)
    if filename_code:
        findings.append({"code": filename_code, "message": f"invalid basename: {path.name}"})

    preflight_code = _check_preflight(text)
    if preflight_code:
        findings.append({"code": preflight_code, "message": "missing preflight fields"})

    tasks = _extract_tasks(text)
    ordered_code = _check_ordered_tasks(tasks)
    if ordered_code:
        findings.append({"code": ordered_code, "message": "tasks not numbered and strictly increasing"})

    file_code = _check_file_targets(tasks)
    if file_code:
        findings.append({"code": file_code, "message": "task missing concrete file targets"})

    validation_code = _check_validation(tasks)
    if validation_code:
        findings.append({"code": validation_code, "message": "task missing validation command or gap"})

    git_code = _check_git_mutation(text)
    if git_code:
        findings.append({"code": git_code, "message": "plan contains git mutation instruction"})

    owner_code = _check_execution_owner(text)
    if owner_code:
        findings.append({"code": owner_code, "message": "missing or incorrect execution owner handoff"})

    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_plan.py <plan-path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 2

    findings = validate_plan(path)
    if findings:
        for finding in findings:
            print(f"{finding['code']}: {finding['message']}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
