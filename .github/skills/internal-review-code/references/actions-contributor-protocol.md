# GitHub Actions contributor protocol

This protocol is portable review guidance for `internal-review-code`. It does
not copy native `.github/instructions/` content and does not replace the Addy
review engine.

## Activation

- Activate `internal-github-actions` when the target contains
  `.github/workflows/**`, `.github/actions/**/action.yml`, or
  `.github/actions/**/action.yaml`.
- Activate neither for unrelated code.

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

The record describes observations and evidence for the wrapper and Addy to
evaluate. It is not a review report or a public projection.

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
operations, or planning. The wrapper remains the single public-verdict owner;
Addy remains the sole substantive review engine.

## Unavailable evidence

If target, source, or engine evidence is insufficient for a safe review, the
wrapper returns `REVIEW BLOCKED`. If static review is possible but runtime
capture is unavailable, preserve the local observations and record an explicit
evidence gap; route live evidence to the operations owner as a separate
follow-up.
