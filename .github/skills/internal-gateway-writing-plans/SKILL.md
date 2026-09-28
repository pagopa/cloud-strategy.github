---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs an approved implementation plan written from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

Write one retained implementation plan and hand it to /internal-gateway-execute-plans only after its contract and read-only handoff gate pass. Load /superpowers-writing-plans and references/plan-contract.md before writing. The imported skill owns plan structure and self-review; this skill owns the repository-specific rules below.

## When to use

- The user asks for an implementation plan from an approved design, a reviewed retained spec, or concrete direct requirements.
- /internal-gateway-idea hands off a +plan selection, with or without a retained spec marked plan_authoring_ready: true.
- /internal-gateway-execute-plans returns a legacy plan for re-authoring.

## When not to use

- Early or unclear ideas belong to /internal-gateway-idea.
- Bounded one-session work belongs to /internal-gateway-simple-task.
- Plan execution belongs to /internal-gateway-execute-plans.
- Edits to imported superpowers-* skills are out of scope.

## Eligibility

Write only when all three conditions hold:

1. The current conversation contains an explicit request to write a plan.
2. A source exists: a retained spec path, an approved design, a reviewed retained spec, concrete direct requirements, or a legacy plan.
3. The target and the anti-scope are known.

A +plan selection satisfies conditions 1 and 2 without another discovery or approval round. implementation_permission: false never blocks plan writing. When a condition is missing, stop and name the one decision that unblocks it.

## Legacy plans

A retained plan with a legacy ## Execution Manifest is conversion input only after an explicit re-authoring request. Leave it unchanged and write a new plan. Set **Spec:** to its Spec when that names a path; otherwise, including direct requirements, use the legacy plan path. Its manifest, execution permissions, and obsolete workflow text carry no authority.

## Workflow

1. Load /superpowers-writing-plans and follow it for file structure, task right-sizing, step content, Interfaces, Global Constraints, Review Focus, and self-review.
2. Apply the repository deltas:
   - Save the plan to tmp/superpowers/plans/YYYY-MM-DD-HHMM-<topic>.md.
   - Use the shared protocol:plan-header block in references/plan-contract.md. Set **Spec:** to the source path; for direct requirements, write direct requirements and copy them into Global Constraints. Set **Status:** to tmp/superpowers/plans/<plan name>/status.md.
   - Write every path outside this repository as <repository root>:<path>. Such sources are read-only context; plan Files paths and commands stay inside this repository.
   - Replace the imported For agentic workers header line with one naming /internal-gateway-execute-plans as the required executor.
   - Classify every executable or evaluable task through /internal-tdd. Record exactly one Posture line per task and order steps to match it: red first for mandatory-test-first, a passing characterization check first for a behavior-preserving refactor, and implementation before validation for feature-first.
   - List every path a task may touch in its Files block. The union of these blocks is the execution perimeter. Apply the shared protocol:files-globs rules. Never list a protected imported skill path unless the user named that exact path in this conversation.
   - Write native, directly executable validation commands. Check that each tool exists before writing its command; never invent a command.
   - Write no commit steps or Git mutations.
   - When another retained plan must deliver an output first, add one Depends on header line per producer, using the shared plan-header syntax. Verify that its path exists. If it does not, write unresolved instead of guessing. Record and run only a read-only check; use pass or fail with a date, or check: none (not-run <date>) when no read-only check exists. A task's planned red test is not a prerequisite.
3. Run every item in the Plan lint checklist in references/plan-contract.md. Fix failures inline and lint again. If an item needs a user decision, retain the unfinished plan and do not hand it off.
4. When lint passes, perform one read-only handoff gate:
   - Read the current branch with git symbolic-ref --quiet --short HEAD.
   - Resolve the default branch with git symbolic-ref --quiet --short refs/remotes/origin/HEAD.
   - Re-run each read-only Depends on check and report its result.
   - Apply Handoff in references/plan-contract.md: classify relevant dirty content, verified upstream output, Foreign paths and conflicting runs. Disjoint work does not block; protected-input changes and relevant pending writes need reconciliation.
   - Show current/default branch, dependency results, relevant dirty Files, Foreign paths and conflicts in one gate message. Offer only the branch and content-bound dirty commands required by that gate; never offer execution while a relevant conflict remains. Preserve per-file evidence for the executor's fresh checks.
   - A supplied Subagent-driven or Inline preference gets one short native-only note. Never ask the user to choose an execution method.
   - Route every valid approval to /internal-gateway-execute-plans. The approval is permission to execute; do not start execution in this skill.
5. Keep the writer read-only with respect to Git mutations and runtime records. Do not create a ledger, status file, or other executor state.

## Boundaries

- No Git mutation while writing or handing off a plan. Read-only branch, dependency, and dirty-path checks are allowed.
- No execution, runtime status file, or ledger creation.
- A plan that still needs a user decision stays unfinished; do not hand it off.

## Report

After the plan and handoff gate are ready, use at most five localized lines:

📋 PLAN READY · <plan name>
🎯 Goal: <target>
🚫 Out of scope: <anti-scope>
🌿 <current branch> / default <default branch> · 🧪 dependencies: <results> · 📂 dirty Files: <paths or none> · Preexisting: <verified upstream paths> · Foreign: <unrelated paths> · Conflicts: <plan and overlap or none>
🛠️ **Action:** <only the needed execute command or commands>

Keep the final action on the last line and make it the only bold action. Omit empty Preexisting and Foreign categories; retain the content-bound delta evidence with the handoff so the offer is inspectable. When no handoff is allowed, name the missing decision, conflicting plan reconciliation or upstream step. If the user supplied Subagent-driven or Inline, include the native-only note in that one action line. Localize the report to the user's language. Do not include the pointing-hand emoji in user-visible output.
