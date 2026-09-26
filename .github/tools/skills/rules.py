from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml
from common.files import read_text
from common.findings import Finding
from common.markdown import split_frontmatter
from common.repository import (
    find_repo_root,
    iter_test_python_files,
    path_exists_at_ref,
)

INLINE_PATH_PATTERN = re.compile(
    r"`("
    r"AGENTS\.md"
    r"|\.github/[A-Za-z0-9._/\-]+"
    r"|\.\./[A-Za-z0-9._/\-]+"
    r"|tmp/[A-Za-z0-9._/\-]+"
    r"|(?:references|scripts|assets|agents)/[A-Za-z0-9._/\-]+"
    r")`"
)
FENCED_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
SHORT_DESCRIPTION_MIN = 25
SHORT_DESCRIPTION_MAX = 64
MAX_SKILL_BODY_LINES = 220
INLINE_TEMPLATE_THRESHOLD = 4
TRIGGER_FIRST_PREFIXES = (
    "Use when",
    "Use only when",
    "Use first when",
    "Use first for",
    "Use this",
    "Use before",
    "When ",
)
ALLOWED_VIRTUAL_PATHS = {
    ".github/copilot-sync.manifest.json",
}
ALLOWED_VIRTUAL_PREFIXES = ("tmp/",)
SKILL_INVOCATION_PATTERN = re.compile(r"(?<![\w-])/(internal|local)-[a-z0-9][a-z0-9-]*")
DOLLAR_SKILL_INVOCATION_PATTERN = re.compile(
    r"(?<![\w-])\$(internal|local)-[a-z0-9][a-z0-9-]*"
)
RAW_SKILL_SOURCE_PATTERN = re.compile(
    r"(?:^|/)\.github/skills/(?:internal|local)-[^/]+/"
    r"(?:SKILL\.md|references/.+\.md|agents/openai\.yaml)$"
)
LEXICAL_METHODS = frozenset({"find", "startswith", "endswith"})
STRUCTURAL_PARSERS = frozenset({"load", "safe_load", "loads", "safe_load_all"})
CHAT_EXCLUSION_MARKERS: tuple[str, ...] = ("appear in chat", "do not emit")
LEGACY_OUTPUT_FIELD_TOKENS: tuple[str, ...] = (
    "Critique",
    "Evidence quality",
    "Fix owner",
    "Expected verification",
    "explicit Blocking",
    "Start with Assessment",
)
PORTABLE_FRONTMATTER_FIELDS = frozenset(
    {"name", "description", "metadata", "license", "compatibility"}
)
INVOCATION_SUGGESTIONS = {
    "unknown-skill-invocation": (
        "Invoke an existing repository-owned skill or keep the identifier non-operational."
    ),
    "cross-skill-dollar-invocation": (
        "Use /<skill-name> for a cross-skill invocation and keep $<skill-name> "
        "for the bundle's own entrypoint."
    ),
}
# Interface text that names no deliverable and survives a copy-paste bundle scaffold.
PLACEHOLDER_INTERFACE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^help with .+ tasks\.?$", re.IGNORECASE),
    re.compile(r"for this task and follow the repository-owned workflow", re.IGNORECASE),
)
EXTERNAL_URL_PATTERN = re.compile(r"https?://\S+")
EVAL_PACK_SCHEMA = "skill-eval-pack/v1"
EVAL_RUN_SCHEMA = "skill-eval-run/v1"
EVAL_PACK_FIELDS = frozenset({"schema", "skill", "requirements", "cases", "triggers"})
EVAL_REQUIREMENT_FIELDS = frozenset({"id", "text", "source"})
EVAL_CASE_FIELDS = frozenset(
    {
        "id",
        "family",
        "kind",
        "requirement_ids",
        "prompt",
        "initial_state",
        "expected_output",
        "files",
        "assertions",
        "forbidden_actions",
        "status",
        "held_out",
    }
)
EVAL_CASE_TEXT_FIELDS = ("family", "prompt", "initial_state", "expected_output")
EVAL_ASSERTION_FIELDS = frozenset({"id", "text", "critical"})
EVAL_QUERY_FIELDS = frozenset({"id", "query", "should_trigger", "split"})
EVAL_RUN_FIELDS = frozenset(
    {"schema", "skill", "date", "host", "model", "configuration", "case_results"}
)
EVAL_RESULT_FIELDS = frozenset({"case_id", "status", "assertions"})
EVAL_VERDICT_FIELDS = frozenset({"id", "passed", "evidence"})
EVAL_CASE_KINDS = frozenset({"deterministic", "rubric"})
EVAL_PACK_STATUSES = frozenset({"generated", "not-run", "blocked"})
EVAL_SPLITS = frozenset({"train", "held-out"})
EVAL_CONFIGURATIONS = frozenset({"with-skill", "baseline-none", "baseline-previous"})
EVAL_RUN_STATUSES = frozenset({"executed", "passed", "failed", "blocked"})
EVAL_TRANSCRIPT_STATUSES = frozenset({"executed", "passed", "failed"})
EVAL_ID_PATTERNS = {
    "requirement": re.compile(r"R-[A-Z0-9-]+"),
    "case": re.compile(r"C-[A-Z0-9-]+"),
    "query": re.compile(r"Q-[A-Z0-9-]+"),
}


class _DuplicateJSONKey(ValueError):
    pass


def _eval_unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJSONKey(key)
        result[key] = value
    return result


def _eval_read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_eval_unique_object)


def _eval_finding(code: str, path: Path | None, message: str) -> Finding:
    return Finding(
        severity="blocking",
        code=code,
        path=path.as_posix() if path is not None else "",
        message=message,
        suggestion="Correct the eval pack or run record to match Schema v1.",
    )


def _eval_fields(value: object, required: frozenset[str], optional: frozenset[str] = frozenset()) -> bool:
    return isinstance(value, dict) and required <= value.keys() and value.keys() <= required | optional


