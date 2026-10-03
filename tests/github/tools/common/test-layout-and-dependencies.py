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
FORBIDDEN_TOOL_DIRECTORIES = {"checks", "copilot_tools", "core", "lib", "utils"}


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
    stems = "|".join(re.escape(stem) for stem in legacy_stems)
    suffix = r"(?:\.(?:py|sh))?"
    public_pattern = re.compile(
        rf"(?:\.github/(?:scripts|tools)/|run\.sh\s+|SCRIPTS_RUNNER\)\s+|resolve_script\s+)"
        rf"(?P<stem>{stems}){suffix}(?![A-Za-z0-9_-])"
        rf"|(?:^|[|\n][ \t]*)(?P<case_stem>{stems}){suffix}\)"
    )
    tracked_files = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    occurrences: list[str] = []

    for tracked in tracked_files.split("\0"):
        if not tracked:
            continue
        relative_path = Path(tracked)
        if ignored_directories.intersection(relative_path.parts):
            continue
        if relative_path == Path(".github/CHANGELOG.md"):
            continue
        file_path = REPO_ROOT / relative_path
        if not file_path.is_file():
            continue
        if legacy_aliases.intersection(relative_path.parts):
            occurrences.append(f"{relative_path}: legacy path")

        content = file_path.read_text(encoding="utf-8", errors="replace")
        found = {
            match.group("stem") or match.group("case_stem")
            for match in public_pattern.finditer(content)
        }
        occurrences.extend(
            f"{relative_path}: {stem}" for stem in legacy_stems if stem in found
        )

    assert not occurrences, "legacy command names remain:\n" + "\n".join(occurrences)
