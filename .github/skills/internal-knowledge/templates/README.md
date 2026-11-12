<!-- knowledge:managed:start -->
# Managed Setup Templates

These are source templates, not accepted repository knowledge.

| Template | Installed destination |
| --- | --- |
| [Placement block](agents-local-placement.md) | `AGENTS.local.md`, at most 15 lines including markers |
| [Layout guide](layout.md) | `docs/agents/layout.md` |
| [Vocabulary guide](vocabulary.md) | `docs/agents/vocabulary.md` |
| [Promotion guide](promotion.md) | `docs/agents/promotion.md` |
| [Tracker guide](issue-tracker.md) | `docs/agents/issue-tracker.md` |
| [Docs Area README](area-docs-readme.md) | `docs/areas/<area>/README.md` |
| [Work Area README](area-work-readme.md) | `work/<area>/README.md`, or approved root override |
| [Topic Glossary](topic-glossary.md) | `docs/areas/<area>/<topic>/GLOSSARY.md` |
| [Glossary Map](glossary-map.md) | Root `GLOSSARY-MAP.md`, as soon as one Topic exists |

Render `{{...}}` substitutions from approved evidence, never guesses. Link
slots must become Markdown links relative to the installed destination and
must resolve within the approved wave. Use a truthful absence statement
instead of a link when an optional owner does not exist. Keep the entire
rendered content inside the managed markers. Re-setup updates only those
blocks, preserving outside bytes and resolved user content within scaffolds.
Optional viewer frontmatter is separate, narrowly owned metadata as described
in the [Obsidian module](../references/obsidian-vault.md#properties).

Use the [complete setup contract](../references/complete-setup.md) for marker
conflicts, approval, customized content, and idempotence.
<!-- knowledge:managed:end -->
