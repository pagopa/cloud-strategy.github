from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TOOLS_ROOT = REPO_ROOT / ".github/tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from common.findings import Finding  # noqa: E402
from skills.rules import (  # noqa: E402
    detect_bundle_security_findings,
    detect_internal_skill_findings,
    detect_skill_invocation_findings,
    detect_skill_prose_assertion_findings,
    validate_internal_skill,
    validate_local_references,
    validate_openai_yaml,
    validate_output_contract_projection,
    validate_token_hygiene,
)

RuleCase = Callable[[Path], list[Finding]]


def _write(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _skill_text(
    name: str = "internal-example",
    description: str = "Use when testing skill fixtures.",
    body: str = "## When to use\n\n- Fixture.\n",
    extra_frontmatter: str = "",
) -> str:
    return (
        f"---\nname: {name}\ndescription: {description}\n"
        f"{extra_frontmatter}---\n\n{body}"
    )


def _openai_yaml(
    name: str = "internal-example",
    display_name: str = "Internal Example",
    short_description: str = "Internal example validator fixture",
    default_prompt: str | None = "Use /internal-example for this fixture.",
    extra: str = "",
) -> str:
    prompt = ""
    if default_prompt is not None:
        prompt = f"  default_prompt: {default_prompt}\n"
    return (
        "interface:\n"
        f"  display_name: {display_name}\n"
        f"  short_description: {short_description}\n"
        f"{prompt}{extra}"
    )


def _write_valid_skill(root: Path, **kwargs: str) -> Path:
    skill_dir = root / ".github/skills/internal-example"
    _write(skill_dir, "SKILL.md", _skill_text(**kwargs))
    _write(skill_dir, "agents/openai.yaml", _openai_yaml())
    return skill_dir


def _validate_skill(root: Path, **kwargs: str) -> list[Finding]:
    skill_dir = _write_valid_skill(root, **kwargs)
    return validate_internal_skill(root, skill_dir)


def _skill_prose_assertion(root: Path) -> list[Finding]:
    _write_valid_skill(root)
    _write(
        root,
        "tests/test_contract.py",
        """from pathlib import Path

SKILL = Path('.github/skills/internal-example/SKILL.md')
text = SKILL.read_text()

def test_contract():
    assert 'required wording' in text
""",
    )
    return detect_skill_prose_assertion_findings(root)


def _unknown_invocation(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(
        skill_dir,
        "SKILL.md",
        _skill_text() + "Load /internal-missing before execution.\n",
    )
    return detect_skill_invocation_findings(root)


def _disabled_invocation(root: Path) -> list[Finding]:
    source_dir = _write_valid_skill(root)
    target_dir = root / ".github/skills/internal-disabled"
    _write(
        target_dir,
        "SKILL.md",
        _skill_text(
            name="internal-disabled",
            description="Use when testing disabled invocation fixtures.",
            extra_frontmatter="disable-model-invocation: true\n",
        ),
    )
    _write(target_dir, "agents/openai.yaml", _openai_yaml(name="internal-disabled"))
    _write(
        source_dir,
        "SKILL.md",
        _skill_text() + "Load /internal-disabled before execution.\n",
    )
    return detect_skill_invocation_findings(root)


def _missing_skill_md(root: Path) -> list[Finding]:
    skill_dir = root / ".github/skills/internal-example"
    skill_dir.mkdir(parents=True)
    return validate_internal_skill(root, skill_dir)


def _missing_frontmatter(root: Path) -> list[Finding]:
    skill_dir = root / ".github/skills/internal-example"
    _write(skill_dir, "SKILL.md", "No frontmatter.\n")
    return validate_internal_skill(root, skill_dir)


def _invalid_frontmatter(root: Path) -> list[Finding]:
    skill_dir = root / ".github/skills/internal-example"
    _write(skill_dir, "SKILL.md", "---\nname: [\n---\n")
    return validate_internal_skill(root, skill_dir)


def _missing_openai_yaml(root: Path) -> list[Finding]:
    skill_dir = root / ".github/skills/internal-example"
    _write(skill_dir, "SKILL.md", _skill_text())
    return validate_openai_yaml(skill_dir, skill_dir.name)


def _invalid_openai_yaml(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(skill_dir, "agents/openai.yaml", "interface: [\n")
    return validate_openai_yaml(skill_dir, skill_dir.name)


def _missing_openai_interface(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(skill_dir, "agents/openai.yaml", "policy: {}\n")
    return validate_openai_yaml(skill_dir, skill_dir.name)


def _stale_output_contract(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(
        skill_dir,
        "SKILL.md",
        _skill_text(body="Deeper fields do not appear in chat.\n"),
    )
    _write(
        skill_dir,
        "agents/openai.yaml",
        _openai_yaml(default_prompt="Every finding must retain Critique."),
    )
    return validate_output_contract_projection(root, skill_dir, skill_dir.name)


def _bundle_external_url(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(skill_dir, "scripts/fetch.py", "URL = 'https://example.test/api'\n")
    return detect_bundle_security_findings(skill_dir)


def _cross_skill_reference(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(
        root,
        ".github/skills/internal-other/SKILL.md",
        _skill_text(
            name="internal-other", description="Use when testing another skill."
        ),
    )
    _write(
        skill_dir,
        "SKILL.md",
        _skill_text() + "See [the other skill](../internal-other/SKILL.md).\n",
    )
    return validate_local_references(root, skill_dir)


def _missing_local_reference(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(
        skill_dir,
        "SKILL.md",
        _skill_text() + "See [the missing reference](references/missing.md).\n",
    )
    return validate_local_references(root, skill_dir)


def _heavy_skill_body(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    body = "\n".join("detail" for _ in range(221))
    return validate_token_hygiene(
        skill_dir,
        skill_dir / "SKILL.md",
        body,
    )


def _inline_template_density(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    body = "```text\nexample one\n```\n\n```text\nexample two\n```\n"
    return validate_token_hygiene(skill_dir, skill_dir / "SKILL.md", body)


def _openai_only_case(root: Path, **kwargs: str) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(skill_dir, "agents/openai.yaml", _openai_yaml(**kwargs))
    return validate_openai_yaml(skill_dir, skill_dir.name)


def _invalid_policy_value(root: Path) -> list[Finding]:
    return _openai_only_case(
        root, extra='policy:\n  allow_implicit_invocation: "yes"\n'
    )


def _missing_icon_asset(root: Path) -> list[Finding]:
    return _openai_only_case(root, extra="  icon_small: ./assets/missing.svg\n")


def _missing_display_name(root: Path) -> list[Finding]:
    return _openai_only_case(root, display_name="")


def _missing_short_description(root: Path) -> list[Finding]:
    skill_dir = _write_valid_skill(root)
    _write(
        skill_dir,
        "agents/openai.yaml",
        "interface:\n  display_name: Internal Example\n",
    )
    return validate_openai_yaml(skill_dir, skill_dir.name)


def _short_description_length(root: Path) -> list[Finding]:
    return _openai_only_case(root, short_description="Too short")


def _missing_default_prompt(root: Path) -> list[Finding]:
    return _openai_only_case(root, default_prompt="")


def _default_prompt_skill_mention(root: Path) -> list[Finding]:
    return _openai_only_case(root, default_prompt="Use the validator fixture.")


def _placeholder_short_description(root: Path) -> list[Finding]:
    return _openai_only_case(root, short_description="Help with Internal Example tasks")


def _placeholder_default_prompt(root: Path) -> list[Finding]:
    return _openai_only_case(
        root,
        default_prompt=(
            "Use /internal-example for this task and follow the "
            "repository-owned workflow in the skill."
        ),
    )


def _cross_skill_dollar_invocation(root: Path) -> list[Finding]:
    source_dir = _write_valid_skill(root)
    _write(
        root / ".github/skills/internal-other",
        "SKILL.md",
        _skill_text(
            name="internal-other",
            description="Use when testing cross-skill invocation fixtures.",
        ),
    )
    _write(
        source_dir,
        "agents/openai.yaml",
        _openai_yaml(
            default_prompt=(
                "Use /internal-example for this fixture, then apply "
                "$internal-other for the rest."
            )
        ),
    )
    return detect_skill_invocation_findings(root)


SKILL_RULE_CASES: list[tuple[str, RuleCase]] = [
    ("skill-prose-lexical-assertion", _skill_prose_assertion),
    ("unknown-skill-invocation", _unknown_invocation),
    ("disabled-skill-invocation", _disabled_invocation),
    ("missing-skill-md", _missing_skill_md),
    (
        "missing-frontmatter-block",
        lambda root: _missing_frontmatter(root),
    ),
    ("invalid-frontmatter-block", _invalid_frontmatter),
    ("skill-name-mismatch", lambda root: _validate_skill(root, name="internal-wrong")),
    ("missing-description", lambda root: _validate_skill(root, description="")),
    (
        "description-not-trigger-first",
        lambda root: _validate_skill(
            root, description="A description without a trigger."
        ),
    ),
    (
        "non-portable-frontmatter-field",
        lambda root: _validate_skill(root, extra_frontmatter="user-invocable: false\n"),
    ),
    (
        "missing-when-to-use-heading",
        lambda root: _validate_skill(root, body="No routing heading.\n"),
    ),
    ("stale-output-contract", _stale_output_contract),
    ("missing-openai-yaml", _missing_openai_yaml),
    ("invalid-openai-yaml", _invalid_openai_yaml),
    ("missing-openai-interface", _missing_openai_interface),
    ("invalid-policy-value", _invalid_policy_value),
    ("missing-icon-asset", _missing_icon_asset),
    ("missing-display-name", _missing_display_name),
    ("missing-short-description", _missing_short_description),
    ("short-description-length", _short_description_length),
    ("missing-default-prompt", _missing_default_prompt),
    ("default-prompt-skill-mention", _default_prompt_skill_mention),
    ("placeholder-interface-text", _placeholder_short_description),
    ("cross-skill-dollar-invocation", _cross_skill_dollar_invocation),
    ("bundle-script-external-url", _bundle_external_url),
    ("cross-skill-file-reference", _cross_skill_reference),
    ("missing-local-reference", _missing_local_reference),
    ("heavy-skill-body", _heavy_skill_body),
    ("inline-template-density", _inline_template_density),
]


def test_disabled_invocation_covers_non_internal_skill_targets(tmp_path: Path) -> None:
    source_dir = _write_valid_skill(tmp_path)
    target_dir = tmp_path / ".github/skills/external-disabled"
    _write(
        target_dir,
        "SKILL.md",
        _skill_text(
            name="external-disabled",
            description="Use when testing external disabled invocation fixtures.",
            extra_frontmatter="disable-model-invocation: true\n",
        ),
    )
    _write(
        source_dir,
        "SKILL.md",
        _skill_text() + "Load /external-disabled before execution.\n",
    )

    findings = detect_skill_invocation_findings(tmp_path)

    assert [finding.code for finding in findings] == ["disabled-skill-invocation"]


def test_invocation_scan_ignores_non_skill_path_segments(tmp_path: Path) -> None:
    source_dir = _write_valid_skill(tmp_path)
    _write(
        source_dir,
        "SKILL.md",
        _skill_text() + "Run /usr/bin/env, then read /docs and /action notes.\n",
    )

    findings = detect_skill_invocation_findings(tmp_path)

    assert findings == []


def test_router_phrasing_is_accepted_as_a_trigger_prefix(tmp_path: Path) -> None:
    findings = _validate_skill(
        tmp_path,
        description=(
            "Use first for every request in this domain. Classify the primary "
            "deliverable and invoke the minimum specialist lane."
        ),
    )

    assert [
        finding for finding in findings if finding.code == "description-not-trigger-first"
    ] == []


def test_trigger_first_check_has_no_per_name_exemption(tmp_path: Path) -> None:
    skill_dir = tmp_path / ".github/skills/internal-aws"
    _write(
        skill_dir,
        "SKILL.md",
        _skill_text(
            name="internal-aws",
            description="A router description without a trigger prefix.",
        ),
    )
    _write(skill_dir, "agents/openai.yaml", _openai_yaml(name="internal-aws"))

    findings = validate_internal_skill(tmp_path, skill_dir)

    assert "description-not-trigger-first" in {finding.code for finding in findings}


def test_skill_rule_case_inventory_is_explicit() -> None:
    codes = [code for code, _ in SKILL_RULE_CASES]
    assert len(codes) == len(set(codes))
    assert len(codes) == 29


def test_placeholder_rule_also_covers_the_default_prompt_template(
    tmp_path: Path,
) -> None:
    findings = _placeholder_default_prompt(tmp_path)

    assert "placeholder-interface-text" in {finding.code for finding in findings}


def test_dollar_invocation_scan_allows_the_bundle_own_entrypoint(
    tmp_path: Path,
) -> None:
    skill_dir = _write_valid_skill(tmp_path)
    _write(
        skill_dir,
        "agents/openai.yaml",
        _openai_yaml(default_prompt="Use $internal-example for this fixture."),
    )

    findings = detect_skill_invocation_findings(tmp_path)

    assert findings == []


def test_dollar_invocation_scan_rejects_missing_repo_owned_skill(
    tmp_path: Path,
) -> None:
    skill_dir = _write_valid_skill(tmp_path)
    _write(
        skill_dir,
        "SKILL.md",
        _skill_text() + "Load $internal-retired before execution.\n",
    )

    findings = detect_skill_invocation_findings(tmp_path)

    assert "unknown-skill-invocation" in {finding.code for finding in findings}


@pytest.mark.parametrize(
    "code, build_findings", SKILL_RULE_CASES, ids=[code for code, _ in SKILL_RULE_CASES]
)
def test_skill_rule_reports_non_absence_finding(
    tmp_path: Path, code: str, build_findings: RuleCase
) -> None:
    findings = build_findings(tmp_path)
    matching = [finding for finding in findings if finding.code == code]

    assert matching, f"{code} did not produce its expected finding"
    assert matching[0].path
    assert matching[0].message


def test_skill_rule_aggregator_keeps_all_rule_families_reachable() -> None:
    assert callable(detect_internal_skill_findings)
