## Plan: Copilot Catalog Deep Audit & Optimization

The repository has **118 skills** (26 internal, 35 antigravity, 21 awesome-copilot, 30 obra, 3 openai, 3 terraform) and **20 agents** (15 internal + 5 imported). This overcrowding is very likely degrading skill activation accuracy. The plan delivers exhaustive quality matrices, a wrapper-strategy verdict, trigger-overlap diagnostics, agent improvements, and lateral-thinking recommendations — all stress-tested through critical thinking and devil's advocate lenses.

---

### Phase 1: Skills Quality Matrices (Research + Classification)

**Step 1.1 — Domain Taxonomy.** Classify all 118 skills into 11 functional domains:

| Domain | Internal | Antigravity | Awesome-Copilot | Obra | Other | Total |
|---|---|---|---|---|---|---|
| **Language/Runtime** (Python, Java, Node, Go, Bash, JS) | 6 | 11 | 0 | 0 | 0 | **17** |
| **Infrastructure** (Terraform, Docker, K8s, CF, Cloud Arch) | 4 | 5 | 0 | 0 | 3 | **12** |
| **Cloud Platform** (AWS, Azure, GCP) | 3 | 3 | 5 | 0 | 0 | **11** |
| **CI/CD & DevOps** | 3 | 0 | 2 | 0 | 0 | **5** |
| **Quality & Review** | 3 | 3 | 5 | 3 | 0 | **14** |
| **Security** | 0 | 2 | 3 | 0 | 0 | **5** |
| **Architecture & Design** | 2 | 5 | 2 | 0 | 0 | **9** |
| **Copilot Governance** | 5 | 0 | 1 | 0 | 1 | **7** |
| **Workflow/Meta (obra)** | 0 | 0 | 0 | 27 | 0 | **27** |
| **Persona/Niche** | 0 | 4 | 0 | 0 | 0 | **4** |
| **PR/Release/Docs** | 2 | 1 | 5 | 0 | 2 | **10** |

**Step 1.2 — Internal vs External Quality Matrix.** For each domain where both exist, compare on 5 axes (Coverage, Actionability, Workflow Structure, Trigger Precision, Repo Integration) scoring 1-5:

| Domain Pair | Internal Skill | External Competitor | Int. Score | Ext. Score | Verdict |
|---|---|---|---|---|---|
| **Bash** | `internal-script-bash` | `antigravity-bash-pro` | ★★★★ (repo conv, emoji logs, validation) | ★★★★★ (deeper: trap, Bats, POSIX) | **Complementary** — internal adds repo policy, external adds depth |
| **Python script** | `internal-script-python` | `antigravity-python-pro` | ★★★★ (folder structure, pins, launcher) | ★★★★★ (3.12+, async, uv, ruff) | **Complementary** — same as above |
| **Python project** | `internal-project-python` | `antigravity-python-patterns` | ★★★★ (DDD, pytest, separation) | ★★★★ (framework selection, architecture) | **Complementary** — different focus |
| **Java** | `internal-project-java` | `antigravity-java-pro` | ★★★★ (BDD tests, purpose JavaDoc) | ★★★★★ (Java 21+, virtual threads, GraalVM) | **Complementary** — internal = repo rules, external = language depth |
| **Node.js** | `internal-project-nodejs` | `antigravity-nodejs-best-practices` | ★★★★ (node:test, early return) | ★★★★ (framework selection, architecture) | **Complementary** |
| **Terraform** | `internal-terraform` | `antigravity-terraform-specialist` + terraform-* | ★★★★ (repo conventions, validation) | ★★★★★ (state mgmt, advanced patterns, testing) | **Complementary** |
| **Docker** | `internal-docker` | none specific | ★★★★★ | N/A | **Standalone** — no external competitor |
| **K8s** | `internal-kubernetes-deployment` | `antigravity-kubernetes-architect` + `antigravity-kubernetes-deployment` | ★★★★ (production manifests, probes) | ★★★★★ (GitOps, service mesh, Helm) | **Complementary** |
| **Code Review** | `internal-code-review` | `antigravity-code-review-checklist` | ★★★★★ (anti-pattern catalog, severity, workflow) | ★★★★ (generic checklist) | **Internal wins** — external is subset |
| **Performance** | `internal-performance-optimization` | none specific | ★★★★★ | N/A | **Standalone** |
| **CI/CD** | `internal-cicd-workflow` | `awesome-copilot-devops-expert` (agent) | ★★★★★ (SHA pinning, OIDC, lean) | ★★★★ (infinity loop, broad scope) | **Internal wins** |

