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
SCRIPT_PATH = REPO_ROOT / ".github/scripts/benchmark-skill-tokens.py"
SKILLS_ROOT = REPO_ROOT / ".github/skills"
REQUIRED_TERRAFORM_FIELDS = {
    "scenario",
    "primary_owner",
    "execution_owner",
    "delegated_owner",
    "delegated_core_owner",
    "loaded_local_references",
    "forbidden_local_references",
    "local_skill_tokens",
    "conditional_reference_tokens",
    "delegated_core_tokens",
    "scenario_proxy_tokens",
}


def _load_benchmark_module() -> Any:
    spec = importlib.util.spec_from_file_location("benchmark_skill_tokens", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_terraform_benchmark_reports_live_distinct_owners_per_scenario() -> None:
    module = _load_benchmark_module()
    reports = module.build_terraform_scenario_report(REPO_ROOT)
    scenario_ids = [report["scenario"] for report in reports]

    assert reports
    assert len(scenario_ids) == len(set(scenario_ids))
    for report in reports:
        assert REQUIRED_TERRAFORM_FIELDS <= report.keys()
        owners = [
            report[field]
            for field in ("primary_owner", "execution_owner", "delegated_owner")
            if report[field]
        ]
        assert len(owners) == len(set(owners)), report["scenario"]
        for owner in [*owners, report["delegated_core_owner"]]:
            if owner:
                assert (SKILLS_ROOT / owner / "SKILL.md").is_file(), owner
        assert not set(report["loaded_local_references"]) & set(
            report["forbidden_local_references"]
        )
        if report["delegated_core_owner"]:
            assert report["delegated_core_tokens"] > 0, report["scenario"]
        else:
            assert report["delegated_core_tokens"] == 0, report["scenario"]


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
        if report["execution_owner"]:
            owners.append(report["execution_owner"])
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
    assert output["terraform_scenarios"] == module.build_terraform_scenario_report(
        REPO_ROOT
    )
