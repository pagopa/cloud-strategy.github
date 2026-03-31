# zOptimizer Final Analysis

> Decision-oriented rewrite of `zOptimizer.md`, preserving its full analytical surface while reorganizing it around the outcome you actually want: a smaller catalog with `obra-*` as the strategic thinking layer, `internal-*` as the tactical/canonical execution layer, and external-prefixed skills kept only when they add narrow support value.

## 2. Main Catalog Decision Plan

### 2.1 Merge Into `internal-*`, Then Delete The External Source

These are the best candidates for “take the good parts, make the internal skill stronger, then remove the competing external skill.”

| External Skill | Target Internal Owner | What To Absorb | Why This Is Better |
|---|---|---|---|
| `awesome-copilot-agent-governance` | `internal-agent-development` and `internal-sync-control-center` | Agent-policy, trust-boundary, audit-trail, tool-approval concepts | Highly relevant to this repo, but it belongs in the internal governance layer. |
| `awesome-copilot-create-github-pull-request-from-specification` | `internal-pr-editor` | The narrow “spec-to-PR-body mapping” idea if you still value it | PR authoring should have one internal owner. |
| `awesome-copilot-instructions-blueprint-generator` | `internal-ai-resource-creator` and `internal-agents-md-bridge` | Better blueprint extraction prompts for repo-local instructions generation | This repo already has internal owners for Copilot asset authoring. |
| `awesome-copilot-postgresql-optimization` | `internal-performance-optimization` | `EXPLAIN ANALYZE`, JSONB/GIN, partial indexes, extension discipline, Postgres-specific guardrails | DB performance should have one internal owner, not a generic and DB-specific split. |
| `awesome-copilot-sql-optimization` | `internal-performance-optimization` | Query-shape, indexing, batching, pagination, and plan-based tuning workflow | Same owner as broader performance work. |
| `terraform-terraform-style-guide` | `internal-terraform` | Formatting and structure conventions only where they match repo conventions | Reduces Terraform collision space without losing useful style guidance. |

### 2.2 Keep As Support-Only Specialists

These skills still add value, but they should stop acting like equal peers to `obra-*` and `internal-*`. Keep them narrow, explicit, and preferably out of broad default routing.

| Skill | Decision | Why Keep It |
|---|---|---|
| `antigravity-api-design-principles` | Support-only | Narrow API contract and interface guidance that complements architecture decisions. |
| `antigravity-aws-cost-optimizer` | Support-only | Specific AWS cost-optimization support, not a generic coding trigger. |
| `antigravity-aws-serverless` | Support-only | Narrow AWS serverless expertise if explicitly needed. |
| `antigravity-cloudformation-best-practices` | Support-only | Specific IaC support outside Terraform. |
| `antigravity-domain-driven-design` | Support-only | Useful architecture support, but not a default owner. |
| `antigravity-golang-pro` | Support-only | There is no internal Go owner today; keep only as explicit support. |
| `antigravity-grafana-dashboards` | Support-only | Narrow observability/dashboarding help. |
| `antigravity-kubernetes-architect` | Support-only | Strategic K8s/GitOps/service-mesh depth that is different from tactical deployment guidance. |
| `antigravity-network-engineer` | Support-only | Narrow network expertise, not a broad repo-governance trigger. |
| `awesome-copilot-agentic-eval` | Support-only | Relevant to evaluation workflows, but still narrower than internal governance ownership. |
| `awesome-copilot-azure-devops-cli` | Support-only | Specific Azure DevOps CLI support. |
| `awesome-copilot-azure-pricing` | Support-only | Specific pricing lookup and cost-estimation support. |
| `awesome-copilot-azure-resource-health-diagnose` | Support-only | Narrow Azure operational diagnosis support. |
| `awesome-copilot-azure-role-selector` | Support-only | Precise least-privilege Azure RBAC support. |
| `awesome-copilot-cloud-design-patterns` | Support-only | Pattern library that can support, but should not lead, architecture decisions. |
| `awesome-copilot-codeql` | Support-only | Narrow and useful security workflow support. |
| `awesome-copilot-dependabot` | Support-only | Narrow dependency-governance workflow support. |
| `awesome-copilot-secret-scanning` | Support-only | Narrow GitHub security support. |
| `openai-gh-address-comments` | Support-only | Good specialized PR-comments workflow through GitHub. |
| `openai-gh-fix-ci` | Support-only | Good specialized CI-failure workflow through GitHub. |
| `openai-skill-creator` | Support-only | Still useful while `internal-skill-management` and `internal-ai-resource-creator` rely on it. |
| `terraform-terraform-search-import` | Support-only | Narrow Terraform import workflow, low collision when kept explicit. |
| `terraform-terraform-test` | Support-only | Narrow Terraform `.tftest.hcl` knowledge that does not need to be a first-line trigger. |



