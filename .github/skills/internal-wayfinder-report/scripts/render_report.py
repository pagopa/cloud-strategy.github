#!/usr/bin/env python3
"""Render a validated Wayfinder report model into one local HTML page."""

from __future__ import annotations

import argparse
import html
import os
import shutil
import string
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from report_model import (
    Behavior,
    Claim,
    DecisionPathEntry,
    Diagram,
    Finding,
    ModelError,
    ReportModel,
    SourceRef,
    load_report_model,
    rank_findings,
)
from report_view import (
    CERTAINTY_LABELS,
    DECISION_STATE_LABELS,
    FINDING_TYPE_LABELS,
    IMPACT_LABELS,
    STATUS_LABELS,
    derive_metrics,
    group_decisions,
    rank_reason,
)

BUNDLE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = BUNDLE_ROOT / "templates" / "report.html"
SAMPLE_WORKSPACE = BUNDLE_ROOT / "templates" / "sample"
DEFAULT_PREVIEW_DIR = Path("tmp/.wayfinder-report-preview")
REQUIRED_PLACEHOLDERS = frozenset(
    {
        "title",
        "slug",
        "status_label",
        "status_class",
        "generated_at",
        "destination",
        "metrics",
        "understand",
        "review",
    }
)
STATUS_CLASSES = {
    "analysis-in-progress": "warning",
    "ready-for-execution": "",
    "implemented": "",
    "unknown": "critical",
}


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def _text(value: str) -> str:
    return _escape(value).replace("\n", "<br>\n")


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _resolve_workspace(workspace: Path) -> Path:
    try:
        root = workspace.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ModelError(f"workspace cannot be resolved: {exc}") from exc
    if not root.is_dir():
        raise ModelError("workspace must be an existing directory")
    for required_name in ("map.md", "analysis.md"):
        required_path = (root / required_name).resolve()
        if not _within(required_path, root) or not required_path.is_file():
            raise ModelError(f"workspace is missing required file: {required_name}")
    return root


def _resolve_report_dir(workspace: Path) -> Path:
    report_candidate = workspace / "report"
    if report_candidate.exists() and not report_candidate.is_dir():
        raise ModelError("report must be a directory")
    try:
        report_candidate.mkdir(exist_ok=True)
        report_dir = report_candidate.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ModelError(f"report cannot be prepared: {exc}") from exc
    if not _within(report_dir, workspace):
        raise ModelError("report must resolve inside the workspace")
    return report_dir


def _resolve_model_path(model_path: Path, report_dir: Path) -> Path:
    try:
        resolved = model_path.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ModelError(f"model cannot be resolved below report: {exc}") from exc
    if not _within(resolved, report_dir) or resolved == report_dir or not resolved.is_file():
        raise ModelError("model must be a file below the report directory")
    return resolved


def _safe_source_path(source: SourceRef, workspace: Path, report_dir: Path) -> tuple[str, str]:
    try:
        resolved = (workspace / source.path).resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ModelError(f"source path must resolve inside the workspace: {exc}") from exc
    if not _within(resolved, workspace) or not resolved.is_file():
        raise ModelError(f"source path must resolve inside the workspace: {source.path!r}")
    href = os.path.relpath(resolved, report_dir).replace(os.sep, "/")
    if href.startswith("/") or href.startswith("//"):
        raise ModelError(f"source link escaped the workspace: {source.path!r}")
    return _escape(href), _escape(source.path)


def _source_links(
    sources: tuple[SourceRef, ...], workspace: Path, report_dir: Path
) -> str:
    rendered: list[str] = [
        f'<details class="sources"><summary>Fonti ({len(sources)})</summary>'
    ]
    for source in sources:
        href, label = _safe_source_path(source, workspace, report_dir)
        rendered.append(
            '<div class="source">'
            f'<a class="source-link" href="{href}">{label}</a>'
            f"<blockquote>{_text(source.excerpt)}</blockquote>"
            "</div>"
        )
    rendered.append("</details>")
    return "".join(rendered)


def _claim_card(
    heading: str,
    claim: Claim,
    workspace: Path,
    report_dir: Path,
    *,
    card_class: str = "card",
) -> str:
    return (
        f'<article class="{_escape(card_class)}">'
        f"<h3>{_escape(heading)}</h3>"
        f'<p class="claim-text">{_text(claim.text)}</p>'
        f"{_source_links(claim.sources, workspace, report_dir)}"
        "</article>"
    )


