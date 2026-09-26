from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TOOLS_ROOT = REPO_ROOT / ".github/tools"
SCRIPTS_ROOT = REPO_ROOT / ".github/scripts"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

TOOL_ENTRYPOINTS = (
    Path("inventory/build-inventory.py"),
    Path("catalog/validate-catalog.py"),
    Path("catalog/validate-github-catalog.py"),
    Path("skills/validate-internal-skills.py"),
    Path("skills/validate-skill-change-scope.py"),
    Path("tokens/detect-token-risks.py"),
)
EXPECTED_SCRIPT_FILES = {
    "benchmark-skill-tokens.py",
    "graphify-file-change-hook.sh",
    "install-graphify-hooks.sh",
}
IGNORED_SCRIPT_ENTRIES = {".pytest_cache", ".venv", "__pycache__", "graphify-out"}
FORBIDDEN_TOOL_DIRECTORIES = {"checks", "copilot_tools", "core", "lib", "utils"}


def test_scripts_root_contains_only_public_standalone_entrypoints() -> None:
    actual_entries = {
        path.name
        for path in SCRIPTS_ROOT.iterdir()
        if path.name not in IGNORED_SCRIPT_ENTRIES
    }

    assert actual_entries == EXPECTED_SCRIPT_FILES


def test_tool_entrypoints_run_outside_the_repository(tmp_path: Path) -> None:
    failures: list[str] = []

    for entrypoint in TOOL_ENTRYPOINTS:
        result = subprocess.run(
            [sys.executable, str(TOOLS_ROOT / entrypoint), "--help"],
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append(f"{entrypoint.as_posix()}: {result.stderr.strip()}")

    assert not failures, "entrypoints failed outside repository:\n" + "\n".join(
        failures
    )


def test_tool_modules_follow_functional_dependency_graph() -> None:
    allowed = {
        "catalog": {"common", "inventory"},
        "common": set(),
        "inventory": {"common"},
        "skills": {"common"},
        "tokens": {"common"},
    }
    violations: list[str] = []

    assert not FORBIDDEN_TOOL_DIRECTORIES & {
        path.name for path in TOOLS_ROOT.iterdir() if path.is_dir()
    }

    for source_path in sorted(TOOLS_ROOT.glob("*/*.py")):
        source_area = source_path.parent.name
        if source_area not in allowed or "-" in source_path.name:
            continue
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            target_area = (node.module or "").split(".", 1)[0]
            if target_area in allowed and target_area not in allowed[source_area]:
                violations.append(
                    f"{source_path.relative_to(TOOLS_ROOT)}: "
                    f"{source_area} -> {target_area}"
                )

    assert not violations, "invalid package edges: " + ", ".join(violations)


def test_inventory_excludes_script_runtime_and_fixture_paths(tmp_path: Path) -> None:
    from inventory.inventory import collect_inventory_sections

    included_paths = {
        ".github/scripts/check.py",
    }
    excluded_paths = {
        ".github/tools/catalog/rules.py",
        ".github/scripts/.venv/lib/tool.py",
        ".github/scripts/.pytest_cache/cache.py",
        ".github/scripts/__pycache__/module.py",
        ".github/scripts/graphify-out/cache.py",
        ".github/scripts/tests/test_fixture.py",
        ".github/tools/common/__init__.py",
    }

    for relative_path in included_paths | excluded_paths:
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n", encoding="utf-8")

    scripts = set(collect_inventory_sections(tmp_path)["Scripts"])

    assert included_paths <= scripts
    assert not scripts & excluded_paths
    assert not any(
        any(
            part in {".venv", ".pytest_cache", "__pycache__", "graphify-out", "tests"}
            for part in Path(path).parts
        )
        for path in scripts
    )


def test_deep_catalog_mode_matches_audit_command() -> None:
    from catalog.rules import run_consistency_checks
    from common.command import has_severity
    from tokens.rules import detect_token_risks

    merged_command = [
        sys.executable,
        str(REPO_ROOT / ".github/tools/catalog/validate-catalog.py"),
        "--root",
        str(REPO_ROOT),
        "--deep",
        "--format",
        "json",
    ]

    previous_audit_findings = run_consistency_checks(
        REPO_ROOT,
        include_token_risks=True,
        token_risk_detector=detect_token_risks,
    )
    previous_audit_json = [finding.to_dict() for finding in previous_audit_findings]
    previous_audit_returncode = int(has_severity(previous_audit_findings, "blocking"))

    merged = subprocess.run(
        merged_command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert merged.returncode == previous_audit_returncode
    assert json.loads(merged.stdout) == previous_audit_json


def test_legacy_script_commands_are_absent_except_in_changelog() -> None:
    legacy_stems = tuple(
        f"{verb}{suffix}"
        for verb, suffix in (
            ("audit", "_copilot_catalog"),
            ("benchmark", "_skill_tokens"),
            ("build", "_inventory"),
            ("check", "_catalog_consistency"),
            ("detect", "_token_risks"),
            ("github", "_catalog_validation"),
            ("validate", "_internal_skills"),
            ("validate", "_skill_change_scope"),
        )
    )
    legacy_aliases = {
        alias for stem in legacy_stems for alias in (stem, f"{stem}.py", f"{stem}.sh")
    }
    ignored_directories = {
        ".git",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "graphify-out",
        ".superpowers",
        "tmp",
    }
    occurrences: list[str] = []

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(REPO_ROOT)
        if ignored_directories.intersection(relative_path.parts):
            continue
        if relative_path == Path(".github/CHANGELOG.md"):
            continue
        if legacy_aliases.intersection(relative_path.parts):
            occurrences.append(f"{relative_path}: legacy path")

        content = path.read_text(encoding="utf-8", errors="replace")
        for legacy_stem in legacy_stems:
            alias = rf"{re.escape(legacy_stem)}(?:\.(?:py|sh))?"
            public_patterns = (
                rf"(?:\.github/(?:scripts|tools)/|run\.sh\s+|SCRIPTS_RUNNER\)\s+|resolve_script\s+){alias}(?![A-Za-z0-9_-])",
                rf"(?:^|[|\n][ \t]*){alias}\)",
            )
            if any(re.search(pattern, content) for pattern in public_patterns):
                occurrences.append(f"{relative_path}: {legacy_stem}")
        if not content:
            continue

    assert not occurrences, "legacy command names remain:\n" + "\n".join(occurrences)
