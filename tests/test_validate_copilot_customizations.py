from __future__ import annotations

from contextlib import contextmanager
import importlib.util
from importlib.machinery import SourceFileLoader
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "scripts" / "validate-copilot-customizations.py"


def load_validator_module():
    module_name = "validate_copilot_customizations"
    loader = SourceFileLoader(module_name, str(VALIDATOR_PATH))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@contextmanager
def validator_repo(root: Path):
    original_root = VALIDATOR.REPO_ROOT
    VALIDATOR.REPO_ROOT = root
    try:
        yield
    finally:
        VALIDATOR.REPO_ROOT = original_root


def build_minimal_repo(root: Path, agent_content: str) -> None:
    write_file(
        root / "AGENTS.md",
        """# AGENTS

- Completion-report details live in `.github/copilot-instructions.md`; keep only the bridge pointer here.
""",
    )
    write_file(
        root / ".github" / "copilot-instructions.md",
        """# Copilot Instructions

## Operational routing model
- Source-side sync must keep the canonical mandatory engine skills explicit in the source-side preferred-skills baseline; do not rely on agent bodies alone for the engine layer.

## Operation Completion Report
- After every completed operation, end with a concise completion report.
- If a category was not used, explicitly say so and explain why.

### ✅ Outcome
- Summarize what changed.

### 🤖 Agents
- State which agents were used and why.

### 📘 Instructions
- State which instructions were used and why.

### 🧩 Skills
- State which skills were used and why.
""",
    )
    write_file(root / ".github" / "security-baseline.md", "# Security Baseline\n")
    write_file(
        root / ".github" / "skills" / "internal-example" / "SKILL.md",
        """---
name: internal-example
description: Example skill.
---

# Internal Example
""",
    )
    write_file(
        root / ".github" / "skills" / "internal-code-review" / "SKILL.md",
        """---
name: internal-code-review
description: Example internal code review skill.
---

# Internal Code Review
""",
    )
    for reference_path in VALIDATOR.INTERNAL_CODE_REVIEW_REFERENCE_PATHS:
        write_file(root / reference_path, "# Reference\n")
    write_file(root / ".github" / "agents" / "internal-example.agent.md", agent_content)


def render_internal_agent(
    *,
    name: str,
    mandatory_engine_skills: list[str],
    optional_support_skills: list[str],
    routing_targets: list[str] | None = None,
    boundary_lines: list[str] | None = None,
) -> str:
    mandatory_engine_section = "\n".join(f"- `{skill}`" for skill in mandatory_engine_skills)
    optional_support_section = "\n".join(f"- `{skill}`" for skill in optional_support_skills)
    extra_sections: list[str] = []
    if routing_targets is not None:
        routing_section = "\n".join(
            f"- Route to `{target}` when the handoff belongs there." for target in routing_targets
        )
        extra_sections.append(f"## Escalation / Routing\n\n{routing_section}")
    if boundary_lines is not None:
        boundary_section = "\n".join(f"- {line}" for line in boundary_lines)
        extra_sections.append(f"## Boundary Definition\n\n{boundary_section}")
    extra_body = "\n\n".join(extra_sections)

    return f"""---
name: {name}
description: Use this agent when the repository needs `{name}` behavior.
tools: [\"read\", \"search\", \"execute\", \"web\", \"agent\"]
---

# {name}

## Role

You are the example command center for `{name}`.

## Mandatory Engine Skills

{mandatory_engine_section}

## Optional Support Skills

{optional_support_section}

{extra_body}

## Output Expectations

- Example output
"""


