# Doctor Checks

Use this checklist when `doctor` needs to explain readiness before a local home sync.

## Common Checks

- Confirm the selected runtime targets are known.
- Confirm the runtime support matrix is readable and current.
- Confirm the allowlist catalog exists and only references repository skill bundle paths.
- Confirm the state root under `~/.sync/cloud-strategy-governance/home-ai-resources/` is readable and writable.
- Confirm the manifest is either absent for a first run or parseable for later runs.
- Confirm every resolved target path stays under the expected home root.
- Confirm no disallowed symlink escape exists in the selected target tree.

## Codex Checks

- Confirm `~/.codex/skills` exists or can be created safely.
- Confirm allowlisted skill bundles contain `SKILL.md`.
- Confirm bundle-relative `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` paths stay self-contained.

## VS Code Checks

- Confirm `~/.copilot/skills` exists or can be created safely.
- Confirm `~/.copilot/agents` and `~/.copilot/instructions` are recognized only as non-v1 resource roots for the current `skills`-only apply flow.
- Confirm no non-v1 `agents` or `instructions` materialization is included in a `skills`-only apply run.

## Antigravity Checks

- Confirm `~/.gemini/antigravity/skills` resolves inside the user home directory.
- Confirm the run is `plan`, `audit`, or `doctor`, unless an explicit experimental override is present.
- Confirm the matrix still marks the runtime as undocumented before blocking `apply`.
