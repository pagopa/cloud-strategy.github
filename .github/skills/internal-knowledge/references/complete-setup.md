# Complete Workspace Setup

Prepare usable knowledge and operational documentation in one approved setup.
This reference owns the scaffold exception; ordinary knowledge authoring keeps
its evidence and maturity requirements.

## Contents

- [One setup](#one-setup)
- [Real Areas and mock](#real-areas-and-mock)
- [Scaffolds and authority](#scaffolds-and-authority)
- [Managed guides and scaffolds](#managed-guides-and-scaffolds)
- [Repeat runs and conflicts](#repeat-runs-and-conflicts)

## One setup

- Trigger: an explicit request to set up the whole project or workspace uses
  `setup`, even when its current knowledge layout is realized. A request
  limited to vocabulary, READMEs, or another bucket keeps that perimeter.
  Automatic escalation to `setup` for layout drift does not imply a complete
  installation.
- Plan: inspect existing owners, real Areas and Topics, glossary destinations,
  and the tracker guide. Present one exact-path allowlist covering knowledge,
  scaffolds, examples when eligible, managed guides and placement block,
  operational README scaffolds, and optional viewer config. Reuse
  approval already granted for those paths; discovery never expands it.
- Ownership: coordinate both layers through this entrypoint. Keep knowledge
  with its canonical owners and real work with the declared tracker. Reuse
  existing operational guides and templates instead of introducing a parallel
  tracker or requiring separate installation requests.
- Boundary: this branch may prepare documentation templates and examples,
  the managed `AGENTS.local.md` placement block, and the narrowly managed
  Obsidian settings in [Obsidian vault](obsidian-vault.md).
  It does not install executables, workflows, dependencies, other runtime settings,
  or validators, edit other router policy, or create live work records. Route real
  work through its tracker owner and non-documentation changes to their owners.

## Real Areas and mock

Identify real Areas and their Topics from intent and evidence, not folder counts.

- Real: a user-declared Area, a maintained project README, or a linked
  analysis with an established project purpose counts. A missing README does
  not erase a documented project. Root workspace orientation alone does not
  identify an Area.
- Excluded: technical folders, empty directories, templates, and synthetic
  examples do not count as real Areas. Never promote a project folder to a
  Topic without semantic or ownership evidence.
- Placement: use `docs/areas/<area>/README.md` for newly established Areas.
  Preserve existing canonical homes unless the request authorizes migration.
  Document-only workspaces also prepare `work/<area>/README.md`, with a
  mandatory 1:1 Area mirror and no `_`-prefixed mirror. Code repositories
  declare existing code paths under `Operational home:`; nothing is moved.
  `AGENTS.local.md` may override the operational root name.
- Zero real Areas: propose a synthetic Area README only with approval and a
  small linked example specification and issue under `tracker/_templates/examples/`.
  Mark every
  example `Status: example` and state that it is synthetic. Keep the example
  self-contained; do not publish fictional tickets to the real tracker.
- One or more real Areas: complete those Areas and do not create `mock`.
  If a previous mock exists, leave it unchanged and outside the real-project
  index and knowledge coverage. Report its retention; remove it only when
  each exact deletion is explicitly authorized.
- Authority: mock content supplies no accepted definitions, strategic IDs,
  accepted ADRs, requirements, or alignment targets. Never count it as
  evidence that a real knowledge type is covered.

## Scaffolds and authority

Install structure without claiming that its content is resolved.

- Glossary: prepare one Topic-local glossary per approved Topic and a root
  `GLOSSARY-MAP.md` as soon as at least one Topic exists. An Area with zero
  Topics has no glossary; do not invent a Topic. Root `GLOSSARY.md` remains
  only without declared Areas. Reuse legacy owners until migration is
  authorized, without duplicating definitions. Without resolved terms, create
  only the title, placeholder notice, and `## Language`; never invent a term.
- Markers: use `<!-- knowledge:placeholder -->` plus `Status: placeholder`
  for an incomplete knowledge scaffold. Use `<!-- knowledge:template -->`
  plus `Status: template` for reusable operational templates. These markers
  identify artifacts; they are not frontmatter, authority, or executable
  enforcement.
- Additional scaffolds: prepare one only when the approved plan names its
  owner and the concrete reader need it supports. Do not generate all nine
  knowledge types, numbered ADRs, or rules to fill a checklist. A blank section
  guides future input and is not an unresolved candidate claim.
- Operational support: use `tracker/<feature-slug>/`, renamed from legacy
  `.scratch/`. Reuse an established local convention until migration is
  approved. When it has no templates, propose `tracker/_templates/spec.md`
  and `tracker/_templates/issue.md`; the spec includes `Area: <area>`,
  outcome, scope, acceptance checks, and evidence prompts as appropriate.
  Keep these reusable forms outside live work records and explain where
  copies belong. Preserve established paths, fields, and status conventions.
- Index: link prepared knowledge separately from confirmed owners, with its
  placeholder status visible. Link operational support separately from
  knowledge coverage. Do not present a template or example as an accepted
  rule, decision, active task, or completed work.
- Promotion: add only resolved, authorized content during later maintenance.
  Keep the placeholder notice while required content is missing; remove it
  only when the owner is substantively complete. Existing acceptance rules
  still control each claim.

## Managed guides and scaffolds

Use the bundle's [templates](../templates/README.md) to prepare the entry chain
`AGENTS.md` → `AGENTS.local.md` → `docs/agents/`. Do not edit `AGENTS.md`; report
a missing local-policy load as a handoff to its instruction owner.

- Guides: install `docs/agents/layout.md`, `vocabulary.md`, `promotion.md`,
  and `issue-tracker.md`. Include them and the `AGENTS.local.md` placement
  block in the approved exact-path allowlist. Keep the placement block at
  most 15 lines, including its managed markers.
- Scaffolds: use the docs-side and work-side Area README templates, Topic
  Glossary placeholder, and Glossary Map template only for approved owners.
  Resolve substitutions and links before writing; do not install broken links
  or an unresolved template as accepted knowledge.
- Work boundary: the skill may scaffold only the Area README in `work/`.
  It never writes sources, research notes, analyses, scripts, or deliverables.
  Operational procedures remain with their declared owners, outside `docs/`.
- Autonomy: guides must say that agents may write in `work/<area>/`, except
  `sources/` is add-only and generated outputs change only via their generator.
  Writes to `docs/`, `GLOSSARY-MAP.md`, `AGENTS.local.md`, and managed Obsidian
  config need an explicit user "yes". Never create an Area or Topic without
  approval; archive, never delete, an approved Topic removal.
- Viewer: load [Obsidian vault](obsidian-vault.md) only when
  `Knowledge viewer: obsidian` is declared in `AGENTS.local.md`. An already
  approved Area/Topic change may update its managed config as a consequence;
  other config writes still require explicit approval.

## Repeat runs and conflicts

Repeat installation must preserve current work.

- Unchanged: an intentional scaffold with its notice, expected sections,
  correct owner links, and no contradictory claims is a valid installed
  artifact. Empty content is not by itself a reason to rewrite it, invent
  knowledge, or report a failed installation.
- Repeat: identical inputs after a complete setup produce zero writes,
  including transient writes. Report unchanged artifacts without updating
  dates, replacing notices, or reformatting files.
- Customized: retain user sections and fields. A difference from a template
  is not permission to reset the file. Repair an evidenced omission only
  within authorized scope and without losing custom content.
- Managed blocks: all installed template content belongs inside exactly one
  `<!-- knowledge:managed:start -->` / `<!-- knowledge:managed:end -->` pair.
  On re-setup, update only that block and preserve every byte outside it.
  Without markers, propose an insertion that preserves existing content; do
  not adopt the whole file as managed. Malformed or repeated markers are a
  conflict, not permission to replace a file. Never reset resolved definitions,
  Purpose, Topic lists, or work indexes to their placeholder templates.
- Config: JSON and `.base` files use the exact key/file ownership contract in
  [Obsidian vault](obsidian-vault.md), not HTML markers. Preserve unknown keys.
- Conflict: when a required repair cannot preserve current intent, show the
  exact conflict and stop that dependent change for a user decision. Keep
  independent approved work separate; report partial results truthfully.
- Verify: check final links, owner destinations, placeholder and example
  classifications, mock eligibility, and preservation of customized files.
  Distinguish installed structure from confirmed knowledge and real work.
  Report unavailable behavioral evaluation instead of claiming automation.
