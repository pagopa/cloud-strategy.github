#!/usr/bin/env python3
"""Derive presentation data from an already validated Wayfinder report model."""

from __future__ import annotations

from dataclasses import dataclass

from report_model import Finding, ReportModel

STATUS_LABELS = {
    "analysis-in-progress": "Analisi in corso",
    "ready-for-execution": "Pronto per l'esecuzione",
    "implemented": "Implementato",
    "unknown": "Stato non dichiarato",
}

DECISION_STATE_LABELS = {
    "resolved": "risolta",
    "open": "aperta",
    "not-specified": "non specificata",
}

IMPACT_LABELS = {
    "critical": "critico",
    "high": "alto",
    "medium": "medio",
    "low": "basso",
}

CERTAINTY_LABELS = {
    "confirmed": "confermata",
    "probable": "probabile",
    "to-verify": "da verificare",
}

FINDING_TYPE_LABELS = {
    "contradiction": "contraddizione",
    "superseded-decision": "decisione superata",
    "missing-dependency": "dipendenza mancante",
    "stale-map": "mappa non aggiornata",
    "ambiguity": "ambiguità",
}

DECISION_STATE_CLASSES = {
    "resolved": "resolved",
    "open": "open",
    "not-specified": "notSpecified",
}

# Excludes -, ;, > and the label delimiter " because they steer Mermaid parsing.
_ALLOWED_LABEL_PUNCTUATION = " .,:/()_+&%'"
_LABEL_SUBSTITUTIONS = {'"': "'"}
_MAX_LABEL_LENGTH = 80


@dataclass(frozen=True)
class Metric:
    label: str
    value: str
    detail: str
    tone: str


def mermaid_label(text: str) -> str:
    """Reduce arbitrary source text to characters that cannot alter Mermaid syntax."""

    cleaned = "".join(
        _LABEL_SUBSTITUTIONS.get(character)
        or (
            character
            if character.isalnum() or character in _ALLOWED_LABEL_PUNCTUATION
            else " "
        )
        for character in text
    )
    collapsed = " ".join(cleaned.split())
    if not collapsed:
        return "(senza titolo)"
    if len(collapsed) > _MAX_LABEL_LENGTH:
        collapsed = collapsed[: _MAX_LABEL_LENGTH - 1].rstrip() + "…"
    return collapsed


def derive_metrics(model: ReportModel) -> tuple[Metric, ...]:
    decision_path = model.understand.decision_path
    resolved = sum(1 for entry in decision_path if entry.state == "resolved")
    specified = len(model.understand.implementation.specified)
    implemented = len(model.understand.implementation.implemented)
    findings = model.review.findings
    blocking = sum(
        1 for finding in findings if finding.impact_level in ("critical", "high")
    )
    to_verify = sum(1 for finding in findings if finding.certainty == "to-verify")

    if specified and not implemented:
        coverage_detail = "specificato senza prova di implementazione"
        coverage_tone = "critical"
    elif specified and implemented < specified:
        coverage_detail = "implementazione parziale rispetto allo specificato"
        coverage_tone = "warning"
    else:
        coverage_detail = "specificato e implementato allineati"
        coverage_tone = "neutral"

    return (
        Metric(
            "Stato",
            STATUS_LABELS[model.status],
            "stato dichiarato dal modello",
            "neutral",
        ),
        Metric(
            "Decisioni",
            f"{resolved}/{len(decision_path)}",
            "decisioni risolte sul percorso",
            "neutral"
            if decision_path and resolved == len(decision_path)
            else "warning",
        ),
        Metric(
            "Copertura",
            f"{implemented}/{specified}",
            coverage_detail,
            coverage_tone,
        ),
        Metric(
            "Findings",
            str(len(findings)),
            f"{blocking} con impatto critico o alto",
            "critical" if blocking else "neutral",
        ),
        Metric(
            "Da verificare",
            str(to_verify),
            "findings con certezza non confermata",
            "warning" if to_verify else "neutral",
        ),
    )


def decision_path_flowchart(model: ReportModel) -> str | None:
    """Build a deterministic Mermaid flowchart from the recorded decision path."""

    entries = model.understand.decision_path
    if not entries:
        return None
    nodes = [
        (f"D{index}", entry.state, f"{index}. {mermaid_label(entry.title)}")
        for index, entry in enumerate(entries, start=1)
    ]
    lines = ["flowchart TD"]
    lines.extend(f'    {node_id}["{label}"]' for node_id, _, label in nodes)
    lines.extend(
        f"    {left[0]} --> {right[0]}" for left, right in zip(nodes, nodes[1:])
    )
    lines.append("    classDef resolved fill:#dcfce7,stroke:#15803d,color:#14532d;")
    lines.append("    classDef open fill:#ffedd5,stroke:#b45309,color:#7c2d12;")
    lines.append("    classDef notSpecified fill:#e2e8f0,stroke:#475569,color:#0f172a;")
    for state, class_name in DECISION_STATE_CLASSES.items():
        members = [node_id for node_id, node_state, _ in nodes if node_state == state]
        if members:
            lines.append(f"    class {','.join(members)} {class_name};")
    return "\n".join(lines)


def rank_reason(finding: Finding) -> str:
    return (
        f"impatto {IMPACT_LABELS[finding.impact_level]}"
        f" · certezza {CERTAINTY_LABELS[finding.certainty]}"
        f" · propagazione {finding.propagation}"
    )
