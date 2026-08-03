#!/usr/bin/env python3
"""Render a validated Wayfinder report model into two local HTML views."""

from __future__ import annotations

import argparse
import html
import os
import sys
import tempfile
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


STYLE = """
:root {
  color-scheme: light;
  --ink: #17202a;
  --muted: #52616b;
  --line: #c7d1d8;
  --surface: #ffffff;
  --soft: #f2f6f8;
  --accent: #075985;
  --accent-soft: #e0f2fe;
  --warning: #92400e;
  --warning-soft: #ffedd5;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--soft); color: var(--ink); line-height: 1.55; }
a { color: var(--accent); }
a:focus-visible, summary:focus-visible { outline: 3px solid #f59e0b; outline-offset: 3px; }
header { background: var(--ink); color: #fff; }
.header-inner, .page { max-width: 1180px; margin: 0 auto; padding: 1.25rem; }
.header-inner { display: flex; gap: 1rem; align-items: center; justify-content: space-between; }
header a { color: #bae6fd; }
nav { display: flex; gap: .8rem; flex-wrap: wrap; }
.page { padding-top: 2rem; padding-bottom: 4rem; }
.eyebrow { color: #bae6fd; font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; }
h1, h2, h3 { line-height: 1.2; }
h1 { margin: .25rem 0; }
h2 { margin-top: 2.3rem; border-bottom: 2px solid var(--line); padding-bottom: .45rem; }
h3 { margin-top: 0; }
.lede { color: var(--muted); max-width: 75ch; }
.grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: .65rem; padding: 1rem; box-shadow: 0 1px 2px #17202a12; }
.card > :first-child { margin-top: 0; }
.claim-text { white-space: normal; }
.sources { margin-top: .8rem; border-top: 1px solid var(--line); padding-top: .65rem; }
.source { margin-top: .65rem; }
.source-link { font-weight: 700; }
blockquote { margin: .25rem 0 0; padding: .45rem .7rem; border-left: 3px solid var(--accent); color: var(--muted); background: #f8fafc; white-space: pre-wrap; }
ul, ol { padding-left: 1.35rem; }
.timeline { display: grid; gap: .8rem; list-style: none; padding-left: 0; counter-reset: step; }
.timeline li { counter-increment: step; display: grid; grid-template-columns: 2.4rem 1fr; gap: .75rem; align-items: start; }
.timeline li::before { content: counter(step); display: grid; place-items: center; width: 2.2rem; height: 2.2rem; border-radius: 50%; background: var(--accent-soft); color: var(--accent); font-weight: 800; }
.badge { display: inline-block; border-radius: 999px; padding: .15rem .55rem; margin: .1rem .2rem .1rem 0; background: var(--accent-soft); color: var(--accent); font-size: .78rem; font-weight: 700; }
.badge.warning { background: var(--warning-soft); color: var(--warning); }
.finding-card { border-left: .4rem solid var(--accent); }
.finding-card.secondary { border-left-color: var(--line); }
.finding-meta { color: var(--muted); font-size: .9rem; }
details { background: var(--surface); border: 1px solid var(--line); border-radius: .65rem; padding: .9rem 1rem; }
summary { cursor: pointer; font-weight: 800; }
.secondary-list { display: grid; gap: 1rem; margin-top: 1rem; }
.mermaid-source { overflow-x: auto; background: #0f172a; color: #e0f2fe; border-radius: .5rem; padding: 1rem; white-space: pre; }
.empty { color: var(--muted); font-style: italic; }
@media (max-width: 620px) {
  .header-inner { align-items: flex-start; flex-direction: column; }
  .page { padding-top: 1rem; }
}
"""


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
    rendered: list[str] = ['<div class="sources"><strong>Sources</strong>']
    for source in sources:
        href, label = _safe_source_path(source, workspace, report_dir)
        rendered.append(
            '<div class="source">'
            f'<a class="source-link" href="{href}">{label}</a>'
            f'<blockquote>{_text(source.excerpt)}</blockquote>'
            "</div>"
        )
    rendered.append("</div>")
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
        return '<p class="empty">No items recorded.</p>'
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
    return (
        "<li>"
        f'<div><h3>{_escape(entry.title)}</h3>'
        f'<span class="badge">{_escape(entry.state)}</span>'
        f'<p class="claim-text">{_text(entry.claim.text)}</p>'
        f"{_source_links(entry.claim.sources, workspace, report_dir)}</div>"
        "</li>"
    )


