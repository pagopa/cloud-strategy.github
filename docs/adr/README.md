# Architectural Decision Records

This directory records repository-wide architectural decisions that explain costly, surprising, or trade-off-driven choices.

## Contents

| ADR | Topic | Level | Serves | Load when |
| --- | --- | --- | --- | --- |
| [ADR-0001](./0001-terraform-skill-routing-boundaries.md) | Terraform skill routing boundaries | tactical | PUR | Changing Terraform skill routing or its implementation boundary. |
| [ADR-0002](./0002-knowledge-domain-layout.md) | Knowledge domain layout | strategic | PUR | Changing the repository's knowledge contexts or their ownership. |

`Level` and `Serves` are index metadata for these existing records; their
bodies remain unchanged. Use `strategic` for a decision that establishes or
changes repository direction and `tactical` for an implementation or
governance choice within that direction. New ADRs state their level next to
status and tactical ADRs name their `Serves:` target.

## Local format

Use sequential filenames in the form `NNNN-<slug>.md`. Each record uses one H1 heading and a concise paragraph describing the context, decision, and rationale. Existing accepted decision bodies are immutable; a changed decision requires a new record that names the superseded record.

## Validation

Check numbering, filename identity, local links, and whether a proposed change preserves accepted ADR bodies before review. Repository-wide Markdown validation is provided by `make docs-lint`.

No diagram is provided because this index has only record-navigation relationships; the domain relationships belong in [CONTEXT-MAP.md](../../CONTEXT-MAP.md).