def build_minimal_canonical_operational_repo(
    root: Path,
    *,
    agent_overrides: dict[str, str] | None = None,
) -> None:
    write_file(
        root / "AGENTS.md",
        """# AGENTS

- `internal-router` is the front door.
- Completion-report details live in `.github/copilot-instructions.md`; keep only the bridge pointer here.
""",
    )
    write_file(
        root / ".github" / "copilot-instructions.md",
        """# Copilot Instructions

## Operational routing model
- The canonical repository-owned operational model is `internal-router` as the front door plus four owners.
- Only `internal-router` actively routes or delegates; the other four owners stay boundary-driven.
- Source-side sync must keep the canonical mandatory engine skills explicit in the source-side preferred-skills baseline; do not rely on agent bodies alone for the engine layer.

## Operation Completion Report
- After every completed operation, end with a concise completion report.
- If a category was not used, explicitly say so and explain why.

### ✅ Outcome
- Summarize what changed.

### 🤖 Agents
- State which agents were used and why.

### 📘 Instructions
- State which instructions were used and why.

### 🧩 Skills
- State which skills were used and why.
""",
    )
    write_file(root / ".github" / "security-baseline.md", "# Security Baseline\n")
    write_file(
        root / ".github" / "skills" / "internal-example" / "SKILL.md",
        """---
name: internal-example
description: Example skill.
---

# Internal Example
""",
    )
    write_file(
        root / ".github" / "skills" / "internal-agent-routing-engine" / "SKILL.md",
        """---
name: internal-agent-routing-engine
description: Example routing engine.
---

# Internal Agent Routing Engine
""",
    )
    write_file(
        root / ".github" / "skills" / "internal-agent-operating-model-engine" / "SKILL.md",
        """---
name: internal-agent-operating-model-engine
description: Example operating model engine.
---

# Internal Agent Operating Model Engine
""",
    )
    write_file(
        root / ".github" / "skills" / "internal-code-review" / "SKILL.md",
        """---
name: internal-code-review
description: Example internal code review skill.
---

# Internal Code Review
""",
    )
    for reference_path in VALIDATOR.INTERNAL_CODE_REVIEW_REFERENCE_PATHS:
        write_file(root / reference_path, "# Reference\n")

    agent_contents = {
        "internal-router": render_internal_agent(
            name="internal-router",
            mandatory_engine_skills=["internal-agent-routing-engine"],
            optional_support_skills=["internal-agent-operating-model-engine"],
            routing_targets=[
                "internal-fast-executor",
                "internal-planning-leader",
                "internal-review-guard",
                "internal-critical-challenger",
            ],
        ),
        "internal-fast-executor": render_internal_agent(
            name="internal-fast-executor",
            mandatory_engine_skills=["internal-agent-operating-model-engine"],
            optional_support_skills=["internal-example"],
            boundary_lines=[
                "Stay in this lane while the work remains clear, local, and execution-owned.",
                "If the boundary breaks, recommend `internal-planning-leader`.",
            ],
        ),
        "internal-planning-leader": render_internal_agent(
            name="internal-planning-leader",
            mandatory_engine_skills=["internal-agent-operating-model-engine"],
            optional_support_skills=["internal-example"],
            boundary_lines=[
                "Stay in this lane while ambiguity or repository-owned authoring remains active.",
                "If execution becomes routine and local, recommend `internal-fast-executor`.",
            ],
        ),
        "internal-review-guard": render_internal_agent(
            name="internal-review-guard",
            mandatory_engine_skills=[
                "internal-agent-operating-model-engine",
                "internal-code-review",
            ],
            optional_support_skills=["internal-example"],
            boundary_lines=[
                "Stay in this lane while the work is review-owned and evidence-first.",
                "If design gaps dominate, recommend `internal-planning-leader`.",
                "If weak reasoning dominates, recommend `internal-critical-challenger`.",
            ],
        ),
        "internal-critical-challenger": render_internal_agent(
            name="internal-critical-challenger",
            mandatory_engine_skills=["internal-agent-operating-model-engine"],
            optional_support_skills=["internal-example"],
            boundary_lines=[
                "Stay in this lane while pressure-testing assumptions is the primary need.",
                "If reformulation is needed, recommend `internal-planning-leader`.",
            ],
        ),
    }
    if agent_overrides:
        agent_contents.update(agent_overrides)

    for agent_name, agent_content in agent_contents.items():
        write_file(root / ".github" / "agents" / f"{agent_name}.agent.md", agent_content)


