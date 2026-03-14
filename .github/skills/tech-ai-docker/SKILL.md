---
name: TechAIDocker
description: Create or modify Docker assets with digest-pinned images, secure runtime defaults, and reproducible builds. Use when the user mentions Dockerfiles, container images, Docker Compose, multi-stage builds, .dockerignore, or container security hardening.
---

# Docker Skill

## When to use
- Creating or updating `Dockerfile` assets.
- Editing Compose manifests or workflow-local image references.
- Hardening container build and runtime configuration.

## Mandatory rules
- Pin images by digest (`@sha256:...`), never by floating tag alone.
- Use multi-stage builds to separate build and runtime layers.
- Run as non-root user in the final stage.
- Use `COPY --from=build` to bring only compiled artifacts into runtime.
- Minimize layer count — combine related `RUN` commands.
- Always include a `.dockerignore` to exclude `.git`, `node_modules`, `__pycache__`, etc.

## Multi-stage pattern
```dockerfile
# -- build stage --
FROM node:22.14.0-alpine3.21@sha256:<digest> AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# -- runtime stage --
FROM node:22.14.0-alpine3.21@sha256:<digest> AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER node
CMD ["node", "dist/server.js"]
```

## Single-stage minimal example
```dockerfile
FROM python:3.12-slim@sha256:<digest>
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
CMD ["python", "main.py"]
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `latest` or floating tags | Non-reproducible builds, supply-chain risk | Pin by digest: `image@sha256:abc...` |
| Running as root in production | Container escape gives host-level privileges | Add `USER node` / `USER nobody` in final stage |
| Copying entire context without `.dockerignore` | Bloated image with `.git`, secrets, dev deps | Create `.dockerignore` excluding non-essential files |
| Installing dev dependencies in runtime stage | Larger image, unnecessary attack surface | Use multi-stage: install in build, copy only artifacts |
| One `RUN` per command | Excessive layers, larger image, slower pulls | Combine related commands with `&&` |
| Missing `--no-cache-dir` on pip install | Wasted space from pip cache in layer | Always `pip install --no-cache-dir` |

## Cross-references
- **TechAICICDWorkflow** (`.github/skills/tech-ai-cicd-workflow/SKILL.md`): for CI/CD pipelines that build and push images.
- **TechAICodeReview** (`.github/skills/tech-ai-code-review/SKILL.md`): for reviewing Dockerfile changes.

## Validation
- Verify image references use digests.
- Verify non-root user in final stage.
- Verify `.dockerignore` exists and excludes sensitive/unnecessary files.
- Build or lint the container definition when tooling is available.
