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
    start = text.index(start_marker, text.index("## Normative Manifest v3 Contract"))
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

    assert not any(
        "internal-gateway-execute-plans" in module for module in imported_modules
    )
    assert "plan_execution" not in imported_names


def test_writer_fixture_emits_manifest_only() -> None:
    text = WRITER_FIXTURE.read_text(encoding="utf-8")
    assert text.count("## Execution Manifest") == 1
    assert "## Execution Contract" not in text
    _, task_ids = extract_manifest_projection(text)
    assert task_ids == ("T1", "T2")


def test_gateway_normative_manifest_contracts_remain_equal() -> None:
    executor = (EXECUTOR_BUNDLE / "references/manifest-v3.md").read_text(
        encoding="utf-8"
    )
    writer = (BUNDLE / "references/manifest-v3.md").read_text(encoding="utf-8")

    assert re.sub(r"\s+", " ", executor).strip() == re.sub(r"\s+", " ", writer).strip()


def test_manifest_references_are_local_and_cover_normative_contract() -> None:
    writer_reference = BUNDLE / "references/manifest-v3.md"
    executor_reference = EXECUTOR_BUNDLE / "references/manifest-v3.md"

    assert writer_reference.is_file()
    assert executor_reference.is_file()
    required_terms = {
        "schema_version",
        "manifest_version",
        "authority_boundaries",
        "delegation",
        "targets",
        "controls",
        "validations",
        "manual_obligations",
        "tasks",
        "retry_policy",
        "approval",
        "bootstrap",
        "rollout",
        "handoff",
        "semantic_fingerprint",
        "status sibling",
        "parser",
    }
    writer_text = writer_reference.read_text(encoding="utf-8")
    executor_text = executor_reference.read_text(encoding="utf-8")
    assert required_terms <= set(re.findall(r"[A-Za-z_]+(?: [A-Za-z_]+)?", writer_text))
    assert required_terms <= set(
        re.findall(r"[A-Za-z_]+(?: [A-Za-z_]+)?", executor_text)
    )

    def normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    assert normalize(writer_text) == normalize(executor_text)


def test_always_loaded_gateway_surfaces_keep_routing_and_shrink() -> None:
    writer = (BUNDLE / "SKILL.md").read_text(encoding="utf-8")
    executor = (EXECUTOR_BUNDLE / "SKILL.md").read_text(encoding="utf-8")

    for text in (writer, executor):
        assert "Manifest v3" in text
        assert "preflight" in text
        assert "no Git" in text or "Git mutation" in text
    assert len(writer) < 17000
    assert len(executor) < 15000
    writer_metadata = (BUNDLE / "agents/openai.yaml").read_text(encoding="utf-8")
    executor_metadata = (EXECUTOR_BUNDLE / "agents/openai.yaml").read_text(
        encoding="utf-8"
    )
    assert "references/manifest-v3.md" in writer_metadata
    assert "references/manifest-v3.md" in executor_metadata


def test_writer_documents_repository_preflight_fields() -> None:
    text = (BUNDLE / "SKILL.md").read_text(encoding="utf-8")
    headings = {
        line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")
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
    writer_manifest = json.loads(
        re.search(
            r"(?ms)^## Execution Manifest\s*\n\s*```json\s*\n(.*?)\n```\s*$",
            WRITER_FIXTURE.read_text(encoding="utf-8"),
        ).group(1)
    )
    executor_manifest = json.loads(
        re.search(
            r"(?ms)^## Execution Manifest\s*\n\s*```json\s*\n(.*?)\n```\s*$",
            executor_fixture,
        ).group(1)
    )
    inventory = INVENTORY.read_text(encoding="utf-8")

    assert isinstance(writer_metadata, dict) and "interface" in writer_metadata
    assert isinstance(executor_metadata, dict) and "interface" in executor_metadata
    assert (EXECUTOR_BUNDLE / "scripts/run.sh").is_file()
    assert (EXECUTOR_BUNDLE / "scripts/requirements.in").is_file()
    assert (EXECUTOR_BUNDLE / "scripts/requirements.txt").is_file()
    assert "## Status Contract" in executor_fixture
    assert "status" in executor_fixture.lower()
    assert writer_manifest["schema_version"] == 3
    assert executor_manifest["schema_version"] == 3
    assert writer_manifest["manifest_version"] == "execution-manifest/v3"
    assert executor_manifest["manifest_version"] == "execution-manifest/v3"
    assert writer_manifest["retry_policy"]["max_corrective_retries"] == 3
    assert executor_manifest["retry_policy"]["max_corrective_retries"] == 3
    assert "semantic_fingerprint" in (BUNDLE / "SKILL.md").read_text(encoding="utf-8")
    assert (
        "content hash" not in (BUNDLE / "SKILL.md").read_text(encoding="utf-8").lower()
    )
    assert "## Execution Contract" not in executor_fixture
    assert "schema_version: 2" in executor_fixture
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


def test_executor_blocks_unsupported_delegated_manifest_tuple(tmp_path: Path) -> None:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    text = WRITER_FIXTURE.read_text(encoding="utf-8")
    manifest_match = re.search(
        r"(?ms)(^## Execution Manifest\s*\n\s*```json\s*\n)(.*?)(\n```\s*$)",
        text,
    )
    assert manifest_match
    manifest = json.loads(manifest_match.group(2))
    manifest["delegation"] = {
        "schema_version": 1,
        "mode": "delegated",
        "worker": "internal-luna-executor",
        "result": "worker-result",
        "receipt": "worker-receipt",
        "acceptance": "caller-acceptance",
    }
    plan.write_text(
        text[: manifest_match.start(2)]
        + json.dumps(manifest, indent=2)
        + text[manifest_match.end(2) :],
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(EXECUTOR_SCRIPT),
            "preflight",
            str(plan),
            "--repo-root",
            str(tmp_path),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert any(
        finding["code"] == "delegation-not-supported" for finding in payload["findings"]
    )
