from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

import yaml

FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
LEGACY_AGENT_TOOL_IDS = {
    "terminalCommand",
    "search/codebase",
    "search/searchResults",
    "search/usages",
    "edit/editFiles",
    "execute/runInTerminal",
    "web/fetch",
    "read/problems",
}
IGNORED_SYNC_FILENAMES = {"README.md", "CHANGELOG.md"}
IGNORED_SYNC_PARTS = {"__pycache__", ".venv"}
CONSUMER_SYNC_EXCLUDED_PREFIX = "internal-sync-"
LESSONS_PATH = "LESSONS_LEARNED.md"
ARCHITECTURE_PATH = "docs/01-local-architecture.md"
REPOSITORY_CONTEXT_PATH = "docs/02-local-repository-context.md"
RETIRED_RUNTIME_OPERATING_MODEL_PATH = "docs/03-local-ai-runtime-operating-model.md"
LEGACY_ARCHITECTURE_PATH = "docs/architecture.md"
LEGACY_RUNTIME_FIT_PATH = "docs/runtime-fit.md"
ARCHITECTURE_TEMPLATE_PATH = ".github/templates/01-architecture.md.template"
REPOSITORY_CONTEXT_TEMPLATE_PATH = ".github/templates/02-repository-context.md.template"
COPILOT_INSTRUCTIONS_OVERRIDE_TEMPLATE_PATH = (
    ".github/templates/copilot-instructions.override.md.template"
)
COPILOT_INSTRUCTIONS_OVERRIDE_PATH = ".github/copilot-instructions.override.md"
CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES = {
    ARCHITECTURE_PATH: ARCHITECTURE_TEMPLATE_PATH,
    REPOSITORY_CONTEXT_PATH: REPOSITORY_CONTEXT_TEMPLATE_PATH,
}
MANAGED_ROOT_FILES = (
    "AGENTS.md",
    LESSONS_PATH,
    ".editorconfig",
    ".pre-commit-config.yaml",
    ".github/copilot-instructions.md",
    ".github/copilot-code-review-instructions.md",
    ".github/copilot-commit-message-instructions.md",
    ".github/security-baseline.md",
    ".github/DEPRECATION.md",
    ".github/repo-profiles.yml",
)
MANAGED_WORKFLOW_FILES = (".github/workflows/_pre-commit.yml",)
INVENTORY_PATH = ".github/INVENTORY.md"
IMPORTED_ASSET_OVERRIDES_PATH = ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
SUPERPOWERS_NORMALIZATION_PATH = ".github/skills/local-agent-sync-external-resources/references/superpowers-normalization.yaml"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass(frozen=True)
class SyncOperation:
    action: str
    path: str
    reason: str
    source_hash: str | None = None
    target_hash: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "action": self.action,
            "path": self.path,
            "reason": self.reason,
            "source_hash": self.source_hash,
            "target_hash": self.target_hash,
        }


@dataclass(frozen=True)
class SyncPlan:
    source_root: Path
    target_root: Path
    source_revision: str | None
    source_version: str | None
    target_manifest_source_version: str | None
    target_dirty: bool
    stacks: tuple[str, ...]
    operations: tuple[SyncOperation, ...]
    local_assets: tuple[str, ...]
    generated_inventory: str
    generated_lessons: str | None = None
    generated_gitignore: str | None = None
    dirty_paths: tuple[str, ...] = ()
    managed_mutation_paths: tuple[str, ...] = ()
    dirty_managed_overlap: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "source_root": self.source_root.as_posix(),
            "target_root": self.target_root.as_posix(),
            "source_revision": self.source_revision,
            "source_version": self.source_version,
            "target_manifest_source_version": self.target_manifest_source_version,
            "target_dirty": self.target_dirty,
            "stacks": list(self.stacks),
            "local_assets": list(self.local_assets),
            "dirty_paths": list(self.dirty_paths),
            "managed_mutation_paths": list(self.managed_mutation_paths),
            "dirty_managed_overlap": list(self.dirty_managed_overlap),
            "operations": [operation.to_dict() for operation in self.operations],
        }


def log_info(message: str) -> None:
    print(f"ℹ️  {message}", flush=True)


def log_warn(message: str) -> None:
    print(f"⚠️  {message}", flush=True)


def log_success(message: str) -> None:
    print(f"✅ {message}", flush=True)


def log_error(message: str) -> None:
    print(f"❌ {message}", flush=True)


