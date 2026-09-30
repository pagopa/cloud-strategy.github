---
description: Markdown review checks for links, fences, references, and technical claims that must match the repository.
applyTo: "**/*.md"
excludeAgent: "cloud-agent"
---

# Markdown Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag relative links to files that do not exist in the repository and
  fragment links to headings that do not exist in the target file.
- Flag empty links, reversed link syntax such as `(text)[url]`, and undefined
  reference-style links.
- Flag unclosed code fences and fence changes that turn prose into code or
  code into prose.
- Check commands, paths, file names, and options in changed text against the
  repository. Flag stale references and guidance that contradicts code, tests,
  or validators.
- Flag text that presents a rule as enforced when no validator, test, or CI
  check in the repository enforces it.
- Flag policy copied from its canonical owner file when both copies can drift.
  Name the owner.
- Assume GitHub Flavored Markdown unless the file targets another renderer.
- Do not review external link targets or editorial style.
