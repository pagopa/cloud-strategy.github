# Conditional Review Contributor

When this skill is invoked through a routing envelope carrying
`role: domain-routing` and a contributor `deliverable`, contribute observations
for the relevant workflow or composite-action surfaces. Inspect
the static chain from the event through workflow or `workflow_call`, job
permissions and environments, composite actions, repository scripts,
artifacts or caches, and external system boundaries when the target links
them.

When reached for a review, this contributor is selected through the caller's
routing envelope. This skill does not assume a specific gateway or direct
review entry point.

For workflow surfaces, focus on OIDC and least privilege, full-SHA action pins,
input and context validity, reuse contracts, permissions and environment
boundaries, artifact and cache transfers, and the relevant chain links.

For composite-action surfaces, focus on input/output contracts, safe
expression and environment handling, explicit Bash and strict mode,
`$GITHUB_OUTPUT`, supported runtime versions, documentation, smoke behavior,
and failure-path evidence.

Return exactly the contributor record fields required by the caller's
envelope and protocol. The record schema is defined by that envelope; use
`domain: github-actions` for both workflow and composite-action observations.

The caller of the envelope owns any verdict, severity, approval, and merge
decision. This contributor returns only the bounded record defined by the
envelope. Static evidence cannot prove runner health or successful runtime
loading; record that limitation and route live evidence to the operations
owner.