def test_normalize_scope_accepts_root_and_all() -> None:
    assert VALIDATOR.normalize_scope("root") == "root"
    assert VALIDATOR.normalize_scope("all") == "root"


def test_normalize_mode_supports_legacy_alias() -> None:
    assert VALIDATOR.normalize_mode("strict") == "strict"
    assert VALIDATOR.normalize_mode("legacy-compatible") == "basic"


def test_has_standalone_identifier_is_case_insensitive() -> None:
    assert VALIDATOR.has_standalone_identifier(
        "Legacy INTERNAL-ARCHITECT routing.", "internal-architect"
    )


def test_build_report_detects_current_repo_state() -> None:
    report = VALIDATOR.build_report("root", "strict")
    assert isinstance(report.valid, bool)
    assert isinstance(report.errors, list)


def test_extract_frontmatter_apply_to_supports_yaml_lists() -> None:
    text = """---
name: internal-example
applyTo:
  - "**/*.py"
  - "**/*.pyi"
---
"""

    assert VALIDATOR.extract_frontmatter_apply_to(text) == ["**/*.py", "**/*.pyi"]


def test_has_frontmatter_key_supports_yaml_sequence_values() -> None:
    text = """---
name: internal-example
tools:
  - read
  - execute
---
"""

    assert VALIDATOR.has_frontmatter_key(text, "tools")


