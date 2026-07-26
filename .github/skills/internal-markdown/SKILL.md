---
name: internal-markdown
description: Use when editing or reviewing Markdown structure, fences, references, links, paths, or dialect-aware format checks.
---

# Internal Markdown

## When to use

- Markdown edits where generic structure and link safety are the active concern.
- Reviews focused on heading fragments, fenced code blocks, local paths,
  inline links, reference definitions, and dialect awareness.
- Format-owner routing when a document has a narrower operational owner.

## When not to use

- Imported Markdown that must remain verbatim unless explicitly allowed.
- A domain-specific document whose semantics are owned by another skill or
  instruction set.
- Editorial, audience, or policy review beyond Markdown structure and links.

## Baseline

- Preserve fenced-code contents and choose a dialect before judging extensions.
- Keep local paths and link destinations explicit and maintainable.
- Check heading fragments, reference definitions, and link structure without
  treating valid Markdown as a prose-quality verdict.

## Validation

Run the bundle-owned checker with explicit files:

```bash
.github/skills/internal-markdown/scripts/check.sh FILE [FILE ...]
```

The checker returns `0` when checks passed within supported scope, `1` for
format findings, and `2` for usage, dependency, file, or internal failures.
It requires `markdownlint-cli2` 0.22.1 and does not install dependencies.
Supported checks are selected structural link and reference rules. Dialect
choice, external or local filesystem availability, editorial quality, and
heading policy are unsupported and remain review-only.
