---
name: internal-wayfinder-report
description: Use when an active local Wayfinder workspace needs a generic, traceable, decision-first HTML report that explains its destination and audits decisions without changing source artifacts.
---

# Internal Wayfinder Report

Turn one local Wayfinder workspace into a generic, traceable, decision-first
single-page report. The report explains what the workspace says and surfaces
coherence questions, while the map, analysis, and issue files remain
authoritative.

For eligible token-intensive work, use `/internal-low-cost-delegation` only in
two stages: candidate evidence inventory after source paths and authority are
locked, then locked report drafting after sections, evidence IDs, findings,
diagram roles, and validation are fixed. Never delegate source authority,
findings, or diagram relationships.

## When to use

Use this skill after a local Wayfinder workspace has source analysis and needs a
readable handoff or coherence review. Use the existing Wayfinder workflow to
chart or resolve decisions; use this skill to project the result into HTML.

## Active workspace and source authority

The active workspace is `tmp/.wayfinder/<analysis-slug>/` and must contain:

```text
map.md
analysis.md
issues/
report/report.json
```

Read `map.md`, `analysis.md`, every regular local file below `issues/`, and
other local analysis assets before writing the report input. See
[compact-authoring.md](references/compact-authoring.md) for the preflight-first
bounded authoring sequence. “Read each distinct source path once in a bounded
pass” means complete file coverage with bounded retained notes; it does not
authorize skipping an issue. The source-note helper is navigation-only, and
`render_report.py` remains the final evidence validator. Generated files under
`report/` may be read when resuming, but are not source authority.

When sources disagree, use this authority order:

1. an explicit correction or replacement;
2. the final answer of a resolved issue;
3. a confirmed comment decision;
4. a question or recommendation;
5. a preliminary-analysis hypothesis.

Keep the source class visible in claim wording. Treat deductions as
interpretation or a finding, not as a canonical decision. Do not modify
`map.md`, `analysis.md`, issue files, or other Wayfinder source artifacts.

## Compact report input

Write `report/report.json` with exactly these top-level keys:

```text
title, slug, status, destination, evidence, sections, findings
```

`destination` and every claim use `{text, evidence}`. The evidence registry
declares each source path and exact non-empty excerpt once:

```json
{
  "E01": {"path": "map.md", "excerpt": "exact source text"}
}
```

Evidence paths are relative to the active workspace and must resolve to local
regular files. Do not use URLs, directories, missing files, traversal, or a
symlink whose resolved target leaves the workspace. Every evidence excerpt is
one non-empty physical source line, occurs exactly once in its declared source,
and uses a unique `(path, excerpt)` pair. The renderer caches each distinct
source read during validation. Every referenced evidence ID must exist.

Sections are required in this order:

```text
overview, solution, decisions, scope, review
```

Each section has a title, optional lede, and ordered blocks. The closed block
vocabulary is `claim`, `list`, `comparison`, `decision-board`, and `diagram`.
Every report has at least one evidence-backed diagram in `overview` and one in
`review`. Treat 12-15 evidence entries, no more than three findings, and
normally two diagrams as editorial defaults: the validator reports bounded
warnings when those defaults are missed but does not reject a valid complex
report. Do not add domain-specific fields or infer causal, sequential, or
dependency edges that are absent from the sources.

Decision boards use only `resolved`, `open`, and `not-specified`. Findings have
a non-empty title and keep these layers distinct: evidence, interpretation,
specification impact, repair, and copyable request. Each finding has a unique
ID and is ranked deterministically by impact, certainty, descending
propagation, then ID.

## Mermaid diagrams

Use a diagram block only when its source relationships are supported by the
Wayfinder evidence. A diagram has a title, `diagram_type`, non-empty Mermaid
`source`, and a normal evidence-backed `claim`. Keep one destination or system
flow diagram in `overview` and one problem, impact, or verification-gap
diagram in `review`; do not fabricate unsupported relationships.

The HTML shell loads the pinned Mermaid browser asset with strict security
settings. Mermaid is optional at runtime. The escaped source, an explanatory
fallback, and an accessible error remain readable when JavaScript is absent or
rendering fails.

## Validate and render

Run validation before loading the template or replacing output:

```bash
python3 .github/skills/internal-wayfinder-report/scripts/render_report.py --workspace tmp/.wayfinder/<analysis-slug> --data tmp/.wayfinder/<analysis-slug>/report/report.json --check --format json
```

`--check` emits only bounded metrics and warnings and does not create or
replace `report/index.html`. After it is valid, run the normal render command:

```bash
python3 .github/skills/internal-wayfinder-report/scripts/render_report.py --workspace tmp/.wayfinder/<analysis-slug> --data tmp/.wayfinder/<analysis-slug>/report/report.json
```

The renderer writes only
`tmp/.wayfinder/<analysis-slug>/report/index.html`. It validates the complete
input before loading the template or replacing the output and writes the page
atomically. A custom shell may be supplied with `--template PATH`. See
[compact-authoring.md](references/compact-authoring.md) for source inventory,
hashing, bounded HTML checks, and preservation evidence.

## Completion gate

Before handoff, confirm that:

- the source inventory and source-before hash manifest were captured;
- validation-only preflight passed before rendering;
- the report input uses only the generic five-section contract and closed block vocabulary;
- `report/index.html` exists under the active workspace's `report/` directory;
- bounded HTML parsing confirms the five sections and two diagram roles;
- all Wayfinder source files are byte-for-byte unchanged; and
- unresolved `to-verify` findings and their source links are reported.

Visual review of the generated report is an offline human follow-up. This skill
does not apply repairs, persist review state, contact remote trackers, generate
PDFs or dashboards, install dependencies, or provide compatibility with an
older input contract. SOPS is only a real-world benchmark and does not define
the generic contract.
