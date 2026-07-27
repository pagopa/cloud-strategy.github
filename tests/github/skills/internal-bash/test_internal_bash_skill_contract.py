import re
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
BASH = SKILLS_ROOT / "internal-bash"
SCRIPT = SKILLS_ROOT / "internal-bash-script"


def _description(bundle: Path) -> str:
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    return str(yaml.safe_load(text.split("---", 2)[1])["description"])


def _runtime(bundle: Path) -> dict[str, str]:
    payload = yaml.safe_load(
        (bundle / "agents/openai.yaml").read_text(encoding="utf-8")
    )
    return payload["interface"]


def _bash_block(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    section = text.split(f"## {heading}", 1)[1]
    return re.search(r"```(?:bash|sh)\n(.*?)```", section, re.DOTALL).group(1)


def _run_shell(
    tmp_path: Path, interpreter: str, body: str, *args: str
) -> subprocess.CompletedProcess[str]:
    script = tmp_path / "contract.sh"
    script.write_text(body, encoding="utf-8")
    return subprocess.run(
        [interpreter, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_bash_descriptions_separate_lightweight_and_operator_contracts() -> None:
    generic = _description(BASH).lower()
    script = _description(SCRIPT).lower()

    assert "non-operator" in generic
    assert "standalone" in script
    assert "operator-facing" in script


def test_bash_descriptions_separate_dialects_and_work_modes() -> None:
    generic = _description(BASH).lower()
    script = _description(SCRIPT).lower()

    assert "bash" in generic and "posix `sh`" in generic
    assert "embedded" in generic
    assert "sourced" in generic
    assert "non-operator" in generic
    assert "bash" in script and "posix `sh`" in script
    assert "creating or modifying" in script
    assert "standalone" in script
    assert "operator-facing" in script
    assert "reviewing" not in script


def test_review_only_and_narrower_platform_work_have_distinct_owners() -> None:
    generic = (BASH / "SKILL.md").read_text(encoding="utf-8")
    script = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert "/internal-review-code" in generic
    assert "/internal-review-code" in script
    assert "/internal-github-action-composite" in generic
    assert "/internal-github-actions" in generic


def test_bash_script_routes_lightweight_near_misses_without_preloading() -> None:
    text = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert "embedded shell" in text
    assert "non-operator Bash helper" in text
    assert "internal-bash" in text
    assert "load `internal-bash` first" not in text.lower()


def test_bash_script_uses_repository_test_first_contract() -> None:
    text = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")

    assert "Do not add unit tests unless explicitly requested." not in text
    assert "failing focused check before the first implementation edit" in text
    assert "pre-code testability exception" in text


def test_bash_runtime_metadata_names_real_owners() -> None:
    expected = {
        BASH: ("Embedded Bash and POSIX shell safety", "$internal-bash"),
        SCRIPT: ("Standalone Bash and POSIX shell scripts", "$internal-bash-script"),
    }

    for bundle, (short_description, invocation) in expected.items():
        runtime = _runtime(bundle)
        assert runtime["short_description"] == short_description
        assert invocation in runtime["default_prompt"]
        assert "Help with Internal" not in runtime["short_description"]


def test_bash_script_keeps_one_command_check_and_printf_logging() -> None:
    skill = (SCRIPT / "SKILL.md").read_text(encoding="utf-8")
    templates = (SCRIPT / "references/templates.md").read_text(encoding="utf-8")

    assert skill.count("command -v") == 1
    assert "printf 'ℹ️  %s\\n'" in templates
    assert "printf '❌ %s\\n'" in templates
    assert 'echo "ℹ️' not in templates
    assert 'echo "❌' not in templates


def test_minimal_template_rejects_an_option_as_target_value(tmp_path: Path) -> None:
    template = _bash_block(SCRIPT / "references/templates.md", "Bash Minimal Template")

    result = _run_shell(tmp_path, "bash", template, "--target", "--help")

    assert result.returncode != 0
    assert "--target requires a value" in result.stderr


def test_argument_parser_defaults_dry_run_and_rejects_option_values(
    tmp_path: Path,
) -> None:
    parser = _bash_block(
        SCRIPT / "references/templates.md", "Bash Argument Parsing Pattern"
    )
    harness = f"""#!/usr/bin/env bash
set -euo pipefail
log_error() {{ printf '%s\\n' "$*" >&2; }}
usage() {{ :; }}
{parser}
printf 'scope=%s dry_run=%s\\n' "$SCOPE" "$DRY_RUN"
"""

    defaults = _run_shell(tmp_path, "bash", harness)
    invalid = _run_shell(tmp_path, "bash", harness, "--scope", "--dry-run")

    assert defaults.returncode == 0
    assert defaults.stdout == "scope=repo dry_run=false\n"
    assert invalid.returncode != 0
    assert "--scope requires a value" in invalid.stderr


def test_bash_review_examples_avoid_invalid_or_unsafe_positive_patterns() -> None:
    review = (BASH / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    assert "| SH-M07 | Function body longer than 30 lines" not in review
    assert "| SH-M07 | Function mixes parsing, orchestration, and mutation" in review
    assert 'rm -rf "${name}"' not in review
    assert "process_directory() {" in review
    assert 'cd -- "$base_dir"' in review
    assert 'echo "ℹ️ Processed' not in review


def test_bash_review_rules_match_the_declared_conditional_baseline() -> None:
    review = (BASH / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    assert "Repo mandates Bash" not in review
    assert "Repo convention violation" not in review
    assert "Missing `set -euo pipefail`" not in review
    assert "Bash-specific syntax under a POSIX shell shebang" in review


def test_bash_routing_reserves_standalone_sh_files_for_script_owner() -> None:
    generic = (BASH / "SKILL.md").read_text(encoding="utf-8")

    assert "- `.sh` files and Bash snippets" not in generic
    assert "Sourced `.sh` helpers" in generic


def test_bash_skills_classify_the_dialect_before_applying_rules() -> None:
    for bundle in (BASH, SCRIPT):
        text = (bundle / "SKILL.md").read_text(encoding="utf-8")
        assert "Dialect: Bash" in text
        assert "Dialect: POSIX `sh`" in text
        assert "interpreter" in text.lower()
        assert "POSIX baseline" in text


def test_generic_shell_guidance_separates_portable_and_bash_only_rules() -> None:
    generic = (BASH / "SKILL.md").read_text(encoding="utf-8")

    assert "## Portable core" in generic
    assert "## Bash branch" in generic
    assert "## POSIX `sh` branch" in generic
    assert "`[[ ]]`" in generic
    assert "arrays" in generic
    assert "`local`" in generic
    assert "POSIX.1-2024" in generic
    assert "`sh -n <script>.sh`" in generic
    assert "`shellcheck -s sh <script>.sh`" in generic


def test_review_catalog_does_not_treat_bash_extensions_as_posix() -> None:
    review = (BASH / "references/review-anti-patterns.md").read_text(encoding="utf-8")

    assert "Declared dialect" in review
    assert "POSIX `sh`" in review
    assert "`[[ ]]` instead of `[ ]`" not in review
    assert "Bash-specific syntax under a POSIX shell shebang" in review


def test_posix_template_is_posix_syntax_and_rejects_option_values(
    tmp_path: Path,
) -> None:
    template = _bash_block(
        SCRIPT / "references/templates.md", "POSIX sh Minimal Template"
    )

    syntax = subprocess.run(
        ["sh", "-n"],
        input=template,
        check=False,
        capture_output=True,
        text=True,
    )
    invalid = _run_shell(tmp_path, "sh", template, "--target", "--help")

    assert syntax.returncode == 0
    assert invalid.returncode != 0
    assert "--target requires a value" in invalid.stderr
    assert "[[" not in template
    assert "local " not in template
    assert "pipefail" not in template


def test_template_reference_has_explicit_dialect_headings() -> None:
    templates = (SCRIPT / "references/templates.md").read_text(encoding="utf-8")

    for heading in (
        "Bash Minimal Template",
        "POSIX sh Minimal Template",
        "Bash Argument Parsing Pattern",
        "POSIX sh Argument Parsing Pattern",
        "Bash Hardening Helpers",
    ):
        assert f"## {heading}" in templates
