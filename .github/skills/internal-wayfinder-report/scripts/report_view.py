#!/usr/bin/env python3
"""Derive presentation data from an already validated Wayfinder report model."""

from __future__ import annotations

from dataclasses import dataclass

from report_model import DecisionPathEntry, Finding, ReportModel

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

@dataclass(frozen=True)
class Metric:
    label: str
    value: str
    detail: str
    tone: str


@dataclass(frozen=True)
class DecisionGroup:
    state: str
    label: str
    tone: str
    entries: tuple[DecisionPathEntry, ...]


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


def group_decisions(model: ReportModel) -> tuple[DecisionGroup, ...]:
    groups: list[DecisionGroup] = []
    for state in ("resolved", "open", "not-specified"):
        entries = tuple(
            entry
            for entry in model.understand.decision_path
            if entry.state == state
        )
        if entries:
            groups.append(
                DecisionGroup(
                    state=state,
                    label=DECISION_STATE_LABELS[state],
                    tone=DECISION_STATE_CLASSES[state],
                    entries=entries,
                )
            )
    return tuple(groups)


def rank_reason(finding: Finding) -> str:
    return (
        f"impatto {IMPACT_LABELS[finding.impact_level]}"
        f" · certezza {CERTAINTY_LABELS[finding.certainty]}"
        f" · propagazione {finding.propagation}"
    )
