from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .shared import Finding, find_repo_root, read_text, split_frontmatter

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
    "Use this",
    "Use before",
    "When ",
)
ROUTER_SKILL_NAMES = frozenset({
    "internal-azure",
    "internal-aws",
    "internal-gcp",
    "internal-github",
})
ALLOWED_VIRTUAL_PATHS = {
    ".github/copilot-sync.manifest.json",
}
ALLOWED_VIRTUAL_PREFIXES = (
    "tmp/",
)
SKILL_INVOCATION_PATTERN = re.compile(r"(?<![\w-])/(internal|local)-[a-z0-9][a-z0-9-]*")
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
                        if literal is not None and self.path_values.get(name) != literal:
                            self.path_values[name] = literal
                            changed = True
                    for name in self._assigned_names(statement):
                        environment[name] = taint

    def _scan_block(self, statements: list[ast.stmt], environment: dict[str, bool]) -> None:
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
            return any(self._expr_tainted(argument, environment) for argument in node.args)
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
            return any(self._expr_tainted(element, environment) for element in node.elts)
        if isinstance(node, ast.Dict):
            return any(
                self._expr_tainted(element, environment)
                for element in (*node.keys, *node.values)
                if element is not None
            )
        if isinstance(node, ast.GeneratorExp):
            return self._expr_tainted(node.elt, environment) or any(
                self._expr_tainted(generator.iter, environment)
                or any(self._expr_tainted(condition, environment) for condition in generator.ifs)
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
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
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
    repo_root = find_repo_root(root)
    findings: list[Finding] = []
    tests_root = repo_root / "tests"
    for source_path in sorted(tests_root.rglob("*.py")):
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


def detect_skill_invocation_findings(
    root: Path, selected_skills: set[str] | None = None
) -> list[Finding]:
    repo_root = find_repo_root(root)
    skill_dirs = iter_internal_skills(repo_root, selected_skills)
    known_skills = {
        skill_dir.name: skill_dir for skill_dir in iter_internal_skills(repo_root)
    }
    findings: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()
    for skill_dir in skill_dirs:
        for source_path in _skill_invocation_sources(skill_dir):
            text = strip_code_fences(read_text(source_path)) if source_path.suffix == ".md" else read_text(source_path)
            for match in SKILL_INVOCATION_PATTERN.finditer(text):
                target_name = f"{match.group(1)}-{match.group(0).split('-', 1)[1]}"
                target_dir = known_skills.get(target_name)
                code = "unknown-skill-invocation"
                if target_dir is None:
                    finding = Finding(
                        severity="blocking",
                        code=code,
                        path=source_path.as_posix(),
                        message=f"Operational skill invocation targets missing skill '{target_name}'.",
                        suggestion="Invoke an existing repository-owned skill or keep the identifier non-operational.",
                    )
                else:
                    target_frontmatter, _ = split_frontmatter(
                        read_text(target_dir / "SKILL.md")
                    )
                    if target_frontmatter.get("disable-model-invocation") is not True:
                        continue
                    if target_name == skill_dir.name:
                        # A bundle's default prompt is a user-facing entrypoint,
                        # not a cross-skill operational call.
                        continue
                    code = "disabled-skill-invocation"
                    finding = Finding(
                        severity="blocking",
                        code=code,
                        path=source_path.as_posix(),
                        message=f"Operational skill invocation targets disabled skill '{target_name}'.",
                        suggestion="Keep called skills model-invocable or remove the operational invocation.",
                    )
                key = (source_path.as_posix(), target_name, code)
                if key not in seen:
                    seen.add(key)
                    findings.append(finding)
    return findings


def detect_internal_skill_findings(root: Path, selected_skills: set[str] | None = None) -> list[Finding]:
    repo_root = find_repo_root(root)
    findings: list[Finding] = []

    for skill_dir in iter_internal_skills(repo_root, selected_skills):
        findings.extend(validate_internal_skill(repo_root, skill_dir))

    findings.extend(detect_skill_invocation_findings(repo_root, selected_skills))
    if selected_skills is None:
        findings.extend(detect_skill_prose_assertion_findings(repo_root))

    return findings


def iter_internal_skills(root: Path, selected_skills: set[str] | None = None) -> list[Path]:
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
        elif skill_name not in ROUTER_SKILL_NAMES and not description.strip().startswith(TRIGGER_FIRST_PREFIXES):
            findings.append(
                Finding(
                    severity="blocking",
                    code="description-not-trigger-first",
                    path=skill_md.as_posix(),
                    message="SKILL.md description must stay trigger-first so routing intent appears immediately.",
                    suggestion="Start the description with an explicit trigger such as 'Use when ...'.",
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
    if not any(
        marker in normalized_body.lower() for marker in CHAT_EXCLUSION_MARKERS
    ):
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
    elif not SHORT_DESCRIPTION_MIN <= len(short_description.strip()) <= SHORT_DESCRIPTION_MAX:
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
    elif f"${skill_name}" not in default_prompt and f"/{skill_name}" not in default_prompt:
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


def validate_local_references(root: Path, skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    markdown_files = [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))] if (skill_dir / "references").exists() else [skill_dir / "SKILL.md"]

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


def resolve_reference(root: Path, skill_dir: Path, source_file: Path, target: str) -> Path | None:
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
