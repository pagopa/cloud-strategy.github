# Advisory Question Bank

Use this reference when `internal-idea-define-advisor` needs `grill-me` coverage for unresolved user-only decisions.

Ask only the branches that local evidence cannot recover. Keep the question set proportionate to the decision risk.

## Core Branches

### Goal and outcome

- What decision must be made before action starts?
- What outcome would make the next owner choice clearly correct?
- What should not happen yet?

### Owner and action surface

- Are you deciding between a direct answer, a local edit, a retained plan, a review, or a repository-owned skill or agent change?
- Is there already a preferred path that should win unless evidence contradicts it?
- Should this stop at a recommendation, or are you asking for the next path to act after approval?

### Validation and evidence

- What evidence would be enough to trust the next step: command output, file diff, review, or explicit gap?
- Is there an existing validator, test, or review path that should constrain the recommendation?
- Does the recommendation need to preserve a manual checkpoint before any edit or phase change?

### Scope and anti-scope

- Which files, directories, or artifacts are in scope?
- What is explicitly out of scope even if it looks adjacent?
- Would the wrong owner create rollout, governance, or policy drift?

### Exploration need

- Are there multiple credible directions that should be explored before choosing?
- Is the uncertainty conceptual enough to justify `idea-refine`, or is it only a missing factual answer?

## Output Reminder

After the questions are resolved, return to the `Gate 0 Advisory Packet` in the paired `SKILL.md`. Do not turn this reference into a standalone workflow.
