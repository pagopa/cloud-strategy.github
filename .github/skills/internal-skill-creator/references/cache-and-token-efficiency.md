# Cache and Token Efficiency

Apply when creating or materially revising a skill bundle. Hosts differ in how
they load skills, form reusable prefixes, and account for cached input. Keep
always-loaded content deliberate, then measure from the runtime fields the
host exposes. Vendor reports below are documented claims, not repository-local
measurements.

## Cache model

Prefix reuse depends on the host's cache rules, request layout, and cache
eligibility. Exact-prefix matching and invalidation behavior are documented
for some providers; do not assume another host behaves the same way. Here,
skill descriptions and frontmatter serve routing, `SKILL.md` loads on
activation, and references are selected on demand. Actual request composition
belongs to the runtime. Measure cache behavior from `cached_tokens` or
`cache_read_input_tokens` when the adapter exposes them; otherwise record the
evidence gap. Repository authors do not configure provider breakpoints.

## Cache-stability rules

- Keep always-loaded surfaces deliberate and stable: description, frontmatter
  serialization, section order, projection order, and reference link order.
  A stable revision date describes release history; it is not per-request
  volatility.
- Keep request IDs, session data, generated counts, run telemetry, and other
  changing values out of descriptions and frontmatter. Put them in a reference
  or the conversation when needed.
- Put durable rules before session-specific guidance. Whether placement affects
  cache reuse depends on where the host draws its prefix.
- Batch related contract changes into one coherent revision. A changed prefix
  can reduce reuse on hosts that cache exact prefixes; verify the effect from
  host usage data rather than assuming a universal cost.
- Prefer progressive disclosure when only some branches need the detail. It
  keeps the main skill easier to scan even when cache behavior is unknown.

## Activation budget

Hosts may cap the initial skill list or truncate descriptions. Codex's
documented limit is the lower of 2% of the context window or 8,000 characters;
this host-specific figure does not define other runtimes. Keep descriptions
concise and trigger-first. A session may retain the skill version loaded at
start; after publishing a change, use a new session to check propagation. The
refresh behavior is host-dependent.

## Progressive-disclosure budgets

- Keep the description trigger-focused. A 1,024-character bound is a
  documented authoring convention, not a universal host limit.
- Keep `SKILL.md` concise and move branch-specific detail to references. The
  500-line and 5,000-token figures are practical review budgets, not cross-host
  runtime guarantees.
- Keep references one level deep; add a table of contents beyond 100 lines.
- Put deterministic or repetitive operations in `scripts/` when an executable
  helper is clearer than more instructions.

## Instruction-sediment review

For each retained paragraph, ask whether removing it changes behavior. Remove
no-op guidance and review accumulated instructions on every material revision.
A rule that must always hold belongs in a validator, hook, or permission rather
than prose alone.

## Value measurement

Measure cost per accepted task, not tokens alone. For a material revision,
record before/after line, word, and estimated token counts for the description
and `SKILL.md` body. Use runtime cost and cache fields when available; shorter
text does not guarantee lower cost or equal outcomes.

## Evidence anchors

- Provider documentation describes exact-prefix matching, cache eligibility,
  invalidation, and usage fields for that provider. Treat the details as
  provider-specific.
- Anthropic Agent Skills documentation describes metadata, body activation,
  progressive disclosure, and authoring budgets. Those limits belong to its
  documented environment.
- Vendor-reported production migrations (GPT-5.6 Build Hour and the Ploy case
  study) report lower cost at equal pass rate after append-only on-demand tool
  loading, batching, compaction, smaller tool output, and moving deterministic
  work out of the model. They report volatility near the prompt start as a
  cache failure pattern. These examples have no local reproduction; treat the
  direction as reported evidence and the magnitudes as unverified.
