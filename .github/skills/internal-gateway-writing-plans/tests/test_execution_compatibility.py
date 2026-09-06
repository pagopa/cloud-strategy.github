import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
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
EXECUTOR_FIXTURE = EXECUTOR_BUNDLE / "fixtures/valid-plan.md"
STRUCTURAL_CHECK = BUNDLE / "scripts/check_plan_structure.py"
INVENTORY = REPO_ROOT / ".github/INVENTORY.md"


def _load_structural_check():
    spec = importlib.util.spec_from_file_location("check_plan_structure", STRUCTURAL_CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _stage_plan(tmp_path: Path, text: str) -> Path:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True, exist_ok=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir(exist_ok=True)
    plan = retained / WRITER_FIXTURE.name
    plan.write_text(text, encoding="utf-8")
    return plan


def _run_checker(plan: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(STRUCTURAL_CHECK),
            str(plan),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )


def _run_executor_preflight(plan: Path, repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(EXECUTOR_SCRIPT),
            "preflight",
            str(plan),
            "--repo-root",
            str(repo_root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )


def _finding_codes(result: subprocess.CompletedProcess[str]) -> set[str]:
    payload = json.loads(result.stdout)
    items = payload.get("findings") or payload.get("finding_sample") or []
    return {item["code"] for item in items}


def _normalized_manifest_contract(text: str) -> str:
    start_marker = "A current"
    end_marker = "no `## Execution Contract`."
    start = text.index(start_marker)
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

    assert _normalized_manifest_contract(executor) == _normalized_manifest_contract(
        writer
    )


def test_manifest_references_are_local_and_cover_normative_contract() -> None:
    writer_reference = BUNDLE / "references/manifest-v3.md"
    executor_reference = EXECUTOR_BUNDLE / "references/manifest-v3.md"

    assert writer_reference.is_file()
    assert executor_reference.is_file()
    assert _normalized_manifest_contract(
        writer_reference.read_text(encoding="utf-8")
    ) == _normalized_manifest_contract(executor_reference.read_text(encoding="utf-8"))


def test_always_loaded_gateway_surfaces_keep_routing_and_shrink() -> None:
    assert (BUNDLE / "SKILL.md").stat().st_size < 17000
    assert (EXECUTOR_BUNDLE / "SKILL.md").stat().st_size < 15000
    writer_metadata = yaml.safe_load(
        (BUNDLE / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    executor_metadata = yaml.safe_load(
        (EXECUTOR_BUNDLE / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    assert "references/manifest-v3.md" in writer_metadata["interface"]["default_prompt"]
    assert "references/manifest-v3.md" in executor_metadata["interface"]["default_prompt"]


def test_writer_documents_repository_preflight_fields() -> None:
    text = (BUNDLE / "SKILL.md").read_text(encoding="utf-8")
    headings = {
        line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")
    }
    lines = text.splitlines()
    start = next(
        index for index, line in enumerate(lines) if line.strip() == "## Repository Preflight"
    )
    tail = lines[start + 1 :]
    end = next((index for index, line in enumerate(tail) if line.startswith("#")), len(tail))
    preflight = "\n".join(tail[:end])
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


def _rewrite_manifest(text: str, mutate) -> str:
    match = re.search(
        r"(?ms)^## Execution Manifest\s*\n\s*```json\s*\n(.*?)\n```\s*$",
        text,
    )
    assert match
    manifest = json.loads(match.group(1))
    mutate(manifest)
    return text[: match.start(1)] + json.dumps(manifest, indent=2) + text[match.end(1) :]


PAST_FAILURE_MODES = (
    (
        "manifest-heading-suffix",
        lambda text: text.replace(
            "## Execution Manifest", "## Execution Manifest v3", 1
        ),
        "missing-execution-manifest",
    ),
    (
        "controls-serialized-as-array",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest.update(
                controls=[
                    {
                        "class": "automatable-local",
                        "owner": "executor preflight",
                        "binding": ["T1"],
                    }
                ]
            ),
        ),
        "malformed-execution-manifest",
    ),
    (
        "missing-manifest-identity-fields",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: [
                manifest.pop(key) for key in ("manifest_version", "repository_root")
            ],
        ),
        "missing-manifest-field",
    ),
    (
        "missing-target-state",
        lambda text: _rewrite_manifest(
            text, lambda manifest: manifest["targets"][0].pop("state")
        ),
        "missing-manifest-field",
    ),
    (
        "missing-baseline-validation-bullet",
        lambda text: re.sub(
            r"(?m)^- \*\*Baseline Validation:\*\*.*\n", "", text, count=1
        ),
        "missing-execution-field",
    ),
    (
        "non-canonical-handoff-requirement",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["handoff"].update(
                requires=[
                    "human execution approval",
                    "exact Manifest v3 review",
                    "zero blocking preflight findings",
                ]
            ),
        ),
        "malformed-execution-manifest",
    ),
)


@pytest.mark.parametrize(
    "name,mutate,expected_code",
    PAST_FAILURE_MODES,
    ids=[mode[0] for mode in PAST_FAILURE_MODES],
)
def test_writer_failure_modes_are_blocked_before_handoff(
    tmp_path: Path, name: str, mutate, expected_code: str
) -> None:
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    plan = retained / WRITER_FIXTURE.name
    plan.write_text(
        mutate(WRITER_FIXTURE.read_text(encoding="utf-8")), encoding="utf-8"
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

    assert result.returncode != 0, name
    findings = json.loads(result.stdout)["findings"]
    assert expected_code in {finding["code"] for finding in findings}, name


def test_writer_reference_documents_manifest_binding_contract() -> None:
    reference = (BUNDLE / "references/manifest-v3.md").read_text(encoding="utf-8")
    normalized = " ".join(reference.split())
    documented = {
        "exact-manifest-heading": re.escape("`## Execution Manifest` heading text is exact"),
        "manifest-section-shape": re.escape("exactly one fenced JSON code block"),
        "task-heading-binding": re.escape("task ids are exactly `T1` through `T<N>`"),
        "control-inventory-bijectivity": re.escape("keys, bijective in both directions"),
        "baseline-validation-bullet": re.escape("`- **Baseline Validation:**`"),
        "canonical-preflight-heading": re.escape("`## Repository Preflight`"),
        "canonical-handoff-requires": re.escape("`human approval`"),
    }
    found = {
        name for name, pattern in documented.items() if re.search(pattern, normalized)
    }
    assert found == set(documented)


def test_structural_check_passes_both_gateway_fixtures(tmp_path: Path) -> None:
    checker = _load_structural_check()
    (tmp_path / "AGENTS.md").write_text("# Test repository\n")
    (tmp_path / ".github").mkdir()
    retained = tmp_path / "tmp" / "superpowers" / "plans"
    retained.mkdir(parents=True)
    for fixture in (WRITER_FIXTURE, EXECUTOR_FIXTURE):
        staged = retained / fixture.name
        shutil.copy(fixture, staged)
        findings = checker.check_plan_structure(
            staged.read_text(encoding="utf-8"), staged
        )
        blocking = [item for item in findings if item.severity == "blocking"]
        assert not blocking, (fixture.name, blocking)


def test_structural_check_reports_lowercase_inventory_row_as_notice(tmp_path: Path) -> None:
    text = WRITER_FIXTURE.read_text(encoding="utf-8").replace(
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n",
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| notes | free text row | - | - | - | - | - | - |\n",
        1,
    )
    checker = _load_structural_check()
    staged = _stage_plan(tmp_path, text)

    findings = checker.check_plan_structure(staged.read_text(encoding="utf-8"), staged)

    assert staged.name == "2026-07-25-1829-valid-plan.md"
    notices = [item for item in findings if item.severity == "notice"]
    assert [item.code for item in notices] == ["inventory-row-not-a-control"]
    assert not [item for item in findings if item.severity == "blocking"]


def test_structural_check_rejects_staged_fixtures_outside_retained_directory(
    tmp_path: Path,
) -> None:
    checker = _load_structural_check()
    staged = tmp_path / "elsewhere.md"
    staged.write_text(WRITER_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    findings = checker.check_plan_structure(staged.read_text(encoding="utf-8"), staged)
    assert "plan-outside-retained-directory" in {item.code for item in findings}


def test_structural_check_compact_payload_matches_executor_shape(
    tmp_path: Path, capsys
) -> None:
    checker = _load_structural_check()
    staged = _stage_plan(tmp_path, WRITER_FIXTURE.read_text(encoding="utf-8"))
    result = _run_checker(staged)

    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert set(payload) == {"status", "finding_counts", "finding_sample", "next_action"}
    assert payload["status"] == "passed"
    assert set(payload["finding_counts"]) == {"total", "blocking", "notice"}


def test_structural_check_never_imports_executor_private_code() -> None:
    source = STRUCTURAL_CHECK.read_text(encoding="utf-8")

    assert "plan_execution" not in source
    assert "internal-gateway-execute-plans/scripts" not in source


def _rewrite_manifest(text: str, mutate) -> str:
    match = re.search(
        r"(?ms)^## Execution Manifest\s*\n\s*```json\s*\n(.*?)\n```\s*$",
        text,
    )
    assert match
    manifest = json.loads(match.group(1))
    mutate(manifest)
    return text[: match.start(1)] + json.dumps(manifest, indent=2) + text[match.end(1) :]


PRODUCER_FAILURE_MODES = (
    (
        "manifest-section-prose",
        lambda text: text.replace(
            "## Execution Manifest\n\n```json",
            "## Execution Manifest\n\nReviewer note: check before dispatch.\n\n```json",
            1,
        ),
        "malformed-execution-manifest",
        "malformed-execution-manifest",
    ),
    (
        "task-heading-missing-colon",
        lambda text: text.replace(
            "### Task 1: Add example test", "### Task 1 Add example test", 1
        ),
        "bootstrap-projection-drift",
        "bootstrap-projection-drift",
    ),
    (
        "task-heading-number-gap",
        lambda text: text.replace("### Task 2:", "### Task 3:", 1),
        "bootstrap-projection-drift",
        "bootstrap-projection-drift",
    ),
    (
        "execution-contract-in-manifest-only",
        lambda text: text + "\n## Execution Contract\n\n```json\n{\"validations\": []}\n```\n",
        "obsolete-execution-contract",
        "obsolete-execution-contract",
    ),
    (
        "duplicate-json-key",
        lambda text: text.replace(
            '"plan_id": "2026-07-25-1829-valid-plan",',
            '"plan_id": "2026-07-25-1829-valid-plan", "plan_id": "drift",',
            1,
        ),
        "duplicate-manifest-field",
        "duplicate-manifest-field",
    ),
    (
        "unknown-target-reference",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["tasks"][0].update({"target_ids": ["TGT-MISSING"]}),
        ),
        "unknown-task-reference",
        "unknown-task-reference",
    ),
    (
        "git-mutating-validation-command",
        lambda text: text.replace(
            '"command": "pytest -q tests/example/test_example.py"',
            '"command": "git commit -am forbidden"',
            1,
        ),
        "git-mutation-command",
        "git-mutation-command",
    ),
    (
        "delegation-mode-delegated",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["delegation"].update({"mode": "delegated"}),
        ),
        "delegation-not-supported",
        "delegation-not-supported",
    ),
    (
        "missing-delegation-receipt-key",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["delegation"].pop("receipt"),
        ),
        "missing-manifest-field",
        "malformed-delegation-extension",
    ),
    (
        "handoff-requires-missing-canonical-string",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["handoff"].update(
                {"requires": ["human approval", "zero blocking preflight findings"]}
            ),
        ),
        "malformed-execution-manifest",
        "malformed-execution-manifest",
    ),
    (
        "bootstrap-projection-binding-conflict",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["bootstrap"]["projection_binding"].update(
                {"validations": "manifest.execution_contract"}
            ),
        ),
        "malformed-execution-manifest",
        "malformed-execution-manifest",
    ),
    (
        "retry-budget-zero",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["retry_policy"].update(
                {"max_corrective_retries": 0}
            ),
        ),
        "malformed-execution-manifest",
        "malformed-execution-manifest",
    ),
    (
        "embedded-semantic-fingerprint",
        lambda text: _rewrite_manifest(
            text,
            lambda manifest: manifest["approval"].update(
                {"semantic_fingerprint": "sha256:" + "1" * 64}
            ),
        ),
        "unknown-manifest-field",
        "unknown-manifest-field",
    ),
    (
        "required-heading-suffix",
        lambda text: text.replace("## Control Inventory", "## Control Inventory v2", 1),
        "missing-heading",
        "missing-control-inventory",
    ),
    (
        "manifest-section-trailing-prose",
        lambda text: text.replace(
            "## Repository Preflight",
            "Editorial note after the manifest fence.\n\n## Repository Preflight",
            1,
        ),
        "malformed-execution-manifest",
        "malformed-execution-manifest",
    ),
)


