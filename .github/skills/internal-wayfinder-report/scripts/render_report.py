#!/usr/bin/env python3
"""Render a generic, evidence-backed Wayfinder report into one HTML page."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import string
import sys
import tempfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple


BUNDLE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = BUNDLE_ROOT / "templates" / "report.html"
SECTION_IDS = ("overview", "solution", "decisions", "scope", "review")
BLOCK_KINDS = ("claim", "list", "comparison", "decision-board", "diagram")
DECISION_STATES = ("resolved", "open", "not-specified")
IMPACT_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
CERTAINTY_RANK = {"confirmed": 0, "probable": 1, "to-verify": 2}
REQUIRED_PLACEHOLDERS = frozenset(
    {
        "title",
        "slug",
        "status_label",
        "generated_at",
        "destination",
        "metrics",
        "priorities",
        "body",
    }
)
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class ReportError(ValueError):
    """Raised when report input cannot be rendered safely."""


class ResolvedEvidence(NamedTuple):
    path: Path
    label: str
    excerpt: str


def _error(location: str, message: str) -> ReportError:
    return ReportError(f"{location}: {message}")


def _mapping(value: object, location: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise _error(location, "must be an object")
    return value


def _list(value: object, location: str) -> list[object]:
    if not isinstance(value, list):
        raise _error(location, "must be a list")
    return value


def _string(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error(location, "must be a non-empty string")
    return value


def _enum(value: object, location: str, allowed: tuple[str, ...]) -> str:
    result = _string(value, location)
    if result not in allowed:
        raise _error(location, f"must be one of {list(allowed)}")
    return result


def _exact_fields(
    value: Mapping[str, object],
    required: set[str],
    location: str,
    optional: set[str] | None = None,
) -> None:
    allowed = required | (optional or set())
    actual = set(value)
    unknown = sorted(actual - allowed)
    missing = sorted(required - actual)
    if unknown or missing:
        details: list[str] = []
        if unknown:
            details.append(f"unknown fields {unknown}")
        if missing:
            details.append(f"missing fields {missing}")
        raise _error(location, "; ".join(details))


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_workspace(workspace: Path) -> Path:
    try:
        root = workspace.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise _error("workspace", f"cannot be resolved: {exc}") from exc
    if not root.is_dir():
        raise _error("workspace", "must be an existing directory")
    for required_name in ("map.md", "analysis.md"):
        required_path = root / required_name
        try:
            resolved = required_path.resolve()
        except (OSError, RuntimeError, ValueError) as exc:
            raise _error(required_name, f"cannot be resolved: {exc}") from exc
        if not _within(resolved, root) or not resolved.is_file():
            raise _error("workspace", f"is missing required file: {required_name}")
    return root


def _resolve_report_dir(workspace: Path) -> Path:
    candidate = workspace / "report"
    if candidate.exists() and not candidate.is_dir():
        raise _error("report", "must be a directory")
    try:
        candidate.mkdir(exist_ok=True)
        report_dir = candidate.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise _error("report", f"cannot be prepared: {exc}") from exc
    if not _within(report_dir, workspace):
        raise _error("report", "must resolve inside the workspace")
    return report_dir


def _resolve_data_path(data_path: Path, report_dir: Path) -> Path:
    try:
        resolved = data_path.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise _error("data", f"cannot be resolved below report: {exc}") from exc
    if not _within(resolved, report_dir) or resolved == report_dir or not resolved.is_file():
        raise _error("data", "must be a file below the report directory")
    return resolved


def _resolve_source_path(path: str, workspace: Path, location: str) -> Path:
    if "\x00" in path:
        raise _error(location, "must resolve to a regular file inside the workspace")
    if URI_SCHEME_RE.match(path) or "://" in path:
        raise _error(location, f"must resolve inside the workspace: {path!r}")
    normalized = path.replace("\\", "/").split("/")
    if ".." in normalized:
        raise _error(location, f"must resolve inside the workspace: {path!r}")
    try:
        candidate = Path(path)
        if candidate.is_absolute():
            raise _error(location, f"must resolve inside the workspace: {path!r}")
        resolved = (workspace / candidate).resolve()
    except ReportError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise _error(location, f"cannot resolve inside the workspace: {exc}") from exc
    if not _within(resolved, workspace) or not resolved.is_file():
        raise _error(
            location,
            f"must resolve to a regular file inside the workspace: {path!r}",
        )
    return resolved


def _load_evidence(
    value: object, workspace: Path
) -> dict[str, ResolvedEvidence]:
    entries = _mapping(value, "evidence")
    if not entries:
        raise _error("evidence", "must contain at least one entry")
    resolved: dict[str, ResolvedEvidence] = {}
    source_cache: dict[Path, str] = {}
    registry: set[tuple[Path, str]] = set()
    for evidence_id, raw_entry in entries.items():
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise _error("evidence", "ids must be non-empty strings")
        location = f"evidence[{evidence_id!r}]"
        entry = _mapping(raw_entry, location)
        _exact_fields(entry, {"path", "excerpt"}, location)
        source_path = _string(entry["path"], f"{location}.path")
        excerpt = _string(entry["excerpt"], f"{location}.excerpt")
        if "\n" in excerpt or "\r" in excerpt:
            raise _error(
                f"{location}.excerpt", "must be one physical line without line breaks"
            )
        resolved_path = _resolve_source_path(source_path, workspace, f"{location}.path")
        registry_key = (resolved_path, excerpt)
        if registry_key in registry:
            raise _error(location, "duplicate (path, excerpt) evidence entry")
        registry.add(registry_key)
        if resolved_path not in source_cache:
            try:
                source_cache[resolved_path] = resolved_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise _error(location, f"source cannot be read as UTF-8: {exc}") from exc
        source_text = source_cache[resolved_path]
        if source_text.count(excerpt) != 1:
            raise _error(location, "excerpt must occur exactly once in its declared source")
        resolved[evidence_id] = ResolvedEvidence(resolved_path, source_path, excerpt)
    return resolved


def _evidence_ids(
    value: object,
    evidence: dict[str, ResolvedEvidence],
    location: str,
) -> tuple[str, ...]:
    values = _list(value, location)
    if not values:
        raise _error(location, "must contain at least one evidence id")
    result: list[str] = []
    for index, raw_id in enumerate(values):
        evidence_id = _string(raw_id, f"{location}[{index}]")
        if evidence_id not in evidence:
            raise _error(f"{location}[{index}]", f"unknown evidence id {evidence_id!r}")
        result.append(evidence_id)
    return tuple(result)


def _claim(
    value: object,
    evidence: dict[str, ResolvedEvidence],
    location: str,
) -> dict[str, object]:
    item = _mapping(value, location)
    _exact_fields(item, {"text", "evidence"}, location)
    return {
        "text": _string(item["text"], f"{location}.text"),
        "evidence": _evidence_ids(item["evidence"], evidence, f"{location}.evidence"),
    }


def _claim_item(
    value: object,
    evidence: dict[str, ResolvedEvidence],
    location: str,
) -> dict[str, object]:
    return _claim(value, evidence, location)


def _list_items(
    value: object,
    evidence: dict[str, ResolvedEvidence],
    location: str,
) -> tuple[dict[str, object], ...]:
    return tuple(
        _claim_item(item, evidence, f"{location}[{index}]")
        for index, item in enumerate(_list(value, location))
    )


def _comparison_side(
    value: object,
    evidence: dict[str, ResolvedEvidence],
    location: str,
) -> dict[str, object]:
    item = _mapping(value, location)
    _exact_fields(item, {"title", "items"}, location)
    return {
        "title": _string(item["title"], f"{location}.title"),
        "items": _list_items(item["items"], evidence, f"{location}.items"),
    }


def _validate_block(
    value: object,
    evidence: dict[str, ResolvedEvidence],
    location: str,
) -> dict[str, object]:
    item = _mapping(value, location)
    kind = _enum(item.get("kind"), f"{location}.kind", BLOCK_KINDS)
    if kind == "claim":
        _exact_fields(item, {"kind", "title", "text", "evidence"}, location)
        return {
            "kind": kind,
            "title": _string(item["title"], f"{location}.title"),
            "text": _string(item["text"], f"{location}.text"),
            "evidence": _evidence_ids(item["evidence"], evidence, f"{location}.evidence"),
        }
    if kind == "list":
        _exact_fields(item, {"kind", "title", "items"}, location)
        return {
            "kind": kind,
            "title": _string(item["title"], f"{location}.title"),
            "items": _list_items(item["items"], evidence, f"{location}.items"),
        }
    if kind == "comparison":
        _exact_fields(item, {"kind", "title", "left", "right"}, location)
        return {
            "kind": kind,
            "title": _string(item["title"], f"{location}.title"),
            "left": _comparison_side(item["left"], evidence, f"{location}.left"),
            "right": _comparison_side(item["right"], evidence, f"{location}.right"),
        }
    if kind == "decision-board":
        _exact_fields(item, {"kind", "title", "decisions"}, location)
        decisions: list[dict[str, object]] = []
        for index, raw_decision in enumerate(_list(item["decisions"], f"{location}.decisions")):
            decision_location = f"{location}.decisions[{index}]"
            decision = _mapping(raw_decision, decision_location)
            _exact_fields(
                decision,
                {"title", "state", "text", "evidence"},
                decision_location,
            )
            decisions.append(
                {
                    "title": _string(decision["title"], f"{decision_location}.title"),
                    "state": _enum(
                        decision["state"], f"{decision_location}.state", DECISION_STATES
                    ),
                    "text": _string(decision["text"], f"{decision_location}.text"),
                    "evidence": _evidence_ids(
                        decision["evidence"],
                        evidence,
                        f"{decision_location}.evidence",
                    ),
                }
            )
        return {
            "kind": kind,
            "title": _string(item["title"], f"{location}.title"),
            "decisions": tuple(decisions),
        }
    _exact_fields(item, {"kind", "title", "diagram_type", "source", "claim"}, location)
    return {
        "kind": kind,
        "title": _string(item["title"], f"{location}.title"),
        "diagram_type": _string(item["diagram_type"], f"{location}.diagram_type"),
        "source": _string(item["source"], f"{location}.source"),
        "claim": _claim(item["claim"], evidence, f"{location}.claim"),
    }


def _validate_sections(
    value: object,
    evidence: dict[str, ResolvedEvidence],
) -> dict[str, dict[str, object]]:
    sections = _mapping(value, "sections")
    _exact_fields(sections, set(SECTION_IDS), "sections")
    validated: dict[str, dict[str, object]] = {}
    for section_id in SECTION_IDS:
        location = f"sections.{section_id}"
        section = _mapping(sections[section_id], location)
        _exact_fields(section, {"title", "blocks"}, location, {"lede"})
        blocks = tuple(
            _validate_block(item, evidence, f"{location}.blocks[{index}]" )
            for index, item in enumerate(_list(section["blocks"], f"{location}.blocks"))
        )
        validated[section_id] = {
            "title": _string(section["title"], f"{location}.title"),
            "lede": _string(section["lede"], f"{location}.lede")
            if "lede" in section
            else "",
            "blocks": blocks,
        }
    for section_id in ("overview", "review"):
        if not any(block["kind"] == "diagram" for block in validated[section_id]["blocks"]):
            raise _error(
                f"sections.{section_id}", "must contain at least one diagram block"
            )
    return validated


def _validate_findings(
    value: object,
    evidence: dict[str, ResolvedEvidence],
) -> tuple[dict[str, object], ...]:
    findings: list[dict[str, object]] = []
    ids: set[str] = set()
    for index, raw_finding in enumerate(_list(value, "findings")):
        location = f"findings[{index}]"
        finding = _mapping(raw_finding, location)
        _exact_fields(
            finding,
            {
                "id",
                "title",
                "impact",
                "certainty",
                "propagation",
                "evidence",
                "interpretation",
                "specification_impact",
                "repair",
                "request",
            },
            location,
        )
        finding_id = _string(finding["id"], f"{location}.id")
        if finding_id in ids:
            raise _error("findings", "ids must be unique")
        ids.add(finding_id)
        propagation = finding["propagation"]
        if isinstance(propagation, bool) or not isinstance(propagation, int) or propagation < 0:
            raise _error(f"{location}.propagation", "must be a non-negative integer")
        findings.append(
            {
                "id": finding_id,
                "title": _string(finding["title"], f"{location}.title"),
                "impact": _enum(finding["impact"], f"{location}.impact", tuple(IMPACT_RANK)),
                "certainty": _enum(
                    finding["certainty"], f"{location}.certainty", tuple(CERTAINTY_RANK)
                ),
                "propagation": propagation,
                "evidence": _evidence_ids(finding["evidence"], evidence, f"{location}.evidence"),
                "interpretation": _claim(
                    finding["interpretation"], evidence, f"{location}.interpretation"
                ),
                "specification_impact": _claim(
                    finding["specification_impact"],
                    evidence,
                    f"{location}.specification_impact",
                ),
                "repair": _claim(finding["repair"], evidence, f"{location}.repair"),
                "request": _claim(finding["request"], evidence, f"{location}.request"),
            }
        )
    return tuple(findings)


def load_report_data(data_path: Path, workspace: Path) -> dict[str, object]:
    """Load JSON, validate the closed contract, and resolve exact evidence."""

    workspace_root = _resolve_workspace(workspace)
    report_dir = _resolve_report_dir(workspace_root)
    resolved_data = _resolve_data_path(data_path, report_dir)
    try:
        payload = json.loads(resolved_data.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _error("data", f"cannot read valid UTF-8 JSON: {exc}") from exc
    item = _mapping(payload, "report")
    _exact_fields(
        item,
        {"title", "slug", "status", "destination", "evidence", "sections", "findings"},
        "report",
    )
    evidence = _load_evidence(item["evidence"], workspace_root)
    return {
        "title": _string(item["title"], "title"),
        "slug": _string(item["slug"], "slug"),
        "status": _string(item["status"], "status"),
        "destination": _claim(item["destination"], evidence, "destination"),
        "evidence": evidence,
        "sections": _validate_sections(item["sections"], evidence),
        "findings": _validate_findings(item["findings"], evidence),
        "data_path": resolved_data,
    }


def report_metrics(report: dict[str, object]) -> dict[str, int]:
    """Return bounded section, evidence, finding, and diagram counts."""

    sections = report["sections"]
    diagrams = sum(
        block["kind"] == "diagram"
        for section in sections.values()
        for block in section["blocks"]
    )
    return {
        "sections": len(sections),
        "evidence": len(report["evidence"]),
        "findings": len(report["findings"]),
        "diagrams": diagrams,
    }


def editorial_warnings(metrics: dict[str, int]) -> tuple[str, ...]:
    """Report soft deviations from the compact editorial defaults."""

    warnings: list[str] = []
    evidence_count = metrics["evidence"]
    if evidence_count < 12:
        warnings.append("evidence count is below the editorial default of 12")
    elif evidence_count > 15:
        warnings.append("evidence count exceeds the editorial default of 15")
    if metrics["findings"] > 3:
        warnings.append("finding count exceeds the editorial default of 3")
    if metrics["diagrams"] != 2:
        warnings.append("diagram count differs from the normal editorial default of 2")
    return tuple(warnings)


def validation_summary(report: dict[str, object]) -> dict[str, object]:
    """Return the bounded result shared by validation-only callers."""

    metrics = report_metrics(report)
    return {
        "status": "valid",
        "metrics": metrics,
        "warnings": list(editorial_warnings(metrics)),
    }


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def _text(value: str) -> str:
    return _escape(value).replace("\n", "<br>\n")


def _evidence_links(
    evidence_ids: tuple[str, ...],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    rendered = [
        f'<details class="sources"><summary>Evidence ({len(evidence_ids)})</summary>'
    ]
    for evidence_id in evidence_ids:
        source = evidence[evidence_id]
        href = os.path.relpath(source.path, report_dir).replace(os.sep, "/")
        rendered.append(
            '<div class="source">'
            f'<a class="source-link" href="{_escape(href)}">{_escape(source.label)}</a>'
            f"<blockquote>{_text(source.excerpt)}</blockquote>"
            "</div>"
        )
    rendered.append("</details>")
    return "".join(rendered)


def _render_claim_contents(
    text: str,
    evidence_ids: tuple[str, ...],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    return (
        f'<p class="claim-text">{_text(text)}</p>'
        + _evidence_links(evidence_ids, evidence, report_dir)
    )


def _render_claim_block(
    block: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    return (
        '<article class="card">'
        f'<h3>{_escape(str(block["title"]))}</h3>'
        + _render_claim_contents(
            str(block["text"]), block["evidence"], evidence, report_dir
        )
        + "</article>"
    )


def _render_list_block(
    block: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    items = block["items"]
    content = [
        '<article class="card">',
        f'<h3>{_escape(str(block["title"]))}</h3>',
        "<ul>",
    ]
    content.extend(
        "<li>"
        + _render_claim_contents(item["text"], item["evidence"], evidence, report_dir)
        + "</li>"
        for item in items
    )
    content.extend(["</ul>", "</article>"])
    return "".join(content)


def _render_comparison_block(
    block: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    content = [
        '<article class="comparison card">',
        f'<h3>{_escape(str(block["title"]))}</h3>',
        '<div class="grid comparison-grid">',
    ]
    for side in (block["left"], block["right"]):
        content.extend(
            [
                '<section class="comparison-side">',
                f'<h4>{_escape(str(side["title"]))}</h4>',
                "<ul>",
            ]
        )
        content.extend(
            "<li>"
            + _render_claim_contents(item["text"], item["evidence"], evidence, report_dir)
            + "</li>"
            for item in side["items"]
        )
        content.extend(["</ul>", "</section>"])
    content.extend(["</div>", "</article>"])
    return "".join(content)


def _render_decision_board(
    block: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    groups: dict[str, list[dict[str, object]]] = {state: [] for state in DECISION_STATES}
    for decision in block["decisions"]:
        groups[decision["state"]].append(decision)
    content = [
        '<article class="decision-board-block card">',
        f'<h3>{_escape(str(block["title"]))}</h3>',
        '<div class="decision-board">',
    ]
    for state in DECISION_STATES:
        decisions = groups[state]
        if not decisions:
            continue
        content.extend(
            [
                f'<section class="decision-group" data-decision-state="{_escape(state)}">',
                f'<h4>{_escape(state)} <span class="count">{len(decisions)}</span></h4>',
                "<ol>",
            ]
        )
        content.extend(
            "<li>"
            f'<h5>{_escape(str(decision["title"]))}</h5>'
            + _render_claim_contents(
                decision["text"], decision["evidence"], evidence, report_dir
            )
            + "</li>"
            for decision in decisions
        )
        content.extend(["</ol>", "</section>"])
    content.extend(["</div>", "</article>"])
    return "".join(content)


def _render_diagram_block(
    block: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    claim = block["claim"]
    return (
        '<figure class="diagram card">'
        f'<h3>{_escape(str(block["title"]))}</h3>'
        f'<span class="badge">{_escape(str(block["diagram_type"]))}</span>'
        '<div class="diagram-target" aria-live="polite"></div>'
        '<p class="diagram-fallback">Diagram preview unavailable. The source remains readable.</p>'
        '<p class="diagram-error" role="alert" hidden></p>'
        '<details class="diagram-debug">'
        "<summary>Show Mermaid source</summary>"
        f'<pre class="diagram-source">{_escape(str(block["source"]))}</pre>'
        "</details>"
        + _render_claim_contents(claim["text"], claim["evidence"], evidence, report_dir)
        + "</figure>"
    )


BLOCK_RENDERERS = {
    "claim": _render_claim_block,
    "list": _render_list_block,
    "comparison": _render_comparison_block,
    "decision-board": _render_decision_board,
    "diagram": _render_diagram_block,
}


def render_block(
    block: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    return BLOCK_RENDERERS[str(block["kind"])](block, evidence, report_dir)


def _render_section(
    section_id: str,
    section: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    content = [
        f'<section id="{_escape(section_id)}" class="section-anchor">',
        f'<h2>{_escape(str(section["title"]))}</h2>',
    ]
    if section["lede"]:
        content.append(f'<p class="lede">{_text(str(section["lede"]))}</p>')
    content.extend(render_block(block, evidence, report_dir) for block in section["blocks"])
    content.append("</section>")
    return "".join(content)


def _render_claim_card(
    heading: str,
    claim: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    return (
        '<article class="card">'
        f"<h3>{_escape(heading)}</h3>"
        + _render_claim_contents(claim["text"], claim["evidence"], evidence, report_dir)
        + "</article>"
    )


def _finding_anchor(finding_id: str) -> str:
    slug = "".join(
        character.lower() if character.isalnum() else "-" for character in finding_id
    ).strip("-")
    return f"finding-{slug or 'without-id'}"


def _finding_sort_key(finding: dict[str, object]) -> tuple[int, int, int, str]:
    return (
        IMPACT_RANK[finding["impact"]],
        CERTAINTY_RANK[finding["certainty"]],
        -finding["propagation"],
        finding["id"],
    )


def _render_finding_claim(
    heading: str,
    claim: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    return (
        f'<section class="finding-block"><h4>{_escape(heading)}</h4>'
        + _render_claim_contents(claim["text"], claim["evidence"], evidence, report_dir)
        + "</section>"
    )


def _render_finding(
    finding: dict[str, object],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
    *,
    is_open: bool,
) -> str:
    finding_id = str(finding["id"])
    anchor = _finding_anchor(finding_id)
    claim_request = finding["request"]
    request_id = f"request-{anchor}"
    open_attribute = " open" if is_open else ""
    return (
        f'<details class="finding-disclosure"{open_attribute} id="{_escape(anchor)}" '
        f'data-finding-id="{_escape(finding_id)}">'
        "<summary>"
        f'<span class="finding-id">{_escape(finding_id)}</span>'
        f'<span class="finding-meta"><strong class="finding-title">{_escape(str(finding["title"]))}</strong>'
        f' <span class="badge">{_escape(str(finding["impact"]))}</span>'
        f' <span class="badge">{_escape(str(finding["certainty"]))}</span>'
        f' <span class="badge">propagation {finding["propagation"]}</span></span>'
        f'<span class="finding-rank">Ranked by impact, certainty, propagation, then ID.</span>'
        "</summary>"
        '<div class="finding-body">'
        f'<section class="finding-block"><h4>Evidence</h4>'
        f'{_evidence_links(finding["evidence"], evidence, report_dir)}</section>'
        + _render_finding_claim(
            "Interpretation", finding["interpretation"], evidence, report_dir
        )
        + _render_finding_claim(
            "Specification impact", finding["specification_impact"], evidence, report_dir
        )
        + _render_finding_claim("Repair", finding["repair"], evidence, report_dir)
        + '<section class="copy-request"><h4>Copyable request</h4>'
        + f'<p id="{_escape(request_id)}">{_text(claim_request["text"])}</p>'
        + _evidence_links(claim_request["evidence"], evidence, report_dir)
        + f'<button type="button" data-copy-target="{_escape(request_id)}" hidden>Copy request</button>'
        + '<span class="copy-status" role="status" aria-live="polite"></span>'
        + "</section></div></details>"
    )


def _render_findings(
    findings: tuple[dict[str, object], ...],
    evidence: dict[str, ResolvedEvidence],
    report_dir: Path,
) -> str:
    ranked = sorted(findings, key=_finding_sort_key)
    content = [
        '<div class="finding-queue">',
    ]
    content.extend(
        _render_finding(finding, evidence, report_dir, is_open=index == 0)
        for index, finding in enumerate(ranked)
    )
    if not ranked:
        content.append('<p class="empty">No findings recorded.</p>')
    content.append("</div>")
    return "".join(content)


def _render_executive_priorities(
    findings: tuple[dict[str, object], ...],
) -> str:
    ranked = sorted(findings, key=_finding_sort_key)[:3]
    content = [
        '<section class="executive-priorities" aria-labelledby="priority-heading">',
        '<h2 id="priority-heading">Priority findings</h2>',
    ]
    if not ranked:
        content.append('<p class="empty">No priority findings.</p>')
    else:
        content.append('<ol class="priority-list">')
        for finding in ranked:
            anchor = _finding_anchor(str(finding["id"]))
            content.append(
                "<li>"
                f'<a class="priority-link" href="#{_escape(anchor)}">'
                f'<span class="priority-id">{_escape(str(finding["id"]))}</span>'
                f'<span class="priority-title">{_escape(str(finding["title"]))}</span>'
                f'<span class="badge">{_escape(str(finding["impact"]))}</span>'
                f'<span class="badge">{_escape(str(finding["certainty"]))}</span>'
                "</a>"
                "</li>"
            )
        content.append("</ol>")
    content.append("</section>")
    return "".join(content)


def _render_body(report: dict[str, object], report_dir: Path) -> str:
    sections = report["sections"]
    evidence = report["evidence"]
    content = [
        _render_section(section_id, sections[section_id], evidence, report_dir)
        for section_id in SECTION_IDS[:-1]
    ]
    review = sections["review"]
    review_content = [
        f'<section id="review" class="section-anchor">',
        f'<h2>{_escape(str(review["title"]))}</h2>',
    ]
    if review["lede"]:
        review_content.append(f'<p class="lede">{_text(str(review["lede"]))}</p>')
    review_content.extend(
        render_block(block, evidence, report_dir) for block in review["blocks"]
    )
    review_content.extend(
        [
            '<h3>Findings</h3>',
            _render_findings(report["findings"], evidence, report_dir),
            "</section>",
        ]
    )
    content.append("".join(review_content))
    return "".join(content)


def _metrics_strip(report: dict[str, object]) -> str:
    decisions: list[dict[str, object]] = []
    diagrams = 0
    for section in report["sections"].values():
        for block in section["blocks"]:
            if block["kind"] == "decision-board":
                decisions.extend(block["decisions"])
            if block["kind"] == "diagram":
                diagrams += 1
    unresolved = sum(decision["state"] in {"open", "not-specified"} for decision in decisions)
    findings = report["findings"]
    to_verify = sum(finding["certainty"] == "to-verify" for finding in findings)
    metrics = (
        ("Status", str(report["status"]), "declared status", "neutral"),
        ("Open decisions", str(unresolved), "unresolved decision states", "warning" if unresolved else "neutral"),
        ("Findings", str(len(findings)), "complete ranked findings", "critical" if findings else "neutral"),
        ("To verify", str(to_verify), "findings requiring confirmation", "warning" if to_verify else "neutral"),
        ("Diagrams", str(diagrams), "evidence-backed diagram blocks", "neutral"),
    )
    return "".join(
        f'<div class="metric {tone}">'
        f'<div class="metric-label">{_escape(label)}</div>'
        f'<div class="metric-value">{_escape(value)}</div>'
        f'<div class="metric-detail">{_escape(detail)}</div>'
        "</div>"
        for label, value, detail, tone in metrics
    )


def _load_template(template_path: Path) -> str:
    try:
        text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _error("template", f"cannot be read: {exc}") from exc
    declared = {
        match.group("named") or match.group("braced")
        for match in string.Template.pattern.finditer(text)
        if match.group("named") or match.group("braced")
    }
    missing = set(REQUIRED_PLACEHOLDERS - declared)
    if missing:
        raise _error(
            "template",
            "missing required placeholders: " + ", ".join(sorted(missing)),
        )
    unknown = declared - REQUIRED_PLACEHOLDERS
    if unknown:
        raise _error(
            "template",
            "unsupported placeholders: " + ", ".join(sorted(unknown)),
        )
    return text


def _fill_template(text: str, values: dict[str, str]) -> str:
    try:
        return string.Template(text).substitute(values)
    except (KeyError, ValueError) as exc:
        raise _error("template", f"cannot be filled: {exc}") from exc


def _write_page(report_dir: Path, destination: Path, content: str) -> None:
    fd, raw_path = tempfile.mkstemp(
        prefix=".wayfinder-report-", suffix=".tmp", dir=report_dir
    )
    temporary_path = Path(raw_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def render_report(
    workspace: Path,
    data_path: Path,
    template_path: Path | None = None,
) -> Path:
    """Render validated generic report data into report/index.html."""

    workspace_root = _resolve_workspace(workspace)
    report_dir = _resolve_report_dir(workspace_root)
    report = load_report_data(data_path, workspace_root)
    template_text = _load_template(template_path or DEFAULT_TEMPLATE)
    generated_at = datetime.fromtimestamp(
        report["data_path"].stat().st_mtime, tz=timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")
    body = _render_body(report, report_dir)
    values = {
        "title": _escape(report["title"]),
        "slug": _escape(report["slug"]),
        "status_label": _escape(report["status"]),
        "generated_at": _escape(generated_at),
        "destination": _render_claim_card(
            "Destination", report["destination"], report["evidence"], report_dir
        ),
        "metrics": _metrics_strip(report),
        "priorities": _render_executive_priorities(report["findings"]),
        "body": body,
    }
    page = _fill_template(template_text, values)
    index_path = report_dir / "index.html"
    _write_page(report_dir, index_path, page)
    return index_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a generic evidence-backed Wayfinder report."
    )
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.check:
            summary = validation_summary(load_report_data(args.data, args.workspace))
            if args.format == "json":
                print(json.dumps(summary, sort_keys=True))
            else:
                print(f"status: {summary['status']}")
                for name, count in summary["metrics"].items():
                    print(f"{name}: {count}")
                for warning in summary["warnings"]:
                    print(f"warning: {warning}")
            return 0
        render_report(args.workspace, args.data, args.template)
    except (ReportError, OSError, ValueError) as exc:
        print(f"render_report: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