### 2.3 Practical Prune Order

After the completed `Delete Now` batch, the next cleanup order should be:

1. Merge agent-governance, SQL, PostgreSQL, and PR-authoring externals into the internal tactical owners.
2. Merge the remaining Terraform style-guide external into the internal Terraform owner.
3. Demote the remaining externals to support-only and remove them from broad default routing.

## 3. Full Carry-Over Of `zOptimizer.md`, Reorganized But Not Lost

This section preserves the pre-prune `117`-skill baseline so the original reasoning is not lost.

### 3.1 Opening Thesis From `zOptimizer.md`

The original file opens with the claim that the catalog is overcrowded and likely degrading skill activation accuracy. I keep that thesis, but with two corrections:

- before the current prune pass, the catalog was even more crowded than stated because the real skill count was `117`, not `118`
- the more important issue is not just count, but flat-namespace competition between:
  - broad external skills
  - broad obra meta skills
  - internal agents that still tell the system not to prefer `internal-*` by default

That combination makes the catalog feel larger than the raw number suggests.

### 3.2 Phase 1: Skills Quality Matrices

#### Step 1.1: Domain Taxonomy

The domain taxonomy in `zOptimizer.md` is directionally useful. The catalog really does concentrate collision risk in these areas:

- Language/runtime
- Quality/review
- Architecture/design
- Infrastructure/Terraform/Kubernetes
- Workflow/meta

The taxonomy is still worth keeping because it explains why some removals matter more than others.

My revisions are:

- the total skill count must be corrected to `117`
- the `awesome-copilot-*` family count must be corrected to `24`
- the architecture and quality/review domains should be treated as the most dangerous for activation collisions because they contain multiple broad, generic descriptions
- the workflow/meta domain should be split mentally into:
  - trusted strategic obra skills
  - generic externals that should not compete with them

#### Step 1.2: Internal vs External Quality Matrix

The original matrix says “complementary” in several places. That is an accurate description of the current state, but not the best target state for your preferred operating model.

##### Terraform

Original conclusion: complementary.

My conclusion:

- `internal-terraform` should become the single tactical owner
- absorb from:
  - `terraform-terraform-style-guide`
- keep as support-only:
  - `terraform-terraform-test`
  - `terraform-terraform-search-import`

Reason:

- `terraform-terraform-test` and `terraform-terraform-search-import` are narrow enough to survive as explicit support
- `terraform-terraform-style-guide` is still broad enough to compete directly with `internal-terraform`

##### Docker

Original conclusion: standalone internal winner.

My conclusion:

- keep as-is
- no external Docker peer exists that is strong enough to change the current structure

##### Code review

Original conclusion: internal wins.

My conclusion:

- fully agree
- `internal-code-review` should stay the canonical owner

##### Performance

Original conclusion: internal standalone winner.

My conclusion:

- agree
- `internal-performance-optimization` should also absorb:
  - `awesome-copilot-sql-optimization`
  - `awesome-copilot-postgresql-optimization`

Reason:

- this gives you one tactical performance owner instead of a generic performance skill plus separate SQL/Postgres peers

##### CI/CD

Original conclusion: internal wins.

My conclusion:

- agree
- the supporting evidence is actually stronger than the original plan states because the imported `awesome-copilot-devops-expert` agent still has deprecated frontmatter and a generic infinity-loop scope
- `internal-cicd` plus `internal-cicd-workflow` plus `internal-devops-core-principles` are the cleaner internal ownership model

#### Step 1.3: High-Risk Overlap Pairs

The original collision groups are correct. My action decisions for each are:

##### Terraform cluster

Original collision set:

- `internal-terraform`
- `terraform-terraform-style-guide`
- `terraform-terraform-test`
- `terraform-terraform-search-import`

