# Practice Checklists

## Infinity Loop Scope

Always identify which parts of the DevOps loop are actually in play:

- Plan: requirements, acceptance criteria, risks, success metrics, and infrastructure or deployment needs.
- Code: reviewable change size, team conventions, dependency discipline, and tests written with the change.
- Build: reproducible builds, locked dependencies, artifact versioning, build speed, and vulnerability scanning.
- Test: automated unit, integration, end-to-end, performance, and security checks with clear pass or fail gates.
- Release: release contents, versioning, changelog or release-note hygiene, approvals proportional to risk, and rollback readiness.
- Deploy: infrastructure as code, progressive rollout strategy, deployment verification, blast-radius control, and rollback automation.
- Operate: incident response, runbooks, SLO ownership, capacity planning, configuration hygiene, patching, backups, and disaster recovery.
- Monitor: actionable metrics, logs, traces, alerts, DORA, SLI and SLO signals, plus business feedback that loops back into planning.

## Minimum Operational Controls

Good DevOps guidance should usually account for these controls when relevant:

- CI that gives fast, actionable feedback on every meaningful change.
- Test layers that are automated, repeatable, and not flaky by default.
- Security scanning and dependency hygiene inside the delivery path.
- Release discipline with clear contents, auditability, and rollback preparation.
- Deployment verification instead of assuming success after the pipeline turns green.
- Runbooks, alert ownership, and an incident path that people can actually execute.
- SLI, SLO, and DORA visibility that influences the next planning cycle.

## What Good Looks Like

- Fast feedback in pull requests and CI.
- Clear ownership from commit to production.
- Builds that work from a clean checkout and produce versioned artifacts.
- Observable systems with actionable alerts, useful logs, and correlatable traces.
- Release pipelines that are testable, repeatable, and reversible.
- Post-incident learning that changes the system, not only the document.
