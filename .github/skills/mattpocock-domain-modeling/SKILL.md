---
name: mattpocock-domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `GLOSSARY.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

Most repos have a single context:

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `GLOSSARY-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   └── GLOSSARY.md
│   └── billing/
│       └── GLOSSARY.md
```

Create files lazily: only when you have something to write. If no `GLOSSARY.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `GLOSSARY.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update GLOSSARY.md inline

When a term is resolved, update `GLOSSARY.md` right there. Don't batch these up: capture them as they happen. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

`GLOSSARY.md` should be totally devoid of implementation details. Do not treat `GLOSSARY.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

<!-- local-sync:domain-knowledge:start -->
## Repository knowledge contract

This contract overrides conflicting placement, inference, creation, and inline
writing instructions above and in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

- Resolve ownership first: read the repository's declared Area and Topic and
  follow their exact entry in `GLOSSARY-MAP.md`. Resolve links relative to the
  map, not by guessing directory names. Topic names are not globally unique:
  the same Topic in two Areas has two distinct owners.
- Missing or ambiguous owner: ask before any dependent write when the map,
  Area, Topic, or linked glossary is missing, ambiguous, or contradictory.
  Never invent an Area, Topic, or root glossary as a fallback. Use a root
  `GLOSSARY.md` only when the repository explicitly declares it canonical.
  Preserve declared legacy homes without migration or duplicate definitions.
- Obtain write approval: show the exact files and proposed changes, then
  obtain explicit approval for that bounded batch before creating or editing
  a glossary, map, or ADR. Agreement on terminology or shared understanding is
  not write authorization. Changes outside the approved batch need new consent.
- Preserve prepared glossaries: retain the
  `<!-- knowledge:managed:start -->` / `<!-- knowledge:managed:end -->` pair
  and every byte outside it. Missing markers do not authorize adopting the
  whole file; malformed or repeated markers require clarification. Preserve
  resolved definitions and custom content rather than resetting the scaffold.
- Preserve incomplete status: keep `<!-- knowledge:placeholder -->` and
  `Status: placeholder` while required content remains incomplete. Remove the
  notice only when the glossary is substantively complete and that promotion
  is part of the approved batch. Add only resolved, authorized terms; never
  invent definitions to fill a placeholder.
- Keep ADRs central: create new records only in `docs/adr/`, including
  Area-scoped decisions. Follow [ADR-FORMAT.md](./ADR-FORMAT.md), use the
  repository's ADR format and required Area metadata, and keep one central
  numbering sequence. Do not create context-local or Area-local ADR folders.
<!-- local-sync:domain-knowledge:end -->