**Step 1.3 — High-Risk Overlap Pairs.** Skills with >60% description overlap that cause activation collisions:

| Collision Group | Competing Skills | Risk |
|---|---|---|
| "Python" | `internal-script-python`, `internal-project-python`, `antigravity-python-pro`, `antigravity-python-patterns`, `antigravity-python-testing-patterns`, `awesome-copilot-pytest-coverage` | **6 skills** compete on "Python" queries |
| "Bash/Shell" | `internal-script-bash`, `antigravity-bash-pro` | 2 skills, moderate |
| "Terraform" | `internal-terraform`, `antigravity-terraform-specialist`, `terraform-terraform-style-guide`, `terraform-terraform-test`, `terraform-terraform-search-import` | **5 skills** compete |
| "Architecture" | `antigravity-software-architecture`, `antigravity-backend-architect`, `antigravity-cloud-architect`, `awesome-copilot-architecture-blueprint-generator`, `awesome-copilot-cloud-design-patterns` | **5 skills** compete |
| "Code review" | `internal-code-review`, `antigravity-code-review-checklist`, `antigravity-clean-code`, `antigravity-simplify-code`, `antigravity-kaizen` | **5 skills** compete |
| "Kubernetes" | `internal-kubernetes-deployment`, `antigravity-kubernetes-architect`, `antigravity-kubernetes-deployment` | 3 skills compete |
| "Java" | `internal-project-java`, `antigravity-java-pro`, `awesome-copilot-java-springboot`, `awesome-copilot-java-junit` | **4 skills** compete |
| "Node.js" | `internal-project-nodejs`, `antigravity-javascript-pro`, `antigravity-nodejs-best-practices`, `awesome-copilot-javascript-typescript-jest` | **4 skills** compete |
| "SQL/DB" | `internal-performance-optimization`, `awesome-copilot-sql-optimization`, `awesome-copilot-postgresql-optimization` | 3 skills compete |

---

### Phase 2: Wrapper Strategy Analysis

**Current state:** Internal skills are NOT wrappers — they are independent, parallel skills that encode repo-specific conventions (emoji logs, folder structure, validation commands, naming policy). External skills provide deeper domain knowledge.

**Recommended strategy per domain:**

| Domain | Strategy | Rationale |
|---|---|---|
| **Bash** | **Keep both, route via agents** | Internal adds `set -euo pipefail` + repo structure; external adds Bats + trap + portability. Agent `internal-developer` already references both. |
| **Python** | **Keep both, sharpen triggers** | Internal enforces repo layout + pins; external teaches language mastery. But 6 competing skills is too many — sharpen descriptions. |
| **Java** | **Keep both, sharpen triggers** | Same pattern — internal = repo rules, external = language depth. |
| **Terraform** | **Keep both, sharpen triggers** | Internal = repo conventions; external = advanced patterns + testing. |
| **Code Review** | **Internal dominates — consider retiring external** | `internal-code-review` is more complete than `antigravity-code-review-checklist`. The checklist adds noise. |
| **Architecture** | **Reduce externals to 2 max** | 5 competing architecture skills is excessive. Keep `antigravity-software-architecture` + `awesome-copilot-cloud-design-patterns`, retire the rest or mark as agent-only. |

**Verdict on wrapper strategy:** Wrappers would add complexity without benefit. The **better strategy is trigger sharpening + agent-scoped routing** — let agents declare which skills to use for their domain, and narrow standalone skill descriptions so they don't self-activate on broad queries.

---

### Phase 3: Trigger/Activation Audit (The Core Problem)

