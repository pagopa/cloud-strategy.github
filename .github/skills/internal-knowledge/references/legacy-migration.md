# Legacy Knowledge Migration

Use this reference when relevant inspected documents show a possible owner,
format or layout transition. Detection runs during the current invocation;
it is not a background watcher or a repository-wide scan.

## Proactive detection

Inspect the requested perimeter, its declaration and directly necessary
references under the selected mode's read boundary. In `targeted`, report
wider concerns without escalating or widening scope. In `sync` and `setup`,
use the layout check. In `audit`, findings stay read-only.

Report the assessment, supporting paths, actual coverage, exclusions and the
next evidence or action, even if the user did not notice the drift:

| Assessment | Evidence |
| --- | --- |
| Not needed in the verified perimeter | Existing ownership, meanings and required references are coherent for the requested result. |
| Recommended | A supported newer convention or useful owner split improves maintenance, but the current result remains valid. |
| Necessary for the requested result | A verified blocker cannot be resolved while retaining the current ownership or layout. Explain why a smaller repair is insufficient. |
| Undetermined | Relevant declaration, content, reference or consumer evidence is missing. Name the gap and the next bounded inspection. |

A legacy `CONTEXT` filename alone never makes migration necessary. An optional
glossary with no resolved term may legitimately be absent. A broken link may
need only a repair. Conflicting meanings need semantic resolution before a
move; a rename does not resolve them. Do not label uninspected areas coherent.

## Activation and scope

Present a concrete transfer table before migration: old owner, new owner,
content or stable IDs retained, affected links and anchors, declarations,
indexes, maps, consumers, and exact removals. Distinguish a format or name
change, extraction from a mixed document, and a changed domain or decision.
Only the last may require a new or superseding domain-set decision; a first
glossary or a routine filename change does not require one by itself.

Migration may start immediately in the same conversation after an explicit
authoring request authorizes the concrete scope. Approval of audit findings
alone does not authorize writes. Reuse inspected evidence but recheck changed
paths and authority. Apply the existing `targeted`, `sync`, or `setup` gate;
do not introduce a seventh mode.

Authorize all destinations and each exact deletion. If completion requires
code, policy, configuration, generated outputs or protected records, identify
the owner and report the dependency in `breaking_refs`; do not start a layout
transition that cannot be completed within authorized scope.

## Transfer and verification

Perform one coherent migration unit:

1. Verify the transfer table against current files and incoming references.
2. Create or update canonical destinations, preserving meanings, stable IDs,
   evidence links and required history. Extract only vocabulary into a glossary;
   retain other content with its maintained owner. Preserve accepted ADR bodies.
3. Update authorized declarations, reading order, indexes, maps, links and
   anchors. Use exact references; do not run an unrestricted rename replacement.
4. Verify old-to-new content coverage, new ownership and affected consumers.
   Keep one active canonical owner per claim, with explicit historical ownership
   where required. Do not leave two active copies of the same definition.
5. Remove only explicitly authorized old paths after transfer and reference
   verification. A mixed source may remain for its other responsibilities.
6. Reread the final files and run applicable checks. Claim completion only when
   every required transfer, reference and authorized removal is verified.

The transfer table is working evidence in the conversation, not a second
durable knowledge artifact. Report actual operations through
[knowledge report](knowledge-report.md). Its parser checks path observations,
not semantic equivalence or reference completeness.

## Interrupted migration

Filesystem edits are not guaranteed atomic. On failure, stop dependent edits
and report `migration_state: incomplete`, actual written and removed paths,
completed transfers, remaining obligations and the failure evidence in `gaps`.
Do not claim a removal or transfer that did not occur, or hide a changed file
under `failed`. Explain validation failures for changed files in `gaps`.

Before resuming, reread files, ownership, references and permissions; reconcile
partial copies and concurrent edits. Restore only this invocation's authorized
changes when doing so safely preserves other work. If safe recovery needs new
authority, stop with the exact dependency. Never infer rollback permission for
another person's changes or label the migration complete to bypass recovery.
