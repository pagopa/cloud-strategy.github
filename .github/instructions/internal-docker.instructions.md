---
description: Container review checks for pinned images, runtime user, secret leakage, reproducible builds, and Compose exposure.
applyTo: "**/Dockerfile,**/Dockerfile.*,**/*.dockerfile,**/.dockerignore,**/docker-compose*.yml,**/docker-compose*.yaml,**/compose*.yml,**/compose*.yaml"
excludeAgent: "cloud-agent"
---

# Docker Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag unpinned base images or mutable tags where digest pinning is expected.
- Verify container runtime user, file permissions, and privilege posture are safe.
- Check for secret leakage through build args, ENV, or copied local files.
- Report oversized build context risks and missing ignore patterns in `.dockerignore`.
- Verify deterministic build behavior across stages and dependency installs.
- Check compose/service files for least-privilege networking and volume exposure.
- Flag missing healthcheck, resource, or restart constraints when operationally required.
- Report deprecated Dockerfile instructions or unsafe shell patterns.
