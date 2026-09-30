# Imported Skill Normalizations

This reference owns the imported-skill normalization policy for the
`local-agent-sync-external-resources` sync skill. The paired `SKILL.md` owns
the operator contract: modes, commands, workspace flow, TSV output, safety,
and validation. Content here describes what the candidate builder enforces per
declared source.

## Managed Skill Reference Normalization

- A source may set `rewrite_skill_references: true` to rewrite slash commands
  and backtick skill references from declared upstream basenames to declared
  `canonical_name` values.
- `skill_reference_aliases` are source-local and point only at declared
  canonical names.
- The `mattpocock-skills` source imports all 25 direct `engineering/` and
  `productivity/` bundles from the pinned release. Keep `grill-me` and
  `grilling` unprefixed; prefix the other 23 canonical names with
  `mattpocock-`.
- Redirect Matt consumer references from `/grilling` to `/grill-me` only after
  canonical reference rewriting. Build the canonical `grill-me` skill with its
  own frontmatter and metadata plus the `grilling` body, so the interview needs
  no second skill invocation. Keep `grilling` as the declared upstream engine
  but publish it as a user-invoked alias back to `/grill-me`; fail candidate
  creation if the engine adds resources that are not merged.
- References to undeclared skills remain unchanged and are reported as
  unresolved dependencies.

## Managed Skill Frontmatter

- Normalize managed `SKILL.md` files for Codex and GitHub Copilot while
  preserving `/skill-name` references.
- Remove `disable-model-invocation` by default because it is not standard Codex
  skill metadata.
- Remove upstream `policy.allow_implicit_invocation` from `agents/openai.yaml`
  by default when the asset declares no `codex.allow_implicit_invocation`.
  Keep other `policy` fields, drop an empty `policy`, and leave metadata
  without that field byte-identical.
- Apply `invocation_policy` generically per asset. Its fields are
  `copilot.disable_model_invocation` and `codex.allow_implicit_invocation`;
  do not hardcode per-asset exceptions.
- The Matt source declares 13 upstream user-invoked skills explicitly and
  leaves the other 12 model-invoked skills unrestricted. Keep `grill-me`
  model-invocable and make `grilling` user-invoked, so skills that must
  interview the user load the self-contained canonical entrypoint.
  Preserve this split in both runtimes.
- `superpowers-brainstorming` remains an independently declared exception:
  keep `disable-model-invocation: true` in `SKILL.md` and set
  `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
- `mattpocock-implement` and `mattpocock-to-spec` are Codex-only restrictions:
  keep `codex.allow_implicit_invocation: false` and declare no Copilot policy,
  because `internal-gateway-execute-plans` and `internal-gateway-idea` `+spec`
  must load them as handoff owners.
- `tests/test_external_resource_catalog_contract.py` verifies that committed
  invocation metadata matches the manifest in both runtimes: declared skills
  carry their policy, and undeclared skills carry none. It checks metadata,
  not observed runtime selection.

## Executable Python Normalization

- A source may set `ensure_python_shebangs: true` to prepend
  `#!/usr/bin/env python3` to executable `.py` files without a shebang.
- The Anthropic source enables this normalization.
- Preserve existing shebangs, non-executable Python modules, and non-Python
  executables unchanged.

## Guided Question Contract

- Append the repository-owned bulk-question contract only to
  `superpowers-brainstorming`.
- Require numbered bulk question blocks. Every question includes a brief
  `Recommendation`, `Why`, and `Default if accepted`.
- Explicitly override upstream one-question-at-a-time pacing. A single
  remaining blocker is a numbered one-item block.
- Use a marker-based idempotent append, never a context-sensitive replay patch.

## Superpowers No-Commit Contract

- Append the repository-owned no-commit contract to the `SKILL.md` of every
  asset from the `obra-superpowers` source, between the
  `local-sync:no-commit` markers.
- The contract overrides upstream commit steps in the skill, its bundled
  prompts, and its scripts. Agents leave changes uncommitted, replace commit
  steps with validation and a `git status --short` report, and review
  `git diff <BASE>` instead of commit ranges.
- Every subagent brief dispatched from these skills must carry the contract.
  Only an explicit user request in the current conversation authorizes a
  commit.
- Leave bundled prompts and scripts byte-identical to upstream; the `SKILL.md`
  contract controls them. The only exception is the sibling-path rule below.
- Adding or changing this block changes the
  `superpowers-brainstorming` override `expected_content_hash`; recompute it in
  the same change.

## Superpowers Sibling Paths

- In every file of every `obra-superpowers` asset, including scripts, rewrite
  relative sibling-skill paths such as `../subagent-driven-development/` or
  `../../subagent-driven-development/` to the prefixed canonical directory
  name.
- Rewrite only a path segment that follows one or more `../` and matches the
  upstream directory name of a declared `obra-superpowers` asset. Leave every
  other byte unchanged.

## Repository-Owned Skill Contracts

- Express additive behavior, workspace, and output-path requirements as
  canonical-name-scoped, marker-based candidate normalizations.
