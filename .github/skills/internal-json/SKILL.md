---
name: internal-json
description: Use when editing or reviewing strict JSON grammar, encoding, duplicate names, numeric interoperability, or format-owner routing.
---

# Internal JSON

## When to use

- JSON edits where strict grammar and interoperable representation are the
  active concern.
- Reviews focused on UTF-8, BOM handling, duplicate object names, ordering
  semantics, numeric portability, and parser-safe strings.
- Routing a file to a stronger ecosystem or domain owner when its semantics
  are the real concern.

## When not to use

- Ecosystem-managed JSON whose owner defines a stronger contract.
- JSON embedded in another domain where that domain owner decides the schema.
- Generated JSON unless the task explicitly asks for format validation.

## Baseline

- Use strict JSON syntax and grammar: no comments, trailing commas, or non-standard
  constants.
- Decode as UTF-8 without a BOM and reject duplicate object names.
- Preserve object order as presentation; JSON object order is not semantic.
- Keep integers within interoperable binary64-safe bounds and reject finite
  numbers outside binary64 range.

## Validation

Run the bundle-owned checker with explicit files:

```bash
python3 .github/skills/internal-json/scripts/check.py FILE [FILE ...]
```

The checker returns `0` when checks passed within supported scope, `1` for
format findings, and `2` for usage, dependency, file, or internal failures.
It uses Python 3.10+ standard-library parsing and does not install
dependencies. Supported checks include strict grammar, UTF-8/BOM handling,
duplicate names via `object_pairs_hook`, non-standard constants, unpaired
surrogates, and numeric interoperability. Schema and content semantics are
unsupported; route them to the domain owner.
