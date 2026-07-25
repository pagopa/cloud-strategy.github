---
name: internal-json
description: Use when editing or reviewing repository-owned JSON registry, organization, data, or configuration files that need formatting and consistency rules.
---

# Internal JSON

## Referenced skills

- None.

## When to use

- JSON under registry-like, organization, source, or data paths.
- Repository-owned JSON configuration where no ecosystem-specific owner is stronger.
- Reviews focused on indentation, key order, schema fit, and stable machine-readable structure.

## When not to use

- `package.json`, lock files, or ecosystem-managed JSON with stronger local conventions.
- JSON embedded in Terraform, Kubernetes, or cloud policy work where that domain owner decides the schema.
- Generated JSON unless the task explicitly asks to regenerate or validate it.

## Baseline

- Use 2-space indentation.
- Do not use trailing commas.
- Preserve ecosystem or generator ordering when a tool owns the file.
- Keep keys alphabetical only when the local file pattern already does that or the schema expects it.
- Validate schema when one exists.
- Use technical English for descriptive fields intended for operator output.

## Validation

- Use `python -m json.tool <file>` only for JSON syntax; it does not reject duplicate object keys.
- For consistency checks, prefer the repository JSON validator or a parser configured to reject duplicate keys, such as Python's `object_pairs_hook`.
- Run the owning schema or focused test when the JSON participates in a registry or generated contract.
