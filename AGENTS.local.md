# AGENTS.local.md - Repository-Local Policy

- Do not duplicate skill-owned paths, templates, workflow states, or command
  examples in this file.
- Keep volatile inventory out of this file; `.github/INVENTORY.md` owns the live
  catalog for this repository.

## Purpose

- Keep standards-repository-only policy separate from the shared baseline.
- Keep architecture and local context in `docs/` knowledge documents.

This file applies only to this standards repository. Do not treat these rules
as consumer-repository defaults without an explicit sync contract change.

## Standards Repository Role

- This repository owns the shared Copilot customization baseline, governance
  contracts, catalog automation, source-side sync tooling, and the source
  content used to generate the global home agent baseline.
- Source-managed AI assets live mainly under `.github/`.

## Standards Repository Validation

- Run `make token-risks` or
  `python3 ./.github/scripts/detect_token_risks.py --root .` after changes that
  affect root policy or major AI assets in this repository.

## Standards Repository Locality

- Repo-local planning, brainstorming, temporary analysis, and working artifacts
  stay outside `docs/` unless a narrower owner explicitly says otherwise.
- Consumer or target repositories own their local override layers after
  materialization.
- Skill bundles under `.github/skills/**` must be self-contained. Keep
  instructions, references, examples, fixtures, scripts, and `agents/openai.yaml`
  resolvable from the bundle itself; do not require bundle users to load
  guidance from outside the skill directory.

## Skill Test Boundaries

- Source wording in skills, prompts, references, and instructions is not itself
  an executable or evaluable seam.
- Validate parsed structure, public producer-consumer protocols, executable
  behavior, or concrete evaluation cases. Do not manufacture tests that assert
  instructional prose.
