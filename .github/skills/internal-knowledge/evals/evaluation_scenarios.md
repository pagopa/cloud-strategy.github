# Evaluation Scenarios

## Should trigger

### Check and create documentation setup

**Prompt:** "Check whether this repository's documentation setup is correct and create the missing structure."

**Expected:** Run `audit`, use `references/documentation-setup.md` for missing structure, run `bootstrap` when the knowledge map is absent, and finish with `audit`.

### Audit ADR and README coverage

**Prompt:** "Audit our ADR numbering and find component READMEs that are not registered."

**Expected:** Select report-only `audit`; do not repair findings.

### Update approved targets

**Prompt:** "Add `docs/guide.md` to the knowledge map." <!-- knowledge-refs: ignore -->

**Expected:** Select `update --target docs/guide.md` and modify only the map.

### Refresh explicit README targets

**Prompt:** "Refresh the README files for `src/service-a` and `src/service-b` from repository evidence." <!-- knowledge-refs: ignore -->

**Expected:** Load `references/readme-maintenance.md` and treat the two targets as the complete README-authoring allowlist. After a successful batch, perform any required knowledge-map registration as a separate bounded operation.

### Refresh a cloud account README

**Prompt:** "Refresh the README for this AWS account Terraform root and explain its execution boundaries."

**Expected:** Separate the logical root, physical account, state boundary, workflow caller, assumed identity, runtime identity, and managed targets only where repository evidence supports each relationship. Do not expose live identifiers or infer trust edges from names.

### Refresh repository architecture

**Prompt:** "Update `docs/architecture.md` to match the current repository."

**Expected:** Load `references/architecture-maintenance.md`, write only `docs/architecture.md`, preserve supported claims, and classify or downgrade uncertain claims from repository evidence.

### Reject an ambiguous architecture root

**Prompt:** "Update the architecture document" from a workspace containing two repository roots without selecting one.

**Expected:** Stop before analysis and ask for the target repository; do not guess a root or write either architecture document.

### Leave a current README unchanged

**Prompt:** "Refresh `src/service-a/README.md`; it may already be current." <!-- knowledge-refs: ignore -->

**Expected:** Validate the evidence and leave a byte-equivalent README untouched, reporting it as unchanged.

### Reject an unsafe README target batch

**Prompt:** "Refresh `src/service-a` and `../../outside`." <!-- knowledge-refs: ignore -->

**Expected:** Reject the escaping target before drafting and write zero README files for the batch.

### Preserve a generated README block

**Prompt:** "Refresh this Terraform module README without changing its generated inputs and outputs block."

**Expected:** Preserve the existing generated block byte-for-byte; report a conflict instead of regenerating or rewriting it.

### CI routing for documentation assets

**Prompt:** "Check whether the knowledge-check action and documentation analysis workflow exist, then tell me who should change them."

**Expected:** Run report-only `audit`, load `references/ci-assets.md`, report presence or absence of the two CI assets, and delegate YAML or runner changes. Do not author GitHub Actions YAML.

### Record an architectural decision

**Prompt:** "Record our decision to isolate authorization validation by bounded context."

**Expected:** Load `references/adr-maintenance.md`, invoke `/mattpocock-domain-modeling` when the trade-off still needs clarification, apply the local ADR contract, and create a new proposed ADR without modifying accepted ADR bodies.

### Supersede an accepted ADR

**Prompt:** "Change the decision recorded in accepted ADR-0003."

**Expected:** Preserve the accepted body, create a new superseding ADR, and change only the old ADR status when the local contract permits it.

## Should not trigger

### Harden a knowledge-check workflow by rewriting YAML

**Prompt:** "Rewrite `.github/workflows/_knowledge-docs-analysis.yml` from this skill so the knowledge check is stricter."

**Expected:** Do not author GitHub Actions YAML. Load `references/ci-assets.md` only to name the assets and delegated owners, then stop.

### Ordinary documentation edit

**Prompt:** "Correct the spelling in this README paragraph."

**Expected:** Use ordinary Markdown editing because no README refresh, architecture contract, ADR, knowledge structure, map, or coverage work is requested.

### Application implementation

**Prompt:** "Add pagination to the users API."

**Expected:** Do not invoke this skill.

## Baseline

On a repository with `README.md` and `docs/guide.md` tracked, `bootstrap` includes both paths and writes only `docs/knowledge-map.yaml`. README and architecture authoring use only the selected target files. ADR authoring follows the local contract and never rewrites an accepted body. On an empty repository, `audit` reports missing structure without writing. `update --all` returns candidates without writing, and a direct update of `AGENTS.md` is blocked. <!-- knowledge-refs: ignore -->
