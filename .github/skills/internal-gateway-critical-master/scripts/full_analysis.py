#!/usr/bin/env python3
"""Strict parser and validator for the full-analysis-v1 critic packet."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping

SCHEMA = "internal-gateway-critical/full-analysis-v1"
ALLOWED_SOURCES = frozenset({"standard", "independent"})
ALLOWED_OUTCOMES = frozenset(
    {
        "accepted",
        "revise-design",
        "reopen-analysis",
        "needs-clarification",
        "invalid-target",
        "request-separate-review",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "source",
        "target_path",
        "target_revision",
        "outcome",
        "findings",
        "residual_risks",
        "diagnostics",
    }
)
FINDING_KEYS = frozenset(
    {"id", "critique", "recommendation", "reason", "blocking", "evidence"}
)
FINDING_ID_PATTERN = re.compile(r"^C-[0-9]{3}$")


@dataclass(frozen=True)
class FullFinding:
    id: str
    critique: str
    recommendation: str
    reason: str
    blocking: bool
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class FullAnalysisResult:
    schema: str | None
    source: str | None
    target_path: str | None
    target_revision: int | None
    outcome: str
    findings: tuple[FullFinding, ...]
    residual_risks: tuple[str, ...]
    diagnostics: tuple[str, ...]


def _invalid_result(
    diagnostics: list[str], *, payload: Mapping[str, Any] | None = None
) -> FullAnalysisResult:
    payload = payload or {}
    revision = payload.get("target_revision")
    return FullAnalysisResult(
        schema=payload.get("schema") if isinstance(payload.get("schema"), str) else None,
        source=payload.get("source") if isinstance(payload.get("source"), str) else None,
        target_path=(
            payload.get("target_path")
            if isinstance(payload.get("target_path"), str)
            else None
        ),
        target_revision=revision if type(revision) is int else None,
        outcome="invalid-target",
        findings=(),
        residual_risks=(),
        diagnostics=tuple(dict.fromkeys(diagnostics)),
    )


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_array(value: object, name: str, diagnostics: list[str]) -> tuple[str, ...]:
    if not isinstance(value, list):
        diagnostics.append(f"{name} must be an array")
        return ()
    if any(not _non_empty_string(item) for item in value):
        diagnostics.append(f"{name} must contain non-empty strings")
    values = tuple(item.strip() for item in value if _non_empty_string(item))
    if len(set(values)) != len(values):
        diagnostics.append(f"{name} must not contain duplicates")
    return values


def _valid_repository_path(value: object) -> bool:
    if not isinstance(value, str) or not value or value.startswith("/"):
        return False
    if "\\" in value:
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and ".." not in parts


def _parse_findings(value: object, diagnostics: list[str]) -> tuple[FullFinding, ...]:
    if not isinstance(value, list):
        diagnostics.append("findings must be an array")
        return ()

    findings: list[FullFinding] = []
    finding_ids: set[str] = set()
    for index, item in enumerate(value):
        prefix = f"findings[{index}]"
        if not isinstance(item, dict):
            diagnostics.append(f"{prefix} must be an object")
            continue

        keys = set(item)
        missing = FINDING_KEYS - keys
        unknown = keys - FINDING_KEYS
        if missing:
            diagnostics.append(f"{prefix} missing keys: {sorted(missing)}")
        if unknown:
            diagnostics.append(f"{prefix} has unknown keys: {sorted(unknown)}")

        finding_id = item.get("id")
        if not isinstance(finding_id, str) or not FINDING_ID_PATTERN.fullmatch(finding_id):
            diagnostics.append(f"{prefix}.id must match C-000 format")
        elif finding_id in finding_ids:
            diagnostics.append(f"duplicate finding id: {finding_id}")
        else:
            finding_ids.add(finding_id)

        text_values: dict[str, str] = {}
        for key in ("critique", "recommendation", "reason"):
            value_for_key = item.get(key)
            if not _non_empty_string(value_for_key):
                diagnostics.append(f"{prefix}.{key} must be a non-empty string")
            else:
                assert isinstance(value_for_key, str)
                text_values[key] = value_for_key.strip()

        blocking = item.get("blocking")
        if type(blocking) is not bool:
            diagnostics.append(f"{prefix}.blocking must be a boolean")

        evidence = _string_array(item.get("evidence"), f"{prefix}.evidence", diagnostics)
        if (
            isinstance(finding_id, str)
            and FINDING_ID_PATTERN.fullmatch(finding_id)
            and len(text_values) == 3
            and type(blocking) is bool
            and evidence
        ):
            findings.append(
                FullFinding(
                    id=finding_id,
                    critique=text_values["critique"],
                    recommendation=text_values["recommendation"],
                    reason=text_values["reason"],
                    blocking=blocking,
                    evidence=evidence,
                )
            )
    return tuple(findings)


def _check_outcome_invariants(
    outcome: object,
    source: object,
    findings: tuple[FullFinding, ...],
    packet_diagnostics: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    blockers = tuple(finding for finding in findings if finding.blocking)
    if outcome == "accepted":
        if blockers:
            errors.append("accepted cannot contain a blocking finding")
        if packet_diagnostics:
            errors.append("accepted must have empty diagnostics")
    elif outcome == "revise-design" and not findings:
        errors.append("revise-design requires at least one finding")
    elif outcome == "reopen-analysis" and not blockers:
        errors.append("reopen-analysis requires a blocking finding")
    elif outcome == "needs-clarification":
        clarification_text = " ".join(
            f"{finding.critique} {finding.reason}" for finding in blockers
        ).lower()
        if not blockers or not any(
            marker in clarification_text
            for marker in ("user decision", "unresolved", "clarif")
        ):
            errors.append(
                "needs-clarification requires a blocker tied to an unresolved user decision"
            )
    elif outcome == "invalid-target" and not packet_diagnostics:
        errors.append("invalid-target requires diagnostics")
    elif outcome == "request-separate-review":
        if source != "independent":
            errors.append("request-separate-review requires independent source")
        if not packet_diagnostics:
            errors.append("request-separate-review requires diagnostics")
    return errors


def validate_full_analysis_packet(
    payload: object, *, expected_target_path: str, expected_revision: int
) -> tuple[str, ...]:
    diagnostics: list[str] = []
    if not isinstance(payload, dict):
        return ("packet must be a JSON object",)

    keys = set(payload)
    missing = TOP_LEVEL_KEYS - keys
    unknown = keys - TOP_LEVEL_KEYS
    if missing:
        diagnostics.append(f"packet missing keys: {sorted(missing)}")
    if unknown:
        diagnostics.append(f"packet has unknown keys: {sorted(unknown)}")

    if payload.get("schema") != SCHEMA:
        diagnostics.append(f"schema must be {SCHEMA}")

    source = payload.get("source")
    if source not in ALLOWED_SOURCES:
        diagnostics.append("source must be standard or independent")

    target_path = payload.get("target_path")
    if not _valid_repository_path(target_path):
        diagnostics.append("target_path must be a repository-relative POSIX path")
    elif target_path != expected_target_path:
        diagnostics.append("target_path does not match the expected target")

    target_revision = payload.get("target_revision")
    if type(target_revision) is not int or target_revision <= 0:
        diagnostics.append("target_revision must be a positive integer")
    elif target_revision != expected_revision:
        diagnostics.append("target_revision does not match the expected revision")

    outcome = payload.get("outcome")
    if outcome not in ALLOWED_OUTCOMES:
        diagnostics.append("outcome is not a supported full-analysis outcome")

    findings = _parse_findings(payload.get("findings"), diagnostics)
    _string_array(payload.get("residual_risks"), "residual_risks", diagnostics)
    packet_diagnostics = _string_array(
        payload.get("diagnostics"), "diagnostics", diagnostics
    )
    diagnostics.extend(
        _check_outcome_invariants(outcome, source, findings, packet_diagnostics)
    )
    return tuple(dict.fromkeys(diagnostics))


def parse_full_analysis_packet(
    payload: str, *, expected_target_path: str, expected_revision: int
) -> FullAnalysisResult:
    if "```" in payload:
        return _invalid_result(["Markdown fences are not valid JSON packets"])
    try:
        decoded = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as error:
        message = error.msg if hasattr(error, "msg") else str(error)
        return _invalid_result([f"invalid JSON: {message}"])

    diagnostics = validate_full_analysis_packet(
        decoded,
        expected_target_path=expected_target_path,
        expected_revision=expected_revision,
    )
    if diagnostics:
        return _invalid_result(
            list(diagnostics), payload=decoded if isinstance(decoded, dict) else None
        )

    assert isinstance(decoded, dict)
    findings = _parse_findings(decoded["findings"], [])
    return FullAnalysisResult(
        schema=decoded["schema"],
        source=decoded["source"],
        target_path=decoded["target_path"],
        target_revision=decoded["target_revision"],
        outcome=decoded["outcome"],
        findings=findings,
        residual_risks=tuple(decoded["residual_risks"]),
        diagnostics=tuple(decoded["diagnostics"]),
    )


def _result_payload(result: FullAnalysisResult) -> dict[str, object]:
    payload = asdict(result)
    payload["findings"] = [asdict(finding) for finding in result.findings]
    return payload


def _read_payload(file_path: str | None) -> str:
    if file_path is None:
        return sys.stdin.read()
    with open(file_path, encoding="utf-8") as stream:
        return stream.read()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an internal-gateway-critical full-analysis-v1 packet."
    )
    parser.add_argument("--file", help="Packet file; stdin is used when omitted.")
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--revision", required=True, type=int)
    parser.add_argument("--format", choices=("text", "json", "compact"), default="text")
    return parser.parse_args()


def _render(result: FullAnalysisResult, format_name: str) -> None:
    if format_name == "json":
        print(json.dumps(_result_payload(result), ensure_ascii=False, indent=2))
        return
    if format_name == "compact":
        print(
            json.dumps(
                {
                    "status": "ok" if result.outcome != "invalid-target" else "failed",
                    "outcome": result.outcome,
                    "finding_count": len(result.findings),
                    "diagnostic_count": len(result.diagnostics),
                },
                ensure_ascii=False,
            )
        )
        return
    if result.outcome == "invalid-target":
        for diagnostic in result.diagnostics:
            print(f"[INVALID] {diagnostic}")
    else:
        print(
            f"[VALID] outcome={result.outcome} findings={len(result.findings)}"
        )


def main() -> int:
    args = _parse_args()
    try:
        payload = _read_payload(args.file)
    except OSError as error:
        print(f"cannot read packet: {error}", file=sys.stderr)
        return 2

    result = parse_full_analysis_packet(
        payload,
        expected_target_path=args.target_path,
        expected_revision=args.revision,
    )
    _render(result, args.format)
    return 1 if result.outcome == "invalid-target" else 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ALLOWED_OUTCOMES",
    "ALLOWED_SOURCES",
    "FINDING_ID_PATTERN",
    "FullAnalysisResult",
    "FullFinding",
    "parse_full_analysis_packet",
    "validate_full_analysis_packet",
]
