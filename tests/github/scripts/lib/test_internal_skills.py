from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_ROOT = (
    next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
    )
    / ".github/scripts"
)
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from lib.internal_skills import (  # noqa: E402
    detect_internal_skill_findings,
    detect_skill_prose_assertion_findings,
)


def write_test_repository(tmp_path: Path, test_source: str) -> Path:
    root = tmp_path / "repo"
    skill = root / ".github/skills/internal-example"
    (skill / "agents").mkdir(parents=True)
    (skill / "references").mkdir()
    (root / "tests").mkdir()
    (root / "AGENTS.md").write_text("# Test repository\n", encoding="utf-8")
    (skill / "SKILL.md").write_text(
        """---
name: internal-example
description: Use when exercising validator fixtures.
---

# Internal Example

## When to use

- Validator fixtures.
""",
        encoding="utf-8",
    )
    (skill / "agents/openai.yaml").write_text(
        """interface:
  display_name: Internal Example
  short_description: Internal example validator fixture
  default_prompt: Use /internal-example for this fixture.
""",
        encoding="utf-8",
    )
    (root / "tests/test_contract.py").write_text(test_source, encoding="utf-8")
    return root


def test_direct_skill_wording_assertion_is_blocking(tmp_path: Path) -> None:
    root = write_test_repository(
        tmp_path,
        """
from pathlib import Path
SKILL = Path(".github/skills/internal-example/SKILL.md")
text = SKILL.read_text()

def test_contract():
    assert "required wording" in text
""",
    )

    findings = detect_skill_prose_assertion_findings(root)

    assert [finding.code for finding in findings] == ["skill-prose-lexical-assertion"]
    assert findings[0].severity == "blocking"
    assert findings[0].path.endswith("tests/test_contract.py:7")


def test_lexical_predicates_on_skill_text_are_blocking(tmp_path: Path) -> None:
    predicates = (
        'assert "wording" not in text',
        'assert text == "wording"',
        'assert text.find("wording") >= 0',
        'assert text.startswith("wording")',
        'assert text.endswith("wording")',
        "assert any(marker in text for marker in markers)",
    )

    for index, predicate in enumerate(predicates):
        root = write_test_repository(
            tmp_path / str(index),
            f"""\nfrom pathlib import Path\nSKILL = Path(".github/skills/internal-example/SKILL.md")\ntext = SKILL.read_text()\nmarkers = ["wording"]\n\ndef test_contract():\n    {predicate}\n""",
        )

        findings = detect_skill_prose_assertion_findings(root)

        assert len(findings) == 1
        assert findings[0].code == "skill-prose-lexical-assertion"


def test_normalized_text_and_helper_return_are_tainted(tmp_path: Path) -> None:
    root = write_test_repository(
        tmp_path,
        """
from pathlib import Path
SKILL = Path(".github/skills/internal-example/SKILL.md")

def read_skill():
    return SKILL.read_text().lower()

text = read_skill()

def test_contract():
    assert "required wording" in text
""",
    )

    findings = detect_skill_prose_assertion_findings(root)

    assert len(findings) == 1
    assert findings[0].code == "skill-prose-lexical-assertion"


def test_other_skill_sources_and_contract_text_are_tainted(tmp_path: Path) -> None:
    sources = (
        ".github/skills/internal-example/agents/openai.yaml",
        ".github/skills/internal-example/references/example.md",
        "INTERNAL_CONTRACT.md",
    )

    for index, source in enumerate(sources):
        root = write_test_repository(
            tmp_path / str(index),
            f'''\nfrom pathlib import Path\nSOURCE = Path("{source}")\ntext = SOURCE.read_text()\n\ndef test_contract():\n    assert "required wording" in text\n''',
        )

        findings = detect_skill_prose_assertion_findings(root)

        assert len(findings) == 1
        assert findings[0].code == "skill-prose-lexical-assertion"


