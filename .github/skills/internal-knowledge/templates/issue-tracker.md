<!-- knowledge:managed:start -->
# Issue Tracker

Keep work state outside durable knowledge.

- Owner: preserve intentional custom paths and remote workflows. An old
  standard-default declaration is not a custom exception. Never infer the
  tracker from folders or duplicate remote records locally.
- Records: specs use `.specs/<area>/<topic>/<feature>/spec.md`; implementation
  tickets use `tmp/.issues/<area>/<topic>/<feature>/<NN>-<slug>.md`, numbered
  from `01` per feature. Incoming issues remain durable under `.issues/`.
- Scope: use the nearest common approved Area/Topic. Omit Topic for Area-wide
  work and Area for cross-Area work or no declared Areas. Unknown applicability
  blocks publication; never invent scope. Feature directories are leaves,
  not scope parents; resolve collisions before writing. Create no empty trees.
- Retention: specs, incoming issues and templates are durable and eligible for
  version control; report conflicting ignore rules. Ticket state and comments
  are temporary. Requirements and acceptance criteria need an authorized
  durable spec or equivalent source before tickets are created. If missing,
  propose it and stop until approved. Link tickets to that source; durable
  records must not depend on temporary tickets for their meaning. Never stage,
  commit or delete records automatically.
- Templates: use `.specs/_templates/spec.md` and
  `.issues/_templates/issue.md`, not `docs/templates/`. Never treat templates
  as real work or accepted knowledge.
- Discovery: recursively scan `.specs/**/spec.md`, configured incoming issue
  records under `.issues/`, and `tmp/.issues/**/*.md` for configured `Status:`
  roles. Exclude every `_`-prefixed segment, templates and examples.
  Implementation frontiers include only the selected feature's tickets.
  Readers use an explicit source reference before configured/default lookup;
  default spec lookup is recursive and ambiguous matches block selection.
- Specification: include `Area:` with all affected values, `Topic:` when
  applicable, outcome, scope, acceptance checks and evidence. Resolve the
  scope against approved Areas and Topics, not directory names alone.
- Deliverables: place analyses, data, scripts, research, and sources in the
  Area's operational home, not `docs/` or the tracker template directory.
- Migration: old standard-default layouts, including `.scratch/`, `tracker/`
  and durable implementation tickets in `.issues/`, require approved migration
  before affected tracker writes. Name each source, destination, removal and
  reference repair; retain unique requirements durably before moving tickets
  into `tmp/`. Preserve records' facts, state and wording. Without approval,
  stop affected writes; read-only operations only report the requirement.
  Unrelated docs, genuine custom paths and remote trackers remain unaffected.
  Do not change Wayfinder or plans in `tmp/.plans/`.
- Authority: this guide grants no new tracker permissions. The tracker owner
  controls live record updates. Creating an Area or Topic and writing
  knowledge still require explicit user approval.
- Promotion: propose durable results through `align harvest`; obtain human
  review and an explicit user "yes" before an authorized knowledge write.
<!-- knowledge:managed:end -->
