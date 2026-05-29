"""Tests for agent_translation module."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_translation import (  # noqa: E402
    _build_claude_tools,
    _build_opencode_permission,
    _render_handoffs_body,
    _translate_for_claude,
    _translate_for_copilot,
    _translate_for_opencode,
    parse_frontmatter_and_body,
    render_frontmatter_md,
    target_extension,
    translate_agent_for_target,
)


class TestParseFrontmatter:
    def test_basic_parse(self):
        content = "---\nname: test-agent\ntools: [read]\n---\nBody content here\n"
        fm, body = parse_frontmatter_and_body(content)
        assert fm["name"] == "test-agent"
        assert fm["tools"] == ["read"]
        assert body == "Body content here\n"

    def test_no_frontmatter_raises(self):
        with pytest.raises(ValueError, match="no valid YAML frontmatter"):
            parse_frontmatter_and_body("Just markdown, no frontmatter")

    def test_empty_frontmatter(self):
        content = "---\n\n---\nBody\n"
        fm, body = parse_frontmatter_and_body(content)
        assert fm == {}
        assert body == "Body\n"


class TestRenderFrontmatter:
    def test_render_simple(self):
        result = render_frontmatter_md({"name": "test", "tools": "Read"})
        assert result.startswith("---\n")
        assert result.endswith("---\n")
        assert "name: test" in result
        assert "tools: Read" in result


class TestClaudeTranslation:
    def test_claude_tools_basic(self):
        fm = {"tools": ["read", "edit"]}
        tools = _build_claude_tools(fm)
        assert "Read" in tools
        assert "Edit" in tools

    def test_claude_tools_search_maps_to_glob_grep(self):
        fm = {"tools": ["search"]}
        tools = _build_claude_tools(fm)
        assert "Glob" in tools
        assert "Grep" in tools

    def test_claude_tools_execute_maps_to_bash(self):
        fm = {"tools": ["execute"]}
        tools = _build_claude_tools(fm)
        assert "Bash" in tools

    def test_claude_tools_web_maps(self):
        fm = {"tools": ["web"]}
        tools = _build_claude_tools(fm)
        assert "WebSearch" in tools
        assert "WebFetch" in tools

    def test_claude_agents_added(self):
        fm = {"tools": ["read"], "agents": ["agent1", "agent2"]}
        tools = _build_claude_tools(fm)
        assert tools.startswith("Agent(agent1, agent2)")

    def test_claude_full_translation(self):
        fm = {
            "name": "my-agent",
            "description": "Test agent",
            "tools": ["read", "execute"],
            "handoffs": [
                {"label": "Next", "agent": "other-agent", "prompt": "Do something"}
            ],
        }
        body = "# My Agent\n\nInstructions here.\n"
        result = _translate_for_claude(fm, body)
        # Verify YAML is valid
        parsed = yaml.safe_load(result.split("---\n", 2)[1])
        assert parsed["name"] == "my-agent"
        assert parsed["tools"] == "Read, Bash"
        assert "Handoffs" in result
        assert "other-agent" in result

    def test_claude_no_tools_field(self):
        fm = {"name": "minimal"}
        body = "Just body.\n"
        result = _translate_for_claude(fm, body)
        parsed = yaml.safe_load(result.split("---\n", 2)[1])
        assert parsed["name"] == "minimal"
        assert "tools" not in parsed


class TestOpenCodeTranslation:
    def test_opencode_permission_basic(self):
        fm = {"tools": ["read", "edit"]}
        perm = _build_opencode_permission(fm)
        assert perm["read"] == "allow"
        assert perm["edit"] == "allow"

    def test_opencode_disable_model_invocation(self):
        fm = {"tools": ["read"], "disable-model-invocation": True}
        body = "Body.\n"
        result = _translate_for_opencode(fm, body)
        assert "hidden: true" in result

    def test_opencode_agents_permission(self):
        fm = {"agents": ["agent1"]}
        perm = _build_opencode_permission(fm)
        assert "task" in perm
        assert perm["task"]["*"] == "deny"
        assert perm["task"]["agent1"] == "allow"

    def test_opencode_full_translation(self):
        fm = {
            "description": "Test agent",
            "tools": ["read", "web"],
            "handoffs": [
                {"label": "Switch", "agent": "other", "prompt": "Handle this"}
            ],
        }
        body = "# Test\n\nContent.\n"
        result = _translate_for_opencode(fm, body)
        parsed = yaml.safe_load(result.split("---\n", 2)[1])
        assert parsed["description"] == "Test agent"
        assert parsed["mode"] == "subagent"
        assert parsed["permission"]["read"] == "allow"
        assert "webfetch" in parsed["permission"]
        assert "websearch" in parsed["permission"]
        assert "Handoffs" in result

    def test_opencode_no_name_in_frontmatter(self):
        fm = {"description": "Just desc"}
        body = "Body.\n"
        result = _translate_for_opencode(fm, body)
        parsed = yaml.safe_load(result.split("---\n", 2)[1])
        assert "name" not in parsed


class TestHandoffsBody:
    def test_empty_handoffs(self):
        assert _render_handoffs_body({}) == ""

    def test_no_handoffs_field(self):
        fm = {"name": "test"}
        assert _render_handoffs_body(fm) == ""

    def test_handoffs_rendered(self):
        fm = {
            "handoffs": [
                {"label": "Go to X", "agent": "agent-x", "prompt": "Do X task"}
            ]
        }
        result = _render_handoffs_body(fm)
        assert "## Handoffs" in result
        assert "**Go to X**" in result
        assert "`agent-x`" in result
        assert "Do X task" in result


class TestCopilotTranslation:
    def test_copilot_passthrough(self):
        fm = {"name": "test", "tools": ["read"]}
        body = "Body here.\n"
        result = _translate_for_copilot(fm, body)
        assert "name: test" in result
        assert "Body here." in result
        assert "tools:" in result


class TestTargetExtension:
    def test_extensions(self):
        assert target_extension("copilot") == ".agent.md"
        assert target_extension("claude") == ".md"
        assert target_extension("opencode") == ".md"
        assert target_extension("codex") == ".toml"


class TestCodexTranslation:
    def test_codex_basic(self):
        fm = {
            "name": "test-agent",
            "description": "A test agent",
        }
        body = "Instructions here.\n"
        from agent_translation import _translate_for_codex
        result = _translate_for_codex(fm, body)
        assert "name" in result
        assert "test-agent" in result
        assert "developer_instructions" in result

    def test_codex_handoffs_in_instructions(self):
        fm = {
            "name": "test",
            "handoffs": [
                {"label": "Go", "agent": "other", "prompt": "Do task"}
            ],
        }
        body = "Main body.\n"
        from agent_translation import _translate_for_codex
        result = _translate_for_codex(fm, body)
        assert "Handoffs" in result
        assert "other" in result

    def test_codex_omit_tools_from_frontmatter(self):
        fm = {"name": "minimal"}
        body = "Body.\n"
        from agent_translation import _translate_for_codex
        result = _translate_for_codex(fm, body)
        assert "name = " in result

    def test_codex_real_file(self):
        source = Path(".github/agents/internal-gateway-operational-flow.agent.md")
        if not source.exists():
            pytest.skip("Source file not available")
        result = translate_agent_for_target(source, "codex")
        assert "name = " in result
        assert "developer_instructions" in result
        assert "internal-gateway-operational-flow" in result


class TestIntegrationWithRealFiles:
    def test_operational_flow_to_claude(self):
        source = Path(".github/agents/internal-gateway-operational-flow.agent.md")
        if not source.exists():
            pytest.skip("Source file not available")
        result = translate_agent_for_target(source, "claude")
        fm, body = parse_frontmatter_and_body(result)
        assert fm["name"] == "internal-gateway-operational-flow"
        assert "Handoffs" in body

    def test_operational_flow_to_opencode(self):
        source = Path(".github/agents/internal-gateway-operational-flow.agent.md")
        if not source.exists():
            pytest.skip("Source file not available")
        result = translate_agent_for_target(source, "opencode")
        fm, body = parse_frontmatter_and_body(result)
        assert fm["mode"] == "subagent"
        assert "hidden" in fm
        assert "Handoffs" in body

    def test_critical_master_to_claude(self):
        source = Path(".github/agents/internal-gateway-critical-master.agent.md")
        if not source.exists():
            pytest.skip("Source file not available")
        result = translate_agent_for_target(source, "claude")
        fm, body = parse_frontmatter_and_body(result)
        assert fm["name"] == "internal-gateway-critical-master"
        assert "Glob" in fm["tools"]
        assert "Grep" in fm["tools"]

    def test_critical_master_to_opencode(self):
        source = Path(".github/agents/internal-gateway-critical-master.agent.md")
        if not source.exists():
            pytest.skip("Source file not available")
        result = translate_agent_for_target(source, "opencode")
        fm, body = parse_frontmatter_and_body(result)
        assert fm["permission"]["read"] == "allow"
        # critical-master has no edit/execute/web tools
        assert "edit" not in fm["permission"]

    def test_all_copilot_passthrough(self):
        source = Path(".github/agents/internal-gateway-simple-task.agent.md")
        if not source.exists():
            pytest.skip("Source file not available")
        original = source.read_text()
        result = translate_agent_for_target(source, "copilot")
        fm_orig, body_orig = parse_frontmatter_and_body(original)
        fm_result, body_result = parse_frontmatter_and_body(result)
        assert fm_result["name"] == fm_orig["name"]
        assert body_result.strip() == body_orig.strip()
