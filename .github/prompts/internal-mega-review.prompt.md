---
name: "internal-mega-review"
agent: "internal-gateway-operational-flow"
description: "Run an analysis-only retained mega review for one or more repositories and write split English analysis under `tmp/`."
argument-hint: "Repository paths or names plus optional focus, constraints, or chat-language preference"
---

<!-- markdownlint-disable-file MD041 -->

Repositories to review:
${input:repositories:List one or more repository paths or names. Use one per line when possible.}

Optional focus areas:
${input:focus:Optional focus such as security, governance, architecture, testing, automation, documentation, AI-readiness, or migration risk.}

Optional constraints or exclusions:
${input:constraints:Optional non-negotiables, exclusions, prior findings to preserve, or rollout concerns.}

Chat response language:
${input:language:Match the current chat unless explicitly overridden. Retained artifacts must stay in English.}

Use these sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
- [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)

Execution contract:

- This prompt is analysis-only. Do not apply fixes or edit production assets.
- Write retained analysis only under `tmp/`.
- Resolve each repository independently before any cross-repo synthesis.
- If a repository path is ambiguous or missing, ask only for the unresolved
  repository.
- Prefer repository evidence over assumptions and move unsupported claims to
  open questions or blockers.
- When a repository-owned bundle owner such as `SKILL.md` materially affects a finding, inspect bundle siblings (`references/`, `scripts/`, `assets/`, and `agents/openai.yaml`) or mark the intentional non-action.

Retained output locations:

- Per repository: `<repo>/tmp/superpowers/mega-review/`
- Multi-repository synthesis:
  `tmp/superpowers/mega-review-global/`

Required per-repository package:

- `01-executive-summary.md`
- `02-inventory-and-current-state.md`
- `03-remediation-plan.md`
- `04-consistency-gate.md`
- `open-questions-and-blockers.md`
- `cloud-infra/01-overview.md`
- `cloud-infra/02-architecture.md`
- `cloud-infra/03-iac-code-and-scripts.md`
- `cloud-infra/04-automation-and-cicd.md`
- `cloud-infra/05-governance-and-auditability.md`
- `cloud-infra/06-security-and-compliance.md`
- `cloud-infra/07-remediation-plan.md`
- `application-engineering/01-overview.md`
- `application-engineering/02-architecture.md`
- `application-engineering/03-code-and-script-quality.md`
- `application-engineering/04-testing-and-validation.md`
- `application-engineering/05-automation-and-cicd.md`
- `application-engineering/06-security-and-dependency-hygiene.md`
- `application-engineering/07-remediation-plan.md`

Required findings format:

- Severity: `Critical`, `Medium`, or `Low`
- Category: `Security`, `Architecture`, `Automation`, `Testing`,
  `Documentation`, `Governance`, `AI-readiness`, or `Cleanup`
- Evidence: concrete files, workflows, repeated patterns, or explicit
  cross-repo contrast
- Problem, impact, proposed action, estimated effort, invasiveness, and less
  invasive alternative when relevant

If a prior retained package already exists, preserve it and add only the
missing coverage, corrections, or review addendum that current evidence
requires.
