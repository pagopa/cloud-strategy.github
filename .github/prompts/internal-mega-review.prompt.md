---
name: "internal-mega-review"
agent: "internal-gateway-review-generic"
description: "Run a complete advisor-only mega review for one or more repositories and write split English analysis under each repo tmp/"
argument-hint: "Repository paths or names; optional focus and constraints; retained output is English"
---

<!-- markdownlint-disable-file MD041 -->

Repositories to review:
${input:repositories:List one or more repository names or paths. Use one per line when possible.}

Optional focus areas:
${input:focus:Optional focus such as security, governance, architecture, testing, automation, documentation, AI-readiness, or migration risk}

Optional constraints or exclusions:
${input:constraints:Optional non-negotiables, exclusions, prior findings to preserve, or rollout concerns}

Output language:
${input:language:Match chat language unless explicitly overridden. If you want to force one, write Italian or English.}

Retained analysis content, headings, tables, and artifact filenames must stay in English.

Use these standards-repository sources first for governance, evidence, and split-output discipline:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-gateway-review-generic.agent.md](../agents/internal-gateway-review-generic.agent.md)
- [.github/agents/internal-gateway-critical-master.agent.md](../agents/internal-gateway-critical-master.agent.md)
- [.github/skills/internal-gateway-writing-plans/SKILL.md](../skills/internal-gateway-writing-plans/SKILL.md)

For this mega-review prompt, the English retained artifact contract below overrides any legacy non-English filename examples in those sources.

Then run a complete, analysis-only mega review with these rules.

## 1. Mission

Review one or more repositories as a pragmatic technical advisor.

- Do not apply fixes.
- Do not edit production files.
- Do not rename, move, or delete real repository assets.
- Write analysis artifacts only under `tmp/`.
- Keep the output concise, operational, evidence-based, written in English, and ready to guide later implementation work.

## 2. Repository Resolution

For each item in `repositories`:

1. Resolve it to a real repository path in the current workspace or obvious sibling path.
2. If the path is ambiguous or missing, stop and ask only for the unresolved repository.
3. Treat each resolved repository independently before producing any cross-repo synthesis.

## 3. Output Locations

For each target repository, write the retained analysis under:

- `<repo>/tmp/superpowers/mega-review/`

If more than one repository is reviewed, also create a global cross-repo package under:

- `tmp/superpowers/mega-review-global/`

If the target `tmp/superpowers/mega-review/` folder already exists:

- Preserve the previous analysis.
- Do not rewrite it wholesale.
- Add only missing coverage, corrections, or newly discovered findings in a separate numbered file such as `05-review-addendum.md`, or in a numbered addendum inside the relevant domain folder.
- Update `01-executive-summary.md` only when the executive summary is materially outdated.
- Do not create new non-English filenames. If a prior package uses legacy non-English filenames, preserve those files and continue with English-named delta files unless the user explicitly asks for migration.

If no prior review exists, create a fresh split review package.

## 4. Required Method

For each repository:

1. Start with a compact inventory before judging the repository.
2. Derive the technology stack only from repository evidence on disk.
3. Adapt the review to the observed stack and domain.
4. If the repository contains technologies, frameworks, or tooling not explicitly anticipated here, extend the review to cover them from first principles instead of skipping them.
5. Never invent technologies, workflows, or controls that are not present.
6. Prefer repository evidence over assumptions, and explicit uncertainty over false confidence.
7. When a repository-owned bundle owner such as `SKILL.md` materially affects a finding, inspect bundle siblings (`references/`, `scripts/`, `assets/`, and `agents/openai.yaml`) or mark the intentional non-action.

## 5. Inventory First

Before findings, produce a compact repository inventory covering what is actually present, for example:

- Languages
- Frameworks and runtime tooling
- IaC tooling such as Terraform, Terragrunt, CloudFormation, Pulumi, Helm, Kubernetes manifests, Rego, policy files, or equivalent
- CI/CD systems and workflow triggers
- Security controls and scanning surfaces
- Test and validation surfaces
- Documentation and runbooks
- Governance and audit artifacts
- AI-facing files such as `AGENTS.md`, prompt files, instructions, skills, memory, or repository-specific agent guidance
- Repository purpose and likely owner, if inferable from evidence

If an area is not present or not verifiable, say so.

## 6. Review Dimensions

For each repository, review at least these dimensions when relevant to the observed stack:

- Security and least privilege
- Architecture and design clarity
- Code and script quality
- Automation and CI/CD
- Testing and validation
- Documentation and operational readiness
- Governance and auditability
- AI-readiness
- Cleanup, dead assets, drift, and standardization opportunities

Also adapt to domain-specific concerns such as IAM, RBAC, policy-as-code, cloud governance, FinOps, GitHub org governance, platform operations, or repo-governance when those are actually present.

## 7. Evidence Rule

Every finding must cite concrete evidence such as:

- A specific path
- A specific workflow
- A repeated pattern observed in files or directories
- A missing but expected validation surface relative to the detected stack
- An explicit contrast with another reviewed repository when doing cross-repo analysis

If a claim cannot be tied to concrete evidence, move it to open questions or blockers instead of classifying it as a finding.

## 8. Finding Format

For each material finding, use this structure:

### Finding Title

- Severity: Critical | Medium | Low
- Category: Security | Architecture | Automation | Testing | Documentation | Governance | AI-readiness | Cleanup
- Classification: Must | Should | Could | Won't for now
- Evidence: specific file, directory, workflow, or repeated pattern
- Problem: what is wrong
- Impact: why it matters
- Proposed action: what to do later
- Estimated effort: S | M | L
- Invasiveness: low | medium | high
- Less invasive alternative: if applicable

## 9. Required Output Shape Per Repository

Use split numbered files, not one monolithic document. The package MUST be organized by reader context: a small top-level entrypoint plus two domain folders, one for cloud infrastructure and one for application engineering. Avoid duplicating the same finding across files; assign it to the domain where the owner will act.

Every retained file MUST begin with a short `Purpose:` blockquote explaining what the file is for.

Required top-level retained output per repository:

- `01-executive-summary.md`
- `02-inventory-and-current-state.md`
- `03-remediation-plan.md`
- `04-consistency-gate.md`
- `open-questions-and-blockers.md`

Required `cloud-infra/` output:

- `cloud-infra/01-overview.md`
- `cloud-infra/02-architecture.md`
- `cloud-infra/03-iac-code-and-scripts.md`
- `cloud-infra/04-automation-and-cicd.md`
- `cloud-infra/05-governance-and-auditability.md`
- `cloud-infra/06-security-and-compliance.md`
- `cloud-infra/07-remediation-plan.md`

Required `application-engineering/` output:

- `application-engineering/01-overview.md`
- `application-engineering/02-architecture.md`
- `application-engineering/03-code-and-script-quality.md`
- `application-engineering/04-testing-and-validation.md`
- `application-engineering/05-automation-and-cicd.md`
- `application-engineering/06-security-and-dependency-hygiene.md`
- `application-engineering/07-remediation-plan.md`

If the repository already has a retained review package, preserve the prior files and add complement files such as:

- `05-review-addendum.md` at top level, or a numbered addendum inside the relevant domain folder.

`01-executive-summary.md` must always exist as the entrypoint for a fresh review package and must link to the domain folder overview files, the top-level remediation index, consistency gate, and open questions file.

Each domain detail file must contain:

1. What this file is for
2. Scope for this repository
3. Critical findings in that category (using the Finding Format from section 8)
4. Medium findings in that category
5. Low findings in that category
6. Quick wins specific to that category, if any
7. Open questions specific to that category, if any

If a domain detail file has no meaningful issue, the file must still exist and explicitly say: `No relevant finding observed.` so reviewers know the dimension was assessed.