My decision:

- active owner:
  - `internal-terraform`
- support-only explicit specialists:
  - `terraform-terraform-test`
  - `terraform-terraform-search-import`
- merge/delete the rest

##### Architecture cluster

Original collision set:

- `antigravity-software-architecture`
- `antigravity-backend-architect`
- `antigravity-cloud-architect`
- `awesome-copilot-architecture-blueprint-generator`
- `awesome-copilot-cloud-design-patterns`

My decision:

- active owner:
  - `internal-architect`
- support-only support set:
  - `antigravity-api-design-principles`
  - `antigravity-domain-driven-design`
  - `awesome-copilot-cloud-design-patterns`
- the broad generic externals in the original cluster should be removed

##### SQL/DB cluster

Original collision set:

- `internal-performance-optimization`
- `awesome-copilot-sql-optimization`
- `awesome-copilot-postgresql-optimization`

My decision:

- collapse to `internal-performance-optimization`

### 3.3 Phase 2: Wrapper Strategy Analysis

The original file says internal skills are not wrappers and that wrapper strategy adds complexity without enough benefit.

My revised view:

- I agree that the current internal skills are not wrappers.
- I agree that pure wrapper proliferation would be a mistake.
- I do not agree that the best answer is mainly “trigger sharpening + coexistence.”

Under your stated priorities, the better strategy is:

1. selective internal absorption for broad, repeated external peers
2. support-only retention for narrow specialists
3. trigger sharpening only after the catalog is materially smaller

In other words:

- when an external skill is broad and repeatedly relevant, it should usually become material for an `internal-*` owner
- when an external skill is narrow and specialist, it can remain support-only
- when an external skill is generic but not strategically important, it should be deleted

That is not a “wrapper everything” strategy.
It is a “make internal the canonical owner wherever the repo repeatedly depends on a capability” strategy.

### 3.4 Phase 3: Trigger / Activation Audit

#### Step 3.1: The Numbers

The original file says:

- `118` visible skills
- flat description matching creates noise
- `30` obra skills can match almost anything

My corrected version is:

- `117` visible skills before the current prune pass
- the flat description problem is real
- the obra count is still `30`
- but the most important change is that your external generic peers should stop competing with obra and internal assets as equals

The collision is not caused by obra alone.
It is caused by the combination of:

- broad obra meta workflows
- broad external domain skills
- internal agents that still say not to prefer `internal-*` by default

#### Step 3.2: Activation Collision Simulation

The original example intents are useful and still hold:

##### “Write a Python script”

Still a layered routing space:

- `internal-script-python`
- `internal-project-python`
- `obra-test-driven-development`
- `obra-writing-plans`

My fix:

- collapse Python externals into the internal owners
- keep obra as the method layer, not a Python domain owner

##### “Write Terraform”

Still too many plausible matches:

- `internal-terraform`
- `terraform-terraform-style-guide`
- `terraform-terraform-test`
- `terraform-terraform-search-import`

My fix:

- keep `internal-terraform` as the active owner
- demote the narrow Terraform support skills
- merge/delete the broad peers

##### “Fix CI”

Still a high-collision space:

- `internal-cicd-workflow`
- `internal-composite-action`
- `openai-gh-fix-ci`
- `obra-systematic-debugging`
- `obra-root-cause-tracing`

My fix:

- keep the internal CI/CD owners
- keep `openai-gh-fix-ci` as specialized support-only
- keep obra only as methodology

##### “Design architecture”

Still the worst or second-worst collision zone:

- `antigravity-software-architecture`
- `antigravity-backend-architect`
- `antigravity-cloud-architect`
- `antigravity-domain-driven-design`
- `awesome-copilot-cloud-design-patterns`
- `awesome-copilot-architecture-blueprint-generator`
- `internal-pair-architect`

My fix:

- make `internal-architect` the clear owner
- keep only narrow support skills around it

#### Step 3.3: obra Skills As The Silent Overcrowder

The original file calls obra the biggest contributor to activation noise.

I partially agree and partially revise that claim.

I agree that:

- many obra descriptions are broad
- several obra skills are really method/process guidance, not domain owners
- they can appear as secondary matches on many requests

I revise the conclusion like this:

- obra is not the main thing to cut
- obra is the thing to protect and position correctly

