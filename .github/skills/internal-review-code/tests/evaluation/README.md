# Controlled review evaluation

This document and the scorer are test support for `internal-review-code`; they
are not runtime guidance and are not a mandatory step for ordinary reviews.

## Capture protocol

1. Choose one currently supported comparison model and record its exact Chat
   Debug identifier.
2. Fingerprint the seeded target, `internal-review-code`, and
   `addyosmani-code-review-and-quality` before the run.
3. Invoke `internal-review-code` directly against only
   `.github/skills/internal-review-code/tests/fixtures/seeded-review-target/`.
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

## Conditional GitHub Actions scenario

The `fixtures/actions-review-target/` scenario preserves the generic exact-two
contract and adds an optional `required_conditional_loaded_skills` manifest
field. When present, the sanitized run must provide the ordered
`conditional_loaded_skills` list exactly. The merged Actions scenario expects
the wrapper and Addy engine plus the ordered gateway and
`internal-github-actions` contributor identities for workflow and
composite-action surfaces, and records
workflow-to-composite-to-script observations through explicit finding IDs.

The scorer checks only structured run fields: contributor identity, finding
recall, verdict, and scope violations. It does not parse report prose, prove
runtime routing, or infer runner health from fixture evidence; these loaded
identities are a proxy, not proof of runtime routing or runner health, and it
does not establish model report quality.
Runtime capture, when available, should record the model identity, target and
source fingerprints, loaded identities, finding IDs, verdict, scope
violations, and a sanitized debug reference. If capture is unavailable, retain
the local scenario result and record the limitation as a follow-up.

Native `.github/instructions/` files remain consumer projections with their
own path-specific application metadata. They are inspected as evidence only;
they are not portable contributor sources. Cloud-agent coverage is outside
this scenario.
