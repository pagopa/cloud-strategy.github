import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-execute-plans"
SCRIPTS = BUNDLE / "scripts"
FIXTURES = BUNDLE / "fixtures"
sys.path.insert(0, str(SCRIPTS))

from plan_execution import (  # noqa: E402
    ExecutionContractError,
    Finding,
    Baseline,
    build_compact_payload,
    canonical_json,
    compute_content_sha256,
    compute_semantic_fingerprint,
    parse_execution_manifest,
    git_diff_check_coverage,
    validate_ignored_artifact,
    validate_manifest_projection,
    validate_plan,
    validate_relevant_baseline,
)


def _fixture(name: str) -> Path:
    return FIXTURES / name


def _stage_valid_plan(tmp_path: Path, text: str | None = None) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "AGENTS.md").write_text("# agents\n")
    (tmp_path / ".github").mkdir()
    staged = tmp_path / "tmp" / "superpowers" / "plans"
    staged.mkdir(parents=True)
    plan = staged / "valid-plan.md"
    plan.write_text(text or _fixture("valid-plan.md").read_text())
    return plan


def test_valid_plan_parses_contract_and_has_no_findings(valid_plan: Path) -> None:
    assert parse_execution_manifest(valid_plan.read_text())["schema_version"] == 1
    assert (
        parse_execution_manifest(valid_plan.read_text())["manifest_version"]
        == "execution-manifest/v1"
    )
    assert validate_plan(valid_plan, repo_root=valid_plan.parents[3]) == []


def test_plan_without_execution_manifest_is_blocking(tmp_path: Path) -> None:
    plan = _stage_valid_plan(
        tmp_path,
        "# Plan\n\n## Goal\n\nStrict plan.\n\n"
        "## Repository Preflight\n\n- Baseline Validation: run check.\n"
        "- Recovery Policy: use bounded recovery.\n"
        "- Escalation Conditions: request authority.\n"
        "- User-Facing Report: report evidence.\n\n"
        "## Global Constraints\n\n- No Git mutation.\n\n"
        "## Task 1: Validate\n\n- [ ] Run validation.\n",
    )
    findings = validate_plan(plan, repo_root=tmp_path)
    assert "missing-execution-manifest" in {item.code for item in findings}
    assert any(item.severity == "blocking" for item in findings)