Because your trust model is:

- obra = high-level/strategic analyst
- internal = tactical owner

the practical action should be:

- do not make obra the first target of reduction
- instead, remove the broad external peers that make obra compete in an already overcrowded space
- then profile or route obra more carefully if needed

#### Step 3.4: Recommended Actions

The original file recommends:

1. narrow obra descriptions
2. add do-not-auto-select guards
3. sharpen internal descriptions
4. consider a tier system

My revised order is:

1. delete the highest-noise external generic skills
2. merge the best external tactics into `internal-*`
3. trim internal agent skill lists so they stop treating external and internal skills as equal peers
4. create an active vs reference tier for support-only skills
5. sharpen descriptions only after the catalog is smaller

That order better matches:

- your stated priorities
- import policy constraints
- the fact that `obra-*` and `internal-*` are excluded from the current deletion target

### 3.5 Phase 4: Agent Analysis & Improvements

#### Step 4.1: Agent Skill Load

The original file gives useful directional judgments, but some numbers were stale or incomplete.

Verified counts from disk:

| Agent | Verified Skill References | My Assessment |
|---|---|---|
| `internal-developer` | `9` | Much leaner after the Java, Node.js, and Python retirements |
| `internal-architect` | `8` | Much tighter than the earlier snapshot, though architecture overlap still exists outside the agent |
| `internal-aws-org-governance` | `15` | Overloaded |
| `internal-infrastructure` | `12` | Borderline |
| `internal-code-review` | `8` | Acceptable and cleaner after the first merge-source retirements |
| `internal-quality-engineering` | `12` | Acceptable and cleaner after the Python testing and coverage merge work |
| `internal-aws-platform-engineering` | `13` | Borderline |
| `internal-azure-platform-engineering` | `12` | Acceptable |
| `internal-azure-platform-strategy` | `11` | Good |
| `internal-gcp-platform-strategy` | `9` | Good |
| `internal-gcp-platform-engineering` | `10` | Acceptable |
| `internal-cicd` | `7` | Good |
| `internal-sync-control-center` | `7` | Focused in its declared skill stack, even though its governance scope remains broad |
| `internal-sync-global-copilot-configs-into-repo` | `5` | Good |
| `internal-ai-resource-creator` | `10` | Acceptable |

The two most important takeaways are:

- `internal-developer` is now meaningfully leaner, though it still spans multiple stacks and should keep shrinking as remaining peers disappear
- the cloud governance and engineering agents remain the biggest dense stacks after the first retirements

#### Step 4.2: Agent Routing Precision Issues

The original routing concerns are correct:

- `internal-developer` vs `internal-code-review` vs `internal-quality-engineering`
- `internal-architect` vs cloud strategy agents
- `internal-infrastructure` vs provider engineering agents

I add one stronger point:

- several internal agents explicitly say not to prioritize `internal-*` over imported skills by default

That instruction directly conflicts with your desired policy direction.

If your new hierarchy is:

- obra first for strategy
- internal first for tactics
- external only if needed

then those routing lines should eventually be changed after catalog cleanup.

#### Step 4.3: Imported Agent Issues

The original file flags deprecated `tools:` frontmatter in the imported agents.

This is confirmed from disk for all `5` imported agents:

- `awesome-copilot-azure-principal-architect.agent.md`
- `awesome-copilot-critical-thinking.agent.md`
- `awesome-copilot-devils-advocate.agent.md`
- `awesome-copilot-devops-expert.agent.md`
- `awesome-copilot-plan.agent.md`

That means the imported agent set is not only overlapping; it also contains normalized-asset debt.

#### Step 4.4: Agent Improvements

The original file proposes:

1. trim obra skills from agents
2. clean imported frontmatter
3. retire `awesome-copilot-plan`
4. retire `awesome-copilot-devops-expert`
5. clarify `internal-developer`

My revised version is:

1. trim broad external peers from `internal-developer`, `internal-architect`, and `internal-infrastructure`
2. stop telling internal agents to treat imported and internal skills as peers by default
3. keep obra where it truly changes the reasoning lens, not as decorative bulk
4. retire or demote `awesome-copilot-plan`
5. retire or demote `awesome-copilot-devops-expert`
6. normalize imported agent frontmatter only if you decide that kind of cleanup is allowed under your import policy, or fork where necessary

