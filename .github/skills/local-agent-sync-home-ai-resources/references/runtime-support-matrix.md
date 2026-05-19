# Runtime Support Matrix

Use this reference when the selected runtime or resource family decides whether `plan`, `audit`, `doctor`, or `apply` is allowed.

## Summary

| Target | Resource family | Support level | Home path | Direct copy | Translation required | Include in v1 | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `codex` | Skills | Documented | `~/.codex/skills/<skill>/` | Yes | No | Yes | Direct-copy bundles with `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`. |
| `codex` | Global instructions | Documented | `~/.codex/AGENTS.md` | Yes | Policy decision | No | Repository `AGENTS.md` stays a workspace bridge, not a default personal sync target. |
| `codex` | Global override | Documented | `~/.codex/AGENTS.override.md` | Yes | Policy decision | No | Keep overrides out of v1 home sync. |
| `codex` | User config | Documented | `~/.codex/config.toml` | No | Yes | No | Personal machine state is out of scope for v1. |
| `codex` | Custom agents | Documented | `~/.codex/agents/*.toml` | No | Yes | No | `.agent.md` requires a TOML adapter and config wiring. |
| `codex` | VS Code `.agent.md` | Not directly supported | None | No | Yes | No | Do not copy `.github/agents/*.agent.md` to Codex. |
| `codex` | VS Code `.instructions.md` | Not supported as such | None | No | Yes | No | No verified direct Codex home-level equivalent. |
| `codex` | Prompt files | Unknown / To verify | None verified | No | Unknown | No | Exclude until user-level prompt support is documented. |
| `vscode` | Skills | Documented | `~/.copilot/skills/<skill>/` | Yes | No | Yes | Prefer `~/.copilot/skills` as the canonical VS Code target. |
| `vscode` | Custom agents | Documented | `~/.copilot/agents/*.agent.md` | Yes | No | No | Direct copy is possible, but keep agents out of the v1 default. |
| `vscode` | Instructions | Documented | `~/.copilot/instructions/**/*.instructions.md` | Yes | No | No | Keep always-on instruction sync out of v1 unless separately approved. |
| `vscode` | Prompt files | Documented but path not stable | VS Code user data profile | Yes | No | No | Defer because the stable filesystem target is not documented like `~/.copilot/*`. |
| `vscode` | `.github/copilot-instructions.md` | Workspace-only | Workspace `.github/copilot-instructions.md` | No | No | No | Do not treat workspace guidance as a home-level resource. |
| `vscode` | `AGENTS.md` | Workspace convention | Workspace root | No | Policy decision | No | Do not promote repository `AGENTS.md` to home-level VS Code guidance. |
| `antigravity` | Skills | User-provided / To verify | `~/.gemini/antigravity/skills/<skill>/` | Yes | No | No | User-provided home path exists; keep `apply` experimental until runtime semantics are documented. |
| `antigravity` | Global rules | Unknown / To verify | `~/.gemini/GEMINI.md` or `~/.gemini/antigravity/GEMINI.md` | Unknown | Policy decision | No | Do not sync without official precedence docs. |
| `antigravity` | MCP config | Unknown / To verify | `~/.gemini/antigravity/mcp_config.json` | No | Config merge | No | Out of scope and likely sensitive. |
| `antigravity` | Project-local resources | Unknown / To verify | None verified | No | Unknown | No | Workspace-local resource paths are out of scope for home sync. |
| `antigravity` | Agents | Unknown | Unknown | No | Unknown | No | Do not assume compatibility. |
| `antigravity` | Instructions | Unknown | Unknown | No | Unknown | No | Do not assume compatibility. |
| `antigravity` | Prompt files | Unknown | Unknown | No | Unknown | No | Do not include without official support evidence. |

## Default v1 Policy

- Include only `skills` rows with `support_level: Documented`, `direct_copy_possible: true`, and `include_in_v1: true`.
- Treat non-`Documented` rows as `plan`, `audit`, and `doctor` only unless the user explicitly enables an experimental run.
- Keep any translation-required row out of v1 `apply`.
