# Failed Run Debugging

Use this reference when a workflow run failed on a branch, schedule, or
manual dispatch. For end-to-end triage of failing checks on an open PR, the
primary owner is `/openai-gh-fix-ci`; this reference applies when the cause
sits in workflow or action YAML.

## Procedure

1. Get the failing evidence first:

   ```bash
   gh run list --workflow <file>.yml --limit 5
   gh run view <run-id> --log-failed
   ```

2. Find the first failed step. Later steps marked skipped are consequences,
   not causes.
3. Classify the cause before editing:

   | Signal | Likely cause | Fix direction |
   |---|---|---|
   | `Resource not accessible by integration` | Missing `GITHUB_TOKEN` scope | Grant the named scope on the job, or disable the option that needs it |
   | Expression or context error | Context not available in that key | Check the context-availability table and move the expression |
   | `Unable to resolve action` | Bad pin or removed release | Re-pin to a verified full SHA |
   | Timeout or queued for a long time | Runner capacity | Hand off to `internal-github-platform` |
   | Test or build failure inside a script | Application code | Hand off to the code owner; the workflow is not the cause |

4. Propose the smallest fix and state how to verify it (rerun, `actionlint`,
   or a dispatch on a branch).

## Traps

- **`pull_request_target`:** the run uses the workflow definition from the
  default branch. A workflow fix inside the PR does not change that PR's run.
  Say so, and validate the fix after merge or on a safe trigger.
- **Action options that widen scope:** some third-party options (for example
  PR comments or check annotations) need more `GITHUB_TOKEN` permissions than
  the action's default. When the action's documentation names a scope, grant
  exactly that scope on the job or turn the option off. Never switch to
  `write-all`.
- **Re-runs:** "Re-run failed jobs" reuses the original commit and workflow
  file. Push a commit or dispatch again to test a changed workflow.
