<!-- knowledge:managed:start -->
# Knowledge Layout

Keep durable knowledge separate from operational work.

- Knowledge: `docs/README.md` indexes strategic and tactical owners.
  `docs/areas/<area>/README.md` states Purpose, scope, boundary, Topics, their
  Core/Supporting/Commodity roles, and links to decisions. All ADRs live in
  `docs/adr/`; new ADRs carry `Area:`. `docs/agents/` contains these guides;
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
  belong to the operational home, never `docs/`. Tracker records belong to
  `tracker/<feature-slug>/`, templates to `tracker/_templates/`.
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
