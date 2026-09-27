"""Runtime view isolation tests for fixture repositories."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

EVALUATION_ROOT = Path(__file__).parent / "evaluation"
if str(EVALUATION_ROOT) not in sys.path:
    sys.path.insert(0, str(EVALUATION_ROOT))

runtime_view = importlib.import_module("runtime_view")
assert_gold_unreachable = runtime_view.assert_gold_unreachable
build_runtime_view = runtime_view.build_runtime_view


def make_bundle(tmp_path: Path) -> tuple[Path, Path]:
    bundle = tmp_path / "internal-knowledge"
    (bundle / "references").mkdir(parents=True)
    (bundle / "agents").mkdir()
    (bundle / "evals").mkdir()
    (bundle / "tests" / "evaluation").mkdir(parents=True)
    (bundle / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    (bundle / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (bundle / "agents" / "agent.md").write_text("# Agent\n", encoding="utf-8")
    (bundle / "evals" / "secret.md").write_text("gold eval\n", encoding="utf-8")
    (bundle / "tests" / "evaluation" / "secret.json").write_text(
        '{"gold":"never expose"}\n', encoding="utf-8"
    )
    tree = tmp_path / "fixture.tree.json"
    tree.write_text(
        json.dumps(
            {
                "schema": "knowledge-fixture-tree/v1",
                "id": "F-test",
                "description": "small test tree",
                "files": {"docs/README.md": "# Repo\n", "src/main.py": "print(1)\n"},
            }
        ),
        encoding="utf-8",
    )
    return bundle, tree


def test_runtime_view_contains_only_runtime_and_fixture_files(tmp_path: Path) -> None:
    bundle, tree = make_bundle(tmp_path)
    destination = tmp_path / "view"
    manifest = build_runtime_view(bundle, tree, destination)
    runtime = destination / "skill" / "internal-knowledge"
    workspace = destination / "workspace"

    assert sorted(path.relative_to(runtime).as_posix() for path in runtime.rglob("*")) == [
        "SKILL.md",
        "agents",
        "agents/agent.md",
        "references",
        "references/guide.md",
    ]
    assert (workspace / "docs/README.md").read_text(encoding="utf-8") == "# Repo\n"
    assert (workspace / "src/main.py").is_file()
    assert not any(path.is_symlink() for path in destination.rglob("*"))
    assert not any("tests" in path.parts or "evals" in path.parts for path in destination.rglob("*"))
    assert manifest["skill/internal-knowledge/SKILL.md"] == hashlib.sha256(
        b"# Skill\n"
    ).hexdigest()
    assert all(len(digest) == 64 for digest in manifest.values())


@pytest.mark.parametrize(
    "unsafe_path",
    ["../escape.md", "/absolute.md", "a\\b.md", "a//b.md", "./leading.md"],
)
def test_runtime_view_rejects_unsafe_tree_path(tmp_path: Path, unsafe_path: str) -> None:
    bundle, tree = make_bundle(tmp_path)
    payload = json.loads(tree.read_text(encoding="utf-8"))
    payload["files"] = {unsafe_path: "bad"}
    tree.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        build_runtime_view(bundle, tree, tmp_path / "view")


def test_runtime_view_rejects_destination_inside_bundle(tmp_path: Path) -> None:
    bundle, tree = make_bundle(tmp_path)
    with pytest.raises(ValueError):
        build_runtime_view(bundle, tree, bundle / "tests" / "evaluation" / "view")


def test_runtime_view_rejects_symlink_destination(tmp_path: Path) -> None:
    bundle, tree = make_bundle(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "view-link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError):
        build_runtime_view(bundle, tree, link)


def test_gold_unreachable_rejects_planted_identical_bytes(tmp_path: Path) -> None:
    bundle, tree = make_bundle(tmp_path)
    destination = tmp_path / "view"
    build_runtime_view(bundle, tree, destination)
    planted = destination / "workspace" / "planted.json"
    planted.write_bytes((bundle / "tests/evaluation/secret.json").read_bytes())
    with pytest.raises(AssertionError):
        assert_gold_unreachable(destination, bundle)


def test_gold_unreachable_accepts_clean_runtime_view(tmp_path: Path) -> None:
    bundle, tree = make_bundle(tmp_path)
    destination = tmp_path / "view"
    build_runtime_view(bundle, tree, destination)
    assert_gold_unreachable(destination, bundle)