def _claim_list(
    claims: tuple[Claim, ...], workspace: Path, report_dir: Path
) -> str:
    if not claims:
        return '<p class="empty">Nessun elemento registrato.</p>'
    return "<ul>" + "".join(
        "<li>"
        f'<span class="claim-text">{_text(claim.text)}</span>'
        f"{_source_links(claim.sources, workspace, report_dir)}"
        "</li>"
        for claim in claims
    ) + "</ul>"


def _behavior_card(
    behavior: Behavior, workspace: Path, report_dir: Path
) -> str:
    return _claim_card(
        behavior.title,
        behavior.claim,
        workspace,
        report_dir,
    )


def _decision_entry(
    entry: DecisionPathEntry, workspace: Path, report_dir: Path
) -> str:
    badge_class = "badge" if entry.state == "resolved" else "badge warning"
    return (
        "<li>"
        f'<div><h3>{_escape(entry.title)}</h3>'
        f'<span class="{badge_class}">{_escape(DECISION_STATE_LABELS[entry.state])}</span>'
        f'<p class="claim-text">{_text(entry.claim.text)}</p>'
        f"{_source_links(entry.claim.sources, workspace, report_dir)}</div>"
        "</li>"
    )


def _diagram_figure(title: str, kind: str, mermaid: str, body: str) -> str:
    return (
        '<figure class="diagram card">'
        f"<h3>{_escape(title)}</h3>"
        f'<span class="badge">{_escape(kind)}</span>'
        '<div class="diagram-target" aria-live="polite"></div>'
        '<p class="diagram-fallback">Anteprima non disponibile. Il sorgente del diagramma resta consultabile.</p>'
        '<p class="diagram-error" role="alert" hidden></p>'
        '<details class="diagram-debug">'
        '<summary>Mostra sorgente Mermaid</summary>'
        f'<pre class="diagram-source">{_escape(mermaid)}</pre>'
        "</details>"
        f"{body}"
        "</figure>"
    )


def _finding_anchor(finding_id: str) -> str:
    slug = "".join(
        character.lower() if character.isalnum() else "-" for character in finding_id
    ).strip("-")
    return f"finding-{slug or 'senza-id'}"


def _load_template(template_path: Path) -> str:
    try:
        text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ModelError(f"template cannot be read: {exc}") from exc
    declared = {
        match.group("named") or match.group("braced")
        for match in string.Template.pattern.finditer(text)
        if match.group("named") or match.group("braced")
    }
    missing = REQUIRED_PLACEHOLDERS - declared
    if missing:
        raise ModelError(
            "template is missing required placeholders: " + ", ".join(sorted(missing))
        )
    unknown = declared - REQUIRED_PLACEHOLDERS
    if unknown:
        raise ModelError(
            "template declares unsupported placeholders: " + ", ".join(sorted(unknown))
        )
    return text


def _fill_template(text: str, values: dict[str, str]) -> str:
    try:
        return string.Template(text).substitute(values)
    except (KeyError, ValueError) as exc:
        raise ModelError(f"template cannot be filled: {exc}") from exc


def _metrics_strip(model: ReportModel) -> str:
    return "".join(
        f'<div class="metric {_escape(metric.tone)}">'
        f'<div class="metric-label">{_escape(metric.label)}</div>'
        f'<div class="metric-value">{_escape(metric.value)}</div>'
        f'<div class="metric-detail">{_escape(metric.detail)}</div>'
        "</div>"
        for metric in derive_metrics(model)
    )


def _overview_section(
    model: ReportModel, workspace: Path, report_dir: Path
) -> str:
    summary = model.understand.summary
    return "".join(
        [
            '<section id="overview" class="section-anchor">',
            "<h2>Panoramica</h2>",
            "<p class=\"lede\">Il risultato, la motivazione e l'esito atteso in una sola vista.</p>",
            '<div class="grid overview-grid">',
            _claim_card("Specifica", summary.specification, workspace, report_dir),
            _claim_card("Problema", summary.problem, workspace, report_dir),
            _claim_card("Decisione", summary.decision, workspace, report_dir),
            _claim_card("Risultato atteso", summary.expected_result, workspace, report_dir),
            "</div>",
            "</section>",
        ]
    )


