# Working Hypothesis Log: Copilot Catalog Optimization

This file is a working artifact, not an execution plan.

Its purpose is to track hypotheses about overlap, instruction-load pressure, and governance gaps that still need evidence. Claims in this file should either:

- cite current repo evidence
- be explicitly framed as a hypothesis
- be deferred until the validator or reporting tools can measure them

---

## Current evidence worth acting on

### 0. Imported resources are not optimization targets

Repository rule:

- non-`internal-*` resources are imported upstream assets and must remain verbatim
- repository-specific behavior belongs in `internal-*` wrappers, extensions, and routing assets

Implication:

- no optimization action in this file should propose editing, trimming, deleting, or renaming non-`internal-*` resources
- when an imported resource is too broad or too heavy, the response must happen in local `internal-*` assets or in import-management workflow, not by rewriting the imported file in place

### 1. Large external instructions are the real load hotspots

Measured line counts from the current repository:

- `awesome-copilot-terraform-azure.instructions.md`: 254 lines

By contrast, the matching internal instructions are compact:

- `internal-github-actions.instructions.md`: 44 lines
- `internal-docker.instructions.md`: 31 lines
- `internal-terraform.instructions.md`: 52 lines
- `internal-terraform-azure.instructions.md`: 64 lines

Implication:

- optimization should target how local `internal-*` wrappers interact with large imported instructions, not the imported instructions themselves
- where the user explicitly decides to absorb an imported instruction into an `internal-*` counterpart, the imported file can be retired after the internal instruction becomes self-sufficient
- compact internal instructions should be left alone unless a contradiction or measurable overlap problem is proven

### 2. Terraform overlap is real, but must be measured by effective load sets

Current `applyTo` patterns show that Terraform files can load several instructions together:

- `internal-terraform.instructions.md` -> `**/*.tf`
- `internal-terraform-azure.instructions.md` -> Azure-specific Terraform patterns
- `awesome-copilot-terraform-azure.instructions.md` -> broad Terraform and Terraform-adjacent Azure patterns

Implication:

- the risk is not “duplicate globs” in isolation
- the risk is the effective instruction set loaded for representative file paths such as generic Terraform, Azure Terraform, workflow YAML, and Docker files

### 3. Governance should guard against stale declared skills

The repo should treat agent `## Declared Skills` as a real contract, not decorative prose.

Actionable contract:

- every declared skill must resolve to `.github/skills/<name>/SKILL.md`

### 4. Routing clarity still benefits from sharper boundaries

Useful routing distinctions to preserve and clarify:

- cloud-agnostic architecture vs cloud-specific strategy
- in-repo catalog governance vs cross-repository baseline propagation
- defect-first code review vs change-impact analysis

---

## Claims intentionally rejected or downgraded

### Rejected: internal Terraform deduplication as a high-priority optimization

This was stale.

The current internal Terraform instructions are already compact and clearly split between shared baseline and cloud-specific rules. Further consolidation is likely to save little while weakening specificity.

### Rejected: line-count-driven prioritization across the whole catalog

Some earlier counts and line totals were outdated.

Use current measured counts or do not claim priority.

### Rejected: broad skill expansion or retirement based on intuition

Short skills are not automatically under-specified.
Topical overlap is not enough reason to retire or merge external skills.

These changes need either:

- a demonstrated failure mode
- a trigger/routing conflict
- a measurable load problem

### Deferred: moving repeated `obra-*` skills into universal instructions

This is an architectural change, not a low-risk optimization.

It may be correct later, but it should not be bundled into a conservative cleanup pass.

### Rejected: “sync agent self-reference bug” as a proven defect

The identifier `internal-sync-global-copilot-configs-into-repo` exists both as:

- an agent
- a skill at `.github/skills/internal-sync-global-copilot-configs-into-repo/SKILL.md`

So the declared skill is not currently a broken reference.

The real need is to keep validating that declared skills resolve on disk and to keep routing boundaries clear.

---

## Conservative implementation baseline

1. Keep this file as a hypothesis log, not a plan of record.
2. Strengthen contracts and tests around declared-skill resolution.
3. Add non-blocking reporting for instruction-load hotspots.
4. Clarify routing in `AGENTS.md` without redesigning the agent catalog.
5. Do not restructure compact internal instructions unless new evidence justifies it.
6. Do not edit imported non-`internal-*` resources during local optimization work.

---

## Concrete action list

### Already implemented

