# Standards Maintenance

Use this reference for the three artifacts that record how a repository works rather than what its words mean: `docs/standards/<name>.md`, `docs/engineering-principles.md`, and `docs/guides/<name>.md`. [Knowledge topology](knowledge-topology.md) decides when they exist; this reference decides what they contain.

## Standard, rule, or principle

The three artifacts look alike and are not interchangeable. Classify before drafting.

| Artifact | What it records | Stable identifier | Automated check |
| --- | --- | --- | --- |
| `docs/domain/<slug>/RULES.md` | An invariant that must hold | Required | Named, or `not enforced` |
| `docs/standards/<name>.md` | A convention the repository follows by agreement | None | None, by definition |
| `docs/engineering-principles.md` | The criteria that decide between alternatives | None | None |

Classify by meaning and owner, not by whether a check exists. A standard is a convention the repository follows by agreement, a rule is a domain invariant, and a principle is a repeated decision criterion. Automated enforcement does not change the semantic category: a check on a convention is enforcement evidence for the standard, while a rule remains a rule because of its invariant. When a rule has no check, record `not enforced` and report the gap.

## Evidence and seeding

Every entry cites the paths that show the repository already practises it. Derive a standard from a shape repeated across unrelated files, from a convention already stated in prose, or from a settled decision that never became a check.

Never invent an entry to fill a section. When an artifact is created with fewer entries than expected, close it with an explicit list of the areas where no convention is established yet. That list is the useful part: it tells the reader the silence is known rather than accidental.

Do not create any of these artifacts empty. A file whose only content is a promise to grow is a placeholder, and a placeholder is a reported gap instead.

## Standards document

```markdown
# <Area> Standards

<One line naming who follows these conventions and where they apply.>

## <Convention>

- Convention: <the statement, in the repository's own vocabulary>
- Evidence: <paths where the repository already follows it>
- Exceptions: <the evidenced exceptions, or `none evidenced`>

## Not established yet

- <Area where no convention is evidenced, and what a reader should do meanwhile.>
```

## Principles document

Record a principle only when the same criterion is visible in two or more independent decisions. One occurrence is an anecdote.

Each principle states the criterion, the trade-off it accepts, and the decisions that evidence it. Link the ADRs that applied it. A principle that no recorded decision ever applied is aspiration, not knowledge.

## Guides

Write a guide only for an evidenced reader task, recovery, troubleshooting journey, or declaration-to-effect chain: identify what the reader does, what consumes it, and what changes as a result. A guide with no consumer describes a machine that does not exist.

- One guide per evidenced reader journey.
- At most three guides per wave.
- Name the guide with a term the repository already uses. A guide named after a concept that appears nowhere in the repository is a sign the chain was inferred.
- State the chain in the repository's own vocabulary. Keep product, provider, and tool names inside the evidence, never in the contract.

## Validation and completion

Verify that every entry cites at least one existing path, that no entry duplicates a rule already carrying an identifier, and that every relative link resolves. Report the created or changed artifacts, the entries added, the areas recorded as not yet established, and any convention that should become a rule.
