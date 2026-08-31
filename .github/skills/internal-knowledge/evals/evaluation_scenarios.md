# Evaluation Scenarios

## Should trigger

### Refresh README directories

**Prompt:** "Refresh the README files for `src/service-a` and `src/service-b` from repository evidence." <!-- knowledge-refs: ignore -->

**Expected:** Load `references/readme-maintenance.md`, normalize the directories to their README destinations, and treat those destinations as the complete write allowlist.

### Refresh an explicit README path

**Prompt:** "Refresh `src/service-a/README.md`; it may already be current." <!-- knowledge-refs: ignore -->

**Expected:** Accept the explicit README path, validate its evidence, and leave a byte-equivalent file untouched when it is already current.

### Refresh a cloud account README

**Prompt:** "Refresh the README for this AWS account Terraform root and explain its execution boundaries."

**Expected:** Separate the logical root, physical account, state boundary, workflow caller, assumed identity, runtime identity, and managed targets only where repository evidence supports each relationship. Do not expose live identifiers or infer trust edges from names.

### Refresh repository architecture

**Prompt:** "Update `docs/architecture.md` to match the current repository."

**Expected:** Load `references/architecture-maintenance.md`, write only `docs/architecture.md`, preserve supported claims, and classify or downgrade uncertain claims from repository evidence.

### Reject an ambiguous architecture root

**Prompt:** "Update the architecture document" from a workspace containing two repository roots without selecting one.

**Expected:** Stop before analysis and ask for the target repository; do not guess a root or write either architecture document.

### Reject an unsafe README target batch

**Prompt:** "Refresh `src/service-a` and `../../outside`." <!-- knowledge-refs: ignore -->

**Expected:** Reject the escaping target before drafting and write zero README files for the batch.

### Preserve a generated README block

**Prompt:** "Refresh this Terraform module README without changing its generated inputs and outputs block."

**Expected:** Preserve the existing generated block byte-for-byte; report a conflict instead of regenerating or rewriting it.

### Record an architectural decision

**Prompt:** "Record our decision to isolate authorization validation by bounded context."

**Expected:** Load `references/adr-maintenance.md`, invoke `/mattpocock-domain-modeling` when the trade-off still needs clarification, apply the local ADR contract, and create a new proposed ADR without modifying accepted ADR bodies.

### Supersede an accepted ADR

**Prompt:** "Change the decision recorded in accepted ADR-0003."

**Expected:** Preserve the accepted body, create a new superseding ADR, and change only the old ADR status when the local contract permits it.

### Guide an unclear request

**Prompt:** "help I want the docs in this repo to make sense to a new joiner"

**Expected:** Resolve `help`, write nothing, and answer with the understood intent, the mode the request would resolve to, the destinations at stake, and one copyable prompt to run. When more than one reading is defensible, offer at most three candidates and ask which applies; never start the work.

### Align repository knowledge from scratch

**Prompt:** "Align the knowledge in `docs` and update all the READMEs in this repository."

**Expected:** Resolve `bootstrap` when the declared layout is absent, incomplete, or contradicted. Load `references/knowledge-scope.md` and `references/knowledge-topology.md`, discover significant components, and present a preflight plan with the exclusion ledger, the resulting topology, one Mermaid diagram, and the current wave. Write nothing before approval.

### Refresh after a new component appears

**Prompt:** "Refresh the repository documentation; we added a new service last month."

**Expected:** Resolve `refresh` because the declared layout is already realized. Include existing documents and the missing README for the new significant component, load `references/knowledge-topology.md` only for that new artifact, and leave already-correct documents untouched.

### Keep a targeted request narrow

**Prompt:** "Refresh `src/service-a/README.md`." <!-- knowledge-refs: ignore -->

**Expected:** Resolve `targeted`, write only that destination, and skip the preflight gate. Report any wider documentation gap instead of authoring it, and do not create a root context document that does not already exist.

### Leave a current repository unchanged

**Prompt:** "Align the repository knowledge again." Run immediately after an accepted alignment.

**Expected:** Evaluate the unchanged predicate for every planned target, report them as `unchanged`, and write zero files. Rewriting for style alone is a defect.

### Refuse an unevidenced domain

**Prompt:** "Bootstrap the knowledge layout with one domain per top-level directory."

**Expected:** Create a domain only where the boundary signals are evidenced. Record the rejected directories in the exclusion ledger, never scaffold empty documentation-mode directories, and state that no relationship is evidenced rather than inventing one between contexts.

### Distrust a declaration that names nothing

**Prompt:** "Align the knowledge in this repository." The agent-facing guide asserts a single-context layout but names no existing artifact, while the repository evidences four domains.

**Expected:** Treat the assertion as a hint rather than a declaration, derive the domain set from evidence, classify the drift, and present the declared layout as a proposal to confirm. Never inherit the declared layout in `bootstrap`, and never write the layout that only the declaration supports.

### Escalate a refresh that understates the repository

**Prompt:** "Refresh the repository documentation." The declared single-context layout is realized, but two domains are evidenced.

**Expected:** Run the layout check, classify the drift as `understated`, escalate the provisional `refresh` to `bootstrap`, and propose recording the domain set as an ADR so later invocations read a decision instead of re-deriving one. Never de-escalate, and never widen a `targeted` request this way.

### Keep a context document to its external format

**Prompt:** "Add the reading order and the component table to the root context document."

**Expected:** Refuse to add sections the external context format does not define. Route the reading order to the agent-facing guide and the root README, route components to section 5 of `docs/architecture.md`, and leave the context document as a glossary.

### Separate a standard from a rule

**Prompt:** "Record our naming convention; a validator already rejects the wrong names."

**Expected:** Recognize that an enforced convention is a rule, not a standard. Load `references/standards-maintenance.md`, record it in the `RULES.md` of the owning domain with an identifier, a severity, and the enforcement owner, and keep it out of `docs/standards/`.

### Report the enforcement gap

**Prompt:** "Align the repository knowledge and make sure it stays correct."

**Expected:** Author the documents, then report which properties would need a check, which existing owner would host it, and what breaks first without it. Do not create or modify a workflow, action, validator, or coverage manifest.

## Should not trigger

### Ordinary documentation edit

**Prompt:** "Correct the spelling in this README paragraph."

**Expected:** Route to `/internal-markdown`; no material README refresh is requested.

### Documentation enforcement

**Prompt:** "Enforce README coverage in CI and add a documentation check to the merge gate."

**Expected:** Do not invoke this skill. Authoring documents is in scope, but installing or modifying a workflow, action, validator, or coverage manifest is not; route the check to its implementation owner.

### Architecture analysis without authoring

**Prompt:** "Explain how the current components depend on each other."

**Expected:** Do not invoke this skill unless the user also asks to create or refresh `docs/architecture.md`.

### Application implementation

**Prompt:** "Add pagination to the users API."

**Expected:** Do not invoke this skill.

## Baseline

Without this skill, an agent may broaden a README refresh beyond the requested targets, overstate architecture from weak evidence, or rewrite an accepted ADR. With this skill, README and architecture authoring remain target-bounded and evidence-based, while ADR authoring follows the local contract and supersedes changed accepted decisions.
