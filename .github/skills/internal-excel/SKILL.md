---
name: internal-excel
description: Use when any task reads, creates, edits, validates, converts, or mentions an Excel workbook or an XLSX, XLSM, CSV, or TSV file. Use alongside /anthropic-xlsx when rendered fidelity, charts, cached recalculation, or polished presentation are first-class.
---

# Internal Excel

## Referenced skills

- `anthropic-xlsx`

## When to use

- Any request that reads, creates, edits, validates, converts, or mentions an Excel workbook or an XLSX, XLSM, CSV, or TSV file.
- CSV, TSV, `.xlsx`, or `.xlsm` tasks centered on tabular data quality, profiling, schema choices, normalization, joins, dedupe, reconciliation, conversion, or large-file processing.
- Requests where the main decision is tool selection for scale, memory use, or integrity tradeoffs across local data files.
- Workbook extraction, contract inspection, writer parity checks, or value-level updates where rendered presentation fidelity is not the primary requirement.
- Requests to copy a workbook tab contract into generated tabs: column order, widths, header or body style, money style, alert or error row style, and formula columns.
- Requests where derived workbook columns must stay as Excel formulas and raw source fields remain atomic input values.

## When to add adjacent skills

- For charts, rendered review, cached recalculation, or polished workbook presentation, keep this skill active and add /anthropic-xlsx.
- For single-language implementation work, add the narrower file or runtime owner while this skill retains the spreadsheet integrity contract.
- For database or warehouse design, add the relevant data-platform owner; keep this skill active only while local CSV, TSV, or Excel artifacts remain in scope.

## Boundary

- This skill owns data integrity first: headers, types, nulls, duplicates, joins, reconciliation, stable IDs, delimiter detection, encoding, locale-sensitive numeric fields, and row-count preservation.
- Keep evidence compact for large files: report headers, counts, targeted anomalies, transformation rules, exact validation gaps, and any locale or coercion assumptions that change numeric meaning.
- Treat `.xlsx` and `.xlsm` as workbook containers first. Stay here for tabular extraction, safe value-level transformation, workbook contract inspection, writer parity checks, and formula-column decisions.
- Preserve identifier fidelity before coercion: keep leading zeros, long numeric IDs, and day-first date text exact until an explicit schema rule says otherwise.
- Flag spreadsheet-bound text that could execute as a formula and minimize sensitive-column exposure in samples or logs; apply the safeguards in `references/data-integrity-and-safety.md` when those risks are material.
- Read `references/tool-selection.md` when choosing between Python `csv`, `pandas`, `openpyxl`, PyArrow, Polars, or DuckDB, or when scale, memory use, file format, or workbook fidelity makes the engine choice non-obvious.
- Read `references/large-file-token-discipline.md` when file size, broad profiling, repeated output, sampling strategy, or context pressure could make the tabular workflow expensive.

## Noise Exclusions

- In discovery commands, exclude `.venv`, `__pycache__`, `.pytest_cache`, dependency directories, generated outputs, and binary exports that are not the active evidence target.
- Ignore workbook lock files such as `~$*` and `.~lock.*`.
- Prefer targeted `rg` queries on source files, writer modules, and the named workbook path. Do not start with broad repo scans when the target file or owner path is already known.

## Workbook Contracts

- When a sample workbook or sample tab defines the expected layout, treat that tab as a contract: column order, widths, header style, body style, money style, alert or error row style, and formula columns.
- Verify that every tab produced by the same writer receives the same contract where applicable, not just the sampled tab.
- When the user asks for verifiable formulas, keep derived columns as Excel formulas and keep source columns as atomic input values instead of precomputed results.
- If workbook behavior stays contract-level and formula-level, keep the guidance here without replacing this skill.

## Binary Artifacts

- Do not modify sample workbooks, generated exports, or other binary artifacts unless the user explicitly asks for that edit.
- If output validation needs a generated workbook, write it to `tmp/` or another declared controlled path and report that path.
- Do not include Excel or LibreOffice lock files in discovery, validation, diffs, or deliverables.

## Workflow

1. Confirm the artifact type, row scale, token budget risk, whether workbook fidelity matters, and whether locale-specific numeric conventions or spreadsheet reopening are in play.
2. Pick the narrowest tool that preserves the needed integrity and performance.
3. Inspect headers, sample rows, counts, null patterns, key columns, and locale-sensitive numeric fields before broad transforms.
4. For `.xlsx` or `.xlsm`, inspect metadata and the active workbook contract before broad reads: sheet names, target dimensions, headers, formula counts, style counts, and the relevant writer blocks.
5. Apply deterministic transformations with explicit schema rules for IDs, dates, currency, and decimal text, and keep a reconciliation path for row counts, keys, duplicates, dropped records, and formula-column intent.
6. Re-run focused integrity and safety checks after each material transform or workbook-writer change.
7. Keep this skill as the spreadsheet entry point.

## Validation

- If the local toolchain or bundle exposes a `.venv` or declared runtime, use that runtime for validation instead of ambient Python.
- Run the smallest deterministic check that proves the transform: row counts, schema diff, duplicate-key scan, delimiter or encoding confirmation, locale-sensitive numeric confirmation, join cardinality, or a reconciliation sample.
- For large files, validation output must stay compact: full-file checks should produce aggregate evidence, anomaly counts, sampled examples only when needed, and paths to generated reports instead of inline dumps.
- When data may return to spreadsheet tools, verify formula-injection handling and avoid exposing raw sensitive values in samples or validation output.
- Run `python3 ./.github/scripts/validate_internal_skills.py --skill internal-excel --strict` after editing this skill bundle.
- Run the closest inventory consistency check when registering or renaming the skill.
