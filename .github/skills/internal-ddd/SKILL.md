---
name: internal-ddd
description: Use when deciding whether a complex domain needs Domain-Driven Design, defining bounded contexts and ubiquitous language, or choosing which tactical or evented DDD patterns are justified by real domain pressure.
---

# Internal DDD

Use this skill to decide how much Domain-Driven Design a problem deserves, then produce only the artifacts needed for the current stage.

## When to use

- Complex or fast-changing business rules are colliding with implementation structure.
- Teams or services are disagreeing on terms, ownership, or domain boundaries.
- Integration seams are unstable and the domain language is drifting between contexts.
- Auditability, invariants, or workflow coordination make tactical or evented modeling worth evaluating.

## When not to use

- Simple CRUD with stable rules and obvious ownership.
- Localized bug fixes, isolated refactors, or framework-only questions.
- Cases where no domain knowledge or proxy product expertise is available.

## Workflow

1. Run a DDD viability check.
   Confirm at least two signals: domain volatility, model collisions, unstable boundaries, or critical invariants.
2. Choose the working mode.
   Use strategic mode for subdomains and bounded contexts, tactical mode for aggregates and invariants, and evented mode only when integration or workflow pressure justifies it.
3. Produce only the smallest useful artifact set.
   Avoid generating strategic, tactical, and evented deliverables all at once.
4. Record evidence and the next owner.
   End with what was decided, what remains risky, and which adjacent skill or engineering lane should act next.

## Working modes

- Strategic: subdomain map, bounded contexts, ubiquitous language, and boundary ADRs.
- Tactical: aggregates, value objects, domain services, repository contracts, and invariants.
- Evented: commands, domain events, projections, saga boundaries, and rebuild or versioning policy.

## References

- Load `references/mode-selection.md` when deciding whether the work is strategic, tactical, or evented.
- Load `references/ddd-deliverables.md` when you need the concrete artifact checklist and exit criteria.
- Use `internal-change-impact-analysis` when the challenge is incremental adoption inside an existing system.
- Use `internal-oop-design-patterns` when a tactical model needs implementation-level pattern choices.
- Use `antigravity-api-design-principles` when bounded-context seams are turning into API or contract design work.

## Output requirements

Always return:

- domain pressure and assumptions
- selected DDD mode and why
- artifacts produced or required next
- explicit anti-overengineering note when DDD is not justified
- open risks and next recommended lane

## Guardrails

- Do not present this skill as a router; it is a decision and artifact workflow.
- Do not recommend CQRS, event sourcing, or sagas without a clear pressure from workflow complexity or integration boundaries.
- Do not let DDD vocabulary replace concrete domain terms.
