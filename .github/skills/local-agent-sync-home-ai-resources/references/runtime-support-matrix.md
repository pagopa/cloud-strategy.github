# Runtime Support Matrix

Use this reference when the selected runtime or resource family decides whether `plan`, `audit`, `doctor`, or `apply` is allowed.

## Summary

| Target | Resource family | Support level | Home path | Direct copy | Translation required | Include in v1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `codex` | Skills | Documented | `~/.codex/skills/<skill>/` | Yes | No | Yes | Direct-copy bundles with `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`. |
| `vscode` | Skills | Documented | `~/.copilot/skills/<skill>/` | Yes | No | Yes | Prefer `~/.copilot/skills` as the canonical VS Code target. |
| `vscode` | Custom agents | Documented | `~/.copilot/agents/*.agent.md` | Yes | No | No | Direct copy is possible, but keep agents out of the current `skills`-only v1 default. |
| `vscode` | Instructions | Documented | `~/.copilot/instructions/**/*.instructions.md` | Yes | No | No | Keep always-on instruction sync out of the current `skills`-only v1 default. |
| `antigravity` | Skills | User-provided / To verify | `~/.gemini/antigravity/skills/<skill>/` | Yes | No | No | User-provided home path exists; keep `apply` experimental until runtime semantics are documented. |

## Default v1 Policy

- Include only `skills` rows with `support_level: Documented`, `direct_copy_possible: true`, and `include_in_v1: true`.
- Treat non-`Documented` rows as `plan`, `audit`, and `doctor` only unless the user explicitly enables an experimental run.
- Keep `vscode` `custom_agents` and `instructions` out of the current `skills`-only v1 `apply`.
