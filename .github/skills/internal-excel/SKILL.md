---
name: internal-excel
description: Use when tasks involve CSV, TSV, or Excel tabular data profiling, schema validation, cleanup, joins, conversions, optimization, or large-file integrity.
---

# Internal Excel

## Referenced skills

- `openai-spreadsheet`: on-demand support owner when formulas, workbook layout, charts, rendering, or formatting preservation matter.

## When to use

- CSV, TSV, or `.xlsx` tasks centered on tabular data quality, profiling, schema choices, normalization, joins, dedupe, reconciliation, conversion, or large-file processing.
- Requests where the main decision is tool selection for scale, memory use, or integrity tradeoffs across local data files.
- Workbook extraction or value-level updates where presentation fidelity is not the primary requirement.

## When not to use

- Spreadsheet layout, formulas, charts, styling, rendered review, or preserving workbook presentation as a first-class requirement; use `openai-spreadsheet`.
- Single-language implementation work after the tabular-data approach is already chosen; use the narrower file or runtime owner for that code.
- Database or warehouse design work that is not primarily about local CSV, TSV, or Excel artifacts.

## Boundary

- This skill owns data integrity first: headers, types, nulls, duplicates, joins, reconciliation, stable IDs, delimiter detection, encoding, locale-sensitive numeric fields, and row-count preservation.
- Keep evidence compact for large files: report headers, counts, targeted anomalies, transformation rules, exact validation gaps, and any locale or coercion assumptions that change numeric meaning.
- Treat `.xlsx` as a workbook container. Stay here when the job is tabular extraction or safe value-level transformation. Route to `openai-spreadsheet` when workbook behavior matters.
- Preserve identifier fidelity before coercion: keep leading zeros, long numeric IDs, and day-first date text exact until an explicit schema rule says otherwise.
- Flag spreadsheet-bound text that could execute as a formula and minimize sensitive-column exposure in samples or logs.
- Read `references/tool-selection.md` when choosing between Python `csv`, `pandas`, `openpyxl`, PyArrow, Polars, or DuckDB, or when scale, memory use, file format, or workbook fidelity makes the engine choice non-obvious.
- Read `references/data-integrity-and-safety.md` when delimiter or encoding detection, locale coercion, operation-specific proof, formula injection, or sensitive data exposure are material.
- Read `references/large-file-token-discipline.md` when file size, broad profiling, repeated output, sampling strategy, or context pressure could make the tabular workflow expensive.

## Token Discipline

- Run a token budget gate before inspecting large or unknown-size files: capture file size, format, sheet names or delimiter, cheap row and column counts, headers, encoding clues, and the smallest representative sample needed.
- Do not paste full tables, raw workbook XML, full profiling JSON, or broad command output into chat by default. Report bounded summaries, counts, schema, anomalies, transformation rules, artifact paths, and validation gaps.
- Treat row samples as discovery only. Keep samples small and redacted, then prove transformations with full-file aggregate checks such as counts, key scans, coercion failures, or reconciliation queries.
- Prefer streaming reads, column projection, chunked scans, DuckDB, Polars, or PyArrow for large files. Use full `pandas` loads or full workbook traversal only after size and scope show that the token and memory cost is justified.
- For `.xlsx`, inspect workbook metadata first and read only the target sheets or ranges when possible. Route to `openai-spreadsheet` before spending tokens on layout, formulas, charts, or rendered fidelity.
- Pause before expensive expansions such as dumping more rows, profiling every sheet, loading all columns, or running repeated wide joins. If the user explicitly asks for full output, state the context impact and provide the smallest bounded next slice or a local artifact path.

## Workflow

1. Confirm the artifact type, row scale, token budget risk, whether workbook fidelity matters, and whether locale-specific numeric conventions or spreadsheet reopening are in play.
2. Pick the narrowest tool that preserves the needed integrity and performance.
3. Inspect headers, sample rows, counts, null patterns, key columns, and locale-sensitive numeric fields before broad transforms.
4. Apply deterministic transformations with explicit schema rules for IDs, dates, currency, and decimal text, and keep a reconciliation path for row counts, keys, duplicates, and dropped records.
5. Re-run focused integrity and safety checks after each material transform.
6. Hand workbook UX, formulas, formatting, charts, or rendering follow-up to `openai-spreadsheet`.

## Validation

- Run the smallest deterministic check that proves the transform: row counts, schema diff, duplicate-key scan, delimiter or encoding confirmation, locale-sensitive numeric confirmation, join cardinality, or a reconciliation sample.
- For large files, validation output must stay compact: full-file checks should produce aggregate evidence, anomaly counts, sampled examples only when needed, and paths to generated reports instead of inline dumps.
- When data may return to spreadsheet tools, verify formula-injection handling and avoid exposing raw sensitive values in samples or validation output.
- Run `python3 ./.github/scripts/validate_internal_skills.py --skill internal-excel --strict` after editing this skill bundle.
- Run the closest inventory consistency check when registering or renaming the skill.
