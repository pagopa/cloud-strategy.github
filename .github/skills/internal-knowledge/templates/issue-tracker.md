<!-- knowledge:managed:start -->
# Issue Tracker

Keep work state outside durable knowledge.

- Owner: retain explicitly configured local paths or remote tracker workflows.
  The local defaults below apply only when no record paths are declared;
  never create local duplicates of remote records.
- Records: specs use `.specs/<feature-slug>/spec.md`; tickets use
  `.issues/<feature-slug>/issues/<NN>-<slug>.md` and link to their source spec.
  Both are durable work records, not disposable `tmp/` artifacts. Keep them
  eligible for version control and report conflicting ignore rules; do not
  stage or commit without a user request.
- Templates: use `.specs/_templates/spec.md` and
  `.issues/_templates/issue.md`, not `docs/templates/`. Never treat templates
  as real work or accepted knowledge.
- Discovery: specs and tickets carry the configured `Status:` roles. Local
  triage scans `.specs/*/spec.md` and `.issues/*/issues/*.md`; implementation
  ticket frontiers scan only the issue files.
- Specification: include `Area: <area>`, outcome, scope, acceptance checks,
  and evidence. Resolve the Area against the approved Area list.
- Deliverables: place analyses, data, scripts, research, and sources in the
  Area's operational home, not `docs/` or the tracker template directory.
- Migration: `.scratch/`, `tracker/`, and `tmp/.issues/` may be established
  legacy homes. Do not move records merely to adopt new defaults. An approved
  transfer may rewrite only paths and links; preserve facts, state, and wording.
- Authority: this guide grants no new tracker permissions. The tracker owner
  controls live record updates. Creating an Area or Topic and writing
  knowledge still require explicit user approval.
- Promotion: propose durable results through `align harvest`; obtain human
  review and an explicit user "yes" before an authorized knowledge write.
<!-- knowledge:managed:end -->
