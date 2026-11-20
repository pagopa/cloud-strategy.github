#!/usr/bin/env python3
"""Check that an internal-tdd posture record supports its completion state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

FIELD_ORDER = ("posture", "boundary", "checks", "state", "gaps")
POSTURES = frozenset(
    {"mandatory-test-first", "feature-first", "prototype-unverified", "validation-only"}
)
STATE_POSTURE = {
    "test-first-validated": "mandatory-test-first",
    "feature-first-validated": "feature-first",
    "prototype-unverified": "prototype-unverified",
    "validation-only": "validation-only",
    "blocked": None,
}
PHASES = frozenset({"red", "characterization", "focused", "broader"})
VALIDATED = ("test-first-validated", "feature-first-validated")
CHANGE_KINDS = {"behavior": "red", "refactor": "characterization"}
# A red run that fails for these reasons proves a broken harness, not missing behavior.
ERROR_MARKERS = (
    "modulenotfounderror",
    "importerror",
    "syntaxerror",
    "nameerror",
    "collection error",
    "command not found",
)


def _outcome(result: str) -> str:
    text = result.strip().lower()
    if text.startswith("passed"):
        return "passed"
    if text.startswith("errored") or (
        text.startswith("failed") and any(marker in text for marker in ERROR_MARKERS)
    ):
        return "errored"
    if text.startswith("failed"):
        return "failed"
    return "unobserved"


def _schema_errors(record: dict[str, Any]) -> list[str]:
    errors = []
    posture = record["posture"]
    if not isinstance(posture, dict) or not isinstance(posture.get("value"), str):
        errors.append("`posture` must be an object with a string `value`.")
    if not isinstance(record["boundary"], dict):
        errors.append("`boundary` must be an object.")
    checks = record["checks"]
    if not isinstance(checks, list) or not all(
        isinstance(item, dict)
        and all(isinstance(item.get(key), str) for key in ("phase", "command", "result"))
        for item in checks
    ):
        errors.append("`checks` must be a list of objects with string phase, command, result.")
    if not isinstance(record["state"], str):
        errors.append("`state` must be a string.")
    if not isinstance(record["gaps"], str):
        errors.append("`gaps` must be a string.")
    return errors


def check(record: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        findings.append({"code": code, "message": message})

    if not isinstance(record, dict):
        add("schema", "The record must be a JSON object.")
        return findings
    if tuple(record) != FIELD_ORDER:
        add("field-order", f"Fields must be exactly {', '.join(FIELD_ORDER)} in that order.")
        if not set(FIELD_ORDER) <= set(record):
            return findings
    schema_errors = _schema_errors(record)
    for message in schema_errors:
        add("schema", message)
    if schema_errors:
        return findings

    posture = record["posture"]["value"]
    if posture not in POSTURES:
        add("unknown-posture", f"Unknown posture: {posture!r}.")
    state = record["state"]
    if state not in STATE_POSTURE:
        add("unknown-state", f"Unknown completion state: {state!r}.")
    elif STATE_POSTURE[state] not in (None, posture):
        add("state-posture-mismatch", f"State {state} does not belong to posture {posture}.")

    phases: list[str] = []
    results: dict[str, str] = {}
    pre_existing = False
    for item in record["checks"]:
        phase = item["phase"]
        if phase not in PHASES:
            add("unknown-phase", f"Unknown check phase: {phase!r}.")
            continue
        if phase in results:
            add("duplicate-phase", f"The {phase} phase appears more than once.")
            continue
        phases.append(phase)
        results[phase] = _outcome(item["result"])
        if "scope" in item:
            if item["scope"] != "pre-existing" or phase != "broader":
                add("invalid-scope", "Only a broader check may set scope to `pre-existing`.")
            elif results[phase] == "failed":
                pre_existing = True
        if state in VALIDATED and results[phase] == "unobserved":
            add("unobserved-check", f"The {phase} check has no observed result.")

    if state in VALIDATED:
        for phase in ("focused", "broader"):
            if results.get(phase) != "passed" and not (phase == "broader" and pre_existing):
                add("validation-not-passed", f"A validated state needs a passing {phase} check.")

    if posture == "mandatory-test-first":
        change = record["posture"].get("change")
        if change not in CHANGE_KINDS:
            add("missing-change-kind", "Set posture.change to `behavior` or `refactor`.")
        elif state == "test-first-validated":
            required = CHANGE_KINDS[change]
            other = "characterization" if required == "red" else "red"
            if other in results:
                add("proof-kind", f"A {change} change needs a {required} check, not {other}.")
            if required not in results:
                add("missing-proof-check", f"A {change} change needs a {required} check.")
            else:
                expected = "failed" if required == "red" else "passed"
                if results[required] != expected:
                    add("proof-check-result", f"The {required} check must be {expected}.")
                if "focused" in phases and phases.index(required) > phases.index("focused"):
                    add("proof-order", f"The {required} check must precede the focused check.")

    gaps = record["gaps"].strip()
    needs_gaps = state in ("blocked", "prototype-unverified", "validation-only") or pre_existing
    if needs_gaps and gaps.lower() in ("", "none"):
        add("missing-gaps", f"State {state} must name the missing evidence and next action.")
    if state == "validation-only" and "focused" not in results:
        add("missing-alternate-check", "Record the alternate validator as a focused check.")
    if state == "blocked" and all(
        outcome == "passed" for phase, outcome in results.items() if phase != "red"
    ):
        add("blocked-without-failure", "A blocked record needs a failing or unobserved check.")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="Posture record JSON file.")
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings = [{"code": "invalid-json", "message": str(exc)}]
    else:
        findings = check(record)
    print(json.dumps({"status": "fail" if findings else "ok", "findings": findings}))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
