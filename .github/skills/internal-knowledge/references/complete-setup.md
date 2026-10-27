# Complete Workspace Setup

Prepare usable knowledge and operational documentation in one approved setup.
This reference owns the scaffold exception; ordinary knowledge authoring keeps
its evidence and maturity requirements.

## One setup

- Trigger: an explicit request to set up the whole project or workspace uses
  `setup`, even when its current knowledge layout is realized. A request
  limited to vocabulary, READMEs, or another bucket keeps that perimeter.
  Automatic escalation to `setup` for layout drift does not imply a complete
  installation.
- Plan: inspect existing owners, real project areas, the glossary destination,
  and the tracker guide. Present one exact-path allowlist covering knowledge,
  scaffolds, examples when eligible, and operational documentation. Reuse
  approval already granted for those paths; discovery never expands it.
- Ownership: coordinate both layers through this entrypoint. Keep knowledge
  with its canonical owners and real work with the declared tracker. Reuse
  existing operational guides and templates instead of introducing a parallel
  tracker or requiring separate installation requests.
- Boundary: this branch may prepare documentation templates and examples.
  It does not install executables, workflows, dependencies, runtime settings,
  or validators, edit router policy, or create live work records. Route real
  work through its tracker owner and non-documentation changes to their owners.

## Real domains and mock

Count real project areas from intent and evidence, not directory names alone.

- Real: a user-declared project area, a maintained project README, or a linked
  analysis with an established project purpose counts. A missing README does
  not erase a documented project. Root workspace orientation alone does not
  identify a project area.
- Excluded: technical folders, empty directories, templates, and synthetic
  examples do not count as real domains. Never promote a project folder to a
  technical bounded context without semantic or ownership evidence.
- Placement: use `docs/domains/<slug>/` for newly established project areas.
  Preserve existing canonical homes unless the request authorizes migration.
  A shared glossary can still serve several project areas.
- Zero real domains: propose `docs/domains/mock/README.md` and a small linked
  example specification and issue under its `examples/` directory. Mark every
  example `Status: example` and state that it is synthetic. Keep the example
  self-contained; do not publish fictional tickets to the real tracker.
- One or more real domains: complete those areas and do not create `mock`.
  If a previous mock exists, leave it unchanged and outside the real-project
  index and knowledge coverage. Report its retention; remove it only when
  each exact deletion is explicitly authorized.
- Authority: mock content supplies no accepted definitions, strategic IDs,
  accepted ADRs, requirements, or alignment targets. Never count it as
  evidence that a real knowledge type is covered.

## Scaffolds and authority

Install structure without claiming that its content is resolved.

- Glossary: always prepare the existing canonical glossary destination in
  complete setup. Reuse a legacy vocabulary owner without duplicating it.
  With no declared owner, use the topology's default for the evidenced
  semantic context set; use root `GLOSSARY.md` for a shared single context.
  Without resolved terms, create only its title, placeholder notice, and
  `## Language` section. Do not manufacture a first definition.
- Markers: use `<!-- knowledge:placeholder -->` plus `Status: placeholder`
  for an incomplete knowledge scaffold. Use `<!-- knowledge:template -->`
  plus `Status: template` for reusable operational templates. These markers
  identify artifacts; they are not frontmatter, authority, or executable
  enforcement.
- Additional scaffolds: prepare one only when the approved plan names its
  owner and the concrete reader need it supports. Do not generate all nine
  knowledge types, numbered ADRs, or rules to fill a checklist. A blank section
  guides future input and is not an unresolved candidate claim.
- Operational support: reuse the tracker convention. When it has no templates,
  propose `docs/templates/spec.md` and `docs/templates/issue.md`; include
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
- Conflict: when a required repair cannot preserve current intent, show the
  exact conflict and stop that dependent change for a user decision. Keep
  independent approved work separate; report partial results truthfully.
- Verify: check final links, owner destinations, placeholder and example
  classifications, mock eligibility, and preservation of customized files.
  Distinguish installed structure from confirmed knowledge and real work.
  Report unavailable behavioral evaluation instead of claiming automation.
