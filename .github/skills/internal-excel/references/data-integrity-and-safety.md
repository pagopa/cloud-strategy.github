# Data Integrity And Safety

Use this reference when tabular work risks corrupting meaning, dropping records, leaking sensitive data, or creating spreadsheet-executable output.

## Locale and Excel pitfalls

- Default CSV handling may stay comma-delimited on macOS and Linux, but detect semicolon-delimited or mixed-locale exports instead of assuming them.
- Treat decimal commas, thousands separators, currency symbols, and percentages as schema decisions; prove the chosen normalization rule before coercion.
- Preserve string semantics for identifiers such as CAPs, codes, account numbers, and long numeric IDs when leading zeros or more than 15 digits matter.
- Verify day-first dates and Excel auto-converted values against protected source samples before normalizing them.
- Check encoding early when accented text, smart quotes, or office exports suggest UTF-8 with BOM or Windows-1252.
- Prefer explicit schema declarations for IDs, dates, currency, and nullable numeric fields when inference could corrupt meaning.
- Preserve original delimiters, quoting, newline style, and column order unless the task explicitly changes them.

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
