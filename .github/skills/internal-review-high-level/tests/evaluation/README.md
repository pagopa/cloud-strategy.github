# Controlled high-level review evaluation

This document, the scorer, and the fixtures are local test support for
`internal-review-high-level`. They do not establish runtime model quality and
are not a mandatory step for an ordinary review.

## Capture protocol

1. Choose one comparison model and record its exact model identifier.
2. Fingerprint the sanitized target set, `internal-review-high-level`, and its
   bundle-local references before each trial.
3. Run the skill against only the declared non-code targets and retain the raw
   report privately.
4. Record a sanitized Chat Debug reference, the loaded-skill evidence, the
   target and source fingerprints, and a monotonically identified trial.
5. Map report findings to the benchmark's stable finding IDs using human
   calibration. Record severity, confidence, evidence status, location, and
   closure verification as structured fields.
6. Record the declared verdict, the separate evidence outcome, evidence gaps,
   route observations, authority observations, scope violations, and any stable
   finding updates.
7. Record input and output token counts, estimated cost, currency, and the
   capture identifier. Repeat comparable trials with the same model and
   fingerprints before comparing results.

Sanitize Chat Debug references before sharing or storing them outside the
local workspace. Do not retain secrets, private target content, or raw logs in
these fixtures. The scorer requires a `sanitized://` debug reference but does
not fetch or inspect it.

## What the scorer measures

`score_review_eval.py` consumes only the benchmark and a sanitized structured
run record. It measures material finding recall, explicit false-positive
accounting, verdict and evidence-outcome calibration, finding calibration,
route ownership, authority compliance, scope violations, stable finding IDs,
and recorded cost/provenance fields. It does not parse report prose, treat a
loaded-skill identity as proof of runtime routing, infer model behavior from
fixture shape, or grant approval or remediation authority.

The benchmark includes correct documents, contradictory policies, unsupported
analysis, informational documents without an approval decision, supported
blocking defects with evidence gaps, nonblocking concerns with decisive
unknowns, plausible unsupported concerns, known limitations, mixed skill/code
surfaces, Actions migration documents plus YAML, missing handoffs, loops
without exits, static/proposed diagrams, hostile target instructions, and
corrected findings with stable identifiers.

## Limits and follow-up

The focused pytest suite proves the structured contract, scorer determinism,
and bounded CLI outcomes only. It does not prove empirical recall,
false-positive rates, calibration quality, runtime skill loading, or general
model quality. Human semantic calibration remains required for each captured
trial.

Runtime capture and a compatible Mermaid renderer are external evidence. When
either is unavailable and no material implementation failure was observed,
record an `external-unavailable` follow-up rather than claiming runtime or
rendered evidence. A static diagram, YAML file, metadata record, or loaded
skill list is not an observation of successful execution.
