# Python Standalone Script Policy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update Copilot customization assets so Python dependency locking guidance is global, while self-contained folder packaging with a Bash launcher applies only to standalone Python scripts.

**Architecture:** Keep common Python dependency policy in global and path-based Python instructions. Keep standalone script packaging guidance in the Python script prompt and skill, with small Bash instruction support for the generated launcher script. Update the changelog because this changes repository-wide authoring guidance.

**Tech Stack:** Markdown customization assets, GitHub Copilot prompts, GitHub Copilot skills, Bash, Python

---

## Chunk 1: Policy Documents

### Task 1: Record the approved design

**Files:**
- Create: `docs/superpowers/specs/2026-03-19-python-standalone-script-policy-design.md`
- Create: `docs/superpowers/plans/2026-03-19-python-standalone-script-policy.md`

- [ ] **Step 1: Capture the approved policy split**
- [ ] **Step 2: List the exact customization assets to update**

## Chunk 2: Global Python Guidance

### Task 2: Strengthen Python dependency guidance

**Files:**
- Modify: `.github/copilot-instructions.md`
- Modify: `.github/instructions/python.instructions.md`
- Modify: `.github/prompts/tech-ai-python.prompt.md`

- [ ] **Step 1: Add repository-wide guidance for hash-locked Python requirements**
- [ ] **Step 2: Clarify that external libraries are recommended when they materially simplify code**
- [ ] **Step 3: Keep the guidance non-mandatory when the standard library is simpler**

## Chunk 3: Standalone Script Packaging

### Task 3: Update the standalone Python script prompt and skill

**Files:**
- Modify: `.github/prompts/tech-ai-python-script.prompt.md`
- Modify: `.github/skills/tech-ai-script-python/SKILL.md`
- Modify: `.github/instructions/bash.instructions.md`

- [ ] **Step 1: Require a self-contained folder layout for new standalone scripts**
- [ ] **Step 2: Require a Bash launcher that bootstraps `.venv`, installs dependencies, and runs the script**
- [ ] **Step 3: Keep Bash guidance aligned with the generated launcher behavior**

## Chunk 4: Governance And Verification

### Task 4: Update governance notes and validate

**Files:**
- Modify: `.github/CHANGELOG.md`

- [ ] **Step 1: Add a changelog entry for the new authoring policy**
- [ ] **Step 2: Run customization validation**
- [ ] **Step 3: Run targeted syntax checks on changed files**
