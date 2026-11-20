---
description: YAML review checks for duplicate keys, indentation, implicit typing, block scalars, anchors, and secret exposure.
applyTo: "**/*.yml,**/*.yaml"
excludeAgent: "cloud-agent"
---

# YAML Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag duplicate mapping keys. Most parsers keep one value silently.
- Flag tab indentation and indentation changes that move a key to another
  parent.
- Flag unquoted scalars that YAML 1.1 parsers retype, such as `yes`, `no`,
  `on`, `off`, `1.10`, and leading-zero numbers, where the consumer expects a
  string. Keys defined by the consumer, such as GitHub Actions `on:`, are
  valid.
- Flag block scalar indicators (`|`, `|-`, `>`) whose trailing-newline change
  alters a value the consumer uses.
- Flag anchors, aliases, and merge keys (`<<`) that the consumer parser does
  not support or that hide an override.
- Flag secrets, environment-scope leaks, and values that change runtime
  behavior without a matching description in the pull request.
- Leave schema checks for workflows, Kubernetes, Compose, and CloudFormation
  to their path-specific instructions.
