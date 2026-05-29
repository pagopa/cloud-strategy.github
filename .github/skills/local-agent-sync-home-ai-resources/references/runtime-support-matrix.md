# Runtime Support Matrix

Use this reference when the selected runtime or resource family decides whether `plan`, `audit`, `doctor`, or `apply` is allowed.

## Summary

| Target | Resource family | Support level | Home path | Direct copy | Translation required | Include in v1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `codex` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | Direct-copy bundles with `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`. |
| `copilot` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | GitHub Copilot supports Agent Skills standard via `~/.agents/skills/`. |
| `claude` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | Claude Code supports Agent Skills standard via `~/.agents/skills/` (compatibility path). |
| `opencode` | Skills | Documented | `~/.agents/skills/<skill>/` | Yes | No | Yes | OpenCode supports Agent Skills standard via `~/.agents/skills/`. |

## Default v1 Policy

- Include only `skills` rows with `support_level: Documented`, `direct_copy_possible: true`, and `include_in_v1: true`.
- Treat non-`Documented` rows as `plan`, `audit`, and `doctor` only unless the user explicitly enables an experimental run.
