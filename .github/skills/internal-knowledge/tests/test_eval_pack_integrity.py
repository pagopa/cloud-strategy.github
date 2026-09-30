"""Integrity and isolation checks for knowledge evaluation fixture data."""

from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path

import pytest

EVALUATION_ROOT = Path(__file__).parent / "evaluation"
BUNDLE_ROOT = Path(__file__).parent.parent
if str(EVALUATION_ROOT) not in sys.path:
    sys.path.insert(0, str(EVALUATION_ROOT))

knowledge_graders = importlib.import_module("knowledge_graders")
runtime_view = importlib.import_module("runtime_view")
load_strict_json = knowledge_graders.core.load_strict_json
assert_gold_unreachable = runtime_view.assert_gold_unreachable
build_runtime_view = runtime_view.build_runtime_view

TREE_FIELDS = {"schema", "id", "description", "files"}
GOLD_FIELDS = {
    "schema",
    "fixture",
    "components",
    "edges",
    "lifecycle_states",
    "protected_paths",
    "generated_paths",
    "adr_dir",
    "ledger",
    "router",
    "expected_placements",
    "sections",
    "must_write",
    "facts",
    "readme_paths",
    "owner_links",
    "diagram_edges",
    "aliases",
    "diagram_triggers",
}


def fixture_ids() -> list[str]:
    return sorted(path.name.removesuffix(".tree.json") for path in (EVALUATION_ROOT / "fixtures").glob("*.tree.json"))


def test_fixture_and_gold_schemas_and_paths_are_valid(tmp_path: Path) -> None:
    for fixture_id in fixture_ids():
        tree_path = EVALUATION_ROOT / "fixtures" / f"{fixture_id}.tree.json"
        gold_path = EVALUATION_ROOT / "gold" / f"{fixture_id}.gold.json"
        tree = load_strict_json(tree_path)
        gold = load_strict_json(gold_path)
        assert set(tree) == TREE_FIELDS
        assert set(gold) == GOLD_FIELDS
        assert tree["schema"] == "knowledge-fixture-tree/v1"
        assert gold["schema"] == "knowledge-fixture-gold/v1"
        assert tree["id"] == gold["fixture"] == fixture_id
        assert all(isinstance(path, str) and isinstance(content, str) for path, content in tree["files"].items())

        tree_paths = set(tree["files"])
        declared = set(gold["must_write"])
        declared.update(gold["expected_placements"].values())
        declared.update(section["dest"] for section in gold["sections"])
        declared.update(fact["path"] for fact in gold["facts"])
        known_paths = tree_paths | declared
        assert all(source in tree_paths for source in gold["expected_placements"])
        assert all(path in known_paths for path in gold["protected_paths"])
        assert all(path in known_paths for path in gold["generated_paths"])
        assert all(path in known_paths for path in gold["readme_paths"])
        assert all(path in known_paths for path in gold["diagram_edges"])
        assert all(link["source"] in known_paths and link["target"] in known_paths for link in gold["owner_links"])
        assert all(trigger["doc"] in known_paths for trigger in gold["diagram_triggers"])
        if gold["ledger"]:
            assert gold["ledger"]["path"] in known_paths
        if gold["router"]:
            assert gold["router"]["path"] in known_paths
        if gold["adr_dir"]:
            assert any(path.startswith(gold["adr_dir"].rstrip("/") + "/") for path in tree_paths)
        assert all(not path.startswith("./") and "\\" not in path and ".." not in path.split("/") for path in tree_paths)

        destination = tmp_path / fixture_id
        build_runtime_view(BUNDLE_ROOT, tree_path, destination)
        assert_gold_unreachable(destination, BUNDLE_ROOT)


def test_fixture_markdown_is_only_stored_inside_json_trees() -> None:
    assert list((EVALUATION_ROOT / "fixtures").rglob("*.md")) == []


def test_load_strict_json_rejects_duplicate_nested_keys(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"files":{"a.md":"one","a.md":"two"}}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_strict_json(path)


def test_fixture_count_is_fixed_for_v0() -> None:
    assert fixture_ids() == ["F1", "F2", "F3", "F6", "FH"]