def _solution_section(
    model: ReportModel, workspace: Path, report_dir: Path
) -> str:
    diagrams = [
        _diagram_figure(
            diagram.title,
            diagram.kind,
            diagram.mermaid,
            f'<p class="claim-text">{_text(diagram.claim.text)}</p>'
            + _source_links(diagram.claim.sources, workspace, report_dir),
        )
        for diagram in model.understand.diagrams
    ]
    return "".join(
        [
            '<section id="solution" class="section-anchor">',
            "<h2>Soluzione</h2>",
            '<p class="lede">Comportamenti, regole e flussi tecnici dichiarati dal modello.</p>',
            "<h3>Comportamenti</h3>",
            '<div class="grid">'
            + "".join(
                _behavior_card(behavior, workspace, report_dir)
                for behavior in model.understand.behaviors
            )
            + "</div>"
            if model.understand.behaviors
            else '<p class="empty">Nessun comportamento registrato.</p>',
            "<h3>Regole</h3>",
            _claim_list(model.understand.rules, workspace, report_dir),
            "<h3>Flussi tecnici espliciti</h3>",
            *(diagrams or ['<p class="empty">Nessun diagramma dichiarato.</p>']),
            "</section>",
        ]
    )


def _decision_board(
    model: ReportModel, workspace: Path, report_dir: Path
) -> str:
    groups = group_decisions(model)
    if not groups:
        return '<p class="empty">Nessuna decisione registrata.</p>'
    return '<div class="decision-board">' + "".join(
        '<section class="decision-group" '
        f'data-decision-state="{_escape(group.state)}" '
        f'data-decision-tone="{_escape(group.tone)}">'
        f'<h3>{_escape(group.label)} <span class="count">{len(group.entries)}</span></h3>'
        + "<ol>"
        + "".join(
            _decision_entry(entry, workspace, report_dir)
            for entry in group.entries
        )
        + "</ol></section>"
        for group in groups
    ) + "</div>"


def _decisions_section(
    model: ReportModel, workspace: Path, report_dir: Path
) -> str:
    return "".join(
        [
            '<section id="decisions" class="section-anchor">',
            "<h2>Decisioni</h2>",
            '<p class="lede">Ogni decisione resta nel suo stato dichiarato; il report non inferisce relazioni o causalità.</p>',
            _decision_board(model, workspace, report_dir),
            "</section>",
        ]
    )


def _scope_section(
    model: ReportModel, workspace: Path, report_dir: Path
) -> str:
    implementation = model.understand.implementation
    implemented_block = (
        _claim_list(implementation.implemented, workspace, report_dir)
        if implementation.implemented
        else '<p class="empty">Nessuna prova di implementazione registrata.</p>'
    )
    return "".join(
        [
            '<section id="scope" class="section-anchor">',
            "<h2>Ambito</h2>",
            '<p class="lede">Cosa è incluso, escluso, specificato e dimostrato come implementato.</p>',
            '<div class="grid">',
            '<article class="card"><h3>Incluso</h3>',
            _claim_list(model.understand.scope.included, workspace, report_dir),
            "</article>",
            '<article class="card"><h3>Escluso</h3>',
            _claim_list(model.understand.scope.excluded, workspace, report_dir),
            "</article>",
            "</div>",
            "<h3>Specificato rispetto a implementato</h3>",
            '<div class="grid">',
            '<article class="card"><h3>Specificato</h3>',
            _claim_list(implementation.specified, workspace, report_dir),
            "</article>",
            '<article class="card"><h3>Implementato</h3>',
            implemented_block,
            "</article>",
            "</div>",
            "<h3>Come leggere questo report</h3>",
            _claim_card("Metodo", model.understand.operation, workspace, report_dir),
            "</section>",
        ]
    )


def _understand_section(model: ReportModel, workspace: Path, report_dir: Path) -> str:
    return "".join(
        (
            _overview_section(model, workspace, report_dir),
            _solution_section(model, workspace, report_dir),
            _decisions_section(model, workspace, report_dir),
            _scope_section(model, workspace, report_dir),
        )
    )


def _finding_claim(
    heading: str, claim: Claim, workspace: Path, report_dir: Path
) -> str:
    return (
        f'<section class="finding-block"><h4>{_escape(heading)}</h4>'
        f'<p class="claim-text">{_text(claim.text)}</p>'
        f"{_source_links(claim.sources, workspace, report_dir)}"
        "</section>"
    )


def _copyable_request(
    finding: Finding, workspace: Path, report_dir: Path
) -> str:
    request_id = f"request-{_finding_anchor(finding.id)}"
    return (
        '<section class="copy-request">'
        "<h4>Richiesta copiabile</h4>"
        f'<p id="{_escape(request_id)}">{_text(finding.copyable_request.text)}</p>'
        f"{_source_links(finding.copyable_request.sources, workspace, report_dir)}"
        f'<button type="button" data-copy-target="{_escape(request_id)}" hidden>Copia richiesta</button>'
        '<span class="copy-status" role="status" aria-live="polite"></span>'
        "</section>"
    )