- Added validator support for non-blocking instruction-load hotspot warnings.
- Added contract coverage for agent declared skills resolving on disk.
- Clarified routing boundaries in `AGENTS.md`.
- Recorded the imported-resource rule in repository knowledge.

### Next internal-only actions

1. Review `internal-*` instruction `applyTo` patterns where they stack on top of broad imported instructions and reduce local overlap only when the internal wrapper is too broad.
2. Review internal routing assets and prompts so imported skills are loaded only when they add clear value for the task.
3. Keep imported non-`internal-*` resources unchanged; if one becomes unusable, handle it through explicit refresh or local wrappering, not inline edits.

---

## Concrete optimization backlog

These items are concrete enough to execute in conservative internal-only passes. They are intentionally narrower than earlier broad restructuring ideas.

### Phase 1. Internal instruction clarity and cross-references

#### 1.1 Python instruction boundary clarification

Observed state:

- `internal-python.instructions.md` is already compact and already separates shared rules from application and script guidance
- the real gap is weak explicit routing to the more specific internal Python skills

Action:

- keep the current structure
- add explicit cross-references from `internal-python.instructions.md` to:
  - `internal-project-python`
  - `internal-script-python`

Reason:

- this improves routing clarity without restructuring a compact file that is not currently a measured hotspot

#### 1.2 Shell deduplication only where overlap is real

Observed state:

- `internal-github-actions.instructions.md` is mostly workflow-specific and is not a meaningful duplicate of `internal-bash.instructions.md`
- `internal-github-action-composite.instructions.md` contains a small amount of shell safety guidance that is context-specific and still useful in-place

Action:

- do not run a broad deduplication pass across workflow instructions
- add or tighten a brief cross-reference to `internal-bash.instructions.md` only where composite-action shell guidance risks drifting from the Bash baseline

Reason:

- the overlap is limited and context-specific; removing too much local shell guidance would weaken usability in YAML-centric files

#### 1.3 Lambda runtime cross-references

Observed state:

- `internal-lambda.instructions.md` is compact and generic
- it lacks explicit bridges to runtime-specific instruction files

Action:

- add explicit runtime-aware cross-references from `internal-lambda.instructions.md` to:
  - `internal-python.instructions.md` for Python Lambdas
  - `internal-nodejs.instructions.md` for JavaScript and TypeScript Lambdas

Reason:

- this sharpens routing without changing the current compact Lambda baseline

### Phase 2. Internal skill quality improvements

#### 2.1 Expand internal skills only where examples improve execution

Candidates:

- `internal-aws-control-plane-governance`
- `internal-copilot-audit`

Action:

- add concrete examples, decision examples, and flagging examples where they improve execution quality

Do not do:

- do not expand files merely to hit a target line count
- do not inline long template material into `internal-cloud-policy` when the detail belongs in `references/policy-templates.md`

Reason:

- examples improve operator usability; line-count-driven expansion does not

#### 2.2 Cross-reference completion inside internal skills

Action:

- add a cross-reference from `internal-terraform` to `terraform-terraform-test` for `.tftest.hcl` and related Terraform test workflows
- add a cross-reference from `internal-docker` to `internal-docker.instructions.md`
- keep validating `internal-code-review` reference files on disk as part of normal validation coverage

Reason:

- these are low-risk improvements that strengthen discovery without changing ownership boundaries

#### 2.3 Do not launch a compression pass based on stale counts

Observed state:

- earlier line-count assumptions for several internal skills were stale
- the current files do not justify a dedicated compression campaign

Action:

- reject line-count-only compression as a near-term optimization driver
- revisit only if instruction-load or usage analytics show an actual problem

### Phase 3. Imported skill handling

#### 3.1 Do not retire or merge imported non-`internal-*` skills locally

Observed state:

- several redundancy suggestions target imported upstream skills such as `antigravity-*`
- repository policy treats those assets as upstream imports to preserve verbatim unless explicitly refreshed, replaced, or forked

Action:

- do not retire, rewrite, merge, or demote imported skills inside this repository as part of local optimization work
- instead, reduce unnecessary routing to them through internal wrappers and measure actual usage first

Reason:

- this preserves the import-as-upstream contract while still enabling evidence-based pruning decisions later

### Phase 4. Agent-catalog simplification hypotheses

#### 4.1 Keep the cloud-agent consolidation idea as a hypothesis

Hypothesis:

- fewer cloud agents with provider-specific skill injection may eventually simplify routing

Action:

- do not redesign the cloud agent catalog yet
- revisit only after usage analytics show whether the current strategic vs tactical split is actually under-used or confusing