def _diagram_card(diagram: Diagram, workspace: Path, report_dir: Path) -> str:
    return (
        '<article class="card">'
        f"<h3>{_escape(diagram.title)}</h3>"
        f'<span class="badge">{_escape(diagram.kind)}</span>'
        f'<pre class="mermaid-source">{_escape(diagram.mermaid)}</pre>'
        f'<p class="claim-text">{_text(diagram.claim.text)}</p>'
        f"{_source_links(diagram.claim.sources, workspace, report_dir)}"
        "</article>"
    )


def _navigation(active: str) -> str:
    understand_class = " aria-current=\"page\"" if active == "understand" else ""
    review_class = " aria-current=\"page\"" if active == "review" else ""
    return (
        "<nav>"
        f'<a href="index.html"{understand_class}>Comprendi il risultato</a>'
        f'<a href="review.html"{review_class}>Revisiona la coerenza</a>'
        "</nav>"
    )


def _document(title: str, active: str, body: str) -> str:
    return (
        '<!doctype html><html lang="it"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{_escape(title)}</title>"
        f"<style>{STYLE}</style></head><body>"
        '<header><div class="header-inner">'
        f'<div><div class="eyebrow">Internal Wayfinder Report</div><h1>{_escape(title)}</h1></div>'
        f"{_navigation(active)}"
        "</div></header>"
        f'<main class="page">{body}</main></body></html>'
    )


def _understand_view(model: ReportModel, workspace: Path, report_dir: Path) -> str:
    summary = model.understand.summary
    implementation = model.understand.implementation
    body: list[str] = [
        '<p class="eyebrow">Comprendi il risultato</p>',
        f'<p class="lede">{_text(model.destination.text)}</p>',
        _source_links(model.destination.sources, workspace, report_dir),
        "<h2>Summary</h2>",
        '<div class="grid">',
        _claim_card("Specification", summary.specification, workspace, report_dir),
        _claim_card("Problem", summary.problem, workspace, report_dir),
        _claim_card("Decision", summary.decision, workspace, report_dir),
        _claim_card("Expected result", summary.expected_result, workspace, report_dir),
        "</div>",
        "<h2>Operation</h2>",
        _claim_card("How this report works", model.understand.operation, workspace, report_dir),
        "<h2>Behaviors</h2>",
        '<div class="grid">',
        *(
            _behavior_card(behavior, workspace, report_dir)
            for behavior in model.understand.behaviors
        ),
        "</div>" if model.understand.behaviors else '<p class="empty">No behaviors recorded.</p>',
        "<h2>Rules</h2>",
        _claim_list(model.understand.rules, workspace, report_dir),
        "<h2>Scope</h2>",
        '<div class="grid">',
        '<article class="card"><h3>Included</h3>'
        f"{_claim_list(model.understand.scope.included, workspace, report_dir)}</article>",
        '<article class="card"><h3>Excluded</h3>'
        f"{_claim_list(model.understand.scope.excluded, workspace, report_dir)}</article>",
        "</div>",
        "<h2>Decision path</h2>",
        '<ol class="timeline">',
        *(
            _decision_entry(entry, workspace, report_dir)
            for entry in model.understand.decision_path
        ),
        "</ol>" if model.understand.decision_path else '<p class="empty">No decision path recorded.</p>',
        "<h2>Specified versus implemented</h2>",
        '<div class="grid">',
        '<article class="card"><h3>Specified</h3>'
        f"{_claim_list(implementation.specified, workspace, report_dir)}</article>",
        '<article class="card"><h3>Implemented</h3>'
        f"{_claim_list(implementation.implemented, workspace, report_dir)}</article>",
        "</div>",
        "<h2>Relationships</h2>",
        '<div class="grid">',
        *(_diagram_card(diagram, workspace, report_dir) for diagram in model.understand.diagrams),
        "</div>" if model.understand.diagrams else '<p class="empty">No relationship blocks recorded.</p>',
    ]
    return "".join(body)


