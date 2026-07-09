# Review Profiles

Use this reference to choose the smallest review profile that can still prove
the decision.

## Family coverage baseline

These families are reviewable when they are in scope or referenced by an
in-scope owner:

- governance bridge: `AGENTS.md`, `.github/copilot-instructions.md`,
  `.github/INVENTORY.md`
- wrapper surfaces: `.github/agents/*.agent.md`, `.github/prompts/*.prompt.md`
- skill bundles: `.github/skills/**/SKILL.md` plus `references/`, `scripts/`,
  `assets/`, and `agents/openai.yaml`
- enforcement: validators, inventory builders, sync helpers, runtime matrices,
  home-sync catalogs, and AI-catalog tests
- retained analysis: review packages under `tmp/` and explicitly referenced
  local docs or manifests

## Profile selector

| Profile | Use when | Default scope | Escalate when |
| --- | --- | --- | --- |
| `focused` | One concrete file or one narrow resource needs review. | Target file, direct references, nearest validator or test, and the smallest required governance files. | A bundle sibling, paired wrapper, sync surface, or validator family becomes material to the decision. |
| `bundle` | The target is a skill, agent, prompt bundle, or one owner whose siblings and propagation matter. | Bundle root, existing siblings, paired wrapper or owner, nearest validators or tests, and affected propagation surfaces. | The decision crosses multiple bundles or needs bridge, inventory, sync, or catalog-wide reasoning. |
| `catalog` | The target spans multiple AI families or the full repository AI catalog. | Bridge files, live prompts, agents, skills, validators, tests, and sync surfaces relevant to the stated decision. | A narrower subset can prove the decision, or the request is really about one retained report package. |
| `retained-report` | The target is an existing retained report package under `tmp/`. | Retained package files plus live repository evidence for every claim that matters. | The user asks to revise live assets, or the report claim requires bundle or catalog review of current files. |

## Target resolution rules

- A path to `.github/skills/<name>/SKILL.md` or `.github/skills/<name>/`
  defaults to `bundle`. Include existing `references/`, `scripts/`, `assets/`,
  and `agents/openai.yaml`.
- A path to one prompt or agent defaults to `focused` unless paired skills,
  validators, or propagation surfaces are material to the decision.
- A folder target under `.github/skills/`, `.github/agents/`, `.github/prompts/`,
  or `.github/scripts/` defaults to `catalog` when it spans more than one owner
  family.
- A path under `tmp/` that looks like a retained review package defaults to
  `retained-report`.
- If the target is ambiguous, resolve the smallest obvious path from repository
  evidence and record the unresolved edge as an evidence gap instead of guessing.

## Minimum evidence pass

### `focused`

1. Read the target file and its nearest validator, test, or paired owner.
2. Read `AGENTS.md` and `.github/copilot-instructions.md` when the decision is
   governance-sensitive.
3. Confirm one real consumption signal such as agent routing, prompt reference,
   inventory presence, sync inclusion, or test coverage.

### `bundle`

1. Read the bundle root owner.
2. Read every existing sibling under `references/`, `scripts/`, `assets/`, and
   `agents/openai.yaml`, or mark intentional non-action.
3. Read the nearest validator or test plus any paired wrapper or owner the
   bundle points to.
4. Confirm propagation surfaces such as inventory, sync, runtime matrices, or
   explicit allowlists.
5. Check live prompt packs, generated artifacts, retained reports, or fixtures
   when the bundle governs materialized output.

Report coverage separately from findings. Checked-clean siblings and propagation
surfaces should support the verdict through an evidence digest or decision trace
instead of appearing as artificial findings.

### `catalog`

1. Read `AGENTS.md`, `.github/copilot-instructions.md`, and
   `.github/INVENTORY.md`.
2. Read the live prompts, agents, skills, scripts, or tests that are directly
   relevant to the stated decision.
3. Map the validator and sync entrypoints that prove the catalog behavior.
4. Check context economy before recommending more always-on or wrapper-level
   content.

### `retained-report`

1. Read the retained package summary and decision sections first.
2. Re-verify every material claim against current repository files, validators,
   or tests.
3. Mark stale, missing, or unverifiable claims explicitly.

## Escalation and de-escalation

- Start at `focused` by default.
- Escalate to `bundle` when sibling resources, lifecycle checks, or propagation
  controls matter.
- Escalate to `catalog` when the decision touches bridge files, inventory,
  sync, or multiple resource families.
- Stay in `retained-report` only while treating the package as evidence. If the
  user asks to change live assets, route to the appropriate delivery or review
  owner separately.
