# Review Contributor

Use this reference when a caller such as `internal-review-code` invokes the
skill with an envelope that carries `role: domain-routing`,
`parent: <caller>`, and a contributor `deliverable`.

## Boundary

- Contribute observations only. Do not invoke the parent again and do not
  route the work elsewhere.
- The caller owns every verdict, severity, approval, merge decision, and
  follow-up. Separate follow-ups go to their deliverable owner, not through
  this skill.
- Static evidence cannot prove runner health or runtime loading. Record that
  limit as an evidence gap; live runner or fleet evidence belongs to
  `internal-github-platform`.

## Inspection chain

Inspect the static chain from the event through the workflow or
`workflow_call`, job permissions and environments, composite actions,
repository scripts, artifacts or caches, and external system boundaries when
the target links them.

- **Workflow surfaces:** OIDC and least privilege, full-SHA pins, input and
  context validity, reuse contracts, environment boundaries, artifact and
  cache transfers.
- **Composite-action surfaces:** input and output contracts, `env:`
  forwarding, `shell: bash` and strict mode on `run:` steps, `$GITHUB_OUTPUT`
  mapping, documentation, smoke and failure-path evidence.

## Contributor record

Return exactly one record with these fields and nothing else:

```yaml
domain: github-actions
changed_contract_surfaces: []
observations: []
probes: []
applicable_validations: []
compatibility_risks: []
evidence_gaps: []
```
