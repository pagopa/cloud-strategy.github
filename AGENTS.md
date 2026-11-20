# AGENTS.md - Repository Operating Core

Keep this baseline portable across repositories.

## Scope And Precedence

- The optional sibling `AGENTS.local.md` owns local policy. If it exists,
  read it before acting and apply it after this baseline. Otherwise proceed
  without creating it.
- Direct user instructions win for the current task unless they require unsafe,
  destructive, or impossible behavior.
- The narrowest applicable owner overrides broader defaults. Local and narrower
  rules must respect user instructions, [Boundaries](#boundaries), and the
  [Protected Skill Boundary](#protected-skill-boundary).
- Keep one active primary owner per execution lane. It makes material decisions
  and accepts the result. Load a narrower owner only when evidence calls for it.
- Apply current policy from its owning file on disk. Exclude removed files,
  generated output, historical aliases, and past automation as policy sources.

## Boundaries

- Keep secrets out of code and history.
- Ask before destructive or irreversible actions and before changing policy or
  a public contract.
- Never force-push or delete others' work.
- Within these limits, a request in the current turn authorizes the action it
  names. Commit only if the user requests a commit in that turn. An answer to
  a question you initiated cannot authorize a commit.

## Think Before Coding

- Before broad reading or commands, identify the target, its nearest owner,
  and the evidence you need. If an executable check applies, name the closest
  one and its expected result. For prose-only work, define an observable
  condition on the final text. For multi-step work, write a plan before
  editing and pair each step with its check.
- Honor explicit scope limits. Inspect known files or symbols directly. Widen
  the search only to locate an unknown component or call path. Use a graph or
  index only when `AGENTS.local.md` or a loaded skill directs it.
- Keep review in proportion to the change. A small policy edit needs its
  nearest owner and adjacent checks. For a one-line change in a known config,
  the file and one adjacent check suffice. Use a heavy workflow only for a
  concrete ambiguity or contradiction.
- Before a non-trivial edit, state the intended result, non-goals, tradeoffs,
  and open questions. Give the assumption and rejected reading on one line
  using `Assumption: <X>. Rejected: <Y>.` Propose a simpler approach when one
  meets the goal.
- Ask one specific question with your recommendation when plausible readings
  lead to materially different edits, a simpler alternative would materially
  change the design the user requested, or an action needs approval. Wait for
  the user's answer before making the affected edit or taking the action.
  If you cannot reach the user, stop at that decision and report the blocker.
- With no decision pending, proceed directly on deterministic, low-risk,
  reversible work or when every reading leads to the same change. Favor
  caution when the risk is unclear.
- On a dirty working tree, take a read-only snapshot of the initial state
  and declare the task file allowlist before editing.

## Build Simple And Surgical

- Write the least code that meets the request. Keep new single-use logic inline,
  omit speculative options, and handle only reachable internal states.
  Validate data at external boundaries.
- Match the surrounding style. Every changed line must trace to the request,
  including comments and formatting inside a function you edit.
- Remove imports, variables, and functions your change makes unused. Report
  unrelated dead code and leave it in place unless the user requests removal.

## Prove With Checks

- Test executable or evaluable behavior first. Reproduce bugs with a failing
  check before fixing them. For new validation, start with failing tests for
  invalid inputs. For refactors, run the same checks before and after.
- After editing, run the closest applicable executable check if available.
  For prose-only work, also verify the stated condition on the final text.
  Run any broader checks the change requires. Fix failures caused by the
  change and rerun affected checks.
- Investigate each failure. Keep failures in code the diff touches or calls
  in scope and never classify them as pre-existing. For other failures, use
  that label only with baseline evidence, such as the same failure on
  untouched `HEAD`. Report unresolved causes explicitly.
- When policy or a contract changes, align the owning tests, validators, and
  documentation. Enforce hard guarantees with permissions, validators, hooks,
  or CI.
- Compare the final diff with the initial state. Remove your own out-of-scope
  hunks and simplify speculative code you introduced. Preserve pre-existing
  edits. If clarification came after editing began, report it and confirm the
  diff matches the clarified request.
- Re-read changed files from the working tree before reporting. Ground claims
  about behavior, runtimes, validators, sync, tests, and policy in repository
  evidence. Report actual check results, unavailable checks, and evidence gaps.
- In comparative evaluations, report regressions separately from unmet
  improvement targets. Identify which results come from actual runs of the
  system under test.

## Human-Facing Responses

- Use the format the user requests. Where the user leaves it open, follow the
  applicable skill's output contract, then the defaults here.
- Lead with the outcome and fit the response on one screen. Include material
  errors, security warnings, blockers, risks, uncertainty, gaps in validation,
  and the next required action.
- Create an artifact only when the task needs one. If it holds the full
  evidence, summarize the outcome, changes, risks, and next action.

## Skill Resolution

- For a filesystem skill named by the user or a loaded skill, verify the exact
  resolved `SKILL.md`. If you need to locate it, search only the declared
  skill roots, even when the catalog omits it. Follow symlinks within permission
  and trust boundaries. Resolve relative resources from its canonical directory.
- Use provider-specific discovery for other skills. Report the specific blocker
  when a skill is missing, a link is broken, a file is unreadable, or the
  runtime cannot invoke a present skill.

## Protected Skill Boundary

- Imported and third-party bundles are read-only by default. In repositories
  with origin prefixes, also protect every bundle whose name lacks an
  `internal-` or `local-` prefix.
- Edit a protected bundle only on an explicit user instruction in the current
  conversation naming the exact skill or path. Limit the edit to the requested
  files, purpose, and turn. Using, wrapping, syncing, or depending on a skill
  grants no edit permission.
- Stop on any unapproved protected-skill finding. Never add an allowlist entry
  to bypass it.

## Placement And Authoring

- Keep detailed procedures, checklists, file layouts, command playbooks, and
  tool-specific workflows in their owning skills or files.
- Use Plain Technical English for repository-owned prose unless a narrower
  owner specifies otherwise. Use short sentences, stable terms, active voice,
  and explicit `must`, `should`, and `may`. Preserve required technical names.
- Place native tests with the component and runner that own the behavior.
  Reserve repository-root `tests/` for non-native or cross-boundary behavior.
