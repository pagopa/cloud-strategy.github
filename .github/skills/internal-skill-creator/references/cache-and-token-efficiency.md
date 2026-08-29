# Cache and Token Efficiency

Apply when creating or materially revising a skill bundle. Every always-loaded
token is paid on every turn, and every byte change to a loaded prefix re-pays
the cache write. Source anchors: OpenAI prompt caching, Anthropic prompt
caching and Agent Skills docs, and the GPT-5.6 valuemaxxing migration evidence
recorded below.

## Cache model

Prompt caching is prefix caching with exact matching, not a similarity cache.
The cacheable prefix is ordered `tools → system → messages`; a change at one
point invalidates that point and everything after it. Skill descriptions and
frontmatter sit in the always-loaded prefix; `SKILL.md` loads on activation;
`references/` load on demand. Measure cache behavior from runtime usage fields
(`cached_tokens`, `cache_read_input_tokens`) only when the adapter exposes
them; otherwise record the evidence gap. Repository skill authors do not place
provider breakpoints; the runtime does.

## Cache-stability rules

- Keep every always-loaded surface byte-stable: description, frontmatter
  serialization, section order, projection order, and reference link order.
- Prohibit volatile content in every cached surface: `SKILL.md`, frontmatter,
  and descriptions. Timestamps, session or request IDs, generated counts, run
  telemetry, and dates belong in on-demand references or in the conversation,
  never in a cached prefix.
- Order content stable-to-volatile inside every file: durable rules first,
  session-specific guidance last. A volatile sentence at the top of a body
  costs the whole prefix; at the end it costs nothing behind the breakpoint.
- Batch contract changes. Each published edit to a loaded prefix re-pays the
  cache write for every consumer; prefer one coherent revision over a trail
  of small edits, which also matches the smallest-coherent-bundle rule.
- Prefer progressive disclosure over inline growth: on-demand references keep
  the prefix intact while still adding capability, the same way append-only
  on-demand tool loading preserves a KV cache.

## Activation budget

Hosts cap the initial skill list. Codex uses at most 2% of the context window,
or 8,000 characters, and shortens or omits descriptions when the limit is
exceeded, so keep descriptions short and trigger-first. Runtime sessions
snapshot skills at start; restart the runtime after publishing a skill change
before validating it.

## Progressive-disclosure budgets

- Description: trigger-focused, at most 1,024 characters.
- `SKILL.md` body: under 500 lines and under 5,000 tokens; split when
  approaching the limit.
- References: one level deep; add a table of contents beyond 100 lines.
- Deterministic or repetitive operations belong in `scripts/`: execution
  returns output without loading source into context.

## Instruction-sediment review

For every retained paragraph, ask whether removing it changes behavior; if
not, delete it. Newer models need less explicit instruction, so audit
accumulated rules on every material revision instead of only adding. A rule
that must always hold goes to a validator, hook, or permission, not prose.

## Value measurement

Measure cost per completed task, not tokens consumed. For a material
revision, record before/after line, word, and estimated token counts for the
always-loaded surfaces (description and `SKILL.md` body). A shorter cached
prefix still wins twice: lower per-turn input cost and smaller cache writes.

## Evidence anchors

- Exact-prefix matching, cache invalidation, ordering, and usage fields:
  OpenAI prompt caching and Anthropic prompt caching documentation.
- Metadata-always-loaded, body-on-activation, budgets, scripts-over-prose:
  Anthropic Agent Skills overview and authoring best practices.
- Vendor-reported production migrations (GPT-5.6 Build Hour, Ploy case study)
  report the same direction of effect: append-only on-demand tool loading,
  cross-chat breakpoints on the system prompt and tools, batched multi-action
  tool calls, compaction, slimmed tool output, and moving deterministic work
  out of the model each cut cost at equal pass rate, and volatile data placed
  at the prompt start was the recurring cache-breaking failure. These figures
  have no repository-local reproduction; treat the direction as guidance and
  the magnitudes as unverified.