**Step 3.1 — The Numbers.**
- **118 skills** visible in skills
- VS Code Copilot matches skills by comparing user intent against `description:` frontmatter
- With 118 candidates, the model's ranking becomes noisy — too many plausible matches
- **30 obra skills** are generic workflow patterns (debugging, planning, TDD) that can match nearly ANY coding query

**Step 3.2 — Activation Collision Simulation.** For common intents:

| User Intent | Skills That Plausibly Match | Collision Severity |
|---|---|---|
| "Write a Python script" | `internal-script-python`, `internal-project-python`, `antigravity-python-pro`, `antigravity-python-patterns`, `obra-test-driven-development`, `obra-writing-plans` | **HIGH (6+)** |
| "Review this code" | `internal-code-review`, `antigravity-code-review-checklist`, `antigravity-clean-code`, `antigravity-simplify-code`, `antigravity-kaizen`, `obra-verification-before-completion`, `obra-requesting-code-review` | **CRITICAL (7+)** |
| "Deploy to Kubernetes" | `internal-kubernetes-deployment`, `antigravity-kubernetes-architect`, `antigravity-kubernetes-deployment`, `internal-docker`, `obra-executing-plans` | **HIGH (5)** |
| "Write Terraform" | `internal-terraform`, `antigravity-terraform-specialist`, `terraform-style-guide`, `terraform-test`, `terraform-search-import` | **HIGH (5)** |
| "Fix CI" | `internal-cicd-workflow`, `internal-composite-action`, `openai-gh-fix-ci`, `obra-systematic-debugging`, `obra-root-cause-tracing` | **HIGH (5)** |
| "Design architecture" | `antigravity-software-architecture`, `antigravity-backend-architect`, `antigravity-cloud-architect`, `antigravity-domain-driven-design`, `awesome-copilot-cloud-design-patterns`, `awesome-copilot-architecture-blueprint-generator`, `internal-pair-architect` | **CRITICAL (7+)** |

**Step 3.3 — obra Skills: The Silent Overcrowder.**
The 30 obra skills are the biggest contributor to activation noise:
- Most have **broad, generic descriptions** — "Write the test first", "Execute plans in batches", "Find bugs systematically"
- They match almost any development query as secondary candidates
- **Only ~5 are truly standalone** (user would explicitly invoke): `obra-brainstorming`, `obra-systematic-debugging`, `obra-test-driven-development`, `obra-writing-plans`, `obra-when-stuck`
- The rest are **agent-internal procedures** that should NOT compete in open skill matching

**Step 3.4 — Recommended Actions (ordered by impact):**
1. **Narrow obra descriptions** to include "Use only when explicitly requested or when invoked by an agent" — this is the single highest-impact change
2. **Add "Do not auto-select" guards** to persona skills (elon-musk, steve-jobs, warren-buffett, youtube-summarizer already have these — extend to network-101, web-scraper)
3. **Sharpen internal skill descriptions** to emphasize repo-specific keywords: "Use when the repository needs..." instead of generic "Use when..."
4. **Consider a skill tier system**: Tier 1 (always-match), Tier 2 (match only via agent), Tier 3 (explicit name only)

---

### Phase 4: Agent Analysis & Improvements

**Step 4.1 — Agent Skill Load.**

| Agent | Skills Referenced | Assessment |
|---|---|---|
| `internal-developer` | **17** | **Overloaded** — too many choices, dilutes routing |
| `internal-aws-org-governance` | **16** | **Overloaded** — 7 obra skills that add generic meta-thinking |
| `internal-infrastructure` | **13** | Borderline — but domain-coherent |
| `internal-code-review` | **10** | Acceptable |
| `internal-architect` | **11** | Borderline |
| `internal-quality-engineering` | **13** | Acceptable — diverse but domain-scoped |
| `internal-aws-platform-engineering` | **14** | Borderline |
| `internal-azure-platform-engineering` | **13** | Acceptable |
| `internal-azure-platform-strategy` | **11** | Good |
| `internal-gcp-platform-strategy` | **10** | Good |
| `internal-gcp-platform-engineering` | **11** | Acceptable |
| `internal-cicd` | **9** | Good |
| `internal-sync-control-center` | **7** | Good |
| `internal-sync-global-copilot-configs-into-repo` | **5** | Good |
| `internal-ai-resource-creator` | **10** | Acceptable |

