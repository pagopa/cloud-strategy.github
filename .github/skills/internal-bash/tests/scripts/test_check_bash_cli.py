from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[2]
CHECKER = BUNDLE / "scripts/check.sh"
FIXTURES = BUNDLE / "fixtures"
VALID_BASH = FIXTURES / "valid/tool.bash"
VALID_SH = FIXTURES / "valid/helper.sh"
SOURCED = FIXTURES / "valid/sourced-helper.sh"
BASH_IN_SH = FIXTURES / "invalid/bash-in-sh.sh"
UNQUOTED = FIXTURES / "invalid/unquoted.bash"
SYNTAX = FIXTURES / "invalid/syntax-error.bash"

REAL_SHELLCHECK = shutil.which("shellcheck")
needs_shellcheck = pytest.mark.skipif(
    REAL_SHELLCHECK is None, reason="shellcheck is not installed"
)


def _link(bin_dir: Path, name: str) -> None:
    target = shutil.which(name)
    if target is not None:
        (bin_dir / name).symlink_to(target)


def _write_tool(bin_dir: Path, name: str, body: str) -> None:
    tool = bin_dir / name
    tool.write_text(body, encoding="utf-8")
    tool.chmod(tool.stat().st_mode | stat.S_IXUSR)


@pytest.fixture
def bin_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "bin"
    directory.mkdir()
    _link(directory, "bash")
    _link(directory, "sh")
    return directory


def run_checker(
    bin_dir: Path, *args: str | Path, **extra_env: str
) -> subprocess.CompletedProcess[str]:
    env = {"PATH": str(bin_dir), "HOME": os.environ.get("HOME", "/")}
    env.update(extra_env)
    return subprocess.run(
        [str(CHECKER), *(str(arg) for arg in args)],
        cwd=BUNDLE,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_checker_is_directly_executable() -> None:
    assert os.access(CHECKER, os.X_OK)
    assert CHECKER.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash\n")


def test_missing_shellcheck_is_actionable(bin_dir: Path) -> None:
    result = run_checker(bin_dir, VALID_BASH)

    assert result.returncode == 2
    assert "shellcheck" in result.stderr
    assert "install" in result.stderr.lower()


def test_missing_input_is_a_usage_failure(bin_dir: Path) -> None:
    _write_tool(bin_dir, "shellcheck", "#!/bin/sh\nexit 0\n")

    result = run_checker(bin_dir)

    assert result.returncode == 2
    assert "usage" in result.stderr.lower()


def test_missing_file_is_a_file_failure(bin_dir: Path) -> None:
    _write_tool(bin_dir, "shellcheck", "#!/bin/sh\nexit 0\n")

    result = run_checker(bin_dir, "does-not-exist.sh")

    assert result.returncode == 2
    assert "not found" in result.stderr.lower()


def test_invalid_dialect_is_a_usage_failure(bin_dir: Path) -> None:
    _write_tool(bin_dir, "shellcheck", "#!/bin/sh\nexit 0\n")

    result = run_checker(bin_dir, "--dialect", "zsh", VALID_BASH)

    assert result.returncode == 2
    assert "dialect" in result.stderr.lower()


def test_file_without_shebang_requires_explicit_dialect(bin_dir: Path) -> None:
    _write_tool(bin_dir, "shellcheck", "#!/bin/sh\nexit 0\n")

    result = run_checker(bin_dir, SOURCED)

    assert result.returncode == 2
    assert "--dialect" in result.stderr


def test_unsupported_interpreter_is_rejected(bin_dir: Path, tmp_path: Path) -> None:
    _write_tool(bin_dir, "shellcheck", "#!/bin/sh\nexit 0\n")
    script = tmp_path / "tool.zsh"
    script.write_text("#!/bin/zsh\nprint ok\n", encoding="utf-8")

    result = run_checker(bin_dir, script)

    assert result.returncode == 2
    assert "unsupported interpreter" in result.stderr.lower()


def test_unexpected_shellcheck_exit_is_normalized_to_two(bin_dir: Path) -> None:
    _write_tool(
        bin_dir,
        "shellcheck",
        '#!/bin/sh\n[ "$1" = --version ] && { echo "version: 0.0.0"; exit 0; }\nexit 3\n',
    )

    result = run_checker(bin_dir, VALID_BASH)

    assert result.returncode == 2
    assert "status 3" in result.stderr


def test_shebang_selects_shellcheck_dialect(bin_dir: Path, tmp_path: Path) -> None:
    log = tmp_path / "args"
    _write_tool(
        bin_dir,
        "shellcheck",
        '#!/bin/sh\n[ "$1" = --version ] && { echo "version: 0.0.0"; exit 0; }\n'
        'printf "%s\\n" "$*" >> "$ARGS_LOG"\nexit 0\n',
    )

    result = run_checker(bin_dir, VALID_BASH, VALID_SH, ARGS_LOG=str(log))

    assert result.returncode == 0, result.stderr
    calls = log.read_text(encoding="utf-8").splitlines()
    assert any("-s bash" in call and "tool.bash" in call for call in calls)
    assert any("-s sh" in call and "helper.sh" in call for call in calls)


@needs_shellcheck
def test_valid_fixtures_pass(bin_dir: Path) -> None:
    _link(bin_dir, "shellcheck")
    _link(bin_dir, "dash")

    result = run_checker(bin_dir, VALID_BASH, VALID_SH)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "summary: passed=2 failed=0" in result.stdout


@needs_shellcheck
def test_explicit_dialect_checks_sourced_helper(bin_dir: Path) -> None:
    _link(bin_dir, "shellcheck")

    result = run_checker(bin_dir, "--dialect", "sh", SOURCED)

    assert result.returncode == 0, result.stdout + result.stderr


@needs_shellcheck
@pytest.mark.parametrize("fixture", [BASH_IN_SH, UNQUOTED, SYNTAX])
def test_defective_fixtures_report_findings(bin_dir: Path, fixture: Path) -> None:
    _link(bin_dir, "shellcheck")
    _link(bin_dir, "dash")

    result = run_checker(bin_dir, fixture)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "failed=1" in result.stdout


@needs_shellcheck
def test_dialect_override_wins_over_shebang(bin_dir: Path) -> None:
    _link(bin_dir, "shellcheck")

    result = run_checker(bin_dir, "--dialect", "bash", BASH_IN_SH)

    assert result.returncode == 0, result.stdout + result.stderr


@needs_shellcheck
def test_posix_check_without_dash_reports_limited_evidence(bin_dir: Path) -> None:
    _link(bin_dir, "shellcheck")
    assert not (bin_dir / "dash").exists()

    result = run_checker(bin_dir, VALID_SH)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "limited" in result.stdout.lower()


@needs_shellcheck
def test_checker_never_executes_target(bin_dir: Path, tmp_path: Path) -> None:
    _link(bin_dir, "shellcheck")
    marker = tmp_path / "executed"
    script = tmp_path / "side-effect.sh"
    script.write_text(f'#!/bin/sh\n: > "{marker}"\n', encoding="utf-8")

    result = run_checker(bin_dir, script)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not marker.exists()


def test_checker_source_has_no_eval() -> None:
    assert "eval" not in CHECKER.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "shebang",
    ["#!/usr/bin/env -S bash -e", "#!/usr/bin/env -i bash", "#!/bin/bash -e"],
)
def test_env_options_and_interpreter_flags_select_bash(
    bin_dir: Path, tmp_path: Path, shebang: str
) -> None:
    log = tmp_path / "args"
    _write_tool(
        bin_dir,
        "shellcheck",
        '#!/bin/sh\n[ "$1" = --version ] && { echo "version: 0.0.0"; exit 0; }\n'
        'printf "%s\\n" "$*" >> "$ARGS_LOG"\nexit 0\n',
    )
    script = tmp_path / "tool"
    script.write_text(f"{shebang}\nprintf '%s\\n' ok\n", encoding="utf-8")

    result = run_checker(bin_dir, script, ARGS_LOG=str(log))

    assert result.returncode == 0, result.stderr
    assert "-s bash" in log.read_text(encoding="utf-8")