def test_build_report_accepts_agent_with_preferred_optional_skills(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Preferred/Optional Skills

- `internal-example`

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert report.valid
    assert report.errors == []


def test_build_report_accepts_agent_with_mandatory_engine_and_optional_support(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Mandatory Engine Skills

- `internal-example`

## Optional Support Skills

- `internal-code-review`

## Escalation / Routing

- Escalate when an example stops being an example.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert report.valid
    assert report.errors == []


def test_build_report_accepts_agent_without_skill_guidance_section(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert report.valid
    assert report.errors == []


def test_build_report_accepts_supported_agent_frontmatter(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "edit", "search", "execute"]
model: gpt-5
target: github-copilot
disable-model-invocation: false
user-invocable: true
metadata:
  owner: platform
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert report.valid
    assert report.errors == []


def test_build_report_rejects_internal_agent_without_tools(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Missing required frontmatter key `tools:` in" in "\n".join(report.errors)


def test_build_report_rejects_retired_agent_frontmatter(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
infer: false
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Retired frontmatter key `infer:` found in" in "\n".join(report.errors)


def test_build_report_rejects_unknown_preferred_optional_skill(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Preferred/Optional Skills

- `internal-missing`

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert (
        "Unknown preferred, optional, or support skill `internal-missing` referenced in"
        in "\n".join(report.errors)
    )


def test_build_report_rejects_unknown_mandatory_engine_skill(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Mandatory Engine Skills

- `internal-missing`

## Optional Support Skills

- `internal-example`

## Escalation / Routing

- Escalate when needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert (
        "Unknown mandatory engine skill `internal-missing` referenced in"
        in "\n".join(report.errors)
    )


def test_build_report_rejects_skill_duplicated_between_mandatory_and_optional_sections(
    tmp_path: Path,
) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Mandatory Engine Skills

- `internal-example`

## Optional Support Skills

- `internal-example`

## Escalation / Routing

- Escalate when needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert (
        "Skill `internal-example` cannot appear in both mandatory and optional sections"
        in "\n".join(report.errors)
    )


def test_build_report_rejects_missing_operation_completion_report_contract(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )
    write_file(tmp_path / ".github" / "copilot-instructions.md", "# Copilot Instructions\n")

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Missing `## Operation Completion Report` in" in "\n".join(report.errors)


def test_build_report_rejects_missing_agents_completion_report_pointer(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )
    write_file(tmp_path / "AGENTS.md", "# AGENTS\n")

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Missing completion-report bridge pointer in" in "\n".join(report.errors)


def test_build_report_rejects_sync_agent_without_completion_report_categories(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: ["read", "search", "execute", "web", "agent"]
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )
    write_file(
        tmp_path / ".github" / "agents" / "internal-sync-global-copilot-configs-into-repo.agent.md",
        """---
name: internal-sync-global-copilot-configs-into-repo
description: Use this agent when syncing a shared Copilot catalog into a consumer repository.
tools: ["read", "edit", "search", "execute"]
---

# Sync Agent

## Output Expectations

- Target analysis
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    joined_errors = "\n".join(report.errors)
    assert (
        "Missing completion report category `### ✅ Outcome` in "
        ".github/agents/internal-sync-global-copilot-configs-into-repo.agent.md"
    ) in joined_errors


def test_build_report_rejects_repo_profile_reference_missing_on_disk(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
tools: [\"read\", \"search\", \"execute\", \"web\", \"agent\"]
---

# Internal Example

## Role

You are the example command center.

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )
    write_file(
        tmp_path / ".github" / "repo-profiles.yml",
        """version: 1

profiles:
  minimal:
    description: Example profile.
    recommended_skills:
      - skills/internal-missing/SKILL.md
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert (
        "Repo profile path missing on disk: .github/skills/internal-missing/SKILL.md"
        in "\n".join(report.errors)
    )


def test_build_report_rejects_routing_section_in_non_router_canonical_agent(
    tmp_path: Path,
) -> None:
    build_minimal_canonical_operational_repo(
        tmp_path,
        agent_overrides={
            "internal-fast-executor": render_internal_agent(
                name="internal-fast-executor",
                mandatory_engine_skills=["internal-agent-operating-model-engine"],
                optional_support_skills=["internal-example"],
                routing_targets=["internal-example"],
            )
        },
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert (
        "Only `internal-router` may publish `## Escalation / Routing`"
        in "\n".join(report.errors)
    )


def test_build_report_rejects_self_route_in_router_agent(tmp_path: Path) -> None:
    build_minimal_canonical_operational_repo(
        tmp_path,
        agent_overrides={
            "internal-router": render_internal_agent(
                name="internal-router",
                mandatory_engine_skills=["internal-agent-routing-engine"],
                optional_support_skills=["internal-agent-operating-model-engine"],
                routing_targets=["internal-router"],
            )
        },
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Self-route `internal-router` found in" in "\n".join(report.errors)


def test_build_report_rejects_missing_boundary_definition_in_non_router_canonical_agent(
    tmp_path: Path,
) -> None:
    build_minimal_canonical_operational_repo(
        tmp_path,
        agent_overrides={
            "internal-fast-executor": render_internal_agent(
                name="internal-fast-executor",
                mandatory_engine_skills=["internal-agent-operating-model-engine"],
                optional_support_skills=["internal-example"],
            )
        },
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Missing `## Boundary Definition` in" in "\n".join(report.errors)


def test_build_report_requires_router_routing_targets(tmp_path: Path) -> None:
    build_minimal_canonical_operational_repo(
        tmp_path,
        agent_overrides={
            "internal-router": render_internal_agent(
                name="internal-router",
                mandatory_engine_skills=["internal-agent-routing-engine"],
                optional_support_skills=["internal-agent-operating-model-engine"],
                routing_targets=[],
            )
        },
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Missing canonical routing target references in" in "\n".join(report.errors)


def test_build_report_rejects_case_insensitive_retired_operational_reference(
    tmp_path: Path,
) -> None:
    build_minimal_canonical_operational_repo(tmp_path)
    write_file(
        tmp_path / ".github" / "skills" / "internal-example" / "notes.md",
        "Legacy INTERNAL-ARCHITECT reference.\n",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert (
        "Stale retired operational agent reference `internal-architect` found in "
        ".github/skills/internal-example/notes.md"
    ) in "\n".join(report.errors)
