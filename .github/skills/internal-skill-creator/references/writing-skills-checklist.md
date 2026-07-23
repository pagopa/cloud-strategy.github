# Writing Skills Checklist

Load this reference when creating a new repository-owned skill or materially revising an existing one.

This is a local distilled checklist informed by external skill-authoring guidance. It exists to keep the wrapper self-contained without cloning the upstream bundle.

## Core posture

- Treat a skill as a reusable guide for future agents, not as a narrative about one past task.
- Prefer executable process over prose: steps, evidence, and exit criteria must change what a future agent does.
- Iron law: do not create or materially revise a skill without first observing the failure, miss, or ambiguity it must fix.
- Use the same proof standard for edits as for new skills.
- Check frontmatter validity before reviewing route quality or body wording. Structural breakage outranks content cleanup.
- Compare the target skill against the closest neighboring owners before deciding the fix. Route quality is a lane-level property.
- Keep `## Referenced skills` immediately after the H1 for any created or materially revised `SKILL.md`.

## Generic skill shape

- Required sections are conditional on behavior, not a rigid template. Frontmatter, H1, trigger-focused `description:`, a clear operating contract, and validation guidance are the stable minimum for material repository-owned skills.
- Conditional sections such as `## Referenced skills`, `## When to use`, `## When not to use`, local references, scripts, examples, and fixtures should appear only when they improve routing, boundary clarity, portability, or maintenance.
- Do not require every section for every skill. A small single-owner skill should stay small when extra sections would only repeat the trigger or body.
- Treat `## Referenced skills` as an audit index, not a preload list. Do not load referenced skills from this section alone; load another skill only when the active task, file, framework, runtime, blocker, validation path, or explicit user request proves that owner is needed.
- Remove duplicated responsibility, not useful trigger reinforcement. Keep short repeated safety or retrieval language when it protects activation, stop conditions, or claim discipline.
- Preserve a working `description:` during cleanup unless the observed baseline failure is routing itself.

## Discovery and retrieval

- Keep `description:` focused on when the skill should load.
- Avoid describing the workflow in `description:`. That creates shortcuts and weakens body retrieval.
- Make `description:` read like realistic user intent, not like a capability summary or mini playbook.
- If `description:` names too many adjacent lanes, treat it as overlap until proven otherwise.
- Add file extensions or path tokens in `description:` only when they materially disambiguate the owner. Do not add long suffix lists when path-based routing or the skill body already proves the lane.
- Use words an agent would actually search for: symptoms, overlaps, file paths, task verbs, and validation terms.
- Prefer direct action-shaped names when naming a new skill.

## Tightening strategy

- Prefer the smallest fix that solves the miss: one description tighten, one boundary note, or one misleading phrase removed.
- Do not rewrite a long body just because it is long. Rewrite only when it duplicates the route, duplicates another owner, or keeps reference material inline.
- A clean "tighten" outcome is often better than expanding the skill.

## Core-backed wrappers

- Compare the wrapper against its core before editing. Inventory which responsibilities the core already owns and remove local restatements instead of polishing them.
- Keep the wrapper limited to its retrieval trigger, repository-local policy, and proven environment fallbacks that the core cannot know.
- Do not restate the core's workflow, decision logic, output contract, or validation procedure. Reference the core by skill name and owner behavior.
- Check the wrapper `SKILL.md`, `agents/openai.yaml`, paired agent, focused tests, and nearby routing text for conflicting or stale contracts.
- Verify external assumptions such as required paths, setup commands, integrations, and runtime capabilities against the current repository before adding a local fallback.
- Structural validation is not semantic alignment. Compare the final wrapper and core responsibilities explicitly, then search for removed owners, stale workflow terms, and conflicting output rules.
- Measure token change with the same method before and after cleanup, but preserve a working trigger and required local safeguards even when they cost a small number of tokens.

## Token discipline

- Keep `SKILL.md` lean and move deeper material into `references/` or reusable tools only when justified.
- If the skill sits behind a paired agent, keep route and boundary language out of `SKILL.md`.
- Preserve a working `description:` during token cuts unless the baseline shows routing is wrong.
- When touching a skill bundle, verify that the bundle stays self-contained by
  default: required instructions, examples, fixtures, metadata, and
  deterministic automation should live inside the bundle unless the contract
  explicitly documents an exception.