def test_missing_posix_interpreter_is_a_dependency_failure(bin_dir: Path) -> None:
    (bin_dir / "sh").unlink()
    _write_tool(bin_dir, "shellcheck", "#!/bin/sh\nexit 0\n")

    result = run_checker(bin_dir, VALID_SH)

    assert result.returncode == 2
    assert "interpreter" in result.stderr.lower()


def test_long_diagnostics_are_bounded(bin_dir: Path) -> None:
    _write_tool(
        bin_dir,
        "shellcheck",
        '#!/bin/sh\n[ "$1" = --version ] && { echo "version: 0.0.0"; exit 0; }\n'
        "head -c 200000 /dev/zero | tr '\\0' x\nprintf '\\n'\n"
        "i=0\nwhile [ $i -lt 300 ]; do printf 'finding %s\\n' $i; i=$((i+1)); done\n"
        "exit 1\n",
    )
    _link(bin_dir, "head")
    _link(bin_dir, "tr")

    result = run_checker(bin_dir, VALID_BASH)

    assert result.returncode == 1
    assert len(result.stdout.encode("utf-8")) < 50_000
    assert "omitted" in result.stdout


@needs_shellcheck
def test_self_test_runs_bundled_fixtures(bin_dir: Path) -> None:
    _link(bin_dir, "shellcheck")
    _link(bin_dir, "dash")

    result = run_checker(bin_dir, "--self-test")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "self-test passed" in result.stdout.lower()