def _eval_nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _eval_one_of(value: object, allowed: Iterable[str]) -> bool:
    return isinstance(value, str) and value in allowed


def _eval_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _eval_safe_file(bundle_root: Path, value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    try:
        root = bundle_root.resolve(strict=True)
        resolved = (root / candidate).resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return False
    return resolved.is_file()


def _validate_eval_pack_data(
    pack: object, bundle_root: Path, skill_name: str, source: Path | None
) -> list[Finding]:
    if not _eval_fields(pack, EVAL_PACK_FIELDS) or pack["schema"] != EVAL_PACK_SCHEMA or pack["skill"] != skill_name:
        return [_eval_finding("eval-pack-schema", source, "Pack fields, schema, or skill name are invalid.")]
    requirements, cases, triggers = pack["requirements"], pack["cases"], pack["triggers"]
    if not isinstance(requirements, list) or not requirements or not isinstance(cases, list) or not cases:
        return [_eval_finding("eval-pack-schema", source, "Requirements and cases must be non-empty lists.")]
    if not _eval_fields(triggers, frozenset({"queries"})) or not isinstance(triggers["queries"], list):
        return [_eval_finding("eval-pack-schema", source, "Triggers must contain a queries list.")]

    findings: list[Finding] = []
    all_ids: set[str] = set()
    requirement_ids: set[str] = set()
    covered: set[str] = set()

    def add_id(value: object, category: str) -> bool:
        if not isinstance(value, str) or not EVAL_ID_PATTERNS[category].fullmatch(value):
            findings.append(_eval_finding("eval-pack-schema", source, f"Invalid {category} identifier: {value!r}"))
            return False
        if value in all_ids:
            findings.append(_eval_finding("eval-pack-duplicate-id", source, f"Duplicate identifier: {value}"))
            return False
        all_ids.add(value)
        return True

    for item in requirements:
        if not _eval_fields(item, EVAL_REQUIREMENT_FIELDS) or not all(
            _eval_nonempty(item[key]) for key in EVAL_REQUIREMENT_FIELDS
        ):
            findings.append(_eval_finding("eval-pack-schema", source, "Requirement fields are invalid."))
            continue
        if add_id(item["id"], "requirement"):
            requirement_ids.add(item["id"])

    for case in cases:
        kind = case.get("kind") if isinstance(case, dict) else None
        optional = frozenset({"defective_fixture"} if kind == "deterministic" else {"rubric"})
        if not _eval_one_of(kind, EVAL_CASE_KINDS) or not _eval_fields(case, EVAL_CASE_FIELDS, optional):
            findings.append(_eval_finding("eval-pack-schema", source, "Case fields or kind are invalid."))
            continue
        add_id(case["id"], "case")
        if not all(_eval_nonempty(case[key]) for key in EVAL_CASE_TEXT_FIELDS):
            findings.append(_eval_finding("eval-pack-schema", source, "Case text values must be non-empty."))
        references = case["requirement_ids"]
        if not isinstance(references, list) or not references:
            findings.append(_eval_finding("eval-pack-schema", source, "Cases need requirement IDs."))
        else:
            for ref in references:
                if _eval_one_of(ref, requirement_ids):
                    covered.add(ref)
                else:
                    findings.append(_eval_finding("eval-pack-unresolved-requirement", source, f"Unknown requirement: {ref!r}"))
        if not isinstance(case["files"], list) or not all(_eval_safe_file(bundle_root, item) for item in case["files"]):
            findings.append(_eval_finding("eval-pack-unsafe-path", source, "Case has an unsafe or missing file path."))
        assertions = case["assertions"]
        if not isinstance(assertions, list) or not assertions:
            findings.append(_eval_finding("eval-pack-schema", source, "Cases need assertions."))
        else:
            assertion_ids: set[str] = set()
            for assertion in assertions:
                if (
                    not _eval_fields(assertion, EVAL_ASSERTION_FIELDS)
                    or not _eval_nonempty(assertion["id"])
                    or not _eval_nonempty(assertion["text"])
                    or not isinstance(assertion["critical"], bool)
                ):
                    findings.append(_eval_finding("eval-pack-schema", source, "Assertion fields are invalid."))
                elif assertion["id"] in assertion_ids:
                    findings.append(_eval_finding("eval-pack-duplicate-id", source, f"Duplicate assertion ID: {assertion['id']}"))
                else:
                    assertion_ids.add(assertion["id"])
        if not isinstance(case["forbidden_actions"], list) or not all(
            _eval_nonempty(item) for item in case["forbidden_actions"]
        ):
            findings.append(_eval_finding("eval-pack-schema", source, "Forbidden actions must be non-empty strings."))
        if not _eval_one_of(case["status"], EVAL_PACK_STATUSES):
            findings.append(_eval_finding("eval-pack-invalid-status", source, "Case evidence status is invalid."))
        if not isinstance(case["held_out"], bool):
            findings.append(_eval_finding("eval-pack-schema", source, "held_out must be boolean."))
        if kind == "deterministic":
            if "defective_fixture" not in case:
                findings.append(_eval_finding("eval-pack-missing-defective-fixture", source, "Deterministic case has no defective fixture."))
            elif not _eval_safe_file(bundle_root, case["defective_fixture"]):
                findings.append(_eval_finding("eval-pack-unsafe-path", source, "Defective fixture is unsafe or missing."))
        elif "rubric" not in case:
            findings.append(_eval_finding("eval-pack-missing-rubric", source, "Rubric case has no rubric."))
        elif not _eval_fields(case["rubric"], frozenset({"pass", "fail"})) or not all(
            isinstance(case["rubric"][key], list)
            and case["rubric"][key]
            and all(_eval_nonempty(anchor) for anchor in case["rubric"][key])
            for key in ("pass", "fail")
        ):
            findings.append(_eval_finding("eval-pack-missing-rubric", source, "Rubric needs pass and fail anchors."))

    if requirement_ids - covered:
        findings.append(_eval_finding("eval-pack-uncovered-requirement", source, "One or more requirements have no case coverage."))

    polarities: set[bool] = set()
    splits: set[str] = set()
    for query in triggers["queries"]:
        if (
            not _eval_fields(query, EVAL_QUERY_FIELDS, frozenset({"competing_owner"}))
            or not _eval_nonempty(query["query"])
            or not isinstance(query["should_trigger"], bool)
            or not _eval_one_of(query["split"], EVAL_SPLITS)
        ):
            findings.append(_eval_finding("eval-pack-trigger-coverage", source, "Trigger fields are invalid."))
            continue
        if add_id(query["id"], "query"):
            polarities.add(query["should_trigger"])
            splits.add(query["split"])
        if "competing_owner" in query and not _eval_nonempty(query["competing_owner"]):
            findings.append(_eval_finding("eval-pack-schema", source, "competing_owner must be non-empty when present."))
    if polarities != {True, False} or splits != set(EVAL_SPLITS):
        findings.append(_eval_finding("eval-pack-trigger-coverage", source, "Triggers need both polarities and both splits."))
    return findings


def validate_eval_pack_file(pack_path: Path, bundle_root: Path, skill_name: str) -> list[Finding]:
    try:
        pack = _eval_read_json(pack_path)
    except (OSError, UnicodeError, json.JSONDecodeError, _DuplicateJSONKey) as error:
        return [_eval_finding("eval-pack-invalid-json", pack_path, f"Pack is not strict JSON: {error}")]
    return _validate_eval_pack_data(pack, bundle_root, skill_name, pack_path)


def validate_eval_run_record(record_path: Path, pack: dict[str, object]) -> list[Finding]:
    try:
        record = _eval_read_json(record_path)
    except (OSError, UnicodeError, json.JSONDecodeError, _DuplicateJSONKey) as error:
        return [_eval_finding("eval-run-unbacked-result", record_path, f"Run record is not strict JSON: {error}")]
    if (
        not _eval_fields(record, EVAL_RUN_FIELDS)
        or record["schema"] != EVAL_RUN_SCHEMA
        or record["skill"] != pack.get("skill")
        or not _eval_iso_date(record["date"])
        or not _eval_nonempty(record["host"])
        or not _eval_nonempty(record["model"])
        or not _eval_one_of(record["configuration"], EVAL_CONFIGURATIONS)
        or not isinstance(record["case_results"], list)
    ):
        return [_eval_finding("eval-run-unbacked-result", record_path, "Run metadata or fields are invalid.")]
    cases = {
        case["id"]: case
        for case in pack.get("cases", [])
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }
    findings: list[Finding] = []
    seen: set[str] = set()
    for result in record["case_results"]:
        if not _eval_fields(result, EVAL_RESULT_FIELDS, frozenset({"transcript_ref"})):
            findings.append(_eval_finding("eval-run-unbacked-result", record_path, "Run case result fields are invalid."))
            continue
        case_id, status = result["case_id"], result["status"]
        if not _eval_one_of(case_id, cases) or not _eval_one_of(status, EVAL_RUN_STATUSES):
            findings.append(_eval_finding("eval-run-unbacked-result", record_path, "Run result is not backed by a pack case."))
            continue
        if case_id in seen:
            findings.append(_eval_finding("eval-run-unbacked-result", record_path, f"Duplicate run result for {case_id}."))
            continue
        seen.add(case_id)
        if status in EVAL_TRANSCRIPT_STATUSES and not _eval_nonempty(result.get("transcript_ref")):
            findings.append(_eval_finding("eval-run-unbacked-result", record_path, "Run result has no transcript reference."))
        declared = {
            item["id"]: item
            for item in cases[case_id].get("assertions", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        verdicts = result["assertions"]
        if not isinstance(verdicts, list) or not all(
            _eval_fields(item, EVAL_VERDICT_FIELDS)
            and isinstance(item["id"], str)
            and isinstance(item["passed"], bool)
            and isinstance(item["evidence"], str)
            for item in verdicts
        ):
            findings.append(_eval_finding("eval-run-assertion-mismatch", record_path, "Run assertion fields are invalid."))
            continue
        ids = [item["id"] for item in verdicts]
        if len(ids) != len(set(ids)) or set(ids) != set(declared):
            findings.append(_eval_finding("eval-run-assertion-mismatch", record_path, "Run assertion IDs do not match the case."))
            continue
        if status == "passed" and not all(item["passed"] and _eval_nonempty(item["evidence"]) for item in verdicts):
            findings.append(_eval_finding("eval-run-unbacked-result", record_path, "Passed run is missing passing assertion evidence."))
        if status == "executed" and any(
            declared[item["id"]].get("critical") is True and not item["passed"] for item in verdicts
        ):
            findings.append(_eval_finding("eval-run-unbacked-result", record_path, "A failed critical assertion requires status failed."))
    return findings


def validate_eval_pack(skill_dir: Path) -> list[Finding]:
    pack_path = skill_dir / "tests/evaluation/evals.json"
    if not pack_path.exists():
        return []
    try:
        pack = _eval_read_json(pack_path)
    except (OSError, UnicodeError, json.JSONDecodeError, _DuplicateJSONKey) as error:
        return [_eval_finding("eval-pack-invalid-json", pack_path, f"Pack is not strict JSON: {error}")]
    findings = _validate_eval_pack_data(pack, skill_dir, skill_dir.name, pack_path)
    if findings:
        return findings
    run_dir = skill_dir / "tests/evaluation/runs"
    if run_dir.is_dir():
        for record_path in sorted(run_dir.glob("*.json")):
            findings.extend(validate_eval_run_record(record_path, pack))
    return findings


def detect_eval_pack_scope_findings(
    root: Path, changed_paths: Iterable[str], base_ref: str | None
) -> list[Finding]:
    """Require packs for changed internal skills, blocking newly added gaps."""
    bundles = {
        parts[2]
        for value in changed_paths
        if (parts := value.split("/"))[:2] == [".github", "skills"]
        and len(parts) >= 4
        and parts[2].startswith("internal-")
    }
    findings: list[Finding] = []
    reference = base_ref or "HEAD"
    for name in sorted(bundles):
        skill_dir = root / ".github" / "skills" / name
        if not (skill_dir / "SKILL.md").is_file():
            continue
        if (skill_dir / "tests/evaluation/evals.json").exists():
            findings.extend(validate_eval_pack(skill_dir))
            continue
        existed = path_exists_at_ref(root, reference, f".github/skills/{name}/SKILL.md")
        findings.append(
            Finding(
                severity="non-blocking" if existed else "blocking",
                code="eval-pack-missing-touched-skill" if existed else "eval-pack-missing-new-skill",
                path=f".github/skills/{name}",
                message=(
                    "Touched internal skill does not have an eval pack."
                    if existed
                    else "New internal skill does not have an eval pack."
                ),
                suggestion="Add tests/evaluation/evals.json for this internal skill.",
            )
        )
    return findings


def _find_repo_root(start: Path) -> Path:
    return find_repo_root(
        start,
        lambda candidate: (
            (candidate / ".github").is_dir() or (candidate / ".git").exists()
        ),
    )


@dataclass(frozen=True)
class _Taint:
    raw: bool = False


class _SkillProseTaintAnalyzer:
    def __init__(self, root: Path, source_path: Path, tree: ast.AST) -> None:
        self.root = root
        self.source_path = source_path
        self.tree = tree
        self.path_aliases: set[str] = set()
        self.path_values: dict[str, str] = {}
        self.module_taint: dict[str, bool] = {}
        self.functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.function_cache: dict[str, bool] = {}
        self.function_stack: set[str] = set()
        self.findings: list[Finding] = []

    def run(self) -> list[Finding]:
        if not isinstance(self.tree, ast.Module):
            return []
        for statement in self.tree.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[statement.name] = statement
        self._collect_module_taint()
        self._scan_block(self.tree.body, dict(self.module_taint))
        return self.findings

    def _collect_module_taint(self) -> None:
        changed = True
        while changed:
            changed = False
            environment = dict(self.module_taint)
            for statement in self.tree.body:
                if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                    value = statement.value
                    if value is None:
                        continue
                    taint = self._expr_tainted(value, environment)
                    for name in self._assigned_names(statement):
                        if taint and not self.module_taint.get(name, False):
                            self.module_taint[name] = True
                            changed = True
                        if self._is_raw_path_expression(value):
                            if name not in self.path_aliases:
                                self.path_aliases.add(name)
                                changed = True
                        literal = self._path_literal(value)
                        if (
                            literal is not None
                            and self.path_values.get(name) != literal
                        ):
                            self.path_values[name] = literal
                            changed = True
                    for name in self._assigned_names(statement):
                        environment[name] = taint

    def _scan_block(
        self, statements: list[ast.stmt], environment: dict[str, bool]
    ) -> None:
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._scan_function(statement, environment)
                continue
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                value = statement.value
                if value is not None:
                    taint = self._expr_tainted(value, environment)
                    for name in self._assigned_names(statement):
                        environment[name] = taint
                        if self._is_raw_path_expression(value):
                            self.path_aliases.add(name)
                        literal = self._path_literal(value)
                        if literal is not None:
                            self.path_values[name] = literal
                continue
            if isinstance(statement, ast.Assert) and self._contains_lexical_taint(
                statement.test, environment
            ):
                self._add_finding(statement.lineno)
                continue
            if isinstance(statement, (ast.If, ast.For, ast.AsyncFor, ast.While)):
                branches = [statement.body, statement.orelse]
                for branch in branches:
                    self._scan_block(branch, dict(environment))

    def _scan_function(
        self,
        function: ast.FunctionDef | ast.AsyncFunctionDef,
        outer_environment: dict[str, bool],
    ) -> None:
        environment = dict(outer_environment)
        self._scan_block(function.body, environment)

    def _add_finding(self, line: int) -> None:
        self.findings.append(
            Finding(
                severity="blocking",
                code="skill-prose-lexical-assertion",
                path=f"{self.source_path.as_posix()}:{line}",
                message="Test assertion compares or lexically searches raw skill prose.",
                suggestion=(
                    "Use parsed structure, an executable consumer, a public protocol "
                    "validator, or a concrete evaluation case."
                ),
            )
        )

    def _function_returns_tainted(self, name: str) -> bool:
        if name in self.function_cache:
            return self.function_cache[name]
        if name in self.function_stack:
            return False
        function = self.functions.get(name)
        if function is None:
            return False
        self.function_stack.add(name)
        environment = dict(self.module_taint)
        result = False
        for statement in function.body:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                value = statement.value
                if value is not None:
                    taint = self._expr_tainted(value, environment)
                    for assigned_name in self._assigned_names(statement):
                        environment[assigned_name] = taint
            elif isinstance(statement, ast.Return) and statement.value is not None:
                result = result or self._expr_tainted(statement.value, environment)
        self.function_stack.remove(name)
        self.function_cache[name] = result
        return result

    def _expr_tainted(self, node: ast.AST, environment: dict[str, bool]) -> bool:
        if isinstance(node, ast.Name):
            return environment.get(node.id, False)
        if isinstance(node, ast.Attribute):
            return False
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in STRUCTURAL_PARSERS:
                    return False
                if node.func.id in self.functions:
                    return self._function_returns_tainted(node.func.id)
            if isinstance(node.func, ast.Attribute):
                receiver = node.func.value
                if node.func.attr == "read_text" and self._is_raw_path_expression(
                    receiver
                ):
                    return True
                if node.func.attr in STRUCTURAL_PARSERS and isinstance(
                    receiver, ast.Name
                ):
                    return False
                if self._expr_tainted(receiver, environment):
                    return True
                if node.func.attr == "join":
                    return any(
                        self._expr_tainted(argument, environment)
                        for argument in node.args
                    )
            return any(
                self._expr_tainted(argument, environment) for argument in node.args
            )
        if isinstance(node, ast.Compare):
            return self._expr_tainted(node.left, environment) or any(
                self._expr_tainted(comparator, environment)
                for comparator in node.comparators
            )
        if isinstance(node, ast.BoolOp):
            return any(self._expr_tainted(value, environment) for value in node.values)
        if isinstance(node, ast.UnaryOp):
            return self._expr_tainted(node.operand, environment)
        if isinstance(node, ast.Subscript):
            return self._expr_tainted(node.value, environment)
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return any(
                self._expr_tainted(element, environment) for element in node.elts
            )
        if isinstance(node, ast.Dict):
            return any(
                self._expr_tainted(element, environment)
                for element in (*node.keys, *node.values)
                if element is not None
            )
        if isinstance(node, ast.GeneratorExp):
            return self._expr_tainted(node.elt, environment) or any(
                self._expr_tainted(generator.iter, environment)
                or any(
                    self._expr_tainted(condition, environment)
                    for condition in generator.ifs
                )
                for generator in node.generators
            )
        return False

    def _contains_lexical_taint(
        self, node: ast.AST, environment: dict[str, bool]
    ) -> bool:
        if isinstance(node, ast.Compare):
            return self._expr_tainted(node, environment)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in LEXICAL_METHODS and self._expr_tainted(
                node.func.value, environment
            ):
                return True
        return any(
            self._contains_lexical_taint(child, environment)
            for child in ast.iter_child_nodes(node)
        )

    def _assigned_names(self, statement: ast.Assign | ast.AnnAssign) -> list[str]:
        targets = (
            statement.targets
            if isinstance(statement, ast.Assign)
            else [statement.target]
        )
        return [target.id for target in targets if isinstance(target, ast.Name)]

    def _is_raw_path_expression(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in self.path_aliases
        literal = self._path_literal(node)
        if literal is None:
            return False
        normalized = literal.replace("\\", "/").lstrip("/")
        return normalized == "INTERNAL_CONTRACT.md" or bool(
            RAW_SKILL_SOURCE_PATTERN.search(normalized)
        )

    def _path_literal(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            if node.id == "REPO_ROOT":
                return ""
            if node.id == "SKILLS_ROOT":
                return ".github/skills"
            return self.path_values.get(node.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "Path" and node.args:
                return self._path_literal(node.args[0])
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left = self._path_literal(node.left)
            right = self._path_literal(node.right)
            if left is not None and right is not None:
                return f"{left}/{right}"
        return None


def detect_skill_prose_assertion_findings(root: Path) -> list[Finding]:
    repo_root = _find_repo_root(root)
    findings: list[Finding] = []
    for source_path in iter_test_python_files(repo_root):
        try:
            tree = ast.parse(read_text(source_path), filename=source_path.as_posix())
        except (OSError, SyntaxError):
            continue
        findings.extend(_SkillProseTaintAnalyzer(repo_root, source_path, tree).run())
    return findings


def _skill_invocation_sources(skill_dir: Path) -> list[Path]:
    sources = [skill_dir / "SKILL.md"]
    references = skill_dir / "references"
    if references.exists():
        sources.extend(sorted(references.rglob("*.md")))
    metadata = skill_dir / "agents/openai.yaml"
    if metadata.exists():
        sources.append(metadata)
    return sources


def _repo_owned_skill_dirs(repo_root: Path) -> dict[str, Path]:
    skills_root = repo_root / ".github" / "skills"
    if not skills_root.is_dir():
        return {}
    return {
        path.name: path
        for path in sorted(skills_root.iterdir())
        if path.is_dir() and path.name.startswith(("internal-", "local-"))
    }


def _all_skill_dirs(repo_root: Path) -> dict[str, Path]:
    skills_root = repo_root / ".github" / "skills"
    if not skills_root.is_dir():
        return {}
    return {
        path.name: path
        for path in sorted(skills_root.iterdir())
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def _named_skill_invocation_pattern(names: Iterable[str]) -> re.Pattern[str] | None:
    return _named_sigil_pattern(names, "/")


def _named_sigil_pattern(names: Iterable[str], sigil: str) -> re.Pattern[str] | None:
    ordered = sorted(names, key=len, reverse=True)
    if not ordered:
        return None
    alternatives = "|".join(re.escape(name) for name in ordered)
    return re.compile(rf"(?<![\w-]){re.escape(sigil)}({alternatives})(?![\w-])")


def detect_skill_invocation_findings(
    root: Path, selected_skills: set[str] | None = None
) -> list[Finding]:
    repo_root = _find_repo_root(root)
    skill_dirs = iter_internal_skills(repo_root, selected_skills)
    repo_owned_skills = _repo_owned_skill_dirs(repo_root)
    known_skills = _all_skill_dirs(repo_root)
    named_pattern = _named_skill_invocation_pattern(known_skills)
    dollar_pattern = _named_sigil_pattern(known_skills, "$")
    findings: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()

    def _record(source_path: Path, target_name: str, code: str, message: str) -> None:
        key = (source_path.as_posix(), target_name, code)
        if key in seen:
            return
        seen.add(key)
        suggestion = INVOCATION_SUGGESTIONS.get(
            code, "Keep called skills model-invocable or remove the operational invocation."
        )
        findings.append(
            Finding(
                severity="blocking",
                code=code,
                path=source_path.as_posix(),
                message=message,
                suggestion=suggestion,
            )
        )

    for skill_dir in skill_dirs:
        for source_path in _skill_invocation_sources(skill_dir):
            text = (
                strip_code_fences(read_text(source_path))
                if source_path.suffix == ".md"
                else read_text(source_path)
            )
            for match in SKILL_INVOCATION_PATTERN.finditer(text):
                target_name = f"{match.group(1)}-{match.group(0).split('-', 1)[1]}"
                if target_name in repo_owned_skills:
                    continue
                _record(
                    source_path,
                    target_name,
                    "unknown-skill-invocation",
                    f"Operational skill invocation targets missing skill '{target_name}'.",
                )
            for match in DOLLAR_SKILL_INVOCATION_PATTERN.finditer(text):
                target_name = f"{match.group(1)}-{match.group(0).split('-', 1)[1]}"
                if target_name in repo_owned_skills:
                    continue
                _record(
                    source_path,
                    target_name,
                    "unknown-skill-invocation",
                    f"Operational skill invocation targets missing skill '{target_name}'.",
                )
            if named_pattern is None:
                continue
            if dollar_pattern is not None:
                for match in dollar_pattern.finditer(text):
                    target_name = match.group(1)
                    if target_name == skill_dir.name:
                        continue
                    _record(
                        source_path,
                        target_name,
                        "cross-skill-dollar-invocation",
                        f"Cross-skill reference to '{target_name}' uses the $ entrypoint sigil.",
                    )
            for match in named_pattern.finditer(text):
                target_name = match.group(1)
                if target_name == skill_dir.name:
                    # A bundle's default prompt is a user-facing entrypoint,
                    # not a cross-skill operational call.
                    continue
                target_frontmatter, _ = split_frontmatter(
                    read_text(known_skills[target_name] / "SKILL.md")
                )
                if target_frontmatter.get("disable-model-invocation") is not True:
                    continue
                _record(
                    source_path,
                    target_name,
                    "disabled-skill-invocation",
                    f"Operational skill invocation targets disabled skill '{target_name}'.",
                )
    return findings


def detect_internal_skill_findings(
    root: Path, selected_skills: set[str] | None = None
) -> list[Finding]:
    repo_root = _find_repo_root(root)
    findings: list[Finding] = []

    for skill_dir in iter_internal_skills(repo_root, selected_skills):
        findings.extend(validate_internal_skill(repo_root, skill_dir))

    findings.extend(detect_skill_invocation_findings(repo_root, selected_skills))
    if selected_skills is None:
        findings.extend(detect_skill_prose_assertion_findings(repo_root))

    return findings


def iter_internal_skills(
    root: Path, selected_skills: set[str] | None = None
) -> list[Path]:
    skills_root = root / ".github" / "skills"
    skill_dirs = sorted(
        path
        for path in skills_root.glob("internal-*")
        if path.is_dir() and (selected_skills is None or path.name in selected_skills)
    )
    return skill_dirs


def validate_internal_skill(root: Path, skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    skill_name = skill_dir.name

    if not skill_md.exists():
        return [
            Finding(
                severity="blocking",
                code="missing-skill-md",
                path=skill_dir.as_posix(),
                message="Internal skill directory is missing SKILL.md.",
                suggestion="Add SKILL.md or remove the incomplete skill directory.",
            )
        ]

    raw_text = read_text(skill_md)
    frontmatter, body = split_frontmatter(raw_text)
    has_valid_frontmatter = True

    if not raw_text.startswith("---"):
        findings.append(
            Finding(
                severity="blocking",
                code="missing-frontmatter-block",
                path=skill_md.as_posix(),
                message="SKILL.md must start with a YAML frontmatter block.",
                suggestion="Add a leading --- frontmatter block with at least name and description.",
            )
        )
        has_valid_frontmatter = False
    elif not frontmatter:
        findings.append(
            Finding(
                severity="blocking",
                code="invalid-frontmatter-block",
                path=skill_md.as_posix(),
                message="SKILL.md frontmatter is missing, malformed, or not parseable as a mapping.",
                suggestion="Fix the YAML frontmatter so structural validation can run before content review.",
            )
        )
        has_valid_frontmatter = False

    if has_valid_frontmatter:
        declared_name = frontmatter.get("name")
        description = frontmatter.get("description")

        if declared_name != skill_name:
            findings.append(
                Finding(
                    severity="blocking",
                    code="skill-name-mismatch",
                    path=skill_md.as_posix(),
                    message=f"Frontmatter name '{declared_name}' does not match folder '{skill_name}'.",
                    suggestion="Keep the internal skill folder name and frontmatter name identical.",
                )
            )

        if not isinstance(description, str) or not description.strip():
            findings.append(
                Finding(
                    severity="blocking",
                    code="missing-description",
                    path=skill_md.as_posix(),
                    message="SKILL.md frontmatter is missing a usable description.",
                    suggestion="Add a clear description that states what the skill does and when to use it.",
                )
            )
        elif not description.strip().startswith(TRIGGER_FIRST_PREFIXES):
            findings.append(
                Finding(
                    severity="blocking",
                    code="description-not-trigger-first",
                    path=skill_md.as_posix(),
                    message="SKILL.md description must stay trigger-first so routing intent appears immediately.",
                    suggestion="Start the description with an explicit trigger such as 'Use when ...'.",
                )
            )

        non_portable_fields = sorted(set(frontmatter) - PORTABLE_FRONTMATTER_FIELDS)
        if non_portable_fields:
            findings.append(
                Finding(
                    severity="blocking",
                    code="non-portable-frontmatter-field",
                    path=skill_md.as_posix(),
                    message=(
                        "SKILL.md frontmatter contains non-portable top-level fields: "
                        + ", ".join(non_portable_fields)
                        + "."
                    ),
                    suggestion=(
                        "Move the field under metadata or into agents/openai.yaml policy."
                    ),
                )
            )

    if "## When to use" not in body:
        findings.append(
            Finding(
                severity="blocking",
                code="missing-when-to-use-heading",
                path=skill_md.as_posix(),
                message="SKILL.md must include a '## When to use' section for consistent routing guidance.",
                suggestion="Add a short '## When to use' section before deeper workflow details.",
            )
        )

    findings.extend(validate_openai_yaml(skill_dir, skill_name))
    findings.extend(validate_output_contract_projection(root, skill_dir, skill_name))
    findings.extend(validate_local_references(root, skill_dir))
    findings.extend(validate_token_hygiene(skill_dir, skill_md, body))
    findings.extend(detect_bundle_security_findings(skill_dir))
    findings.extend(validate_eval_pack(skill_dir))
    return findings


def _strip_chat_exclusion_sentences(text: str) -> str:
    normalized = " ".join(text.split())
    kept = [
        sentence
        for sentence in normalized.split(". ")
        if not any(marker in sentence.lower() for marker in CHAT_EXCLUSION_MARKERS)
    ]
    return " ".join(kept)


def validate_output_contract_projection(
    root: Path, skill_dir: Path, skill_name: str
) -> list[Finding]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return findings
    _, body = split_frontmatter(read_text(skill_md))
    normalized_body = " ".join(body.split())
    if not any(marker in normalized_body.lower() for marker in CHAT_EXCLUSION_MARKERS):
        return findings
    surfaces: list[tuple[Path, str]] = [
        (skill_dir / "agents" / "openai.yaml", "agents/openai.yaml")
    ]
    paired_agent = root / ".github" / "agents" / f"{skill_name}.agent.md"
    if paired_agent.exists():
        surfaces.append((paired_agent, "paired agent projection"))
    for path, surface in surfaces:
        if not path.exists():
            continue
        cleaned = _strip_chat_exclusion_sentences(read_text(path))
        stale = [token for token in LEGACY_OUTPUT_FIELD_TOKENS if token in cleaned]
        if stale:
            findings.append(
                Finding(
                    severity="blocking",
                    code="stale-output-contract",
                    path=path.as_posix(),
                    message=(
                        f"{surface} still requires chat-excluded output fields: "
                        f"{', '.join(stale)}."
                    ),
                    suggestion=(
                        "Update the projection to the current SKILL.md output "
                        "contract; bookkeeping fields belong to the "
                        "caller-owned ledger only."
                    ),
                )
            )
    return findings


def _is_placeholder_interface_text(value: str) -> bool:
    candidate = value.strip()
    return any(pattern.search(candidate) for pattern in PLACEHOLDER_INTERFACE_PATTERNS)


def validate_openai_yaml(skill_dir: Path, skill_name: str) -> list[Finding]:
    findings: list[Finding] = []
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        return [
            Finding(
                severity="blocking",
                code="missing-openai-yaml",
                path=skill_dir.as_posix(),
                message="Internal skill is missing agents/openai.yaml metadata.",
                suggestion="Generate agents/openai.yaml so the UI metadata stays aligned with SKILL.md.",
            )
        ]

    try:
        parsed = yaml.safe_load(read_text(openai_yaml)) or {}
    except yaml.YAMLError as error:
        return [
            Finding(
                severity="blocking",
                code="invalid-openai-yaml",
                path=openai_yaml.as_posix(),
                message=f"agents/openai.yaml is not valid YAML: {error}",
                suggestion="Fix the YAML syntax and keep interface fields deterministic.",
            )
        ]

    interface = parsed.get("interface")
    if not isinstance(interface, dict):
        return [
            Finding(
                severity="blocking",
                code="missing-openai-interface",
                path=openai_yaml.as_posix(),
                message="agents/openai.yaml must contain an interface mapping.",
                suggestion="Add interface.display_name and interface.short_description at minimum.",
            )
        ]

    display_name = interface.get("display_name")
    short_description = interface.get("short_description")
    default_prompt = interface.get("default_prompt")

    policy = parsed.get("policy")
    if isinstance(policy, dict) and "allow_implicit_invocation" in policy:
        if not isinstance(policy["allow_implicit_invocation"], bool):
            findings.append(
                Finding(
                    severity="blocking",
                    code="invalid-policy-value",
                    path=openai_yaml.as_posix(),
                    message="policy.allow_implicit_invocation must be a boolean.",
                    suggestion="Set policy.allow_implicit_invocation to true or false.",
                )
            )

    for icon_field in ("icon_small", "icon_large"):
        icon_path = interface.get(icon_field)
        if isinstance(icon_path, str) and icon_path:
            resolved_icon = skill_dir / icon_path
            if not resolved_icon.exists():
                findings.append(
                    Finding(
                        severity="blocking",
                        code="missing-icon-asset",
                        path=openai_yaml.as_posix(),
                        message=f"interface.{icon_field} points to a missing asset: {icon_path}.",
                        suggestion="Add the referenced icon asset to the skill bundle.",
                    )
                )

    if not isinstance(display_name, str) or not display_name.strip():
        findings.append(
            Finding(
                severity="blocking",
                code="missing-display-name",
                path=openai_yaml.as_posix(),
                message="agents/openai.yaml is missing interface.display_name.",
                suggestion="Add a concise human-facing display name for the skill.",
            )
        )

    if not isinstance(short_description, str) or not short_description.strip():
        findings.append(
            Finding(
                severity="blocking",
                code="missing-short-description",
                path=openai_yaml.as_posix(),
                message="agents/openai.yaml is missing interface.short_description.",
                suggestion="Add a 25-64 character short description.",
            )
        )
    elif (
        not SHORT_DESCRIPTION_MIN
        <= len(short_description.strip())
        <= SHORT_DESCRIPTION_MAX
    ):
        findings.append(
            Finding(
                severity="blocking",
                code="short-description-length",
                path=openai_yaml.as_posix(),
                message=(
                    "interface.short_description must stay between "
                    f"{SHORT_DESCRIPTION_MIN} and {SHORT_DESCRIPTION_MAX} characters."
                ),
                suggestion="Shorten or expand the description to fit the UI constraint.",
            )
        )

    interface_texts = (
        ("short_description", short_description),
        ("default_prompt", default_prompt),
    )
    for field_name, value in interface_texts:
        if not isinstance(value, str) or not _is_placeholder_interface_text(value):
            continue
        findings.append(
            Finding(
                severity="blocking",
                code="placeholder-interface-text",
                path=openai_yaml.as_posix(),
                message=f"interface.{field_name} still carries scaffold placeholder text.",
                suggestion=(
                    "Derive the text from the skill description so it names the "
                    "real trigger and deliverable."
                ),
            )
        )

    if not isinstance(default_prompt, str) or not default_prompt.strip():
        findings.append(
            Finding(
                severity="non-blocking",
                code="missing-default-prompt",
                path=openai_yaml.as_posix(),
                message="agents/openai.yaml does not define interface.default_prompt.",
                suggestion="Add a deterministic default prompt that shows how to invoke the skill.",
            )
        )
    elif (
        f"${skill_name}" not in default_prompt
        and f"/{skill_name}" not in default_prompt
    ):
        findings.append(
            Finding(
                severity="non-blocking",
                code="default-prompt-skill-mention",
                path=openai_yaml.as_posix(),
                message="interface.default_prompt does not mention the skill identifier explicitly.",
                suggestion=(
                    f"Mention ${skill_name} or /{skill_name} in the default prompt "
                    "for consistent invocation hints."
                ),
            )
        )

    return findings


def detect_bundle_security_findings(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return findings
    for script_path in sorted(
        path for path in scripts_dir.rglob("*") if path.is_file()
    ):
        try:
            text = read_text(script_path)
        except (OSError, UnicodeDecodeError):
            continue
        if EXTERNAL_URL_PATTERN.search(text):
            findings.append(
                Finding(
                    severity="non-blocking",
                    code="bundle-script-external-url",
                    path=script_path.as_posix(),
                    message="Bundle script contains an external HTTP(S) URL.",
                    suggestion="Confirm and document the external endpoint.",
                )
            )
    return findings


def validate_local_references(root: Path, skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    markdown_files = (
        [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))]
        if (skill_dir / "references").exists()
        else [skill_dir / "SKILL.md"]
    )
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if openai_yaml.exists():
        markdown_files.append(openai_yaml)

    seen: set[tuple[str, str]] = set()
    for markdown_file in markdown_files:
        text = read_text(markdown_file)
        stripped = strip_code_fences(text)

        for target in markdown_targets(stripped):
            resolved = resolve_reference(root, skill_dir, markdown_file, target)
            if resolved is None:
                continue
            key = (markdown_file.as_posix(), target)
            if key in seen:
                continue
            seen.add(key)
            if is_cross_skill_file_reference(root, skill_dir, resolved):
                findings.append(
                    Finding(
                        severity="blocking",
                        code="cross-skill-file-reference",
                        path=markdown_file.as_posix(),
                        message=f"Skill Markdown points at another skill's internal file: {target}",
                        suggestion="Reference the owning skill by name and behavior instead of linking to files inside another skill bundle.",
                    )
                )
                continue
            if not resolved.exists():
                findings.append(
                    Finding(
                        severity="blocking",
                        code="missing-local-reference",
                        path=markdown_file.as_posix(),
                        message=f"Referenced local path does not exist: {target}",
                        suggestion="Fix the path or remove the stale local reference.",
                    )
                )

    return findings


def is_cross_skill_file_reference(root: Path, skill_dir: Path, resolved: Path) -> bool:
    skills_root = (root / ".github" / "skills").resolve()
    skill_dir = skill_dir.resolve()
    resolved = resolved.resolve()
    try:
        resolved.relative_to(skills_root)
    except ValueError:
        return False
    try:
        resolved.relative_to(skill_dir)
    except ValueError:
        return True
    return False


def validate_token_hygiene(skill_dir: Path, skill_md: Path, body: str) -> list[Finding]:
    findings: list[Finding] = []
    body_lines = len([line for line in body.splitlines() if line.strip()])
    code_fence_count = body.count("```")
    has_references_dir = (skill_dir / "references").is_dir()

    if body_lines > MAX_SKILL_BODY_LINES:
        findings.append(
            Finding(
                severity="non-blocking",
                code="heavy-skill-body",
                path=skill_md.as_posix(),
                message=f"SKILL.md body has {body_lines} non-empty lines.",
                suggestion="Move detailed examples, matrices, or checklists into references/ to reduce token cost.",
            )
        )

    if code_fence_count >= INLINE_TEMPLATE_THRESHOLD and not has_references_dir:
        findings.append(
            Finding(
                severity="non-blocking",
                code="inline-template-density",
                path=skill_md.as_posix(),
                message=f"SKILL.md embeds {code_fence_count // 2} fenced code examples without a references/ directory.",
                suggestion="Extract bulky templates or examples into references/ and keep SKILL.md focused on routing and workflow.",
            )
        )

    return findings


def strip_code_fences(text: str) -> str:
    return FENCED_BLOCK_PATTERN.sub("", text)


def markdown_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        cleaned = target.strip()
        if cleaned:
            targets.add(cleaned)
    for match in INLINE_PATH_PATTERN.findall(text):
        targets.add(match.strip())
    return targets


def resolve_reference(
    root: Path, skill_dir: Path, source_file: Path, target: str
) -> Path | None:
    if not target or target.startswith("#"):
        return None
    if "://" in target or target.startswith("mailto:"):
        return None
    if target.endswith("/"):
        return None
    if target in ALLOWED_VIRTUAL_PATHS:
        return None
    if target.startswith(ALLOWED_VIRTUAL_PREFIXES):
        return None

    target_path = Path(target)
    if target.startswith(".github/"):
        return root / target_path
    if target == "AGENTS.md":
        return root / target_path
    if target.startswith(("references/", "scripts/", "assets/", "agents/")):
        return skill_dir / target_path
    if target_path.suffix in {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".hcl"}:
        return source_file.parent / target_path
    return None
