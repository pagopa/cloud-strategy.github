import ast
from pathlib import Path

import pytest

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


def test_no_script_invokes_argumentless_git_fetch(script_dir: Path) -> None:
    for script in sorted(script_dir.glob("*.py")):
        commands = _extract_subprocess_commands(script)
        violations = _find_argumentless_fetch(commands)
        assert not violations, (
            f"{script.name} invokes argumentless git fetch: {violations}"
        )


def test_no_script_invokes_forbidden_package_managers(script_dir: Path) -> None:
    for script in sorted(script_dir.glob("*.py")):
        commands = _extract_subprocess_commands(script)
        for cmd in commands:
            base = cmd[0] if cmd else ""
            assert base not in _FORBIDDEN_COMMANDS, (
                f"{script.name} invokes forbidden command: {cmd}"
            )


def test_no_script_invokes_git_pull_or_remote_update(script_dir: Path) -> None:
    for script in sorted(script_dir.glob("*.py")):
        commands = _extract_subprocess_commands(script)
        for cmd in commands:
            if not cmd or cmd[0] != "git":
                continue
            if "pull" in cmd:
                pytest.fail(f"{script.name} invokes git pull: {cmd}")
            if len(cmd) >= 3 and cmd[1] == "remote" and cmd[2] == "update":
                pytest.fail(f"{script.name} invokes git remote update: {cmd}")


def _has_git_fetch_literal(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)):
            continue
        values = {
            elt.value
            for elt in node.elts
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        }
        if {"git", "fetch"} <= values:
            return True
    return False


def test_only_source_prepare_core_executes_git_fetch(script_dir: Path) -> None:
    fetch_scripts = [
        script.name
        for script in sorted(script_dir.glob("*.py"))
        if _has_git_fetch_literal(ast.parse(script.read_text(encoding="utf-8")))
    ]

    assert fetch_scripts == ["source_prepare_core.py"], (
        f"Expected only source_prepare_core.py to execute git fetch, "
        f"found: {fetch_scripts}"
    )


def test_audit_does_not_call_prepare_sources(script_dir: Path) -> None:
    source = (script_dir / "sync_external_resources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    audit_functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_audit"
    ]
    assert len(audit_functions) == 1, "sync_external_resources.py must define _audit"
    for node in audit_functions:
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


def test_plan_and_apply_delegate_source_readiness_to_auto_prepare(
    script_dir: Path,
) -> None:
    source = (script_dir / "sync_external_resources.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {
        node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }

    for function_name in ("_plan", "_apply"):
        calls = {
            inner.func.id
            for inner in ast.walk(functions[function_name])
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
        }
        assert "_materialize_candidate_with_auto_prepare" in calls

    auto_prepare_calls = {
        inner.func.id
        for inner in ast.walk(functions["_materialize_candidate_with_auto_prepare"])
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
    }
    assert "prepare_sources" in auto_prepare_calls
