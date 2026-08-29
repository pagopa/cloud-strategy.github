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
PACKAGE_ROOT = REPO_ROOT / ".github/scripts/copilot_tools"
SCRIPTS_ROOT = REPO_ROOT / ".github/scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


def _layer_for(relative_path: Path) -> str | None:
    parts = relative_path.parts
    if relative_path == Path("cli.py"):
        return "cli"
    if parts and parts[0] == "checks":
        return "checks"
    if relative_path == Path("inventory.py"):
        return "inventory"
    if parts and parts[0] == "core":
        return "core"
    return None


def _imported_layer(source_path: Path, node: ast.ImportFrom) -> str | None:
    relative_path = source_path.relative_to(PACKAGE_ROOT)
    current_package = relative_path.parts[:-1]
    module_parts = tuple((node.module or "").split(".")) if node.module else ()

    if node.level:
        package_prefix = (
            current_package[: -(node.level - 1)] if node.level > 1 else current_package
        )
        target_parts = package_prefix + module_parts
    else:
        if not module_parts or module_parts[0] != "copilot_tools":
            return None
        target_parts = module_parts[1:]

    return _layer_for(Path(*target_parts)) if target_parts else _layer_for(Path("."))


def test_copilot_tools_imports_follow_one_way_layers() -> None:
    assert PACKAGE_ROOT.is_dir(), "the layered copilot_tools package must exist"

    allowed = {
        "cli": {"checks", "inventory", "core"},
        "checks": {"inventory", "core"},
        "inventory": {"core"},
        "core": set(),
    }
    violations: list[str] = []

    for source_path in sorted(PACKAGE_ROOT.rglob("*.py")):
        source_layer = _layer_for(source_path.relative_to(PACKAGE_ROOT))
        if source_layer is None:
            continue
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            target_layer = _imported_layer(source_path, node)
            if target_layer is not None and target_layer not in allowed[source_layer]:
                violations.append(
                    f"{source_path.relative_to(PACKAGE_ROOT)}: "
                    f"{source_layer} -> {target_layer}"
                )

    assert not violations, "invalid package edges: " + ", ".join(violations)


def test_inventory_excludes_script_runtime_and_fixture_paths(tmp_path: Path) -> None:
    from copilot_tools.inventory import collect_inventory_sections

    included_paths = {
        ".github/scripts/check.py",
        ".github/scripts/copilot_tools/core.py",
        ".github/scripts/copilot_tools/run.sh",
    }
    excluded_paths = {
        ".github/scripts/.venv/lib/tool.py",
        ".github/scripts/.pytest_cache/cache.py",
        ".github/scripts/__pycache__/module.py",
        ".github/scripts/graphify-out/cache.py",
        ".github/scripts/tests/test_fixture.py",
        ".github/scripts/copilot_tools/__init__.py",
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
    from copilot_tools.checks.catalog import run_consistency_checks
    from copilot_tools.checks.token_risks import detect_token_risks
    from copilot_tools.cli import has_severity

    merged_command = [
        sys.executable,
        str(REPO_ROOT / ".github/scripts/validate-catalog.py"),
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
                rf"(?:\.github/scripts/|run\.sh\s+|SCRIPTS_RUNNER\)\s+|resolve_script\s+){alias}(?![A-Za-z0-9_-])",
                rf"(?:^|[|\n][ \t]*){alias}\)",
            )
            if any(re.search(pattern, content) for pattern in public_patterns):
                occurrences.append(f"{relative_path}: {legacy_stem}")
        if not content:
            continue

    assert not occurrences, "legacy command names remain:\n" + "\n".join(occurrences)