- Each normalization replaces its own marked block, is idempotent, and
  preserves unrelated upstream content.
- Retain only the Matt Pocock Handoff, Teach, and Improve Architecture
  repository paths. Keep Handoff non-duplication wording as a canonical marked
  normalization rather than replay-patch ownership.
- Keep Matt Research output under `tmp/.research/`. Before delegation, the
  caller applies a value gate; when delegation is worthwhile, it uses
  `/internal-subagent-contract` and retains routing, authority, acceptance, and
  validation.
- Do not add Git-autonomy, Wayfinder workspace, Wayfinder critical-validation,
  Wayfinder grilling, or `grill-me` guided-question contracts to Matt imports.
- After composition, apply one marker-based scope-and-convergence guardrail to
  canonical `grill-me`; preserve the imported body, rounds, frontier,
  formatting, and invocation policy.
- Do not create or register new Git replay patches for imported-skill
  customizations. Keep existing legacy entries supported without extending
  their scope; incompatible legacy replay still stops for review.
- Append instruction overrides at the end of the affected `SKILL.md` in one
  marked note that explicitly supersedes earlier conflicting information.
  Preserve unrelated upstream content and replace the note idempotently.
- For path changes, search only the declared target bundle and rewrite matched
  path boundaries in text files, including executable scripts. Do not match
  surrounding prose, line numbers, or a full-file hash. Record the target,
  search rule, destination, and behavioral validation here and implement it
  in the candidate normalizer for every refresh.
- If the upstream path or producer changes beyond the recorded rule, inspect
  the new producer and update the bounded search and behavioral check. Do not
  silently assume that the old rule proves the new producer's destination.

## Idea Refine Output Override

- Target only the canonical `addyosmani-idea-refine` bundle.
- Search every UTF-8 text file, including scripts and nested references, for
  the project-root path `docs/ideas` or `./docs/ideas`, and replace it with
  `tmp/ideas`. Preserve suffixes, unrelated text, paths such as
  `docs/ideas-archive`, and nested paths such as `other/docs/ideas`.
- Append or move one `local-sync:idea-refine-workspace` marked override to the
  end of `SKILL.md`. It keeps every idea artifact inside `tmp/ideas/` and
  retains user confirmation before saving the final one-pager.
- No replay patch or expected full-file hash owns this override. The native
  candidate tests execute the initialized script after normalization, check
  repeated runs and retained artifacts, simulate changed upstream wording and
  variable names, and verify scope and idempotence.
- Run `tests/scripts/test_candidate.py -k idea_refine` and the full native sync
  test suite before accepting changes to this rule. Keep test workspaces under
  repository-local `tmp/`.

## Single Implementation Plan

- Target only `addyosmani-planning-and-task-breakdown`. In every UTF-8 text
  file, replace project-root `tasks/plan.md` and `tasks/todo.md` (optionally
  prefixed by `./`) with `tmp/.plans/YYYY-MM-DD-HHMM-<topic>.md`. Preserve
  nested paths and filename suffixes such as `.backup`.
- Append one `local-sync:planning-output` override at the end of `SKILL.md`.
  It supersedes separate todo files, implicit tracker selection, creation of
  `tasks/`, and routine human checkpoint prompts. It requires one plan with
  detailed task contracts and a separate mutable progress section.
- The user's executor invocation authorizes the identified plan; a writer
  result or internal call does not. Explicit human gates and real blockers
  remain authoritative. Never overwrite other incomplete work or migrate plans.
- New implementation plans always stay under `tmp/.plans/`, including an
  explicitly requested alternative filename or tracker-backed plan.
- Test bounded path replacement, nested-path preservation, unchanged neighbors,
  upstream text additions, trailing override placement, and idempotence through
  `tests/scripts/test_candidate.py -k planning_normalization`.

## Retired Plan Skills And Gateway Routing

- `superpowers-writing-plans` and `superpowers-executing-plans` are retired:
  remove their manifest declarations and local bundles. Do not reimport them.
- Only in `superpowers-brainstorming`, replace complete `writing-plans` or
  `superpowers-writing-plans` names with `internal-gateway-writing-plans`.
  Only in `superpowers-subagent-driven-development`, replace `executing-plans`
  or `superpowers-executing-plans` with `internal-gateway-execute-plans`.
  Search all UTF-8 text resources in each declared target bundle. Preserve
  compound identifiers and unrelated content.
- Append one `local-sync:plan-gateway-routing` note after other normalizations.
  It overrides conflicting handoff instructions without adopting another
  workflow. Spec approval alone does not request a plan. Inline routing never
  manufactures the user's execution approval or widens writable authority.
- Preserve the legacy brainstorming description patch. Since normalization
  runs before replay and changes the verified content, recompute that existing
  override's `expected_content_hash` when its normalized output changes; do
  not add or extend a replay patch.
- Run `tests/scripts/test_candidate.py -k retired_planner_routing`, manifest
  tests, and the full native sync suite. Source snapshot path attestations must
  be rebuilt when the declared Superpowers import set changes; the pinned SHA
  does not change. Do not accept a stale attestation by weakening checks.
