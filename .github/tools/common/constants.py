from __future__ import annotations

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
CONSUMER_SYNC_EXCLUDED_PREFIX = "internal-sync-"
CONSUMER_SYNC_EXCLUDED_PATH_PREFIXES = frozenset()
LESSONS_PATH = "LESSONS_LEARNED.md"
DOCS_README_PATH = "docs/README.md"
ARCHITECTURE_PATH = "docs/architecture.md"
REPOSITORY_CONTEXT_PATH = "docs/repository-context.md"
TECH_PATH = "docs/tech.md"
STRUCTURE_PATH = "docs/structure.md"
RETIRED_RUNTIME_OPERATING_MODEL_PATH = "docs/03-local-ai-runtime-operating-model.md"
LEGACY_LOCAL_ARCHITECTURE_PATH = "docs/01-local-architecture.md"
LEGACY_LOCAL_REPOSITORY_CONTEXT_PATH = "docs/02-local-repository-context.md"
LEGACY_ARCHITECTURE_PATH = "docs/01-architecture.md"
LEGACY_REPOSITORY_CONTEXT_PATH = "docs/02-repository-context.md"
LEGACY_RUNTIME_FIT_PATH = "docs/runtime-fit.md"
DOCS_README_TEMPLATE_PATH = ".github/templates/docs-README.md.template"
ARCHITECTURE_TEMPLATE_PATH = ".github/templates/architecture.md.template"
REPOSITORY_CONTEXT_TEMPLATE_PATH = ".github/templates/repository-context.md.template"
TECH_TEMPLATE_PATH = ".github/templates/tech.md.template"
STRUCTURE_TEMPLATE_PATH = ".github/templates/structure.md.template"
CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES = {
    DOCS_README_PATH: DOCS_README_TEMPLATE_PATH,
    ARCHITECTURE_PATH: ARCHITECTURE_TEMPLATE_PATH,
    REPOSITORY_CONTEXT_PATH: REPOSITORY_CONTEXT_TEMPLATE_PATH,
    TECH_PATH: TECH_TEMPLATE_PATH,
    STRUCTURE_PATH: STRUCTURE_TEMPLATE_PATH,
}
MANAGED_ROOT_FILES = (
    "AGENTS.md",
    LESSONS_PATH,
    ".editorconfig",
    ".pre-commit-config.yaml",
    ".github/copilot-instructions.md",
    ".github/copilot-commit-message-instructions.md",
    ".github/security-baseline.md",
    ".github/DEPRECATION.md",
    ".github/repo-profiles.yml",
)
MANAGED_WORKFLOW_FILES = (".github/workflows/_pre-commit.yml",)
VSCODE_SETTINGS_PATH = ".vscode/settings.json"
INVENTORY_PATH = ".github/INVENTORY.md"
IMPORTED_ASSET_OVERRIDES_PATH = ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
MANAGED_EXTERNAL_RESOURCES_PATH = ".github/skills/local-agent-sync-external-resources/references/managed-resources.yaml"
