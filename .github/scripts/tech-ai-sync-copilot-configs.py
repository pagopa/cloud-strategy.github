#!/usr/bin/env python3
"""Purpose: Align portable Copilot customization assets with a local target repository.

Usage examples:
  python .github/scripts/tech-ai-sync-copilot-configs.py --target /path/to/repo
  python .github/scripts/tech-ai-sync-copilot-configs.py --target /path/to/repo --mode apply
  python .github/scripts/tech-ai-sync-copilot-configs.py --target /path/to/repo --report-format json
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


SCRIPT_NAME = "TechAISyncCopilotConfigs"
MANIFEST_RELATIVE_PATH = ".github/tech-ai-sync-copilot-configs.manifest.json"
SUPPORTED_SCOPE = "copilot-core"
SUPPORTED_CONFLICT_POLICY = "conservative-merge"
MANAGED_ALWAYS = (
    ".github/copilot-instructions.md",
    ".github/copilot-commit-message-instructions.md",
    ".github/copilot-code-review-instructions.md",
    ".github/security-baseline.md",
    ".github/DEPRECATION.md",
    ".github/repo-profiles.yml",
    ".github/scripts/validate-copilot-customizations.sh",
)
SOURCE_ONLY_AGENT_PATHS = {
    ".github/agents/customization-auditor.agent.md",
    ".github/agents/tech-ai-script-reviewer.agent.md",
    ".github/agents/tech-ai-sync-copilot-configs.agent.md",
}
SOURCE_ONLY_PROMPT_PATHS = {
    ".github/prompts/add-platform.prompt.md",
    ".github/prompts/add-report-script.prompt.md",
    ".github/prompts/tech-ai-code-review.prompt.md",
    ".github/prompts/tech-ai-sync-copilot-configs.prompt.md",
}
SOURCE_ONLY_SKILL_PATHS = {
    ".github/skills/code-review/SKILL.md",
    ".github/skills/tech-ai-sync-copilot-configs/SKILL.md",
}
CANONICAL_BASH_SCRIPT_PROMPT_PATH = ".github/prompts/tech-ai-bash-script.prompt.md"
CANONICAL_PYTHON_SCRIPT_PROMPT_PATH = ".github/prompts/tech-ai-python-script.prompt.md"
ALWAYS_EXCLUDED_RELATIVE_PATHS = {
    ".github/README.md",
    ".github/CHANGELOG.md",
    ".github/dependabot.yml",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/scripts/bootstrap-copilot-config.sh",
}
ALWAYS_EXCLUDED_DIRECTORIES = {
    ".git",
    ".terraform",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}
STACK_PRIORITY = ("terraform", "python", "nodejs", "java", "bash")
PROMPT_SKILL_REFERENCE_PREFIX = ".github/"


def log_info(message: str) -> None:
    print(f"ℹ️  {message}", file=sys.stderr)


def log_warn(message: str) -> None:
    print(f"⚠️  {message}", file=sys.stderr)


def log_success(message: str) -> None:
    print(f"✅ {message}", file=sys.stderr)


def log_error(message: str) -> None:
    print(f"❌ {message}", file=sys.stderr)


class CliError(RuntimeError):
    """Raised when the CLI input is invalid."""


@dataclass
class RepoProfile:
    name: str
    description: str
    recommended_instructions: list[str] = field(default_factory=list)
    recommended_prompts: list[str] = field(default_factory=list)
    recommended_skills: list[str] = field(default_factory=list)


@dataclass
class TargetAnalysis:
    repo_name: str
    repo_root: Path
    config_root: Path
    agents_relative_path: str
    agents_is_root: bool
    git_dirty: bool
    git_status_lines: list[str]
    stacks: list[str]
    unsupported_stacks: list[str]
    workflow_count: int
    composite_action_count: int
    focus: str
    priority_paths: list[str]
    top_extension_counts: dict[str, int]
    target_only_assets: dict[str, list[str]]
    profile_name: str


@dataclass
class AssetSelection:
    profile: RepoProfile
    instructions: list[str]
    prompts: list[str]
    skills: list[str]
    agents: list[str]
    baseline_files: list[str]
    validation_commands: list[str]
    preferred_prompts: list[str]
    preferred_skills: list[str]
    profile_extra_instructions: list[str]

    @property
    def managed_source_paths(self) -> list[str]:
        return sorted(
            set(self.baseline_files)
            | set(self.instructions)
            | set(self.prompts)
            | set(self.skills)
            | set(self.agents)
        )


@dataclass
class PlannedFile:
    source_relative_path: str | None
    target_relative_path: str
    desired_content: str
    category: str
    generated: bool = False


@dataclass
class FileAction:
    target_relative_path: str
    source_relative_path: str | None
    status: str
    category: str
    reason: str
    desired_sha256: str
    current_sha256: str | None = None
    generated: bool = False


@dataclass
class SyncPlan:
    analysis: TargetAnalysis
    selection: AssetSelection
    actions: list[FileAction]
    recommendations: dict[str, list[str]]
    manifest_relative_path: str

    @property
    def action_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for action in self.actions:
            counts[action.status] = counts.get(action.status, 0) + 1
        return counts


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Local repository path to analyze or update.")
    parser.add_argument("--source", help="Source standards repository root. Defaults to the current repository.")
    parser.add_argument(
        "--mode",
        choices=("plan", "apply"),
        default="plan",
        help="Whether to preview changes or apply them.",
    )
    parser.add_argument(
        "--scope",
        default=SUPPORTED_SCOPE,
        help=f"Supported value: {SUPPORTED_SCOPE}.",
    )
    parser.add_argument(
        "--conflict-policy",
        default=SUPPORTED_CONFLICT_POLICY,
        help=f"Supported value: {SUPPORTED_CONFLICT_POLICY}.",
    )
    parser.add_argument(
        "--report-format",
        choices=("md", "json"),
        default="md",
        help="Output format for stdout and optional report file.",
    )
    parser.add_argument("--report-file", help="Optional file path for the generated report.")
    args = parser.parse_args(argv)

    if args.scope != SUPPORTED_SCOPE:
        raise CliError(f"Unsupported scope '{args.scope}'. Expected '{SUPPORTED_SCOPE}'.")

    if args.conflict_policy != SUPPORTED_CONFLICT_POLICY:
        raise CliError(
            "Unsupported conflict policy "
            f"'{args.conflict_policy}'. Expected '{SUPPORTED_CONFLICT_POLICY}'."
        )

    return args


def resolve_source_repo_root(input_path: str | None, default_root: Path) -> Path:
    candidate = Path(input_path).expanduser().resolve() if input_path else default_root.resolve()
    if candidate.name == ".github":
        candidate = candidate.parent

    if not candidate.is_dir():
        raise CliError(f"Repository path not found: {candidate}")

    config_root = candidate / ".github"
    if not config_root.is_dir():
        raise CliError(f"Missing .github directory in repository: {candidate}")

    return candidate


def resolve_target_repo_root(input_path: str) -> Path:
    candidate = Path(input_path).expanduser().resolve()
    if candidate.name == ".github":
        candidate = candidate.parent

    if not candidate.is_dir():
        raise CliError(f"Repository path not found: {candidate}")

    return candidate


def load_profiles(path: Path) -> dict[str, RepoProfile]:
    profiles: dict[str, RepoProfile] = {}
    current_profile: RepoProfile | None = None
    current_list: list[str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith("  ") and not raw_line.startswith("    ") and raw_line.rstrip().endswith(":"):
            profile_name = raw_line.strip()[:-1]
            if profile_name == "profiles":
                continue
            current_profile = RepoProfile(name=profile_name, description="")
            profiles[profile_name] = current_profile
            current_list = None
            continue

        if current_profile is None:
            continue

        stripped = raw_line.strip()
        if stripped.startswith("description:"):
            current_profile.description = stripped.split(":", 1)[1].strip()
            current_list = None
            continue

        if stripped.startswith("recommended_") and stripped.endswith(":"):
            key = stripped[:-1]
            current_list = getattr(current_profile, key)
            continue

        if stripped.startswith("- ") and current_list is not None:
            current_list.append(stripped[2:].strip())

    return profiles


def frontmatter_value(path: Path, key: str) -> str:
    inside_frontmatter = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip() == "---":
            inside_frontmatter = not inside_frontmatter
            continue

        if not inside_frontmatter:
            continue

        if raw_line.startswith(f"{key}:"):
            return raw_line.split(":", 1)[1].strip().strip('"')

    return ""


def prompt_skill_refs(path: Path) -> list[str]:
    refs: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if "skills/" not in raw_line or "SKILL.md" not in raw_line:
            continue

        for token in raw_line.replace("`", " ").replace("(", " ").replace(")", " ").split():
            cleaned = token.strip(".,")
            if cleaned.endswith("SKILL.md") and "skills/" in cleaned:
                if cleaned.startswith(PROMPT_SKILL_REFERENCE_PREFIX):
                    refs.add(cleaned)
                else:
                    refs.add(f"{PROMPT_SKILL_REFERENCE_PREFIX}{cleaned}")
    return sorted(refs)


def scan_repo_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue

        relative_parts = set(path.relative_to(repo_root).parts)
        if relative_parts & ALWAYS_EXCLUDED_DIRECTORIES:
            continue
        files.append(path)
    return files


def detect_stacks(repo_root: Path, files: list[Path]) -> tuple[list[str], list[str], dict[str, int]]:
    extension_counts = {
        ".tf": 0,
        ".sh": 0,
        ".py": 0,
        ".js": 0,
        ".ts": 0,
        ".java": 0,
        ".json": 0,
        ".yaml": 0,
        ".yml": 0,
        ".md": 0,
    }
    stacks: set[str] = set()
    unsupported: set[str] = set()

    for path in files:
        suffix = path.suffix.lower()
        if suffix in extension_counts:
            extension_counts[suffix] += 1

        name = path.name
        if suffix == ".tf":
            stacks.add("terraform")
        elif suffix == ".sh":
            stacks.add("bash")
        elif suffix == ".py":
            stacks.add("python")
        elif suffix in {".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs"}:
            stacks.add("nodejs")
        elif suffix == ".java":
            stacks.add("java")
        elif name == "Makefile" or suffix == ".mk":
            stacks.add("makefile")
        elif suffix in {".yaml", ".yml"}:
            stacks.add("yaml")
        elif suffix == ".json":
            stacks.add("json")
        elif suffix == ".md":
            stacks.add("markdown")
        elif suffix == ".go" or name == "go.mod":
            unsupported.add("go")
        elif suffix == ".cs" or suffix == ".csproj":
            unsupported.add("dotnet")

        if name.startswith("Dockerfile"):
            unsupported.add("docker")

    if (repo_root / ".github" / "workflows").is_dir():
        stacks.add("github-actions")
    if any(part == "actions" for path in files for part in path.parts) and any(
        path.name in {"action.yml", "action.yaml"} for path in files
    ):
        stacks.add("composite-action")
    if (repo_root / "package.json").is_file():
        stacks.add("nodejs")
    if (repo_root / "pyproject.toml").is_file() or any(path.name.startswith("requirements") for path in files):
        stacks.add("python")
    if any(path.name in {"pom.xml", "build.gradle", "build.gradle.kts"} for path in files):
        stacks.add("java")

    return sorted(stacks), sorted(unsupported), extension_counts


def detect_profile_name(stacks: list[str]) -> str:
    stack_set = set(stacks)
    major = stack_set & set(STACK_PRIORITY)

    if "terraform" in major:
        return "infrastructure-heavy"
    if major == {"python"}:
        return "backend-python"
    if major == {"nodejs"}:
        return "backend-nodejs"
    if major == {"java"}:
        return "backend-java"
    if len(major) >= 2:
        return "mixed-platform"
    return "minimal"


def detect_focus(repo_name: str, stacks: list[str], repo_root: Path) -> str:
    stack_set = set(stacks)
    src_dir = repo_root / "src"
    src_children = {child.name for child in src_dir.iterdir()} if src_dir.is_dir() else set()

    if "terraform" in stack_set and any(name.startswith("02_policy_") for name in src_children):
        return "Infrastructure governance repository for policies, assignments, and custom roles."
    if "terraform" in stack_set:
        return "Infrastructure-heavy repository with Terraform-managed platform assets."
    if "python" in stack_set and stack_set <= {"python", "markdown", "yaml", "json", "makefile"}:
        return "Python service repository with reusable automation and supporting documentation."
    if "nodejs" in stack_set:
        return "Node.js service repository with application and workflow automation."
    if "java" in stack_set:
        return "Java service repository with build and delivery automation."
    return f"Repository '{repo_name}' with reusable GitHub Copilot customization assets."


def detect_priority_paths(repo_root: Path, stacks: list[str]) -> list[str]:
    src_dir = repo_root / "src"
    priorities: list[str] = []

    if src_dir.is_dir():
        children = sorted(child.name for child in src_dir.iterdir() if child.is_dir())
        if "01_custom_roles" in children:
            priorities.append("src/01_custom_roles")
        policy_children = [child for child in children if child.startswith("02_policy_")]
        if policy_children:
            priorities.append("src/02_policy_*")
        for preferred in ("03_policy_set", "04_policy_assignments"):
            if preferred in children:
                priorities.append(f"src/{preferred}")
        if (src_dir / "scripts").is_dir():
            priorities.append("src/scripts")

    if not priorities:
        ranked = rank_content_paths(repo_root)
        priorities.extend(ranked)

    if ".github" not in priorities:
        priorities.append(".github")

    return priorities[:5]


def rank_content_paths(repo_root: Path) -> list[str]:
    scores: dict[str, int] = {}
    for path in scan_repo_files(repo_root):
        relative = path.relative_to(repo_root)
        if relative.parts[0].startswith("."):
            continue

        anchor = relative.parts[0]
        if anchor == "src" and len(relative.parts) > 1:
            anchor = f"{anchor}/{relative.parts[1]}"

        scores[anchor] = scores.get(anchor, 0) + 1

    return [path for path, _count in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:5]]


def detect_git_state(repo_root: Path) -> tuple[bool, list[str]]:
    if not (repo_root / ".git").exists():
        return False, []

    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return bool(lines), lines


def detect_target_only_assets(source_root: Path, target_root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {"prompts": [], "skills": [], "agents": []}
    for category, pattern in (("prompts", "*.prompt.md"), ("skills", "SKILL.md"), ("agents", "*.agent.md")):
        target_dir = target_root / ".github" / category
        source_dir = source_root / ".github" / category
        if not target_dir.is_dir():
            continue

        source_names = {path.name for path in source_dir.rglob(pattern)} if source_dir.is_dir() else set()
        for path in sorted(target_dir.rglob(pattern)):
            if path.name not in source_names:
                result[category].append(str(path.relative_to(target_root)))
    return result


def build_analysis(source_root: Path, target_root: Path, profiles: dict[str, RepoProfile]) -> TargetAnalysis:
    files = scan_repo_files(target_root)
    stacks, unsupported_stacks, extension_counts = detect_stacks(target_root, files)
    profile_name = detect_profile_name(stacks)
    if profile_name not in profiles:
        profile_name = "minimal"

    agents_root_path = target_root / "AGENTS.md"
    agents_config_path = target_root / ".github" / "AGENTS.md"
    if agents_root_path.exists():
        agents_relative_path = "AGENTS.md"
        agents_is_root = True
    elif agents_config_path.exists():
        agents_relative_path = ".github/AGENTS.md"
        agents_is_root = False
    else:
        agents_relative_path = "AGENTS.md"
        agents_is_root = True

    git_dirty, git_status_lines = detect_git_state(target_root)
    workflow_dir = target_root / ".github" / "workflows"
    action_dir = target_root / ".github" / "actions"

    return TargetAnalysis(
        repo_name=target_root.name,
        repo_root=target_root,
        config_root=target_root / ".github",
        agents_relative_path=agents_relative_path,
        agents_is_root=agents_is_root,
        git_dirty=git_dirty,
        git_status_lines=git_status_lines,
        stacks=stacks,
        unsupported_stacks=unsupported_stacks,
        workflow_count=len(list(workflow_dir.glob("*.y*ml"))) if workflow_dir.is_dir() else 0,
        composite_action_count=len(list(action_dir.glob("*/action.y*ml"))) if action_dir.is_dir() else 0,
        focus=detect_focus(target_root.name, stacks, target_root),
        priority_paths=detect_priority_paths(target_root, stacks),
        top_extension_counts={key: value for key, value in extension_counts.items() if value},
        target_only_assets=detect_target_only_assets(source_root, target_root),
        profile_name=profile_name,
    )


def select_assets(source_root: Path, analysis: TargetAnalysis, profiles: dict[str, RepoProfile]) -> AssetSelection:
    profile = profiles[analysis.profile_name]
    stacks = set(analysis.stacks)
    instructions = {
        ".github/instructions/markdown.instructions.md",
        ".github/instructions/yaml.instructions.md",
    }
    profile_extra_instructions: set[str] = set()

    if "json" in stacks:
        instructions.add(".github/instructions/json.instructions.md")
    if "bash" in stacks:
        instructions.update(
            {
                ".github/instructions/bash.instructions.md",
                ".github/instructions/scripts.instructions.md",
            }
        )
    if "python" in stacks:
        instructions.add(".github/instructions/python.instructions.md")
    if "terraform" in stacks:
        instructions.add(".github/instructions/terraform.instructions.md")
    if "github-actions" in stacks:
        instructions.add(".github/instructions/github-actions.instructions.md")
    if "composite-action" in stacks:
        instructions.add(".github/instructions/github-action-composite.instructions.md")
    if "makefile" in stacks:
        instructions.add(".github/instructions/makefile.instructions.md")
    if "nodejs" in stacks and (source_root / ".github" / "instructions" / "nodejs.instructions.md").is_file():
        instructions.add(".github/instructions/nodejs.instructions.md")
    if "java" in stacks and (source_root / ".github" / "instructions" / "java.instructions.md").is_file():
        instructions.add(".github/instructions/java.instructions.md")

    for recommended in profile.recommended_instructions:
        prefixed = ensure_github_prefix(recommended)
        if (source_root / prefixed).is_file():
            instructions.add(prefixed)
        elif prefixed != recommended and (source_root / recommended).is_file():
            instructions.add(recommended)

    profile_expected = {ensure_github_prefix(item) for item in profile.recommended_instructions}
    for item in instructions:
        if item not in profile_expected:
            profile_extra_instructions.add(item)

    prompts: set[str] = set()
    for recommended in profile.recommended_prompts:
        prefixed = ensure_github_prefix(recommended)
        if (source_root / prefixed).is_file():
            prompts.add(prefixed)

    if "bash" in stacks:
        prompts.add(CANONICAL_BASH_SCRIPT_PROMPT_PATH)
    if "python" in stacks:
        prompts.update(
            {
                ".github/prompts/tech-ai-python.prompt.md",
                CANONICAL_PYTHON_SCRIPT_PROMPT_PATH,
                ".github/prompts/tech-ai-add-unit-tests.prompt.md",
            }
        )
    if "terraform" in stacks:
        prompts.add(".github/prompts/tech-ai-terraform.prompt.md")
    if "github-actions" in stacks:
        prompts.add(".github/prompts/github-action.prompt.md")
    if "composite-action" in stacks:
        prompts.add(".github/prompts/github-composite-action.prompt.md")
    if target_has_pr_template(analysis.repo_root):
        prompts.add(".github/prompts/github-pr-description.prompt.md")

    prompts = {
        prompt
        for prompt in prompts
        if prompt not in SOURCE_ONLY_PROMPT_PATHS and (source_root / prompt).is_file()
    }

    skills: set[str] = set()
    for recommended in profile.recommended_skills:
        prefixed = ensure_github_prefix(recommended)
        if (source_root / prefixed).is_file():
            skills.add(prefixed)

    for prompt in prompts:
        skills.update(path for path in prompt_skill_refs(source_root / prompt) if (source_root / path).is_file())

    skills = {skill for skill in skills if skill not in SOURCE_ONLY_SKILL_PATHS}

    agents: set[str] = {
        ".github/agents/planner.agent.md",
        ".github/agents/implementer.agent.md",
        ".github/agents/reviewer.agent.md",
        ".github/agents/security-reviewer.agent.md",
    }
    if "github-actions" in stacks:
        agents.add(".github/agents/github-workflow-supply-chain.agent.md")
    if "terraform" in stacks:
        agents.add(".github/agents/terraform-guardrails.agent.md")
    if repo_needs_iam_review(analysis.repo_root):
        agents.add(".github/agents/iam-least-privilege.agent.md")
    if target_has_pr_template(analysis.repo_root):
        agents.add(".github/agents/github-pr-writer.agent.md")

    agents = {agent for agent in agents if agent not in SOURCE_ONLY_AGENT_PATHS and (source_root / agent).is_file()}

    baseline_files = [path for path in MANAGED_ALWAYS if (source_root / path).is_file()]
    validation_commands = build_validation_commands(analysis, instructions)

    preferred_prompts = [path for path in sorted(prompts) if path in {ensure_github_prefix(item) for item in profile.recommended_prompts}]
    if not preferred_prompts:
        preferred_prompts = sorted(prompts)[:5]

    preferred_skills = [path for path in sorted(skills) if path in {ensure_github_prefix(item) for item in profile.recommended_skills}]
    if not preferred_skills:
        preferred_skills = sorted(skills)[:5]

    return AssetSelection(
        profile=profile,
        instructions=sorted(instructions),
        prompts=sorted(prompts),
        skills=sorted(skills),
        agents=sorted(agents),
        baseline_files=baseline_files,
        validation_commands=validation_commands,
        preferred_prompts=preferred_prompts,
        preferred_skills=preferred_skills,
        profile_extra_instructions=sorted(profile_extra_instructions),
    )


def ensure_github_prefix(path: str) -> str:
    if path.startswith(".github/"):
        return path
    return f".github/{path}"


def target_has_pr_template(repo_root: Path) -> bool:
    return any(
        path.is_file()
        for path in (
            repo_root / ".github" / "PULL_REQUEST_TEMPLATE.md",
            repo_root / ".github" / "pull_request_template.md",
        )
    )


def repo_needs_iam_review(repo_root: Path) -> bool:
    interesting_parts = ("custom_roles", "authorization", "iam", "role", "policy")
    for path in scan_repo_files(repo_root):
        if any(part in path.as_posix() for part in interesting_parts):
            return True
    return False


def build_validation_commands(analysis: TargetAnalysis, instruction_paths: set[str] | list[str]) -> list[str]:
    commands: list[str] = []
    if "terraform" in analysis.stacks:
        commands.extend(["terraform fmt -recursive", "terraform validate"])
    if "bash" in analysis.stacks:
        commands.extend(["bash -n <changed_bash_paths>", "shellcheck -s bash <changed_bash_paths>"])
    if "python" in analysis.stacks:
        commands.extend(["python -m compileall <changed_python_paths>", "pytest"])
    commands.append("bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict")
    return commands


def build_planned_files(
    source_root: Path,
    target_root: Path,
    analysis: TargetAnalysis,
    selection: AssetSelection,
) -> list[PlannedFile]:
    planned_files: list[PlannedFile] = []
    for source_relative_path in selection.managed_source_paths:
        if source_relative_path == ".github/AGENTS.md":
            continue

        desired_content = (source_root / source_relative_path).read_text(encoding="utf-8")
        planned_files.append(
            PlannedFile(
                source_relative_path=source_relative_path,
                target_relative_path=source_relative_path,
                desired_content=desired_content,
                category=asset_category(source_relative_path),
            )
        )

    planned_files.append(
        PlannedFile(
            source_relative_path=None,
            target_relative_path=analysis.agents_relative_path,
            desired_content=render_agents_markdown(analysis, selection, source_root),
            category="agents",
            generated=True,
        )
    )

    return sorted(planned_files, key=lambda item: item.target_relative_path)


def asset_category(relative_path: str) -> str:
    for category in ("instructions", "prompts", "skills", "agents", "scripts"):
        if f"/{category}/" in relative_path:
            return category
    return "baseline"


def load_manifest(target_root: Path) -> dict[str, object]:
    manifest_path = target_root / MANIFEST_RELATIVE_PATH
    if not manifest_path.is_file():
        return {}

    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CliError(f"Invalid JSON manifest at {manifest_path}: {error}") from error


def plan_actions(target_root: Path, planned_files: list[PlannedFile], manifest: dict[str, object]) -> list[FileAction]:
    actions: list[FileAction] = []
    managed_files = manifest.get("managed_files", {})
    if not isinstance(managed_files, dict):
        managed_files = {}

    for planned_file in planned_files:
        target_path = target_root / planned_file.target_relative_path
        desired_sha256 = sha256_text(planned_file.desired_content)
        current_sha256 = sha256_path(target_path) if target_path.is_file() else None
        managed_entry = managed_files.get(planned_file.target_relative_path)

        if managed_entry is not None and not isinstance(managed_entry, dict):
            managed_entry = None

        if managed_entry:
            recorded_sha256 = str(managed_entry.get("sha256", ""))
            if current_sha256 and current_sha256 != recorded_sha256 and current_sha256 != desired_sha256:
                actions.append(
                    FileAction(
                        target_relative_path=planned_file.target_relative_path,
                        source_relative_path=planned_file.source_relative_path,
                        status="conflict",
                        category=planned_file.category,
                        reason="Source-managed file changed locally after the last sync.",
                        desired_sha256=desired_sha256,
                        current_sha256=current_sha256,
                        generated=planned_file.generated,
                    )
                )
                continue

            if current_sha256 == desired_sha256:
                actions.append(
                    FileAction(
                        target_relative_path=planned_file.target_relative_path,
                        source_relative_path=planned_file.source_relative_path,
                        status="unchanged",
                        category=planned_file.category,
                        reason="Target content already matches the desired content.",
                        desired_sha256=desired_sha256,
                        current_sha256=current_sha256,
                        generated=planned_file.generated,
                    )
                )
                continue

            actions.append(
                FileAction(
                    target_relative_path=planned_file.target_relative_path,
                    source_relative_path=planned_file.source_relative_path,
                    status="update",
                    category=planned_file.category,
                    reason="Update an existing source-managed file.",
                    desired_sha256=desired_sha256,
                    current_sha256=current_sha256,
                    generated=planned_file.generated,
                )
            )
            continue

        if current_sha256 is None:
            actions.append(
                FileAction(
                    target_relative_path=planned_file.target_relative_path,
                    source_relative_path=planned_file.source_relative_path,
                    status="create",
                    category=planned_file.category,
                    reason="Target file is missing.",
                    desired_sha256=desired_sha256,
                    current_sha256=None,
                    generated=planned_file.generated,
                )
            )
            continue

        if current_sha256 == desired_sha256:
            actions.append(
                FileAction(
                    target_relative_path=planned_file.target_relative_path,
                    source_relative_path=planned_file.source_relative_path,
                    status="adopt",
                    category=planned_file.category,
                    reason="Existing target file already matches the desired content and can be adopted.",
                    desired_sha256=desired_sha256,
                    current_sha256=current_sha256,
                    generated=planned_file.generated,
                )
            )
            continue

        actions.append(
            FileAction(
                target_relative_path=planned_file.target_relative_path,
                source_relative_path=planned_file.source_relative_path,
                status="conflict",
                category=planned_file.category,
                reason="Existing target file differs and is not source-managed yet.",
                desired_sha256=desired_sha256,
                current_sha256=current_sha256,
                generated=planned_file.generated,
            )
        )

    return actions


def render_agents_markdown(analysis: TargetAnalysis, selection: AssetSelection, source_root: Path) -> str:
    instructions_apply_to = build_instruction_rules(source_root, selection.instructions)
    prompts_list = describe_assets(source_root, selection.prompts, "prompt")
    skills_list = describe_assets(source_root, selection.skills, "skill")
    agents_list = describe_assets(source_root, selection.agents, "agent")
    governance_references = [
        ".github/security-baseline.md",
        ".github/DEPRECATION.md",
        ".github/repo-profiles.yml",
        ".github/scripts/validate-copilot-customizations.sh",
    ]

    lines: list[str] = [
        f"# AGENTS.md - {analysis.repo_name}",
        "",
        "This file is for GitHub Copilot and AI assistants working in this repository.",
        "",
        "## Naming Policy",
        "- Use GitHub Copilot terminology in repository-facing content.",
        "- Do not mention internal runtime names in repository artifacts.",
        "- Treat prompt frontmatter `name:` as the canonical command identifier.",
        "",
        "## Decision Priority",
        "1. Apply repository non-negotiables from `copilot-instructions.md`.",
        "2. Apply explicit user requirements for the current task.",
        "3. Apply the selected agent behavior (agent-first routing).",
        "4. Apply matching files under `instructions/*.instructions.md` using `applyTo`.",
        "5. Apply selected prompt constraints from `prompts/*.prompt.md`.",
        "6. Apply implementation details from referenced `skills/*/SKILL.md`.",
        "7. If no agent is explicitly selected, default to `Implementer`.",
        "",
        "## Stack Resolution Rules",
        "- The agent role is behavioral, not language-specific.",
        "- Resolve stack from target files and explicit prompt inputs.",
        "- Primary `applyTo` rules (one instruction per file type):",
    ]
    lines.extend(f"  - `{rule}`" for rule in instructions_apply_to)
    lines.extend(
        [
            "- Overlay instructions never conflict with primary instructions - they add cross-cutting standards.",
            "",
            "## Agent Routing",
            "",
            "### When to use each agent",
        ]
    )
    lines.extend(agent_routing_lines(selection.agents))
    lines.extend(
        [
            "",
            "### Agent composition",
            "- For changes spanning multiple specialist domains, run each relevant specialist and aggregate findings.",
            "- The standard chain for non-trivial work is: `Planner` -> `Implementer` -> `Reviewer` or a matching specialist.",
            "",
            "## Available Skills",
        ]
    )
    lines.extend(skills_list)
    lines.extend(["", "## Available Prompts"])
    lines.extend(prompts_list)
    lines.extend(["", "## Governance References"])
    lines.extend(f"- `{path}`" for path in governance_references)
    lines.extend(
        [
            "",
            "## Prohibitions",
            "- Never hardcode secrets, tokens, or credentials.",
            "- Never modify `README.md` files unless explicitly requested by the user.",
            "- Never introduce new patterns when existing repository conventions exist.",
            "- Keep all repository artifacts in English (user chat may be in other languages).",
            "- Never run destructive commands unless explicitly requested.",
            "- Never skip validation after making changes.",
            "",
            "## Repository Defaults",
            f"- Primary focus: {analysis.focus}",
            f"- Profile hint: `{selection.profile.name}`",
            "- AGENTS.md is the external bridge for assistant behavior and naming; keep runtime references abstract.",
            "- Prioritize these paths:",
        ]
    )
    lines.extend(f"  - `{path}`" for path in analysis.priority_paths)
    lines.extend(["", "### Default instruction routing"])
    lines.extend(f"- `{strip_github_prefix(path)}`" for path in selection.instructions)
    lines.extend(["", "### Preferred prompts"])
    lines.extend(f"- `{strip_github_prefix(path)}`" for path in selection.preferred_prompts)
    lines.extend(["", "### Preferred skills"])
    lines.extend(f"- `{strip_github_prefix(path)}`" for path in selection.preferred_skills)
    lines.extend(["", "### Required validations before PR"])
    lines.extend(f"- `{command}`" for command in selection.validation_commands)
    lines.extend(
        [
            "",
            "## Repository Inventory (Auto-generated)",
            "",
            "### Instructions",
        ]
    )
    lines.extend(f"- `{path}`" for path in selection.instructions)
    lines.extend(["", "### Prompts"])
    lines.extend(f"- `{path}`" for path in selection.prompts)
    lines.extend(["", "### Skills"])
    lines.extend(f"- `{path}`" for path in selection.skills)
    lines.extend(["", "### Agents"])
    lines.extend(f"- `{path}`" for path in selection.agents)
    lines.extend(["", "## Agents"])
    lines.extend(agents_list)

    return "\n".join(lines) + "\n"


def strip_github_prefix(value: str) -> str:
    if value.startswith(".github/"):
        return value[len(".github/") :]
    return value


def build_instruction_rules(source_root: Path, instruction_paths: list[str]) -> list[str]:
    rules: list[str] = []
    for instruction_path in instruction_paths:
        apply_to = frontmatter_value(source_root / instruction_path, "applyTo")
        if not apply_to:
            continue
        label = strip_github_prefix(instruction_path)
        rules.append(f"{apply_to} -> `{label}`")
    return rules


def describe_assets(source_root: Path, relative_paths: list[str], asset_type: str) -> list[str]:
    described: list[str] = []
    for relative_path in relative_paths:
        asset_path = source_root / relative_path
        name = frontmatter_value(asset_path, "name") or asset_path.stem
        description = frontmatter_value(asset_path, "description") or "No description available."
        label = relative_path[len(".github/") :]
        if asset_type == "prompt":
            described.append(f"- `{name}` (`{label}`): {description}")
        elif asset_type == "skill":
            described.append(f"- `{name}` (`{label}`): {description}")
        else:
            described.append(f"- `{name}` (`{label}`): {description}")
    return described


def agent_routing_lines(agent_paths: list[str]) -> list[str]:
    lines: list[str] = []
    agent_names = {Path(path).name for path in agent_paths}
    if "planner.agent.md" in agent_names:
        lines.append("- Use `Planner` for ambiguous scope, tradeoff analysis, or multi-step design.")
    if "implementer.agent.md" in agent_names:
        lines.append("- Use `Implementer` for direct code/config changes and validation-first delivery.")
    if "reviewer.agent.md" in agent_names:
        lines.append("- Use `Reviewer` for quality gates and defect/regression findings.")
    if "terraform-guardrails.agent.md" in agent_names:
        lines.append("- Use `TerraformGuardrails` for Terraform safety and policy guardrail reviews.")
    if "iam-least-privilege.agent.md" in agent_names:
        lines.append("- Use `IAMLeastPrivilege` for role and permission scoping checks.")
    if "github-workflow-supply-chain.agent.md" in agent_names:
        lines.append("- Use `WorkflowSupplyChain` for workflow supply-chain hardening and CI checks.")
    if "security-reviewer.agent.md" in agent_names:
        lines.append("- Use `SecurityReviewer` as the security-focused review gate.")
    if "github-pr-writer.agent.md" in agent_names:
        lines.append("- Use `PRWriter` when generating pull request content from the repository template.")
    return lines


def build_recommendations(
    analysis: TargetAnalysis,
    selection: AssetSelection,
    actions: list[FileAction],
    source_root: Path,
) -> dict[str, list[str]]:
    recommendations: dict[str, list[str]] = {
        "missing profiles": [],
        "missing instructions/prompts/skills": [],
        "unsupported stack detection": [],
        "weak conflict-handling rules": [],
        "missing consumer-facing validation or onboarding guidance": [],
    }

    if analysis.unsupported_stacks:
        stacks = ", ".join(analysis.unsupported_stacks)
        recommendations["missing profiles"].append(
            f"Add reusable profile guidance for unsupported target stacks: {stacks}."
        )
        recommendations["missing instructions/prompts/skills"].append(
            f"Add matching instructions, prompts, or skills for unsupported target stacks: {stacks}."
        )

    if selection.profile_extra_instructions:
        extra = ", ".join(strip_github_prefix(path) for path in selection.profile_extra_instructions)
        recommendations["missing profiles"].append(
            "The selected profile does not currently capture all required instructions for the detected target "
            f"shape: {extra}."
        )

    target_only_prompt_assets = analysis.target_only_assets.get("prompts", [])
    if target_only_prompt_assets:
        recommendations["missing instructions/prompts/skills"].append(
            "The target repository already contains prompt assets that are not available in the source standards "
            f"repo: {', '.join(target_only_prompt_assets)}."
        )

    if any(action.target_relative_path == analysis.agents_relative_path and action.status == "conflict" for action in actions):
        recommendations["weak conflict-handling rules"].append(
            "Consider generated section markers or a dedicated root-AGENTS template to reduce consumer AGENTS "
            "merge conflicts."
        )

    if analysis.agents_is_root and not (source_root / "AGENTS.md").exists():
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "Document root-level AGENTS adoption explicitly because the source standards repo currently ships its "
            "authoritative AGENTS file under `.github/`."
        )

    if not recommendations["missing consumer-facing validation or onboarding guidance"]:
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "No additional onboarding or validation gap detected from the current target analysis."
        )

    for category, entries in recommendations.items():
        if not entries:
            recommendations[category] = ["No gap identified."]

    return recommendations


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def apply_plan(target_root: Path, plan: SyncPlan, planned_files: list[PlannedFile]) -> None:
    content_map = {item.target_relative_path: item for item in planned_files}
    for action in plan.actions:
        if action.status not in {"create", "update"}:
            continue

        planned_file = content_map[action.target_relative_path]
        target_path = target_root / action.target_relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(planned_file.desired_content, encoding="utf-8")

    manifest = {
        "tool": SCRIPT_NAME,
        "version": 1,
        "generated_at_utc": utc_now(),
        "target_repo": str(target_root),
        "profile": plan.selection.profile.name,
        "managed_files": {},
    }

    for action in plan.actions:
        if action.status in {"conflict"}:
            continue

        target_path = target_root / action.target_relative_path
        if not target_path.is_file():
            continue

        manifest["managed_files"][action.target_relative_path] = {
            "sha256": sha256_path(target_path),
            "source_relative_path": action.source_relative_path,
            "generated": action.generated,
        }

    manifest_path = target_root / plan.manifest_relative_path
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_markdown_report(plan: SyncPlan) -> str:
    lines = [
        "# TechAISyncCopilotConfigs Report",
        "",
        "## Target analysis summary",
        f"- Source repo: `{plan.selection.profile.name}` profile from the current standards repository",
        f"- Target repo: `{plan.analysis.repo_root}`",
        f"- Detected profile: `{plan.analysis.profile_name}`",
        f"- Detected stacks: {', '.join(plan.analysis.stacks) if plan.analysis.stacks else 'none'}",
        f"- Unsupported stacks: {', '.join(plan.analysis.unsupported_stacks) if plan.analysis.unsupported_stacks else 'none'}",
        f"- AGENTS location: `{plan.analysis.agents_relative_path}`",
        f"- Git worktree state: {'dirty' if plan.analysis.git_dirty else 'clean'}",
        f"- Priority paths: {', '.join(plan.analysis.priority_paths)}",
        "",
        "## Asset selection",
        f"- Baseline files: {', '.join(plan.selection.baseline_files)}",
        f"- Instructions: {', '.join(plan.selection.instructions)}",
        f"- Prompts: {', '.join(plan.selection.prompts)}",
        f"- Skills: {', '.join(plan.selection.skills)}",
        f"- Agents: {', '.join(plan.selection.agents)}",
        "",
        "## Planned or applied actions",
    ]
    for status in ("create", "update", "adopt", "unchanged", "conflict"):
        matching = [action for action in plan.actions if action.status == status]
        lines.append(f"### {status.title()}")
        if not matching:
            lines.append("- None")
            continue
        for action in matching:
            lines.append(f"- `{action.target_relative_path}`: {action.reason}")

    lines.extend(["", "## Target validation commands"])
    for command in plan.selection.validation_commands:
        lines.append(f"- `{command}`")

    lines.extend(["", "## Recommendations for improving the source repo"])
    for category, items in plan.recommendations.items():
        lines.append(f"### {category.title()}")
        for item in items:
            lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def render_json_report(plan: SyncPlan) -> str:
    payload = {
        "tool": SCRIPT_NAME,
        "generated_at_utc": utc_now(),
        "analysis": {
            "target_repo": str(plan.analysis.repo_root),
            "profile": plan.analysis.profile_name,
            "stacks": plan.analysis.stacks,
            "unsupported_stacks": plan.analysis.unsupported_stacks,
            "agents_relative_path": plan.analysis.agents_relative_path,
            "git_dirty": plan.analysis.git_dirty,
            "priority_paths": plan.analysis.priority_paths,
            "top_extension_counts": plan.analysis.top_extension_counts,
            "target_only_assets": plan.analysis.target_only_assets,
        },
        "selection": {
            "baseline_files": plan.selection.baseline_files,
            "instructions": plan.selection.instructions,
            "prompts": plan.selection.prompts,
            "skills": plan.selection.skills,
            "agents": plan.selection.agents,
            "validation_commands": plan.selection.validation_commands,
        },
        "actions": [
            {
                "target_relative_path": action.target_relative_path,
                "source_relative_path": action.source_relative_path,
                "status": action.status,
                "category": action.category,
                "reason": action.reason,
            }
            for action in plan.actions
        ],
        "recommendations": plan.recommendations,
        "manifest_relative_path": plan.manifest_relative_path,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_plan(source_root: Path, target_root: Path) -> tuple[SyncPlan, list[PlannedFile]]:
    profiles = load_profiles(source_root / ".github" / "repo-profiles.yml")
    analysis = build_analysis(source_root, target_root, profiles)
    selection = select_assets(source_root, analysis, profiles)
    manifest = load_manifest(target_root)
    planned_files = build_planned_files(source_root, target_root, analysis, selection)
    actions = plan_actions(target_root, planned_files, manifest)
    recommendations = build_recommendations(analysis, selection, actions, source_root)
    return (
        SyncPlan(
            analysis=analysis,
            selection=selection,
            actions=actions,
            recommendations=recommendations,
            manifest_relative_path=MANIFEST_RELATIVE_PATH,
        ),
        planned_files,
    )


def emit_report(plan: SyncPlan, report_format: str) -> str:
    if report_format == "json":
        return render_json_report(plan)
    return render_markdown_report(plan)


def main(argv: list[str] | None = None) -> int:
    default_source_root = Path(__file__).resolve().parents[2]

    try:
        args = parse_args(argv or sys.argv[1:])
        source_root = resolve_source_repo_root(args.source, default_source_root)
        target_root = resolve_target_repo_root(args.target)
    except CliError as error:
        log_error(str(error))
        return 2

    log_info(f"Source repository: {source_root}")
    log_info(f"Target repository: {target_root}")
    log_info(f"Mode: {args.mode}")

    try:
        plan, planned_files = build_plan(source_root, target_root)
    except CliError as error:
        log_error(str(error))
        return 2

    if args.mode == "apply":
        log_info("Applying conservative merge for source-managed files.")
        apply_plan(target_root, plan, planned_files)
        log_success(f"Manifest written to {target_root / MANIFEST_RELATIVE_PATH}")
    else:
        log_info("Plan mode selected - no repository files will be changed.")

    report = emit_report(plan, args.report_format)
    sys.stdout.write(report)

    if args.report_file:
        write_report(Path(args.report_file).expanduser().resolve(), report)
        log_success(f"Report written to {args.report_file}")

    if any(action.status == "conflict" for action in plan.actions):
        log_warn("Conflicts detected. Review the report before applying changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