def find_repo_root(start: Path) -> Path:
    candidate = start.resolve()
    for current in (candidate, *candidate.parents):
        if (current / ".github").is_dir() or (current / ".git").exists():
            return current
    raise FileNotFoundError(f"Unable to find repository root from {start}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def is_git_dirty(root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def git_dirty_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout:
        return []

    entries = result.stdout.decode("utf-8", errors="replace").split("\0")
    dirty_paths: list[str] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue

        status = entry[:2]
        path = entry[3:]
        if path:
            dirty_paths.append(path)

        if "R" in status or "C" in status:
            if index < len(entries):
                renamed_path = entries[index]
                index += 1
                if renamed_path:
                    dirty_paths.append(renamed_path)

    return sorted(dedupe_preserve_order(dirty_paths))


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---"):
        return {}, text

    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, text

    frontmatter_text = match.group(1)
    try:
        parsed = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    return parsed, text[match.end() :]


def load_frontmatter(path: Path) -> dict[str, object]:
    return split_frontmatter(read_text(path))[0]


def strip_frontmatter(text: str) -> str:
    return split_frontmatter(text)[1]


def markdown_link_targets(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def normalize_markdown_text(text: str) -> str:
    normalized_lines: list[str] = []
    in_code_block = False
    for raw_line in strip_frontmatter(text).splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        cleaned = re.sub(r"^[#>*\-\d\.)\s]+", "", line).replace("`", "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
        if cleaned:
            normalized_lines.append(cleaned)
    return "\n".join(normalized_lines)


def significant_text_lines(text: str) -> set[str]:
    return {
        line
        for line in normalize_markdown_text(text).splitlines()
        if len(line) >= 18 and not line.startswith("http")
    }


def render_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def iter_markdown_assets(root: Path) -> Iterator[Path]:
    candidates = [root / "AGENTS.md"]
    github_root = root / ".github"
    if github_root.exists():
        candidates.extend(
            path
            for path in github_root.rglob("*.md")
            if path.is_file()
            and not any(part in IGNORED_SYNC_PARTS for part in path.parts)
        )
    for path in candidates:
        if path.exists():
            yield path


def is_ignored_sync_path(relative_path: str) -> bool:
    path = Path(relative_path)
    if path.name in IGNORED_SYNC_FILENAMES:
        return True
    if path.suffix == ".pyc":
        return True
    return any(part in IGNORED_SYNC_PARTS for part in path.parts)


def is_local_asset(relative_path: str) -> bool:
    path = Path(relative_path)
    parts = path.parts
    if len(parts) < 3 or parts[0] != ".github":
        return False
    if parts[1] == "skills":
        return len(parts) >= 3 and parts[2].startswith("local-")
    return path.name.startswith("local-")


def is_imported_asset(relative_path: str) -> bool:
    path = Path(relative_path)
    parts = path.parts
    if len(parts) < 3 or parts[0] != ".github":
        return False
    if parts[1] == "skills":
        prefix = parts[2]
        return not prefix.startswith(("internal-", "local-"))
    if parts[1] in {"agents", "instructions"}:
        return not path.name.startswith(("internal-", "local-"))
    return False


def is_consumer_sync_excluded_path(relative_path: str) -> bool:
    path = Path(relative_path)
    return any(part.startswith(CONSUMER_SYNC_EXCLUDED_PREFIX) for part in path.parts)


def resolve_markdown_target(root: Path, current_file: Path, target: str) -> Path | None:
    clean_target = target.split("#", maxsplit=1)[0].strip()
    if not clean_target:
        return None
    if "://" in clean_target or clean_target.startswith(("mailto:", "file:")):
        return None
    if clean_target.startswith("/"):
        return None
    if clean_target.startswith((".github/", "docs/")) or clean_target == "AGENTS.md":
        return root / clean_target
    return (current_file.parent / clean_target).resolve()


def action_sort_key(action: str) -> int:
    ordering = {
        "create": 0,
        "update": 1,
        "rename": 2,
        "ensure": 3,
        "rebuild": 4,
        "delete": 5,
        "manual": 6,
        "preserve": 7,
        "unchanged": 8,
    }
    return ordering.get(action, 99)


def finding_sort_key(finding: Finding) -> tuple[int, str, str]:
    severity_order = {"blocking": 0, "non-blocking": 1}
    return (severity_order.get(finding.severity, 99), finding.path, finding.code)


def path_list(root: Path, pattern: str) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.glob(pattern)
        if path.is_file()
    )


def all_files_under(root: Path, relative_dir: str) -> list[str]:
    base_dir = root / relative_dir
    if not base_dir.exists():
        return []
    results: list[str] = []
    for path in base_dir.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root).as_posix()
        if is_ignored_sync_path(relative_path):
            continue
        results.append(relative_path)
    return sorted(results)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