def test_bindings_and_pack_cases_are_bijective() -> None:
    pack = load_strict_json(EVALUATION_ROOT / "evals.json")
    bindings = load_strict_json(EVALUATION_ROOT / "bindings.json")
    assert set(bindings) == {"schema", "cases"}
    assert bindings["schema"] == "knowledge-eval-bindings/v1"
    pack_cases = {case["id"]: case for case in pack["cases"]}
    assert set(bindings["cases"]) == set(pack_cases)
    for case_id, case in pack_cases.items():
        binding = bindings["cases"][case_id]
        assert set(binding) == {
            "fixture",
            "gold",
            "profile",
            "graders",
            "runs",
            "allowlist",
            "gold_overrides",
        }
        assert binding["fixture"] in fixture_ids()
        assert binding["gold"] == f"tests/evaluation/gold/{binding['fixture']}.gold.json"
        assert binding["profile"] in {"audit", "author", "protected"}
        assert set(binding["graders"]) <= set(knowledge_graders.core.GRADERS)
        assert binding["runs"] >= 1
        assertion_ids = {assertion["id"] for assertion in case["assertions"]}
        assert any(assertion["critical"] for assertion in case["assertions"])
        if case["kind"] == "deterministic":
            assert assertion_ids == set(binding["graders"])
            assert case["defective_fixture"] == f"tests/evaluation/grader-fixtures/{binding['graders'][0]}.json"
        else:
            assert assertion_ids == {"rubric-pass", "rubric-fail"}
            assert binding["graders"] == []
        expected_family = "held-out-downstream" if case["held_out"] else case["id"].split("-")[1].lower()
        assert case["family"] == expected_family
        assert f"tests/evaluation/fixtures/{binding['fixture']}.tree.json" in case["files"]
        assert binding["gold"] in case["files"]


def test_pack_coverage_status_and_holdout_seal() -> None:
    pack = load_strict_json(EVALUATION_ROOT / "evals.json")
    bindings = load_strict_json(EVALUATION_ROOT / "bindings.json")["cases"]
    requirements = {item["id"] for item in pack["requirements"]}
    covered = {req for case in pack["cases"] for req in case["requirement_ids"]}
    assert requirements <= covered
    assert len(pack["requirements"]) == 21
    assert len(pack["cases"]) == 31
    assert all(case["status"] == "not-run" for case in pack["cases"])
    assert not (EVALUATION_ROOT / "runs").exists()
    for case in pack["cases"]:
        is_holdout = case["fixture"] if "fixture" in case else bindings[case["id"]]["fixture"]
        assert (is_holdout == "FH") == case["held_out"]
        if case["held_out"]:
            assert case["family"] == "held-out-downstream"
    queries = pack["triggers"]["queries"]
    assert len(queries) == 20
    assert sum(query["should_trigger"] for query in queries) == 10
    assert sum(query["split"] == "train" for query in queries) == 12
    assert sum(query["split"] == "held-out" for query in queries) == 8
    seal = (EVALUATION_ROOT / "holdout.sha256").read_text(encoding="utf-8").splitlines()
    assert len(seal) == 2
    for line in seal:
        expected, relative = line.split("  ", 1)
        actual = hashlib.sha256((EVALUATION_ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected


def test_grader_fixtures_and_compatibility_matrix_are_complete() -> None:
    pack = load_strict_json(EVALUATION_ROOT / "evals.json")
    case_ids = {case["id"] for case in pack["cases"]}
    grader_files = sorted((EVALUATION_ROOT / "grader-fixtures").glob("*.json"))
    assert {path.stem for path in grader_files} == set(knowledge_graders.core.GRADERS)
    required_mutants = {
        "no-op",
        "critical-omission",
        "false-relation",
        "false-success-claim",
        "transient-write",
        "out-of-scope-write",
    }
    found_mutants: set[str] = set()
    for path in grader_files:
        fixture = load_strict_json(path)
        assert fixture["schema"] == "knowledge-grader-fixture/v1"
        assert fixture["grader"] == path.stem
        assert len(fixture["good"]) >= 1
        assert len(fixture["mutants"]) >= 2
        found_mutants.update(mutant["kind"] for mutant in fixture["mutants"])
    assert required_mutants <= found_mutants

    compatibility = load_strict_json(EVALUATION_ROOT / "compatibility.json")
    assert set(compatibility) == {"schema", "scenarios", "tests"}
    assert compatibility["schema"] == "knowledge-eval-compat/v1"
    scenario_headings = {
        line[4:].strip()
        for line in (BUNDLE_ROOT / "evals/evaluation_scenarios.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("### ")
    }
    test_names = {
        node.name
        for node in ast.walk(ast.parse((BUNDLE_ROOT / "tests/test_bundle_contract.py").read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }
    assert {row["heading"] for row in compatibility["scenarios"]} == scenario_headings
    assert {row["name"] for row in compatibility["tests"]} == test_names
    for row in [*compatibility["scenarios"], *compatibility["tests"]]:
        assert row["case_ids"]
        assert set(row["case_ids"]) <= case_ids
