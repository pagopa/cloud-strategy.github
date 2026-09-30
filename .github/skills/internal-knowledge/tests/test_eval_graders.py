"""Offline acceptance tests for the knowledge grader package."""

from __future__ import annotations

import importlib
import json
import shutil
import sys
from pathlib import Path

import pytest

EVALUATION_ROOT = Path(__file__).parent / "evaluation"
BUNDLE_ROOT = Path(__file__).parent.parent
if str(EVALUATION_ROOT) not in sys.path:
    sys.path.insert(0, str(EVALUATION_ROOT))


def grader_package():
    try:
        return importlib.import_module("knowledge_graders")
    except ImportError:
        pytest.fail("knowledge_graders package is missing", pytrace=False)


def core_module():
    try:
        return importlib.import_module("knowledge_graders.core")
    except ImportError:
        pytest.fail("knowledge_graders.core is missing", pytrace=False)


def fixture_paths() -> list[Path]:
    return sorted((EVALUATION_ROOT / "grader-fixtures").glob("*.json"))


def run_payload(profile: object = "author") -> dict[str, object]:
    return {
        "profile": profile,
        "allowlist": ["docs/**"],
        "before": {"docs/guide.md": "old"},
        "after": {"docs/guide.md": "new"},
        "steps": [{"docs/guide.md": "new"}],
        "trace": [{"step": 0, "tool": "write", "kind": "write", "path": "docs/guide.md"}],
        "trace_complete": True,
        "report": "",
        "second_after": None,
    }


def test_load_run_input_rejects_unknown_key() -> None:
    payload = run_payload()
    payload["unexpected"] = True
    with pytest.raises(ValueError):
        core_module().load_run_input(payload)


def test_load_run_input_rejects_bad_profile() -> None:
    with pytest.raises(ValueError):
        core_module().load_run_input(run_payload("unknown"))


def test_load_run_input_rejects_non_string_profile() -> None:
    with pytest.raises(ValueError):
        core_module().load_run_input(run_payload(["audit"]))


