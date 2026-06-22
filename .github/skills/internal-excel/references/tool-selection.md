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

## Locale and Excel pitfalls

- Default CSV handling may stay comma-delimited on macOS and Linux, but detect semicolon-delimited or mixed-locale exports instead of assuming them.
- Treat decimal commas, thousands separators, currency symbols, and percentages as schema decisions; prove the chosen normalization rule before coercion.
- Preserve string semantics for identifiers such as CAPs, codes, account numbers, and long numeric IDs when leading zeros or more than 15 digits matter.
- Verify day-first dates and Excel auto-converted values against protected source samples before normalizing them.
- Check encoding early when accented text, smart quotes, or office exports suggest UTF-8 with BOM or Windows-1252.

## Integrity checks by operation

| Operation | Minimum proof |
| --- | --- |
| Filter or dedupe | Input and output row counts plus kept vs dropped rationale |
| Join or merge | Join cardinality, unmatched keys, and duplicate-key scan |
| Type coercion | Before and after schema, coercion failures, and null increase |
| Locale-sensitive numeric normalization | Raw samples, chosen decimal or date rule, coercion failures, and proof that protected IDs kept string fidelity |
| Conversion between CSV, TSV, XLSX, and Parquet | Row counts plus header equality or a mapped rename log |
| Stable ID generation | Collision scan and deterministic rule |
| Spreadsheet-bound export | Formula-injection scan or escaping rule plus row-count parity |
| Large-file sampling | Sampling is discovery only; full-file validation still applies to transforms |

## Security and sensitive data

- If CSV or TSV output will be reopened in Excel or LibreOffice, neutralize or flag untrusted text starting with `=`, `+`, `-`, or `@`.
- Keep PII and confidential fields out of logs, chat excerpts, and validation samples unless the task explicitly requires those raw values.
- Prefer hashed, truncated, or representative-key reconciliation when you need to prove joins or duplicates without exposing full identifiers.

## Escalation to `openai-spreadsheet`

Route to `openai-spreadsheet` when any of these are first-class requirements:

- formulas or cached recalculation
- charts or workbook layout
- preserving styles, comments, merged cells, or sheet presentation
- rendered review of spreadsheet output
- creating a polished workbook for user delivery
