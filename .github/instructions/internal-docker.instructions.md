---
description: Docker and container build standards for secure, reproducible images and pinned digests.
applyTo: "**/Dockerfile,**/Dockerfile.*,**/*.dockerfile,**/.dockerignore,**/docker-compose*.yml,**/docker-compose*.yaml,**/compose*.yml,**/compose*.yaml"
---

# Docker Instructions

## Mandatory rules
- Pin base images and runtime images by digest rather than tag alone.
- Keep an adjacent comment, label, or nearby reference that states the human-readable tag/version for each pinned digest.
- Prefer multi-stage builds when build tooling is not needed at runtime.
- Run containers as a non-root user unless a documented exception is required.
- Run one primary process per container unless a supervisor pattern is explicitly justified.
- Keep `.dockerignore` current so secrets, VCS data, caches, and local virtualenvs are excluded.
- Keep configuration externalized through environment variables or mounted config, not hardcoded environment-specific values.

## Image pinning
- Prefer `image:tag@sha256:<digest>` for Dockerfiles, Compose files, and workflow container references.
- Avoid floating tags such as `latest`, `stable`, or major-only tags without a digest.
- When a digest cannot be used, pin to the most specific stable tag available and document why the digest is unavailable.
- Prefer official, minimal, and regularly patched base images such as `alpine`, `slim`, or distroless variants when compatible.

## Build hygiene
- Order Dockerfile instructions to maximize cache reuse: dependency metadata first, source code later.
- Combine related package-manager commands in one layer and clean caches in the same layer.
- Keep layers deterministic and minimize package-manager cache residue.
- Pin package-manager dependencies when practical for the target ecosystem.
- Separate build-time and runtime concerns so the final image stays minimal.
- Copy only the files needed for each stage; avoid `COPY . .` when a narrower copy set is practical.
- Prefer exec-form `CMD` or `ENTRYPOINT` for signal handling and predictable process behavior.

## Runtime and compose guidance
- Use `EXPOSE` to document intended ports even though publishing happens at runtime.
- In Compose files, prefer explicit networks, named volumes, and restart policies when the service lifecycle requires them.
- Add resource limits or reservations when the workload has known CPU or memory expectations.
- Avoid host networking, privileged mode, and broad bind mounts unless explicitly required and documented.

## Validation
- Validate Dockerfile or Compose syntax when tooling is available.
- Check that all image references are pinned by digest before merge.
- Review the final runtime stage for unnecessary tooling, shells, or package managers.
