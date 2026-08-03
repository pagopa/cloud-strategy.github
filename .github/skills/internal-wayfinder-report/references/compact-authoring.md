# Compact Authoring

Use this procedure to author one bounded report from an active Wayfinder
workspace. Keep source files authoritative and keep generated output under the
workspace's `report/` directory.

## 1. Inventory sources

Set the workspace to `tmp/.wayfinder/<analysis-slug>`. Confirm `map.md`,
`analysis.md`, `issues/`, and `report/report.json` exist. Inventory paths,
byte sizes, issue-file counts, and obvious anomalies without printing full
files:

```bash
find "$workspace" -type f ! -path '*/report/*' -print | LC_ALL=C sort | while IFS= read -r file_path; do wc -c "$file_path"; done
```

Use the inventory to identify the source files that need one controlled read.
Do not treat existing files under `report/` as source authority.

## 2. Hash source authority

Before changing report files, save a deterministic manifest for every
authoritative file outside `report/`:

```bash
find tmp/.wayfinder/<analysis-slug> -type f ! -path '*/report/*' -print | LC_ALL=C sort | while IFS= read -r file_path; do shasum -a 256 "$file_path"; done > tmp/.wayfinder/<analysis-slug>/report/source-before.sha256
```

## 3. Read once and retain notes

Read each distinct source path once in controlled chunks. Retain only
material notes: destination, declared decisions, unresolved questions,
relationships, impacts, and verification boundaries. Use exact physical source
lines for evidence. Do not repair, rewrite, or normalize source files.

## 4. Draft the compact report

Write one generic `report/report.json` with exactly five sections:
`overview`, `solution`, `decisions`, `scope`, and `review`. Include at least
one evidence-backed diagram in `overview` and one in `review`. Keep Mermaid
relationships inside the evidence; do not infer unsupported edges.

Use 12-15 unique evidence entries, no more than three titled findings, and
normally two diagrams as editorial defaults. These are bounded warnings, not
hard rejection limits. Every evidence excerpt must be one non-empty physical
line, occur exactly once in its declared workspace-relative regular file, and
use a unique `(path, excerpt)` pair. Keep findings complete through evidence,
interpretation, specification impact, repair, and request layers.

## 5. Preflight before rendering

Run the validation-only command and fix every contract error before rendering:

```bash
python3 .github/skills/internal-wayfinder-report/scripts/render_report.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --data tmp/.wayfinder/<analysis-slug>/report/report.json \
  --check --format json
```

The command emits only bounded metrics and warnings. It must not load the
HTML template or create or replace `report/index.html`. A valid result may
contain editorial warnings for a complex report.

## 6. Render once

After preflight is valid, render the single artifact:

```bash
python3 .github/skills/internal-wayfinder-report/scripts/render_report.py \
  --workspace tmp/.wayfinder/<analysis-slug> \
  --data tmp/.wayfinder/<analysis-slug>/report/report.json
```

The renderer validates before loading the template and replaces only
`report/index.html` atomically.

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
