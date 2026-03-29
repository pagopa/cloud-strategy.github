---
description: Docker and container build standards for secure, reproducible images and pinned digests.
applyTo: "**/Dockerfile,**/Dockerfile.*,**/.dockerignore,**/docker-compose*.yml,**/compose*.yml"
---

<!-- Core Knowledge Source: awesome-copilot-containerization-docker-best-practices.instructions.md -->
<!-- This internal instruction extends the external with governance-specific rules. -->
<!-- Do not duplicate content from the core source; reference it instead. -->

# Docker Instructions

## Mandatory rules
- Pin base images and runtime images by digest rather than tag alone.
- Keep an adjacent comment, label, or nearby reference that states the human-readable tag/version for each pinned digest.
- Prefer multi-stage builds when build tooling is not needed at runtime.
- Run containers as a non-root user unless a documented exception is required.
- Keep `.dockerignore` current so secrets, VCS data, caches, and local virtualenvs are excluded.

## Image pinning
- Prefer `image:tag@sha256:<digest>` for Dockerfiles, Compose files, and workflow container references.
- Avoid floating tags such as `latest`, `stable`, or major-only tags without a digest.
- When a digest cannot be used, pin to the most specific stable tag available and document why the digest is unavailable.

## Build hygiene
- Keep layers deterministic and minimize package-manager cache residue.
- Pin package-manager dependencies when practical for the target ecosystem.
- Separate build-time and runtime concerns so the final image stays minimal.

## Validation
- Validate Dockerfile or Compose syntax when tooling is available.
- Check that all image references are pinned by digest before merge.
