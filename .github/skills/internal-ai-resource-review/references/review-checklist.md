# Review Checklist

Use this reference after the profile is selected. Keep the checklist
proportional to the active profile.

## Control pass

Confirm these before drawing conclusions:

- What owns the target resource and what anti-scope should stay outside it?
- What selects or consumes it in practice?
- Which local files, validators, tests, or sync surfaces does it depend on?
- What happens if the resource is stale, missing, oversized, or weakly routed?

## Consumption and flow

Check these when the review is about real usage, not just file quality:

- Activation: how the resource is loaded, selected, or referenced.
- Owner split: whether route, reusable procedure, deep detail, and deterministic
  enforcement stay with the correct owner.
- Phase behavior: whether the resource supports plan, execute, review, sync, or
  handoff roles without silent role mixing.
- Failure behavior: whether missing references, ambiguous targets, or validator
  failures surface clearly.
- Bundle integrity: whether bundle reviews actually cover existing siblings.

## Lifecycle and compatibility

Check lifecycle posture when the decision affects medium-term maintenance:

- Compatibility with paired wrappers, adjacent skills, validators, runtime
  expectations, and naming contracts.
- Propagation requirements across inventory, sync catalogs, runtime matrices,
  and focused tests.
- Periodic review posture: whether the resource has a realistic place in future
  review, maintenance, or refresh work.
- Retirement readiness: whether a resource can be merged, replaced, or retired
  without leaving hollow references or unmanaged sync fallout.

## Quality and context economy

Check these before recommending expansion or extraction:

- Trigger clarity: descriptions and inputs are specific enough to retrieve the
  right owner.
- Boundary clarity: thin wrappers stay thin and deep reusable detail lives in
  references or owned skills.
- Token economy: always-on or prompt-visible content is justified by routing
  value, not convenience.
- Coherence: duplicated owner maps, checklists, or report taxonomies are pushed
  back to one canonical owner.

## Validation and test surface

Check the proof path as part of the review, not as an afterthought:

- Which validator, test, or script proves the resource still works?
- Is the proof path focused and fast enough for the decision being made?
- Are there missing tests for ownership, bundle coverage, inventory, sync, or
  token-risk claims?
- Are retained claims marked as gaps when live evidence is missing?

## Sync and propagation

Review propagation whenever a recommendation would change what ships or syncs:

- `.github/INVENTORY.md`
- explicit allowlists such as home-sync catalogs
- runtime support matrices and sync helpers
- paired prompts, agents, skills, and nearby contract tests

## Drift lens handoff

Load `internal-copilot-audit` instead of cloning its checklist when the review
needs any of these:

- overlap or weak alias detection
- hollow references or missing bundle siblings
- stale contracts, naming drift, or governance drift
- bridge coherence checks between `AGENTS.md` and `.github/copilot-instructions.md`

Use this checklist for qualitative judgment. Keep deterministic enforcement in
validators and tests.
