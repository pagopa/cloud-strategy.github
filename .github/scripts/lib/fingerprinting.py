"""Compatibility exports for the pre-package fingerprinting API."""

# Re-exported names preserve the legacy import surface.
# ruff: noqa: F401

from copilot_tools.core.fingerprinting import (
    HASH_ALGO,
    NORMALIZATION_VERSION,
    TEXT_EXTENSIONS,
    ResourceFingerprint,
    build_fingerprint,
    build_manifest,
    build_source_ref,
    collect_files,
    detect_kind,
    diff_manifests,
    index_resources,
    load_manifest,
    normalize_content,
    render_diff_text,
    sha256_bytes,
)