Reason:

- this is an architecture decision, not a conservative cleanup item

### Phase 5. Usage metrics and analytics

#### 5.1 Add repository-owned usage reporting

Need:

- optimization should be driven by observed resource usage, not intuition
- the current repo validates catalog contracts and instruction-load hotspots, but it does not track actual resource use frequency

Action:

- add a repository-owned reporting workflow for resource usage analytics
- start with a new internal reporting script rather than overloading the validator

Suggested outputs:

- agent invocation counts
- skill load counts
- prompt and instruction reference counts where observable
- co-usage mappings such as agent -> declared skills actually used
- zero-use or near-zero-use assets over a chosen time window
- top resources by 30-day and 90-day windows

Suggested implementation shape:

- keep `validate-copilot-customizations.sh` focused on structural validation
- add a separate reporting entrypoint such as `report-copilot-usage.py`
- support machine-readable JSON output plus a Markdown summary
- treat telemetry ingestion format as explicit input data, not an implied runtime capability

Success criteria:

- we can identify which agents, skills, prompts, and instructions are actually used
- we can distinguish declared catalog breadth from observed utility
- future pruning or consolidation proposals can cite measured evidence

#### 5.2 Deferred implementation task for the next pass

Action:

- implement an initial repository-owned usage analytics entrypoint in a later pass, likely as `.github/scripts/report-copilot-usage.py`
- define the input event schema explicitly before coding
- emit both JSON and Markdown summaries
- keep this work separate from the validator so structural validation and usage reporting stay decoupled

Status:

- deferred by choice for a follow-up implementation pass

---

## Explicit rejects and deferrals from the current review

### Reject for now

- restructuring `internal-python.instructions.md` into a larger multi-section rewrite
- broad shell-rule deduplication across workflow instructions
- line-count-based compression targets for internal skills
- local retirement or merge of imported `antigravity-*` skills
- adding imported `antigravity-*` architecture references to `internal-pair-architect` without a measured trigger need

### Defer until usage evidence exists

- cloud-agent consolidation
- broader catalog pruning of imported skills
- any optimization justified only by intuition rather than validator output or usage analytics

---

## Skill catalog action matrix

### Delete now

- None.

### Keep unchanged because they are imported

- All non-`internal-*` skills:
  - `antigravity-*`
  - `awesome-copilot-*`
  - `obra-*`
  - `openai-*`
  - `terraform-*`

Reason:

- these are imported upstream assets
- this repository uses `internal-*` resources to wrap, extend, and route around them
- pruning, rewriting, or normalizing them locally would break the import-as-upstream model

### Keep as active internal wrappers or core local capabilities

- `internal-code-review`
- `internal-pair-architect`
- `internal-devops-core-principles`
- `internal-cicd-workflow`
- `internal-terraform`
- `internal-docker`
- `internal-cloud-policy`
- `internal-kubernetes-deployment`
- `internal-aws-control-plane-governance`
- `internal-aws-mcp-research`
- `internal-project-java`
- `internal-project-nodejs`
- `internal-project-python`
- `internal-script-bash`
- `internal-script-python`
- `internal-pr-editor`
- `internal-changelog-automation`

Reason:

- these provide repository-owned behavior, local constraints, or wrapper value that imported skills do not provide directly

### Keep, but review for trigger clarity and overlap within the internal catalog

- `internal-agent-development`
- `internal-skill-management`
- `internal-copilot-audit`
- `internal-copilot-docs-research`
- `internal-agents-md-bridge`
- `internal-sync-global-copilot-configs-into-repo`
- `internal-data-registry`
- `internal-composite-action`
- `internal-performance-optimization`

Concrete review questions:

- does this skill have a unique trigger that is not already owned by another `internal-*` skill?
- does it add repository-specific value beyond the imported upstream skill it may sit next to?
- does it act as a real wrapper or extension, or is it only restating generic upstream guidance?

### Defer any merge or retirement decision until all of these are true

- the candidate skills are both `internal-*`
- their triggers materially overlap
- their output contract is duplicative
- no agent, prompt, or governance file relies on the distinction
- the replacement keeps the wrapper/extension role intact

---

## Follow-up items for measured optimization

- Review validator warnings for workflow, Docker, and Terraform sample paths.
- If a hotspot remains consistently large, choose only one of these responses:
  - narrow the external instruction `applyTo`
  - split deep reference material into a skill and keep the instruction short
- Avoid hard token caps until the reporting is stable enough to justify policy.
