# Runtime Support Matrix

Use this reference when the selected runtime or resource family decides whether `plan`, `audit`, `doctor`, or `apply` is allowed.

## Summary

| Target | Resource family | Support level | Home path | Direct copy | Translation required | Include in v1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `codex` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | Direct-copy bundles with `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`. |
| `copilot` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | GitHub Copilot supports Agent Skills standard via `~/.agents/skills/`. |
| `opencode` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | OpenCode supports Agent Skills standard via `~/.agents/skills/`. |
| `codex` | Agents | Documented | `~/.codex/agents/` | No | Yes | Yes | Requires MD to TOML translation. |
| `copilot` | Agents | Documented | `~/.copilot/agents/` | Yes | No | Yes | Direct copy of `.agent.md` files. |
| `opencode` | Agents | Documented | `~/.config/opencode/agents/` | No | Yes | Yes | Requires frontmatter translation (permission object, handoffs to body). |

## Default v1 Policy

- Include only `skills` rows with `support_level: Documented`, `direct_copy_possible: true`, and `include_in_v1: true`.
- Include `agents` rows with `support_level: Documented` and `include_in_v1: true`. For targets where `direct_copy_possible: false` and `translation_required: true`, the sync plan delegates to the agent translation module (`scripts/agent_translation.py`).
- Treat non-`Documented` rows as `plan`, `audit`, and `doctor` only unless the user explicitly enables an experimental run.