**Step 4.2 — Agent Routing Precision Issues:**
- `internal-developer` vs `internal-code-review` vs `internal-quality-engineering`: When someone says "fix this Python bug", all three plausibly match
- `internal-architect` vs cloud-specific strategy agents: "Design a VPC" could route to architect or cloud agent
- `internal-infrastructure` vs cloud-specific engineering agents: Terraform work overlaps

**Step 4.3 — Imported Agent Issues:**
| Agent | Issues Found |
|---|---|
| `awesome-copilot-critical-thinking` | Has **deprecated `tools:` frontmatter**, should be removed per repo policy |
| `awesome-copilot-devils-advocate` | Has **deprecated `tools:` frontmatter** |
| `awesome-copilot-azure-principal-architect` | Has **deprecated `tools:` frontmatter** + massive tools list; overlaps with `internal-azure-platform-strategy` |
| `awesome-copilot-devops-expert` | Has **deprecated `tools:` frontmatter**; overlaps with `internal-cicd` + `internal-devops-core-principles` |
| `awesome-copilot-plan` | Has **deprecated `tools:` frontmatter**; generic planning that overlaps with VS Code's built-in plan mode |

**Step 4.4 — Agent Improvements:**
1. **Trim obra skills from agents** — most agents carry 5-7 obra skills as "optional workflow aids". These add noise without clear routing value. Keep only `obra-verification-before-completion` and `obra-systematic-debugging` for most agents.
2. **Clean imported agent frontmatter** — remove deprecated `tools:` from all 5 imported agents
3. **Consider retiring `awesome-copilot-plan`** — VS Code now has native plan mode, making this redundant
4. **Consider retiring `awesome-copilot-devops-expert`** — fully superseded by `internal-cicd` + `internal-devops-core-principles`
5. **Clarify `internal-developer` scope** — split by language or reduce skill list to core routing skills only

---

### Phase 5: Lateral Thinking — What You Haven't Seen

1. **Missing: Skill activation metrics.** You have no way to measure which skills actually get loaded, how often, or whether they produce useful outputs. Consider adding a `## Activation Log` section to AGENTS.md or a lightweight analytics prompt.

2. **Missing: Negative trigger guards on ALL external skills.** Only 4 persona skills have "Do not auto-select" guards. All 35 antigravity skills and 21 awesome-copilot skills should have explicit `## Do Not Use This Skill When` sections that prevent false activation.

3. **The "description tax."** Every skill's `description:` competes in a flat namespace. There's no hierarchy, no priority, no weighting. The repo treats all skills equally, but they're not equal — some are core daily-use tools, others are niche monthly-use references. **Consider a two-tier activation model**: a smaller "active" catalog synced to consumer repos and a "reference" catalog available only when explicitly invoked.

4. **Obra skills as instruction files, not skills.** Many obra skills are workflow guidelines, not action-producing skills. They would be more appropriate as `.instructions.md` files with narrow `applyTo` patterns, which are loaded contextually by file type rather than competing in open skill matching.

5. **Missing inter-skill routing.** When `internal-code-review` says "run `internal-pair-architect` after for bigger picture", there's no enforcement mechanism. Consider adding a `## Chain To` frontmatter field that agents can use for deterministic handoffs.

6. **The imported-asset paradox.** The repo policy says "treat non-`internal-*` resources as imported upstream assets kept verbatim." But this means you can't fix their broad descriptions, deprecated frontmatter, or missing negative guards. **Consider forking the most problematic imports** into `internal-*` variants with tighter triggers, and retiring the originals.

7. **Missing: Consolidation candidates.** `antigravity-code-refactoring-refactor-clean` and `antigravity-code-refactoring-tech-debt` are almost certainly better as one skill. `antigravity-kubernetes-architect` and `antigravity-kubernetes-deployment` overlap heavily. `awesome-copilot-sql-optimization` and `awesome-copilot-postgresql-optimization` should be one skill with a PostgreSQL section.

---

### Phase 6: Critical Thinking & Devil's Advocate Self-Challenge

