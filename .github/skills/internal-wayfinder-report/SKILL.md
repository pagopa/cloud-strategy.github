---
name: internal-wayfinder-report
description: Use when an active local Wayfinder workspace needs a traceable HTML report that explains its destination and audits its decision consistency without changing source artifacts.
---

# Internal Wayfinder Report

Turn one local Wayfinder workspace into a traceable single-page report with
progressive overview, solution, decision, scope, and review sections. The
report is an evidence projection: it explains what the workspace says and
surfaces coherence questions, while source maps, analysis, and tickets remain
the authoritative artifacts.

## When to use

Use this skill when a local `tmp/.wayfinder/<analysis-slug>/` workspace needs a
readable report for handoff or coherence review. Use the existing Wayfinder
workflow to chart or resolve decisions; use this skill after source analysis is
available and before a user needs the single report page.

## Active workspace

Use the repository-local workspace contract:

```text
tmp/.wayfinder/<analysis-slug>/
├── map.md
├── analysis.md
└── issues/
```

The active workspace is the directory whose name is the analysis slug. Require
`map.md` and `analysis.md`. Enumerate and read every regular local source file
before writing a summary, including every file under `issues/` and any local
analysis assets. Read generated files under `report/` only when resuming an
existing report. Keep the model and rendered pages inside the active workspace.

The map's `Decisions so far` section is an index. Use it to find the full
ticket answer, then cite the ticket itself; an index line never replaces the
answer it points to.

## Trace the evidence

Apply this authority order when sources disagree about the same material point:

1. An explicit correction or replacement.
2. The final answer of a resolved ticket.
3. A confirmed comment decision.
4. A question or recommendation.
5. A preliminary-analysis hypothesis.

Keep the source class visible in the claim wording. Treat deductions as
interpretation or a finding, not as canonical decisions. Every material claim
must include one or more `sources` with a workspace-relative `path` and a short
faithful `excerpt`. Source paths must resolve to regular files below the active
workspace; use the exact relative path that the renderer can link from
`report/`.

## Write model v1

Read [`references/report-model-v1.schema.json`](references/report-model-v1.schema.json)
before writing `report/report-model.v1.json`. Use exactly these top-level fields:

```text
schema_version, analysis_slug, title, status, destination, understand, review
```

Use `schema_version: 1`. `destination` and every material claim are a
`{text, sources}` object. Populate `understand` with `summary`, `operation`,
`behaviors`, `rules`, `scope`, `decision_path`, `implementation`, and optional
`diagrams`. Keep `understand.implementation.specified` separate from
`understand.implementation.implemented`; an empty implemented list means that
the workspace specifies work without evidence that it is implemented.

Each review finding must keep these layers distinct:

- `evidence`: the source excerpts that establish the observation;
- `interpretation`: what the evidence means;
- `specification_impact`: how the observation affects the intended result;
- `repair`: a proposed correction, still only a proposal;
- `copyable_request`: text the user may send to request that correction.

Use only the model enums. Give every finding a unique ID, non-empty evidence,
and one or more sources on every claim. Rank is computed by impact level,
certainty, propagation, and ID; provide every finding and let the renderer
expose the complete ranked queue with only the highest-ranked detail open
initially.

## Render the report

Run the native standard-library renderer with the model path under the active
workspace's `report/` directory:

```bash
python3 .github/skills/internal-wayfinder-report/scripts/render_report.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --model tmp/.wayfinder/<analysis-slug>/report/report-model.v1.json
```

The renderer writes exactly one page:

```text
tmp/.wayfinder/<analysis-slug>/report/index.html
```

The page presents `overview`, `solution`, `decisions`, `scope`, and `review` in
that order. It includes a derived indicator strip, truthful decision-state
groups without inferred dependencies, collapsed but complete source blocks,
and every finding as a ranked progressive disclosure. Only diagrams explicitly
declared by the model use Mermaid; no decision flowchart is fabricated when no
diagram exists. Output is deterministic: the displayed timestamp comes from
the model file `mtime`, not the current clock. Local source links are relative
to `report/`.

## Template and preview

The editable shell is
`.github/skills/internal-wayfinder-report/templates/report.html`. It declares
these exact placeholders:

```text
title, slug, status_label, status_class, generated_at, destination, metrics,
understand, review, preview_attributes
```

Pass `--template PATH` to render with a custom shell. Pass `--preview [PATH]`
to materialize the bundled sample workspace and render it to
`tmp/.wayfinder-report-preview/` by default. A missing or unsupported template
placeholder fails before any report file is written. The preview renders the
same template with a visible structure overlay and uses only the bundled sample
workspace, so the layout can be adjusted before real report data is supplied.

Mermaid is optional, pinned, isolated in the template, and removable. The
renderer parses each explicit diagram before attempting to render it. A
missing library or invalid diagram leaves an accessible fallback, an explicit
diagnostic state, and escaped Mermaid source available for inspection. Without
the script, the source and fallback remain usable. The renderer itself never
performs network access.

## Completion gate

Before reporting completion, confirm that:

- all source files were read and every material claim is traceable;
- the model is accepted as v1 and the renderer accepts workspace confinement;
- the generated `index.html` exists under the active workspace's `report/` directory;
- source maps, analysis, tickets, and other Wayfinder source files are byte-for-
  byte unchanged; and
- unresolved `to-verify` findings and their source links are reported to the
  user.

If a required source is missing, a claim cannot be traced, a path leaves the
workspace, or the renderer rejects the model, stop with the exact gap. Keep the
report model or finding proposal as the next actionable artifact; do not
silently downgrade the claim.

This skill creates a single-page report only. It does not apply repairs, edit `map.md`,
`analysis.md`, `issues/`, or other source artifacts; persist review state;
compare analysis versions; contact a remote tracker; or generate PDF,
dashboard, or network-fetched diagram output.
