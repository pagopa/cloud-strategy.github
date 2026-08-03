#!/usr/bin/env python3
"""Validate and load the versioned Wayfinder report model."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class ModelError(ValueError):
    """Raised when a report model cannot be safely consumed."""


@dataclass(frozen=True)
class SourceRef:
    path: str
    excerpt: str


@dataclass(frozen=True)
class Claim:
    text: str
    sources: tuple[SourceRef, ...]


@dataclass(frozen=True)
class Summary:
    specification: Claim
    problem: Claim
    decision: Claim
    expected_result: Claim


@dataclass(frozen=True)
class Behavior:
    title: str
    claim: Claim


@dataclass(frozen=True)
class Scope:
    included: tuple[Claim, ...]
    excluded: tuple[Claim, ...]


@dataclass(frozen=True)
class DecisionPathEntry:
    title: str
    state: str
    claim: Claim


@dataclass(frozen=True)
class Implementation:
    specified: tuple[Claim, ...]
    implemented: tuple[Claim, ...]


@dataclass(frozen=True)
class Diagram:
    title: str
    kind: str
    mermaid: str
    claim: Claim


@dataclass(frozen=True)
class Understand:
    summary: Summary
    operation: Claim
    behaviors: tuple[Behavior, ...]
    rules: tuple[Claim, ...]
    scope: Scope
    decision_path: tuple[DecisionPathEntry, ...]
    implementation: Implementation
    diagrams: tuple[Diagram, ...]


@dataclass(frozen=True)
class Finding:
    id: str
    type: str
    certainty: str
    impact_level: str
    propagation: int
    evidence: tuple[SourceRef, ...]
    interpretation: Claim
    specification_impact: Claim
    repair: Claim
    copyable_request: Claim


@dataclass(frozen=True)
class Review:
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class ReportModel:
    schema_version: int
    analysis_slug: str
    title: str
    status: str
    destination: Claim
    understand: Understand
    review: Review


IMPACT_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
CERTAINTY_RANK = {"confirmed": 0, "probable": 1, "to-verify": 2}
REPORT_STATUSES = {
    "analysis-in-progress",
    "ready-for-execution",
    "implemented",
    "unknown",
}
FINDING_TYPES = {
    "contradiction",
    "superseded-decision",
    "missing-dependency",
    "stale-map",
    "ambiguity",
}
DECISION_STATES = {"resolved", "open", "not-specified"}
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _error(label: str, message: str) -> ModelError:
    return ModelError(f"{label}: {message}")


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise _error(label, "must be an object")
    return value


def _exact_fields(value: Mapping[str, object], expected: set[str], label: str) -> None:
    actual = set(value)
    unknown = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unknown or missing:
        details: list[str] = []
        if unknown:
            details.append(f"unknown fields {unknown}")
        if missing:
            details.append(f"missing fields {missing}")
        raise _error(label, "; ".join(details))


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error(label, "must be a non-empty string")
    return value


def _enum(value: object, label: str, allowed: set[str]) -> str:
    result = _string(value, label)
    if result not in allowed:
        raise _error(label, f"must be one of {sorted(allowed)}")
    return result


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise _error(label, "must be a list")
    return value


def _workspace_root(workspace: Path) -> Path:
    try:
        root = workspace.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise _error("workspace", f"cannot be resolved: {exc}") from exc
    if not root.is_dir():
        raise _error("workspace", "must be an existing directory")
    return root


def _source_ref(value: object, workspace: Path, label: str) -> SourceRef:
    item = _mapping(value, label)
    _exact_fields(item, {"path", "excerpt"}, label)
    path = _string(item["path"], f"{label}.path")
    excerpt = _string(item["excerpt"], f"{label}.excerpt")
    _validate_source_path(path, workspace, f"{label}.path")
    return SourceRef(path=path, excerpt=excerpt)


def _validate_source_path(path: str, workspace: Path, label: str) -> Path:
    if "\x00" in path:
        raise _error(label, "contains a NUL byte and is outside the workspace")
    if URI_SCHEME_RE.match(path) or "://" in path:
        raise _error(label, f"must resolve inside the workspace: {path!r}")
    normalized_components = path.replace("\\", "/").split("/")
    if ".." in normalized_components:
        raise _error(label, f"must resolve inside the workspace: {path!r}")
    try:
        candidate_path = Path(path)
        if candidate_path.is_absolute():
            raise _error(label, f"must resolve inside the workspace: {path!r}")
        resolved = (workspace / candidate_path).resolve()
    except ModelError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise _error(label, f"cannot resolve inside the workspace: {exc}") from exc
    if resolved != workspace and workspace not in resolved.parents:
        raise _error(label, f"must resolve inside the workspace: {path!r}")
    if not resolved.is_file():
        raise _error(label, f"must resolve to a regular file in the workspace: {path!r}")
    return resolved


def _sources(value: object, workspace: Path, label: str) -> tuple[SourceRef, ...]:
    values = _list(value, label)
    if not values:
        raise _error(label, "must contain at least one source")
    return tuple(
        _source_ref(item, workspace, f"{label}[{index}]")
        for index, item in enumerate(values)
    )


def _claim(value: object, workspace: Path, label: str) -> Claim:
    item = _mapping(value, label)
    _exact_fields(item, {"text", "sources"}, label)
    return Claim(
        text=_string(item["text"], f"{label}.text"),
        sources=_sources(item["sources"], workspace, f"{label}.sources"),
    )


def _claims(value: object, workspace: Path, label: str) -> tuple[Claim, ...]:
    return tuple(
        _claim(item, workspace, f"{label}[{index}]")
        for index, item in enumerate(_list(value, label))
    )


def _summary(value: object, workspace: Path) -> Summary:
    item = _mapping(value, "understand.summary")
    expected = {"specification", "problem", "decision", "expected_result"}
    _exact_fields(item, expected, "understand.summary")
    return Summary(
        specification=_claim(item["specification"], workspace, "understand.summary.specification"),
        problem=_claim(item["problem"], workspace, "understand.summary.problem"),
        decision=_claim(item["decision"], workspace, "understand.summary.decision"),
        expected_result=_claim(
            item["expected_result"], workspace, "understand.summary.expected_result"
        ),
    )


def _behaviors(value: object, workspace: Path) -> tuple[Behavior, ...]:
    result: list[Behavior] = []
    for index, raw_behavior in enumerate(_list(value, "understand.behaviors")):
        label = f"understand.behaviors[{index}]"
        item = _mapping(raw_behavior, label)
        _exact_fields(item, {"title", "claim"}, label)
        result.append(
            Behavior(
                title=_string(item["title"], f"{label}.title"),
                claim=_claim(item["claim"], workspace, f"{label}.claim"),
            )
        )
    return tuple(result)


def _scope(value: object, workspace: Path) -> Scope:
    item = _mapping(value, "understand.scope")
    _exact_fields(item, {"included", "excluded"}, "understand.scope")
    return Scope(
        included=_claims(item["included"], workspace, "understand.scope.included"),
        excluded=_claims(item["excluded"], workspace, "understand.scope.excluded"),
    )


def _decision_path(value: object, workspace: Path) -> tuple[DecisionPathEntry, ...]:
    result: list[DecisionPathEntry] = []
    for index, raw_entry in enumerate(_list(value, "understand.decision_path")):
        label = f"understand.decision_path[{index}]"
        item = _mapping(raw_entry, label)
        _exact_fields(item, {"title", "state", "claim"}, label)
        result.append(
            DecisionPathEntry(
                title=_string(item["title"], f"{label}.title"),
                state=_enum(item["state"], f"{label}.state", DECISION_STATES),
                claim=_claim(item["claim"], workspace, f"{label}.claim"),
            )
        )
    return tuple(result)


def _implementation(value: object, workspace: Path) -> Implementation:
    item = _mapping(value, "understand.implementation")
    _exact_fields(item, {"specified", "implemented"}, "understand.implementation")
    return Implementation(
        specified=_claims(item["specified"], workspace, "understand.implementation.specified"),
        implemented=_claims(item["implemented"], workspace, "understand.implementation.implemented"),
    )


def _diagrams(value: object, workspace: Path) -> tuple[Diagram, ...]:
    result: list[Diagram] = []
    for index, raw_diagram in enumerate(_list(value, "understand.diagrams")):
        label = f"understand.diagrams[{index}]"
        item = _mapping(raw_diagram, label)
        _exact_fields(item, {"title", "kind", "mermaid", "claim"}, label)
        result.append(
            Diagram(
                title=_string(item["title"], f"{label}.title"),
                kind=_string(item["kind"], f"{label}.kind"),
                mermaid=_string(item["mermaid"], f"{label}.mermaid"),
                claim=_claim(item["claim"], workspace, f"{label}.claim"),
            )
        )
    return tuple(result)


def _understand(value: object, workspace: Path) -> Understand:
    item = _mapping(value, "understand")
    expected = {
        "summary",
        "operation",
        "behaviors",
        "rules",
        "scope",
        "decision_path",
        "implementation",
        "diagrams",
    }
    _exact_fields(item, expected, "understand")
    return Understand(
        summary=_summary(item["summary"], workspace),
        operation=_claim(item["operation"], workspace, "understand.operation"),
        behaviors=_behaviors(item["behaviors"], workspace),
        rules=_claims(item["rules"], workspace, "understand.rules"),
        scope=_scope(item["scope"], workspace),
        decision_path=_decision_path(item["decision_path"], workspace),
        implementation=_implementation(item["implementation"], workspace),
        diagrams=_diagrams(item["diagrams"], workspace),
    )


def _finding(value: object, workspace: Path, label: str) -> Finding:
    item = _mapping(value, label)
    expected = {
        "id",
        "type",
        "certainty",
        "impact_level",
        "propagation",
        "evidence",
        "interpretation",
        "specification_impact",
        "repair",
        "copyable_request",
    }
    _exact_fields(item, expected, label)
    propagation = item["propagation"]
    if isinstance(propagation, bool) or not isinstance(propagation, int) or propagation < 0:
        raise _error(f"{label}.propagation", "must be a non-negative integer")
    return Finding(
        id=_string(item["id"], f"{label}.id"),
        type=_enum(item["type"], f"{label}.type", FINDING_TYPES),
        certainty=_enum(item["certainty"], f"{label}.certainty", CERTAINTY_RANK.keys()),
        impact_level=_enum(item["impact_level"], f"{label}.impact_level", IMPACT_RANK.keys()),
        propagation=propagation,
        evidence=_sources(item["evidence"], workspace, f"{label}.evidence"),
        interpretation=_claim(item["interpretation"], workspace, f"{label}.interpretation"),
        specification_impact=_claim(
            item["specification_impact"], workspace, f"{label}.specification_impact"
        ),
        repair=_claim(item["repair"], workspace, f"{label}.repair"),
        copyable_request=_claim(
            item["copyable_request"], workspace, f"{label}.copyable_request"
        ),
    )


def _review(value: object, workspace: Path) -> Review:
    item = _mapping(value, "review")
    _exact_fields(item, {"findings"}, "review")
    findings = tuple(
        _finding(raw_finding, workspace, f"review.findings[{index}]")
        for index, raw_finding in enumerate(_list(item["findings"], "review.findings"))
    )
    ids = [finding.id for finding in findings]
    if len(ids) != len(set(ids)):
        raise _error("review.findings", "ids must be unique")
    return Review(findings=findings)


def load_payload(payload: object, workspace: Path) -> ReportModel:
    """Validate a decoded v1 payload against an active workspace."""

    workspace_root = _workspace_root(workspace)
    item = _mapping(payload, "report model")
    expected = {
        "schema_version",
        "analysis_slug",
        "title",
        "status",
        "destination",
        "understand",
        "review",
    }
    _exact_fields(item, expected, "report model")
    if item["schema_version"] != 1:
        raise _error("schema_version", "must be 1")
    return ReportModel(
        schema_version=1,
        analysis_slug=_string(item["analysis_slug"], "analysis_slug"),
        title=_string(item["title"], "title"),
        status=_enum(item["status"], "status", REPORT_STATUSES),
        destination=_claim(item["destination"], workspace_root, "destination"),
        understand=_understand(item["understand"], workspace_root),
        review=_review(item["review"], workspace_root),
    )


def load_report_model(model_path: Path, workspace: Path) -> ReportModel:
    """Read and strictly validate a report model JSON file."""

    try:
        payload = json.loads(model_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _error("model", f"cannot read valid UTF-8 JSON: {exc}") from exc
    return load_payload(payload, workspace)


def finding_sort_key(finding: Finding) -> tuple[int, int, int, str]:
    return (
        IMPACT_RANK[finding.impact_level],
        CERTAINTY_RANK[finding.certainty],
        -finding.propagation,
        finding.id,
    )


def rank_findings(findings: tuple[Finding, ...]) -> tuple[Finding, ...]:
    """Return every finding in deterministic priority order."""

    return tuple(sorted(findings, key=finding_sort_key))
