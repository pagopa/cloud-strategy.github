<!-- knowledge:managed:start -->
# Knowledge Layout

Keep durable knowledge separate from operational work.

- Knowledge: `docs/README.md` indexes strategic and tactical owners.
  `docs/areas/<area>/README.md` states Purpose, scope, boundary, Topics, their
  Core/Supporting/Commodity roles, and a link to its ADR scope index.
  Keep one ADR at its nearest common scope: `docs/adr/<area>/<topic>/`,
  `docs/adr/<area>/`, or `docs/adr/` for cross-Area and repository decisions.
  Use the approved Area/Topic names, create no empty scope trees, and keep
  numbering global. New ADRs state affected Areas and Topics in their local
  format. The root ADR index links root decisions and Area indexes; Area and
  Topic indexes link applicable shared decisions without copying them.
  Misplaced ADRs require migration before knowledge authoring continues:
  approve exact moves, removals and reference repairs first; otherwise stop.
  Preserve IDs, filenames and accepted bodies. `docs/agents/` contains these guides;
  optional `docs/views/*.base` files are navigation indexes.
- Topics: use `docs/areas/<area>/<topic>/{GLOSSARY,RULES}.md`; create Rules only
  when evidenced. At least one Topic requires root `GLOSSARY-MAP.md`, even for
  a single Topic. Zero Topics means no Area glossary. Root `GLOSSARY.md`
  remains only without declared Areas. Shared Terms live lazily in
  `docs/areas/_shared/`, which is not a Topic.
- Operational home: {{operational_home_declaration}}. Document-only workspaces
  default to `work/<area>/`; `AGENTS.local.md` may override the root name.
  Mirror docs Areas 1:1 only when using that operational tree. `_`-prefixed
  names are reserved and never mirrored. Code repositories declare
  `Operational home:` code paths in each Area README; do not move code.
- Operations: sources, research, analyses, data, scripts, and deliverables
  belong to the operational home, never `docs/`. Local specs use
  `.specs/<area>/<topic>/<feature>/spec.md`; implementation tickets use
  `tmp/.issues/<area>/<topic>/<feature>/`, omitting non-applicable scope levels.
  Incoming issues stay durable in `.issues/`; keep `_templates/` under
  `.specs/` and `.issues/`. Preserve genuine custom paths and remote workflows.
  Legacy standard layouts require approved migration before affected tracker
  writes, not silent moves; retain requirements in a durable source first.
  Follow the tracker guide for scope, discovery and retention.
  `tmp/` is disposable and must not be cited as durable evidence.
- Autonomy: agents may write in `work/<area>/` except `sources/` is add-only
  and generated files change only through their generator. Writes to `docs/`,
  root `GLOSSARY-MAP.md`, `AGENTS.local.md`, and managed Obsidian config need
  an explicit user "yes". Never create Areas or Topics without approval.
  Approved Topic removal archives it, never deletes it.
- Promotion: work-to-docs changes go through `align harvest` and human review.
  The knowledge skill itself writes only Area README scaffolds in `work/`.
- Viewer: if `Knowledge viewer: obsidian` is enabled, use the repository root
  as the vault. An already-approved Area/Topic change may update managed
  viewer config as a consequence. Docs-side Area status is authoritative;
  the work README mirrors it. Use Markdown links, never wikilinks.

{{vocabulary_guide_link}} · {{promotion_guide_link}} · {{tracker_guide_link}}
<!-- knowledge:managed:end -->
