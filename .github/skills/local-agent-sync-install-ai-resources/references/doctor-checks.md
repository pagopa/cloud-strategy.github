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

- Confirm `~/.agents/skills` exists or can be created safely.
- Confirm `~/.codex/agents` exists or can be created safely.
- Confirm allowlisted skill bundles contain `SKILL.md`.
- Confirm allowlisted agent source files are valid `.agent.md` files.
- Confirm bundle-relative `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` paths stay self-contained.

## Copilot Checks

- Confirm `~/.agents/skills` exists or can be created safely.
- Confirm `~/.copilot/agents` exists or can be created safely.
- Confirm allowlisted skill bundles contain `SKILL.md`.
- Confirm allowlisted agent source files are valid `.agent.md` files.
- Confirm bundle-relative paths stay self-contained.

## Claude Checks

- Confirm `~/.agents/skills` exists or can be created safely.
- Confirm `~/.claude/agents` exists or can be created safely.
- Confirm allowlisted skill bundles contain `SKILL.md`.
- Confirm allowlisted agent source files are valid `.agent.md` files.
- Confirm bundle-relative paths stay self-contained.

## OpenCode Checks

- Confirm `~/.agents/skills` exists or can be created safely.
- Confirm `~/.config/opencode/agents` exists or can be created safely.
- Confirm allowlisted skill bundles contain `SKILL.md`.
- Confirm allowlisted agent source files are valid `.agent.md` files.
- Confirm bundle-relative paths stay self-contained.
