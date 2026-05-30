"""Agent translation module for converting .agent.md to target-specific formats.

Translates Copilot-native .agent.md files into Claude, OpenCode, and Codex
agent definitions while preserving the original body content and translating
frontmatter fields appropriately.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

_TOOL_MAP_CLAUDE = {
    "read": "Read",
    "edit": "Edit",
    "search": "Glob, Grep",
    "execute": "Bash",
    "web": "WebSearch, WebFetch",
}

_PERMISSION_MAP_OPENCODE = {
    "read": "read",
    "edit": "edit",
    "search": ["grep", "glob"],
    "execute": "bash",
    "web": ["webfetch", "websearch"],
}

_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter_and_body(content: str) -> tuple[dict, str]:
    m = _FRONTMATTER_PATTERN.match(content)
    if not m:
        raise ValueError("Source file has no valid YAML frontmatter")
    frontmatter = yaml.safe_load(m.group(1)) or {}
    body = content[m.end() :]
    return frontmatter, body


def render_frontmatter_md(frontmatter: dict) -> str:
    return "---\n" + yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip() + "\n---\n"


def load_agent_config(config_path: Path | None) -> dict:
    if config_path is None or not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def merge_config(frontmatter: dict, config: dict, target: str) -> dict:
    target_overrides = config.get(target, {})
    if not isinstance(target_overrides, dict):
        return dict(frontmatter)
    merged = dict(frontmatter)
    merged.update(target_overrides)
    return merged


def translate_agent_for_target(
    source_path: Path,
    target: str,
    config_path: Path | None = None,
) -> str:
    content = source_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter_and_body(content)
    config = load_agent_config(config_path)
    frontmatter = merge_config(frontmatter, config, target)

    if target == "copilot":
        return _translate_for_copilot(frontmatter, body)
    elif target == "claude":
        return _translate_for_claude(frontmatter, body)
    elif target == "opencode":
        return _translate_for_opencode(frontmatter, body)
    elif target == "codex":
        return _translate_for_codex(frontmatter, body)
    raise ValueError(f"Unknown target: {target}")


def target_extension(target: str) -> str:
    if target == "copilot":
        return ".agent.md"
    elif target == "codex":
        return ".toml"
    return ".md"


def _translate_for_copilot(frontmatter: dict, body: str) -> str:
    return render_frontmatter_md(frontmatter) + body


def _translate_for_claude(frontmatter: dict, body: str) -> str:
    claude_fm: dict[str, object] = {}
    if "name" in frontmatter:
        claude_fm["name"] = frontmatter["name"]
    if "description" in frontmatter:
        claude_fm["description"] = frontmatter["description"]

    tools_list = _build_claude_tools(frontmatter)
    if tools_list:
        claude_fm["tools"] = tools_list

    output = render_frontmatter_md(claude_fm)
    output += body.rstrip() + "\n"

    handoffs_body = _render_handoffs_body(frontmatter)
    if handoffs_body:
        output += "\n" + handoffs_body + "\n"

    return output


def _build_claude_tools(frontmatter: dict) -> str:
    parts: list[str] = []

    agents = frontmatter.get("agents") or []
    if isinstance(agents, list) and agents:
        agent_names = ", ".join(agents)
        parts.append(f"Agent({agent_names})")

    tools = frontmatter.get("tools") or []
    if isinstance(tools, list):
        for tool in tools:
            mapped = _TOOL_MAP_CLAUDE.get(tool)
            if mapped:
                for t in mapped.split(", "):
                    if t not in parts:
                        parts.append(t)

    return ", ".join(parts)


def _render_handoffs_body(frontmatter: dict) -> str:
    handoffs = frontmatter.get("handoffs") or []
    if not isinstance(handoffs, list) or not handoffs:
        return ""

    lines = ["## Handoffs"]
    for h in handoffs:
        if not isinstance(h, dict):
            continue
        label = h.get("label", "")
        agent = h.get("agent", "")
        prompt = h.get("prompt", "")
        lines.append(f"- **{label}** → `{agent}`")
        if prompt:
            lines.append(f"  {prompt}")
    return "\n".join(lines)


def _translate_for_opencode(frontmatter: dict, body: str) -> str:
    opencode_fm: dict[str, object] = {}

    if "description" in frontmatter:
        opencode_fm["description"] = frontmatter["description"]

    opencode_fm["mode"] = "subagent"

    permission: dict[str, object] = _build_opencode_permission(frontmatter)
    if permission:
        opencode_fm["permission"] = permission

    if frontmatter.get("disable-model-invocation"):
        opencode_fm["hidden"] = True

    output = render_frontmatter_md(opencode_fm)
    output += body.rstrip() + "\n"

    handoffs_body = _render_handoffs_body(frontmatter)
    if handoffs_body:
        output += "\n" + handoffs_body + "\n"

    return output


def _build_opencode_permission(frontmatter: dict) -> dict[str, object]:
    permission: dict[str, object] = {}

    tools = frontmatter.get("tools") or []
    if isinstance(tools, list):
        for tool in tools:
            mapped = _PERMISSION_MAP_OPENCODE.get(tool)
            if mapped:
                if isinstance(mapped, list):
                    for m in mapped:
                        permission[m] = "allow"
                else:
                    permission[mapped] = "allow"

    agents = frontmatter.get("agents") or []
    if isinstance(agents, list) and agents:
        task_rules: dict[str, str] = {"*": "deny"}
        for agent in agents:
            task_rules[agent] = "allow"
        permission["task"] = task_rules

    return permission


def _translate_for_codex(frontmatter: dict, body: str) -> str:
    try:
        import tomli_w
    except ImportError:
        raise ImportError(
            "tomli_w is required for Codex TOML translation. "
            "Install it with: pip install tomli_w"
        )

    toml_data: dict[str, object] = {}

    if "name" in frontmatter:
        toml_data["name"] = frontmatter["name"]
    if "description" in frontmatter:
        toml_data["description"] = frontmatter["description"]

    instructions = body.strip()
    handoffs_text = _render_handoffs_instructions(frontmatter)
    if handoffs_text:
        instructions += "\n\n" + handoffs_text

    toml_data["developer_instructions"] = instructions

    return tomli_w.dumps(toml_data)


def _render_handoffs_instructions(frontmatter: dict) -> str:
    handoffs = frontmatter.get("handoffs") or []
    if not isinstance(handoffs, list) or not handoffs:
        return ""

    lines = ["## Handoffs"]
    for h in handoffs:
        if not isinstance(h, dict):
            continue
        label = h.get("label", "")
        agent = h.get("agent", "")
        prompt = h.get("prompt", "")
        lines.append(f"- **{label}**: Delegate to `{agent}`. {prompt}")

    return "\n".join(lines)
