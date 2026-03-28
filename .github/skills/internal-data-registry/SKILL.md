---
name: internal-data-registry
description: Safely update structured JSON/YAML registry files such as users, groups, teams, repositories, or policy maps. Use when the user needs to add, remove, or modify entries in authorization registries, team configurations, permission maps, or any structured data file that follows a registry pattern.
---

# Data Registry Skill

## When to use
- Add or update records in structured JSON/YAML data files.
- Apply naming/order conventions across registry-like data.
- Validate referential integrity between related data files.

## Mandatory rules
- Preserve existing schema and file format.
- Keep keys ordered when repository convention requires it.
- Avoid duplicate identifiers and conflicting records.
- Keep comments/documentation in English.
- Keep changes minimal — modify only the requested entries.

## Integrity checks
- Unique IDs, names, usernames, emails, and slugs.
- Cross-file references point to existing entries.
- Required fields are present for each object.
- Sort order follows repository conventions.
- No orphaned references after deletions.

## Minimal example
```json
{
  "id": "example-user",
  "email": "example@company.com",
  "role": "read"
}
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Adding an entry without checking for duplicates | Silent conflicts, non-deterministic behavior | Search existing entries by ID/email/slug before adding |
| Deleting a record without checking cross-references | Orphaned references in other registry files | Trace all files that reference the record before removing |
| Changing key sort order inconsistently | Noisy diffs that obscure real changes | Match the existing ordering convention in the file |
| Mixing formats (JSON in a YAML file or vice versa) | Breaks parsers downstream | Preserve the original file format exactly |
| Leaving placeholder values (`TODO`, `TBD`, `example@`) | Passes validation but causes runtime failures | Use real values or omit optional fields |

## Cross-references
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for reviewing registry change PRs.
- **internal-pair-architect** (`.github/skills/internal-pair-architect/SKILL.md`): for impact analysis when modifying authorization registries.

## Validation
- Run repository checks for JSON/YAML syntax.
- Run domain-specific validation scripts when available.
- Verify referential integrity across related files.
- Keep changes minimal and scoped to requested records.