- For material skill-bundle revisions, measure the touched bundle or loaded files before and after the first material patch with the same token estimate; if no exact script exists, state the closest measurement.
- Prefer focused references or reusable scripts over broad context dumps when a change needs supporting detail.
- Cross-reference reusable material instead of restating it.
- For lightweight or umbrella skills, treat `## Referenced skills` as an audit index, not a preload bundle. State that named skills stay on-demand and load only when the file, framework, runtime, blocker, or validation path proves that owner.
- If local references own the deep tables, templates, or examples, point to them instead of copying them back into `SKILL.md`.
- Prefer moving static lookup tables, starter templates, and detailed taxonomies into `references/`.
- Prefer new `references/` over new `scripts/` unless the workflow is deterministic, repeated, and execution-heavy.
- If the skill must stay direct-copy portable or runnable outside the source repository, keep the required deterministic automation, loaders, and dependency bootstrap inside the bundle; repository scripts may wrap that engine but should not be the only runnable owner.
- Prefer bundle-relative self-references to files under `references/`,
  `scripts/`, and `fixtures/` over repository-rooted paths to the same bundle
  files.
- Reference other skills by skill name and owner behavior, not by file paths inside their bundles.
- Keep `## Referenced skills` as an audit index: one backticked skill name plus one short owner-behavior phrase per item, or `- None.` when no other skill is referenced.
- Update the referenced-skill index whenever the body adds, removes, renames, routes to, delegates to, or compares against another skill.
- When a referenced-skill rule changes, compare the touched skill with nearby skills that cite it or that it cites. Keep optional owners lazy and on-demand unless the active contract explicitly requires loading.
- Prefer one strong example over several repetitive ones.

## Script output contract (evidence-based)

Apply these rules when a skill introduces or revises scripts, CLIs, or deterministic automation:

- Default to `text` for short operator-facing summaries; use `json` for nested or machine-consumed output; reserve `tsv`/`csv` for large flat tables where token cost is material.
- Do not migrate output formats by default: no first-party source (OpenAI, Anthropic, agentskills.io) ranks TSV above JSON; the spec lists JSON, CSV, and TSV as equivalent structured options.
- Put data on stdout and diagnostics on stderr; keep output bounded with summaries, `--offset`, or `--output` options.
- Require documented `--help`, meaningful exit codes, and scripts that solve their own errors when the failure is deterministic.
- Sources: `agentskills.io/skill-creation/using-scripts.md`, `developers.openai.com/codex/build-skills`, OpenAI curated skill `gh-fix-ci`.

## Test posture

- Run a baseline scenario without the skill or before the edit and capture the failure.
- Re-run the same scenario with the skill after the change.
- Re-run at least one neighboring-owner scenario when the edit changes routing or boundary wording.
- Add a misuse, pressure, or counterexample test based on the skill type.
- Make every verification item evidence-shaped: command output, diff evidence, rendered artifact, or an explicit validation gap.
- When the bundle owns runnable automation, validate the bundled entrypoint directly and validate any repository wrapper separately.
- Verify that every listed referenced skill exists or is explicitly marked as external/on-demand, and that no later skill reference is missing from the index.
- Verify that related skills use compatible referenced-skill wording and do not turn optional owners into preload instructions.
- Verify bundle hygiene: no `__pycache__/`, stale `.pyc`, or other build artifacts inside the touched bundle.
- Verify `agents/openai.yaml` consistency: it must not duplicate top-level `name:` or `description:` keys that can drift from the `SKILL.md` frontmatter, which is the single source of truth.
- Scan the touched bundle for contradictory or ambiguous rules: GPT-5-family models follow instructions literally and degrade on conflicting instructions (OpenAI GPT-5 prompting guide).

## Skill-type checks

- Discipline: test pressure, loopholes, and rationalizations.
- Technique: test failure case, success case, and one misuse case.
- Pattern: test recognition, correct use, and counterexample boundaries.
- Reference: test retrieval, correct application, and common gaps.

## Red flags

- "This is obvious."
- "It is only wording."
- "We can test later."
- "This should probably become a new skill."
- "I already know what the skill should say."
- The section explains a topic but does not alter trigger choice, workflow steps, evidence, or exit criteria.

When one of these appears, stop and re-check the baseline and boundary.
