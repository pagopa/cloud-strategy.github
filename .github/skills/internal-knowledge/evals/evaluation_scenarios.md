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

## Should not trigger

### Ordinary documentation edit

**Prompt:** "Correct the spelling in this README paragraph."

**Expected:** Route to `/internal-markdown`; no material README refresh is requested.

### Documentation governance

**Prompt:** "Create a documentation map and enforce README coverage in CI."

**Expected:** Do not invoke this skill. Route the map and CI work to their nearest implementation owners.

### Architecture analysis without authoring

**Prompt:** "Explain how the current components depend on each other."

**Expected:** Do not invoke this skill unless the user also asks to create or refresh `docs/architecture.md`.

### Application implementation

**Prompt:** "Add pagination to the users API."

**Expected:** Do not invoke this skill.

## Baseline

Without this skill, an agent may broaden a README refresh beyond the requested targets, overstate architecture from weak evidence, or rewrite an accepted ADR. With this skill, README and architecture authoring remain target-bounded and evidence-based, while ADR authoring follows the local contract and supersedes changed accepted decisions.