def _finding_card(
    finding: Finding, workspace: Path, report_dir: Path, *, is_open: bool
) -> str:
    metadata = (
        f'<span class="badge">{_escape(FINDING_TYPE_LABELS[finding.type])}</span>'
        f'<span class="badge">{_escape(CERTAINTY_LABELS[finding.certainty])}</span>'
        f'<span class="badge">{_escape(IMPACT_LABELS[finding.impact_level])}</span>'
        f'<span class="badge">propagazione {finding.propagation}</span>'
    )
    open_attribute = " open" if is_open else ""
    return (
        f'<details class="finding-disclosure"{open_attribute} '
        f'id="{_escape(_finding_anchor(finding.id))}" '
        f'data-finding-id="{_escape(finding.id)}">'
        "<summary>"
        f'<span class="finding-id">{_escape(finding.id)}</span>'
        f'<span class="finding-meta">{metadata}</span>'
        f'<span class="finding-rank">Perché è in cima: {_escape(rank_reason(finding))}</span>'
        "</summary>"
        '<div class="finding-body">'
        f'<section class="finding-block"><h4>Evidenza</h4>{_source_links(finding.evidence, workspace, report_dir)}</section>'
        f'{_finding_claim("Interpretazione", finding.interpretation, workspace, report_dir)}'
        f'{_finding_claim("Impatto sulla specifica", finding.specification_impact, workspace, report_dir)}'
        f'{_finding_claim("Proposta di riparazione", finding.repair, workspace, report_dir)}'
        f'{_copyable_request(finding, workspace, report_dir)}'
        "</div></details>"
    )


def _review_section(model: ReportModel, workspace: Path, report_dir: Path) -> str:
    ranked = rank_findings(model.review.findings)
    body: list[str] = [
        '<section id="review" class="section-anchor">',
        "<h2>Revisione</h2>",
        '<p class="lede">Ogni finding resta completo, ordinato per priorità e progressivamente apribile.</p>',
        '<div class="finding-queue">',
    ]
    if ranked:
        body.extend(
            _finding_card(
                finding,
                workspace,
                report_dir,
                is_open=index == 0,
            )
            for index, finding in enumerate(ranked)
        )
    else:
        body.append('<p class="empty">Nessun finding registrato.</p>')
    body.extend(["</div>", "</section>"])
    return "".join(body)


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
    workspace: Path, model_path: Path, template_path: Path | None = None
) -> Path:
    """Validate inputs, then write the deterministic single-page report."""

    workspace_root = _resolve_workspace(workspace)
    report_dir = _resolve_report_dir(workspace_root)
    resolved_model = _resolve_model_path(model_path, report_dir)
    model = load_report_model(resolved_model, workspace_root)
    template_text = _load_template(template_path or DEFAULT_TEMPLATE)
    generated_at = datetime.fromtimestamp(
        resolved_model.stat().st_mtime, tz=timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")
    page = _fill_template(
        template_text,
        {
            "title": _escape(model.title),
            "slug": _escape(model.analysis_slug),
            "status_label": _escape(STATUS_LABELS[model.status]),
            "status_class": STATUS_CLASSES[model.status],
            "generated_at": _escape(generated_at),
            "destination": _text(model.destination.text)
            + _source_links(model.destination.sources, workspace_root, report_dir),
            "metrics": _metrics_strip(model),
            "understand": _understand_section(model, workspace_root, report_dir),
            "review": _review_section(model, workspace_root, report_dir),
        },
    )
    index_path = report_dir / "index.html"
    _write_page(report_dir, index_path, page)
    return index_path


def render_preview(target: Path, template_path: Path | None = None) -> Path:
    """Materialize the bundled sample workspace and render it for template review."""

    try:
        shutil.copytree(SAMPLE_WORKSPACE, target, dirs_exist_ok=True)
    except OSError as exc:
        raise ModelError(f"preview workspace cannot be prepared: {exc}") from exc
    return render_report(
        target, target / "report" / "report-model.v1.json", template_path
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a validated report-model.v1.json into one local HTML page."
    )
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument(
        "--preview",
        nargs="?",
        const=DEFAULT_PREVIEW_DIR,
        type=Path,
        help="Render the bundled sample workspace into the given directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.preview is None and (args.workspace is None or args.model is None):
        parser.error("--workspace and --model are required without --preview")
    try:
        if args.preview is not None:
            render_preview(args.preview, args.template)
        else:
            render_report(args.workspace, args.model, args.template)
    except (ModelError, OSError, ValueError) as exc:
        print(f"render_report: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