def test_parsed_frontmatter_assertion_is_allowed(tmp_path: Path) -> None:
    root = write_test_repository(
        tmp_path,
        """
from pathlib import Path
import yaml
SKILL = Path(".github/skills/internal-example/SKILL.md")

def test_metadata():
    raw = SKILL.read_text()
    metadata = yaml.safe_load(raw.split("---", 2)[1])
    assert metadata["name"] == "internal-example"
""",
    )

    assert detect_skill_prose_assertion_findings(root) == []


def test_executable_and_protocol_boundaries_are_allowed(tmp_path: Path) -> None:
    root = write_test_repository(
        tmp_path,
        """
from pathlib import Path
from lib.internal_skills import detect_internal_skill_findings

def test_validator():
    assert not detect_internal_skill_findings(Path("."))

def test_transformation(tmp_path):
    output = tmp_path / "output.txt"
    output.write_text("required wording")
    assert output.read_text() == "required wording"
""",
    )

    assert detect_skill_prose_assertion_findings(root) == []


def test_unknown_slash_invocation_is_blocking(tmp_path: Path) -> None:
    root = write_test_repository(
        tmp_path,
        "def test_fixture_module_imports():\n    assert True\n",
    )
    skill = root / ".github/skills/internal-example/SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8")
        + "\nLoad `/internal-missing` before execution.\n",
        encoding="utf-8",
    )

    findings = detect_internal_skill_findings(root)

    assert "unknown-skill-invocation" in {finding.code for finding in findings}


def test_disabled_slash_invocation_is_blocking(tmp_path: Path) -> None:
    root = write_test_repository(tmp_path, "def test_fixture():\n    assert True\n")
    target = root / ".github/skills/internal-disabled"
    (target / "agents").mkdir(parents=True)
    (target / "SKILL.md").write_text(
        """---
name: internal-disabled
description: Use when this fixture is selected.
disable-model-invocation: true
---

## When to use

- Fixture.
""",
        encoding="utf-8",
    )
    (target / "agents/openai.yaml").write_text(
        """interface:
  display_name: Internal Disabled
  short_description: Internal disabled fixture
  default_prompt: Use /internal-disabled for this fixture.
""",
        encoding="utf-8",
    )
    skill = root / ".github/skills/internal-example/SKILL.md"
    skill.write_text(
        skill.read_text() + "\nLoad `/internal-disabled` before execution.\n",
        encoding="utf-8",
    )

    findings = detect_internal_skill_findings(root)

    assert "disabled-skill-invocation" in {finding.code for finding in findings}


def test_invocations_in_references_and_openai_metadata_are_checked(
    tmp_path: Path,
) -> None:
    root = write_test_repository(tmp_path, "def test_fixture():\n    assert True\n")
    skill = root / ".github/skills/internal-example"
    (skill / "references/example.md").write_text(
        "Load `/internal-missing-reference`.\n", encoding="utf-8"
    )
    (skill / "agents/openai.yaml").write_text(
        """interface:
  display_name: Internal Example
  short_description: Internal example validator fixture
  default_prompt: Use /internal-missing-prompt for this fixture.
""",
        encoding="utf-8",
    )

    findings = detect_internal_skill_findings(root)

    unknown = [
        finding for finding in findings if finding.code == "unknown-skill-invocation"
    ]
    assert {finding.path for finding in unknown} == {
        (skill / "references/example.md").as_posix(),
        (skill / "agents/openai.yaml").as_posix(),
    }


def test_bare_identifier_and_fenced_examples_are_not_invocations(
    tmp_path: Path,
) -> None:
    root = write_test_repository(
        tmp_path,
        "def test_fixture():\n    assert True\n",
    )
    skill = root / ".github/skills/internal-example/SKILL.md"
    skill.write_text(
        skill.read_text()
        + "\nThe `internal-missing` identifier is descriptive.\n"
        + "\n```text\nLoad `/internal-missing-fenced`\n```\n",
        encoding="utf-8",
    )

    findings = detect_internal_skill_findings(root)

    assert "unknown-skill-invocation" not in {finding.code for finding in findings}
