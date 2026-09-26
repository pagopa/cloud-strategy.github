# Delegation

Load this writer-local reference only for an explicitly chosen delegated
authoring route. The SKILL.md body keeps the default local tuple and the
exception conditions; this file owns the worker preflight, the delegation
brief and receipt mechanics, and the plan-owner retention statement.

## Worker preflight

Before invoking any worker, materialize the exact retained-plan skeleton and
output path with the final Manifest tuple. Resolve the physical executor
bundle from its loaded runner and run:

```bash
bash <physical-executor-bundle>/scripts/run.sh preflight <skeleton> --format compact
```

A nonzero result or any blocking finding, including `delegation-not-supported`,
prevents dispatch and requires local authoring or a corrected route.

## Delegation brief and receipt

For an explicitly chosen delegated route:

- Fix the objective, value gate, bounded evidence, constraints, exact
  retained-plan write scope, expected output, acceptance, validation, and
  budgets.
- Write one `DelegationBrief` v1 in `mode: plan` through
  `/internal-subagent-contract` before invoking `internal-luna-executor`.
  Bind the single retained-plan path as `write_scope` and
  `expected_output.path`, with the required manifest and preflight acceptance
  plus exact focused validation.
- Record `worker: internal-luna-executor` in the plan authority boundary.
- Luna returns the semantic fields for one `WorkerResult` v1. The runtime
  adapter composes deterministic fields and a caller-owned
  `VerificationReceipt` v1; unobserved validation or budget data stay claims
  or `unavailable`.
- Caller acceptance binds the exact final artifact bytes and manifest semantic
  fingerprint. A material edit invalidates the result and receipt and routes
  one new evidence-bound corrective brief to Luna under the retry contract
  instead of silently transferring authorship to the parent.
- Caller-authorized local continuation begins a fresh local route with the
  local tuple and no inherited worker artifacts.
- Preserve the final-byte physical preflight requirement on either branch.

## Plan-owner retention

The plan owner retains eligibility, control classification, routing, authority,
lifecycle, retry choice, semantic review, independent `preflight`, final
acceptance, handoff, and the no-Git-mutation boundary.