def test_current_plan_requires_control_inventory(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text()
    start = text.index("## Control Inventory")
    end = text.index("\n## ", start + 1)
    plan = _stage_valid_plan(tmp_path, text[:start] + text[end + 1 :])
    assert "missing-control-inventory" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_current_plan_requires_explicit_no_git_constraint(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text().replace("- No Git mutation.\n", "", 1)
    plan = _stage_valid_plan(tmp_path, text)
    assert "missing-no-git-constraint" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_explicit_legacy_or_imported_plan_remains_non_actionable(
    tmp_path: Path,
) -> None:
    plan = _stage_valid_plan(tmp_path, "# Legacy plan\n\n## Goal\n\nNo manifest.\n")
    assert any(item.severity == "blocking" for item in validate_plan(plan, tmp_path))


def test_legacy_plan_is_rejected(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path, "# Legacy plan\n\n## Goal\n\nNo manifest.\n")
    assert any(item.severity == "blocking" for item in validate_plan(plan, tmp_path))


def test_plan_rejects_duplicate_validation_ids(tmp_path: Path) -> None:
    text = (
        _fixture("valid-plan.md")
        .read_text()
        .replace('"id": "diff-check", "command"', '"id": "focused-tests", "command"')
    )
    plan = _stage_valid_plan(tmp_path, text)
    assert "duplicate-validation-id" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_current_plan_rejects_git_mutating_validation_command(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text().replace(
        '"command": "git diff --check"',
        '"command": "git commit -am forbidden"',
        1,
    )
    plan = _stage_valid_plan(tmp_path, text)

    assert "git-mutation-command" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_current_plan_rejects_git_mutation_with_global_option(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text().replace(
        '"command": "git diff --check"',
        '"command": "git -c user.name=bot commit"',
        1,
    )
    plan = _stage_valid_plan(tmp_path, text)

    assert "git-mutation-command" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


def test_current_plan_rejects_git_directory_target(tmp_path: Path) -> None:
    text = _fixture("valid-plan.md").read_text().replace(
        '"path": "tests/fixture/"',
        '"path": ".git/"',
        1,
    )
    plan = _stage_valid_plan(tmp_path, text)

    assert "git-target-prohibited" in {
        item.code for item in validate_plan(plan, tmp_path)
    }


@pytest.mark.parametrize(
    ("needle", "replacement", "message"),
    (
        ('"schema_version": 1', '"schema_version": 2', "schema_version"),
        (
            '"id": "focused-tests", "command"',
            '"id": "focused-tests", "unknown": true, "command"',
            "unknown fields",
        ),
        (
            '"command": "python3 -m pytest -q tests/fixture/"',
            '"command": ""',
            "command",
        ),
        ('"phases": ["final"]', '"phases": ["other"]', "phases"),
        ('"mode": "manifest-only"', '"mode": "unsupported"', "bootstrap.mode"),
    ),
)
def test_execution_manifest_rejects_invalid_fields(
    tmp_path: Path, needle: str, replacement: str, message: str
) -> None:
    plan = _stage_valid_plan(
        tmp_path, _fixture("valid-plan.md").read_text().replace(needle, replacement, 1)
    )
    assert any(message in item.message for item in validate_plan(plan, tmp_path))


def test_execution_manifest_rejects_malformed_json_and_duplicate_blocks(
    tmp_path: Path,
) -> None:
    malformed = _stage_valid_plan(
        tmp_path,
        _fixture("valid-plan.md")
        .read_text()
        .replace('"schema_version": 1', '"schema_version":', 1),
    )
    assert "malformed-execution-manifest" in {
        item.code for item in validate_plan(malformed, tmp_path)
    }
    duplicate = _stage_valid_plan(
        tmp_path / "duplicate",
        _fixture("valid-plan.md").read_text()
        + "\n## Execution Manifest\n\n```json\n{}\n```\n",
    )
    assert "duplicate-execution-manifest" in {
        item.code for item in validate_plan(duplicate, duplicate.parents[3])
    }


def test_compact_output_is_bounded() -> None:
    assert (
        build_compact_payload([Finding("missing-heading", "detail", "blocking")])[
            "status"
        ]
        == "failed"
    )


def test_preflight_cli_valid_fixture(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
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
    manifest = parse_execution_manifest(plan.read_text())
    assert manifest["tasks"][0]["depends_on"] == []


def test_manifest_only_plan_rejects_legacy_execution_contract_projection(
    tmp_path: Path,
) -> None:
    text = _fixture("valid-plan.md").read_text()
    plan = _stage_valid_plan(
        tmp_path,
        text + "\n## Execution Contract\n\n```json\n{}\n```\n",
    )
    codes = {item.code for item in validate_plan(plan, tmp_path)}
    assert "obsolete-execution-contract" in codes


def test_relevant_baseline_detects_path_and_undeclared_dependency_drift() -> None:
    baseline = Baseline(
        head="sha256:head",
        paths={"declared/source.py": "sha256:source", "declared/config.json": "sha256:config"},
    )
    current = Baseline(
        head="sha256:head",
        paths={
            "declared/source.py": "sha256:changed",
            "declared/config.json": "sha256:config",
            "undeclared/dependency.py": "sha256:new",
        },
    )

    findings = validate_relevant_baseline(baseline, current)
    codes = {finding.code for finding in findings}

    assert "relevant-path-drift" in codes
    assert "undeclared-dependency-drift" in codes


def test_relevant_baseline_accepts_clean_declared_paths() -> None:
    baseline = Baseline(
        head="sha256:head",
        paths={"declared/source.py": "sha256:source"},
    )

    assert validate_relevant_baseline(baseline, baseline) == []


def test_ignored_artifact_validates_direct_bytes(tmp_path: Path) -> None:
    artifact = tmp_path / "ignored-plan.md"
    artifact.write_text("retained bytes", encoding="utf-8")
    expected = compute_content_sha256(artifact)

    assert validate_ignored_artifact(artifact, expected) is None
    assert validate_ignored_artifact(artifact, "sha256:" + "0" * 64).code == "ignored-artifact-hash-drift"
    assert validate_ignored_artifact(tmp_path / "missing.md", expected).code == "ignored-artifact-missing"


def test_git_diff_check_coverage_names_git_visible_limit() -> None:
    coverage = git_diff_check_coverage("passed")

    assert coverage["outcome"] == "passed"
    assert coverage["coverage"] == "Git-visible paths only"
    assert "ignored" in coverage["limit"].lower()


def _current_bootstrap_plan() -> Path:
    return FIXTURES / "valid-plan.md"


def _manifest_text(plan: Path) -> str:
    return plan.read_text(encoding="utf-8")


def test_execution_manifest_parses_and_binds_current_bootstrap_projection() -> None:
    plan = _current_bootstrap_plan()
    text = _manifest_text(plan)
    manifest = parse_execution_manifest(text)

    assert manifest["manifest_version"] == "execution-manifest/v1"
    assert validate_manifest_projection(text, manifest) == []


def test_execution_manifest_rejects_duplicate_fenced_blocks(tmp_path: Path) -> None:
    plan = _current_bootstrap_plan()
    text = _manifest_text(plan) + "\n## Execution Manifest\n\n```json\n{}\n```\n"

    with pytest.raises(ExecutionContractError) as exc:
        parse_execution_manifest(text)
    assert exc.value.code == "duplicate-execution-manifest"


def test_execution_manifest_rejects_unknown_fields(tmp_path: Path) -> None:
    plan = _current_bootstrap_plan()
    text = _manifest_text(plan)
    text = text.replace(
        '"manifest_version": "execution-manifest/v1"',
        '"unknown": true,\n  "manifest_version": "execution-manifest/v1"',
        1,
    )

    with pytest.raises(ExecutionContractError) as exc:
        parse_execution_manifest(text)
    assert exc.value.code == "unknown-manifest-field"


def test_content_hash_tracks_editorial_bytes_but_semantic_hash_does_not(
    tmp_path: Path,
) -> None:
    plan = _current_bootstrap_plan()
    original = _manifest_text(plan)
    editorial = original + "\nEditorial note that does not change the manifest.\n"
    original_manifest = parse_execution_manifest(original)
    editorial_manifest = parse_execution_manifest(editorial)

    (tmp_path / "original.md").write_text(original, encoding="utf-8")
    (tmp_path / "editorial.md").write_text(editorial, encoding="utf-8")
    assert compute_content_sha256(tmp_path / "original.md") != compute_content_sha256(
        tmp_path / "editorial.md"
    )
    assert compute_semantic_fingerprint(
        original_manifest
    ) == compute_semantic_fingerprint(editorial_manifest)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda m: m["authority_boundaries"].update({"no_git_mutation": False}),
        lambda m: m["targets"][0].update({"path": "changed/path"}),
            lambda m: m["controls"]["CI-01"]["binding"].append("T8"),
        lambda m: m["validations"][0].update({"command": "make changed"}),
        lambda m: m["tasks"][0].update({"depends_on": ["T8"]}),
        lambda m: m["bootstrap"].update({"mode": "generic"}),
        lambda m: m["handoff"].update({"next_owner": "/other-owner"}),
    ],
)
def test_every_normative_manifest_class_changes_semantic_fingerprint(mutator) -> None:
    manifest = parse_execution_manifest(_manifest_text(_current_bootstrap_plan()))
    changed = json.loads(json.dumps(manifest))
    mutator(changed)

    assert compute_semantic_fingerprint(manifest) != compute_semantic_fingerprint(
        changed
    )


def test_manifest_hashes_are_external_and_self_reference_is_rejected() -> None:
    manifest = parse_execution_manifest(_manifest_text(_current_bootstrap_plan()))
    content_hash = compute_content_sha256(_current_bootstrap_plan())
    semantic_hash = compute_semantic_fingerprint(manifest)
    encoded = canonical_json(manifest)

    assert content_hash.encode() not in encoded
    assert semantic_hash.encode() not in encoded

    polluted = json.loads(encoded)
    polluted["semantic_fingerprint"] = semantic_hash
    with pytest.raises(ExecutionContractError) as exc:
        compute_semantic_fingerprint(polluted)
    assert exc.value.code == "manifest-hash-self-reference"


def test_bootstrap_projection_drift_fails_closed() -> None:
    text = _manifest_text(_current_bootstrap_plan())
    manifest = parse_execution_manifest(text)
    changed = json.loads(json.dumps(manifest))
    changed["controls"].pop("CI-01")

    findings = validate_manifest_projection(text, changed)

    assert any("projection" in finding.lower() for finding in findings)


def _stage_bundle(tmp_path: Path) -> tuple[Path, Path]:
    bundle = tmp_path / "canonical" / "internal-gateway-execute-plans"
    scripts = bundle / "scripts"
    scripts.mkdir(parents=True)
    (bundle / "SKILL.md").write_text("# Executor bundle\n")
    entrypoint = scripts / "plan_execution.py"
    entrypoint.write_text("#!/usr/bin/env python3\n")
    runner = scripts / "run.sh"
    runner.write_text("#!/usr/bin/env bash\n")
    runner.chmod(0o755)
    return bundle, entrypoint


def test_resolve_loaded_bundle_from_external_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = sys.modules["plan_execution"]
    bundle, entrypoint = _stage_bundle(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    monkeypatch.chdir(external)

    assert module.resolve_loaded_bundle(entrypoint) == bundle.resolve()


def test_resolve_loaded_bundle_accepts_canonical_symlink(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    bundle, entrypoint = _stage_bundle(tmp_path)
    loaded = tmp_path / "loaded" / "plan_execution.py"
    loaded.parent.mkdir()
    loaded.symlink_to(entrypoint)

    assert module.resolve_loaded_bundle(loaded) == bundle.resolve()


def test_resolve_loaded_bundle_rejects_stale_symlink(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    loaded = tmp_path / "loaded" / "plan_execution.py"
    loaded.parent.mkdir()
    loaded.symlink_to(tmp_path / "missing" / "plan_execution.py")

    with pytest.raises(module.ExecutionContractError) as exc:
        module.resolve_loaded_bundle(loaded)

    assert exc.value.code == "loaded-bundle-stale"
    assert "next action" in str(exc.value).lower()


def test_bundle_runner_uses_loaded_bundle_from_external_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = sys.modules["plan_execution"]
    bundle, entrypoint = _stage_bundle(tmp_path)
    loaded = tmp_path / "loaded" / "plan_execution.py"
    loaded.parent.mkdir()
    loaded.symlink_to(entrypoint)
    external = tmp_path / "external"
    external.mkdir()
    monkeypatch.chdir(external)

    command = module.bundle_runner_command(
        loaded, ("preflight", "tmp/superpowers/plans/plan.md"), external
    )

    assert command == [
        "bash",
        str(bundle / "scripts" / "run.sh"),
        "preflight",
        "tmp/superpowers/plans/plan.md",
    ]


def test_bundle_runner_does_not_install_dependencies_on_normal_execution(
    tmp_path: Path,
) -> None:
    runtime_bin = tmp_path / "runtime" / "bin"
    runtime_bin.mkdir(parents=True)
    invocation_log = tmp_path / "invocations.log"
    fake_python = runtime_bin / "python"
    fake_python.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"$FAKE_RUNTIME_LOG\"\n"
        "if [[ \"${1:-}\" == \"-m\" && \"${2:-}\" == \"pip\" ]]; then\n"
        "  exit 99\n"
        "fi\n"
    )
    fake_python.chmod(0o755)
    environment = os.environ.copy()
    environment["EXECUTOR_BUNDLE_RUNTIME_DIR"] = str(runtime_bin.parent)
    environment["FAKE_RUNTIME_LOG"] = str(invocation_log)

    result = subprocess.run(
        ["bash", str(SCRIPTS / "run.sh"), "preflight", "ignored-plan.md"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "-m pip" not in invocation_log.read_text()


def test_bundle_runner_requires_explicit_bootstrap_for_missing_runtime(
    tmp_path: Path,
) -> None:
    fake_python = tmp_path / "python"
    fake_python.write_text("#!/usr/bin/env bash\nexit 99\n")
    fake_python.chmod(0o755)
    environment = os.environ.copy()
    environment["PYTHON_BIN"] = str(fake_python)
    environment["EXECUTOR_BUNDLE_RUNTIME_DIR"] = str(tmp_path / "missing-runtime")

    result = subprocess.run(
        ["bash", str(SCRIPTS / "run.sh"), "preflight", "ignored-plan.md"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "not provisioned" in result.stderr


def test_bundle_runner_rejects_stale_loaded_symlink(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    loaded = tmp_path / "loaded" / "plan_execution.py"
    loaded.parent.mkdir()
    loaded.symlink_to(tmp_path / "missing" / "plan_execution.py")

    with pytest.raises(module.ExecutionContractError) as exc:
        module.bundle_runner_command(loaded, (), tmp_path)

    assert exc.value.code == "loaded-bundle-stale"
    assert "next action" in str(exc.value).lower()


def test_dependency_lock_contains_hash_locked_pyyaml() -> None:
    requirements_in = SCRIPTS / "requirements.in"
    requirements_lock = SCRIPTS / "requirements.txt"

    assert "PyYAML" in requirements_in.read_text(encoding="utf-8")
    lock_text = requirements_lock.read_text(encoding="utf-8")
    assert re.search(r"(?im)^pyyaml==[0-9][^\\s]*", lock_text)
    assert re.search(r"(?im)^\s+--hash=sha256:[0-9a-f]{64}", lock_text)


def _passing_verdicts(module):
    return {
        category: module.Verdict(category, "passed", "observed", "none")
        for category in module.VERDICT_CATEGORIES
    }


def test_status_persists_hash_bound_approval_and_delivery_verdicts(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    payload = _status_payload(module, plan)

    assert payload["schema_version"] == 2
    assert payload["approval_evidence"] == {
        "source": "current-conversation",
        "statement": "explicit execution approval",
        "plan_fingerprint": payload["plan_fingerprint"],
        "content_hash": payload["content_hash"],
    }
    assert [item["category"] for item in payload["delivery_verdicts"]] == list(
        module.VERDICT_CATEGORIES
    )

    parsed = module.parse_status_yaml(
        payload, plan.with_name(f"{plan.stem}.DONE.yaml")
    )
    assert parsed.approval_evidence.source == "current-conversation"
    assert {item.category for item in parsed.delivery_verdicts} == set(
        module.VERDICT_CATEGORIES
    )


def test_status_rejects_approval_hash_drift(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    payload = _status_payload(module, plan)
    payload["approval_evidence"]["content_hash"] = "sha256:" + "0" * 64

    with pytest.raises(module.ExecutionContractError) as exc:
        module.parse_status_yaml(payload, plan.with_name(f"{plan.stem}.DONE.yaml"))

    assert exc.value.code == "approval-binding-mismatch"


def test_done_state_rejects_unpassed_delivery_verdicts(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    state_path = plan.with_name(f"{plan.stem}.DONE.yaml")
    payload = _status_payload(module, plan)
    payload["delivery_verdicts"][-1]["outcome"] = "inconclusive"
    payload["delivery_verdicts"][-1]["limit"] = "authority evidence missing"
    with pytest.raises(module.ExecutionContractError) as exc:
        module.write_status_yaml(state_path, payload)
    assert exc.value.code == "done-with-unpassed-delivery-verdicts"
    state_path.write_text(module.yaml.safe_dump(payload), encoding="utf-8")

    findings = module.validate_state(plan, state_path, tmp_path)

    assert "done-with-unpassed-delivery-verdicts" in {
        item.code for item in findings
    }


def _status_payload(
    module,
    plan: Path,
    status: str = "DONE",
    completed: tuple[str, ...] | None = None,
) -> dict[str, object]:
    manifest = module.parse_execution_manifest(plan.read_text())
    task_ids = tuple(module._manifest_task_ids(manifest))
    completed_task_ids = (
        completed
        if completed is not None
        else (task_ids if status == "DONE" else ())
    )
    remaining_task_ids = tuple(
        task_id for task_id in task_ids if task_id not in completed_task_ids
    )
    delivery_verdicts = {
        category: module.Verdict(category, "passed", "observed", "none")
        for category in module.VERDICT_CATEGORIES
    }
    return module.build_status_yaml(
        plan,
        status,
        completed_task_ids,
        remaining_task_ids,
        "focused: native tests passed",
        "No further execution is required." if status == "DONE" else "Continue the approved task loop.",
        approval_source="current-conversation",
        delivery_verdicts=delivery_verdicts,
        repo_root=plan.parents[3],
    )


def test_yaml_status_filename_and_content_status_must_match(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    done_path = plan.with_name(f"{plan.stem}.DONE.yaml")
    payload = _status_payload(module, plan)

    assert module.parse_status_yaml(payload, done_path).status == "DONE"

    with pytest.raises(module.ExecutionContractError) as exc:
        module.parse_status_yaml(payload, plan.with_name(f"{plan.stem}.PARTIAL.yaml"))

    assert exc.value.code == "status-filename-mismatch"


def test_status_discovery_rejects_duplicate_or_ambiguous_siblings(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    module.write_status_yaml(
        plan.with_name(f"{plan.stem}.DONE.yaml"), _status_payload(module, plan, "DONE")
    )
    module.write_status_yaml(
        plan.with_name(f"{plan.stem}.PARTIAL.yaml"),
        _status_payload(module, plan, "PARTIAL"),
    )

    discovery = module.discover_status(plan)
    assert "ambiguous-status-siblings" in {finding.code for finding in discovery.findings}


def test_status_discovery_rejects_interrupted_transition(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    transition = plan.with_name(f"{plan.stem}.DONE.yaml.tmp")
    transition.write_text("incomplete transition\n")

    discovery = module.discover_status(plan)
    assert "interrupted-status-transition" in {
        finding.code for finding in discovery.findings
    }


def test_yaml_state_check_rejects_plan_or_hash_drift(tmp_path: Path) -> None:
    module = sys.modules["plan_execution"]
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_name(f"{plan.stem}.DONE.yaml")
    module.write_status_yaml(state, _status_payload(module, plan))
    plan.write_text(plan.read_text().replace("## Goal\n", "## Goal\nEditorial drift.\n", 1))

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode != 0
    assert "content-hash-drift" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }


def test_legacy_only_plan_has_no_manifest_fallback() -> None:
    with pytest.raises(ExecutionContractError) as exc:
        parse_execution_manifest("# Legacy plan\n\n## Goal\n\nNo manifest.\n")
    assert exc.value.code == "missing-execution-manifest"


def _write_status_yaml(plan: Path, state: Path, status: str = "DONE") -> None:
    module = sys.modules["plan_execution"]
    module.write_status_yaml(state, _status_payload(module, plan, status))


def _run_state_check(
    plan: Path, state: Path, repo_root: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "plan_execution.py"),
            "state-check",
            str(plan),
            str(state),
            "--repo-root",
            str(repo_root),
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
    )


def test_state_check_accepts_current_yaml_status(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_name(f"{plan.stem}.DONE.yaml")
    _write_status_yaml(plan, state)

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "passed"


def test_state_check_rejects_content_hash_drift(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_name(f"{plan.stem}.DONE.yaml")
    _write_status_yaml(plan, state)
    plan.write_text(plan.read_text() + "\nEditorial drift.\n")

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode != 0
    assert "content-hash-drift" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }


@pytest.mark.parametrize("status", ("DONE", "PARTIAL", "BLOCKED"))
def test_state_check_accepts_current_yaml_run_statuses(tmp_path: Path, status: str) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_name(f"{plan.stem}.{status}.yaml")
    _write_status_yaml(plan, state, status)

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode == 0, result.stderr


def test_state_check_rejects_current_yaml_retired_status(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_name(f"{plan.stem}.DONE.yaml")
    payload = _status_payload(sys.modules["plan_execution"], plan, "DONE")
    payload["status"] = "NEEDS_REVIEW"
    state.write_text(sys.modules["plan_execution"].yaml.safe_dump(payload))

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode != 0
    assert "unknown-status" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }


def test_state_check_rejects_non_yaml_status_path(tmp_path: Path) -> None:
    plan = _stage_valid_plan(tmp_path)
    state = plan.with_name(f"{plan.stem}.DONE.txt")
    state.write_text("not a runtime status\n")

    result = _run_state_check(plan, state, tmp_path)

    assert result.returncode != 0
    assert "status-format-required" in {
        item["code"] for item in json.loads(result.stdout)["finding_sample"]
    }


@pytest.mark.parametrize(
    "retired_command",
    ("status-check", "resume-check", "closeout-check", "completion-check"),
)
def test_retired_status_protocol_commands_are_not_exposed(retired_command: str) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "plan_execution.py"), retired_command, "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
