from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TOOLS_ROOT = REPO_ROOT / ".github/tools"
CREATOR_ROOT = REPO_ROOT / ".github/skills/internal-skill-creator"
FIXTURES = CREATOR_ROOT / "fixtures/eval-packs"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from skills import rules, scope  # noqa: E402


def _run_git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _init_repo(root: Path) -> str:
    _run_git(root, "init", "-q")
    _run_git(root, "config", "user.email", "eval-pack-tests@example.com")
    _run_git(root, "config", "user.name", "Eval Pack Tests")
    return ""


def _commit(root: Path, message: str) -> str:
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-q", "-m", message)
    return _run_git(root, "rev-parse", "HEAD")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _valid_skill(root: Path, name: str) -> Path:
    skill_dir = root / ".github/skills" / name
    _write(
        skill_dir / "SKILL.md",
        f"---\nname: {name}\ndescription: Use when validating internal skill evaluation packs.\n---\n\n## When to use\n\n- Fixture.\n",
    )
    _write(
        skill_dir / "agents/openai.yaml",
        f"interface:\n  display_name: {name}\n  short_description: Eval pack test fixture\n  default_prompt: Use /{name} for this fixture.\n",
    )
    return skill_dir


def _finding_codes(findings) -> list[str]:
    return sorted(finding.code for finding in findings)


def _fixture_entries():
    return json.loads((FIXTURES / "defective-packs.json").read_text(encoding="utf-8"))


def _fixture_pack_file(tmp_path: Path, entry: dict) -> Path:
    path = tmp_path / f"{entry['name']}.json"
    raw = entry.get("raw_text")
    path.write_text(raw if raw is not None else json.dumps(entry["pack"]), encoding="utf-8")
    return path


def test_host_pack_and_run_verdicts_match_shared_fixtures(tmp_path: Path) -> None:
    valid_path = FIXTURES / "valid-pack.json"
    valid_pack = json.loads(valid_path.read_text(encoding="utf-8"))
    assert _finding_codes(
        rules.validate_eval_pack_file(valid_path, CREATOR_ROOT, "fixture-skill")
    ) == []
    valid_run = FIXTURES / "valid-run-record.json"
    assert _finding_codes(
        rules.validate_eval_run_record(valid_run, CREATOR_ROOT, valid_pack)
    ) == []

    for entry in _fixture_entries():
        if "record" in entry:
            path = tmp_path / f"{entry['name']}.json"
            path.write_text(json.dumps(entry["record"]), encoding="utf-8")
            findings = rules.validate_eval_run_record(path, CREATOR_ROOT, valid_pack)
        else:
            path = _fixture_pack_file(tmp_path, entry)
            findings = rules.validate_eval_pack_file(path, CREATOR_ROOT, "fixture-skill")
        assert _finding_codes(findings) == sorted(entry["expected_codes"]), entry["name"]


def test_creator_pack_passes_host_validation() -> None:
    skill_dir = CREATOR_ROOT
    assert (skill_dir / "tests/evaluation/evals.json").is_file()
    assert rules.validate_eval_pack(skill_dir) == []


def test_full_catalog_validates_only_packs_that_exist(tmp_path: Path) -> None:
    skill_dir = _valid_skill(tmp_path, "internal-example")
    assert not any(code.startswith("eval-") for code in _finding_codes(rules.validate_internal_skill(tmp_path, skill_dir)))

    pack = json.loads((FIXTURES / "valid-pack.json").read_text(encoding="utf-8"))
    pack["skill"] = "internal-example"
    pack["cases"][0]["defective_fixture"] = "SKILL.md"
    pack_path = _write(skill_dir / "tests/evaluation/evals.json", json.dumps(pack))
    assert not any(code.startswith("eval-") for code in _finding_codes(rules.validate_internal_skill(tmp_path, skill_dir)))

    defective = dict(pack)
    defective["unexpected"] = True
    pack_path.write_text(json.dumps(defective), encoding="utf-8")
    assert "eval-pack-schema" in _finding_codes(rules.validate_internal_skill(tmp_path, skill_dir))


