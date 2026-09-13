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
- After refresh, manually verify that no policy-managed skill is implicitly
  selected in either runtime.

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
- Reserve replay patches for irreducible upstream-line edits. Record why a
  normalization is insufficient before registering an exception.
- Register each approved in-place override in
  `references/imported-asset-overrides.yaml` with a replay patch and expected
  content hash.
- Replay runs clean `git apply --check` first, then `--3way --check` only when
  declared. Stop for review if neither applies.