@pytest.mark.parametrize(
    "name,mutate,checker_code,executor_code",
    PRODUCER_FAILURE_MODES,
    ids=[mode[0] for mode in PRODUCER_FAILURE_MODES],
)
def test_producer_failure_modes_are_blocked_before_handoff(
    tmp_path: Path,
    name: str,
    mutate,
    checker_code: str | None,
    executor_code: str | None,
) -> None:
    plan = _stage_plan(tmp_path, mutate(WRITER_FIXTURE.read_text(encoding="utf-8")))

    checker_result = _run_checker(plan)
    executor_result = _run_executor_preflight(plan, tmp_path)

    checker_codes = _finding_codes(checker_result)
    executor_codes = _finding_codes(executor_result)
    if checker_code is None:
        assert checker_result.returncode == 0, (name, checker_codes)
    else:
        assert checker_result.returncode != 0, (name, checker_codes)
        assert checker_code in checker_codes, (name, checker_codes)
    if executor_code is None:
        assert executor_result.returncode == 0, (name, executor_codes)
    else:
        assert executor_result.returncode != 0, (name, executor_codes)
        assert executor_code in executor_codes, (name, executor_codes)


@pytest.mark.parametrize(
    "name,mutate",
    [
        (mode[0], mode[1])
        for mode in (*PAST_FAILURE_MODES, *PRODUCER_FAILURE_MODES)
        if mode[2] is not None
    ],
    ids=[mode[0] for mode in (*PAST_FAILURE_MODES, *PRODUCER_FAILURE_MODES) if mode[2] is not None],
)
def test_executor_blocking_implies_structural_check_blocking(
    tmp_path: Path, name: str, mutate
) -> None:
    plan = _stage_plan(tmp_path, mutate(WRITER_FIXTURE.read_text(encoding="utf-8")))

    checker_result = _run_checker(plan)
    executor_result = _run_executor_preflight(plan, tmp_path)

    if executor_result.returncode != 0:
        assert checker_result.returncode != 0, name