`03-remediation-plan.md` is a short routing index only. It must link to `cloud-infra/07-remediation-plan.md` and `application-engineering/07-remediation-plan.md`.

The two domain remediation plan files hold their own priorities, quick wins, strategic moves, and file actions. Do not create separate backlog, quick-win, and file-action files unless the user explicitly asks for them.

## 10. Required Tables

Use compact tables where relevant. Tables should normally have 3 or 4 columns and MUST NOT exceed 5 columns unless the user explicitly asks for a wider table. Prefer bullets for details that would make a table hard to read.

Priority plan:

| Priority | Area | Work item | First action |
| --- | --- | --- | --- |

Allowed priorities:

- P0 = critical risk or major blocker
- P1 = high value or high risk
- P2 = important but not urgent
- P3 = cleanup or optional optimization

File actions:

| Action | Target | Reason | Effort |
| --- | --- | --- | --- |

Allowed actions:

- keep
- delete
- merge
- split
- rename
- compress
- move
- create
- automate
- standardize

Quick wins:

| Action | Owner area | Target |
| --- | --- | --- |

## 11. Cross-Repo Output When Reviewing More Than One Repository

If more than one repository is in scope, also produce a global split review under `tmp/superpowers/mega-review-global/`.

Minimum global output:

- `01-executive-summary.md`
- `02-consistency-cross-repo.md`
- `03-security-and-automation-gaps.md`
- `04-global-roadmap.md`
- `05-global-ai-readiness.md`
- `06-recommended-global-standard.md`
- `open-questions-and-blockers.md`

Optional when complementing an existing global package:

- `07-review-addendum.md`
- `08-critical-master-consistency-gate.md`

Global review coverage must include:

1. Executive summary
2. Global maturity matrix
3. Cross-repo consistency
4. Common security gaps
5. Common automation opportunities
6. Standardization candidates
7. Provider-specific or domain-specific differences that should remain local
8. Global AI-readiness assessment
9. Recommended repository standard
10. Global prioritized roadmap

Use this compact maturity matrix:

| Repo | Strengths | Main gaps | Top next step |
| --- | --- | --- | --- |

Use this compact roadmap table:

| Priority | Initiative | Repositories | First step |
| --- | --- | --- | --- |

## 12. Review Discipline

- Be severe but useful.
- Prefer pragmatic changes over aesthetic refactors.
- Recommend invasive changes only when the benefit is clearly justified.
- For every invasive proposal, explain why it is necessary, the less invasive option, the risk of doing it, the risk of not doing it, and the estimated effort.
- Do not overuse `Must`.
- Do not confuse temporary uncertainty with a verified problem.

## 13. Existing Analysis Handling

If the repository already contains prior analysis under `tmp/`:

- Read it first.
- Preserve what is still valid.
- Only add missing sections, corrected evidence, or newly observed findings.
- Avoid duplicating the same backlog item unless the evidence has materially changed.
- Keep newly created retained artifacts in English even when prior retained analysis used another language or legacy filenames.

## 14. Final Consistency Gate

Before finishing, validate the resulting analysis against the challenge posture defined in:

- [.github/agents/internal-gateway-critical-master.agent.md](../agents/internal-gateway-critical-master.agent.md)

Run a brief consistency gate that answers:

1. What in the final review is most likely correct?
2. What is most likely incorrect, contradictory, overstated, or insufficiently verified?
3. Which findings should be downgraded, reframed, or moved to open questions?

If useful, save that gate as a retained artifact in the global package or in the reviewed repository package.

## 15. Final Quality Bar

Before stopping, verify that the retained output is:

- Concrete
- Verifiable
- Non-generic
- Non-destructive
- Adapted to the observed repositories and stacks
- Split into multiple files
- Written with English retained content and filenames
- Useful for follow-up implementation work
- Explicit about impact, priority, effort, and uncertainty

If a repository cannot support a complete review because key evidence is missing, say exactly what is not verifiable from the repository and continue with the parts that are verifiable.
