# Knowledge Completion Report

Use this reference for the completion report in every authoring mode. The
report is a compact, machine-readable summary of observed work, not a substitute
for the reader-facing explanation.

## Grammar

Write two or three non-empty prose lines, followed by the exact marker
`knowledge-report/v1`. Then write one `key: value` field per line until a blank
line or end of report. The first prose lines summarize the outcome and assign
each authored target its lifecycle status: `created`, `refreshed`,
`unchanged`, `excluded`, or `failed`. Keep those statuses accurate and do not
claim a file was written when it was not.

`mode` is required and has exactly one value: `help`, `audit`, `align`,
`targeted`, `sync`, or `setup`. Other fields are optional; omit a field
when it has no evidenced value. Each key appears at most once, and values must
not be empty. Use only these keys:

| Key | Meaning |
| --- | --- |
| `mode` | The single resolved skill mode. |
| `bucket` | The requested README or docs filter, when one applies. |
| `signal` | The evidence that selected the mode. |
| `router` | `written`, `unchanged`, `gap`, or `not-applicable`. |
| `written` | Every created or refreshed path, exactly matching observed changes. |
| `unchanged` | Existing planned paths that needed no change. |
| `failed` | Planned paths whose authoring or validation failed. |
| `omitted` | `<path>: <reason>` for required content or diagrams not supplied. |
| `excluded` | `<path>: <reason>` for discovered paths outside the approved scope. |
| `gaps` | Unresolved evidence, ownership, enforcement, or validation gaps. |
| `breaking_refs` | `<path>: <reason>` for code or other non-documentation consumers that need owner action. |
| `diagrams` | `<path>: <reason>` for diagram dispositions, including a recorded cap derogation. |
| `coverage` | Counts of inspected, planned, written, unchanged, excluded, and failed targets, plus checks actually performed when useful. |

Represent path lists as semicolon-separated items. For `omitted`,
`breaking_refs`, and `diagrams`, each item uses `<path>: <reason>`; separate
items with a semicolon and a following space. Keep paths repository-relative
and supported by observed evidence. Do not use prose such as "all files" when
coverage is bounded.

The `written` set must equal the paths actually changed. A path reported as
`unchanged` or `failed` must not also be reported as written. The prose lines
carry the per-target lifecycle status; `written` records only the changed-path
set. This lets a reader distinguish a newly created target from a refreshed
one without changing the stable field vocabulary.

## Truth And Coverage

Resolve status from the final filesystem and the authorized plan. `created`
means the path did not exist before and now exists; `refreshed` means an
existing path changed; `unchanged` means it was considered and left byte-
equivalent; `excluded` means it was considered but not authorized or protected;
`failed` means an authorized target could not be completed. Report each target
exactly once.

Report only checks that ran and what they covered. Distinguish structural
validation, executable checks, human review, and checks not run. Name the
reason when evidence is unavailable. A `not-run` check is a gap, never a pass.
For `audit` and `help`, keep the report consistent with their read-only
contracts and never list authored paths in those reports.

## Problems Found

When material defects or conflicts are discovered, report them to the human in
an optional `## Problems found` section after the machine block, with a blank
line separating it from the final `knowledge-report/v1` field. The section is
required only when material problems were found; omit it otherwise. The blank
line ends the machine block, so this human-facing section does not add fields to
or change the `knowledge-report/v1` parser contract.

Use a table with severity, problem, location, impact, and status columns. Set
status to `verified` or `reported`. Link to an evidenced file location when
available and include a line fragment only when the exact line is supported by
evidence; use a file-only location or `not available` otherwise. Never invent a
path or line number. Do not turn defects into document warnings, disclaimers,
manufactured unknowns, or open questions. Keep `gaps` for its existing meaning:
unresolved evidence, ownership, enforcement, or validation gaps; the human
problem section does not replace it or any required machine field.

Material alignment problems include orphan tactical items, uncovered Direction
items, contradictions, expired Direction horizons, undefined terms, and
references to superseded ADRs.