**Applying `awesome-copilot-critical-thinking` — challenging my own assumptions:**

**Q: "Why do I assume 118 skills is too many?"**
A: Because VS Code Copilot uses description-based matching in a flat namespace. But I don't have empirical data on the model's skill-selection accuracy at this count. It's possible the model handles 118 fine if descriptions are sufficiently distinct. The real problem might be **description quality**, not count.

**Q: "Why do I assume obras are the main problem?"**
A: Because they have the broadest descriptions and match the widest range of intents. But they're imported — the repo policy says don't modify them. The real lever might be **sharpening internal descriptions** rather than touching obra.

**Q: "Is the wrapper strategy truly inferior?"**
A: I dismissed it as adding complexity. But a well-designed wrapper that imports external knowledge and adds repo constraints could actually *reduce* total skill count — one wrapper replacing two skills (internal + external) in the activation space. This deserves deeper analysis.

**Applying `awesome-copilot-devils-advocate` — stress-testing the plan:**

**Objection 1: "You're proposing to modify obra skills, but repo policy explicitly forbids modifying imported upstream assets."**
Defense: I'm proposing description-level narrowing only for internal skills. For obra and external skills, the action is to adjust agent skill lists and routing, not modify the files themselves. However, if the files can't be touched, the overcrowding problem persists unless consumer repos use a filtered subset via repo-profiles.yml.

**Objection 2: "Reducing agent skill lists might remove useful capabilities."**
Defense: Skills listed in agents are advisory guidance, not hard dependencies. Removing a skill from an agent's list doesn't remove it from the repo — the agent can still be instructed to use it. The goal is to reduce noise in the default routing, not eliminate access.

**Objection 3: "The two-tier activation model you suggest doesn't exist in VS Code Copilot — you're proposing a feature that doesn't exist."**
Defense: True. The actual implementation would be: move niche skills to a `skills-reference/` folder outside skills, so VS Code doesn't auto-discover them. Users would reference them explicitly by path. This is a practical approximation of tiering.

**Objection 4: "Forking imported assets into internal-* variants contradicts the upstream asset policy."**
Defense: The policy allows "local fork" when the user explicitly asks for it. The plan would need explicit user approval for each fork. Alternatively, use `internal-*` wrapper skills that reference the external ones rather than replacing them.

**Revised recommendations after self-challenge:**
1. **Primary lever: sharpen internal skill descriptions** (no policy conflict)
2. **Secondary lever: trim agent skill lists** (no policy conflict)
3. **Tertiary lever: propose obra subset via repo-profiles.yml** (respects import policy)
4. **Escalation lever: fork specific externals into internal-* wrappers** (requires explicit user approval, one by one)

---

### Verification
1. Cross-check every skill path against disk to confirm existence
2. Validate no internal skill references a missing companion
3. Confirm description uniqueness: no two skills should have >80% description overlap
4. Verify agent skill lists match actual installed skills
5. Run `scripts/validate-copilot-customizations.sh` for structural integrity
6. After changes, re-run activation collision simulation to measure improvement

### Decisions
- All analysis based on actual file contents, not assumptions
- External skills treated as read-only imports (per AGENTS.md policy)
- Changes proposed only for `internal-*` skills and governance files
- obra skills evaluated as a group — propose subset, not individual modifications
- Each external fork requires explicit user approval

### Further Considerations
1. **Obra subset size**: How many of the 30 obra skills should be in the "active" set synced to consumer repos? I recommend **5-8 max** (brainstorming, debugging, TDD, verification, writing-plans, executing-plans, when-stuck, dispatching-parallel-agents). The remaining 22 would stay available but not compete in open matching.
2. **Consumer repo filtering**: Should repo-profiles.yml profiles explicitly list which skills to sync vs. exclude? Currently profiles are advisory — making them enforceable would be the strongest overcrowding fix.
3. **Imported agent cleanup**: The 5 imported agents all have deprecated `tools:` frontmatter. Should we clean them (violates import policy) or fork them (adds to count)? I recommend cleaning frontmatter-only changes as "normalization" rather than "modification", since `tools:` is a deprecated field that does nothing.
