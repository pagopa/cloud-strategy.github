# Controlled review evaluation

This document and the scorer are test support for `internal-review-code`; they
are not runtime guidance and are not a mandatory step for ordinary reviews.

## Capture protocol

1. Choose one currently supported comparison model and record its exact Chat
   Debug identifier.
2. Fingerprint the seeded target, `internal-review-code`, and
   `addyosmani-code-review-and-quality` before the run.
3. Invoke `internal-review-code` directly against only
   `tests/github/skills/internal-review-code/fixtures/seeded-review-target/`.
4. Verify in Chat Debug that exactly the two mandatory skill bodies are
   present, with their names and resolved sources.
5. Retain the raw report privately and record a sanitized Chat Debug reference.
6. Map evidence-backed report findings to the seeded IDs
   `CAP_101`, `VERSION_BOUNDARY`, `SOURCE_IDENTITY`, and `UTF8_COORDINATE`.
7. Run the deterministic scorer against the manifest and sanitized run JSON.
8. Repeat comparison runs with the same model identifier and fingerprints.

Chat Debug may contain source or terminal content. Sanitize it before sharing
or storing a reference outside the local workspace. The run JSON must record
the model, target fingerprint, `review_skill_sha256`, `engine_sha256`, Chat
Debug reference, loaded skill identities, matched finding IDs, verdict, and
scope violations.

Pytest validates only fixture and scorer behavior. It does not validate review
recall, runtime skill loading, or a model's report quality.
