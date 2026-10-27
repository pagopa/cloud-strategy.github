<!-- knowledge:managed:start -->
# Issue Tracker

Keep work state outside durable knowledge.

- Records: use `tracker/<feature-slug>/` for specifications and issues.
  `.scratch/` is the legacy name; migration needs approval.
- Templates: use `tracker/_templates/spec.md` and `issue.md`, not
  `docs/templates/`. Never treat templates as real work or accepted knowledge.
- Specification: include `Area: <area>`, outcome, scope, acceptance checks,
  and evidence. Resolve the Area against the approved Area list.
- Deliverables: place analyses, data, scripts, research, and sources in the
  Area's operational home, not `docs/` or the tracker template directory.
- Migration: rewrite only paths and links in existing tracker records.
  Preserve their facts, state, and wording.
- Authority: this guide grants no new tracker permissions. The tracker owner
  controls live record updates. Creating an Area or Topic and writing
  knowledge still require explicit user approval.
- Promotion: propose durable results through `align harvest`; obtain human
  review and an explicit user "yes" before an authorized knowledge write.
<!-- knowledge:managed:end -->
