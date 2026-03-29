from __future__ import annotations

from contextlib import contextmanager
import importlib.util
from importlib.machinery import SourceFileLoader
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / ".github" / "scripts" / "validate-copilot-customizations.sh"


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
    write_file(root / "AGENTS.md", "# AGENTS\n")
    write_file(root / ".github" / "copilot-instructions.md", "# Copilot Instructions\n")
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


def test_build_report_accepts_agent_with_declared_skills(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
---

# Internal Example

## Role

You are the example command center.

## Declared Skills

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


def test_build_report_rejects_agent_without_declared_skills_section(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
---

# Internal Example

## Role

You are the example command center.

## Primary Skill Stack

- `internal-example`

## Routing Rules

- Use this agent when an example is needed.

## Output Expectations

- Example output
""",
    )

    with validator_repo(tmp_path):
        report = VALIDATOR.build_report("root", "strict")

    assert not report.valid
    assert "Deprecated agent section `## Primary Skill Stack` found in" in "\n".join(report.errors)
    assert "Missing `## Declared Skills` section:" in "\n".join(report.errors)


def test_build_report_rejects_unknown_declared_skill(tmp_path: Path) -> None:
    build_minimal_repo(
        tmp_path,
        """---
name: internal-example
description: Use this agent when the repository needs an example command center.
---

# Internal Example

## Role

You are the example command center.

## Declared Skills

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
    assert "Unknown declared skill `internal-missing` referenced in" in "\n".join(report.errors)