def test_load_strict_json_rejects_duplicate_key(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema":"first","schema":"second"}', encoding="utf-8")
    with pytest.raises(ValueError):
        core_module().load_strict_json(path)


def test_load_strict_json_rejects_non_object_top_level(tmp_path: Path) -> None:
    path = tmp_path / "array.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        core_module().load_strict_json(path)


def test_parse_report_accepts_crlf() -> None:
    report = importlib.import_module("knowledge_graders.report")
    lf = "Summary.\nNo changes were made.\nknowledge-report/v1\nmode: audit\nrouter: gap\n"
    crlf = lf.replace("\n", "\r\n")
    assert report.parse_report(crlf) == report.parse_report(lf)


def test_parse_report_ignores_problems_section_after_machine_block() -> None:
    report = importlib.import_module("knowledge_graders.report")
    machine_block = (
        "Summary line.\nSecond line.\nknowledge-report/v1\n"
        "mode: audit\nrouter: gap\n"
    )
    with_problems = (
        machine_block
        + "\n## Problems found\n\n"
        + "| Severity | Problem | Location | Impact | Status |\n"
        + "|---|---|---|---|---|\n"
        + "| medium | Conflicting guidance | `docs/guide.md#L4` | Reader confusion | verified |\n"
    )

    assert report.parse_report(with_problems) == report.parse_report(machine_block)


def test_parse_report_requires_two_prose_lines() -> None:
    report = importlib.import_module("knowledge_graders.report")
    two = "Summary line.\nSecond line.\nknowledge-report/v1\nmode: audit\n"
    assert report.parse_report(two)["mode"] == "audit"
    with pytest.raises(ValueError):
        report.parse_report("Summary.\nknowledge-report/v1\nmode: audit\n")


def test_parse_report_rejects_marker_trailing_space() -> None:
    report = importlib.import_module("knowledge_graders.report")
    with pytest.raises(ValueError):
        report.parse_report("Summary.\nknowledge-report/v1 \nmode: audit\n")


def test_changed_paths_includes_deleted() -> None:
    assert core_module().changed_paths({"gone.md": "old"}, {}) == {"gone.md"}


def test_allowlist_grader_rejects_unapproved_authored_deletion() -> None:
    core = core_module()
    package = grader_package()
    data = run_payload()
    data.update({
        "allowlist": ["docs/README.md"],
        "before": {"docs/unmaintained.md": "authored content"},
        "after": {},
        "steps": [{}],
        "trace": [{"step": 0, "tool": "write", "kind": "write", "path": "docs/unmaintained.md"}],
    })

    verdict = package.core.GRADERS["writes_within_allowlist"](
        core.load_run_input(data), {}
    )

    assert (verdict.status, verdict.code) == ("fail", "write-outside-allowlist")


@pytest.mark.parametrize("status", ["fail", "blocked", "not-run"])
def test_is_green_false_for_nonpass_status(status: str) -> None:
    core = core_module()
    assert not core.is_green([core.Verdict("example", status, "reason", "evidence")])


def test_registry_and_fixture_files_match() -> None:
    package = grader_package()
    registered = set(package.core.GRADERS)
    fixture_names = {path.stem for path in fixture_paths()}
    assert registered == fixture_names


@pytest.mark.parametrize("fixture_path", fixture_paths(), ids=lambda path: path.stem)
def test_grader_fixture_expectations(fixture_path: Path) -> None:
    core = core_module()
    package = grader_package()
    fixture = core.load_strict_json(fixture_path)
    grader_name = fixture["grader"]
    if grader_name == "mermaid_parse" and shutil.which("mmdc") is None:
        pytest.skip("mmdc is unavailable; Mermaid parse fixtures were not executed")
    grader = package.core.GRADERS[grader_name]
    gold = core.load_strict_json(BUNDLE_ROOT / fixture["gold"])
    for item in fixture["good"]:
        verdict = grader(core.load_run_input(item["run"]), gold)
        assert verdict.status == "pass", item["name"]
    for item in fixture["mutants"]:
        verdict = grader(core.load_run_input(item["run"]), gold)
        assert (verdict.status, verdict.code) == (
            item["expected_status"],
            item["expected_code"],
        ), item["name"]


def test_mermaid_parse_not_run_without_mmdc(monkeypatch: pytest.MonkeyPatch) -> None:
    package = grader_package()
    core = package.core
    mermaid = importlib.import_module("knowledge_graders.mermaid")
    fixture = core.load_strict_json(EVALUATION_ROOT / "grader-fixtures/mermaid_parse.json")
    monkeypatch.setattr(mermaid.shutil, "which", lambda _: None)
    run = core.load_run_input(fixture["good"][0]["run"])
    verdict = core.GRADERS["mermaid_parse"](run, {})
    assert (verdict.status, verdict.code) == ("not-run", "mmdc-unavailable")
    assert not core.is_green([verdict])


def test_fixture_json_is_strict_object(tmp_path: Path) -> None:
    path = tmp_path / "object.json"
    path.write_text(json.dumps({"schema": "example"}), encoding="utf-8")
    assert core_module().load_strict_json(path) == {"schema": "example"}


def _eval_inputs() -> tuple[dict, dict, dict]:
    root = EVALUATION_ROOT
    cases = {
        case["id"]: case
        for case in core_module().load_strict_json(root / "evals.json")["cases"]
    }
    bindings = core_module().load_strict_json(root / "bindings.json")["cases"]
    gold = {
        path.stem.removesuffix(".gold"): core_module().load_strict_json(path)
        for path in (root / "gold").glob("*.gold.json")
    }
    return cases, bindings, gold


def test_composed_glossary_binding_accepts_unchanged_fixture() -> None:
    core = core_module()
    package = grader_package()
    _, bindings, gold_by_fixture = _eval_inputs()
    tree = core.load_strict_json(EVALUATION_ROOT / "fixtures/F3.tree.json")["files"]
    case = bindings["C-GLOSSARY-BOLD"]
    gold = gold_by_fixture[case["fixture"]] | case["gold_overrides"]
    run = core.load_run_input({
        **run_payload("protected"), "before": tree, "after": tree,
        "steps": [], "trace": [], "trace_complete": True,
    })
    verdicts = [package.core.GRADERS[name](run, gold) for name in case["graders"]]
    assert all(verdict.status == "pass" for verdict in verdicts), verdicts


def test_owner_link_gold_path_resolves_from_nested_readme_and_deleted_target_fails() -> None:
    package = grader_package()
    core = package.core
    grader = core.GRADERS["readme_links"]
    gold = {"owner_links": [{"source": "services/billing/README.md", "target": "services/api/README.md"}]}
    good_data = run_payload()
    good_data.update({
        "before": {"services/billing/README.md": "", "services/api/README.md": "API"},
        "after": {"services/billing/README.md": "[API](../api/README.md#overview)", "services/api/README.md": "API"},
        "steps": [], "trace": [], "trace_complete": True,
    })
    assert grader(core.load_run_input(good_data), gold).status == "pass"
    deleted = dict(good_data)
    deleted["after"] = {"services/billing/README.md": "[API](../api/README.md#overview)"}
    verdict = grader(core.load_run_input(deleted), gold)
    assert (verdict.status, verdict.code) == ("fail", "broken-link")


def test_incomplete_trace_blocks_process_acceptance_and_final_snapshot_mismatch() -> None:
    core = core_module()
    package = grader_package()
    data = run_payload()
    data.update({"steps": [], "trace_complete": False})
    run = core.load_run_input(data)
    gold = {"protected_paths": ["docs/guide.md"]}
    for name in ("no_transient_writes", "protected_bytes_per_step"):
        assert package.core.GRADERS[name](run, gold).status == "blocked"
    data = run_payload()
    data["steps"] = [{"docs/guide.md": "different"}]
    assert package.core.GRADERS["trace_complete"](core.load_run_input(data), {}).status == "blocked"


def test_generated_write_then_restore_fails_per_step() -> None:
    core = core_module()
    package = grader_package()
    original = {"docs/README.md": "generated"}
    data = run_payload()
    data.update({
        "before": original, "after": original,
        "steps": [{"docs/README.md": "changed"}, original],
        "trace": [
            {"step": 0, "tool": "write", "kind": "write", "path": "docs/README.md"},
            {"step": 1, "tool": "write", "kind": "write", "path": "docs/README.md"},
        ],
    })
    run = core.load_run_input(data)
    verdict = package.core.GRADERS["protected_bytes_per_step"](run, {"protected_paths": ["docs/README.md"]})
    assert (verdict.status, verdict.code) == ("fail", "protected-changed-in-step")


def test_inline_mermaid_labels_are_extracted_and_unicode_target_is_rejected() -> None:
    core = core_module()
    package = grader_package()
    mermaid = importlib.import_module("knowledge_graders.mermaid")
    diagram = "```mermaid\nflowchart TD\naccTitle: Dependencies\naccDescr: API to auth\napi[API] --> auth[Auth]\n```"
    data = run_payload()
    data.update({"before": {}, "after": {"docs/architecture.md": diagram}, "steps": [], "trace": [], "trace_complete": True})
    run = core.load_run_input(data)
    gold = {"diagram_edges": {"docs/architecture.md": [["api", "auth"]]}}
    assert package.core.GRADERS["diagram_relations"](run, gold).status == "pass"
    diagram = diagram.replace("auth[Auth]", "α[Auth]")
    data["after"] = {"docs/architecture.md": diagram}
    assert mermaid._check_block(mermaid.BLOCK.findall(diagram)[0]) == "mermaid-static"


def test_adr_index_update_is_not_validated_as_an_adr_decision() -> None:
    core = core_module()
    package = grader_package()
    data = run_payload()
    data.update({
        "before": {"docs/adr/README.md": "old index"},
        "after": {"docs/adr/README.md": "# Architecture decisions\n\n[ADR](0001-choice.md)"},
        "steps": [], "trace": [], "trace_complete": True,
    })
    assert package.core.GRADERS["adr_format"](core.load_run_input(data), {"adr_dir": "docs/adr"}).status == "pass"


def test_eval_bindings_authorize_requested_targets_and_define_case_constraints() -> None:
    cases, bindings, gold = _eval_inputs()
    for case_id, binding in bindings.items():
        allowlist = binding["allowlist"]
        if "readme_opening" in binding["graders"]:
            for path in binding["gold_overrides"].get("readme_paths", []):
                assert any(_glob_allows(pattern, path) for pattern in allowlist), (case_id, path)
    assert any(_glob_allows(pattern, "README.md") for pattern in bindings["C-HOLD-MERMAID"]["allowlist"])
    split = bindings["C-SPLIT-SIGNAL-ONLY"]["gold_overrides"]
    lifecycle = bindings["C-MERMAID-LIFECYCLE"]["gold_overrides"]
    mixed = bindings["C-SPLIT-MIXED"]["gold_overrides"]
    setup = bindings["C-HOLD-SETUP"]["gold_overrides"]
    assert split["sections"] and split["protected_paths"]
    assert lifecycle["facts"] and lifecycle["diagram_edges"]
    assert mixed == {}
    f6_sections = {section["marker"]: section["dest"] for section in gold["F6"]["sections"]}
    assert f6_sections == {
        "## Procedure": "docs/guides/maintain-ci-ux.md",
        "## Active obligation": "docs/guides/maintain-ci-ux.md",
    }
    assert setup["must_write"] and setup["expected_placements"]
    assert "docs/history/ci-ux-history.md" not in str(gold["F6"]["sections"])


def _bound_verdicts(case_id: str, before: dict[str, str], after: dict[str, str], report: str = ""):
    core = core_module()
    package = grader_package()
    _, bindings, gold_by_fixture = _eval_inputs()
    binding = bindings[case_id]
    run = core.load_run_input({
        **run_payload(binding["profile"]),
        "allowlist": binding["allowlist"],
        "before": before,
        "after": after,
        "steps": [],
        "trace": [],
        "trace_complete": True,
        "report": report,
    })
    gold = gold_by_fixture[binding["fixture"]] | binding["gold_overrides"]
    return [package.core.GRADERS[name](run, gold) for name in binding["graders"]]


def test_composed_split_signal_case_passes_and_rejects_deleted_reference() -> None:
    core = core_module()
    tree = core.load_strict_json(EVALUATION_ROOT / "fixtures/F2.tree.json")["files"]
    assert all(v.status == "pass" for v in _bound_verdicts("C-SPLIT-SIGNAL-ONLY", tree, tree))
    deleted = dict(tree)
    del deleted["docs/reference/api-errors.md"]
    assert any(v.status == "fail" for v in _bound_verdicts("C-SPLIT-SIGNAL-ONLY", tree, deleted))


def test_composed_lifecycle_case_checks_states_and_transitions() -> None:
    core = core_module()
    tree = core.load_strict_json(EVALUATION_ROOT / "fixtures/F2.tree.json")["files"]
    after = dict(tree)
    after["services/billing/README.md"] += (
        "\nBilling moves through draft, active, and retired states.\n\n"
        "```mermaid\nstateDiagram-v2\naccTitle: Billing lifecycle\n"
        "accDescr: Billing moves from draft to active to retired.\n"
        "draft --> active\nactive --> retired\n```\n"
    )
    verdicts = _bound_verdicts("C-MERMAID-LIFECYCLE", tree, after)
    assert all(v.status == "pass" for v in verdicts), verdicts
    after["services/billing/README.md"] = after["services/billing/README.md"].replace("active --> retired\n", "")
    verdicts = _bound_verdicts("C-MERMAID-LIFECYCLE", tree, after)
    assert any(v.code == "critical-omission" for v in verdicts)


def test_composed_mixed_content_and_holdout_setup_cases_have_required_outputs() -> None:
    core = core_module()
    f6 = core.load_strict_json(EVALUATION_ROOT / "fixtures/F6.tree.json")["files"]
    mixed = dict(f6)
    del mixed["docs/ci-ux.md"]
    mixed["docs/guides/maintain-ci-ux.md"] = (
        "# CI and UX guide\n\n## Procedure\nRun the docs checker before opening a pull request.\n\n"
        "## Active obligation\nUpdate the compatibility matrix with each contract change.\n"
    )
    assert "docs/guides/ci-ux-history.md" not in mixed
    assert all(v.status == "pass" for v in _bound_verdicts("C-SPLIT-MIXED", f6, mixed))
    holdout = core.load_strict_json(EVALUATION_ROOT / "fixtures/FH.tree.json")["files"]
    setup = {"docs/index.md": "# Documentation index\n\nRepository guide.\n"}
    setup["README.md"] = "# Delivery system\n\nA guide to the repository.\n"
    for name in ("ingest", "transform", "publish", "jobs"):
        setup[f"docs/domain/{name}/README.md"] = f"# {name.title()}\n\nGuide for {name}.\n"
    report = "Setup complete.\nAll required destinations were written.\nknowledge-report/v1\nmode: setup\n"
    verdicts = _bound_verdicts("C-HOLD-SETUP", holdout, setup, report)
    assert all(v.status == "pass" for v in verdicts), verdicts
    del setup["docs/domain/jobs/README.md"]
    assert any(v.code == "critical-omission" for v in _bound_verdicts("C-HOLD-SETUP", holdout, setup, report))


def _glob_allows(pattern: str, path: str) -> bool:
    from fnmatch import fnmatchcase

    return fnmatchcase(path, pattern) or (
        pattern.endswith("/**") and path.startswith(pattern[:-3] + "/")
    )
