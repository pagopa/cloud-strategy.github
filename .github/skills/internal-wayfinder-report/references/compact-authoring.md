# Compact Authoring

Use this procedure to author one bounded report from an active Wayfinder
workspace. Keep source files authoritative and keep generated output under the
workspace's `report/` directory.

## 1. Preflight the existing report

Set the workspace to `tmp/.wayfinder/<analysis-slug>`. Validate the existing
`report/report.json` before reading source bodies:

```bash
python3 scripts/render_report.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --data tmp/.wayfinder/<analysis-slug>/report/report.json \
  --check --format json
```

This validation-only check emits bounded metrics and warnings. It must not load
the template or create or replace `report/index.html`.

## 2. Inventory and hash source authority

Confirm `map.md`, `analysis.md`, `issues/`, and `report/report.json` exist.
Inventory paths, byte sizes, issue-file counts, and obvious anomalies without
printing full files:

```bash
find "$workspace" -type f ! -path '*/report/*' -print | LC_ALL=C sort | while IFS= read -r file_path; do wc -c "$file_path"; done
```

Use the inventory to identify every authoritative source path. Before changing
report files, save a deterministic manifest for every authoritative file
outside `report/`:

```bash
find tmp/.wayfinder/<analysis-slug> -type f ! -path '*/report/*' -print | LC_ALL=C sort | while IFS= read -r file_path; do shasum -a 256 "$file_path"; done > tmp/.wayfinder/<analysis-slug>/report/source-before.sha256
```

Do not treat existing files under `report/` as source authority.

## 3. Build one bounded navigation index

At this point, a parent may invoke `internal-luna-executor` through
`/internal-subagent-contract` with a `DelegationBrief` v1 containing the source
paths, authority order, expected output, write scope, acceptance, and
validation. Verify the adapter-composed `WorkerResult` v1 and caller-owned
`VerificationReceipt` v1; treat unobserved validation and budget data as claims
or unavailable evidence. When timeout, interruption, executor unavailability,
or missing terminal output prevents a worker payload, the caller records a
`LifecycleRecord` and creates neither a synthetic `WorkerResult` nor a
`VerificationReceipt`. The parent retains source authority, findings, diagram
relationships, retry choice, and closeout.

Run the read-only helper once after inventory and hashing:

```bash
python3 scripts/collect_source_notes.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --format json \
  --max-preview-lines 12
```

The helper output is navigation-only, not source authority. It must remain
bounded and must not be redirected into a source or report input file.

## 4. Read every source once and retain bounded notes

Read every authoritative source path once in controlled ranges guided by the
index. Complete coverage is required for `map.md`, `analysis.md`, every regular
file below `issues/`, and other local analysis assets. Retain only destination,
final decisions, explicit corrections, unresolved questions, relationships,
impacts, and verification boundaries. Use exact physical source lines for
evidence; the helper's windows never replace those lines.

Full source dumps, raw debug logs, repeated reads, and iterative warning cleanup
are out of scope. Do not repair, rewrite, or normalize source files.

## 5. Draft the compact report shape

After the parent fixes sections, evidence IDs, findings, diagram roles,
acceptance, and validation, it may invoke `internal-luna-executor` through
`/internal-subagent-contract` for drafting. Do not delegate source authority,
findings, diagram relationships, acceptance, or closeout; use the common brief
and result protocol and the caller-owned retry budget.

Choose the generic five-section skeleton, evidence IDs, findings, and two
diagram roles before editing. Write one `report/report.json` with exactly five
sections: `overview`, `solution`, `decisions`, `scope`, and `review`. Include at
least one evidence-backed diagram in `overview` and one in `review`.

Use 12-15 unique evidence entries, no more than three titled findings, and
normally two diagrams as editorial defaults. These are bounded warnings, not
hard rejection limits. Every evidence excerpt must be one non-empty physical
line, occur exactly once in its declared workspace-relative regular file, and
use a unique `(path, excerpt)` pair. Keep findings complete through evidence,
interpretation, specification impact, repair, and request layers.

Keep Mermaid relationships inside the evidence; do not infer unsupported
edges.

## 6. Validate, render, and preserve once

Write `report/report.json` once, then run validation-only preflight again and
fix every contract error before rendering:

```bash
python3 scripts/render_report.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --data tmp/.wayfinder/<analysis-slug>/report/report.json \
  --check --format json
```

After preflight is valid, render the single artifact:

```bash
python3 scripts/render_report.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --data tmp/.wayfinder/<analysis-slug>/report/report.json
```

The renderer validates the complete input before loading the template or
replacing the output and writes only
`tmp/.wayfinder/<analysis-slug>/report/index.html` atomically.

## 7. Run bounded HTML checks

Confirm the output is non-empty and inspect it through parsing and targeted
counts rather than dumping minified markup:

```bash
test -s tmp/.wayfinder/<analysis-slug>/report/index.html
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path

class Counts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.diagrams = 0
        self.findings = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id") in {"overview", "solution", "decisions", "scope", "review"}:
            self.ids.append(attributes["id"])
        classes = set(attributes.get("class", "").split())
        self.diagrams += "diagram" in classes
        self.findings += "finding-disclosure" in classes

page = Path("tmp/.wayfinder/<analysis-slug>/report/index.html").read_text(encoding="utf-8")
counts = Counts()
counts.feed(page)
print({"sections": counts.ids, "diagrams": counts.diagrams, "findings": counts.findings})
if counts.ids != ["overview", "solution", "decisions", "scope", "review"] or counts.diagrams < 2:
    raise SystemExit(1)
PY
```

Keep checks bounded: do not run unbounded `rg`, `grep`, or full-file output over
the one-line generated document. Use standard-library parsing for structured
checks and targeted byte counts for compactness.

## 8. Verify preservation and follow-up

Run the saved hash manifest after rendering:

```bash
shasum -a 256 -c tmp/.wayfinder/<analysis-slug>/report/source-before.sha256
wc -c tmp/.wayfinder/<analysis-slug>/report/report.json tmp/.wayfinder/<analysis-slug>/report/index.html
```

Every authoritative source must report `OK`. Report any editorial warnings and
`to-verify` findings with their source links. Visual review at desktop, mobile,
and print widths is a human follow-up; it does not replace contract checks or
permit source changes.