### 3.6 Phase 5: Lateral Thinking — What The Original File Saw, And What I Add

The original file has seven strong “you haven’t seen this” points. I keep all seven and tighten them against your preferred operating model.

#### 1. Missing skill activation metrics

I agree completely.

Without metrics, you are still reasoning from structure and trigger language, not observed activation.

That said, you already have enough structural evidence to justify pruning:

- real overlap clusters
- generic descriptions
- overloaded agent lists

Metrics would improve prioritization, not overturn the current diagnosis.

#### 2. Missing negative trigger guards on external skills

I agree with the diagnosis.

I revise the implementation path:

- because imported assets should stay verbatim unless explicitly refreshed or forked
- the safer first lever is not mass-editing imports
- the safer first lever is:
  - deletion
  - support-only demotion
  - agent-list trimming
  - profile filtering

#### 3. The description tax

I fully agree.

This is one of the deepest structural problems in the catalog:

- every skill competes in a flat description namespace
- there is no native weighting
- generic descriptions are tax multipliers

Your desired hierarchy is basically an attempt to impose weighting outside the platform:

- obra = strategic lens
- internal = canonical execution
- external = optional specialists

That is the right conceptual direction.

#### 4. obra skills as instruction files, not skills

I agree conceptually, but I would not make this your first move.

Reason:

- obra is trusted
- obra is excluded from the deletion target
- migrating obra out of skills is a structural redesign, not a fast optimization

So I would stage this as:

1. shrink the competing external catalog
2. re-test routing quality
3. only then decide whether obra should partly move into instructions or profiles

#### 5. Missing inter-skill routing

I agree.

This is especially visible where one internal asset says “use X after Y” but there is no enforcement mechanism.

A stronger internal hierarchy would help because:

- fewer peers means clearer handoffs
- support-only specialists can be named explicitly rather than left floating in open trigger space

#### 6. The imported-asset paradox

I strongly agree.

This is the core strategic tension:

- imported assets are supposed to remain verbatim
- but many imported assets are too broad, stale, or structurally noisy

Your practical options are:

1. delete them
2. demote them to support-only
3. internally absorb their best ideas
4. fork only when a capability is strategically core and cannot be expressed more simply inside an internal owner

This is exactly why “merge into internal and delete the external” is such a strong move here.

#### 7. Missing consolidation candidates

I agree, and I would make the following concrete consolidation set the first one:

- `terraform-terraform-style-guide` -> `internal-terraform`
- `awesome-copilot-sql-optimization` + `awesome-copilot-postgresql-optimization` -> `internal-performance-optimization`

### 3.7 Phase 6: Critical Thinking And Devil’s Advocate Self-Challenge

The original file already self-challenges well. I preserve that and sharpen it.

#### Question: Is `117` skills automatically too many?

My answer:

- not automatically
- but it is too many for this specific flat, overlapping, peer-like structure

If the catalog were strongly tiered and descriptions were narrow, `117` would be less alarming.
The current problem is the combination of count, overlap, and peer-status competition.

#### Question: Are obra skills really the main problem?

My answer:

- not in the way the original wording suggests
- obra is noisy, but obra is also trusted and strategically valuable
- the bigger issue is that broad external peers are competing in the same open space as obra and the internal canon

#### Question: Is wrapper strategy really inferior?

My answer:

- blanket wrapper strategy is inferior
- selective internal absorption is not

That is the key distinction.

When a capability is strategically important to this repository, the right move is often:

- internal owner
- external ideas harvested selectively
- no external peer left standing

#### Objection: “You cannot modify imported assets.”

Answer:

- correct
- which is why this document recommends deletion, demotion, and internal absorption first
- not in-place rewriting of imported resources as the default path

#### Objection: “Reducing agent skill lists removes capability.”

Answer:

- not necessarily
- support-only skills can still be invoked explicitly
- the goal is to reduce default competition, not erase access to every specialist capability

#### Objection: “A tier system is not a native GitHub Copilot feature.”

Answer:

- true
- but you can approximate it operationally through:
  - sync profiles
  - smaller active subsets
  - support-only conventions
  - trimmed agent skill lists

#### Objection: “Forking imports adds even more assets.”

Answer:

