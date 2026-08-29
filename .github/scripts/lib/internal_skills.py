"""Compatibility exports for the pre-package internal-skill checks API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from copilot_tools.checks.internal_skills import (
    ALLOWED_VIRTUAL_PATHS,
    ALLOWED_VIRTUAL_PREFIXES,
    CHAT_EXCLUSION_MARKERS,
    EXTERNAL_URL_PATTERN,
    FENCED_BLOCK_PATTERN,
    INLINE_PATH_PATTERN,
    INLINE_TEMPLATE_THRESHOLD,
    LEGACY_OUTPUT_FIELD_TOKENS,
    LEXICAL_METHODS,
    MAX_SKILL_BODY_LINES,
    PORTABLE_FRONTMATTER_FIELDS,
    RAW_SKILL_SOURCE_PATTERN,
    ROUTER_SKILL_NAMES,
    SHORT_DESCRIPTION_MAX,
    SHORT_DESCRIPTION_MIN,
    SKILL_INVOCATION_PATTERN,
    STRUCTURAL_PARSERS,
    TRIGGER_FIRST_PREFIXES,
    detect_bundle_security_findings,
    detect_internal_skill_findings,
    detect_skill_invocation_findings,
    detect_skill_prose_assertion_findings,
    is_cross_skill_file_reference,
    iter_internal_skills,
    markdown_targets,
    resolve_reference,
    strip_code_fences,
    validate_internal_skill,
    validate_local_references,
    validate_openai_yaml,
    validate_output_contract_projection,
    validate_token_hygiene,
)
