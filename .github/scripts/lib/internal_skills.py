from __future__ import annotations

import re
from pathlib import Path

import yaml

from .shared import Finding, find_repo_root, read_text, split_frontmatter

INLINE_PATH_PATTERN = re.compile(
    r"`("
    r"AGENTS\.md"
    r"|\.github/[A-Za-z0-9._/\-]+"
    r"|tmp/[A-Za-z0-9._/\-]+"
    r"|(?:references|scripts|assets|agents)/[A-Za-z0-9._/\-]+"
    r")`"
)
FENCED_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
SHORT_DESCRIPTION_MIN = 25
SHORT_DESCRIPTION_MAX = 64
MAX_SKILL_BODY_LINES = 220
INLINE_TEMPLATE_THRESHOLD = 4
ALLOWED_VIRTUAL_PATHS = {
    ".github/copilot-sync.manifest.json",
}
ALLOWED_VIRTUAL_PREFIXES = (
    "tmp/",
)


def detect_internal_skill_findings(root: Path, selected_skills: set[str] | None = None) -> list[Finding]:
    repo_root = find_repo_root(root)
    findings: list[Finding] = []

    for skill_dir in iter_internal_skills(repo_root, selected_skills):
        findings.extend(validate_internal_skill(repo_root, skill_dir))

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

    frontmatter, body = split_frontmatter(read_text(skill_md))
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

    findings.extend(validate_openai_yaml(skill_dir, skill_name))
    findings.extend(validate_local_references(root, skill_dir))
    findings.extend(validate_token_hygiene(skill_dir, skill_md, body))
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
    elif f"${skill_name}" not in default_prompt:
        findings.append(
            Finding(
                severity="non-blocking",
                code="default-prompt-skill-mention",
                path=openai_yaml.as_posix(),
                message="interface.default_prompt does not mention the skill identifier explicitly.",
                suggestion=f"Mention ${skill_name} in the default prompt for consistent invocation hints.",
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
