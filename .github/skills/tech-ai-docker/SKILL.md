---
name: TechAIDocker
description: Create or modify Docker assets with digest-pinned images, secure runtime defaults, and reproducible builds.
---

# Docker Skill

## When to use
- Creating or updating `Dockerfile` assets.
- Editing Compose manifests or workflow-local image references.
- Hardening container build and runtime configuration.

## Mandatory rules
- Pin external images by digest and keep the human-readable tag/version nearby.
- Prefer multi-stage builds so build dependencies stay out of the runtime image.
- Use a non-root runtime user unless a documented exception is required.
- Keep build steps deterministic and minimize leftover package-manager caches.
- Maintain `.dockerignore` so secrets, VCS metadata, caches, and local environments are excluded.

## Minimal example
```dockerfile
# node:22.14.0-alpine3.21
FROM node:22.14.0-alpine3.21@sha256:<digest> AS runtime

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .

USER node
CMD ["node", "server.js"]
```

## Validation
- Check that image references use digests instead of floating tags.
- Build or lint the container definition when tooling is available.
