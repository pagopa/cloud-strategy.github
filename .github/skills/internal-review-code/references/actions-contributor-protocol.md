# GitHub Actions contributor protocol

This protocol is portable review guidance for the GitHub Actions contributor.
It does not copy native `.github/instructions/` content and does not replace
the declared review engine.

## Activation

- When the target contains `.github/workflows/**`,
  `.github/actions/**/action.yml`, or `.github/actions/**/action.yaml`, the
  caller may use this minimal envelope:

  ```yaml
  role: domain-routing
  parent: internal-review-code
  deliverable: GitHub Actions contributor observations
  evidence: target and linked static evidence
  ```

- The envelope fields are the caller-owned contract. The caller selects and
  invokes the specialist; the specialist returns exactly the contributor
  record schema defined here. Invoke neither contributor for unrelated code.

## Contributor record

Each contributor returns one bounded record with only these fields:

```yaml
domain: github-actions
changed_contract_surfaces: []
observations: []
probes: []
applicable_validations: []
compatibility_risks: []
evidence_gaps: []
```

The record describes observations and evidence for the declared review engine
to evaluate. It is not a review report or a public projection.

## Static chain boundary

When target evidence links the components, inspect the static chain from event
to workflow, reusable workflow or job permissions/environment, composite
action, repository script, artifact, and external-system boundary. Follow only
links present in the target or cited source evidence. Record missing links as
evidence gaps. Do not infer live runner health, successful execution, or
runtime loading from YAML, metadata, or static source.

## Forbidden contributor output

Contributors must not return or derive a public verdict, severity, approval,
merge decision, merge authority, remediation plan, or replacement review
procedure. They must not claim ownership of PR readiness, merge, runtime
operations, or planning. The caller remains the public-verdict owner; the
declared review engine remains responsible for substantive review.

## Unavailable evidence

If target, source, or declared review engine evidence is insufficient for a safe review, the
wrapper returns `REVIEW BLOCKED`. If static review is possible but runtime
capture is unavailable, preserve the local observations and record an explicit
evidence gap; route live evidence to the operations owner as a separate
follow-up.
