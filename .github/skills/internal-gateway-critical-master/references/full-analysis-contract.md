# Full Analysis Contract

`internal-gateway-critical-master` has one output mode:
`internal-gateway-critical/full-analysis-v1`.

The output is one UTF-8 JSON object. Markdown, prose, emoji cards, headings,
and code fences are not valid output.

## Packet shape

The packet has exactly these top-level keys:

`schema`, `source`, `target_path`, `target_revision`, `outcome`, `findings`,
`residual_risks`, `diagnostics`.

`schema` is exactly `internal-gateway-critical/full-analysis-v1`.
`source` is `standard` or `independent`. `target_path` is a repository-relative
POSIX path. `target_revision` is a positive integer supplied by the caller and
must match the living design revision.

`outcome` is exactly one of:

- `accepted`: no blocking finding and no diagnostics.
- `revise-design`: at least one finding requires a design remedy.
- `reopen-analysis`: at least one finding is blocking and the assumptions or
  scope must be reopened.
- `needs-clarification`: a blocking finding is tied to an unresolved user
  decision.
- `invalid-target`: the target or required evidence is invalid; diagnostics
  are required.
- `request-separate-review`: an independent review is required; `source` must
  be `independent` and diagnostics are required.

`findings`, `residual_risks`, and `diagnostics` are arrays. String arrays contain
non-empty unique strings. Each finding has exactly these keys:

`id`, `critique`, `recommendation`, `reason`, `blocking`, `evidence`.

Finding IDs are unique packet-local strings matching `^C-[0-9]{3}$`.
`critique`, `recommendation`, and `reason` are non-empty strings. `blocking` is
a boolean. `evidence` is a non-empty array of unique strings.

Malformed JSON, Markdown fences, unknown or missing keys, invalid nested values,
path mismatch, revision mismatch, and outcome-invariant failures are invalid
packets. They must not be treated as review passes.

## Ownership

The critic produces the packet and includes every material finding from the
full-scope challenge. `internal-gateway-idea` validates the packet, binds it to
the current target revision, consolidates equivalent findings, renders any
localized user-facing view, and owns state transitions.

The producer is never replaced by a compact card or an early-stop summary.
