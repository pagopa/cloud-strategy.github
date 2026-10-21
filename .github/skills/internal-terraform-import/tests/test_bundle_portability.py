from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
RUNNER = "scripts/import-manifest-runner.sh"
FRONTMATTER_KEYS = {"name", "description", "metadata", "license", "compatibility"}
LINK_PATTERN = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
REQUIRED_FUNCTION_PATTERN = re.compile(
    r"declare -F \"?\$?(\w+)\"?|for required_function in ([\w ]+); do"
)


def _split_skill(bundle: Path) -> tuple[dict[str, Any], str]:
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter), body


def _section(body: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    assert match, heading
    return match.group(1)


def _fenced_blocks(markdown: str) -> list[list[str]]:
    return [block.strip("\n").splitlines() for block in re.findall(r"```text\n(.*?)```", markdown, re.S)]


def _table_first_column(markdown: str) -> set[str]:
    cells = set()
    for line in markdown.splitlines():
        if line.startswith("| `"):
            cells.add(line.split("|")[1].strip().strip("`"))
    return cells


def _runner_required_functions(runner_text: str) -> set[str]:
    functions: set[str] = set()
    for single, listed in REQUIRED_FUNCTION_PATTERN.findall(runner_text):
        if single and single != "required_function":
            functions.add(single)
        functions.update(listed.split())
    return functions


def test_frontmatter_and_metadata_are_portable() -> None:
    frontmatter, _ = _split_skill(BUNDLE_ROOT)
    metadata = yaml.safe_load((BUNDLE_ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))

    assert set(frontmatter) <= FRONTMATTER_KEYS
    assert frontmatter["name"] == BUNDLE_ROOT.name
    assert metadata["policy"]["allow_implicit_invocation"] is False


def test_bundle_is_standalone_and_every_reference_is_linked(tmp_path: Path) -> None:
    copied = tmp_path / BUNDLE_ROOT.name
    shutil.copytree(BUNDLE_ROOT, copied, ignore=shutil.ignore_patterns("__pycache__"))
    _, body = _split_skill(copied)
    links = {target for target in LINK_PATTERN.findall(body) if "://" not in target}
    references = {
        path.relative_to(copied).as_posix() for path in (copied / "references").glob("*.md")
    }

    assert references <= links
    for target in links:
        resolved = (copied / target).resolve()
        assert resolved.is_relative_to(copied.resolve()), target
        assert resolved.is_file(), target
    for script in ("import-manifest-runner.sh", "adoption_protocol.py", "resolve-aws-identity-center-import.sh"):
        assert (copied / "scripts" / script).is_file(), script


def test_documented_synopsis_matches_runner_usage(tmp_path: Path) -> None:
    result = subprocess.run(
        ["bash", str(BUNDLE_ROOT / RUNNER), "--help"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    _, body = _split_skill(BUNDLE_ROOT)

    assert result.returncode == 0
    assert result.stderr.strip("\n").splitlines() in _fenced_blocks(_section(body, "Run"))


def test_documented_adapter_functions_match_runner_capability_checks() -> None:
    runner_text = (BUNDLE_ROOT / RUNNER).read_text(encoding="utf-8")
    _, body = _split_skill(BUNDLE_ROOT)

    assert _table_first_column(_section(body, "Run")) == _runner_required_functions(runner_text)


def test_import_protocol_cli_runs_from_external_working_directory(tmp_path: Path) -> None:
    protocol = BUNDLE_ROOT / "scripts/adoption_protocol.py"
    result = subprocess.run(
        [sys.executable, str(protocol), "classify-plan"],
        cwd=tmp_path,
        input=json.dumps({"actions": [{"address": "resource.example", "action": "no-op"}]}),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["allowed"] is True