def _finding_card(
    finding: Finding,
    workspace: Path,
    report_dir: Path,
    card_kind: str,
) -> str:
    metadata = (
        f'<span class="badge">{_escape(finding.type)}</span>'
        f'<span class="badge">{_escape(finding.certainty)}</span>'
        f'<span class="badge">{_escape(finding.impact_level)}</span>'
        f'<span class="badge">propagation {finding.propagation}</span>'
    )
    return (
        f'<article class="card finding-card {"secondary" if card_kind == "secondary" else "primary"}" '
        f'data-finding-card="{_escape(card_kind)}" data-finding-id="{_escape(finding.id)}">'
        f"<h3>{_escape(finding.id)}</h3>"
        f'<p class="finding-meta">{metadata}</p>'
        f"{_source_links(finding.evidence, workspace, report_dir)}"
        f"{_claim_card('Interpretation', finding.interpretation, workspace, report_dir)}"
        f"{_claim_card('Specification impact', finding.specification_impact, workspace, report_dir)}"
        f"{_claim_card('Repair proposal', finding.repair, workspace, report_dir)}"
        f"{_claim_card('Copyable request', finding.copyable_request, workspace, report_dir)}"
        "</article>"
    )


def _review_view(model: ReportModel, workspace: Path, report_dir: Path) -> str:
    ranked = rank_findings(model.review.findings)
    primary = ranked[:5]
    secondary = ranked[5:]
    body: list[str] = [
        '<p class="eyebrow">Revisiona la coerenza</p>',
        '<p class="lede">Prioritized findings separate evidence, interpretation, specification impact, and repair proposal.</p>',
        "<h2>Primary findings</h2>",
    ]
    if primary:
        body.extend(
            _finding_card(finding, workspace, report_dir, "primary")
            for finding in primary
        )
    else:
        body.append('<p class="empty">No findings recorded.</p>')
    if secondary:
        body.extend(
            [
                '<details class="secondary-findings">'
                f"<summary>Show {len(secondary)} additional findings</summary>"
                '<div class="secondary-list">',
                *(
                    _finding_card(finding, workspace, report_dir, "secondary")
                    for finding in secondary
                ),
                "</div></details>",
            ]
        )
    return "".join(body)


def _write_pair(report_dir: Path, outputs: tuple[tuple[Path, str], ...]) -> None:
    temporary_paths: list[Path] = []
    try:
        for _, content in outputs:
            fd, raw_path = tempfile.mkstemp(
                prefix=".wayfinder-report-", suffix=".tmp", dir=report_dir
            )
            temporary_path = Path(raw_path)
            temporary_paths.append(temporary_path)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        for (destination, _), temporary_path in zip(outputs, temporary_paths):
            os.replace(temporary_path, destination)
        temporary_paths.clear()
    finally:
        for temporary_path in temporary_paths:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def render_report(workspace: Path, model_path: Path) -> tuple[Path, Path]:
    """Validate inputs, then write the deterministic Understand and Review views."""

    workspace_root = _resolve_workspace(workspace)
    report_dir = _resolve_report_dir(workspace_root)
    resolved_model = _resolve_model_path(model_path, report_dir)
    model = load_report_model(resolved_model, workspace_root)
    index_path = report_dir / "index.html"
    review_path = report_dir / "review.html"
    index_html = _document(
        model.title,
        "understand",
        _understand_view(model, workspace_root, report_dir),
    )
    review_html = _document(
        model.title,
        "review",
        _review_view(model, workspace_root, report_dir),
    )
    _write_pair(report_dir, ((index_path, index_html), (review_path, review_html)))
    return index_path, review_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a validated report-model.v1.json into two local HTML views."
    )
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        render_report(args.workspace, args.model)
    except (ModelError, OSError, ValueError) as exc:
        print(f"render_report: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
