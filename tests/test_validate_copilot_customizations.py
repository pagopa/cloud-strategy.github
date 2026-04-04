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


def test_normalize_scope_accepts_root_and_all() -> None:
    assert VALIDATOR.normalize_scope("root") == "root"
    assert VALIDATOR.normalize_scope("all") == "root"


def test_normalize_mode_supports_legacy_alias() -> None:
    assert VALIDATOR.normalize_mode("strict") == "strict"
    assert VALIDATOR.normalize_mode("legacy-compatible") == "basic"


def test_build_report_detects_current_repo_state() -> None:
    report = VALIDATOR.build_report("root", "strict")
    assert isinstance(report.valid, bool)
    assert isinstance(report.errors, list)


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
        "Unknown preferred or optional skill `internal-missing` referenced in"
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
