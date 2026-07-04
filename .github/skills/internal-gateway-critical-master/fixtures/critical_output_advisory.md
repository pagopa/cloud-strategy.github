## Summary

This summary intentionally exceeds the allowed word budget so the validator emits a non-blocking finding while the overall structure still remains valid for strict-mode coverage. It does so by repeating the same narrow point in several different clauses, which is exactly the kind of padding the contract is supposed to reject. The content still looks structurally correct, but the summary itself should cross the seventy-five word threshold and leave the rest of the document usable for strict-mode regression coverage.

## Findings

### 1. The output is still structurally valid

- **Impact:** The content can be reviewed, but it should still trip strict mode because the summary is too long.
- **Evidence:** `inference` - the section uses a valid finding shape.
- **Mitigation:** Shorten the summary back under the limit.

## Synthesis

The output is structurally valid, but the word-budget finding should cause `--strict` to fail.

## Outcome

`accept-with-risk`
