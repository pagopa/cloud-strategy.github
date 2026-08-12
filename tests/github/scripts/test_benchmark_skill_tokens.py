from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").is_file() and (parent / ".github").is_dir()
)
SCRIPT_PATH = REPO_ROOT / ".github/scripts/benchmark_skill_tokens.py"
FIXTURE_PATH = (
    REPO_ROOT / "tests/github/skills/internal-terraform/fixtures/routing-cases.json"
)


def _load_benchmark_module() -> Any:
    spec = importlib.util.spec_from_file_location("benchmark_skill_tokens", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_terraform_benchmark_covers_the_routing_fixture() -> None:
    module = _load_benchmark_module()
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    reports = module.build_terraform_scenario_report(REPO_ROOT)
    report_by_id = {report["scenario"]: report for report in reports}
    fixture_by_id = {scenario["id"]: scenario for scenario in fixture["scenarios"]}

    assert set(report_by_id) == set(fixture_by_id)
    required_fields = {
        "scenario",
        "primary_owner",
        "delegated_owner",
        "loaded_local_references",
        "forbidden_local_references",
        "local_skill_tokens",
        "conditional_reference_tokens",
        "delegated_core_tokens",
        "scenario_proxy_tokens",
    }
    for scenario_id, report in report_by_id.items():
        assert required_fields <= report.keys()
        expected = fixture_by_id[scenario_id]
        assert report["primary_owner"] == expected["primary_owner"]
        assert report["delegated_owner"] == expected["delegated_owner"]
        assert report["loaded_local_references"] == expected["loaded_local_references"]
        assert (
            report["forbidden_local_references"]
            == expected["forbidden_local_references"]
        )


def test_terraform_benchmark_keeps_language_and_operational_owners_distinct() -> None:
    module = _load_benchmark_module()
    reports = {
        report["scenario"]: report
        for report in module.build_terraform_scenario_report(REPO_ROOT)
    }

    assert reports["hcl-only"]["primary_owner"] == "internal-tf"
    assert reports["tfvars-json-only"]["primary_owner"] == "internal-tf"
    assert reports["mixed-adoption"]["primary_owner"] == "internal-terraform"
    assert reports["mixed-adoption"]["delegated_owner"] == "internal-tf"
    assert reports["mixed-adoption"]["delegated_core_tokens"] > 0
    assert reports["hcl-only"]["delegated_core_tokens"] == 0
    assert reports["native-test"]["delegated_core_tokens"] > 0


def test_terraform_benchmark_excludes_forbidden_references_from_the_proxy() -> None:
    module = _load_benchmark_module()
    reports = module.build_terraform_scenario_report(REPO_ROOT)

    for report in reports:
        assert not (
            set(report["loaded_local_references"])
            & set(report["forbidden_local_references"])
        )
        expected_reference_tokens = 0
        owners = [report["primary_owner"]]
        if report["delegated_owner"]:
            owners.append(report["delegated_owner"])
        for reference in report["loaded_local_references"]:
            for owner in owners:
                reference_path = REPO_ROOT / ".github/skills" / owner / reference
                if reference_path.is_file():
                    expected_reference_tokens += module.estimate_tokens(reference_path)
                    break
        assert report["conditional_reference_tokens"] == expected_reference_tokens
        assert report["scenario_proxy_tokens"] == (
            report["local_skill_tokens"]
            + report["conditional_reference_tokens"]
            + report["delegated_core_tokens"]
        )


def test_benchmark_output_labels_static_proxy_and_runtime_gap(capsys: Any) -> None:
    module = _load_benchmark_module()

    assert module.main([str(REPO_ROOT)]) == 0
    output = json.loads(capsys.readouterr().out)

    assert "static proxy" in output["measurement_note"].casefold()
    assert "does not prove runtime loading" in output["measurement_note"].casefold()
    assert "billed-token savings" in output["measurement_note"].casefold()
    assert len(output["terraform_scenarios"]) == 8