@pytest.mark.parametrize(
    "name,mutate,checker_code",
    (
        (
            "required-heading-wrong-level",
            lambda text: text.replace("## Goal", "### Goal", 1),
            "missing-heading",
        ),
        (
            "preflight-field-outside-section",
            lambda text: text.replace(
                "- **Baseline Validation:** run `pytest -q tests/example/test_example.py` before edits and record the result.\n",
                "",
                1,
            ).replace(
                "Validate the manifest-authoritative writer output against the executor.",
                "Validate the manifest-authoritative writer output against the executor.\n\n"
                "Baseline Validation: run the focused pytest before edits.",
                1,
            ),
            "missing-execution-field",
        ),
        (
            "handoff-requires-superset",
            lambda text: _rewrite_manifest(
                text,
                lambda manifest: manifest["handoff"].update(
                    {
                        "requires": [
                            "human approval",
                            "exact Manifest v3 review",
                            "zero blocking preflight findings",
                            "extra re-confirmation",
                        ]
                    }
                ),
            ),
            "non-canonical-handoff-requires",
        ),
    ),
    ids=[
        "required-heading-wrong-level",
        "preflight-field-outside-section",
        "handoff-requires-superset",
    ],
)
def test_writer_canonical_strictness_blocks_before_executor(
    tmp_path: Path, name: str, mutate, checker_code: str
) -> None:
    plan = _stage_plan(tmp_path, mutate(WRITER_FIXTURE.read_text(encoding="utf-8")))

    checker_result = _run_checker(plan)
    executor_result = _run_executor_preflight(plan, tmp_path)

    assert checker_result.returncode != 0, name
    assert checker_code in _finding_codes(checker_result), name
    assert executor_result.returncode == 0, name
