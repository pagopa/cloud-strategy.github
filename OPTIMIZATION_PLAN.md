# Remaining Optimization Plan

Outstanding work only. Completed items were removed after re-auditing the current repository state.

Current snapshot on this branch:

- Skills: `122`
- Instructions: `28`
- Prompts: `20`
- Agents: `12`

Already completed and therefore removed from this plan:

- Creation of `internal-agents-md-bridge`
- Creation of `internal-copilot-audit`
- Creation of `internal-agent-authoring`
- Split of the old platform command-center direction into `internal-agent-cicd` and `internal-agent-copilot-governance`
- Creation of `internal-agent-developer`
- Creation of `internal-agent-architect`
- Creation of `internal-agent-infrastructure`
- Creation of `internal-agent-code-review`
- Creation of `internal-agent-quality`
- Creation of `internal-agent-principal-aws`
- Creation of `internal-agent-principal-azure`
- Creation of `internal-agent-principal-gcp`
- Python conversion of `.github/scripts/validate-copilot-customizations.sh`
- Final deprecated frontmatter cleanup, including `antigravity-warren-buffett`
- Removal of retired or overlapping skills:
  - `claude-agent-development`
  - `claude-skill-creator`
  - `awesome-copilot-create-agentsmd`
  - `antigravity-ddd-context-mapping`
  - `antigravity-ddd-strategic-design`
  - `antigravity-ddd-tactical-patterns`
  - `antigravity-error-detective`
  - `antigravity-cloud-devops`
  - `antigravity-bash-scripting`

## Ranking (truth priority, highest first)

1. `claude` (Anthropic)
2. `obra` (obra/superpowers-skills)
3. `terraform` (hashicorp/agent-skills)
4. `awesome-copilot` (github/awesome-copilot)
5. `antigravity` (sickn33/antigravity-awesome-skills)
6. `internal` (this repository)

Internals are the governance layer and are always kept.
When two external skills overlap, delete the lower-ranked one.

---

## Phase 1 — Patch internal instructions (5 files)

Add a "Core Knowledge Source" header to each internal instruction that overlaps with an external instruction.

| Internal instruction | Core Knowledge Source (external) |
|---------------------|----------------------------------|
| `internal-terraform.instructions.md` | `awesome-copilot-terraform.instructions.md` |
| `internal-terraform-azure.instructions.md` | `awesome-copilot-terraform-azure.instructions.md` |
| `internal-docker.instructions.md` | `awesome-copilot-containerization-docker-best-practices.instructions.md` |
| `internal-github-actions.instructions.md` | `awesome-copilot-github-actions-ci-cd-best-practices.instructions.md` |
| `internal-bash.instructions.md` | `awesome-copilot-shell.instructions.md` |

Add this block immediately after the frontmatter closing `---`:

```markdown
<!-- Core Knowledge Source: <external-instruction-filename> -->
<!-- This internal instruction extends the external with governance-specific rules. -->
<!-- Do not duplicate content from the core source; reference it instead. -->
```

---

## Phase 2 — Delete prompts now superseded by skills or agents

Delete these prompts:

```bash
rm .github/prompts/internal-code-review.prompt.md
rm .github/prompts/internal-cicd-workflow.prompt.md
rm .github/prompts/internal-cloud-policy.prompt.md
rm .github/prompts/internal-docker.prompt.md
rm .github/prompts/internal-pr-editor.prompt.md
rm .github/prompts/internal-sync-global-copilot-configs-into-repo.prompt.md
rm .github/prompts/internal-pair-architect-analysis.prompt.md
rm .github/prompts/internal-python-script.prompt.md
rm .github/prompts/internal-python.prompt.md
rm .github/prompts/internal-bash-script.prompt.md
rm .github/prompts/internal-java.prompt.md
rm .github/prompts/internal-nodejs.prompt.md
rm .github/prompts/internal-terraform.prompt.md
rm .github/prompts/internal-data-registry.prompt.md
rm .github/prompts/internal-github-composite-action.prompt.md
```

Keep only:

- `internal-terraform-module.prompt.md`
- `internal-github-action.prompt.md`
- `internal-add-unit-tests.prompt.md`
- `internal-add-platform.prompt.md`
- `internal-add-report-script.prompt.md`

### Validation

```bash
ls .github/prompts/*.prompt.md | wc -l
# Expected: 5
```

---

## Phase 3 — Second overlap pass

Run a new audit with `internal-copilot-audit` and review these candidates specifically:

- `antigravity-simplify-code` vs `antigravity-code-simplifier`
- `antigravity-javascript-mastery` vs `antigravity-javascript-pro`
- `awesome-copilot-azure-architecture-autopilot` for runtime-specific assumptions that may justify internal replacement or retirement

Apply the same rule set:

- no deprecated fallback assets
- no hollow bundles
- no weaker aliases kept beside a stronger internal or cleaner external skill

---

## Phase 4 — Obra compatibility notes

Add a compatibility warning after the frontmatter in:

- `.github/skills/obra-dispatching-parallel-agents/SKILL.md`
- `.github/skills/obra-subagent-driven-development/SKILL.md`
- `.github/skills/obra-remembering-conversations/SKILL.md`

```markdown
> **Compatibility note:** This skill was designed for Claude Code. Some features
> (subagent dispatch, conversation search) are not available in VS Code Copilot.
> The conceptual patterns remain useful as guidance.
```

---

## Final validation checklist

Run after the remaining phases are complete:

```bash
echo "Skills:" && ls -d .github/skills/*/ | wc -l
echo "Instructions:" && ls .github/instructions/*.instructions.md | wc -l
echo "Prompts:" && ls .github/prompts/*.prompt.md | wc -l
echo "Agents:" && ls .github/agents/*.agent.md | wc -l

echo "Deprecated tools:" && grep -rl "^tools:" .github/agents .github/skills | wc -l
echo "Deprecated model:" && grep -rl "^model:" .github/agents | wc -l
echo "Deprecated color:" && grep -rl "^color:" .github/agents | wc -l

python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict
```