- also true
- therefore forking should be the escalation path, not the first-line solution
- internal absorption is usually cleaner when you only need a subset of the external value

### 3.8 Verification, Decisions, And Further Considerations From The Original File

#### Verification

The original file proposes:

1. cross-check every skill path
2. validate references
3. confirm description uniqueness
4. verify agent skill lists
5. run structural validation
6. re-run collision simulation after changes

For this analysis and applied cleanup passes, I actually verified:

- skill families and counts on disk
- agent count on disk
- selected skill descriptions and bodies for the major collision groups
- imported-agent `tools:` frontmatter
- skill-reference counts for internal agents
- structural validation after retiring the first two merge-source externals

Validation run for this pass:

- `python3 .github/scripts/validate-copilot-customizations.sh`

#### Decisions

The original file declares:

- analysis based on actual file contents
- external skills treated as read-only imports
- changes proposed only for internal assets and governance files
- obra skills evaluated as a group
- external forks require approval

I keep those decisions with one refinement:

- external skills should now be split explicitly into:
  - delete
  - merge source
  - support-only

That turns the original plan into an executable inventory strategy.

#### Further Considerations

The original file ends with three key considerations. I keep all three and sharpen them.

##### Obra subset size

The original recommendation of roughly `5-8` active obra skills is reasonable if you are syncing to consumer repos or curating an active subset.

I would not treat this as a deletion plan.
I would treat it as an activation-tier decision.

##### Consumer repo filtering

I agree that profile-driven filtering would be one of the strongest levers available.

In your desired model, this would let you preserve:

- obra strategic value
- internal tactical canon
- only a very small explicit external support set

##### Imported agent cleanup

I agree that the imported agent frontmatter problem is real.

I would treat it as a second-wave governance cleanup after the skill catalog is reduced, because the skill catalog is currently the larger source of routing noise.

## 4. Recommended End-State

### Strategic layer

Keep `obra-*` as the trusted high-level thinking layer.

Do not try to make external generic planning/review/architecture skills share that role.

### Tactical layer

Strengthen `internal-*` until the repository has one clear internal owner for:

- Bash
- Python scripts
- Python projects
- Java projects
- Node.js projects
- Terraform
- Kubernetes deployment
- Code review
- Performance / SQL / PostgreSQL
- Agent governance / Copilot catalog governance
- PR authoring

### Support layer

Keep only a small external specialist set, and treat it as:

- explicit-name only where practical
- support-only in agents
- not equal-priority peers to internal owners

## 5. Coverage Map

This is the explicit map showing that the content of `zOptimizer.md` was not dropped; it was reorganized.

| Original `zOptimizer.md` section | Preserved in this file |
|---|---|
| Opening thesis and overcrowding premise | Section `3.1` |
| Phase 1, Step 1.1 Domain Taxonomy | Section `3.2`, Step `1.1` |
| Phase 1, Step 1.2 Internal vs External Quality Matrix | Section `3.2`, Step `1.2` |
| Phase 1, Step 1.3 High-Risk Overlap Pairs | Section `3.2`, Step `1.3` |
| Phase 2 Wrapper Strategy Analysis | Section `3.3` |
| Phase 3, Step 3.1 The Numbers | Section `3.4`, Step `3.1` |
| Phase 3, Step 3.2 Activation Collision Simulation | Section `3.4`, Step `3.2` |
| Phase 3, Step 3.3 obra Skills | Section `3.4`, Step `3.3` |
| Phase 3, Step 3.4 Recommended Actions | Section `3.4`, Step `3.4` |
| Phase 4, Step 4.1 Agent Skill Load | Section `3.5`, Step `4.1` |
| Phase 4, Step 4.2 Routing Precision Issues | Section `3.5`, Step `4.2` |
| Phase 4, Step 4.3 Imported Agent Issues | Section `3.5`, Step `4.3` |
| Phase 4, Step 4.4 Agent Improvements | Section `3.5`, Step `4.4` |
| Phase 5 Lateral Thinking | Section `3.6` |
| Phase 6 Critical Thinking | Section `3.7` |
| Verification | Section `3.8`, Verification |
| Decisions | Section `3.8`, Decisions |
| Further Considerations | Section `3.8`, Further Considerations |
| Practical “what should I do now?” outcome | Sections `2` and `4` |
