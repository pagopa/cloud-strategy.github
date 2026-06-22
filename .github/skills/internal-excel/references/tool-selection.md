# Tool Selection

Read this reference when scale, file format, or workbook fidelity makes the engine choice non-obvious.

## Quick routing

| Situation | Preferred tool | Why | Notes |
| --- | --- | --- | --- |
| Header sniffing, delimiter detection, exact raw CSV pass | Python `csv` | Minimal dependency and exact text handling | Good for first-pass validation and small streaming transforms. |
| Small or medium CSV or TSV analysis, schema cleanup, reshaping | `pandas` | Familiar transform surface | Prefer when the file fits memory and workbook fidelity is irrelevant. |
| Large local files, multi-file joins, aggregations, SQL-style reconciliation | DuckDB | Fast scans and joins without full in-memory loads | Good for `.csv`, `.tsv`, Parquet, and exported worksheet tables. |
| Columnar scans, type-stable interchange, Parquet or Arrow conversion | PyArrow | Strong schema control and efficient IO | Prefer when conversion fidelity and explicit types matter. |
| Large in-memory transforms with strict schema and speed focus | Polars | Fast columnar execution | Prefer when `pandas` becomes memory-heavy or slow. |
| Reading or updating `.xlsx` cell values while workbook UX is secondary | `openpyxl` | Native workbook access | Stay here only when layout, styles, and rendered review are not the main goal. |
| Formulas, styles, charts, cached recalculation, rendered review, workbook preservation | `openai-spreadsheet` | Workbook UX owner | Route out of this skill. |

## Selection rules

- Start with the smallest tool that can prove or preserve the needed integrity.
- Do not default to `pandas` for files that only need sniffing, counts, or a simple streaming pass.
- Do not use `openpyxl` as a general data-frame replacement; it is slower for heavy tabular transforms and does not evaluate formulas.
- Prefer DuckDB, Polars, or PyArrow when file size or join volume makes full `pandas` loads risky.
- Prefer explicit schema declarations for IDs, dates, currency, and nullable numeric fields when inference could corrupt meaning.
- Preserve original delimiters, quoting, newline style, and column order unless the task explicitly changes them.

## Integrity checks by operation

| Operation | Minimum proof |
| --- | --- |
| Filter or dedupe | Input and output row counts plus kept vs dropped rationale |
| Join or merge | Join cardinality, unmatched keys, and duplicate-key scan |
| Type coercion | Before and after schema, coercion failures, and null increase |
| Conversion between CSV, TSV, XLSX, and Parquet | Row counts plus header equality or a mapped rename log |
| Stable ID generation | Collision scan and deterministic rule |
| Large-file sampling | Sampling is discovery only; full-file validation still applies to transforms |

## Escalation to `openai-spreadsheet`

Route to `openai-spreadsheet` when any of these are first-class requirements:

- formulas or cached recalculation
- charts or workbook layout
- preserving styles, comments, merged cells, or sheet presentation
- rendered review of spreadsheet output
- creating a polished workbook for user delivery
