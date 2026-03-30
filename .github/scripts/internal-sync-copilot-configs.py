#!/usr/bin/env python3
"""Purpose: Align portable Copilot customization assets with a local target repository.

Usage examples:
  python .github/scripts/internal-sync-copilot-configs.py --target /path/to/repo
  python .github/scripts/internal-sync-copilot-configs.py --target /path/to/repo --mode apply
  python .github/scripts/internal-sync-copilot-configs.py --target /path/to/repo --report-format json
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


SCRIPT_NAME = "internal-sync-global-copilot-configs-into-repo"
MANIFEST_RELATIVE_PATH = ".github/internal-sync-copilot-configs.manifest.json"
SUPPORTED_SCOPE = "copilot-core"
SUPPORTED_CONFLICT_POLICY = "conservative-merge"
VSCODE_SETTINGS_RELATIVE_PATH = ".vscode/settings.json"
PR_DESCRIPTION_SETTING_KEY = "githubPullRequests.pullRequestDescription"
PR_DESCRIPTION_SETTING_VALUE = "template"
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
    ".github/agents/internal-ai-resource-development.agent.md",
    ".github/agents/internal-sync-global-copilot-configs-into-repo.agent.md",
}
SOURCE_ONLY_PROMPT_PATHS = {
    ".github/prompts/internal-add-platform.prompt.md",
    ".github/prompts/internal-add-report-script.prompt.md",
}
SOURCE_ONLY_SKILL_PATHS = {
    ".github/skills/internal-agent-development/SKILL.md",
    ".github/skills/internal-agents-md-bridge/SKILL.md",
    ".github/skills/internal-copilot-audit/SKILL.md",
    ".github/skills/internal-skill-management/SKILL.md",
    ".github/skills/internal-sync-global-copilot-configs-into-repo/SKILL.md",
    ".github/skills/openai-skill-creator/SKILL.md",
}
ALWAYS_EXCLUDED_RELATIVE_PATHS = {
    ".github/README.md",
    ".github/CHANGELOG.md",
    ".github/dependabot.yml",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
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
STACK_PRIORITY = ("terraform", "python", "nodejs", "java", "docker", "bash")
PROMPT_SKILL_REFERENCE_PREFIX = ".github/"
EXTRA_LEGACY_ALIAS_PATHS = {
    ".github/prompts/internal-github-action.prompt.md": (
        ".github/prompts/cicd-workflow.prompt.md",
    ),
}
ROLE_OVERLAP_SECTION_PREFIXES = ("workflow", "instructions", "validation")
ROLE_OVERLAP_LINE_THRESHOLD = 3
AGENTS_INVENTORY_CATEGORIES = ("instructions", "prompts", "skills", "agents")
PROMPT_NAME_OVERRIDES: dict[str, str] = {}
SOURCE_ONLY_TARGET_RESIDUE_PATHS = (
    ".github/README.md",
    ".github/agents/README.md",
)
SOURCE_ONLY_TARGET_RESIDUE_DIRECTORIES = (".github/templates",)


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
    redundant_assets: list["RedundantAsset"]
    target_asset_issues: list["TargetAssetIssue"]
    source_audit: "SourceAudit"
    recommendations: dict[str, list[str]]
    manifest_relative_path: str

    @property
    def action_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for action in self.actions:
            counts[action.status] = counts.get(action.status, 0) + 1
        return counts


@dataclass
class RedundantAsset:
    category: str
    canonical_target_path: str
    existing_target_paths: list[str]
    issue_type: str
    selected_for_sync: bool

    @property
    def reason(self) -> str:
        listed = ", ".join(self.existing_target_paths)
        if self.issue_type == "sync_would_duplicate":
            return (
                "Equivalent legacy asset(s) already exist in target: "
                f"{listed}. Syncing `{self.canonical_target_path}` would create redundant configuration."
            )
        if self.issue_type == "legacy_alias_only":
            return (
                "Legacy alias asset(s) exist in target without the canonical file: "
                f"{listed}. Prefer `{self.canonical_target_path}` when aligning this capability family."
            )

        return (
            "Equivalent assets from the same capability family already coexist in target: "
            f"{listed}. Consolidate to one canonical asset before continuing."
        )


@dataclass
class TargetAssetIssue:
    category: str
    target_relative_path: str
    issue_types: list[str]
    details: list[str]
    severity: str
    canonical_source_path: str | None = None


@dataclass
class CanonicalAssetGroup:
    category: str
    family: str
    paths: list[str]

    @property
    def has_physical_duplicates(self) -> bool:
        return len(self.paths) > 1


@dataclass
class LegacyAlias:
    category: str
    canonical_path: str
    alias_paths: list[str]


@dataclass
class RoleOverlap:
    family: str
    asset_paths: list[str]
    shared_instruction_count: int
    examples: list[str]


@dataclass
class AgentsMdRepeat:
    reference: str
    sections: list[str]
    count: int


@dataclass
class SourceAudit:
    canonical_assets: list[CanonicalAssetGroup]
    legacy_aliases: list[LegacyAlias]
    role_overlaps: list[RoleOverlap]
    agents_md_repeats: list[AgentsMdRepeat]
    recommendations: list[str]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prune_empty_parent_dirs(path: Path, stop_at: Path) -> None:
    current = path.parent
    while current != stop_at and current.is_dir():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_source_version(source_root: Path) -> str | None:
    version_path = source_root / "VERSION"
    if not version_path.is_file():
        return None

    value = version_path.read_text(encoding="utf-8").strip()
    return value or None


def git_commit_sha(repo_root: Path) -> str | None:
    if not (repo_root / ".git").exists():
        return None

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    return result.stdout.strip() or None


def is_composite_action_file(path: Path) -> bool:
    if path.name not in {"action.yml", "action.yaml"}:
        return False

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False

    return bool(re.search(r"(?ms)^runs:\s*$.*?^[ \t]+using:\s*[\"']?composite[\"']?\s*$", content))


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


def parse_frontmatter(path: Path) -> dict[str, str]:
    frontmatter: dict[str, str] = {}
    inside_frontmatter = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == "---":
            if inside_frontmatter:
                break
            inside_frontmatter = True
            continue

        if not inside_frontmatter or ":" not in raw_line:
            continue

        key, value = raw_line.split(":", 1)
        key = key.strip()
        if not key or " " in key:
            continue
        frontmatter[key] = value.strip().strip('"')

    return frontmatter


def frontmatter_value(path: Path, key: str) -> str:
    return parse_frontmatter(path).get(key, "")


def prompt_skill_refs(path: Path) -> list[str]:
    refs: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if "skills/" not in raw_line or "SKILL.md" not in raw_line:
            continue

        for token in re.findall(r"(?:\.github/)?skills/[A-Za-z0-9._/-]+/SKILL\.md", raw_line):
            if token.startswith(PROMPT_SKILL_REFERENCE_PREFIX):
                refs.add(token)
            else:
                refs.add(f"{PROMPT_SKILL_REFERENCE_PREFIX}{token}")
    return sorted(refs)


def source_asset_paths(source_root: Path, category: str) -> list[str]:
    category_root = source_root / ".github" / category
    if not category_root.is_dir():
        return []

    if category == "skills":
        return sorted(str(path.relative_to(source_root)) for path in category_root.rglob("SKILL.md"))

    suffix_map = {
        "agents": ".agent.md",
        "instructions": ".instructions.md",
        "prompts": ".prompt.md",
    }
    suffix = suffix_map.get(category)
    if not suffix:
        return []

    return sorted(str(path.relative_to(source_root)) for path in category_root.rglob(f"*{suffix}"))


def source_named_assets(source_root: Path, category: str) -> dict[str, str]:
    assets: dict[str, str] = {}
    for relative_path in source_asset_paths(source_root, category):
        display_name = asset_display_name(source_root, relative_path)
        if display_name:
            assets[display_name] = relative_path
    return assets


def markdown_named_section_items(path: Path, heading: str) -> list[str]:
    items: list[str] = []
    inside_section = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == heading:
            inside_section = True
            continue

        if not inside_section:
            continue

        if stripped.startswith("## ") or stripped.startswith("### "):
            break

        match = re.match(r"^- `([^`]+)`", stripped)
        if match:
            items.append(match.group(1))

    return items


def source_preferred_assets_from_agents_md(source_root: Path, category: str) -> list[str]:
    agents_md_path = source_root / "AGENTS.md"
    if not agents_md_path.is_file():
        return []

    heading_map = {
        "prompts": "### Preferred prompts",
        "skills": "### Preferred skills",
    }
    heading = heading_map.get(category)
    if not heading:
        return []

    named_assets = source_named_assets(source_root, category)
    preferred_names = markdown_named_section_items(agents_md_path, heading)
    return sorted(
        {
            named_assets[name]
            for name in preferred_names
            if name in named_assets
        }
    )


def repo_matches_apply_to(repo_root: Path, apply_to: str) -> bool:
    patterns = [pattern.strip() for pattern in apply_to.split(",") if pattern.strip()]
    if not patterns:
        return False

    repo_paths = [
        PurePosixPath(path.relative_to(repo_root).as_posix())
        for path in scan_repo_files(repo_root)
    ]
    return any(repo_path.match(pattern) for repo_path in repo_paths for pattern in patterns)


def markdown_headings(path: Path) -> list[str]:
    headings: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("#"):
            headings.append(stripped)
    return headings


def has_heading_exact(path: Path, heading: str) -> bool:
    return heading in markdown_headings(path)


def has_heading_regex(path: Path, pattern: str) -> bool:
    regex = re.compile(pattern)
    return any(regex.match(heading) for heading in markdown_headings(path))


def tech_ai_prompt_name(stem: str) -> str:
    remainder = stem[len("tech-ai-") :]
    output = "TechAI"
    for part in remainder.split("-"):
        if not part:
            continue
        output += part[:1].upper() + part[1:]
    return output


def prompt_expected_name(relative_path: str) -> str | None:
    name = Path(relative_path).name
    if name in PROMPT_NAME_OVERRIDES:
        return PROMPT_NAME_OVERRIDES[name]
    if name.startswith("tech-ai-") and name.endswith(".prompt.md"):
        return tech_ai_prompt_name(name[: -len(".prompt.md")])
    if name.endswith(".prompt.md"):
        return name[: -len(".prompt.md")]
    return None


def internal_asset_identifier(relative_path: str) -> str | None:
    path = Path(relative_path)
    category = asset_category(relative_path)

    if category == "prompts" and path.name.endswith(".prompt.md"):
        return path.name[: -len(".prompt.md")]
    if category == "agents" and path.name.endswith(".agent.md"):
        return path.name[: -len(".agent.md")]
    if category == "skills" and path.name == "SKILL.md":
        return path.parent.name
    return None


def has_supported_origin_prefix(identifier: str) -> bool:
    return identifier.startswith(("internal-", "local-", "obra-", "terraform-", "tech-ai-"))


def is_internal_asset_path(relative_path: str) -> bool:
    identifier = internal_asset_identifier(relative_path)
    return bool(identifier and has_supported_origin_prefix(identifier))


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
            stacks.add("docker")
        if is_composite_action_file(path):
            stacks.add("composite-action")

    if (repo_root / ".github" / "workflows").is_dir():
        stacks.add("github-actions")
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


def count_composite_action_files(files: list[Path]) -> int:
    return sum(1 for path in files if is_composite_action_file(path))


def legacy_alias_paths_for_canonical_path(canonical_relative_path: str) -> list[str]:
    aliases = set(EXTRA_LEGACY_ALIAS_PATHS.get(canonical_relative_path, ()))
    path = Path(canonical_relative_path)
    parent = path.parent.as_posix()
    name = path.name

    if canonical_relative_path.endswith(".prompt.md") and name.startswith("tech-ai-"):
        remainder = name[len("tech-ai-") :]
        aliases.add(f"{parent}/{remainder}")
        aliases.add(f"{parent}/cs-{remainder}")
    elif name == "SKILL.md" and path.parent.name.startswith("tech-ai-"):
        legacy_dir = path.parent.name[len("tech-ai-") :]
        aliases.add(f"{path.parent.parent.as_posix()}/{legacy_dir}/SKILL.md")
    elif canonical_relative_path.endswith(".agent.md") and name.startswith("tech-ai-"):
        aliases.add(f"{parent}/{name[len('tech-ai-') :]}")

    return sorted(aliases)


def known_legacy_alias_paths(source_root: Path) -> set[str]:
    aliases: set[str] = set()
    for path in scan_repo_files(source_root):
        relative_path = str(path.relative_to(source_root))
        aliases.update(legacy_alias_paths_for_canonical_path(relative_path))
    return aliases


def known_legacy_alias_map(source_root: Path) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for group in detect_canonical_asset_groups(source_root):
        if group.category not in {"prompts", "skills", "agents"}:
            continue
        canonical_path = group.paths[0]
        for alias_path in legacy_alias_paths_for_canonical_path(canonical_path):
            alias_map.setdefault(alias_path, canonical_path)
    return alias_map


def collect_target_config_assets(target_root: Path) -> dict[str, list[str]]:
    assets: dict[str, list[str]] = {category: [] for category in AGENTS_INVENTORY_CATEGORIES}
    patterns = {
        "instructions": "*.instructions.md",
        "prompts": "*.prompt.md",
        "skills": "SKILL.md",
        "agents": "*.agent.md",
    }

    for category, pattern in patterns.items():
        target_dir = target_root / ".github" / category
        if not target_dir.is_dir():
            continue
        assets[category] = sorted(str(path.relative_to(target_root)) for path in target_dir.rglob(pattern))

    return assets


def detect_target_only_assets(source_root: Path, target_root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {"prompts": [], "skills": [], "agents": []}
    known_aliases = known_legacy_alias_paths(source_root)
    manifest_paths = manifest_managed_paths(load_manifest(target_root))
    for category, pattern in (("prompts", "*.prompt.md"), ("skills", "SKILL.md"), ("agents", "*.agent.md")):
        target_dir = target_root / ".github" / category
        source_dir = source_root / ".github" / category
        if not target_dir.is_dir():
            continue

        source_relative_paths = (
            {str(path.relative_to(source_root)) for path in source_dir.rglob(pattern)} if source_dir.is_dir() else set()
        )
        for path in sorted(target_dir.rglob(pattern)):
            relative_path = str(path.relative_to(target_root))
            if relative_path in known_aliases:
                continue
            if relative_path in manifest_paths:
                continue
            if relative_path not in source_relative_paths:
                result[category].append(relative_path)
    return result


def is_canonical_source_asset(relative_path: str) -> bool:
    category = asset_category(relative_path)
    path = Path(relative_path)
    if category == "instructions":
        return path.name.endswith(".instructions.md")
    if category == "prompts":
        return path.name.startswith("tech-ai-") and path.name.endswith(".prompt.md")
    if category == "agents":
        return path.name.startswith("tech-ai-") and path.name.endswith(".agent.md")
    if category == "skills":
        return path.name == "SKILL.md" and path.parent.name.startswith("tech-ai-")
    return False


def canonical_family_name(relative_path: str) -> str:
    category = asset_category(relative_path)
    path = Path(relative_path)
    if category == "instructions":
        name = path.name[: -len(".instructions.md")]
    elif category == "prompts":
        name = path.name[: -len(".prompt.md")]
    elif category == "agents":
        name = path.name[: -len(".agent.md")]
    elif category == "skills":
        name = path.parent.name
    else:
        name = path.stem

    if name.startswith("tech-ai-"):
        return name[len("tech-ai-") :]
    return name


def detect_canonical_asset_groups(source_root: Path) -> list[CanonicalAssetGroup]:
    grouped_paths: dict[tuple[str, str], list[str]] = defaultdict(list)
    for path in scan_repo_files(source_root):
        relative_path = str(path.relative_to(source_root))
        if not is_canonical_source_asset(relative_path):
            continue
        key = (asset_category(relative_path), canonical_family_name(relative_path))
        grouped_paths[key].append(relative_path)

    groups = [
        CanonicalAssetGroup(category=category, family=family, paths=sorted(paths))
        for (category, family), paths in sorted(grouped_paths.items())
    ]
    return groups


def detect_source_legacy_aliases(source_root: Path, canonical_assets: list[CanonicalAssetGroup]) -> list[LegacyAlias]:
    aliases: list[LegacyAlias] = []
    for group in canonical_assets:
        if group.category not in {"prompts", "skills", "agents"}:
            continue
        canonical_path = group.paths[0]
        present_aliases = [
            alias_path
            for alias_path in legacy_alias_paths_for_canonical_path(canonical_path)
            if (source_root / alias_path).is_file()
        ]
        if not present_aliases:
            continue
        aliases.append(
            LegacyAlias(
                category=group.category,
                canonical_path=canonical_path,
                alias_paths=sorted(present_aliases),
            )
        )
    return aliases


def detect_role_overlaps(source_root: Path, canonical_assets: list[CanonicalAssetGroup]) -> list[RoleOverlap]:
    family_paths: dict[str, list[str]] = defaultdict(list)
    for group in canonical_assets:
        if group.category not in {"prompts", "skills", "agents"}:
            continue
        family_paths[group.family].extend(group.paths)

    overlaps: list[RoleOverlap] = []
    for family, relative_paths in sorted(family_paths.items()):
        if len(relative_paths) < 2:
            continue

        shared_lines: dict[str, set[str]] = defaultdict(set)
        examples_by_line: dict[str, str] = {}
        for relative_path in sorted(relative_paths):
            for normalized, original in extract_operational_lines(source_root / relative_path).items():
                shared_lines[normalized].add(relative_path)
                examples_by_line.setdefault(normalized, original)

        examples = [
            examples_by_line[normalized]
            for normalized, paths in sorted(shared_lines.items())
            if len(paths) >= 2
        ]
        if len(examples) < ROLE_OVERLAP_LINE_THRESHOLD:
            continue

        overlaps.append(
            RoleOverlap(
                family=family,
                asset_paths=sorted(relative_paths),
                shared_instruction_count=len(examples),
                examples=examples[:5],
            )
        )

    return overlaps


def extract_operational_lines(path: Path) -> dict[str, str]:
    lines: dict[str, str] = {}
    inside_frontmatter = False
    current_heading = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == "---":
            inside_frontmatter = not inside_frontmatter
            continue
        if inside_frontmatter:
            continue
        if stripped.startswith("#"):
            current_heading = stripped.lstrip("#").strip().lower()
            continue
        if not should_audit_operational_section(current_heading):
            continue

        item_text = extract_markdown_list_text(stripped)
        if not item_text:
            continue

        normalized = normalize_instruction_text(item_text)
        if len(normalized.split()) < 4:
            continue
        lines.setdefault(normalized, item_text)
    return lines


def should_audit_operational_section(heading: str) -> bool:
    return any(heading.startswith(prefix) for prefix in ROLE_OVERLAP_SECTION_PREFIXES)


def extract_markdown_list_text(line: str) -> str:
    if not line:
        return ""
    if line.startswith("- ") or line.startswith("* "):
        return line[2:].strip()

    match = re.match(r"^\d+\.\s+(.*)$", line)
    if match:
        return match.group(1).strip()

    return ""


def normalize_instruction_text(value: str) -> str:
    lowered = value.lower().replace("`", "")
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def detect_agents_markdown_repeats(source_root: Path) -> list[AgentsMdRepeat]:
    agents_path = source_root / "AGENTS.md"
    if not agents_path.is_file():
        return []

    current_h2 = "Introduction"
    current_section = current_h2
    references: dict[str, list[str]] = defaultdict(list)

    for raw_line in agents_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            current_h2 = stripped[3:].strip()
            current_section = current_h2
        elif stripped.startswith("### "):
            current_section = f"{current_h2} / {stripped[4:].strip()}"

        for token in re.findall(r"`([^`]+)`", stripped):
            normalized = normalize_agents_inventory_reference(token)
            if not normalized:
                continue
            references[normalized].append(current_section)

    repeats: list[AgentsMdRepeat] = []
    for reference, sections in sorted(references.items()):
        unique_sections = list(dict.fromkeys(sections))
        if len(unique_sections) < 2:
            continue
        repeats.append(
            AgentsMdRepeat(
                reference=reference,
                sections=unique_sections,
                count=len(sections),
            )
        )
    return repeats


def normalize_agents_inventory_reference(value: str) -> str | None:
    cleaned = value.strip()
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    if cleaned.startswith(".github/"):
        normalized = cleaned
    elif any(cleaned.startswith(f"{category}/") for category in AGENTS_INVENTORY_CATEGORIES):
        normalized = f".github/{cleaned}"
    else:
        return None

    if not any(f"/{category}/" in normalized for category in AGENTS_INVENTORY_CATEGORIES):
        return None
    return normalized


def build_source_audit_recommendations(
    canonical_assets: list[CanonicalAssetGroup],
    legacy_aliases: list[LegacyAlias],
    role_overlaps: list[RoleOverlap],
    agents_md_repeats: list[AgentsMdRepeat],
) -> list[str]:
    recommendations: list[str] = []

    duplicate_families = [group for group in canonical_assets if group.has_physical_duplicates]
    if duplicate_families:
        summary = ", ".join(
            f"{group.category}:{group.family}" for group in duplicate_families[:5]
        )
        recommendations.append(
            "Consolidate physical duplicate canonical asset families so each capability resolves to one real file: "
            f"{summary}."
        )

    if legacy_aliases:
        summary = ", ".join(alias.canonical_path for alias in legacy_aliases[:5])
        recommendations.append(
            "Remove or clearly deprecate source-side legacy aliases so the standards repository ships one canonical "
            f"`tech-ai-*` family per capability: {summary}."
        )

    if role_overlaps:
        summary = ", ".join(overlap.family for overlap in role_overlaps[:5])
        recommendations.append(
            "Keep detailed workflow and validation steps in the matching skill only; agent and prompt files should "
            f"remain thin entrypoints for: {summary}."
        )

    if agents_md_repeats:
        summary = ", ".join(repeat.reference for repeat in agents_md_repeats[:5])
        recommendations.append(
            "Keep asset path references in `AGENTS.md` inventory only and use capability names elsewhere to avoid "
            f"documentation repeats: {summary}."
        )

    if not recommendations:
        recommendations.append(
            "No source-side redundancy detected in canonical assets, legacy aliases, triad roles, or AGENTS.md "
            "inventory references."
        )

    return recommendations


def audit_source_configuration(source_root: Path) -> SourceAudit:
    canonical_assets = detect_canonical_asset_groups(source_root)
    legacy_aliases = detect_source_legacy_aliases(source_root, canonical_assets)
    role_overlaps = detect_role_overlaps(source_root, canonical_assets)
    agents_md_repeats = detect_agents_markdown_repeats(source_root)
    recommendations = build_source_audit_recommendations(
        canonical_assets,
        legacy_aliases,
        role_overlaps,
        agents_md_repeats,
    )
    return SourceAudit(
        canonical_assets=canonical_assets,
        legacy_aliases=legacy_aliases,
        role_overlaps=role_overlaps,
        agents_md_repeats=agents_md_repeats,
        recommendations=recommendations,
    )


def build_analysis(source_root: Path, target_root: Path, profiles: dict[str, RepoProfile]) -> TargetAnalysis:
    files = scan_repo_files(target_root)
    stacks, unsupported_stacks, extension_counts = detect_stacks(target_root, files)
    profile_name = detect_profile_name(stacks)
    if profile_name not in profiles:
        profile_name = "minimal"

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
        composite_action_count=(
            count_composite_action_files(files)
            if action_dir.is_dir() or workflow_dir.is_dir()
            else 0
        ),
        focus=detect_focus(target_root.name, stacks, target_root),
        priority_paths=detect_priority_paths(target_root, stacks),
        top_extension_counts={key: value for key, value in extension_counts.items() if value},
        target_only_assets=detect_target_only_assets(source_root, target_root),
        profile_name=profile_name,
    )


def select_assets(source_root: Path, analysis: TargetAnalysis, profiles: dict[str, RepoProfile]) -> AssetSelection:
    profile = profiles[analysis.profile_name]
    stacks = set(analysis.stacks)
    source_preferred_prompts = source_preferred_assets_from_agents_md(source_root, "prompts")
    source_preferred_skills = source_preferred_assets_from_agents_md(source_root, "skills")
    portable_source_instructions = source_asset_paths(source_root, "instructions")
    portable_source_agents = {
        agent
        for agent in source_asset_paths(source_root, "agents")
        if agent not in SOURCE_ONLY_AGENT_PATHS
    }
    instructions = {
        ".github/instructions/internal-markdown.instructions.md",
        ".github/instructions/internal-yaml.instructions.md",
    }
    profile_extra_instructions: set[str] = set()

    if "json" in stacks:
        instructions.add(".github/instructions/internal-json.instructions.md")
    if "bash" in stacks:
        instructions.add(".github/instructions/internal-bash.instructions.md")
    if "python" in stacks:
        instructions.add(".github/instructions/internal-python.instructions.md")
    if "terraform" in stacks:
        instructions.add(".github/instructions/internal-terraform.instructions.md")
    if "github-actions" in stacks:
        instructions.add(".github/instructions/internal-github-actions.instructions.md")
    if "composite-action" in stacks:
        instructions.add(".github/instructions/internal-github-action-composite.instructions.md")
    if "makefile" in stacks:
        instructions.add(".github/instructions/internal-makefile.instructions.md")
    if "nodejs" in stacks and (source_root / ".github" / "instructions" / "internal-nodejs.instructions.md").is_file():
        instructions.add(".github/instructions/internal-nodejs.instructions.md")
    if "java" in stacks and (source_root / ".github" / "instructions" / "internal-java.instructions.md").is_file():
        instructions.add(".github/instructions/internal-java.instructions.md")

    for recommended in profile.recommended_instructions:
        prefixed = ensure_github_prefix(recommended)
        if (source_root / prefixed).is_file():
            instructions.add(prefixed)
        elif prefixed != recommended and (source_root / recommended).is_file():
            instructions.add(recommended)

    for instruction_path in portable_source_instructions:
        apply_to = frontmatter_value(source_root / instruction_path, "applyTo")
        if apply_to and repo_matches_apply_to(analysis.repo_root, apply_to):
            instructions.add(instruction_path)

    profile_expected = {ensure_github_prefix(item) for item in profile.recommended_instructions}
    for item in instructions:
        if item not in profile_expected:
            profile_extra_instructions.add(item)

    prompts: set[str] = set()
    for recommended in profile.recommended_prompts:
        prefixed = ensure_github_prefix(recommended)
        if (source_root / prefixed).is_file():
            prompts.add(prefixed)
    prompts.update(source_preferred_prompts)

    if {"python", "java", "nodejs"} & set(stacks):
        prompts.add(".github/prompts/internal-add-unit-tests.prompt.md")
    if "terraform" in stacks:
        prompts.add(".github/prompts/internal-terraform-module.prompt.md")
    if "github-actions" in stacks or "composite-action" in stacks:
        prompts.add(".github/prompts/internal-github-action.prompt.md")

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
    skills.update(source_preferred_skills)

    for prompt in prompts:
        skills.update(path for path in prompt_skill_refs(source_root / prompt) if (source_root / path).is_file())

    skills = {skill for skill in skills if skill not in SOURCE_ONLY_SKILL_PATHS}

    agents: set[str] = {
        ".github/agents/internal-planner.agent.md",
        ".github/agents/internal-implementer.agent.md",
        ".github/agents/internal-reviewer.agent.md",
        ".github/agents/internal-security-reviewer.agent.md",
    }
    if "github-actions" in stacks:
        agents.add(".github/agents/internal-github-workflow-supply-chain.agent.md")
    if "terraform" in stacks:
        agents.add(".github/agents/internal-terraform-guardrails.agent.md")
    if repo_needs_iam_review(analysis.repo_root):
        agents.add(".github/agents/internal-iam-least-privilege.agent.md")
    if target_has_pr_template(analysis.repo_root):
        agents.add(".github/agents/internal-pr-editor.agent.md")
    agents.update(portable_source_agents)

    agents = {agent for agent in agents if agent not in SOURCE_ONLY_AGENT_PATHS and (source_root / agent).is_file()}

    baseline_files = [path for path in MANAGED_ALWAYS if (source_root / path).is_file()]
    validation_commands = build_validation_commands(analysis, instructions)

    preferred_prompt_candidates = {ensure_github_prefix(item) for item in profile.recommended_prompts} | set(source_preferred_prompts)
    preferred_prompts = [path for path in sorted(prompts) if path in preferred_prompt_candidates]
    if not preferred_prompts:
        preferred_prompts = sorted(prompts)[:5]

    preferred_skill_candidates = {ensure_github_prefix(item) for item in profile.recommended_skills} | set(source_preferred_skills)
    preferred_skills = [path for path in sorted(skills) if path in preferred_skill_candidates]
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


def repo_needs_data_registry(repo_root: Path, analysis: TargetAnalysis) -> bool:
    json_count = analysis.top_extension_counts.get(".json", 0)
    if json_count >= 5:
        return True

    interesting_dirs = {"authorizations", "organization", "data", "registry", "registries", "resources"}
    for path in scan_repo_files(repo_root):
        if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        relative_path = path.relative_to(repo_root)
        if relative_path.parts and relative_path.parts[0] == ".github":
            continue
        if any(part in interesting_dirs for part in relative_path.parts):
            return True

    return False


def repo_has_pytest_tests(repo_root: Path) -> bool:
    tests_dir = repo_root / "tests"
    if tests_dir.is_dir():
        for pattern in ("test_*.py", "*_test.py"):
            if any(tests_dir.rglob(pattern)):
                return True

    if (repo_root / "pytest.ini").is_file():
        return True

    pyproject = repo_root / "pyproject.toml"
    if pyproject.is_file() and "pytest" in pyproject.read_text(encoding="utf-8"):
        return True

    for requirements_file in repo_root.glob("requirements*.txt"):
        if "pytest" in requirements_file.read_text(encoding="utf-8"):
            return True

    return False


def detect_source_only_residues(target_root: Path) -> list[str]:
    residues: list[str] = []

    for relative_path in SOURCE_ONLY_TARGET_RESIDUE_PATHS:
        if (target_root / relative_path).exists():
            residues.append(relative_path)

    for relative_dir in SOURCE_ONLY_TARGET_RESIDUE_DIRECTORIES:
        if (target_root / relative_dir).exists():
            residues.append(f"{relative_dir}/**")

    return residues


def build_validation_commands(analysis: TargetAnalysis, instruction_paths: set[str] | list[str]) -> list[str]:
    commands: list[str] = []
    if "terraform" in analysis.stacks:
        commands.extend(["terraform fmt -recursive", "terraform validate"])
    if "bash" in analysis.stacks:
        commands.extend(["bash -n <changed_bash_paths>", "shellcheck -s bash <changed_bash_paths>"])
    if "python" in analysis.stacks:
        commands.append("python -m compileall <changed_python_paths>")
        if repo_has_pytest_tests(analysis.repo_root):
            commands.append("pytest")
    commands.append("python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict")
    return commands


def merged_inventory_paths(target_root: Path, selection: AssetSelection) -> dict[str, list[str]]:
    target_assets = collect_target_config_assets(target_root)
    return {
        "instructions": sorted(set(selection.instructions) | set(target_assets["instructions"])),
        "prompts": sorted(set(selection.prompts) | set(target_assets["prompts"])),
        "skills": sorted(set(selection.skills) | set(target_assets["skills"])),
        "agents": sorted(set(selection.agents) | set(target_assets["agents"])),
    }


def validate_unmanaged_prompt_asset(target_root: Path, relative_path: str, repo_local: bool = False) -> list[str]:
    path = target_root / relative_path
    frontmatter = parse_frontmatter(path)
    issues: list[str] = []

    for key in ("description", "name", "agent", "argument-hint"):
        if not frontmatter.get(key):
            issues.append(f"Missing frontmatter key `{key}`.")

    if "mode" in frontmatter:
        issues.append("Legacy prompt key `mode` found.")

    expected_name = prompt_expected_name(relative_path)
    actual_name = frontmatter.get("name", "")
    if expected_name and actual_name and actual_name != expected_name:
        issues.append(f"Prompt name policy mismatch: expected `{expected_name}`, found `{actual_name}`.")

    if repo_local:
        if not is_internal_asset_path(relative_path):
            issues.append(
                "Repository-owned prompt filename must use a supported origin prefix (`internal-`, `local-`, `obra-`, or `terraform-`)."
            )
        if actual_name and not has_supported_origin_prefix(actual_name):
            issues.append(
                "Repository-owned prompt `name` must use a supported origin prefix (`internal-`, `local-`, `obra-`, or `terraform-`)."
            )
        internal_identifier = internal_asset_identifier(relative_path)
        if internal_identifier and has_supported_origin_prefix(internal_identifier) and actual_name and actual_name != internal_identifier:
            issues.append(f"Repository-owned prompt `name` should match filename stem `{internal_identifier}`.")

    for heading in ("## Instructions", "## Validation", "## Minimal example"):
        if not has_heading_exact(path, heading):
            issues.append(f"Missing `{heading}` section.")

    refs = prompt_skill_refs(path)
    if not refs:
        issues.append("Missing skill reference.")
        return issues

    for ref in refs:
        if not (target_root / ref).is_file():
            issues.append(f"Referenced skill path is missing: `{ref}`.")

    return issues


def validate_unmanaged_skill_asset(target_root: Path, relative_path: str, repo_local: bool = False) -> list[str]:
    path = target_root / relative_path
    frontmatter = parse_frontmatter(path)
    issues: list[str] = []

    for key in ("name", "description"):
        if not frontmatter.get(key):
            issues.append(f"Missing frontmatter key `{key}`.")

    if not has_heading_regex(path, r"^## When to [Uu]se$"):
        issues.append("Missing `## When to use` section.")
    if not has_heading_regex(path, r"^## (Validation|Checklist|Testing|Test stack)$"):
        issues.append("Missing validation/testing section.")

    if repo_local:
        internal_identifier = internal_asset_identifier(relative_path)
        actual_name = frontmatter.get("name", "")
        if not is_internal_asset_path(relative_path):
            issues.append(
                "Repository-owned skill directory must use a supported origin prefix (`internal-`, `local-`, `obra-`, or `terraform-`)."
            )
        if actual_name and not has_supported_origin_prefix(actual_name):
            issues.append(
                "Repository-owned skill `name` must use a supported origin prefix (`internal-`, `local-`, `obra-`, or `terraform-`)."
            )
        if internal_identifier and has_supported_origin_prefix(internal_identifier) and actual_name and actual_name != internal_identifier:
            issues.append(f"Repository-owned skill `name` should match directory name `{internal_identifier}`.")

    return issues


def validate_unmanaged_agent_asset(target_root: Path, relative_path: str, repo_local: bool = False) -> list[str]:
    path = target_root / relative_path
    frontmatter = parse_frontmatter(path)
    issues: list[str] = []

    for key in ("name", "description", "tools"):
        if not frontmatter.get(key):
            issues.append(f"Missing frontmatter key `{key}`.")

    if not any(heading.startswith("# ") for heading in markdown_headings(path)):
        issues.append("Missing top heading.")
    if not has_heading_exact(path, "## Objective"):
        issues.append("Missing `## Objective` section.")
    if not has_heading_exact(path, "## Restrictions"):
        issues.append("Missing `## Restrictions` section.")

    if repo_local:
        internal_identifier = internal_asset_identifier(relative_path)
        actual_name = frontmatter.get("name", "")
        if not is_internal_asset_path(relative_path):
            issues.append(
                "Repository-owned agent filename must use a supported origin prefix (`internal-`, `local-`, `obra-`, or `terraform-`)."
            )
        if actual_name and not has_supported_origin_prefix(actual_name):
            issues.append(
                "Repository-owned agent `name` must use a supported origin prefix (`internal-`, `local-`, `obra-`, or `terraform-`)."
            )
        if internal_identifier and has_supported_origin_prefix(internal_identifier) and actual_name and actual_name != internal_identifier:
            issues.append(f"Repository-owned agent `name` should match filename stem `{internal_identifier}`.")

    return issues


def validate_unmanaged_instruction_asset(target_root: Path, relative_path: str, repo_local: bool = False) -> list[str]:
    path = target_root / relative_path
    frontmatter = parse_frontmatter(path)
    issues: list[str] = []

    for key in ("applyTo", "description"):
        if not frontmatter.get(key):
            issues.append(f"Missing frontmatter key `{key}`.")

    if not any(heading.startswith("# ") for heading in markdown_headings(path)):
        issues.append("Missing top heading.")

    return issues


def detect_unmanaged_target_asset_issues(
    source_root: Path,
    target_root: Path,
    selection: AssetSelection,
) -> list[TargetAssetIssue]:
    alias_map = known_legacy_alias_map(source_root)
    managed_paths = set(selection.managed_source_paths)
    managed_paths.update(manifest_managed_paths(load_manifest(target_root)))
    validators = {
        "instructions": validate_unmanaged_instruction_asset,
        "prompts": validate_unmanaged_prompt_asset,
        "skills": validate_unmanaged_skill_asset,
        "agents": validate_unmanaged_agent_asset,
    }

    issues: list[TargetAssetIssue] = []
    for category, relative_paths in collect_target_config_assets(target_root).items():
        validator = validators[category]
        for relative_path in relative_paths:
            if relative_path in managed_paths:
                continue

            issue_types: list[str] = []
            details: list[str] = []
            canonical_source_path = alias_map.get(relative_path)
            repo_local = canonical_source_path is None and not (source_root / relative_path).is_file()

            if canonical_source_path:
                issue_types.append("legacy_alias")
                details.append(f"Legacy alias of `{canonical_source_path}`.")

            validation_issues = validator(target_root, relative_path, repo_local=repo_local)
            if validation_issues:
                issue_types.append("validation")
                if any(detail.startswith("Repository-internal ") for detail in validation_issues):
                    issue_types.append("internal_naming")
                details.extend(validation_issues)

            if not issue_types:
                continue

            issues.append(
                TargetAssetIssue(
                    category=category,
                    target_relative_path=relative_path,
                    issue_types=issue_types,
                    details=sorted(dict.fromkeys(details)),
                    severity="error" if "validation" in issue_types else "warn",
                    canonical_source_path=canonical_source_path,
                )
            )

    return sorted(issues, key=lambda item: (item.category, item.target_relative_path))


def detect_editor_integration_issues(target_root: Path) -> list[TargetAssetIssue]:
    settings_path = target_root / VSCODE_SETTINGS_RELATIVE_PATH
    if not settings_path.is_file():
        return [
            TargetAssetIssue(
                category="editor",
                target_relative_path=VSCODE_SETTINGS_RELATIVE_PATH,
                issue_types=["editor_integration"],
                details=[
                    "Missing VS Code workspace settings; add "
                    f"`{PR_DESCRIPTION_SETTING_KEY}` set to `{PR_DESCRIPTION_SETTING_VALUE}` "
                    "to default the GitHub Pull Requests form to the repository template."
                ],
                severity="warn",
            )
        ]

    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [
            TargetAssetIssue(
                category="editor",
                target_relative_path=VSCODE_SETTINGS_RELATIVE_PATH,
                issue_types=["editor_integration", "validation"],
                details=[
                    "Invalid JSON in VS Code workspace settings: "
                    f"{error.msg} (line {error.lineno}, column {error.colno})."
                ],
                severity="error",
            )
        ]

    if not isinstance(settings, dict):
        return [
            TargetAssetIssue(
                category="editor",
                target_relative_path=VSCODE_SETTINGS_RELATIVE_PATH,
                issue_types=["editor_integration", "validation"],
                details=[
                    "VS Code workspace settings must be a JSON object so "
                    f"`{PR_DESCRIPTION_SETTING_KEY}` can be resolved."
                ],
                severity="error",
            )
        ]

    configured_value = settings.get(PR_DESCRIPTION_SETTING_KEY)
    if configured_value == PR_DESCRIPTION_SETTING_VALUE:
        return []

    if configured_value is None:
        detail = (
            f"Missing `{PR_DESCRIPTION_SETTING_KEY}` in VS Code workspace settings; set it to "
            f"`{PR_DESCRIPTION_SETTING_VALUE}` to default the GitHub Pull Requests form to the "
            "repository template."
        )
    else:
        detail = (
            f"`{PR_DESCRIPTION_SETTING_KEY}` must be `{PR_DESCRIPTION_SETTING_VALUE}`, found "
            f"{json.dumps(configured_value, sort_keys=True)}."
        )

    return [
        TargetAssetIssue(
            category="editor",
            target_relative_path=VSCODE_SETTINGS_RELATIVE_PATH,
            issue_types=["editor_integration"],
            details=[detail],
            severity="warn",
        )
    ]


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


def detect_redundant_assets(source_root: Path, target_root: Path, selection: AssetSelection) -> list[RedundantAsset]:
    selected_paths = set(selection.managed_source_paths)
    redundant_assets: list[RedundantAsset] = []

    canonical_candidates = set(known_legacy_alias_map(source_root).values())
    canonical_candidates.update(
        path for path in selected_paths if asset_category(path) in {"prompts", "skills", "agents"}
    )
    canonical_candidates.update(
        str(path.relative_to(target_root))
        for path in scan_repo_files(target_root)
        if is_canonical_source_asset(str(path.relative_to(target_root)))
        and asset_category(str(path.relative_to(target_root))) in {"prompts", "skills", "agents"}
    )

    for canonical_relative_path in sorted(canonical_candidates):
        legacy_aliases = legacy_alias_paths_for_canonical_path(canonical_relative_path)
        if not legacy_aliases:
            continue

        canonical_exists = (target_root / canonical_relative_path).is_file()
        present_aliases = [path for path in legacy_aliases if (target_root / path).is_file()]
        present_variants = ([canonical_relative_path] if canonical_exists else []) + present_aliases
        selected_for_sync = canonical_relative_path in selected_paths

        if len(present_variants) >= 2:
            redundant_assets.append(
                RedundantAsset(
                    category=asset_category(canonical_relative_path),
                    canonical_target_path=canonical_relative_path,
                    existing_target_paths=present_variants,
                    issue_type="existing_redundancy",
                    selected_for_sync=selected_for_sync,
                )
            )
            continue

        if selected_for_sync and present_aliases and not canonical_exists:
            redundant_assets.append(
                RedundantAsset(
                    category=asset_category(canonical_relative_path),
                    canonical_target_path=canonical_relative_path,
                    existing_target_paths=present_aliases,
                    issue_type="sync_would_duplicate",
                    selected_for_sync=True,
                )
            )
            continue

        if present_aliases and not canonical_exists:
            redundant_assets.append(
                RedundantAsset(
                    category=asset_category(canonical_relative_path),
                    canonical_target_path=canonical_relative_path,
                    existing_target_paths=present_aliases,
                    issue_type="legacy_alias_only",
                    selected_for_sync=False,
                )
            )

    return redundant_assets


def apply_redundancy_conflicts(
    actions: list[FileAction],
    redundant_assets: list[RedundantAsset],
    agents_relative_path: str,
) -> list[FileAction]:
    action_by_target_path = {action.target_relative_path: action for action in actions}
    blocks_agents_inventory = False

    for redundant_asset in redundant_assets:
        if not redundant_asset.selected_for_sync:
            continue

        action = action_by_target_path.get(redundant_asset.canonical_target_path)
        if action is None:
            continue

        if action.status == "conflict":
            action.reason = f"{action.reason} Also, {redundant_asset.reason}"
        else:
            action.status = "conflict"
            action.reason = redundant_asset.reason
        blocks_agents_inventory = True

    if not blocks_agents_inventory:
        return actions

    agents_action = action_by_target_path.get(agents_relative_path)
    if agents_action is not None and agents_action.status != "conflict":
        agents_action.status = "conflict"
        agents_action.reason = (
            "Redundant legacy prompt, skill, or agent aliases were detected in the target. Resolve duplicate "
            "configuration families before regenerating `AGENTS.md` inventory."
        )

    return actions


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


def manifest_managed_paths(manifest: dict[str, object]) -> set[str]:
    managed_files = manifest.get("managed_files", {})
    if not isinstance(managed_files, dict):
        return set()
    return {relative_path for relative_path, entry in managed_files.items() if isinstance(relative_path, str) and isinstance(entry, dict)}


def plan_actions(target_root: Path, planned_files: list[PlannedFile], manifest: dict[str, object]) -> list[FileAction]:
    actions: list[FileAction] = []
    managed_files = manifest.get("managed_files", {})
    if not isinstance(managed_files, dict):
        managed_files = {}
    planned_target_paths = {planned_file.target_relative_path for planned_file in planned_files}

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

    for managed_relative_path, managed_entry in sorted(managed_files.items()):
        if managed_relative_path in planned_target_paths or managed_relative_path == MANIFEST_RELATIVE_PATH:
            continue
        if not isinstance(managed_entry, dict):
            continue

        target_path = target_root / managed_relative_path
        if not target_path.is_file():
            continue

        current_sha256 = sha256_path(target_path)
        recorded_sha256 = str(managed_entry.get("sha256", ""))
        if current_sha256 != recorded_sha256:
            actions.append(
                FileAction(
                    target_relative_path=managed_relative_path,
                    source_relative_path=managed_entry.get("source_relative_path"),
                    status="conflict",
                    category=asset_category(managed_relative_path),
                    reason="Source-managed file was removed from the desired baseline but changed locally after the last sync.",
                    desired_sha256="",
                    current_sha256=current_sha256,
                    generated=bool(managed_entry.get("generated", False)),
                )
            )
            continue

        actions.append(
            FileAction(
                target_relative_path=managed_relative_path,
                source_relative_path=managed_entry.get("source_relative_path"),
                status="delete",
                category=asset_category(managed_relative_path),
                reason="Remove a source-managed file that is no longer part of the desired baseline.",
                desired_sha256="",
                current_sha256=current_sha256,
                generated=bool(managed_entry.get("generated", False)),
            )
        )

    return actions


def render_agents_markdown(analysis: TargetAnalysis, selection: AssetSelection, source_root: Path) -> str:
    instructions_apply_to = build_instruction_rule_pairs(source_root, selection.instructions)
    preferred_prompts = preferred_asset_lines(source_root, selection.preferred_prompts)
    preferred_skills = preferred_asset_lines(source_root, selection.preferred_skills)
    inventory_paths = merged_inventory_paths(analysis.repo_root, selection)
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
        "- External resources must use `<short-repo>-<original-resource-name>` in filenames and `name:` values.",
        "- Resources created in `cloud-strategy.github` must use the `internal-` prefix in filenames and `name:` values.",
        "- Resources created in other local repositories must use the `local-` prefix in filenames and `name:` values.",
        "- Keep legacy prefixes only when required for backward compatibility.",
        "",
        "## Decision Priority",
        "1. Apply repository non-negotiables from `.github/copilot-instructions.md`.",
        "2. Apply explicit user requirements for the current task.",
        "3. Apply the selected agent behavior (agent-first routing).",
        "4. Apply matching files under `.github/instructions/*.instructions.md` using `applyTo`.",
        "5. Apply selected prompt constraints from `.github/prompts/*.prompt.md`.",
        "6. Apply implementation details from referenced `.github/skills/*/SKILL.md`.",
        "7. If no agent is explicitly selected, use the matching instructions, prompts, and skills directly.",
        "",
        "## Agent Routing",
        "",
        "### When to use each agent",
    ]
    lines.extend(agent_routing_lines(source_root, selection.agents))
    lines.extend(
        [
            "",
            "### Agent composition",
            "- For changes spanning multiple specialist domains, run each relevant specialist and aggregate findings.",
            "- The standard path for non-trivial work is: planning capability -> implementation capability -> review capability, or a matching specialist.",
            "",
            "## Governance References",
        ]
    )
    lines.extend(f"- `{path}`" for path in governance_references)
    lines.extend(
        [
            "",
            "## Prohibitions",
            "- Apply all non-negotiables from `.github/copilot-instructions.md` plus:",
            "- Never run destructive commands unless explicitly requested.",
            "- Never skip validation after making changes.",
            "",
            "## Repository Defaults",
            f"- Primary focus: {analysis.focus}",
            f"- Profile hint: `{selection.profile.name}`",
            "- AGENTS.md is the external bridge for assistant behavior and naming; keep runtime references abstract.",
            "- Resolve stack from target files and explicit prompt inputs; the agent role remains behavioral, not language-specific.",
            "- Prioritize these paths:",
        ]
    )
    lines.extend(f"  - `{path}`" for path in analysis.priority_paths)
    lines.extend(["", "### Default instruction routing", "| Pattern | Instruction |", "| --- | --- |"])
    lines.extend(f"| `{pattern}` | `{label}` |" for pattern, label in instructions_apply_to)
    lines.extend(["", "### Preferred prompts"])
    lines.extend(preferred_prompts)
    lines.extend(["", "### Preferred skills"])
    lines.extend(preferred_skills)
    lines.extend(["", "### Required validations before PR"])
    lines.extend(f"- `{command}`" for command in selection.validation_commands)
    lines.extend(
        [
            "",
            "## Repository Inventory (Auto-generated)",
            "This inventory reflects the desired managed baseline plus repository-owned internal Copilot assets already present in the target repository.",
            "",
            "### Instructions",
        ]
    )
    lines.extend(f"- `{path}`" for path in inventory_paths["instructions"])
    lines.extend(["", "### Prompts"])
    lines.extend(f"- `{path}`" for path in inventory_paths["prompts"])
    lines.extend(["", "### Skills"])
    lines.extend(f"- `{path}`" for path in inventory_paths["skills"])
    lines.extend(["", "### Agents"])
    lines.extend(f"- `{path}`" for path in inventory_paths["agents"])

    return "\n".join(lines) + "\n"


def strip_github_prefix(value: str) -> str:
    if value.startswith(".github/"):
        return value[len(".github/") :]
    return value


def build_instruction_rule_pairs(source_root: Path, instruction_paths: list[str]) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    for instruction_path in instruction_paths:
        apply_to = frontmatter_value(source_root / instruction_path, "applyTo")
        if not apply_to:
            continue
        label = Path(strip_github_prefix(instruction_path)).name
        rules.append((apply_to, label))
    return rules


def preferred_asset_lines(source_root: Path, relative_paths: list[str]) -> list[str]:
    lines: list[str] = []
    for relative_path in relative_paths:
        name = asset_display_name(source_root, relative_path)
        lines.append(f"- `{name}`")
    return lines


def asset_display_name(source_root: Path, relative_path: str) -> str:
    asset_path = source_root / relative_path
    category = asset_category(relative_path)
    if category in {"prompts", "agents"}:
        return frontmatter_value(asset_path, "name") or asset_path.stem
    if category == "skills":
        return frontmatter_value(asset_path, "name") or asset_path.parent.name
    return Path(strip_github_prefix(relative_path)).name


def agent_routing_lines(source_root: Path, agent_paths: list[str]) -> list[str]:
    explicit_lines = {
        "tech-ai-planner.agent.md": "- Use the installed planning capability for ambiguous scope, tradeoff analysis, or multi-step design.",
        "tech-ai-implementer.agent.md": "- Use the installed implementation capability for direct code/config changes and validation-first delivery.",
        "tech-ai-reviewer.agent.md": "- Use the installed review capability for quality gates and defect/regression findings.",
        "tech-ai-terraform-guardrails.agent.md": "- Use the installed Terraform guardrail reviewer for Terraform safety and policy checks.",
        "tech-ai-iam-least-privilege.agent.md": "- Use the installed IAM least-privilege reviewer for role and permission scoping checks.",
        "tech-ai-github-workflow-supply-chain.agent.md": "- Use the installed workflow supply-chain reviewer for CI and workflow hardening checks.",
        "tech-ai-security-reviewer.agent.md": "- Use the installed security review capability as the security-focused gate.",
        "tech-ai-pr-editor.agent.md": "- Use the installed PR editor capability when generating pull request content from the repository template.",
    }
    lines: list[str] = []
    for relative_path in sorted(agent_paths):
        filename = Path(relative_path).name
        if filename in explicit_lines:
            lines.append(explicit_lines[filename])
            continue

        asset_path = source_root / relative_path
        name = frontmatter_value(asset_path, "name") or asset_path.stem
        description = frontmatter_value(asset_path, "description").strip()
        if not description:
            lines.append(f"- Use `{name}` when its specialization matches the task.")
            continue

        first_sentence = description.split(".", 1)[0].strip().rstrip(".")
        if first_sentence:
            first_sentence = f"{first_sentence[0].lower()}{first_sentence[1:]}"
            lines.append(f"- Use `{name}` to {first_sentence}.")
        else:
            lines.append(f"- Use `{name}` when its specialization matches the task.")
    return lines


def build_recommendations(
    analysis: TargetAnalysis,
    selection: AssetSelection,
    actions: list[FileAction],
    redundant_assets: list[RedundantAsset],
    target_asset_issues: list[TargetAssetIssue],
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
    target_only_skill_assets = analysis.target_only_assets.get("skills", [])
    if target_only_prompt_assets or target_only_skill_assets:
        target_only_summary: list[str] = []
        if target_only_prompt_assets:
            target_only_summary.append(f"prompts: {', '.join(target_only_prompt_assets)}")
        if target_only_skill_assets:
            target_only_summary.append(f"skills: {', '.join(target_only_skill_assets)}")
        recommendations["missing instructions/prompts/skills"].append(
            "The target repository already contains Copilot assets that are not available in the source standards "
            f"repo: {'; '.join(target_only_summary)}."
        )

    legacy_alias_issues = [
        f"{issue.target_relative_path} -> {issue.canonical_source_path}"
        for issue in target_asset_issues
        if "legacy_alias" in issue.issue_types and issue.canonical_source_path
    ]
    if legacy_alias_issues:
        recommendations["weak conflict-handling rules"].append(
            "The target repository still contains legacy prompt/skill/agent aliases outside the selected baseline: "
            f"{', '.join(legacy_alias_issues)}."
        )

    validation_issue_paths = [
        issue.target_relative_path for issue in target_asset_issues if "validation" in issue.issue_types
    ]
    if validation_issue_paths:
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "The target repository contains unmanaged Copilot assets with strict-validation gaps: "
            f"{', '.join(validation_issue_paths)}."
        )

    internal_naming_issue_paths = [
        issue.target_relative_path for issue in target_asset_issues if "internal_naming" in issue.issue_types
    ]
    if internal_naming_issue_paths:
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "Repository-owned Copilot prompts, skills, and agents should use origin-based prefixes in both filenames "
            "and `name:` values (`internal-*`, `local-*`, or the supported external short-repo prefixes): "
            f"{', '.join(internal_naming_issue_paths)}."
        )

    editor_integration_issue_paths = [
        issue.target_relative_path for issue in target_asset_issues if "editor_integration" in issue.issue_types
    ]
    if editor_integration_issue_paths:
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "The target repository is missing the VS Code GitHub Pull Requests setting "
            f"`{PR_DESCRIPTION_SETTING_KEY} = \"{PR_DESCRIPTION_SETTING_VALUE}\"`; add it in "
            f"`{VSCODE_SETTINGS_RELATIVE_PATH}` to use the repository PR template by default in the PR form."
        )

    source_only_residues = detect_source_only_residues(analysis.repo_root)
    if source_only_residues:
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "The target repository still contains source-only bootstrap residues that should not be treated as "
            f"consumer baseline assets: {', '.join(source_only_residues)}."
        )

    if any(action.target_relative_path == analysis.agents_relative_path and action.status == "conflict" for action in actions):
        recommendations["weak conflict-handling rules"].append(
            "Consider generated section markers or a dedicated root-AGENTS template to reduce consumer AGENTS "
            "merge conflicts."
        )

    if any(asset.selected_for_sync for asset in redundant_assets):
        recommendations["weak conflict-handling rules"].append(
            "Keep the sync alias map current when canonical `tech-ai-*` assets replace legacy `cs-*` or "
            "unprefixed consumer assets, so sync can stop before creating redundant configuration families."
        )

    if not (analysis.repo_root / "AGENTS.md").exists() and (analysis.repo_root / ".github" / "AGENTS.md").exists():
        recommendations["missing consumer-facing validation or onboarding guidance"].append(
            "Move legacy `.github/AGENTS.md` to root `AGENTS.md`; root is the canonical location for project "
            "agent routing and inventory."
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


def apply_plan(target_root: Path, plan: SyncPlan, planned_files: list[PlannedFile], source_root: Path) -> None:
    content_map = {item.target_relative_path: item for item in planned_files}
    for action in plan.actions:
        target_path = target_root / action.target_relative_path
        if action.status in {"create", "update"}:
            planned_file = content_map[action.target_relative_path]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(planned_file.desired_content, encoding="utf-8")
            continue

        if action.status == "delete" and target_path.is_file():
            target_path.unlink()
            prune_empty_parent_dirs(target_path, target_root)

    manifest = {
        "tool": SCRIPT_NAME,
        "version": 1,
        "generated_at_utc": utc_now(),
        "target_repo": str(target_root),
        "profile": plan.selection.profile.name,
        "source_version": read_source_version(source_root),
        "source_commit": git_commit_sha(source_root),
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
        "# internal-sync-global-copilot-configs-into-repo Report",
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
    ]
    lines.extend(render_source_audit_markdown(plan.source_audit))
    lines.extend(
        [
            "",
            "## Unmanaged target asset issues",
        ]
    )
    if not plan.target_asset_issues:
        lines.append("- None")
    else:
        for issue in plan.target_asset_issues:
            issue_types = ", ".join(issue.issue_types)
            details = "; ".join(issue.details)
            lines.append(
                f"- `{issue.target_relative_path}` [{issue.severity}] ({issue.category}; {issue_types}): {details}"
            )

    lines.extend(
        [
            "",
            "## Redundant or legacy target assets",
        ]
    )
    if not plan.redundant_assets:
        lines.append("- None")
    else:
        for redundant_asset in plan.redundant_assets:
            lines.append(
                f"- `{redundant_asset.category}` canonical `{redundant_asset.canonical_target_path}` overlaps with "
                f"{', '.join(f'`{path}`' for path in redundant_asset.existing_target_paths)}"
                f" ({redundant_asset.issue_type})"
            )

    lines.extend(
        [
            "",
        "## Planned or applied actions",
        ]
    )
    for status in ("create", "update", "delete", "adopt", "unchanged", "conflict"):
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

    lines.extend(["", "## Target-driven recommendations"])
    for category, items in plan.recommendations.items():
        lines.append(f"### {category.title()}")
        for item in items:
            lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def render_source_audit_markdown(source_audit: SourceAudit) -> list[str]:
    lines = ["## Source configuration audit", "", "### canonical_assets"]
    grouped: dict[str, list[CanonicalAssetGroup]] = defaultdict(list)
    for asset in source_audit.canonical_assets:
        grouped[asset.category].append(asset)

    for category in AGENTS_INVENTORY_CATEGORIES:
        assets = grouped.get(category, [])
        if not assets:
            continue
        duplicate_families = [asset for asset in assets if asset.has_physical_duplicates]
        if duplicate_families:
            duplicate_summary = "; ".join(
                f"`{asset.family}` -> {', '.join(f'`{path}`' for path in asset.paths)}"
                for asset in duplicate_families
            )
            lines.append(
                f"- `{category}`: {len(assets)} canonical families; physical duplicates: {duplicate_summary}"
            )
        else:
            lines.append(f"- `{category}`: {len(assets)} canonical families; no physical duplicates.")

    lines.extend(["", "### legacy_aliases"])
    if not source_audit.legacy_aliases:
        lines.append("- None")
    else:
        for alias in source_audit.legacy_aliases:
            lines.append(
                f"- `{alias.canonical_path}` has legacy aliases {', '.join(f'`{path}`' for path in alias.alias_paths)}"
            )

    lines.extend(["", "### role_overlaps"])
    if not source_audit.role_overlaps:
        lines.append("- None")
    else:
        for overlap in source_audit.role_overlaps:
            lines.append(
                f"- `{overlap.family}` shares {overlap.shared_instruction_count} operational lines across "
                f"{', '.join(f'`{path}`' for path in overlap.asset_paths)}"
            )
            for example in overlap.examples:
                lines.append(f"- Example for `{overlap.family}`: `{example}`")

    lines.extend(["", "### agents_md_repeats"])
    if not source_audit.agents_md_repeats:
        lines.append("- None")
    else:
        for repeat in source_audit.agents_md_repeats:
            lines.append(
                f"- `{repeat.reference}` appears in {', '.join(f'`{section}`' for section in repeat.sections)}"
            )

    lines.extend(["", "### recommendations"])
    for item in source_audit.recommendations:
        lines.append(f"- {item}")
    return lines


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
            "unmanaged_target_asset_issues": [
                {
                    "category": issue.category,
                    "target_relative_path": issue.target_relative_path,
                    "issue_types": issue.issue_types,
                    "details": issue.details,
                    "severity": issue.severity,
                    "canonical_source_path": issue.canonical_source_path,
                }
                for issue in plan.target_asset_issues
            ],
            "redundant_assets": [
                {
                    "category": asset.category,
                    "canonical_target_path": asset.canonical_target_path,
                    "existing_target_paths": asset.existing_target_paths,
                    "issue_type": asset.issue_type,
                    "selected_for_sync": asset.selected_for_sync,
                }
                for asset in plan.redundant_assets
            ],
        },
        "source_audit": {
            "canonical_assets": [
                {
                    "category": asset.category,
                    "family": asset.family,
                    "paths": asset.paths,
                    "has_physical_duplicates": asset.has_physical_duplicates,
                }
                for asset in plan.source_audit.canonical_assets
            ],
            "legacy_aliases": [
                {
                    "category": alias.category,
                    "canonical_path": alias.canonical_path,
                    "alias_paths": alias.alias_paths,
                }
                for alias in plan.source_audit.legacy_aliases
            ],
            "role_overlaps": [
                {
                    "family": overlap.family,
                    "asset_paths": overlap.asset_paths,
                    "shared_instruction_count": overlap.shared_instruction_count,
                    "examples": overlap.examples,
                }
                for overlap in plan.source_audit.role_overlaps
            ],
            "agents_md_repeats": [
                {
                    "reference": repeat.reference,
                    "sections": repeat.sections,
                    "count": repeat.count,
                }
                for repeat in plan.source_audit.agents_md_repeats
            ],
            "recommendations": plan.source_audit.recommendations,
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
    redundant_assets = detect_redundant_assets(source_root, target_root, selection)
    target_asset_issues = detect_unmanaged_target_asset_issues(source_root, target_root, selection)
    target_asset_issues.extend(detect_editor_integration_issues(target_root))
    target_asset_issues = sorted(target_asset_issues, key=lambda item: (item.category, item.target_relative_path))
    source_audit = audit_source_configuration(source_root)
    actions = apply_redundancy_conflicts(actions, redundant_assets, analysis.agents_relative_path)
    recommendations = build_recommendations(
        analysis,
        selection,
        actions,
        redundant_assets,
        target_asset_issues,
        source_root,
    )
    return (
        SyncPlan(
            analysis=analysis,
            selection=selection,
            actions=actions,
            redundant_assets=redundant_assets,
            target_asset_issues=target_asset_issues,
            source_audit=source_audit,
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
        apply_plan(target_root, plan, planned_files, source_root)
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
