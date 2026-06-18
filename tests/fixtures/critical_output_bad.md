## Summary

We are challenging a proposal to add a sync manifest layer between the
governance catalog and consumer repositories. The change matters now because
it rewires the contract that every consumer repo reads and could break
materialization for repositories that already adopted the older layout.

## Findings

### 1. The consumer rollout risk is understated

- **Impact:** Consumer repos mid-migration will lose catalog updates.
- **Evidence:** rollout looks fine — no class is declared.
- **Mitigation:** Ship a v1/v2 manifest reader behind a feature flag.

### 2. The validation cost is hidden

- **Impact:** Each new schema field requires a sync-wide revalidation.
- **Evidence:** `guess` — the contract test must cover every manifest field.
- **Mitigation:** Reuse the existing inventory validator.

### 3. The compatibility window is undefined

- **Impact:** Teams without a documented deprecation timeline stall.
- **Evidence:** `inference` — the proposal does not name a deprecation owner.
- **Mitigation:** Add a deprecation owner and a published window.

### 4. The observability surface drifts

- **Impact:** Drift detection loses signal as the manifest evolves.
- **Evidence:** `inference` — no schema-versioned metrics are described.
- **Mitigation:** Version the manifest metrics in the same change.

## Outcome

`defer-forever`

## Next owner

Route to `internal-gateway-simple-task` to draft the compatibility shim and
the validator reuse notes for the next rollout cycle once the proposal is
finalized end to end and we have a single named owner for the deprecation
window, the rollout flag, the observability plan, and the validation
strategy.
