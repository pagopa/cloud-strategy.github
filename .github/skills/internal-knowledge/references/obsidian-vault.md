# Optional Obsidian Vault

Enable the viewer only when `AGENTS.local.md` declares
`Knowledge viewer: obsidian`. The vault is the repository root, not a nested
folder under `docs/`. Obsidian is a viewer, not the knowledge authority.

## Contents

- [Approval and ownership](#approval-and-ownership)
- [Managed app settings](#managed-app-settings)
- [Graph layers](#graph-layers)
- [Navigation views](#navigation-views)
- [Properties](#properties)
- [Verification and evidence](#verification-and-evidence)

## Approval and ownership

Keep config ownership narrower than file ownership.

- Setup: name `.obsidian/app.json`, `.obsidian/graph.json`, and each generated
  `docs/views/*.base` path in the approved allowlist. An explicit user "yes"
  is required before writing managed config, except config maintenance that
  follows an already-approved Area/Topic change.
- Scope: manage only the app keys below, graph `colorGroups`, and the approved
  navigation views. Preserve all other JSON keys and existing user exclusions.
  JSON and `.base` ownership uses keys or named files, not HTML markers.
- Never touch: `.obsidian/workspace.json`, `appearance.json`, or
  `core-plugins.json`. Do not enable plugins, install Obsidian, alter appearance,
  or edit protected files to make the viewer work. Missing enabled Bases is a
  user action, not permission to change plugin config.
- Maintenance: after an approved Area/Topic create or rename, update affected
  managed queries. A new transient folder needs approval to update exclusions
  unless it is a consequence of that approved change. Identical inputs produce
  no writes; malformed JSON or conflicting ownership blocks the dependent edit.

## Managed app settings

Merge only these keys into `.obsidian/app.json`:

```json
{
  "useMarkdownLinks": true,
  "newLinkFormat": "relative",
  "userIgnoreFilters": ["tmp/"]
}
```

Keep existing ignore entries and add `tmp/` once. Never replace the complete
app config with this fragment. Agents write ordinary relative Markdown links,
never wikilinks. Do not normalize links in accepted ADRs or sources for style.

The official [Settings](https://help.obsidian.md/settings) and
[Internal links](https://help.obsidian.md/links) pages document disabling
Wikilinks and selecting relative paths. Settings documents that excluded files
are hidden from Search, Graph, and unlinked mentions; exclusion does not mean
deletion or removal from disk. The exact persisted key mappings and `tmp/`
filter matching require installed-runtime verification; the UI documentation
does not establish that JSON schema. Do not claim exclusions as a security
boundary or imply that files cannot be opened directly.

## Graph layers

Manage `colorGroups` only in `.obsidian/graph.json`. Derive four groups in this
order from approved paths:

| Layer | Membership | Default RGB |
| --- | --- | --- |
| Glossary / Rules | Topic and Shared Terms `GLOSSARY.md` / `RULES.md`, plus root `GLOSSARY-MAP.md` | `#4e79a7` |
| ADR | Notes under `docs/adr/` | `#f28e2b` |
| Area README | Exact `docs/areas/<area>/README.md` paths, excluding `_` names | `#59a14f` |
| Work | Notes in the declared `work/` operational root or its override | `#b07aa1` |

Use Search queries for membership, not new `type`/`area`/`topic` properties.
For exact files, combine escaped, anchored `path:/.../` regular expressions
with `OR`; derive them from the current Area/Topic list rather than hard-coding
example Areas. The official [Search](https://help.obsidian.md/plugins/search)
page documents path queries, `OR`, and JavaScript-style regular expressions.
Preserve unrelated graph settings and customized group colors when possible.
Do not silently remove user groups: obtain approval for the complete
`colorGroups` result before taking ownership of an existing list.

The official [Graph view](https://help.obsidian.md/plugins/graph) page verifies
query-based color groups, but does not document the persisted `colorGroups`
entry/color schema. Inspect a runtime-produced entry before serializing it;
if unavailable, report the schema as unverified rather than inventing one.
Code repositories without a work tree need no synthetic `work/` group.

## Navigation views

Generate only approved `.base` navigation indexes under `docs/views/`.
They are not knowledge claims. Use valid YAML, not HTML managed markers.
The [Bases syntax](https://help.obsidian.md/bases/syntax) page documents
filters, table views, property order, and dated grouping. The
[Functions](https://help.obsidian.md/bases/functions) page documents
`file.inFolder()` as including subfolders and the string/list functions below.

For `docs/views/active-areas.base`, select docs-side Area READMEs only:

```yaml
filters:
  and:
    - 'file.inFolder("docs/areas")'
    - 'file.path.split("/").length == 4'
    - 'file.path.endsWith("/README.md")'
    - '!file.path.startsWith("docs/areas/_")'
    - 'status == "active"'
views:
  - type: table
    name: Active Areas
    order:
      - file.path
      - note.status
```

For `docs/views/research-by-date.base`, generate an `or` filter with one
`file.inFolder("<operational-home>/research")` per approved home that has
research. This sample needs path substitution before installation:

```yaml
filters:
  and:
    - 'file.ext == "md"'
    - 'file.inFolder("<operational-home>/research")'
    - 'file.hasProperty("retrieved")'
views:
  - type: table
    name: Research by date
    groupBy:
      property: note.retrieved
      direction: DESC
    order:
      - file.path
      - note.source
      - note.retrieved
```

Do not invent a research home when no Area declares one. Exclude sources,
generated files, and `tmp/`; report absent research instead of populating it.
Validate queries in the installed app when possible; a YAML parse does not
prove that a Base renders or that its result set is correct.

## Properties

Add only properties that cannot be derived from paths.

- Area READMEs: `status: active` or `status: archived`. The docs-side README is
  authoritative; the work-side README mirrors it, never decides it. Status is
  lifecycle metadata, not the scaffold's body `Status: placeholder` marker.
- Research notes: operational authors may set `source` and `retrieved`
  (retrieval date in `YYYY-MM-DD` form). The knowledge skill does not author
  research notes.
- Preservation: never add frontmatter to accepted ADRs, `sources/`, generated
  files, or other protected files. Never add path-derived `type`, `area`, or
  `topic`, or new tags merely to make a view work.

YAML frontmatter must precede Markdown. The optional Area `status` key is
managed separately from the README's HTML-managed body block; preserve every
other byte outside that block except the specifically approved status key.
Do not place HTML markers inside frontmatter.

## Verification and evidence

Separate documented semantics from installed-runtime proof.

Official pages above were fetched on 2026-10-27; the help site's HTML shell
loads published Markdown, which was also fetched for Settings, Internal links,
Graph view, Search, Functions, Bases syntax, and
[How Obsidian stores data](https://help.obsidian.md/data-storage). The storage
page verifies that a vault includes subfolders and `.obsidian` lives at its
root; it describes OS-hidden dot folders, not their visibility inside Obsidian.
Installed macOS
`/Applications/Obsidian.app/Contents/Info.plist` reports version **1.14.5**.
No vault UI or config round-trip was exercised in this wave.

Before claiming runtime verification, check link generation, dot-folder
visibility, `file.inFolder()` results, and `tmp/` exclusion from Search/Graph
while its files remain on disk. Official UI semantics are verified above;
JSON key persistence, ignore-filter matching, graph entry serialization, and
installed Bases rendering remain unverified. Dot-folder visibility is not
established by those pages; do not rely on `.scratch/` being visible.
Use visible `tracker/` and leave hidden-file preferences untouched.

Report unavailable checks explicitly. Optional viewer verification must not
block ordinary knowledge maintenance or widen the approved allowlist.
