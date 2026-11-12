---
name: internal-ddd
description: Use when deciding whether a complex domain needs Domain-Driven Design and framing the current DDD stage from strategic modeling through tactical and evented patterns.
---

# Internal DDD

Decide how much Domain-Driven Design a problem deserves. Produce only the
artifacts needed for the current stage and the next adjacent lane.

## When to use

- Complex or fast-changing business rules collide with implementation
  structure.
- Teams or services disagree on terms, ownership, or domain boundaries.
- Integration seams are unstable and the domain language drifts between
  contexts.
- Auditability, invariants, or workflow coordination make tactical or evented
  modeling worth evaluating.

## When not to use

- Simple CRUD with stable rules and obvious ownership.
- Localized bug fixes, isolated refactors, or framework-only questions.
- Cases where no domain knowledge or proxy product expertise is available.

## Workflow

1. **Run a DDD viability check.** Confirm at least two signals: domain
   volatility, model collisions, unstable boundaries, or critical invariants.
2. **Start with the strategic frame** unless the boundaries are already
   stable. Name subdomains, bounded contexts, language, and translation seams
   before escalating into tactical or evented modeling.
3. **Choose the working mode** from [Working modes](#working-modes).
4. **Produce only the smallest useful artifact set.** Do not generate
   strategic, tactical, and evented deliverables all at once.
5. **Record evidence, success criteria, and the next owner.** End with what
   was decided, what remains risky, and which adjacent skill or engineering
   lane should act next.

## Working modes

- **Strategic**, for subdomains and bounded contexts: subdomain map, bounded
  contexts, ubiquitous language, boundary ADRs, and cross-context translation
  seams.
- **Tactical**, for aggregates and invariants inside a stable bounded context:
  aggregates, value objects, domain services, repository contracts, and
  invariants.
- **Evented**, only when integration or workflow pressure justifies it:
  commands, domain events, read models or projections, CQRS rationale, saga
  boundaries, and rebuild or versioning policy.

## Pressure map

- Boundary and terminology collisions: stay strategic until context ownership
  and translation seams are explicit.
- Weak invariants inside one context: use tactical modeling to decide
  aggregate boundaries, value objects, and enforcement homes.
- Read-write separation, read models, or long-running workflows: treat them as
  evented candidates only when operational pressure is explicit.
- Event history as source of truth: justify it separately from general event
  publication; it is a higher-cost choice than simple domain events.

## Adjacent lanes

- Treat infrastructure boundaries as legitimate bounded-context candidates
  when the real seams are module ownership, environment contracts, or
  repo-level responsibility lines rather than object-oriented code.
- Keep evented design inside this skill until the rationale, ownership, and
  operational cost are explicit enough to hand off safely.

## Guardrails

- This skill decides the DDD stage and artifacts; routing to other owners
  happens only after that decision.
- Recommend CQRS, event sourcing, or sagas only under clear pressure from
  workflow complexity or integration boundaries.
- Keep concrete domain terms; DDD vocabulary never replaces them.

## Output requirements

Always return:

- domain pressure and assumptions
- selected DDD mode and why
- artifacts produced or required next
- success criteria or evidence captured for the current stage
- explicit anti-overengineering note when DDD is not justified
- open risks and next recommended lane

## References

- [`references/mode-selection.md`](references/mode-selection.md): load when
  deciding whether the work is strategic, tactical, or evented.
- [`references/ddd-deliverables.md`](references/ddd-deliverables.md): load
  when you need the concrete artifact checklist and exit criteria.
