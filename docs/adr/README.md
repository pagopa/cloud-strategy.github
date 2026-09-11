# Architectural Decision Records

This directory records repository-wide architectural decisions that explain costly, surprising, or trade-off-driven choices.

## Contents

- [0001 Terraform skill routing boundaries](./0001-terraform-skill-routing-boundaries.md)
- [0002 Knowledge domain layout](./0002-knowledge-domain-layout.md)

## Local format

Use sequential filenames in the form `NNNN-<slug>.md`. Each record uses one H1 heading and a concise paragraph describing the context, decision, and rationale. Existing accepted decision bodies are immutable; a changed decision requires a new record that names the superseded record.

## Validation

Check numbering, filename identity, local links, and whether a proposed change preserves accepted ADR bodies before review. Repository-wide Markdown validation is provided by `make docs-lint`.

No diagram is provided because this index has only record-navigation relationships; the domain relationships belong in [CONTEXT-MAP.md](../../CONTEXT-MAP.md).
