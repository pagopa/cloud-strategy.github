---
name: internal-excel
description: Use when a task reads, creates, edits, validates, converts, profiles, reconciles, or transforms data in an Excel workbook or an XLSX, XLSM, CSV, or TSV file, including casual requests that name such a file as input or output. Use alongside /anthropic-xlsx when rendered fidelity, charts, cached recalculation, or polished presentation are first-class.
---

# Internal Excel

This skill is the spreadsheet entry point and keeps the data-integrity
contract while adjacent owners join.

## Referenced skills

Keep this skill active and add a narrower owner only when its concern becomes
material:

- `anthropic-xlsx`: add `/anthropic-xlsx` for charts, rendered review, cached
  recalculation, or polished workbook presentation.
- For single-language implementation work, add the narrower file or runtime
  owner while this skill retains the spreadsheet integrity contract.
- For database or warehouse design, add the relevant data-platform owner; keep
  this skill active only while local CSV, TSV, or Excel artifacts remain in
  scope.

## When to use

- Any read, write, conversion, profiling, or reconciliation of XLSX, XLSM,
  CSV, or TSV data, including casual requests that name such a file.
- Tabular data quality, profiling, schema choices, normalization, joins,
  dedupe, reconciliation, conversion, or large-file processing.
- Tool selection for scale, memory use, or integrity tradeoffs across local
  data files.
- Workbook extraction, contract inspection, writer parity checks, or
  value-level updates where rendered presentation fidelity is not the primary
  requirement.
- Copying a workbook tab contract into generated tabs, or keeping derived
  columns as Excel formulas over atomic source values.

## Integrity boundary

- Own data integrity first: headers, types, nulls, duplicates, joins,
  reconciliation, stable IDs, delimiter detection, encoding, locale-sensitive
  numeric fields, and row-count preservation.
- Keep evidence compact for large files: report headers, counts, targeted
  anomalies, transformation rules, exact validation gaps, and any locale or
  coercion assumptions that change numeric meaning.
- Treat `.xlsx` and `.xlsm` as workbook containers first. Stay here for
  tabular extraction, safe value-level transformation, workbook contract
  inspection, writer parity checks, and formula-column decisions.
- Preserve identifier fidelity before coercion: keep leading zeros, long
  numeric IDs, and day-first date text exact until an explicit schema rule
  says otherwise.
- Flag spreadsheet-bound text that could execute as a formula and minimize
  sensitive-column exposure in samples or logs.

## Workbook contracts

- When a sample workbook or sample tab defines the expected layout, treat that
  tab as a contract: column order, widths, header style, body style, money
  style, alert or error row style, and formula columns.
- Verify that every tab produced by the same writer receives the same contract
  where applicable, not just the sampled tab.
- When the user asks for verifiable formulas, keep derived columns as Excel
  formulas and keep source columns as atomic input values instead of
  precomputed results.

## Discovery and binary artifacts

- Start from the named workbook, writer modules, and source files. In
  discovery, exclude `.venv`, `__pycache__`, `.pytest_cache`, dependency
  directories, generated outputs, and binary exports that are not the active
  evidence target.
- Exclude Excel and LibreOffice lock files such as `~$*` and `.~lock.*` from
  discovery, validation, diffs, and deliverables.
- Do not modify sample workbooks, generated exports, or other binary artifacts
  unless the user explicitly asks for that edit.
- If output validation needs a generated workbook, write it to a declared
  controlled path and report that path.

## Workflow

1. Confirm the artifact type, row scale, token budget risk, whether workbook
   fidelity matters, and whether locale-specific numeric conventions or
   spreadsheet reopening are in play.
2. Pick the narrowest tool that preserves the needed integrity and
   performance.
3. Inspect headers, sample rows, counts, null patterns, key columns, and
   locale-sensitive numeric fields before broad transforms.
4. For `.xlsx` or `.xlsm`, inspect metadata and the active workbook contract
   before broad reads: sheet names, target dimensions, headers, formula
   counts, style counts, and the relevant writer blocks.
5. Apply deterministic transformations with explicit schema rules for IDs,
   dates, currency, and decimal text, and keep a reconciliation path for row
   counts, keys, duplicates, dropped records, and formula-column intent.
6. Re-run focused integrity and safety checks after each material transform
   or workbook-writer change.

## Validation

- If the local toolchain or bundle exposes a `.venv` or declared runtime, use
  that runtime for validation instead of ambient Python.
- Run the smallest deterministic check that proves the transform: row counts,
  schema diff, duplicate-key scan, delimiter or encoding confirmation,
  locale-sensitive numeric confirmation, join cardinality, or a reconciliation
  sample.
- For large files, keep validation output compact: full-file checks produce
  aggregate evidence, anomaly counts, sampled examples only when needed, and
  paths to generated reports instead of inline dumps.
- When data may return to spreadsheet tools, verify formula-injection handling
  and avoid exposing raw sensitive values in samples or validation output.

## References

- [`references/data-integrity-and-safety.md`](references/data-integrity-and-safety.md):
  apply these safeguards when formula-injection or sensitive-data risks are
  material.
- [`references/tool-selection.md`](references/tool-selection.md): read when
  choosing between Python `csv`, `pandas`, `openpyxl`, PyArrow, Polars, or
  DuckDB, or when scale, memory use, file format, or workbook fidelity makes
  the engine choice non-obvious.
- [`references/large-file-token-discipline.md`](references/large-file-token-discipline.md):
  read when file size, broad profiling, repeated output, sampling strategy, or
  context pressure could make the tabular workflow expensive.
