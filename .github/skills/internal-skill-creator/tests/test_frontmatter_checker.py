import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = BUNDLE_ROOT / "tests" / "evaluation" / "fixtures"
CHECKER_PATH = BUNDLE_ROOT / "scripts" / "check_skill_frontmatter.py"
SPEC = importlib.util.spec_from_file_location("check_skill_frontmatter", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def _codes(text, tmp_path):
    path = tmp_path / "SKILL.md"
    path.write_text(text, encoding="utf-8")
    return sorted(finding["code"] for finding in CHECKER.check_file(path))


@pytest.mark.parametrize(
    "frontmatter",
    [
        'name: demo\ndescription: "Use when the need is narrow: a, b, or c."',
        "name: demo\ndescription: 'Use when the need is narrow: a, b, or c.'",
        "name: demo\ndescription: Use when the need is narrow, with a, b, or c.",
        "name: demo\ndescription: >-\n  Use when the need is narrow: a, b,\n  or c.",
        "name: demo\ndescription: Use when the need is narrow,\n  with a, b, or c.",
        "name: demo\ndescription: Use when a URL like https://x.y/z appears.",
        "name: demo\ndescription: Use when needed.\nmetadata:\n  source: x\n  risk: low",
    ],
)
def test_strict_yaml_safe_frontmatter_has_no_findings(frontmatter, tmp_path):
    assert _codes(f"---\n{frontmatter}\n---\n\n# Demo\n", tmp_path) == []


@pytest.mark.parametrize(
    "frontmatter",
    [
        "name: demo\ndescription: Use when the problem is workplace-first: negotiation or review.",
        "name: demo\ndescription: Use when the need is narrow,\n  with these parts: a, b, or c.",
        "name: demo\ndescription: Use when needed: ",
        "name: demo\ndescription: Use when needed #1 is set.",
        "name: demo\ndescription: `demo` is used when needed.",
        "name: demo\ndescription: @user asks.",
    ],
)
def test_unsafe_plain_scalar_is_reported(frontmatter, tmp_path):
    assert _codes(f"---\n{frontmatter}\n---\n", tmp_path) == [
        "frontmatter-unsafe-plain-scalar"
    ]


def test_missing_frontmatter_is_reported(tmp_path):
    assert _codes("# Demo\n", tmp_path) == ["frontmatter-missing"]


@pytest.mark.parametrize(
    "frontmatter",
    ["name: demo", "name: demo\ndescription:", "description: Use when needed."],
)
def test_missing_required_key_is_reported(frontmatter, tmp_path):
    assert _codes(f"---\n{frontmatter}\n---\n", tmp_path) == [
        "frontmatter-missing-key"
    ]


def test_strict_parser_error_is_reported_when_available(tmp_path):
    pytest.importorskip("yaml")
    assert _codes('---\nname: demo\ndescription: "Use when needed.\n---\n', tmp_path) == [
        "frontmatter-yaml-error"
    ]


def test_value_that_parses_as_mapping_is_reported_when_available(tmp_path):
    pytest.importorskip("yaml")
    assert _codes("---\nname: demo\ndescription:\n  Use when x: y\n---\n", tmp_path) == [
        "frontmatter-yaml-error"
    ]


def test_eval_fixtures_match_their_declared_outcome():
    assert CHECKER.check_file(FIXTURES / "frontmatter-valid.md") == []
    assert [f["code"] for f in CHECKER.check_file(FIXTURES / "frontmatter-defective.md")] == [
        "frontmatter-unsafe-plain-scalar"
    ]


def test_cli_reports_compact_findings_and_exit_code():
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            str(FIXTURES / "frontmatter-valid.md"),
            str(FIXTURES / "frontmatter-defective.md"),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert [f["code"] for f in payload["findings"]] == ["frontmatter-unsafe-plain-scalar"]
    assert payload["findings"][0]["line"] == 3


def test_creator_skill_frontmatter_is_yaml_safe():
    assert CHECKER.check_file(BUNDLE_ROOT / "SKILL.md") == []
