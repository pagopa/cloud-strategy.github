## Summary

We are challenging a proposal to add a sync manifest layer between the
governance catalog and consumer repositories. The change matters now because
it rewires the contract that every consumer repo reads and could break
materialization for repositories that already adopted the older layout.

## Findings

### 1. The consumer rollout risk is understated

- **Impact:** Consumer repos mid-migration will lose catalog updates.
- **Evidence:** `inference` — no compatibility shim is described.
- **Mitigation:** Ship a v1/v2 manifest reader behind a feature flag.
- **Reframe:** Treat the manifest as a contract API, not a config file.

### 2. Validation cost is hidden

- **Impact:** Each new schema field requires a sync-wide revalidation.
- **Evidence:** `confirmed` — the contract test must cover every manifest field.
- **Mitigation:** Reuse the existing inventory validator instead of adding one.

## Synthesis

The strongest risk is the consumer rollout gap; the validation cost is real
but recoverable by reusing existing tooling. The plan can move forward once
the compatibility shim and the validator reuse are agreed.

## Outcome

`execute-clear-next-step`

## Next owner

Route to `internal-gateway-simple-task` to draft the compatibility shim and
the validator reuse notes.