def test_scope_finds_new_touched_deleted_and_ignored_bundles(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _init_repo(root)
    existing = root / ".github/skills/internal-existing"
    _write(existing / "SKILL.md", "base\n")
    deleted = root / ".github/skills/internal-deleted"
    _write(deleted / "SKILL.md", "base\n")
    base_ref = _commit(root, "baseline")

    _write(existing / "README.md", "changed\n")
    _write(root / ".github/skills/internal-new/SKILL.md", "new\n")
    (deleted / "SKILL.md").unlink()
    _write(root / ".github/skills/local-example/SKILL.md", "local\n")
    _write(root / ".github/skills/mattpocock-example/SKILL.md", "protected\n")
    changed = (
        ".github/skills/internal-existing/README.md",
        ".github/skills/internal-new/SKILL.md",
        ".github/skills/internal-deleted/SKILL.md",
        ".github/skills/local-example/SKILL.md",
        ".github/skills/mattpocock-example/SKILL.md",
    )
    findings = rules.detect_eval_pack_scope_findings(root, changed, base_ref)
    assert [(item.code, item.severity, item.path) for item in findings] == [
        ("eval-pack-missing-touched-skill", "non-blocking", ".github/skills/internal-existing"),
        ("eval-pack-missing-new-skill", "blocking", ".github/skills/internal-new"),
    ]
    assert scope.path_exists_at_ref(root, base_ref, ".github/skills/internal-existing/SKILL.md")
    assert not scope.path_exists_at_ref(root, "missing-ref", ".github/skills/internal-existing/SKILL.md")


def test_base_ref_controls_new_vs_touched_classification(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _init_repo(root)
    _write(root / ".keep", "base\n")
    empty_ref = _commit(root, "empty baseline")
    new_skill = root / ".github/skills/internal-change/SKILL.md"
    _write(new_skill, "base\n")
    creation_ref = _commit(root, "create skill")
    new_skill.write_text("changed\n", encoding="utf-8")
    changed = (".github/skills/internal-change/SKILL.md",)

    assert [item.code for item in rules.detect_eval_pack_scope_findings(root, changed, empty_ref)] == ["eval-pack-missing-new-skill"]
    assert [item.code for item in rules.detect_eval_pack_scope_findings(root, changed, creation_ref)] == ["eval-pack-missing-touched-skill"]
    assert [item.code for item in rules.detect_eval_pack_scope_findings(root, changed, "missing-ref")] == ["eval-pack-missing-new-skill"]


def test_malformed_pack_is_blocking_and_cli_fails_only_for_blockers(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _init_repo(root)
    _valid_skill(root, "internal-example")
    _commit(root, "create skill")
    changed_file = root / ".github/skills/internal-example/SKILL.md"
    changed_file.write_text("changed\n", encoding="utf-8")
    malformed = _write(root / ".github/skills/internal-example/tests/evaluation/evals.json", '{"schema":"bad"}')

    findings = rules.detect_eval_pack_scope_findings(root, (str(changed_file.relative_to(root)),), "HEAD")
    assert _finding_codes(findings) == ["eval-pack-schema"]
    assert findings[0].severity == "blocking"

    cli = REPO_ROOT / ".github/tools/skills/validate-skill-change-scope.py"
    blocking = subprocess.run(
        [sys.executable, str(cli), "--root", str(root), "--format", "compact"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocking.returncode == 1
    assert json.loads(blocking.stdout)["finding_counts"]["blocking"] >= 1

    malformed.unlink()
    (root / ".github/skills/internal-example/tests/evaluation").rmdir()
    (root / ".github/skills/internal-example/tests").rmdir()
    touched = subprocess.run(
        [sys.executable, str(cli), "--root", str(root), "--format", "compact"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert touched.returncode == 0
    assert json.loads(touched.stdout)["finding_counts"]["notice"] >= 1
