---
description: Create or modify Dockerfiles and container manifests with digest-pinned images and reproducible builds
name: internal-docker
agent: agent
argument-hint: action=<create|modify> artifact_type=<dockerfile|compose|container-image> purpose=<purpose> [target_path=<path>] [target_file=<path>]
---

# Docker Task

## Context
Create or modify Docker-related assets while keeping image references immutable, builds reproducible, and runtime posture secure.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Artifact type**: ${input:artifact_type:dockerfile,compose,container-image}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:.}
- **Target file (when modifying)**: ${input:target_file}

## Instructions
1. Use `.github/skills/internal-docker/SKILL.md` and `.github/instructions/internal-docker.instructions.md`.
2. Reuse existing repository patterns before introducing new Docker structure.
3. Preserve existing behavior unless the task explicitly changes the container contract.

## Minimal example
- Input: `action=modify artifact_type=dockerfile purpose="Pin the runtime image and reduce attack surface" target_file=Dockerfile`
- Expected output:
  - Updated Docker asset with digest-pinned image references.
  - Reproducible build/runtime behavior with clear version provenance.

## Validation
- Validate Dockerfile or Compose syntax when tooling is available.
- Verify image references use digests instead of floating tags.
- Run `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` when changing Copilot assets.
