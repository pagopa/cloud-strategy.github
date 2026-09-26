# Conditional Review Contributor

This contributor is selected through a caller's routing envelope that carries
`role: domain-routing` and a contributor `deliverable`. It contributes
observations for the relevant workflow or composite-action surfaces and does
not assume a specific gateway or direct review entry point.

## Inspection chain

Inspect the static chain from the event through workflow or `workflow_call`,
job permissions and environments, composite actions, repository scripts,
artifacts or caches, and external system boundaries when the target links
them.

- **Workflow surfaces:** OIDC and least privilege, full-SHA action pins, input
  and context validity, reuse contracts, permissions and environment
  boundaries, artifact and cache transfers, and the relevant chain links.
- **Composite-action surfaces:** input/output contracts, safe expression and
  environment handling, explicit Bash and strict mode, `$GITHUB_OUTPUT`,
  supported runtime versions, documentation, smoke behavior, and failure-path
  evidence.

## Contributor record

Return only the bounded contributor record whose fields the caller's envelope
and protocol define. Use `domain: github-actions` for both workflow and
composite-action observations.

The caller owns any verdict, severity, approval, and merge decision. Static
evidence cannot prove runner health or successful runtime loading; record that
limitation and route live evidence to the operations owner.
