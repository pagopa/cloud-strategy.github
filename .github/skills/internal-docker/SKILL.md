---
name: internal-docker
description: Use when creating or modifying Dockerfiles, Compose assets, image build settings, or container hardening rules.
---

# Internal Docker

## When to use

- Creating or updating `Dockerfile` assets.
- Editing Compose manifests or workflow-local image references.
- Hardening container build and runtime configuration.

## Mandatory rules

- Pin images by digest (`image@sha256:...`), never by `latest` or another
  floating tag alone; floating tags make builds non-reproducible and add
  supply-chain risk.
- Use multi-stage builds: install build and dev dependencies in the build
  stage, then `COPY --from=build` only compiled artifacts into the runtime
  stage. Dev dependencies in the runtime stage enlarge the image and the
  attack surface.
- Run as a non-root user in the final stage, for example `USER node` or
  `USER nobody`; a container escape from root gives host-level privileges.
- Combine related `RUN` commands with `&&`; one `RUN` per command adds layers,
  enlarges the image, and slows pulls.
- Always include a `.dockerignore` that excludes `.git`, `node_modules`,
  `__pycache__`, secrets, dev dependencies, and other non-essential files.
- Always use `pip install --no-cache-dir` so the pip cache does not persist in
  a layer.

## Validation

- Verify image references use digests.
- Verify non-root user in final stage.
- Verify `.dockerignore` exists and excludes sensitive/unnecessary files.
- Build or lint the container definition when tooling is available.

## References

- [`references/dockerfile-patterns.md`](references/dockerfile-patterns.md):
  load when you need the canonical multi-stage or single-stage example.
