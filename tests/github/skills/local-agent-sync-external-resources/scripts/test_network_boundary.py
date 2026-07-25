import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
sys.path.insert(0, SCRIPT_DIR.as_posix())


_FORBIDDEN_COMMANDS = {
    "pull",
    "pip",
    "uv",
    "npm",
    "brew",
    "yarn",
    "pnpm",
}


def _extract_subprocess_commands(script: Path) -> list[list[str]]:
    source = script.read_text(encoding="utf-8")
    tree = ast.parse(source)
    commands: list[list[str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        func_name = ""
        if isinstance(func, ast.Attribute):
            func_name = func.attr
        elif isinstance(func, ast.Name):
            func_name = func.id
        if func_name not in ("run", "Popen", "check_output", "check_call"):
            continue

        all_args: list[str] = []
        if node.args:
            first = node.args[0]
            if isinstance(first, ast.List):
                for elt in first.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        all_args.append(elt.value)
            elif isinstance(first, ast.Constant) and isinstance(first.value, str):
                all_args.append(first.value)

        for kw in node.keywords:
            if kw.arg == "args" and isinstance(kw.value, ast.List):
                for elt in kw.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        all_args.append(elt.value)

        if all_args:
            commands.append(all_args)

    return commands


def _find_argumentless_fetch(commands: list[list[str]]) -> list[list[str]]:
    violations: list[list[str]] = []
    for cmd in commands:
        if not cmd:
            continue
        base = cmd[0]
        if base != "git":
            continue
        if "fetch" not in cmd:
            continue
        non_flag_args = [
            a
            for a in cmd[1:]
            if not a.startswith("-")
            and not a.startswith("--")
            and a != "fetch"
            and not a.startswith("+")
        ]
        if not non_flag_args:
            violations.append(cmd)
    return violations


def test_no_script_invokes_argumentless_git_fetch() -> None:
    for script in sorted(SCRIPT_DIR.glob("*.py")):
        commands = _extract_subprocess_commands(script)
        violations = _find_argumentless_fetch(commands)
        assert not violations, (
            f"{script.name} invokes argumentless git fetch: {violations}"
        )


def test_no_script_invokes_forbidden_package_managers() -> None:
    for script in sorted(SCRIPT_DIR.glob("*.py")):
        commands = _extract_subprocess_commands(script)
        for cmd in commands:
            base = cmd[0] if cmd else ""
            assert base not in _FORBIDDEN_COMMANDS, (
                f"{script.name} invokes forbidden command: {cmd}"
            )


def test_no_script_invokes_git_pull_or_remote_update() -> None:
    for script in sorted(SCRIPT_DIR.glob("*.py")):
        commands = _extract_subprocess_commands(script)
        for cmd in commands:
            if not cmd or cmd[0] != "git":
                continue
            if "pull" in cmd:
                pytest.fail(f"{script.name} invokes git pull: {cmd}")
            if len(cmd) >= 3 and cmd[1] == "remote" and cmd[2] == "update":
                pytest.fail(f"{script.name} invokes git remote update: {cmd}")


def test_only_source_prepare_core_executes_git_fetch() -> None:
    fetch_scripts: list[str] = []
    for script in sorted(SCRIPT_DIR.glob("*.py")):
        source = script.read_text(encoding="utf-8")
        if '"fetch"' in source or "'fetch'" in source:
            tree = ast.parse(source)
            has_subprocess = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = getattr(node, "module", "") or ""
                    if "subprocess" in module:
                        has_subprocess = True
                        break
                    for alias in getattr(node, "names", []):
                        if "subprocess" in alias.name:
                            has_subprocess = True
                            break
            if not has_subprocess:
                continue
            has_git_command = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    func_name = ""
                    if isinstance(func, ast.Attribute):
                        func_name = func.attr
                    elif isinstance(func, ast.Name):
                        func_name = func.id
                    if func_name in (
                        "run",
                        "Popen",
                        "check_output",
                        "check_call",
                        "_run_command",
                    ):
                        has_git_command = True
                        break
            if has_git_command:
                fetch_scripts.append(script.name)

    assert fetch_scripts == ["source_prepare_core.py"], (
        f"Expected only source_prepare_core.py to execute git fetch, "
        f"found: {fetch_scripts}"
    )


def test_audit_does_not_call_prepare_sources() -> None:
    source = (SCRIPT_DIR / "sync_external_resources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_audit":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    if (
                        isinstance(inner.func, ast.Name)
                        and inner.func.id == "prepare_sources"
                    ):
                        pytest.fail("_audit calls prepare_sources")
                    if (
                        isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "prepare_sources"
                    ):
                        pytest.fail("_audit calls prepare_sources")


def test_plan_does_not_call_prepare_sources() -> None:
    source = (SCRIPT_DIR / "sync_external_resources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_plan":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    if (
                        isinstance(inner.func, ast.Name)
                        and inner.func.id == "prepare_sources"
                    ):
                        pytest.fail("_plan calls prepare_sources")
                    if (
                        isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "prepare_sources"
                    ):
                        pytest.fail("_plan calls prepare_sources")


def test_apply_does_not_call_prepare_sources() -> None:
    source = (SCRIPT_DIR / "sync_external_resources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_apply":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    if (
                        isinstance(inner.func, ast.Name)
                        and inner.func.id == "prepare_sources"
                    ):
                        pytest.fail("_apply calls prepare_sources")
                    if (
                        isinstance(inner.func, ast.Attribute)
                        and inner.func.attr == "prepare_sources"
                    ):
                        pytest.fail("_apply calls prepare_sources")
