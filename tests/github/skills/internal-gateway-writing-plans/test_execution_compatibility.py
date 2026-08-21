import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-writing-plans"
WRITER_FIXTURE = BUNDLE / "fixtures/2026-07-25-1829-valid-plan.md"
EXECUTOR_SCRIPT = (
    REPO_ROOT
    / ".github/skills/internal-gateway-execute-plans/scripts/plan_execution.py"
)
EXECUTOR_BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-execute-plans"
INVENTORY = REPO_ROOT / ".github/INVENTORY.md"


def _normalized_manifest_contract(text: str) -> str:
    start_marker = "A current"
    end_marker = "no `## Execution Contract`."
    start = text.index(start_marker, text.index("## Normative Manifest v2 Contract"))
    end = text.index(end_marker, start) + len(end_marker)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def extract_manifest_projection(text: str) -> tuple[set[str], tuple[str, ...]]:
    """Extract the writer-owned control table and task IDs from the manifest."""

    lines = text.splitlines()
    collecting = False
    control_ids: set[str] = set()
    for line in lines:
        if line == "## Control Inventory":
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if collecting and line.strip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and cells[0] not in {"ID", "---"} and cells[0]:
                control_ids.add(cells[0])

    match = re.search(
        r"(?ms)^## Execution Manifest\s*\n\s*```json\s*\n(.*?)\n```\s*$",
        text,
    )
    assert match
    manifest = json.loads(match.group(1))
    tasks = sorted(manifest["tasks"], key=lambda item: item["order"])
    task_ids = tuple(task["id"] for task in tasks)
    return control_ids, task_ids


def test_writer_producer_projection_has_exact_controls_and_tasks() -> None:
    text = WRITER_FIXTURE.read_text()
    controls, task_ids = extract_manifest_projection(text)
    task_headings = [
        line.strip()
        for line in WRITER_FIXTURE.read_text().splitlines()
        if re.match(r"^#{2,6}\s+Task\s+\d+\b", line)
    ]

    assert controls == {"CI-01"}
    assert task_ids == ("T1", "T2")
    assert len(task_headings) == len(task_ids)
    assert "## Producer Readiness" in text


def test_writer_producer_does_not_import_executor_private_code() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert not any("internal-gateway-execute-plans" in module for module in imported_modules)
    assert "plan_execution" not in imported_names


def test_writer_fixture_emits_manifest_only() -> None:
    text = WRITER_FIXTURE.read_text(encoding="utf-8")
    assert text.count("## Execution Manifest") == 1
    assert "## Execution Contract" not in text
    _, task_ids = extract_manifest_projection(text)
    assert task_ids == ("T1", "T2")


def test_gateway_normative_manifest_contracts_remain_equal() -> None:
    executor = (REPO_ROOT / ".github/skills/internal-gateway-execute-plans/SKILL.md").read_text(
        encoding="utf-8"
    )
    writer = (BUNDLE / "SKILL.md").read_text(encoding="utf-8")

    assert _normalized_manifest_contract(executor) == _normalized_manifest_contract(writer)


def test_writer_documents_repository_preflight_fields() -> None:
    text = (BUNDLE / "SKILL.md").read_text(encoding="utf-8")
    headings = {
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("#")
    }
    preflight = text.split("## Repository Preflight", 1)[1].split("## ", 1)[0]
    fields = {
        line.split(":", 1)[0].strip(" -*")
        for line in preflight.splitlines()
        if ":" in line
    }

    assert "Repository Preflight" in headings
    assert {
        "Baseline Validation",
        "Recovery Policy",
        "Escalation Conditions",
        "User-Facing Report",
    } <= fields


def test_metadata_fixtures_runner_and_inventory_are_structurally_aligned() -> None:
    writer_metadata = yaml.safe_load(
        (BUNDLE / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    executor_metadata = yaml.safe_load(
        (EXECUTOR_BUNDLE / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    executor_fixture = (EXECUTOR_BUNDLE / "fixtures/valid-plan.md").read_text(
        encoding="utf-8"
    )
    inventory = INVENTORY.read_text(encoding="utf-8")

    assert isinstance(writer_metadata, dict) and "interface" in writer_metadata
    assert isinstance(executor_metadata, dict) and "interface" in executor_metadata
    assert (EXECUTOR_BUNDLE / "scripts/run.sh").is_file()
    assert (EXECUTOR_BUNDLE / "scripts/requirements.in").is_file()
    assert (EXECUTOR_BUNDLE / "scripts/requirements.txt").is_file()
    assert "## Status Contract" in executor_fixture
    assert "status" in executor_fixture.lower()
    assert ".github/skills/internal-gateway-writing-plans/SKILL.md" in inventory
    assert ".github/skills/internal-gateway-execute-plans/SKILL.md" in inventory


def test_writer_plan_remains_actionable_through_preflight_cli(tmp_path: Path) -> None:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    shutil.copy(WRITER_FIXTURE, plan)

    manifest_match = re.search(
        r"(?ms)^## Execution Manifest\s*\n\s*```json\s*\n(.*?)\n```\s*$",
        plan.read_text(encoding="utf-8"),
    )
    assert manifest_match
    assert json.loads(manifest_match.group(1))["delegation"] == {
        "schema_version": 1,
        "mode": "none",
        "worker": "primary-owner",
        "result": "not_applicable",
        "receipt": None,
        "acceptance": None,
    }

    result = subprocess.run(
        [
            sys.executable,
            str(EXECUTOR_SCRIPT),
            "preflight",
            str(plan),
            "--repo-root",
            str(tmp_path),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "passed"
