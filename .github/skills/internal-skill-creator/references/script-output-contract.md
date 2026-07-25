# Script Output Contract

Use this reference when a skill introduces or materially revises scripts, CLIs, or deterministic automation.

## Contract selection

- JSON is the only common machine-readable contract in this repository guidance.
- `text` is operator presentation, not a machine-readable data contract.
- Add JSON only for a named machine consumer. Do not add machine output speculatively.
- `compact` and `full` are detail profiles of JSON, not separate serializations.
- New interfaces should prefer `--format json --detail compact|full`.
- Existing `--format compact` interfaces may remain compatibility aliases for compact JSON. Do not require repository-wide migration.

## Compact profile

Reduce data before encoding it. Filter, aggregate, deduplicate, rank, and limit deterministic data before returning it.

When applicable, compact JSON must preserve status, material counts, blockers, minimum traceable evidence, truncation state or continuation information, and next action.

Compact output must remain bounded by default. Use domain-named selectors, limits, offsets, or output files instead of silently dropping decision-critical evidence.

## Full profile

Use full JSON only for a named audit, debugging, or durable machine-consumer need. Full does not authorize unbounded stdout; write large complete results to an explicit output file and return a bounded summary.

## Deterministic behavior

- Put successful data on stdout and diagnostics, progress, warnings, and actionable failure context on stderr.
- Document the contract version and validate it with an executable typed contract or pinned JSON Schema dialect when justified.
- Define required and nullable fields, additional-field policy, numeric limits, list ordering, and success or failure representation.
- Serialize deterministically and use standard serializers and parsers.
- Preserve useful failure evidence on non-zero exit and do not emit a misleading success payload.

## Out of scope

TSV, CSV, JSONL, NDJSON, TOON, binary formats, and a universal JSON envelope are out of scope. Reconsider one only through separate evidence: a named consumer, representative fixtures, parser and recovery tests, and a measured advantage over compact JSON.

## Validation

- Verify `--help`, meaningful exit codes, bounds, empty results, parseability, contract conformance, deterministic repeated output, and stdout/stderr separation.
- Exercise quotes, backslashes, controls, Unicode, nulls, booleans, nested values, truncation, and non-zero failures.
- Confirm compact output retains every field required for the next decision.
